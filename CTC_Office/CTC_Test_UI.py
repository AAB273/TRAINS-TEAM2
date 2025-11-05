import tkinter as tk
from tkinter import ttk

class TestUI:
#"Test UI" ui screen appearance and data

    
    '''
    Attributes:

    self.win: main Tk() variable for the test ui window

    ttk.Frame variables
    self.leftFrame: sub-frame to halve the window
    self.rightFrame: sub-frame to halve the window

    ttk.Entry and ttk.Combobox variables
    self.dtTrainOutput: train number to display on the deployed train output section
    self.dtSpeedOutput: suggested speed to display on the deployed train output section
    self.dtAuthOutput: suggested authority to display on the deployed train output section
    self.mmLocOutput: location to display on the maintenance mode output section
    self.mmSentOutput: signal sent (yes/no) to display on the maintenance mode output section
    self.tsLocOutput: location to display on the track state output section
    self.tsSentOutput: signal sent (yes/no) to display on the track state output section
    '''

    def __init__(self, win: tk.Tk):
    #initialize variables and create layout for ui screen

        self.win = win
        self.win.title("Test UI")
        self.win.geometry("450x750+1210+0")
        #format window

        #two sub-frames to split in half
        self.leftFrame = ttk.Frame(self.win)
        self.leftFrame.pack(side = "left", expand = True, fill = "y")
        self.rightFrame = ttk.Frame(self.win)
        self.rightFrame.pack(side = "left", expand = True, fill = "y")
        #create a sub-frame for each side of the screen to center all widgets

        inpText = ttk.Label(self.leftFrame, text = "Inputs")
        inpText.pack(side = "top")
        outText = ttk.Label(self.rightFrame, text = "Outputs")
        outText.pack(side = "top")
        #input/output title Labels

        self.server = TrainSocketServer(port=12346, ui_id="CTC_Test_UI")
        self.server.set_allowed_connections(["CTC", "ui_3"])
        
        self.server.start_server(self._processMessage)
        self.server.connect_to_ui('localhost', 12341, "CTC")

        self.createInputs()
        self.createOutputs()

###############################################################################################################################################################

    def updateTestUI(self):
    #update test ui values to show the user inputs/outputs to/from the system

        infile = open("CTC_Office/to_test_ui.txt", "r")
        data = infile.readline()

        if (data.strip() == "TL"):
        #train location/deployed train case
            train = infile.readline().strip()
            speed = float(infile.readline().strip())
            auth = infile.readline().strip()
            line = infile.readline().strip()
            #grab all data

            speed *= 2.237 
            #change speed to mph           

            self.dtTrainOutput.config(text = "Train " + train + ", " + line + " line")
            self.dtSpeedOutput.config(text = f"{speed:.3f} mph")
            self.dtAuthOutput.config(text = auth + " blocks")
            #display outputs on screen

        elif (data.strip() == "MM"):
        #maintenance mode case
            location = infile.readline().strip()
            direction = infile.readline().strip()
            line = infile.readline().strip()
            #grab data

            self.mmLocOutput.config(text = "Block " + location + ", " + line + " line")
            self.mmSentOutput.config(text = "Yes, pointed at block " + direction)
            #display outputs on screen

        elif (data.strip() == "TS"):
        #track state case
            location = infile.readline().strip()
            line = infile.readline().strip()
            #grab data

            self.tsLocOutput.config(text = "Block " + location + ", " + line + " line")
            self.tsSentOutput.config(text = "Yes")
            #display outputs on screen

        
        infile.close()
        reset = open("CTC_Office/to_test_ui.txt", "w")
        reset.close()
        #close and wipe the dat file

