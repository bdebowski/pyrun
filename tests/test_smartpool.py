import sys
sys.path.extend(['D:\\bazyli\\Dropbox\\code\\PycharmProjects\\pyrunner'])  # todo

from threading import Thread
from multiprocessing import TimeoutError
import time

from smartpool import SmartPool

RETURN42 = """
def foo():
    return 42

return_value_container.value = foo()
"""

TIMEOUT = """
def foo():
    while(True):
        pass

return_value_container.value = foo()
"""

EXCEEDMEMORY = """
def foo():
    l = [1]*1024*1024*512

return_value_container.value = foo()
"""

CRASH = """
def foo():
    raise RuntimeError("foo raised this RuntimeError()")

return_value_container.value = foo()
"""


class ReturnValContainer:
    def __init__(self):
        self.value = None


def exec_and_return(payload: str, exec_globals={}):
    exec(payload, exec_globals)
    time.sleep(1)
    return exec_globals["return_value_container"].value


def run_test():
    _globals = {"return_value_container": ReturnValContainer()}
    pool = SmartPool(worker_fn=exec_and_return, kwargs={"exec_globals": _globals}, num_workers=4, timeout_sec=2.0)
    t = Thread(target=pool, daemon=True)
    t.start()
    time.sleep(1)
    codes = [RETURN42, TIMEOUT, EXCEEDMEMORY, CRASH]
    required_result_type = [int, TimeoutError, MemoryError, RuntimeError]
    for i in range(100):
        pool.put_job(i, codes[i % 4])
    for i in range(1, 101):
        if i % 10 == 0:
            print("Received {}".format(i))
        job_result = pool.get_result()
        assert type(job_result.return_val) == required_result_type[job_result.id % 4], "Result type mismatch for result id={}".format(job_result.id)
    print("DONE")


if __name__ == "__main__":
    run_test()
