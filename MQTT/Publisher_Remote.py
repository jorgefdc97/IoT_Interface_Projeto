import paho.mqtt.client as mqtt
import time

broker_address = "192.168.0.101"  # broker's IP address
port = 1883  # Default MQTT port
username = "DuckNet"  # Your network's username
password = "DuckieUPT"  # Your network's password

client = mqtt.Client(client_id="Publisher")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed with code", rc)

client.on_connect = on_connect

client.username_pw_set(username, password)

client.connect(broker_address, port)

client.loop_start()

try:
    while True:
        client.publish("/ic/Grupo3/SCRIPT", "Hello MQTT from Publisher")
        print("Message Published")
        time.sleep(10)
except KeyboardInterrupt:
    print("Exiting")
    client.loop_stop()
    client.disconnect()
