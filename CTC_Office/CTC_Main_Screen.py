import json    
from pathlib import Path 

def load_socket_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config.get("modules", {})

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk
from time import strftime
import CTC_Schedule_Screen

#necessary to import the clock from the parent directory#
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
import clock
from TrainSocketServer import TrainSocketServer


class MainScreen:
#"System Information" ui screen appearance and data


    '''
    Attributes:
    
    self.root: main Tk() variable for the ui window
    self.frame: main ttk.Frame() that all ui widgets are placed onto
    self.scheduleScreen: holds the ScheduleScreen object that displays the "Schedule" tab
    self.notebook = notebook: main notebook that contains the ui tabs
    self.totalPassengers: integer for the number of passengers on the blue line
    self.numberOfTrains: integer for the number of trains on the blue line
    self.clockText: a ttk.Label() that holds the current time
    self.clockTimer: contains the call to updateTime, allowing the program to cancel the timer when switching tabs

    self.tlArea: a ttk.Treeview() object that holds information about the train locations
    self.tsArea: a ttk.Treeview() object that holds information about the track state
    self.mmArea: a ttk.Treeview() object that holds information about maintenance mode
    self.tpArea: a ttk.Treeview() object that holds information about throughputs
    self.lsArea: a ttk.Treeview() object that holds information about light states

    self.mmList: a dictionary containing every block with a switch and what blocks they can face
    '''

    def __init__(self, root: tk.Tk, schedule: CTC_Schedule_Screen.ScheduleScreen, frame: ttk.Frame, notebook: ttk.Notebook):
    #initialize class variables and create backdrop for main screen

        self.root = root 
        self.frame = frame
        self.schedule_screen = schedule  
        self.notebook = notebook 
        self.totalPassengers = 0 
        self.numberOfTrains = 1

        self.mmList = {12: [1, 13], 28: [29, 150], 77: [76, 101], 85: [86, 100], 0: [57, 63]}


        # Socket server setup
        module_config = load_socket_config()
        ctc_config = module_config.get("CTC", {"port": 1})
        self.server = TrainSocketServer(port = ctc_config["port"], ui_id = "CTC")
        self.server.set_allowed_connections(["Track SW", "Track HW", "Track Model", "CTC_Test_UI"])  #add "CTC_Test_UI when using test ui"
        self.server.start_server(self._processMessage)
        self.server.connect_to_ui('localhost', 12342, "Track SW")
        self.server.connect_to_ui('localhost', 12343, "Track HW")
        self.server.connect_to_ui('localhost', 12344, "Track Model")

        #for test ui
        self.server.connect_to_ui('localhost', 12349, "CTC_Test_UI")

        self.createTopRow()
        #print the logo, reference map button, time
        self.createAreas()
        #print the titles of each section to the window 

###############################################################################################################################################################

    def send_to_ui(self, command, value=None):
        pass
        """Send command to the target UI (creates dict for socket server)"""
        message = {'command': command}
        if value is not None:
            message['value'] = value
        
        # Always send to Train_Model_Passenger_UI
        target_ui = "CTC_Test_UI"
        success = self.server.send_to_ui(target_ui, message)
        
        if success:
            print(f"Sent {command} to {target_ui}")
        else:
            print(f"Failed to send {command} to {target_ui}")

        return success
    
###############################################################################################################################################################

    def _processMessage(self, message, source_ui_id):
        """Process incoming messages and update train state"""
        try:
            print(f"Received message from {source_ui_id}: {message}")

            command = message.get('command')
            value = message.get('value')

            self.updateMainScreen(command, value)

        except Exception as e:
            print(f"Error processing message: {e}")

