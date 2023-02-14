from threading import Lock
from queue import Queue
import time

from job import JobStatus, Job, JobResult


class Dispatcher:
    def __init__(self):
        self._job_queue = Queue()
        self._job_results = dict()
        self._job_state_transfer_lock = Lock()

    def put_job(self, job: Job):
        """
        Add a job to the input queue for the dispatcher to run.
        """
        self._job_state_transfer_lock.acquire()
        try:
            if job.id in self._job_results:
                raise RuntimeError("Job with id='{}' already exists".format(job.id))
            self._job_queue.put(job)
            self._job_results[job.id] = JobResult(job.id, status=JobStatus.QUEUED)
        finally:
            self._job_state_transfer_lock.release()

    def get_job_result(self, job_id) -> JobResult:
        """
        Return a JobResult object for the job_id provided.  If no job with this id is found we return a JobResult object status="NotFound".
        :param job_id: The id of the job to get results for.
        :return: Returns a JobResult object with status and result fields appropriately set.
        """
        self._job_state_transfer_lock.acquire()
        try:
            job_result = self._job_results.get(job_id, JobResult(job_id, status=JobStatus.NOT_FOUND))
            if job_result.status is JobStatus.COMPLETED:
                del self._job_results[job_id]
        finally:
            self._job_state_transfer_lock.release()

        return job_result

    def __call__(self, *args, **kwargs):
        while True:
            if self._job_queue.empty():
                time.sleep(1)
