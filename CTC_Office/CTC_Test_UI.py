import tkinter as tk
from tkinter import ttk

class TestUI:
    def __init__(self, win):
        #create the test UI layout
        self.win = win
        self.win.title("Test UI")  #title of the window
        self.win.geometry("450x750+1210+0")

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

        #create the areas to hold output data
        #for deployed trains
        dtFrame = ttk.Frame(self.rightFrame)
        dtFrame.pack(pady = 15, side = "top")
        dtText = ttk.Label(dtFrame, text = "Suggested Speed/Authority")
        dtText.pack(side = "top")

        dtTrainFrame = ttk.Frame(dtFrame)
        dtTrainFrame.pack(side = "top")
        dtTrainText = ttk.Label(dtTrainFrame, text = "Train:")
        dtTrainText.pack(side = "left", padx = 5, expand = True)
        self.dtTrainOutput = ttk.Label(dtTrainFrame, text = "(None)")
        self.dtTrainOutput.pack(side = "left", expand = True)

        dtSpeedFrame = ttk.Frame(dtFrame)
        dtSpeedFrame.pack(side = "top")
        dtSpeedText = ttk.Label(dtSpeedFrame, text = "Suggested Speed:")
        dtSpeedText.pack(side = "left", padx = 5, expand = True)
        self.dtSpeedOutput = ttk.Label(dtSpeedFrame, text = "(None)")
        self.dtSpeedOutput.pack(side = "left", expand = True)

        dtAuthFrame = ttk.Frame(dtFrame)
        dtAuthFrame.pack(side = "top")
        dtAuthText = ttk.Label(dtAuthFrame, text = "Suggested Authority:")
        dtAuthText.pack(side = "left", padx = 5, expand = True)
        self.dtAuthOutput = ttk.Label(dtAuthFrame, text = "(None)")
        self.dtAuthOutput.pack(side = "left", expand = True)


        #for maintenance mode output data
        mmFrame = ttk.Frame(self.rightFrame)
        mmFrame.pack(pady = 15, side = "top")
        mmText = ttk.Label(mmFrame, text = "Maintenance Mode")
        mmText.pack(side = "top") 

        mmLocFrame = ttk.Frame(mmFrame)
        mmLocFrame.pack(side = "top")
        mmLocText = ttk.Label(mmLocFrame, text = "Location:")
        mmLocText.pack(side = "left", padx = 5, expand = True)
        self.mmLocOutput = ttk.Label(mmLocFrame, text = "(None)")
        self.mmLocOutput.pack(side = "left", expand = True)

        mmSentFrame = ttk.Frame(mmFrame)
        mmSentFrame.pack(side = "top")
        mmSentText = ttk.Label(mmSentFrame, text = "Signal sent: ")
        mmSentText.pack(side = "left", padx = 5, expand = True)
        self.mmSentOutput = ttk.Label(mmSentFrame, text = "(None)")
        self.mmSentOutput.pack(side = "left", expand = True)


        #for train state output data
        tsFrame = ttk.Frame(self.rightFrame)
        tsFrame.pack(pady = 15, side = "top")
        tsText = ttk.Label(tsFrame, text = "Track State")
        tsText.pack(side = "top")

        tsLocFrame = ttk.Frame(tsFrame)
        tsLocFrame.pack(side = "top")
        tsLocText = ttk.Label(tsLocFrame, text = "Location:")
        tsLocText.pack(side = "left", padx = 5, expand = True)
        self.tsLocOutput = ttk.Label(tsLocFrame, text = "(None)")
        self.tsLocOutput.pack(side = "left", expand = True)
        
        tsSentFrame = ttk.Frame(tsFrame)
        tsSentFrame.pack(side = "top")
        tsSentText = ttk.Label(tsSentFrame, text = "Signal sent: ")
        tsSentText.pack(side = "left", padx = 5, expand = True)
        self.tsSentOutput = ttk.Label(tsSentFrame, text = "(None)")
        self.tsSentOutput.pack(side = "left", expand = True)

        self.create_inputs()


    def updateTestUI(self):
        infile = open("CTC_Office/to_test_ui.txt", "r")  #read in the data file text
        data = infile.readline()  #grab the first line to see what data needs to be updated

        if (data.strip() == "TL"):
            train = infile.readline().strip()
            speed = float(infile.readline().strip())
            auth = infile.readline().strip()
            line = infile.readline().strip()

            speed *= 2.237            

            self.dtTrainOutput.config(text = "Train " + train + ", " + line + " line")
            self.dtSpeedOutput.config(text = f"{speed:.2f} mph")
            self.dtAuthOutput.config(text = auth + " blocks")

        elif (data.strip() == "MM"):
            location = infile.readline().strip()
            direction = infile.readline().strip()
            line = infile.readline().strip()

            self.mmLocOutput.config(text = "Block " + location + ", " + line + " line")
            self.mmSentOutput.config(text = "Yes, pointed at block " + direction)

        elif (data.strip() == "TS"):
            location = infile.readline().strip()
            line = infile.readline().strip()

            self.tsLocOutput.config(text = "Block " + location + ", " + line + " line")
            self.tsSentOutput.config(text = "Yes")

        
        infile.close()
        reset = open("CTC_Office/to_test_ui.txt", "w")
        reset.close()

    
    #create the UI appearance, as well as bind buttons and data to functions
    def create_inputs(self):
        #configure button appearance
        button_style = ttk.Style()
        button_style.configure("normal.TButton", font = ("Arial", 10))  #change text style


        #create track state input
        #changeable string variablesfor dynamic updating
        errorLocation = tk.StringVar()

        #sub-frame to hold all track state data for packing, plus title label
        tsFrame = ttk.Frame(self.leftFrame)
        tsFrame.pack(pady = 15, side = "top")
        tsText = ttk.Label(tsFrame, text = "Track State")
        tsText.pack(side = "top")
        #sub-frame to hold the text entry for location
        tsLocFrame = ttk.Frame(tsFrame)
        tsLocFrame.pack(side = "top", fill = "x")
        tsLocText = ttk.Label(tsLocFrame, text = "Enter location:")
        tsLocText.pack(padx = 5, fill = "x")
        tsLocEntry = ttk.Entry(tsLocFrame, textvariable = errorLocation)
        tsLocEntry.pack(padx = 5, fill = "x")

        #button that sends data to data file (error checking needed for text entry)
        getLS = ttk.Button(tsFrame, text = "Submit", style = "normal.TButton", command = lambda: self.send_ts_data(errorLocation.get()))
        getLS.pack(side = "top")


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

        #button that sends data to data file (error checking needed for text entry)
        getTP = ttk.Button(tpFrame, text = "Submit", style = "normal.TButton", command = lambda: self.send_tp_data(soldValue.get(), leaveValue.get()))
        getTP.pack(side = "top")


        #create light state input
        #changeable string values for dynamic updating
        lightState = tk.StringVar()
        lightLocation = tk.StringVar()

        #sub-frame for all light state data for packing, plus title label
        lsFrame = ttk.Frame(self.leftFrame)
        lsFrame.pack(pady = 15, side = "top")
        lsText = ttk.Label(lsFrame, text = "Light State")
        lsText.pack(side = "top")
        #sub-frame for location text entry
        lsLocFrame = ttk.Frame(lsFrame)
        lsLocFrame.pack(side = "top", fill = "x")
        lsLocText = ttk.Label(lsLocFrame, text = "Enter location:")
        lsLocText.pack(padx = 5, fill = "x")
        lsLocEntry = ttk.Entry(lsLocFrame, textvariable = lightLocation)
        lsLocEntry.pack(padx = 5, fill = "x")
        #sub-frame for Combobox with light state choices
        lsStateFrame = ttk.Frame(lsFrame)
        lsStateFrame.pack(side = "top", fill = "x")
        lsStateText = ttk.Label(lsStateFrame, text = "Enter light state:")
        lsStateText.pack(padx = 5, fill = "x")
        lsStateEntry = ttk.Combobox(lsStateFrame, textvariable = lightState)
        lsStateEntry["values"] = ["red", "yellow", "green", "supergreen"]
        lsStateEntry["state"] = "readonly"
        lsStateEntry.pack(padx = 5, fill = "x")

        #button to send data to data file
        getLS = ttk.Button(lsFrame, text = "Submit", style = "normal.TButton", command = lambda: self.send_ls_data(lightLocation.get(), lightState.get()))
        getLS.pack(side = "top")


        #create railroad crossing input
        #changeable string values for dynamic updating
        crossingState = tk.StringVar()
        crossingLocation = tk.StringVar()

        #sub-frame for all crossing data for packing, plus title label
        rcFrame = ttk.Frame(self.leftFrame)
        rcFrame.pack(pady = 15, side = "top")
        rcText = ttk.Label(rcFrame, text = "Railway Crossing")
        rcText.pack(side = "top")
        #sub-frame for location text entry
        rcLocFrame = ttk.Frame(rcFrame)
        rcLocFrame.pack(side = "top", fill = "x")
        rcLocText = ttk.Label(rcLocFrame, text = "Enter location:")
        rcLocText.pack(padx = 5, fill = "x")
        rcLocEntry = ttk.Entry(rcLocFrame, textvariable = crossingLocation)
        rcLocEntry.pack(padx = 5, fill = "x")
        #sub-frame for Combobox with crossing choices
        rcStateFrame = ttk.Frame(rcFrame)
        rcStateFrame.pack(side = "top", fill = "x")
        rcStateText = ttk.Label(rcStateFrame, text = "Enter crossing state:")
        rcStateText.pack(padx = 5, fill = "x")
        rcStateEntry = ttk.Combobox(rcStateFrame, textvariable = crossingState)
        rcStateEntry["values"] = ["inactive", "active"]
        rcStateEntry["state"] = "readonly"
        rcStateEntry.pack(padx = 5, fill = "x")

        #button to send data to data file
        getRC = ttk.Button(rcFrame, text = "Submit", style = "normal.TButton", command = lambda: self.send_rc_data(crossingLocation.get(), crossingState.get()))
        getRC.pack(side = "top")


#formatting function that sends light state data to the data file
    def send_ts_data(self, location):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("TS\n")
        outfile.write(location + "\n")
        outfile.write("blue")
        outfile.close()


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

    
    #formatting function that sends light state data to the data file
    def send_rc_data(self, location, state):
        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("RC\n")
        outfile.write(location + "\n")
        if (state == "inactive"):
            outfile.write("0\n")
        else:
            outfile.write("1\n")
        outfile.write("blue")
        outfile.close()