###############################################################################################################################################################

    def updateMainScreen(self, code, data):
    #update any data according to the data file
        '''
        Note: Follows formatting rules specified in README.txt.
        '''

        if (code == "TS"):
        #track state data case
            location = ""
            commaInd = 0
            #index of the space to allow us to grab other data from the string
            for i in range(len(data)):
                if (data[i] == ","):
                    commaInd = i
                    break
                location += data[i]
            line = data[(commaInd + 2):]

            children = self.tsArea.get_children("")
            #get a list of the items in the Treeview
            if (not children):
            #if there is no data yet, add first child
                level = self.tsArea.insert('', "end", text = line.title())
                self.tsArea.insert(level, "end", text = "Block " + location, values = ["Send Maintenance"])
            else:
                added = False
                #flag variable
                for child in children:
                #iterate for each parent in the Treeview
                    for item in self.tsArea.get_children(child):
                    #iterate for each child of every parent in the treeview
                        loc = self.tsArea.item(item, "text")
                        #grab the location text
                        if ((loc == ("Block " + location))):
                        #if item exists already, update that item
                            added = True
                            break
                    if (not added and self.tsArea.item(child, "text") == line.title()):
                    #if item does not exist and on the same line, add to the existing line
                        self.tsArea.insert(child, "end", text = "Block " + location, values = ["Send Maintenance"])
                        added = True
                        break
                if (not added):
                #if item is not in Treeview, add a new parent/child set
                    level = self.tsArea.insert('', "end", text = line.title())
                    self.tsArea.insert(level, "end", text = "Block " + location, values = ["Send Maintenance"])

        elif (code == "TP"):
        #throughput data case
            tickets = data[0]
            disemb = data[1]

            self.totalPassengers += (tickets - disemb)
            #add new passengers to total

            children = self.tpArea.get_children("")
            #get a list of items in the treeview
            if (not children):
            #if there is no data yet, add item
                self.tpArea.insert("", "end", text = line.title(), values = [self.totalPassengers/self.numberOfTrains])
            else:
                for child in children:
                #iterate for each child in the Treeview
                    text = self.tpArea.item(child, "text")
                    if (text == line.title()):  
                    #update if already exists
                        self.tpArea.item(child, values = [self.totalPassengers/self.numberOfTrains])
                        break
                    else:  
                    #add new if it does not exist yet
                        self.tpArea.insert("", "end", text = line.title(), values = [self.totalPassengers/self.numberOfTrains])
                        break

        elif (code == "LS"):  
        #light switch data case
            location = ""
            state = ""
            commaInd = 0

            #grab data from message
            for i in range(len(data)):
                if (data[i] == ","):
                    commaInd = i
                    break
                location += data[i]
            data = data[commaInd + 2:]
            for i in range(len(data)):
                if (data[i] == ","):
                    commaInd = i
                    break
                state += data[i]
            line = data[commaInd + 2:]
        
            if (state == "00"):
                state = "red"
            elif (state == "01"):
                state = "yellow"
            elif (state == "10"):
                state = "green"
            else:
                state = "supergreen"
            #get actual light states from the binary code (based on OP code in README.txt)

            children = self.lsArea.get_children("")
            #get list of items in the Treeview
            if (not children):  
            #if there is nothing added yet, add the first parent/child
                level = self.lsArea.insert('', "end", text = line.title())
                self.lsArea.insert(level, "end", text = "Block " + location, values = [state])
            else:
                added = False
                updated = False  
                #flag variables
                for child in children:
                #iterate for each parent in the Treeview
                    for item in self.lsArea.get_children(child):
                    #iterate for each child of every parent in the Treeview
                        loc = self.lsArea.item(item, "text")
                        if ((loc == ("Block " + location))):  
                        #if location exists, update item
                            self.lsArea.item(item, values = [state])
                            updated = True
                            added = True
                            break
                    if ((not updated) and (line.title() == self.lsArea.item(child, "text"))):
                    #add to existing line if item does not exist yet
                        self.lsArea.insert(child, "end", text = "Block " + location, values = [state])
                        added = True
                        break
                if (not added):
                #if value is not already in the treeview, add a new parent/child set
                    level = self.lsArea.insert('', "end", text = line.title())
                    self.lsArea.insert(level, "end", text = "Block " + location, values = [state])

        elif (code == "RC"):
            #railway crossing data case
            location = ""
            state = ""
            commaInd = 0
            
            #grab data from message
            for i in range(len(data)):
                if (data[i] == ","):
                    commaInd = i
                    break
                location += data[i]
            data = data[commaInd + 2:]
            for i in range(len(data)):
                if (data[i] == ","):
                    commaInd = i
                    break
                state += data[i]
            line = data[commaInd + 2:]
           
            if (state == "0"):
                state = "inactive"
            elif (state == "1"):
                state = "active"
            #get actual light states from the binary code (based on the OP code in README.txt)

            children = self.rcArea.get_children("")
            #get list of items in Treeview
            if (not children):
            #if there is nothing added yet, add the first parent/child
                level = self.rcArea.insert('', "end", text = line.title())
                self.rcArea.insert(level, "end", text = "Block " + location, values = [state])
            else:
                added = False
                updated = False
                #flag variables
                for child in children:
                #iterate for each parent in the treeview
                    for item in self.rcArea.get_children(child):
                    #iterate for each child of every parent in the treeview
                        loc = self.rcArea.item(item, "text")
                        if ((loc == ("Block " + location))):
                        #if item exists, update item
                            self.rcArea.item(item, values = [state])
                            updated = True
                            added = True
                            break
                    if ((not updated) and (line.title() == self.rcArea.item(child, "text"))):
                    #add to existing line if data does not exist yet
                        self.rcArea.insert(child, "end", text = "Block " + location, values = [state])
                        added = True
                        break
                if (not added):
                #if value is not already in the treeview, add a new parent/child set
                    level = self.rcArea.insert('', "end", text = line.title())
                    self.rcArea.insert(level, "end", text = "Block " + location, values = [state])
        
