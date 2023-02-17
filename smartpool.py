from multiprocessing import Process, Pipe, TimeoutError
from multiprocessing.connection import Connection
from queue import Queue
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class _Job:
    id: Any
    payload: Any


@dataclass
class JobResult:
    id: Any
    return_val: Any


class ProcessDiedException(Exception):
    """
    The process died outside any try/except block.  We don't know what happened.
    """
    pass


class _ManagedProcess(Process):
    _STOP_COMMAND = "STOP"

    def __init__(self, parent_conn: Connection, child_conn: Connection, worker_fn: Callable):
        super().__init__(daemon=True)
        self._parent_conn = parent_conn
        self._child_conn = child_conn
        self._worker_fn = worker_fn
        self._current_job = None
        self._job_start_time = None

    def is_available(self):
        return self._current_job is None and self.is_alive()

    def result_ready(self):
        return self._parent_conn.poll()

    def get_result(self):
        result = self._parent_conn.recv()
        self._current_job = None
        self._job_start_time = None
        return result

    def assign_job(self, job: _Job):
        self._current_job = job.id
        self._parent_conn.send(job)
        self._job_start_time = time.time()

    @property
    def current_job(self):
        return self._current_job

    def time_on_job(self):
        if not self._job_start_time:
            return 0.0
        return time.time() - self._job_start_time

    def stop(self):
        self._parent_conn.send(self._STOP_COMMAND)

    def run(self):
        job = self._child_conn.recv()
        while job != self._STOP_COMMAND:
            try:
                return_val = self._worker_fn(job.payload)
            except Exception as e:
                return_val = e
            self._child_conn.send(return_val)
            job = self._child_conn.recv()


class SmartPool:
    def __init__(self, worker_fn: Callable, num_workers: int = 1, timeout_sec: float = 5.0):
        self._worker_fn = worker_fn
        self._num_workers = num_workers
        self._timeout_sec = timeout_sec

        self._processes = []

        self._input_queue = Queue()
        self._output_queue = Queue()

    def put_job(self, job_id: Any, payload: Any):
        self._input_queue.put(_Job(job_id, payload))

    def result_ready(self) -> bool:
        return not self._output_queue.empty()

    def get_result(self) -> JobResult:
        return self._output_queue.get()

    def _add_process(self):
        parent_conn, child_conn = Pipe()
        new_process = _ManagedProcess(parent_conn, child_conn, self._worker_fn)
        new_process.start()
        self._processes.append(new_process)

    def __call__(self):
        while True:
            # Ensure there are num_workers processes running
            # Spin up however many new processes we need
            while len(self._processes) < self._num_workers:
                self._add_process()

            # Pull jobs from the input_queue and assign them to all available processes
            available = [p for p in self._processes if p.is_available()]
            while not self._input_queue.empty() and len(available) > 0:
                next_available = available.pop()
                next_available.assign_job(self._input_queue.get())

            # Get returned results from each process that has results for us and create and put JobResult objects in the output queue
            results_ready = [p for p in self._processes if p.result_ready()]
            for p in results_ready:
                self._output_queue.put(JobResult(p.current_job, p.get_result()))

            # Check if any submitted jobs have gone over time
            # If they have, kill that process, remove it from the process pool, and create and put JobResult with a TimeoutException
            overtime = [p for p in self._processes if p.time_on_job() >= self._timeout_sec]
            for p in overtime:
                p.terminate()
                self._output_queue.put(JobResult(p.current_job, TimeoutError("The process running this job timed out")))
                self._processes.remove(p)

            # Check if any processes have died (i.e. is_alive() == False)
            # For any that died, remove them from the pool and return a JobResult with ProcessDiedException
            died = [p for p in self._processes if not p.is_alive()]
            for p in died:
                self._output_queue.put(JobResult(p.current_job, ProcessDiedException("The process running this job died outside a try/except block")))
                self._processes.remove(p)

            # Sleep a little so we don't hog cpu
            time.sleep(0.01)
