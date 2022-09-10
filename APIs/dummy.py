from fastapi import FastAPI, status
from pymongo import MongoClient

app = FastAPI()  ## name of the app is 'app'

# API endpoint : status :: checking status of the API

@app.get("/status/")
def get_status():
    return {"status": "running"}