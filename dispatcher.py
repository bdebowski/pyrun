from threading import Lock
from queue import Queue


class Dispatcher:
    def __init__(self, job_queue: Queue):
        self._job_queue = job_queue
        self._completed_or_running = dict()

    def get_job(self, job_id):
        pass

    def __call__(self, *args, **kwargs):
        while True:
            pass
