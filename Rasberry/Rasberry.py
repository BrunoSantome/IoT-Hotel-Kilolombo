import random
import subprocess
import paho.mqtt.client as mqtt
import time
import signal
import Adafruit_DHT
import RPi.GPIO as raspi
import sys
import json


def get_host_name():
    bashCommandName = 'echo $HOSTNAME'
    host = subprocess \
               .check_output(['bash', '-c', bashCommandName]) \
               .decode("utf-8")[0:-1]
    return host

###############Sensores-Raspi######################

raspi.setmode(raspi.BOARD)
dht_sensor = Adafruit_DHT.DHT11
sensor_pin_weather = 4
redPin = 11
greenPin = 12
bluePin = 13
IN = 36
E = 18
IN1 = 22
IN2 = 16

raspi.setup(redPin, raspi.OUT)
raspi.setup(greenPin, raspi.OUT)
raspi.setup(bluePin, raspi.OUT)

raspi.setup(E, raspi.OUT)
raspi.setup(IN1, raspi.OUT)
raspi.setup(IN2, raspi.OUT)


def azul():
    raspi.output(redPin, raspi.LOW)
    raspi.output(greenPin, raspi.LOW)
    raspi.output(bluePin, raspi.HIGH)
    #print("El valor actual de la Led es: Azul")

def blanco():
    raspi.output(redPin, raspi.HIGH)
    raspi.output(greenPin, raspi.HIGH)
    raspi.output(bluePin, raspi.HIGH)
    #print("El valor actual de la Led es: Blanco")

def OFF():
    raspi.output(redPin, raspi.LOW)
    raspi.output(greenPin, raspi.LOW)
    raspi.output(bluePin, raspi.LOW)

def motorON():
    raspi.output(E, raspi.HIGH)
    raspi.output(IN1, raspi.HIGH)
    raspi.output(IN2, raspi.LOW)
    print("motor: ON")

def motorONreverse():
    raspi.output(E, raspi.HIGH)
    raspi.output(IN1, raspi.LOW)
    raspi.output(IN2, raspi.HIGH)
    print("motor: ON")

def motorOFF():
    raspi.output(E, raspi.LOW)
    raspi.output(IN1, raspi.LOW)
    raspi.output(IN2, raspi.LOW)
    print("motor: OFF")

def motorUP():
    print("Subiendo persianas")
    motorON()
    time.sleep(3)
    motorOFF()

def motorDOWN():
    print("Bajando persianas")
    motorONreverse()
    time.sleep(3)
    motorOFF()


#Valores inciales aleatorios de la habitación.
def SensorsRandomState():
    global Sensors
    Sensors = {
        "indoor_light": {
            "mode": "ON" if random.randint(0, 1) == 1 else "OFF",
        },
        "blind": {
            "mode": "OPEN" if random.randint(0, 1) == 1 else "CLOSE",
        },
        "temperature": {
            "level": str(getTemperature())
        },
        "state": {
            "mode": "inactivo"
        }

    }
    return Sensors

#Obtener la temperatura
def getTemperature():
    global temperature,Sensors
    temperature, weather = Adafruit_DHT.read(dht_sensor, sensor_pin_weather)
    if temperature == None:
        while temperature == None:
            temperature, weather = Adafruit_DHT.read(dht_sensor, sensor_pin_weather)

    return temperature




############# MQTT_1 && MQTT_2 ########################

def on_connect_1883(client, userdata,flags, rc):
    print("Connected on subscriber with code", rc)
    client.subscribe("hotel/rooms/+/config/room")
    client.publish(CONFIG_TOPIC, payload=ROOM_ID, qos=0, retain=False)
    print("Subscribed to all rooms config")

def on_message_1883(client, userdata, msg):
    global room_number, is_connected
    topic = (msg.topic).split('/')
    if topic[-1] == "room":
        room_number = msg.payload.decode()
        print("Room number recieved in the raspberry as: ", room_number)
        global is_connected
        is_connected = True