###############################################################################################################################################################

    def createTopRow(self):
    #create the logo, reference map button, and clock at the top of the ui screen
        
        topFrame = ttk.Frame(self.frame, style = "white.TFrame")
        topFrame.pack(side = "top", anchor = "n", expand = True, fill = "x")
        #sub-frame used to center the top row of widgets

        '''
        create the BLT image
        '''
        bltOriginalImage = Image.open("CTC_Office/blt logo.png")
        bltOriginalImage = bltOriginalImage.resize((75, 75))
        #create and resize image
        bltImage = ImageTk.PhotoImage(bltOriginalImage)  
        bltImageLabel = ttk.Label(topFrame, image = bltImage, background = "white")
        bltImageLabel.image = bltImage
        #keep a reference to the image so that it appears on the window
        bltImageLabel.pack(side = "left", anchor = "nw")

        '''
        create a button to display the reference map
        '''
        centerFrame = ttk.Frame(topFrame)
        centerFrame.pack(side="left", anchor = "n", expand=True)
        #create a sub-frame to center the button within
        buttonStyle = ttk.Style()
        buttonStyle.configure("TButton", font = ("Arial", 15))
        #button style be used for all buttons on the main ui screens
        mapButton = ttk.Button(centerFrame, text = "Reference Map", style = "TButton", command = lambda: self.dispRefMap())
        #bind button to the dispRefMap method
        mapButton.pack(pady = 5, anchor = "n")

        '''
        create a label for the time
        '''
        self.clockText = ttk.Label(topFrame, text = clock.clock.getTime(), font = ("Arial", 20, "bold"), background = "white")
        self.clockText.pack(side = "right", anchor = "ne")
        #create a blank Label to hold the text
        self.updateTime()
        #initial call for the method that updates the time dynamically

        self.notebook.bind("<<NotebookTabChanged>>", self.updateToSchedule)
        #bind the tab switching action to a handler function