###############################################################################################################################################################
    
    def createInputs(self):
    #create the area where outputs are shown to the user
        
        buttonStyle = ttk.Style()
        buttonStyle.configure("normal.TButton", font = ("Arial", 10))
        #configure button appearance


        '''
        block error area
        '''
        errorLocation = tk.StringVar()
        #changeable string variable for dynamic updating

        tsFrame = ttk.Frame(self.leftFrame)
        tsFrame.pack(pady = 15, side = "top")
        #sub-frame to hold all track state widgets
        tsText = ttk.Label(tsFrame, text = "Block Errors")
        tsText.pack(side = "top")
        #"Track State" title Label

        tsLocFrame = ttk.Frame(tsFrame)
        tsLocFrame.pack(side = "top", fill = "x")
        #sub-frame to hold schedule train location widgets
        tsLocText = ttk.Label(tsLocFrame, text = "Enter location:")
        tsLocText.pack(padx = 5, fill = "x")
        tsLocEntry = ttk.Entry(tsLocFrame, textvariable = errorLocation)
        tsLocEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and an Entry to grab user data

        getLS = ttk.Button(tsFrame, text = "Submit", style = "normal.TButton", command = lambda: self.sendTSData(errorLocation.get()))
        getLS.pack(side = "top")
        #button that sends data to data file (error checking needed for text entry)


        '''
        throughput area
        '''
        leaveValue = tk.StringVar()
        soldValue = tk.StringVar()
        #changeable string variables for dynamic updating

        tpFrame = ttk.Frame(self.leftFrame)
        tpFrame.pack(pady = 15, side = "top")
        #sub-frame to hold all throughput widgets
        tpText = ttk.Label(tpFrame, text = "Throughput")
        tpText.pack(side = "top")
        #"Throughput" title Label

        soldFrame = ttk.Frame(tpFrame)
        soldFrame.pack(side = "top", fill = "x")
        #sub-frame to hold schedule tickets sold input data
        soldText = ttk.Label(soldFrame, text = "Enter tickets sold:")
        soldText.pack(padx = 5, fill = "x")
        soldEntry = ttk.Entry(soldFrame, textvariable = soldValue)
        soldEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and an Entry to grab user data

        leaveFrame = ttk.Frame(tpFrame)
        leaveFrame.pack(side = "top", fill = "x")
        #sub-frame to hold schedule people disembarking input data
        leaveText = ttk.Label(leaveFrame, text = "Enter tickets sold:")
        leaveText.pack(padx = 5, fill = "x")
        leaveEntry = ttk.Entry(leaveFrame, textvariable = leaveValue)
        leaveEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and an Entry to grab user data

        getTP = ttk.Button(tpFrame, text = "Submit", style = "normal.TButton", command = lambda: self.sendTPData(soldValue.get(), leaveValue.get()))
        getTP.pack(side = "top")
        #button that sends data to data file (error checking needed for text entry)


        '''
        light state area
        '''
        lightState = tk.StringVar()
        lightLocation = tk.StringVar()
        #changeable string values for dynamic updating

        lsFrame = ttk.Frame(self.leftFrame)
        lsFrame.pack(pady = 15, side = "top")
        #sub-frame for all light state data widgets
        lsText = ttk.Label(lsFrame, text = "Light State")
        lsText.pack(side = "top")
        #"Light State" title Label
        
        lsLocFrame = ttk.Frame(lsFrame)
        lsLocFrame.pack(side = "top", fill = "x")
        #sub-frame for light state location input data
        lsLocText = ttk.Label(lsLocFrame, text = "Enter location:")
        lsLocText.pack(padx = 5, fill = "x")
        lsLocEntry = ttk.Entry(lsLocFrame, textvariable = lightLocation)
        lsLocEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and an Entry to grab user data

        lsStateFrame = ttk.Frame(lsFrame)
        lsStateFrame.pack(side = "top", fill = "x")
        #sub-frame for light state state input data
        lsStateText = ttk.Label(lsStateFrame, text = "Enter light state:")
        lsStateText.pack(padx = 5, fill = "x")
        lsStateEntry = ttk.Combobox(lsStateFrame, textvariable = lightState)
        lsStateEntry["values"] = ["red", "yellow", "green", "supergreen"]
        lsStateEntry["state"] = "readonly"
        lsStateEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and a Combobox to grab user data

        getLS = ttk.Button(lsFrame, text = "Submit", style = "normal.TButton", command = lambda: self.sendLSData(lightLocation.get(), lightState.get()))
        getLS.pack(side = "top")
        #button to send data to data file


        '''
        railway crossing area
        '''
        crossingState = tk.StringVar()
        crossingLocation = tk.StringVar()
        #changeable string values for dynamic updating

        rcFrame = ttk.Frame(self.leftFrame)
        rcFrame.pack(pady = 15, side = "top")
        #sub-frame for all railway crossing widgets
        rcText = ttk.Label(rcFrame, text = "Railway Crossing")
        rcText.pack(side = "top")
        #"Railway Crossing" title Label

        rcLocFrame = ttk.Frame(rcFrame)
        rcLocFrame.pack(side = "top", fill = "x")
        #sub-frame for railway crossing location input data
        rcLocText = ttk.Label(rcLocFrame, text = "Enter location:")
        rcLocText.pack(padx = 5, fill = "x")
        rcLocEntry = ttk.Entry(rcLocFrame, textvariable = crossingLocation)
        rcLocEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and an Entry to grab user data

        rcStateFrame = ttk.Frame(rcFrame)
        rcStateFrame.pack(side = "top", fill = "x")
        #sub-frame for railway crossing state input data
        rcStateText = ttk.Label(rcStateFrame, text = "Enter crossing state:")
        rcStateText.pack(padx = 5, fill = "x")
        rcStateEntry = ttk.Combobox(rcStateFrame, textvariable = crossingState)
        rcStateEntry["values"] = ["inactive", "active"]
        rcStateEntry["state"] = "readonly"
        rcStateEntry.pack(padx = 5, fill = "x")
        #text to describe what to input, and a Combobox to grab user data

        getRC = ttk.Button(rcFrame, text = "Submit", style = "normal.TButton", command = lambda: self.sendRCData(crossingLocation.get(), crossingState.get()))
        getRC.pack(side = "top")
        #button to send data to data file

