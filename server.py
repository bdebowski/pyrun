from threading import Thread

from flask import Flask, request

from dispatcher import Dispatcher
from job import Job


app = Flask(__name__)
dispatcher = Dispatcher()
Thread(target=dispatcher, daemon=True).start()


@app.get("/")
def get_result():
    return dispatcher.get_job_result(request.json["id"]).as_dict()


@app.post("/")
def post_request():
    try:
        dispatcher.put_job(Job(request.json["id"], src_code=request.json["src_code"]))
    except Exception as e:
        return e.__repr__()
    return "OK"