###############################################################################################################################################################
    
    def createAreas(self):
    #create titles and display areas for each item on the "System Information" tab

        leftFrame = ttk.Frame(self.frame, style = "white.TFrame")
        leftFrame.pack(side = "left", expand = True, fill = "y")
        rightFrame = ttk.Frame(self.frame, style = "white.TFrame")
        rightFrame.pack(side = "left", expand = True, fill = "y")
        #create a sub-frame for each side of the screen to center all widgets

        whiteText = ttk.Style()
        whiteText.configure("White.TLabel", foreground = "white", font = ("Arial", 20))
        #Style to put white text in each of the titles

        '''
        train location area
        '''
        tlFrame = ttk.Frame(leftFrame, style = "white.TFrame")
        tlFrame.pack(pady = 5, side = "top", expand = True)
        #sub-frame to store the train location widgets
        tlText = ttk.Label(tlFrame, text = " Train Locations ", style = "White.TLabel")
        tlText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")
        tlText.pack(side = "top")
        #"Train Locations" title Label

        self.tlArea = ttk.Treeview(tlFrame, columns = ("Location", "Destination", "Arrival Time"))
        self.tlArea.heading("#0", text = "Train")
        self.tlArea.heading("Location", text = "Location")
        self.tlArea.heading("Destination", text = "Destination")
        self.tlArea.heading("Arrival Time", text = "Arrival Time")
        self.tlArea.column("#0", width = 100, anchor = "w", stretch = "no")
        self.tlArea.column("Location", width = 100)
        self.tlArea.column("Destination", width = 150)
        self.tlArea.column("Arrival Time", width = 100)
        self.tlArea.pack(side = "left")
        #create and format the Treeview holding the train location data

        tlScrollbar = ttk.Scrollbar(tlFrame, orient = "vertical", command = self.tlArea.yview)
        self.tlArea.configure(yscrollcommand = tlScrollbar.set)
        tlScrollbar.pack(side = "right", fill = "y")
        #add a scrollbar to the train location Treeview

        '''
        block error area
        '''
        tsFrame = ttk.Frame(leftFrame, style = "white.TFrame")
        tsFrame.pack(pady = 5, side = "top", expand = True)
        #sub-frame to store the track state widgets
        tsText = ttk.Label(tsFrame, text = " Block Errors ", style = "White.TLabel")
        tsText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        tsText.pack(side = "top")
        #"Track State" title Label

        self.tsArea = ttk.Treeview(tsFrame, columns = ("Maintenance"))
        self.tsArea.heading("#0", text = "Location")
        self.tsArea.heading("Maintenance", text = "Maintenance")
        self.tsArea.column("#0", width = 200)
        self.tsArea.column("Maintenance", width = 200)
        self.tsArea.pack(side = "left")
        #create and format the Treeview holding the track state data

        self.tsArea.bind("<Button-1>", self.sendMaintenance)
        #if a user clicks in the tsArea Treeview, bind the click to a handler function

        tsScrollbar = ttk.Scrollbar(tsFrame, orient = "vertical", command = self.tsArea.yview)
        self.tsArea.configure(yscrollcommand = tsScrollbar.set)
        tsScrollbar.pack(side = "right", fill = "y")
        #add a scrollbar to the track state Treeview

        '''
        maintenance mode area
        '''
        mmFrame = ttk.Frame(leftFrame, style = "white.TFrame")  
        mmFrame.pack(pady = 5, side = "top", expand = True)
        #sub-frame to store the maintenance mode widgets
        mmText =  ttk.Label(mmFrame, text = " Maintenance Mode ", style = "White.TLabel")
        mmText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        mmText.pack(side = "top")
        #"Maintenance Mode" title Label

        self.mmArea = ttk.Treeview(mmFrame, columns = ("Direction", "Switch"))
        self.mmArea.heading("#0", text = "Location")
        self.mmArea.heading("Direction", text = "Block pointed towards")
        self.mmArea.heading("Switch", text = "Switch?")
        self.mmArea.column("#0", width = 150)
        self.mmArea.column("Direction", width = 150)
        self.mmArea.column("Switch", width = 100)
        #create and format the Treeview holding maintenance mode data

        greenLineLevel = self.mmArea.insert("", "end", text = "Green")
        for key in self.mmList:
            self.mmArea.insert(greenLineLevel, "end", text = "Block " + str(key), values = ["Block " + str(self.mmList[key][0]), "Switch"])
        #switches for green line only (will add red later)

        self.mmArea.bind("<Button-1>", self.switchTrack)
        self.mmArea.pack(side = "left")
        #if a user clicks in the mmArea treeview, bind the click to a handler function

        mmScrollbar = ttk.Scrollbar(mmFrame, orient = "vertical", command = self.mmArea.yview)
        self.mmArea.configure(yscrollcommand = mmScrollbar.set)
        mmScrollbar.pack(side = "right", fill = "y")
        #add a scrollbar to the maintenance mode Treeview

        '''
        thoughput area
        '''
        tpFrame = ttk.Frame(rightFrame, style = "white.TFrame")
        tpFrame.pack(pady = 5, side = "top", expand = True)
        #sub-frame to store the throughput widgets
        tpText =  ttk.Label(tpFrame, text = " Throughputs ", style = "White.TLabel")
        tpText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        tpText.pack(side = "top")
        #"Throughputs" title Label
        
        self.tpArea = ttk.Treeview(tpFrame, columns = ("Throughput"), height = 2)
        #only 2 lines max, so we can limit the height to account for this
        self.tpArea.heading("#0", text = "Line")
        self.tpArea.heading("Throughput", text = "Throughput")
        self.tpArea.column("#0", width = 200)
        self.tpArea.column("Throughput", width = 200)
        self.tpArea.pack(side = "top")
        #create and format the Treeview holding throughput data

        '''
        #light states area
        '''
        lsFrame = ttk.Frame(rightFrame, style = "white.TFrame")
        lsFrame.pack(pady = 5, side = "top", expand = True)
        #sub-frame to store the light state widgets
        lsText =  ttk.Label(lsFrame, text = " Light States ", style = "White.TLabel")
        lsText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        lsText.pack(side = "top")
        #"Light State" title Label

        self.lsArea = ttk.Treeview(lsFrame, columns = ("State"))
        self.lsArea.heading("#0", text = "Location")
        self.lsArea.heading("State", text = "State")
        self.lsArea.column("#0", width = 200)
        self.lsArea.column("State", width = 200)
        self.lsArea.pack(side = "left")
        #create and format the Treeview holding light state data

        lsScrollbar = ttk.Scrollbar(lsFrame, orient = "vertical", command = self.lsArea.yview)
        self.lsArea.configure(yscrollcommand = lsScrollbar.set)
        lsScrollbar.pack(side = "right", fill = "y")
        #add a scrollbar to the light state Treeview
        
        '''
        railway crossings area
        '''
        rcFrame = ttk.Frame(rightFrame, style = "white.TFrame")
        rcFrame.pack(pady = 5, side = "top", expand = True)
        #sub-frame to store the railway crossings widgets
        rcText = ttk.Label(rcFrame, text = " Railway Crossings ", style = "White.TLabel")
        rcText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        rcText.pack(side = "top")
        #"Railway Crossings" title Label

        self.rcArea = ttk.Treeview(rcFrame, columns = ("State"))
        self.rcArea.heading("#0", text = "Location")
        self.rcArea.heading("State", text = "State")
        self.rcArea.column("#0", width = 200)
        self.rcArea.column("State", width = 200)
        self.rcArea.pack(side = "left")
        #create and format the Treeview holding railway crossing data

        rcScrollbar = ttk.Scrollbar(rcFrame, orient = "vertical", command = self.rcArea.yview)
        self.rcArea.configure(yscrollcommand = rcScrollbar.set)
        rcScrollbar.pack(side = "right", fill = "y")
        
