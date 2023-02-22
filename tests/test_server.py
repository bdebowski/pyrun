import requests
from time import sleep


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
    l = [1]*1024*1024*256

return_value_container.value = foo()
"""

CRASH = """
def foo():
    raise RuntimeError("foo raised this RuntimeError()")

return_value_container.value = foo()
"""

codes = [RETURN42, TIMEOUT, EXCEEDMEMORY, CRASH]


def create_work():
    i = 0
    while True:
        yield {"id": i, "src_code": codes[i % len(codes)]}
        i += 1


work_generator = create_work()


def get_n(n):
    jobs = []
    for work in work_generator:
        jobs.append(work)
        if len(jobs) == n:
            return jobs


url = "http://127.0.0.1:5345"

for i in range(5):
    print("Posting 10 jobs")
    r = requests.post(url, json=get_n(10))
    print(r.text)

results = []
while len(results) < 50:
    print("Asking for up to 5 results")
    r = requests.get(url, json={"num_results": 5})
    received = r.json()
    print("Got back {}".format(len(received)))
    results.extend(received)
    for result in received:
        print(result)
    sleep(1)
