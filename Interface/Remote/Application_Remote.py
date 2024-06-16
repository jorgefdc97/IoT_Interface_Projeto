import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import time
import re

# Constants
BROKER_ADDRESS = "192.168.0.101"  # IP address of the MQTT broker
PORT = 1883  # Default MQTT port

# Light colors for different states
RED_LIGHT_OFF_COLOR = "indian red4"
RED_LIGHT_ON_COLOR = "red3"
GREEN_LIGHT_OFF_COLOR = "DarkOliveGreen4"
GREEN_LIGHT_ON_COLOR = "chartreuse2"
BLUE_LIGHT_OFF_COLOR = "midnight blue"
BLUE_LIGHT_ON_COLOR = "blue2"
YELLOW_LIGHT_OFF_COLOR = "goldenrod4"
YELLOW_LIGHT_ON_COLOR = "gold"
WARNING_PANEL_COLOR = "gray11"

# Paths
SCRIPT_PATH = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(SCRIPT_PATH, "../resources")
APPLICATION_NAME = "Internet of Things"


class IoTApplication:
    """
    Main class for the IoT application, managing the GUI and interactions with the MQTT subscriber.
    """

    def __init__(self):
        # Initialize the main application window
        self.root = ttk.Window(themename="darkly")
        self.root.title(APPLICATION_NAME)
        self.root.geometry("1280x680")

        # Application state variables
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
        self.group_message = None
        self.thermometer_image = None
        self.red_bar = None
        self.snooze = False
        self.temperature_canvas = None
        self.thermometer_frame = None
        self.graph_frame = None
        self.is_blinking = True

        # Set up the frames for lights and temperature display
        self.setup_lights_frame()
        self.setup_temperature_frame()

        # Initialize the MQTT subscriber
        self.subscriber = Subscriber(self)

        # Initialize temperature data storage
        self.temperature_storage = [0.0] * 20
        self.temperature_timestamp = [""] * 20

        """ 
        # Example data for demonstration
        self.temperature_storage = [
            12.34, 23.45, 34.56, 45.67, 15.78, 26.89, 37.90, 48.01, 19.12, 29.23,
            39.34, 49.45, 10.56, 20.67, 30.78, 40.89, 11.90, 22.01, 33.12, 44.23
        ]
        self.temperature_timestamp = [
            "08:15:32", "09:25:43", "10:35:54", "11:45:05", "12:55:16", "13:05:27",
            "14:15:38", "15:25:49", "16:35:50", "17:45:01", "18:55:12", "19:05:23",
            "20:15:34", "21:25:45", "22:35:56", "23:45:07", "00:55:18", "01:05:29",
            "02:15:30", "03:25:41"
        ]
        """

    def run(self):
        """Start the application."""
        print("Application running")
        self.subscriber.run()
        self.root.mainloop()

    def setup_lights_frame(self):
        """Set up the frame and widgets for the light indicators."""
        self.lights_frame = tk.Frame(self.root, width=400, height=300)
        self.lights_frame.pack(side="left", pady=5, anchor="center")

        # Style for the SNOOZE button
        style = ttk.Style()
        style.configure("Custom.TButton", font=('Arial', 12, 'bold'), foreground="black", background="yellow")

        # SNOOZE button
        button = ttk.Button(self.lights_frame, text="SNOOZE", command=self.snooze_click)
        button.configure(style="Custom.TButton")
        button.pack()

        # Canvas for the lights and warning messages
        self.lights_canvas = ttk.Canvas(self.lights_frame, width=300, height=200, background="white")
        self.lights_canvas.pack()

        # Warning message text
        self.warning_message = self.lights_canvas.create_text(150, 55, text="INITIATING", font=("Digital-7", 25),
                                                              fill="white")
        warning_background = self.lights_canvas.create_rectangle(80, 30, 220, 80, fill=WARNING_PANEL_COLOR)
        self.lights_canvas.tag_lower(warning_background, self.warning_message)

        # Group message text
        self.group_message = self.lights_canvas.create_text(150, 145, text="", font=("Digital-7", 15), fill="white")
        warning_background = self.lights_canvas.create_rectangle(80, 120, 220, 170, fill=WARNING_PANEL_COLOR)
        self.lights_canvas.tag_lower(warning_background, self.group_message)

        # Initialize lights to off state
        self.turn_off_yellow_light()
        self.turn_off_blue_light()
        self.turn_off_green_light()
        self.turn_off_red_light()

    def setup_temperature_frame(self):
        """Set up the frame and widgets for the temperature display."""
        self.temperature_frame = ttk.Frame(self.root, width=200, height=400)
        self.temperature_frame.pack(side="right")

        # Frame for the graph
        self.graph_frame = ttk.Frame(self.temperature_frame)
        self.graph_frame.pack(side="left")

        # Frame for the thermometer
        self.thermometer_frame = ttk.Frame(self.temperature_frame)
        self.thermometer_frame.pack()

        # Canvas for the thermometer
        self.temperature_canvas = ttk.Canvas(self.thermometer_frame, width=200, height=400, bg="skyblue")
        self.temperature_canvas.pack()

        # Red bar indicating temperature
        self.red_bar = self.temperature_canvas.create_rectangle(110, 225, 88, 350, fill="red")

        # Load and display thermometer image
        image_path = os.path.join(RESOURCES_DIR, "thermometer.png")
        try:
            image = Image.open(image_path)
            resized_img = image.resize((70, 350))
            self.thermometer_image = ImageTk.PhotoImage(resized_img)
            self.temperature_canvas.create_image(100, 200, image=self.thermometer_image)
        except Exception as e:
            print(f"Error loading thermometer image: {e}")

    def snooze_click(self):
        """Handle SNOOZE button click."""
        if self.snooze:
            self.subscriber.client.publish("/ic/Grupo3_APP/snooze", 0)
            print("Snooze deactivated!")
        else:
            self.subscriber.client.publish("/ic/Grupo3_APP/snooze", 1)
            print("Snooze activated!")
        self.snooze = not self.snooze

    def update_thermometer(self, value):
        """Update the thermometer display based on the new temperature value."""
        red_bar_height = 225 - (value * 2.6)
        self.temperature_canvas.coords(self.red_bar, 110, red_bar_height, 88, 350)

    def turn_on_red_light(self):
        """Turn on the red light indicator."""
        self.lights_canvas.create_oval(65, 155, 25, 195, fill=RED_LIGHT_ON_COLOR, outline="black", width="1")

    def turn_off_red_light(self):
        """Turn off the red light indicator."""
        self.lights_canvas.create_oval(65, 155, 25, 195, fill=RED_LIGHT_OFF_COLOR, outline="black", width="1")
        self.lights_canvas.create_oval(65, 155, 25, 195, outline="gray7", width="3")

    def turn_on_green_light(self):
        """Turn on the green light indicator."""
        self.lights_canvas.create_oval(65, 105, 25, 145, fill=GREEN_LIGHT_ON_COLOR, outline="black", width="1")

    def turn_off_green_light(self):
        """Turn off the green light indicator."""
        self.lights_canvas.create_oval(65, 105, 25, 145, fill=GREEN_LIGHT_OFF_COLOR, outline="black", width="1")
        self.lights_canvas.create_oval(65, 105, 25, 145, outline="gray7", width="3")

    def turn_on_blue_light(self):
        """Turn on the blue light indicator."""
        self.lights_canvas.create_oval(65, 55, 25, 95, fill=BLUE_LIGHT_ON_COLOR, outline="black", width="1")

    def turn_off_blue_light(self):
        """Turn off the blue light indicator."""
        self.lights_canvas.create_oval(65, 55, 25, 95, fill=BLUE_LIGHT_OFF_COLOR, outline="black", width="1")
        self.lights_canvas.create_oval(65, 55, 25, 95, outline="gray7", width="3")

    def turn_on_yellow_light(self):
        """Turn on the yellow light indicator."""
        self.lights_canvas.create_oval(65, 5, 25, 45, fill=YELLOW_LIGHT_ON_COLOR, outline="black", width="1")

    def turn_off_yellow_light(self):
        """Turn off the yellow light indicator."""
        self.lights_canvas.create_oval(65, 5, 25, 45, fill=YELLOW_LIGHT_OFF_COLOR, outline="black", width="1")
        self.lights_canvas.create_oval(65, 5, 25, 45, outline="gray7", width="3")

    def toggle_red_light(self):
        """Toggle the red light on and off for blinking effect."""
        while self.is_blinking:
            if self.red_light_state:
                self.turn_off_red_light()
            else:
                self.turn_on_red_light()
            self.red_light_state = not self.red_light_state
            time.sleep(self.blink_interval)

    def start_blinking(self):
        """Start the red light blinking."""
        self.is_blinking = True
        self.blink_thread = threading.Thread(target=self.toggle_red_light)
        self.blink_thread.daemon = True
        self.blink_thread.start()

    def stop_blinking(self):
        """Stop the red light blinking."""
        self.is_blinking = False
        self.turn_off_red_light()

    def refresh_temperature(self, new_temperature):
        """Refresh the temperature display with a new temperature value."""
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")

        # Update the temperature storage and timestamps
        self.temperature_timestamp = self.temperature_timestamp[1:]
        self.temperature_timestamp.append(timestamp)

        self.temperature_storage = self.temperature_storage[1:]
        self.temperature_storage.append(new_temperature)

        # Generate the updated temperature graph and update the thermometer display
        self.generate_temperature_graph()
        self.update_thermometer(new_temperature)

    def generate_temperature_graph(self):
        """Generate the temperature graph from stored temperature data."""
        graph_width = 800
        graph_height = 400

        # Plot the temperature data
        plt.plot(self.temperature_timestamp, self.temperature_storage)
        plt.xlabel("Timestamp")
        plt.ylabel("Temperature")
        plt.xticks(fontsize=4)
        graph_path = os.path.join(RESOURCES_DIR, "temperature_register.png")
        plt.savefig(graph_path)
        plt.close()

        try:
            # Load and resize the graph image
            image1 = Image.open(graph_path)
            image2 = image1.resize((graph_width, graph_height))
            photo = ImageTk.PhotoImage(image2)

            # Update the graph label in the GUI
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
        """Clear all widgets in the graph frame."""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def warning_panel_message(self, new_message):
        """Update the warning panel message."""
        self.lights_canvas.itemconfig(self.warning_message, text=new_message)

    def group_panel_message(self, new_message):
        """Update the group panel message."""
        self.lights_canvas.itemconfig(self.group_message, text=new_message)


