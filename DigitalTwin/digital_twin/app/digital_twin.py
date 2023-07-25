import random
import os
import subprocess
import time
import paho.mqtt.client as mqtt
import json
import sys

def randomize_sensors():

    
    global Sensors
    Sensors = {
        "indoor_light": {
            "mode": "ON" if random.randint(0, 1) == 1 else "OFF",
        },
        "blind": {
            "mode": "OPEN" if random.randint(0, 1) == 1 else "CLOSE",
        },
        "temperature": {
            "level": str(random.randint(20, 30))
        },
        "state": {
            "mode": "OFF"
        }
    }
    return Sensors


def on_connect_1883(client, userdata, flags, rc):
    print("Digital Twin connected with code", rc)
    client.subscribe(CONFIG_TOPIC +"/room")
    print("Nos suscribimos al canal de configuaración")
    client.publish(CONFIG_TOPIC, payload=ROOM_ID, qos=0, retain=False)
    print("Enviado el id", ROOM_ID, "al topic", CONFIG_TOPIC)


def on_message_1883(client, userdata, msg):
    global room_number, is_connected
    topic = (msg.topic).split('/')
    if topic[-1] == "room":
        room_number = msg.payload.decode()
        print("Room number recieved as: ", room_number)
        is_connected = True
    

def connect_mqtt_1883():
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect_1883
    client.on_message = on_message_1883
    client.connect(MQTT_SERVER, MQTT_PORT_1, 60)

def on_connect_1884(client, userdata, flags, rc):
    global Sensors, room_number, new_topic
    print("Digital Twin connected with code", rc)
    newtopic = "hotel/rooms/" + room_number + "/command/+"
    client.subscribe(newtopic)
    print("Nos suscribimos al canal de comandos")
    new_topic = "hotel/rooms/" + room_number + "/telemetry/"
    randomize_sensors()
    temperature = Sensors["temperature"]["level"]
    LightValue = Sensors["indoor_light"]["mode"]
    BlindValue = Sensors["blind"]["mode"]
    client.publish(new_topic + "temperature", payload=temperature, qos=0, retain=True)
    client.publish(new_topic + "indoor_light", payload=json.dumps({"mode": LightValue}), qos=0, retain=True)
    client.publish(new_topic + "blind", payload=json.dumps({"mode": BlindValue}), qos=0, retain=True)
    if is_connected == True:
        Sensors["state"]["mode"] = "activo"
        value = Sensors["state"]["mode"]
        client.publish(new_topic + "state", payload=json.dumps({"mode": value}), qos=0, retain=True)

    print("DATA SENT")
    time.sleep(2)

def on_message_1884(client, userdata, msg):
    global new_topic
    print("Mensaje recibido en ", msg.topic, "con mensaje", msg.payload.decode())
    global Sensors, is_connected
    topic = (msg.topic).split('/')
    temperature = Sensors["temperature"]["level"]
    client.publish(new_topic + "temperature", payload=temperature, qos=0, retain=True)
    if topic[-1] == "shutdown":
        message = json.loads(msg.payload)
        if message["mode"] == "OFF":
            if is_connected == True:
                if topic[2] == room_number:
                    Sensors["state"]["mode"] = "inactivo"
                    value = Sensors["state"]["mode"]
                    is_connected = False
                    client.publish(new_topic + "state", payload=json.dumps({"mode": value}), qos=0, retain=True)
                    

    if topic[-1] == "indoor_light":
        ValueLight = json.loads(msg.payload)
        Sensors["indoor_light"]["mode"] = ValueLight["mode"]
        print("Lights are: ",ValueLight["mode"] )
        client.publish(new_topic + "indoor_light", payload=json.dumps({"mode":ValueLight["mode"]}), qos=0, retain=True)
    if topic[-1] == "blind":
        ValueBlind = json.loads(msg.payload)
        Sensors["blind"]["mode"] = ValueBlind["mode"]
        print("Blinds are: ",ValueBlind["mode"])
        client.publish(new_topic + "blind",json.dumps({"mode":ValueBlind["mode"]}), qos=0, retain=True)
    
    
    

def connect_mqtt_1884():
    client2.username_pw_set(username="dso_server", password="dso_password")
    client2.on_connect = on_connect_1884
    client2.on_message = on_message_1884
    client2.connect(MQTT_SERVER, MQTT_PORT_2, 60)


def get_host_name():
    bashCommandName = 'echo $HOSTNAME'
    host = subprocess \
               .check_output(['bash', '-c', bashCommandName]) \
               .decode("utf-8")[0:-1]
    return host


MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
MQTT_PORT_1 = int(os.getenv("MQTT_SERVER_PORT_1"))
MQTT_PORT_2 = int(os.getenv("MQTT_SERVER_PORT_2"))
room_number = ""
ROOM_ID = get_host_name()
CONFIG_TOPIC = "hotel/rooms/" + ROOM_ID + "/config"
TELEMETRY_TOPIC = "hotel/rooms/" + room_number + "/telemetry/"
COMMAND_TOPIC = "hotel/rooms/"+ room_number +"/command/"
ALL_TOPICS ="hotel/rooms/+/telemetry/+"
ALL_COMMAND = "hotel/rooms/"+room_number+ "/command/+"


if __name__ == "__main__":

    client = mqtt.Client()
    client2 = mqtt.Client()
    connect_mqtt_1883()
    client.loop_start()
    while room_number =="":
        time.sleep(1)
    connect_mqtt_1884() 
    client2.loop_start()
    while is_connected == True:
        time.sleep(1)
    client2.disconnect()
    print("Desconexión ordenada succes de la habitación: ", room_number)
    client2.loop_stop()
    sys.exit()
        


        

