import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import threading  # Import threading

# Constants
BROKER_ADDRESS = "192.168.0.101"  # broker's IP address
PORT = 1883  # Default MQTT port

TOPIC = "/ic/"

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
        # self.root.iconbitmap("")  # Add a valid icon path or remove this line
        self.setup_lights_frame()
        self.setup_temperature_frame()
        self.subscriber = Subscriber(self)

    def run(self):
        print("Application running")
        self.subscriber.run()
        self.root.mainloop()

    def setup_lights_frame(self):
        self.lights_frame = tk.Frame(self.root, width=400, height=100)
        self.lights_frame.pack(side="left", pady=5)

        self.lights_canvas = ttk.Canvas(self.lights_frame, width=300, height=100, background="white")
        self.lights_canvas.pack()

        warning_message = self.lights_canvas.create_text(150, 45, text="WARNING", font=("Digital-7", 25), fill="white")
        warning_background = self.lights_canvas.create_rectangle(80, 20, 220, 70, fill=WARNING_PANEL_COLOR)
        self.lights_canvas.tag_lower(warning_background, warning_message)

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

        self.red_bar = self.temperature_canvas.create_rectangle(110, 277, 88, 350, fill="red")

        image_path = os.path.join(RESOURCES_DIR, "thermometer.png")
        try:
            image = Image.open(image_path)
            resized_img = image.resize((70, 350))
            self.thermometer_image = ImageTk.PhotoImage(resized_img)
            self.temperature_canvas.create_image(100, 200, image=self.thermometer_image)
        except Exception as e:
            print(f"Error loading thermometer image: {e}")

    def update_thermometer(self, value):
        slider_value = int(value)
        red_bar_height = 350 - (slider_value * 3.5)
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

    def generate_temperature_graph(self):
        graph_width = 400
        graph_height = 400
        x = np.arange(0, 10, 0.1)
        y = 2 * x + 3 * 2

        plt.plot(x, y)
        plt.xlabel("Number")
        plt.ylabel("Temperature")

        graph_path = os.path.join(RESOURCES_DIR, "temperature_register.png")
        plt.savefig(graph_path)
        plt.close()

        try:
            image1 = Image.open(graph_path)
            image2 = image1.resize((graph_width, graph_height))
            photo = ImageTk.PhotoImage(image2)

            label = tk.Label(self.graph_frame, image=photo, width=graph_width, height=graph_height)
            label.image = photo  # Keep a reference to avoid garbage collection
            label.pack()
        except Exception as e:
            print(f"Error loading graph image: {e}")

    def warning_panel_message(self):
        # Implement warning message logic here
        pass


class Subscriber:
    def __init__(self, app):
        self.client = mqtt.Client(client_id="Grupo3_Interface")
        self.TOPIC = "/ic/Grupo3/"
        self.app = app
        self.USERNAME = "DuckNet"  # Your network's username
        self.PASSWORD = "DuckieUPT"  # Your network's password

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, PORT)

        # Run MQTT client in a separate thread
        mqtt_thread = threading.Thread(target=self.client.loop_forever)
        mqtt_thread.daemon = True  # Allows thread to exit when main program exits
        mqtt_thread.start()

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
            self.app.turn_off_red_light()
            print("fire_off")


if __name__ == "__main__":
    app = IoTApplication()
    app.run()
