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
        self.leftFrame = ttk.Frame(self.win)
        self.leftFrame.pack(side = "left", expand = True, fill = "y")
        self.rightFrame = ttk.Frame(self.win)
        self.rightFrame.pack(side = "left", expand = True, fill = "y")

        inp_text = ttk.Label(self.leftFrame, text = "Inputs")
        inp_text.pack(side = "top")
        out_text = ttk.Label(self.rightFrame, text = "Outputs")
        out_text.pack(side = "top")

        self.create_inputs()

        
    def write_value(self):
        outfile = open("CTC_Office/CTC_data.txt", "a")
        outfile.write("hello\n")
        outfile.close()

    
    def create_inputs(self):
        #create throughput
        leaveValue = tk.StringVar()
        soldValue = tk.StringVar()

        tpFrame = ttk.Frame(self.leftFrame)
        tpFrame.pack(pady = 15, side = "top")
        tpText = ttk.Label(tpFrame, text = "Throughput")
        tpText.pack(side = "top")

        soldFrame = ttk.Frame(tpFrame)
        soldFrame.pack(side = "top", fill = "x")
        soldText = ttk.Label(soldFrame, text = "Enter tickets sold:")
        soldText.pack(padx = 5, fill = "x")
        soldEntry = ttk.Entry(soldFrame, textvariable = soldValue)
        soldEntry.pack(padx = 5, fill = "x")

        leaveFrame = ttk.Frame(tpFrame)
        leaveFrame.pack(side = "top", fill = "x")
        leaveText = ttk.Label(leaveFrame, text = "Enter tickets sold:")
        leaveText.pack(padx = 5, fill = "x")
        leaveEntry = ttk.Entry(leaveFrame, textvariable = leaveValue)
        leaveEntry.pack(padx = 5, fill = "x")

        getTP = ttk.Button(tpFrame, text = "Submit", command = lambda: self.send_tp_data(soldValue.get(), leaveValue.get()))
        getTP.pack(side = "top")
    

    def send_tp_data(self, sold, leave):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("TP\n")
        outfile.write(sold + "\n")
        outfile.write(leave + "\n")
        outfile.write("blue")
        outfile.close()