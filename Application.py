import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk


def update_thermometer(value):
    slider_value = int(value)
    red_bar_height = 350 - (slider_value * 3.5)
    temperature_canvas.coords(red_bar, 110, red_bar_height, 88, 350)


SCRIPT_PATH = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(SCRIPT_PATH, "resources")
APPLICATION_NAME = "Internet of Things"

root = ttk.Window(themename="darkly")
root.title(APPLICATION_NAME)
root.geometry("1280x680")
root.iconbitmap("")

title_label = ttk.Label(master=root, text="Title")

# lights
lights_frame = tk.Canvas(root, width=400, height=100)
lights_frame.pack(side="top", pady=50)

lights_canvas = ttk.Canvas(lights_frame, width=300, height=100)
lights_canvas.pack()
red_light = lights_canvas.create_oval(75, 75, 5, 5, fill="red", outline="black", width="4")
green_light = lights_canvas.create_oval(295, 75, 220, 5, fill="green", outline="black", width="4", )

# temperature
temperature_frame = ttk.Frame(root, width=200, height=400)

temperature_frame.pack(side="right")

temperature_canvas = ttk.Canvas(temperature_frame, width=200, height=400)
temperature_canvas.configure(bg="skyblue")
temperature_canvas.pack()

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

root.mainloop()
