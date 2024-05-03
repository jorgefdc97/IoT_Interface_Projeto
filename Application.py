import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

RED_LIGHT_OFF_COLOR = "indianred4"
RED_LIGHT_ON_COLOR = "red3"
GREEN_LIGHT_OFF_COLOR = "chartreuse4"
GREEN_LIGHT_ON_COLOR = "chartreuse2"
WARNING_PANEL_COLOR = "gray11"

SCRIPT_PATH = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(SCRIPT_PATH, "resources")
APPLICATION_NAME = "Internet of Things"


def update_thermometer(value):
    slider_value = int(value)
    red_bar_height = 350 - (slider_value * 3.5)
    temperature_canvas.coords(red_bar, 110, red_bar_height, 88, 350)


def turn_off_red_light():
    lights_canvas.create_oval(65, 5, 25, 45, fill=RED_LIGHT_OFF_COLOR, outline="black", width="1")
    lights_canvas.create_oval(65, 5, 25, 45, outline="gray7", width="3")

def turn_off_green_light():
    lights_canvas.create_oval(65, 55, 25, 95, fill=GREEN_LIGHT_OFF_COLOR, outline="black", width="1")
    lights_canvas.create_oval(65, 55, 25, 95, outline="gray7", width="3")

def turn_on_red_light():
    lights_canvas.create_oval(65, 5, 25, 45, fill=RED_LIGHT_ON_COLOR, outline="black", width="1")


def turn_on_green_light():
    lights_canvas.create_oval(65, 55, 25, 95, fill=GREEN_LIGHT_ON_COLOR, outline="black", width="1")


def warning_panel_message():
    return

def generate_temperature_graph():
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

    image1 = Image.open(graph_path)
    image2 = image1.resize((graph_width, graph_height))
    photo = ImageTk.PhotoImage(image2)

    label = tk.Label(graph_frame, image=photo, width=graph_width, height=graph_height)
    label.image = photo  # Keep a reference to avoid garbage collection
    label.pack()


root = ttk.Window(themename="darkly")
root.title(APPLICATION_NAME)
root.geometry("1280x680")
root.iconbitmap("")

# lights
lights_frame = tk.Frame(root, width=400, height=100)
lights_frame.configure()
lights_frame.pack(side="left", pady=5)

lights_canvas = ttk.Canvas(lights_frame, width=300, height=100)
lights_canvas.pack()

warning_message = lights_canvas.create_text(150, 45, text="WARNING", font=("Digital-7", 25), fill="white")
warning_background = lights_canvas.create_rectangle(80, 20, 220, 70, fill=WARNING_PANEL_COLOR)
lights_canvas.tag_lower(warning_background, warning_message)
turn_off_red_light()
turn_off_green_light()

# temperature
temperature_frame = ttk.Frame(root, width=200, height=400)

temperature_frame.pack(side="right")
graph_frame = ttk.Frame(temperature_frame)
graph_frame.pack(side="left")

thermometer_frame = ttk.Frame(temperature_frame)
thermometer_frame.pack()

temperature_canvas = ttk.Canvas(thermometer_frame, width=200, height=400)
temperature_canvas.configure(bg="skyblue")
temperature_canvas.pack()

generate_temperature_graph()


image_path = os.path.join(RESOURCES_DIR, "thermometer.png")
red_bar = temperature_canvas.create_rectangle(110, 277, 88, 350, fill="red")

try:
    image = Image.open(image_path)
    resized_img = image.resize((70, 350))
    thermometer_image = ImageTk.PhotoImage(resized_img)
    temperature_canvas.create_image(100, 200, image=thermometer_image)
except tk.TclError as e:
    print("Error loading image:", e)

# slider to simulate temperature change
# replace later with input values from arduino
slider = tk.Scale(temperature_frame, from_=21, to=80, orient=ttk.HORIZONTAL, command=update_thermometer)
slider.pack()

#button to change collor
ttk.Button(lights_frame, text="Turn on Red", command=turn_on_red_light, padding=10).pack()
ttk.Button(lights_frame, text="Turn off Red", command=turn_off_red_light, padding=10).pack()
ttk.Button(lights_frame, text="Turn on Green", command=turn_on_green_light, padding=10).pack()
ttk.Button(lights_frame, text="Turn off Green", command=turn_off_green_light, padding=10).pack()


root.mainloop()
