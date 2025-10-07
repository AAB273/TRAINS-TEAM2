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

        #input/output title labels
        inp_text = ttk.Label(self.leftFrame, text = "Inputs")
        inp_text.pack(side = "top")
        out_text = ttk.Label(self.rightFrame, text = "Outputs")
        out_text.pack(side = "top")

        self.create_inputs()

    
    #create the UI appearance, as well as bind buttons and data to functions
    def create_inputs(self):
        #create throughput input
        #changeable string variables for dynamic updating
        leaveValue = tk.StringVar()
        soldValue = tk.StringVar()

        #sub-frame to hold all throughput data for packing, plus title label
        tpFrame = ttk.Frame(self.leftFrame)
        tpFrame.pack(pady = 15, side = "top")
        tpText = ttk.Label(tpFrame, text = "Throughput")
        tpText.pack(side = "top")

        #sub-frame to hold the text entry for tickets sold
        soldFrame = ttk.Frame(tpFrame)
        soldFrame.pack(side = "top", fill = "x")
        soldText = ttk.Label(soldFrame, text = "Enter tickets sold:")
        soldText.pack(padx = 5, fill = "x")
        soldEntry = ttk.Entry(soldFrame, textvariable = soldValue)
        soldEntry.pack(padx = 5, fill = "x")
        #sub-frame to hold the text entry for people disembarking
        leaveFrame = ttk.Frame(tpFrame)
        leaveFrame.pack(side = "top", fill = "x")
        leaveText = ttk.Label(leaveFrame, text = "Enter tickets sold:")
        leaveText.pack(padx = 5, fill = "x")
        leaveEntry = ttk.Entry(leaveFrame, textvariable = leaveValue)
        leaveEntry.pack(padx = 5, fill = "x")

        #button that sends data to data file (error checking maybe needed for text entry)
        getTP = ttk.Button(tpFrame, text = "Submit", command = lambda: self.send_tp_data(soldValue.get(), leaveValue.get()))
        getTP.pack(side = "top")


        #create light state input
        #changeable string values for dynamic updating
        state = tk.StringVar()
        location = tk.StringVar()

        #sub-frame for all light state data for packing, plus title label
        lsFrame = ttk.Frame(self.leftFrame)
        lsFrame.pack(pady = 15, side = "top")
        lsText = ttk.Label(lsFrame, text = "Light State")
        lsText.pack(side = "top")

        #sub-frame for location text entry
        locFrame = ttk.Frame(lsFrame)
        locFrame.pack(side = "top", fill = "x")
        locText = ttk.Label(locFrame, text = "Enter location:")
        locText.pack(padx = 5, fill = "x")
        locEntry = ttk.Entry(locFrame, textvariable = location)
        locEntry.pack(padx = 5, fill = "x")
        #sub-frame for Combobox with light state choices
        stateFrame = ttk.Frame(lsFrame)
        stateFrame.pack(side = "top", fill = "x")
        locText = ttk.Label(stateFrame, text = "Enter light state:")
        locText.pack(padx = 5, fill = "x")
        locEntry = ttk.Combobox(stateFrame, textvariable = state)
        locEntry["values"] = ["red", "yellow", "green", "supergreen"]
        locEntry["state"] = "readonly"
        locEntry.pack(padx = 5, fill = "x")

        #button to send data to data file
        getLS = ttk.Button(lsFrame, text = "Submit", command = lambda: self.send_ls_data(location.get(), state.get()))
        getLS.pack(side = "top")
    

    #formatting function that sends throughput data to the data file
    def send_tp_data(self, sold, leave):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("TP\n")
        outfile.write(sold + "\n")
        outfile.write(leave + "\n")
        outfile.write("blue")
        outfile.close()


    #formatting function that sends light state data to the data file
    def send_ls_data(self, location, state):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("LS\n")
        outfile.write(location + "\n")
        #write binary code for light state to simulate input from wayside controller
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