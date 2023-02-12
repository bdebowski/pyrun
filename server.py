from flask import Flask, request

app = Flask(__name__)


@app.get("/")
def get_result():
    return {
        "response": "Got GET",
        "id": request.json["id"]}


@app.post("/")
def post_request():
    return {
        "response": "Got POST",
        "id": request.json["id"]}