def on_connect_1884(client, userdata, flags, rc):
    global new_topic
    newtopic = "hotel/rooms/" + room_number + "/command/+"
    client.subscribe(newtopic)
    print("Nos suscribimos al canal de comandos")
    new_topic = "hotel/rooms/"+room_number +"/telemetry/"
    S = SensorsRandomState()
    ChangeLight(S)
    ChangeBlinds(S)
    temperature = Sensors["temperature"]["level"]
    LightValue = Sensors["indoor_light"]["mode"]
    BlindValue = Sensors["blind"]["mode"]
    client.publish(new_topic +"temperature", payload=temperature, qos=0, retain=True)
    client.publish(new_topic + "indoor_light", payload=json.dumps({"mode":LightValue}), qos=0, retain=True)
    client.publish(new_topic + "blind", payload=json.dumps({"mode":BlindValue}), qos=0, retain=True)
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
    temperature = str(getTemperature())
    client.publish(new_topic + "temperature", payload=temperature, qos=0, retain=True)
    if topic[-1] == "shutdown":
        message = json.loads(msg.payload)
        if message["mode"] == "OFF":
            if is_connected == True:
                if topic[2] == room_number:
                    Sensors["state"]["mode"] = "inactivo"
                    value = Sensors["state"]["mode"]
                    is_connected = False
                    OFF()
                    client.publish(new_topic + "state", payload=json.dumps({"mode": value}), qos=0, retain=True)

    if topic[-1] == "indoor_light":
        ValueLight=json.loads(msg.payload)
        Sensors["indoor_light"]["mode"] = ValueLight["mode"]
        ChangeLight(Sensors)
        client.publish(new_topic + "indoor_light", payload=json.dumps({"mode":ValueLight["mode"]}), qos=0, retain=True)
    if topic[-1] == "blind":
        ValueBlind = json.loads(msg.payload)
        Sensors["blind"]["mode"] = ValueBlind["mode"]
        ChangeBlinds(Sensors)
        client.publish(new_topic + "blind", payload=json.dumps({"mode":ValueBlind["mode"]}), qos=0, retain=True)

def ChangeBlinds(Sensors):
    Blind_value = Sensors["blind"]["mode"]

    if Blind_value == "OPEN":
        motorDOWN()
    if Blind_value == "CLOSE":
        motorUP()

def ChangeLight(Sensors):
    Light_value = Sensors["indoor_light"]["mode"]

    if Light_value == "ON":
        blanco()
    if Light_value == "OFF":
        OFF()

def connect_mqtt_1883():
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect_1883
    client.on_message = on_message_1883
    client.connect(MQTT_SERVER, MQTT_PORT_1, 60)
def connect_mqtt_1884():

    client2.username_pw_set(username="dso_server", password="dso_password")
    client2.on_connect = on_connect_1884
    client2.on_message = on_message_1884
    client2.connect(MQTT_SERVER, MQTT_PORT_2, 60)

ROOM_ID = get_host_name()
ALL_TELEMETRY ="hotel/rooms/+/telemetry/+"
CONFIG_TOPIC = "hotel/rooms/" + ROOM_ID + "/config"
MQTT_SERVER = "34.91.117.155"
MQTT_PORT_1 = 1883
MQTT_PORT_2 = 1884
room_number =""
COMMAND_TOPIC = "hotel/rooms/"+room_number +"/command/+"
ALL_COMMAND = "hotel/rooms/+/command/+"


if __name__ == "__main__":

    raspi.setwarnings(False)
    raspi.setup(IN, raspi.IN, pull_up_down=raspi.PUD_UP)

    client = mqtt.Client()
    client2 = mqtt.Client()

    connect_mqtt_1883()
    client.loop_start()
    while room_number == "":
      time.sleep(1)
    client.loop_stop()

    connect_mqtt_1884()
    client2.loop_start()
    while is_connected == True:
        time.sleep(1)
    client2.disconnect()
    print("Desconexion ordenada success de la habitación: ", room_number )
    client2.loop_stop()
    sys.exit()