class Subscriber:
    """
    Subscriber class for handling MQTT connections and messages.
    """

    def __init__(self, root):
        self.client = mqtt.Client(client_id="Grupo3_Interface")
        self.GENERAL_TOPIC = "/ic/#"
        self.TOPIC = "/ic/Grupo3/"
        self.TOPIC_APP = "/ic/Grupo3_APP/"
        self.app = root

        # MQTT credentials
        self.USERNAME = "DuckNet"
        self.PASSWORD = "DuckieUPT"

    def run(self):
        """Run the MQTT client and set up callbacks."""
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
        """Callback for when the client connects to the broker."""
        if rc == 0:
            print("Connected to broker")
            self.client.subscribe(self.TOPIC + "#")
            self.client.subscribe("/ic/+/alarme")
            self.app.turn_on_green_light()
            self.app.warning_panel_message("OK")
            self.app.generate_temperature_graph()
        else:
            print("Connection failed with code", rc)

    def on_message(self, client, userdata, msg):
        """Callback for when a message is received from the broker."""
        print("Received message on topic:", msg.topic)
        print("Message payload:", msg.payload.decode())

        # Regex pattern to match alarm messages
        pattern = re.compile(r'^/ic/([a-zA-Z]+[0-24-9])/alarme$')

        if msg.topic == (self.TOPIC + "test"):
            print("TEST:", msg.payload.decode())
        elif msg.topic == (self.TOPIC + "temp"):
            temp = msg.payload.decode()
            temperature = float(temp)
            self.app.refresh_temperature(new_temperature=temperature)
            print("TEMP:", msg.payload.decode())
        elif msg.topic == (self.TOPIC + "fire"):
            if msg.payload.decode() == '0':
                self.app.stop_blinking()
                self.app.turn_on_green_light()
                self.app.system_ok = True
                self.app.system_fire = False
                self.app.warning_panel_message("OK")
            else:
                self.app.start_blinking()
                self.app.turn_on_red_light()
                self.app.turn_off_green_light()
                self.app.system_ok = False
                self.app.system_fire = True
                self.app.warning_panel_message("FIRE")
        elif msg.topic == (self.TOPIC + "alarme"):
            if msg.payload.decode() == '0':
                self.app.turn_off_blue_light()
            else:
                self.app.turn_on_blue_light()
        elif pattern.match(msg.topic):
            match = re.search(pattern, msg.topic)
            sender = match.group(1)
            if msg.payload.decode() == '0':
                self.app.turn_off_yellow_light()
                self.app.group_panel_message("")
            else:
                self.app.turn_on_yellow_light()
                self.app.group_panel_message(sender)


if __name__ == "__main__":
    # Instantiate and run the application
    app = IoTApplication()
    app.run()
