import threading
import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import time

# Constants
broker_address = "127.0.0.1"
port = 1883
TOPIC = "/ic/Grupo3/"


class ESP32Simulator:
    def __init__(self, root):
        self.temp_label = None
        self.temp_entry = None
        self.button_button = None
        self.fire_button = None
        self.temp_button = None
        self.app = root
        self.client = mqtt.Client(client_id="ESP32Simulator")
        self.client.on_connect = self.on_connect
        self.client.connect(broker_address, port)
        self.fire_status = False
        self.button_pressed = False
        self.alarm_status = False
        # Run MQTT client in a separate thread
        mqtt_thread = threading.Thread(target=self.client.loop_forever)
        mqtt_thread.daemon = True  # Allows thread to exit when main program exits
        mqtt_thread.start()

        self.create_widgets()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
        else:
            print("Connection failed with code", rc)

    def create_widgets(self):
        self.temp_button = ttk.Button(self.app, text="Publish Temp", command=self.publish_temp)
        self.temp_button.pack(pady=10)

        self.fire_button = ttk.Button(self.app, text="Publish Fire", command=self.publish_fire)
        self.fire_button.pack(pady=10)

        self.button_button = ttk.Button(self.app, text="Publish Alarm", command=self.publish_alarm)
        self.button_button.pack(pady=10)

        self.button_button = ttk.Button(self.app, text="Publish Self Alarm", command=self.publish_self_alarm)
        self.button_button.pack(pady=10)

        self.temp_label = ttk.Label(self.app, text="Insert temperature: ")
        self.temp_label.pack()
        self.temp_entry = ttk.Entry(self.app)
        self.temp_entry.pack()
        self.temp_entry.insert(0, "25.0")  # Default temperature value

    def publish_temp(self):
        temp = self.temp_entry.get()
        self.client.publish(TOPIC + "temp", temp)
        print(f"Published Temp: {temp}")

    def publish_fire(self):
        if self.fire_status:
            fire_status = "0"
        else:
            fire_status = "1"
        self.fire_status = not self.fire_status
        self.client.publish(TOPIC + "fire", fire_status)
        print(f"Published Fire: {fire_status}")

    def publish_alarm(self):
        if self.alarm_status:
            alarm_status = "0"
        else:
            alarm_status = "1"
        self.alarm_status = not self.alarm_status
        self.client.publish("/ic/Grupo2/alarme", alarm_status)
        print(f"Published Alarm: {alarm_status}")

    def publish_self_alarm(self):
        if self.alarm_status:
            alarm_status = "0"
        else:
            alarm_status = "1"
        self.alarm_status = not self.alarm_status
        self.client.publish("/ic/Grupo3/alarme", alarm_status)
        print(f"Published Alarm: {alarm_status}")

    def publish_button(self):
        if self.button_pressed:
            button_status = "0"  # Fire detected
        else:
            button_status = "1"
        self.button_pressed = not self.button_pressed
        # Button pressed
        self.client.publish(TOPIC + "button", button_status)
        print(f"Published Button: {button_status}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ESP32 Simulator")
    root.geometry("300x250")

    simulator = ESP32Simulator(root)

    root.mainloop()
