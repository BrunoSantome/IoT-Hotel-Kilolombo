import json
import os
import paho.mqtt.client as mqtt
import threading
import time
import requests
from flask import Flask, request
from flask_cors import CORS
import os, requests, json

API_HOST = os.getenv("API_HOST")
API_PORT = os.getenv("API_PORT")
index_room = 1
room_name = ""
API_URL = "http://" + os.getenv("DATA_INGESTION_API_HOST") + ":" + os.getenv("DATA_INGESTION_API_PORT")
MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
MQTT_PORT_1 = int(os.getenv("MQTT_SERVER_PORT_1"))
MQTT_PORT_2 = int(os.getenv("MQTT_SERVER_PORT_2"))
TELEMETRY_TOPIC = "hotel/rooms/" + room_name + "/telemetry/"
TEMPERATURE_TOPIC = TELEMETRY_TOPIC + "temperature"
IN_LIGHT_TOPIC = TELEMETRY_TOPIC + "indoor_light"
BLIND_TOPIC = TELEMETRY_TOPIC + "blind"
CONFIG_TOPIC = "hotel/rooms/+/config"
ALL_TELEMETRY = "hotel/rooms/+/telemetry/+"
COMMAND_TOPIC = "hotel/rooms/" + room_name + "/command/"
LIGHTIN_COMMAND = COMMAND_TOPIC + "idoor_light"
BLIND_COMMAND = COMMAND_TOPIC + "blind"
ALL_COMMAND = "hotel/rooms/+/command/+"
app = Flask(__name__)
CORS(app)


def on_connect_1(client, userdata, flags, rc):
    print("Connected on subscriber with code", rc)
    client.subscribe(CONFIG_TOPIC)
    #client.subscribe(ALL_TELEMETRY)
    print("Subscribed to all rooms config")

def on_connect_2(client,userdata,flags, rc):
    client.subscribe(ALL_TELEMETRY)
    print("Subscribed to all telemetry")


def on_message_1(client, userdata, msg):
    global index_room, room_name
    print("Mensaje recibido en ", msg.topic, "con mensaje", msg.payload.decode())
    topic = (msg.topic).split('/')
    # una habitación me pide saber su numero( le doy el primero libre)
    if topic[-1] == "config":
        room_name = "Room" + str(index_room)
        print("Digital with id", msg.payload.decode(), "saved as", room_name)
        index_room += 1
        client.publish(msg.topic + "/room", payload=room_name, qos=0, retain=True)
        print("Publicado", room_name, "en TOPIC", msg.topic)
        semaforo = True


def on_message_2(client, userdata, msg):

    print("Mensaje recibido en ", msg.topic, "con mensaje", msg.payload.decode())
    topic = (msg.topic).split('/')
    if "telemetry" in topic:
        
        # ver lo de room_name si vale con pillar la variable global o hay q vovler a pillarla del topic
        value = -1
        if topic[-1] == "temperature":
            payload = json.loads(msg.payload)
            value = payload
            print("valor de temperatura recibido: ", value)
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
        if topic[-1] == "blind":
            payload = json.loads(msg.payload)
            value = payload["mode"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
        if topic[-1] == "indoor_light":
            payload = json.loads(msg.payload)
            value = payload["mode"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )
        if topic[-1] == "state":
            payload = json.loads(msg.payload)
            
            value = payload["mode"]
            requests.post(
                API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": value}
            )


def send_command(params):
    type_dev = params["type"]
    value = params["value"]
    room = params["room"]
    topic = "hotel/rooms/" + room + "/command"
    if type_dev == "blind":
        
        client2.publish(topic + "/blind", payload=json.dumps({"mode": value}), qos=0, retain=True)
        return {"response": "Message successfully sent"}, 200
    if type_dev == "indoor_light":
    
        client2.publish(topic + "/indoor_light", payload=json.dumps({"mode": value}), qos=0, retain=True)
        return {"response": "Message successfully sent"}, 200
    if type_dev == "SHUTDOWN":
        client2.publish(topic + "/shutdown", payload=json.dumps({"mode":value}), qos=0, retain=True)
        return {"response": "Message successfully sent"}, 200
    else:
        return {"response": "Incorrect type param"}, 401


@app.route('/device_state', methods=['POST'])
def device_state():
    if request.method == 'POST':
        params = request.get_json()
        print(params)
        return send_command(params)


def connect_mqtt_1():
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect_1
    client.on_message = on_message_1
    client.connect(MQTT_SERVER, MQTT_PORT_1, 60)

def connect_mqtt_2():
    client2.username_pw_set(username="dso_server", password="dso_password")
    client2.on_connect = on_connect_2
    client2.on_message = on_message_2
    client2.connect(MQTT_SERVER, MQTT_PORT_2, 60)

def initiate_api():
    
    CORS(app)
    app.run(host=API_HOST, port=API_PORT, debug=False)


if __name__ == "__main__":
    client = mqtt.Client()
    client2 = mqtt.Client()
    tmqtt = threading.Thread(target=initiate_api)
    tmqtt.start()
    connect_mqtt_1()
    client.loop_start()
    while room_name == "":
        time.sleep(1)
    connect_mqtt_2()
    client2.loop_forever()
