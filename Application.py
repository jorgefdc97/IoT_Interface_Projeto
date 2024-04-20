import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk

SCRIPT_PATH = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(SCRIPT_PATH, "resources")
APPLICATION_NAME = "Internet of Things"

root = ttk.Window(themename="darkly")
root.title(APPLICATION_NAME)
root.geometry("1280x680")
root.iconbitmap("")

title_label = ttk.Label(master=root, text="Title")



root.mainloop()
