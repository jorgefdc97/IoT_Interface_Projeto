import paho.mqtt.client as mqtt
import Interface.Application as Application  # Assuming app is your IoTApplication instance

broker_address = "127.0.0.1"  # Localhost
port = 1883  # Use the port where your broker is running


class Subscriber:
    def __init__(self):
        self.client = mqtt.Client(client_id="TestSubscriber")
        self.TOPIC = "/ic/Grupo3/"
        self.app = Application.IoTApplication()
        self.app.run()

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(broker_address, port)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            client.subscribe(self.TOPIC + "#")
        else:
            print("Connection failed with code", rc)

    def on_message(self, client, userdata, msg):
        if msg.topic == (self.TOPIC + "test"):
            print(msg.payload.decode())
        elif msg.topic == (self.TOPIC + "temp"):
            print(msg.payload.decode())
        elif msg.topic == (self.TOPIC + "fire_on"):
            self.app.turn_on_red_light()
            print("fire_on")
        elif msg.topic == (self.TOPIC + "fire_off"):
            print("fire_off")


if __name__ == "__main__":
    subscriber = Subscriber()
    subscriber.run()

