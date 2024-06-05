import paho.mqtt.client as mqtt
import Interface.Application as app

BROKER_ADDRESS = "192.168.0.101"  # broker's IP address
PORT = 1883  # Default MQTT port
USERNAME = "DuckNet"  # Your network's username
PASSWORD = "DuckieUPT"  # Your network's password

CLIENT = mqtt.Client(client_id="TestSubscriber")

TOPIC = "/ic/Grupo3/"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(TOPIC + "#")
    else:
        print("Connection failed with code", rc)


def on_message(client, userdata, msg):
    print(msg.topic)
    if msg.topic == (TOPIC + "fire"):
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")


CLIENT.on_connect = on_connect
CLIENT.on_message = on_message

CLIENT.username_pw_set(USERNAME, PASSWORD)

CLIENT.connect(BROKER_ADDRESS, PORT)

CLIENT.loop_forever()
