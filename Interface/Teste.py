import tkinter as tk
import os
from PIL import Image, ImageTk


class Application:
    SCRIPT_PATH = os.path.dirname(__file__)
    RESOURCES_DIR = os.path.join(SCRIPT_PATH, "resources")

    def __init__(self, master):
        self.master = master
        self.master.title("Thermometer App")

        # Create a Canvas widget
        self.canvas = tk.Canvas(self.master, width=200, height=400)
        self.canvas.pack()

        # Load the thermometer image
        image_path = os.path.join(self.RESOURCES_DIR, "thermometer.png")

        # Create a rectangle to represent the red bar
        self.red_bar = self.canvas.create_rectangle(106, 350, 91, 350, fill="red")

        try:
            image = Image.open(image_path)
            img = image.resize((50, 200))
            # Load the thermometer image
            self.thermometer_image = ImageTk.PhotoImage(img)

            # Resize image

            # Display the thermometer image on the canvas
            self.canvas.create_image(100, 300, image=self.thermometer_image)
        except tk.TclError as e:
            print("Error loading image:", e)

        # Create a Scale widget (slider)
        self.slider = tk.Scale(self.master, from_=0, to=36, orient=tk.HORIZONTAL, command=self.update_thermometer)
        self.slider.pack()

    def update_thermometer(self, value):
        # Update the height of the red bar according to the slider value
        slider_value = int(value)
        red_bar_height = 350 - (slider_value * 3.5)  # Each unit of the slider represents 3.5 pixels
        self.canvas.coords(self.red_bar, 106, red_bar_height, 91, 350)


def main():
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
