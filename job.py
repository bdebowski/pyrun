from enum import Enum


class JobStatus(Enum):
    NOT_FOUND = "NotFound"
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"


class Job:
    def __init__(self, job_id, src_code: str = ""):
        self.id = job_id
        self.src_code = src_code

    def as_dict(self) -> dict:
        return vars(self)


class JobResult:
    def __init__(self, job_id, status: JobStatus = JobStatus.NOT_FOUND, result=None):
        self.id = job_id
        self.status = status
        self.result = result

    def as_dict(self) -> dict:
        d = vars(self)
        d["status"] = self.status.value
        return d