###############################################################################################################################################################

    def createOutputs(self):
    #create the area where outputs are shown to the user

        '''
        deployed train output area
        '''
        dtFrame = ttk.Frame(self.rightFrame)
        dtFrame.pack(pady = 15, side = "top")
        #sub-frame to hold deployed train output widgets
        dtText = ttk.Label(dtFrame, text = "Suggested Speed/Authority")
        dtText.pack(side = "top")
        #"Suggested Speed/Authority" title Label

        dtTrainFrame = ttk.Frame(dtFrame)
        dtTrainFrame.pack(side = "top")
        #sub-frame to hold deployed train train info
        dtTrainText = ttk.Label(dtTrainFrame, text = "Train:")
        dtTrainText.pack(side = "left", padx = 5, expand = True)
        self.dtTrainOutput = ttk.Label(dtTrainFrame, text = "(None)")
        self.dtTrainOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information

        dtSpeedFrame = ttk.Frame(dtFrame)
        dtSpeedFrame.pack(side = "top")
        #sub-frame to hold deployed train suggested speed info
        dtSpeedText = ttk.Label(dtSpeedFrame, text = "Suggested Speed:")
        dtSpeedText.pack(side = "left", padx = 5, expand = True)
        self.dtSpeedOutput = ttk.Label(dtSpeedFrame, text = "(None)")
        self.dtSpeedOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information

        dtAuthFrame = ttk.Frame(dtFrame)
        dtAuthFrame.pack(side = "top")
        #sub-frame to hold deployed train suggested speed info
        dtAuthText = ttk.Label(dtAuthFrame, text = "Suggested Authority:")
        dtAuthText.pack(side = "left", padx = 5, expand = True)
        self.dtAuthOutput = ttk.Label(dtAuthFrame, text = "(None)")
        self.dtAuthOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information


        '''
        maintenance mode output area
        '''
        mmFrame = ttk.Frame(self.rightFrame)
        mmFrame.pack(pady = 15, side = "top")
        #sub-frame to hold maintenance output widgets
        mmText = ttk.Label(mmFrame, text = "Maintenance Mode")
        mmText.pack(side = "top")
        #"Maintenance Mode" title Label

        mmLocFrame = ttk.Frame(mmFrame)
        mmLocFrame.pack(side = "top")
        #sub-frame to hold maintenance mode location info
        mmLocText = ttk.Label(mmLocFrame, text = "Location:")
        mmLocText.pack(side = "left", padx = 5, expand = True)
        self.mmLocOutput = ttk.Label(mmLocFrame, text = "(None)")
        self.mmLocOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information

        mmSentFrame = ttk.Frame(mmFrame)
        mmSentFrame.pack(side = "top")
        #sub-frame to hold maintenance mode signal sent info
        mmSentText = ttk.Label(mmSentFrame, text = "Signal sent: ")
        mmSentText.pack(side = "left", padx = 5, expand = True)
        self.mmSentOutput = ttk.Label(mmSentFrame, text = "(None)")
        self.mmSentOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information


        '''
        block errors output area
        '''
        tsFrame = ttk.Frame(self.rightFrame)
        tsFrame.pack(pady = 15, side = "top")
        #sub-frame to hold track state output widgets
        tsText = ttk.Label(tsFrame, text = "Block Errors")
        tsText.pack(side = "top")
        #"Track State" title Label

        tsLocFrame = ttk.Frame(tsFrame)
        tsLocFrame.pack(side = "top")
        #sub-frame to hold track state location info
        tsLocText = ttk.Label(tsLocFrame, text = "Location:")
        tsLocText.pack(side = "left", padx = 5, expand = True)
        self.tsLocOutput = ttk.Label(tsLocFrame, text = "(None)")
        self.tsLocOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information
        
        tsSentFrame = ttk.Frame(tsFrame)
        tsSentFrame.pack(side = "top")
        #sub-frame to hold track state signal sent info
        tsSentText = ttk.Label(tsSentFrame, text = "Signal sent: ")
        tsSentText.pack(side = "left", padx = 5, expand = True)
        self.tsSentOutput = ttk.Label(tsSentFrame, text = "(None)")
        self.tsSentOutput.pack(side = "left", expand = True)
        #one Label to describe what the output is (for user), other Label dynamically shows information