###############################################################################################################################################################

    def updateTime(self):
    #continuously recall itself every second to update the time variable 
        
        time = clock.clock.getTime()
        self.clockText.configure(text = time)
        self.clockTimer = self.root.after(100, self.updateTime)

###############################################################################################################################################################
    
    def updateToSchedule(self, event):
    #update the screen if "Schedule" tab is clicked

        if (event.widget.tab(event.widget.select(), "text") == "Schedule"):
        #prevents errors on boot
            self.root.after_cancel(self.clockTimer)
            #cancel this call if active
            self.notebook.select(1)

###############################################################################################################################################################     

    def dispRefMap(self):
    #display the reference map to the user

        refMap = tk.Toplevel(self.root)
        refMap.title("Reference Map")
        refMap.geometry("1000x500+1201+0")
        #configure the window holding the reference map

        mapOriginalImage = Image.open("CTC_Office/blue_line.png") 
        mapImage = ImageTk.PhotoImage(mapOriginalImage.resize((1000, 500)))
        #create and resize image
        mapImageLabel = ttk.Label(refMap, image = mapImage, background = "white")
        mapImageLabel.image = mapImage
        #keep a reference to the image so that it appears on the window
        mapImageLabel.pack()

###############################################################################################################################################################

    def updateTrainLocations(self, location: str, destination: str, time: str, line: str, tNum: int):
        '''
        Handle user clicks in the train location Treeview
        Because this is sent directly from ScheduleScreen, avoid the UpdateMainScreen() method
        to leave CTC_data.txt purely for inputs from other modules.
        '''

        children = self.tlArea.get_children("")
        #get a list of the items in the Treeview
        if (not children):
        #if no children, add first item
            level = self.tlArea.insert('', "end", text = line.title())
            self.tlArea.insert(level, "end", text = ("Train " + str(tNum)), values = [("Block " + location), destination, time])
        else:
            added = False
            #flag variable
            for child in children:
            #iterate for each parent in the Treeview
                for item in self.tlArea.get_children(child):
                #iterate for each child of every parent in the Treeview
                    train = self.tlArea.item(item, "text")
                    #grab the train number
                    if (train == "Train " + str(tNum)):
                    #if the user edits an existing train, update rather than adding a new train
                        self.tlArea.item(item, values = ["Block " + location, destination, time])
                        added = True
                        break
                if (not added and self.tlArea.item(child, "text") == line.title()):
                #if train does not exist but is on an existing line, add under that specific line
                    self.tlArea.insert(child, "end", text = "Train " + str(tNum), values = [("Block " + location), destination, time])
                    added = True
                    break
            if (not added):
            #if value is not already in the Treeview at all, add a new parent/child set
                level = self.tlArea.insert('', "end", text = line.title())
                self.tlArea.insert(level, "end", text = "Train " + str(tNum), values = [("Block " + location), destination, time])

