import time
import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import threading  # Import threading
from datetime import datetime
import threading
import time

# Constants
BROKER_ADDRESS = "192.168.0.101"  # broker's IP address
PORT = 1883  # Default MQTT port

RED_LIGHT_OFF_COLOR = "indianred4"
RED_LIGHT_ON_COLOR = "red3"
GREEN_LIGHT_OFF_COLOR = "chartreuse4"
GREEN_LIGHT_ON_COLOR = "chartreuse2"
WARNING_PANEL_COLOR = "gray11"

# Paths
SCRIPT_PATH = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(SCRIPT_PATH, "resources")
APPLICATION_NAME = "Internet of Things"


class IoTApplication:
    def __init__(self):
        self.root = ttk.Window(themename="darkly")
        self.root.title(APPLICATION_NAME)
        self.root.geometry("1280x680")
        self.system_fire = False
        self.system_ok = True
        self.graph_label = None
        self.red_light_state = False
        self.blink_interval = 0.5
        self.blink_thread = None
        self.lights_frame = None
        self.lights_canvas = None
        self.temperature_frame = None
        self.warning_message = None
        self.thermometer_image = None
        self.red_bar = None
        self.temperature_canvas = None
        self.thermometer_frame = None
        self.graph_frame = None
        self.is_blinking = True
        self.setup_lights_frame()
        self.setup_temperature_frame()
        self.subscriber = Subscriber(self)
        #self.temperature_storage = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        #                            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        #self.temperature_timestamp = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.temperature_storage = [12.34, 23.45, 34.56, 45.67, 15.78, 26.89, 37.90, 48.01, 19.12, 29.23, 39.34, 49.45,
                               10.56, 20.67, 30.78, 40.89, 11.90, 22.01, 33.12, 44.23]
        self.temperature_timestamp = ["08:15:32", "09:25:43", "10:35:54", "11:45:05", "12:55:16", "13:05:27", "14:15:38",
                                 "15:25:49", "16:35:50", "17:45:01", "18:55:12", "19:05:23", "20:15:34", "21:25:45",
                                 "22:35:56", "23:45:07", "00:55:18", "01:05:29", "02:15:30", "03:25:41"]

    def run(self):
        print("Application running")
        self.subscriber.run()
        self.root.mainloop()

    def setup_lights_frame(self):
        self.lights_frame = tk.Frame(self.root, width=400, height=100)
        self.lights_frame.pack(side="left", pady=5)

        # Create button with image and function
        button = ttk.Button(self.lights_frame, command=self.alarm_click)
        button.pack(pady=30)

        self.lights_canvas = ttk.Canvas(self.lights_frame, width=300, height=100, background="white")
        self.lights_canvas.pack()

        self.warning_message = self.lights_canvas.create_text(150, 45, text="INITIATING", font=("Digital-7", 25), fill="white")
        warning_background = self.lights_canvas.create_rectangle(80, 20, 220, 70, fill=WARNING_PANEL_COLOR)
        self.lights_canvas.tag_lower(warning_background, self.warning_message)

        self.turn_off_green_light()
        self.turn_off_red_light()

    def setup_temperature_frame(self):
        self.temperature_frame = ttk.Frame(self.root, width=200, height=400)
        self.temperature_frame.pack(side="right")

        self.graph_frame = ttk.Frame(self.temperature_frame)
        self.graph_frame.pack(side="left")

        self.thermometer_frame = ttk.Frame(self.temperature_frame)
        self.thermometer_frame.pack()

        self.temperature_canvas = ttk.Canvas(self.thermometer_frame, width=200, height=400, bg="skyblue")
        self.temperature_canvas.pack()

        self.red_bar = self.temperature_canvas.create_rectangle(110, 225, 88, 350, fill="red")

        image_path = os.path.join(RESOURCES_DIR, "thermometer.png")
        try:
            image = Image.open(image_path)
            resized_img = image.resize((70, 350))
            self.thermometer_image = ImageTk.PhotoImage(resized_img)
            self.temperature_canvas.create_image(100, 200, image=self.thermometer_image)
        except Exception as e:
            print(f"Error loading thermometer image: {e}")

    def alarm_click(self):
        self.turn_off_red_light()
        print("Button clicked!")

    def update_thermometer(self, value):
        red_bar_height = 225 - (value * 2.6)
        self.temperature_canvas.coords(self.red_bar, 110, red_bar_height, 88, 350)

    def turn_off_red_light(self):
        self.lights_canvas.create_oval(65, 5, 25, 45, fill=RED_LIGHT_OFF_COLOR, outline="black", width="1")
        self.lights_canvas.create_oval(65, 5, 25, 45, outline="gray7", width="3")

    def turn_off_green_light(self):
        self.lights_canvas.create_oval(65, 55, 25, 95, fill=GREEN_LIGHT_OFF_COLOR, outline="black", width="1")
        self.lights_canvas.create_oval(65, 55, 25, 95, outline="gray7", width="3")

    def turn_on_red_light(self):
        self.lights_canvas.create_oval(65, 5, 25, 45, fill=RED_LIGHT_ON_COLOR, outline="black", width="1")

    def turn_on_green_light(self):
        self.lights_canvas.create_oval(65, 55, 25, 95, fill=GREEN_LIGHT_ON_COLOR, outline="black", width="1")

    def toggle_red_light(self):
        while self.is_blinking:
            if self.red_light_state:
                self.turn_off_red_light()
            else:
                self.turn_on_red_light()
            self.red_light_state = not self.red_light_state
            time.sleep(self.blink_interval)

    def start_blinking(self):
        self.is_blinking = True
        self.blink_thread = threading.Thread(target=self.toggle_red_light)
        self.blink_thread.daemon = True
        self.blink_thread.start()

    def stop_blinking(self):
        self.is_blinking = False
        self.turn_off_red_light()

    def refresh_temperature(self, new_temperature):
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")

        self.temperature_timestamp = self.temperature_timestamp[1:]
        self.temperature_timestamp.append(timestamp)

        self.temperature_storage = self.temperature_storage[1:]
        self.temperature_storage.append(new_temperature)
        self.generate_temperature_graph()
        self.update_thermometer(new_temperature)

    def generate_temperature_graph(self):
        graph_width = 800
        graph_height = 400

        plt.plot(self.temperature_timestamp, self.temperature_storage)
        plt.xlabel("Timestamp")
        plt.ylabel("Temperature")
        plt.xticks(fontsize=4)
        graph_path = os.path.join(RESOURCES_DIR, "temperature_register.png")
        plt.savefig(graph_path)
        plt.close()

        try:
            image1 = Image.open(graph_path)
            image2 = image1.resize((graph_width, graph_height))
            photo = ImageTk.PhotoImage(image2)

            if self.graph_label is None:
                self.graph_label = tk.Label(self.graph_frame, image=photo, width=graph_width, height=graph_height)
                self.graph_label.image = photo  # Keep a reference to avoid garbage collection
                self.graph_label.pack()
            else:
                self.graph_label.configure(image=photo)
                self.graph_label.image = photo  # Update the reference to avoid garbage collection
        except Exception as e:
            print(f"Error loading graph image: {e}")

    def clear_graph_frame(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def system_on_fire(self):
        if self.system_fire:
            self.stop_blinking()
            self.turn_on_green_light()
            self.system_ok = True
            self.system_fire = False
            self.warning_panel_message("OK")
        else:
            self.start_blinking()
            self.turn_on_red_light()
            self.turn_off_green_light()
            self.system_ok = False
            self.system_fire = True
            self.warning_panel_message("FIRE")

    def warning_panel_message(self, new_message):
        self.lights_canvas.itemconfig(self.warning_message, text=new_message)


class Subscriber:
    def __init__(self, app):
        self.client = mqtt.Client(client_id="Grupo3_Interface")
        self.GENERAL_TOPIC = "/ic/#"
        self.TOPIC = "/ic/Grupo3/"
        self.app = app
        self.USERNAME = "DuckNet"  # Your network's username
        self.PASSWORD = "DuckieUPT"  # Your network's password

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, PORT)
        self.client.username_pw_set(self.USERNAME, self.PASSWORD)

        # Run MQTT client in a separate thread
        mqtt_thread = threading.Thread(target=self.client.loop_forever)
        mqtt_thread.daemon = True
        mqtt_thread.start()
        print('MQTT thread loop started')

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            client.subscribe(self.TOPIC + "#")
            print("Subscribing" + self.TOPIC + "#")
            self.app.generate_temperature_graph()
            self.app.system_on_fire()
        else:
            print("Connection failed with code", rc)

    def on_message(self, client, userdata, msg):
        print("Received message on topic:", msg.topic)
        print("Message payload:", msg.payload.decode())
        if msg.topic == (self.TOPIC + "test"):
            print("TEST:", msg.payload.decode())
        elif msg.topic == (self.TOPIC + "temp"):
            new_temp = float(msg.payload.decode())
            self.app.refresh_temperature(new_temperature=new_temp)
            print("TEMP: ", msg.payload.decode())
        elif msg.topic == (self.TOPIC + "fire"):
            self.app.system_on_fire()
            print("FIRE")
        elif msg.topic == (self.TOPIC + "button"):
            self.app.turn_on_blue_light()


if __name__ == "__main__":
    app = IoTApplication()
    app.run()
