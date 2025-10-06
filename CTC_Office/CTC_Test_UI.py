import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class TestUI:
    def __init__(self, win):
        #create the test UI layout
        self.win = win
        self.win.title("Test UI")  #title of the window
        self.win.geometry("250x250+1300+0")

        #two sub-frames to split in half
        self.left_frame = ttk.Frame(self.win)
        self.left_frame.pack(side = "left", expand = True, fill = "y")
        self.right_frame = ttk.Frame(self.win)
        self.right_frame.pack(side = "left", expand = True, fill = "y")

        inp_text = ttk.Label(self.left_frame, text = "Inputs")
        inp_text.pack(side = "top")
        out_text = ttk.Label(self.right_frame, text = "Outputs")
        out_text.pack(side = "top")

    
    def write_value(self):
        outfile = open("CTC_Office/CTC_data.txt", "a")
        outfile.write("hello\n")
        outfile.close()

        