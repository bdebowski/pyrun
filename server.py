from threading import Thread

from flask import Flask, request

from smartpool import SmartPool


ONE_MB = 1024*1024


class ReturnValContainer:
    def __init__(self):
        self.value = None


def exec_and_return(payload: str, _globals={}):
    exec(payload, _globals)
    return _globals["return_value_container"].value


pool = SmartPool(
    worker_fn=exec_and_return,
    kwargs={"_globals": {"return_value_container": ReturnValContainer()}},
    num_workers=4,
    timeout_sec=5.0,
    maxmem_bytes=512*ONE_MB)
app = Flask(__name__)


@app.get("/")
def get_result():
    num_results = request.json["num_results"]
    results = []
    while pool.result_ready() and len(results) < num_results:
        result = pool.get_result()
        return_val = result.return_val.__repr__() if isinstance(result.return_val, Exception) else result.return_val
        results.append({"id": result.id, "returned": return_val})
    return results


@app.post("/")
def post_request():
    try:
        for job in request.json:
            pool.put_job(job["id"], job["src_code"])
    except Exception as e:
        return e.__repr__()
    return "OK"


if __name__ == "__main__":
    smartpool_thread = Thread(target=pool, name='smartpool_thread', daemon=True)
    smartpool_thread.start()
    app.run()