###############################################################################################################################################################

    def sendTSData(self, location: str):
    #formatting function that sends light state data to the data file
        '''
        Write all data to CTC_data.txt data file so the test ui can read in data changes
        Follows formatting rules specified in README.txt
        '''

        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("TS\n")
        outfile.write(location + "\n")
        outfile.write("blue")
        outfile.close()

###############################################################################################################################################################

    def sendTPData(self, sold: str, leave: str):
    #formatting function that sends throughput data to the data file
        '''
        Write all data to CTC_data.txt data file so the test ui can read in data changes
        Follows formatting rules specified in README.txt
        '''

        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("TP\n")
        outfile.write(sold + "\n")
        outfile.write(leave + "\n")
        outfile.write("blue")
        outfile.close()

###############################################################################################################################################################

    def sendLSData(self, location: str, state: str):
    #formatting function that sends light state data to the data file
        '''
        Write all data to CTC_data.txt data file so the test ui can read in data changes
        Follows formatting rules specified in README.txt
        '''

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
        #write binary code for light state to simulate input from wayside controller
          
        outfile.write("blue")
        outfile.close()

###############################################################################################################################################################
    
    def sendRCData(self, location: str, state: str):
    #formatting function that sends light state data to the data file
        '''
        Write all data to CTC_data.txt data file so the test ui can read in data changes
        Follows formatting rules specified in README.txt
        '''

        outfile = open("CTC_Office/CTC_data.txt", "w")
        outfile.write("RC\n")
        outfile.write(location + "\n")

        if (state == "inactive"):
            outfile.write("0\n")
        else:
            outfile.write("1\n")
        #write binary code for railway crossing to simulate input from wayside controller

        outfile.write("blue")
        outfile.close()