###############################################################################################################################################################

    def sendMaintenance(self, event):
    #handle user clicks in the maintenance mode Treeview
    
        rowID = self.tsArea.identify_row(event.y)
        #grab the row the user clicked in
        colID = self.tsArea.identify_column(event.x)
        #grab the column the user clicked in

        if (rowID):
            if (colID == "#1" and (self.tsArea.item(rowID, "values") != ("In maintenance...",))):
            #check the user clicked the right column and the maintenance has not already been sent
                answer = askyesno(title = "Confirmation", message = "Would you like to send maintenance?")
                #confirmation pop-up, returns True if user clicks "Yes"
                if (answer):
                    self.tsArea.set(rowID, column = colID, value = "In maintenance...")
                    #change the row text to reflect that maintenance has been sent
                    
                    '''
                    Write all data to to_test_ui.txt data file so the test ui can read in data changes
                    Follows formatting rules specified in README.txt
                    '''

                    temp = self.tsArea.item(rowID, "text")
                    location = ""
                    for char in temp:
                    #grab block number from row
                        if (char.isdigit()):
                            location += char

                    self.send_to_ui("TS", location + ", " + self.tsArea.item(self.tsArea.parent(rowID), "text").lower())

###############################################################################################################################################################
    
    def switchTrack(self, event):
    #handle user clicks in the maintenance mode Treeview
    
        rowID = self.mmArea.identify_row(event.y)
        #grab row user clicked in 
        colID = self.mmArea.identify_column(event.x)
        #grab column user clicked in
        if (rowID):
            if (colID == "#2" and (self.mmArea.item(rowID, "values")[1] == "Switch")):
            #check that the user clicked the correct column
                answer = askyesno(title = "Confirmation", message = "Would you like to switch the track?")
                #confirmation pop-up, returns True if user clicks "Yes"
                if (answer):
                    
                    for key in self.mmList:
                        if (self.mmArea.item(rowID, "text") == "Block " + str(key)):
                            if (self.mmArea.item(rowID, "values")[0] == "Block " + str(self.mmList[key][0])):
                                self.mmArea.set(rowID, column = "Direction", value = "Block " + str(self.mmList[key][1]))
                                break
                            else:
                                self.mmArea.set(rowID, column = "Direction", value = "Block " + str(self.mmList[key][0]))
                                break
                        #edit which block the switch is pointed at


                    temp = self.mmArea.item(rowID, "text")
                    location = ""
                    for char in temp:
                        if (char.isdigit()):
                            location += char
                    #grab specific block location

                    temp = self.mmArea.item(rowID, "values")[0]
                    direction = ""
                    for char in temp:
                        if (char.isdigit()):
                            direction += char
                    #grab specific block direction

                    self.send_to_ui("MM", location + ", " + direction + ", " + self.mmArea.item(self.mmArea.parent(rowID), "text").lower())

###############################################################################################################################################################

    def onClosing(self):
        """Handle application closing"""
        print("Closing application...")
        self.server.running = False
        if self.server.server_socket:
            try:
                self.server.server_socket.close()
            except:
                pass