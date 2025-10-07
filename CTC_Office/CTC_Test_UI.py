import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class TestUI:
    def __init__(self, win):
        #create the test UI layout
        self.win = win
        self.win.title("Test UI")  #title of the window
        self.win.geometry("250x750+1300+0")

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
        #create throughput input
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

        #create light state input
        state = tk.StringVar()
        location = tk.StringVar()

        lsFrame = ttk.Frame(self.leftFrame)
        lsFrame.pack(pady = 15, side = "top")
        lsText = ttk.Label(lsFrame, text = "Light State")
        lsText.pack(side = "top")

        locFrame = ttk.Frame(lsFrame)
        locFrame.pack(side = "top", fill = "x")
        locText = ttk.Label(locFrame, text = "Enter location:")
        locText.pack(padx = 5, fill = "x")
        locEntry = ttk.Entry(locFrame, textvariable = location)
        locEntry.pack(padx = 5, fill = "x")

        stateFrame = ttk.Frame(lsFrame)
        stateFrame.pack(side = "top", fill = "x")
        locText = ttk.Label(stateFrame, text = "Enter light state:")
        locText.pack(padx = 5, fill = "x")
        locEntry = ttk.Combobox(stateFrame, textvariable = state)
        locEntry["values"] = ["red", "yellow", "green", "supergreen"]
        locEntry["state"] = "readonly"
        locEntry.pack(padx = 5, fill = "x")

        getLS = ttk.Button(lsFrame, text = "Submit", command = lambda: self.send_ls_data(location.get(), state.get()))
        getLS.pack(side = "top")
    

    def send_tp_data(self, sold, leave):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("TP\n")
        outfile.write(sold + "\n")
        outfile.write(leave + "\n")
        outfile.write("blue")
        outfile.close()


    def send_ls_data(self, location, state):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("LS\n")
        outfile.write(location + "\n")
        if (state == "red"):
            outfile.write("00\n")
        elif (state == "yellow"):
            outfile.write("01\n")
        elif (state == "green"):
            outfile.write("10\n")
        else:
            outfile.write("11\n")    

        outfile.write("blue")
        outfile.close()