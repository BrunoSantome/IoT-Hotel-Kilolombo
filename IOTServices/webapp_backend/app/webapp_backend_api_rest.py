from flask import Flask, request
from flask_cors import CORS
import os, requests, json

app= Flask(__name__)
CORS(app)

@app.route('/device_state', methods=['GET','POST'])
def device_satate():
    if request.method == 'POST':
        params = request.get_json()
        print(MESSAGE_ROUTER_API_URL, flush = True)
        r = requests.post(
            MESSAGE_ROUTER_API_URL+"/device_state",
            json = params
        )
        print("params: ",params, flush = True)
        return json.dumps(r.json()),r.status_code
    elif request.method == 'GET':
        r = requests.get(DATA_INGESTION_API_URL+"/device_state")
        print("r: ",r, flush = True)
        return json.dumps(r.json()),r.status_code

DATA_INGESTION_API_URL = "http://"+os.getenv("DATA_INGESTION_API_ADDRESS")+":"+os.getenv("DATA_INGESTION_API_PORT")
MESSAGE_ROUTER_API_URL = "http://"+os.getenv("MESSAGE_ROUTER_API_ADDRESS")+":"+os.getenv("MESSAGE_ROUTER_API_PORT")
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
app.run(host= HOST, port=PORT, debug=True)
