import paho.mqtt.client as mqtt

broker_address = "192.168.0.101"  # broker's IP address
port = 1883  # Default MQTT port
username = "DuckNet"  # Your network's username
password = "DuckieUPT"  # Your network's password

client = mqtt.Client(client_id="TestSubscriber")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe("/ic/#")
    else:
        print("Connection failed with code", rc)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username, password)

client.connect(broker_address, port)

client.loop_forever()
