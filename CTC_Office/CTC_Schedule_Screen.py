import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk
from time import strftime, strptime
from datetime import datetime, timedelta
import CTC_Main_Screen
import pandas as pd

#necessary to import the clock from the parent directory#
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
import clock
from TrainSocketServer import TrainSocketServer

class ScheduleScreen:
#"Schedule" ui screen appearance and data
    '''
    Attributes:
    
    self.root: main Tk() variable for the ui window
    self.frame: main ttk.Frame() that all ui widgets are placed onto
    self.mainScreen: holds the MainScreen object that displays the "Syestem Information" tab
    self.notebook: main notebook that contains the ui tabs
    self.trainNum: number of trains released into the yard
    self.clockText: a ttk.Label() that holds the current time
    self.clockTimer: contains the call to updateTime, allowing the program to cancel the timer when switching tabs

    self.trainRoutes: dictionary containing each train's route (defined as the block it will travel to next, plus its scheduled stops)
    '''

    def __init__(self, root: tk.Tk, main: CTC_Main_Screen, frame: ttk.Frame, notebook: ttk.Notebook):
    #initialize class variables and create backdrop for schedule screen

        self.root = root  #main variable for the window
        self.frame = frame
        self.mainScreen = main  #variable to hold the data of the schedule screen
        self.notebook = notebook  #variable to hold data about the tab buttons
        self.trainNum = 1;  #number of trains that have been sent to the system

        self.greenStationLocations = {63: "start", 65: "Glenbury", 73: "Dormont", 77: "Mt. Lebanon", 88: "Poplar",
                                      96: "Castle Shannon", 105: "Dormont", 114: "Glenbury", 123: "Overbrook", 132: "Inglewood",
                                      141: "Central", 2: "Pioneer", 9: "Edgebrook", 16: "LLC Plaza", 22: "Whited", 31: "South Bank",
                                      39: "Central", 48: "Inglewood", 57: "Overbrook", 58: "end"}
        self.greenStations = ["Pioneer", "Edgewood", "LLC Plaza", "Whited", "South Bank", "Central", "Inglewood", "Overbrook", "Glenbury", "Dormont", "Mt. Lebanon", "Poplar", "Castle Shannon"]
        
        self.redStationLocations = {9: "start", 7: "Shadyside", 16: "Herron Ave", 21: "Swissville", 25: "Penn Station",
                                    35: "Steel Plaza", 45: "First Ave", 48: "Station Square", 60: "South Hills Junction", 9: "end"}
        self.redStations = ["Shadyside", "Herron Ave", "Swissville", "Penn Station", "Steel Plaza", "First Ave", "Station Square", "South Hills Junction"]

        self.trainRoutes = {}

        self.createTopRow()
        #print to top row of the UI to the window
        self.createAreas()
        #print the titles of each section to the window 

###############################################################################################################################################################     

    def createTopRow(self):
    #create the logo, tab, and reference map button
        
        topFrame = ttk.Frame(self.frame, style = "white.TFrame")
        topFrame.pack(side = "top", anchor = "n", expand = True, fill = "x")
        #sub-frame used to center the top row of widgets

        '''
        create the BLT logo
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
        #button style be used for all buttons on the schedule ui screen
        mapButton = ttk.Button(centerFrame, text = "Reference Map", style = "TButton", command = lambda: self.dispRefMap())
        #bind button to the dispRefMap method
        mapButton.pack(pady = 5, anchor = "n")

        '''
        create a label for the time
        '''
        self.clockText = ttk.Label(topFrame, text = "", font = ("Arial", 20, "bold"), background = "white")
        self.clockText.pack(side = "right", anchor = "ne")
        #create a blank Label to hold the text
        self.updateTime()
        #initial call for the method that updates the time dynamically

        self.notebook.bind("<<NotebookTabChanged>>", self.updateToMain)
        #bind the tab switching action to a handler function

###############################################################################################################################################################

    def createAreas(self):
    #create titles and display areas for each item on the "System Information" tab

        leftFrame = ttk.Frame(self.frame, style = "white.TFrame")
        leftFrame.pack(pady = 125, side = "left", expand = True, fill = "y")
        rightFrame = ttk.Frame(self.frame, style = "white.TFrame")
        rightFrame.pack(side = "left", expand = True, fill = "y")
        #create a sub-frame for each side of the screen to center all widgets

        whiteText = ttk.Style()
        whiteText.configure("White.TLabel", foreground = "white", font = ("Arial", 20))
        #Style to put white text in each of the titles

        '''
        schedule train area
        '''
        scText = ttk.Label(leftFrame, text = " Schedule Train ", style = "White.TLabel")
        scText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")
        scText.pack(pady = 50, side = "top")
        #"Schedule Train" title Label
        
        
        locFrame = ttk.Frame(leftFrame, style = "white.TFrame")
        locFrame.pack(pady = 25, side = "top", fill = "x")
        #sub-frame to hold words and user Combobox entry
        locText = ttk.Label(locFrame, text = "Select a destination:")
        locText.pack(padx = 5, pady = 5, fill = "x")
        #text to describe what the user should input

        selectedLocation = tk.StringVar()
        arrivalTime = tk.StringVar()
        #dynamic string variables that update with user choice

        locSelect = ttk.Combobox(locFrame, textvariable = selectedLocation)
        #shows options for the user to select for destination
        locSelect["values"] = ["Pioneer", "Edgewood", "LLC Plaza", "Whited", "South Bank", "Central", "Inglewood", "Overbrook", "Glenbury", "Dormont", "Mt. Lebanon", "Poplar", "Castle Shannon",
                               "Shadyside", "Herron Ave", "Swissville", "Penn Station", "Steel Plaza", "First Ave", "Station Square", "South Hills Junction"]
        #for GREEN LINE ONLY
        locSelect["state"] = "readonly"
        locSelect.pack(padx = 5, pady = 5, fill = "x")

        timeFrame = ttk.Frame(leftFrame, style = "white.TFrame")
        timeFrame.pack(pady = 25, side = "top", fill = "x")
        #sub-frame to hold words and user Entry
        timeText = ttk.Label(timeFrame, text = "Enter a time:")
        timeText.pack(padx = 5, pady = 5, fill = "x")
        #text to describe what the user should input
        timeEntry = ttk.Entry(timeFrame, textvariable = arrivalTime)
        timeEntry.pack(padx = 5, pady = 5, fill = "x")
        #grabs user text input

        buttonFrame = ttk.Frame(leftFrame, style = "white.TFrame")
        buttonFrame.pack(pady = 40, side = "top", expand = True)
        #sub-frame to organize buttons
        getDeploy = ttk.Button(buttonFrame, text = "Deploy Train", style = "TButton", command = lambda: (self.sendDeployData("63", selectedLocation.get(), arrivalTime.get(), "green"), self.updateManualEdit("63", [selectedLocation.get()], arrivalTime.get(), "green")))
        getDeploy.pack(pady = 15, side = "top", fill = "x")
        #grab inputs from the Combobox and Entry (if user inputs values)
        autoButton = ttk.Button(buttonFrame, text = "Automatic Mode", style = "TButton", command = lambda: self.updateAutoEdit())
        autoButton.pack(side = "top")
        #opens a tab to ask the user to input a .csv file to automatically schedule trains
    
        '''
        manual edit area
        '''
        meFrame = ttk.Frame(rightFrame, style = "white.TFrame")
        meFrame.pack(pady = 160, side = "top")
        #sub-frame to store the manual edit widgets
        meText = ttk.Label(meFrame, text = " Manual Edit ", style = "White.TLabel")
        meText.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")
        meText.pack()
        #"Manual Edit" title Label

        self.meArea = ttk.Treeview(meFrame, columns = ("Location", "Destination", "Arrival Time")) 
        self.meArea.heading("#0", text = "Train")
        self.meArea.heading("Location", text = "Location")
        self.meArea.heading("Destination", text = "Destination")
        self.meArea.heading("Arrival Time", text = "Arrival Time")
        self.meArea.column("#0", width = 100)
        self.meArea.column("Location", width = 100)
        self.meArea.column("Destination", width = 150)
        self.meArea.column("Arrival Time", width = 100)
        self.meArea.pack(side = "left")
        #create and format the Treeview holding the manual edit data (should be identical to train location data)

        self.meArea.bind("<Button-1>", self.manualEdit)
        #if a user clicks in the meArea treeview, bind the click to a handler function

        meScrollbar = ttk.Scrollbar(meFrame, orient = "vertical", command = self.meArea.yview)
        self.meArea.configure(yscrollcommand = meScrollbar.set)
        meScrollbar.pack(side = "right", fill = "y")
        #add a scrollbar to the manual edit Treeview

###############################################################################################################################################################

    def updateTime(self):
    #continuously recall itself every second to update the time variable

        time = clock.clock.getTime()
        self.clockText.configure(text = time)
        self.clockTimer = self.root.after(1000, self.updateTime)

###############################################################################################################################################################
    
    def updateToMain(self, event):
    #update the screen if "System Information" tab is clicked
        if (event.widget.tab(event.widget.select(), "text") == "System Information"):
        #prevents errors on boot
            #self.root.after_cancel(self.clockTimer)
            #cancel this call if active
            self.notebook.select(0)

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
    
    def sendDeployData(self, location: str, destination: str, time: str, line: str):
    #send user inputs to main screen to update train locations Treeview

        if (destination in self.redStations):
            location = "9"
            line = "red"

        self.mainScreen.updateTrainLocations(location, destination, time, line, self.trainNum)
        #increase of trains on the line

###############################################################################################################################################################

    def updateManualEdit(self, location: str, destination: list, time: str, line: str):
    #update the manual edit tab
        if (time != None):
        #if we are creating a new train on the line
            if (destination[0] in self.redStations):
                location = "9"
                line = "red"

            arrTime = self.timeToSeconds(time)
            speed = 0
            auth = 0

            children = self.meArea.get_children("")
            #get a list of the items in the Treeview
            if (not children):
            #if there is no data yet, add first item
                level = self.meArea.insert('', "end", text = line.title())
                self.meArea.insert(level, "end", text = ("Train " + str(self.trainNum)), values = [("Block " + location), destination[0], time])
            else:
                added = False
                #flag variable
                for child in children: 
                #iterate for each parent in the Treeview
                    for item in self.meArea.get_children(child):
                    #iterate for each child of every parent in the Treeview
                        dest = self.meArea.item(item, "text")
                        if (dest == "Train " + str(self.trainNum)):
                        #if the user edits an existing train, update rather than adding a new item
                            self.meArea.item(item, values = ["Block " + location, destination[0], time])
                            added = True
                            break
                    if (not added and self.meArea.item(child, "text") == line.title()):
                    #if train does not exist but is on an existing line, add under that specific line
                        self.meArea.insert(child, "end", text = "Train " + str(self.trainNum), values = [("Block " + location), destination[0], time])
                        added = True
                        break
                if (not added):
                #if item is not already in the treeview, add a new parent/child set
                    level = self.meArea.insert('', "end", text = line.title())
                    self.meArea.insert(level, "end", text = "Train " + str(self.trainNum), values = [("Block " + location), destination[0], time])

            if (line == "red"):
                self.trainRoutes[self.trainNum] = [int(location), line, "backward"]
            else:
                self.trainRoutes[self.trainNum] = [int(location), line, "forward"]

            for station in destination:
                self.trainRoutes[self.trainNum].append(station)

            self.trainNum += 1
            
            values = self.calculateAuthority(self.trainRoutes[self.trainNum - 1], destination[0])
            auth = values[0] - 1
            speed = float(values[1]) / arrTime

            self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [str(self.trainNum - 1), f"{speed:.3f}", str(auth), line]})
            self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": line.title(), "block": location, "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
            self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": line.title(), "block": location, "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})
    
            return auth  #for test case 1
        
        else:
        #if we are updating a train on the line
            updated = False
            train = 0

            for key in self.trainRoutes:
                if (line == "green"):

                    '''statements to move the train'''
                    if ((self.trainRoutes[key][0] + 1) == int(location) and self.trainRoutes[key][2] == "forward"):
                        self.updateTrainInManualEdit(key, location)
                        updated = True
                    elif (self.trainRoutes[key][0] == 100 and int(location) == 85 and self.trainRoutes[key][2] == "forward"):
                    #switch from 100->85
                        self.updateTrainInManualEdit(key, location)
                        self.trainRoutes[key][2] = "backward"
                        updated = True
                    elif (self.trainRoutes[key][0] == 76 and int(location) == 101 and self.trainRoutes[key][2] == "backward"):
                    #switch from 76->101
                        self.updateTrainInManualEdit(key, location)
                        self.trainRoutes[key][2] = "forward"
                        updated = True
                    elif (self.trainRoutes[key][0] == 150 and int(location) == 28 and self.trainRoutes[key][2] == "forward"):
                    #switch from 150->28
                        self.updateTrainInManualEdit(key, location)
                        self.trainRoutes[key][2] = "backward"
                        updated = True
                    elif (self.trainRoutes[key][0] == 1 and int(location) == 13 and self.trainRoutes[key][2] == "backward"):
                    #switch from 1->13
                        self.updateTrainInManualEdit(key, location)
                        self.trainRoutes[key][2] = "forward"
                        updated = True
                    elif (self.trainRoutes[key][0] in range(1, 29) and self.trainRoutes[key][0] == int(location) + 1 and self.trainRoutes[key][2] == "backward"):
                    #if moving backwards
                        self.updateTrainInManualEdit(key, location)
                        updated = True
                    elif (self.trainRoutes[key][0] in range(76, 86) and self.trainRoutes[key][0] == int(location) + 1 and self.trainRoutes[key][2] == "backward"):
                    #if moving backwards
                        self.updateTrainInManualEdit(key, location)
                        updated = True

                    if (len(self.trainRoutes[key]) == 3):
                        if (self.trainRoutes[key][0] == 58):
                            children = self.meArea.get_children("")
                            for child in children: 
                            #iterate for each parent in the Treeview
                                for item in self.meArea.get_children(child):
                                #iterate for each child of every parent in the Treeview
                                    dest = self.meArea.item(item, "text")
                                    if (dest == "Train " + str(key)):
                                        self.meArea.delete(item)
                                        self.mainScreen.tlArea.delete(item)
                                        train = key
                                        break

                    else:
                        if (self.trainRoutes[key][0] in self.greenStationLocations):
                            if (self.trainRoutes[key][3] == self.greenStationLocations[self.trainRoutes[key][0]]):

                                self.trainRoutes[key].remove(self.trainRoutes[key][3])
                            
                                if (len(self.trainRoutes[key]) == 3):
                                #if there is no more destination backlog go to yard
                                    children = self.meArea.get_children("")
                                    for child in children: 
                                    #iterate for each parent in the Treeview
                                        for item in self.meArea.get_children(child):
                                        #iterate for each child of every parent in the Treeview
                                            dest = self.meArea.item(item, "text")
                                            if (dest == "Train " + str(key)):
                                                newTime = clock.clock.getTimeObj() + timedelta(minutes = 10)
                                                arrTime = self.timeToSeconds(newTime.strftime("%H:%M"))
                                                values = self.calculateAuthority(self.trainRoutes[key], "end")
                                                auth = values[0] - 1
                                                speed = float(values[1]) / arrTime

                                                self.meArea.item(item, values = ["Block " + location, "Yard", newTime.strftime("%H:%M")])
                                                self.mainScreen.tlArea.item(item, values = ["Block " + location, "Yard", newTime.strftime("%H:%M")])

                                                self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [str(key), f"{speed:.3f}", str(auth), self.trainRoutes[key][1]]})
                                                self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
                                                self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})
                                                break
                                else:
                                #otherwise go to next station
                                    children = self.meArea.get_children("")
                                    for child in children: 
                                    #iterate for each parent in the Treeview
                                        for item in self.meArea.get_children(child):
                                        #iterate for each child of every parent in the Treeview
                                            dest = self.meArea.item(item, "text")
                                            if (dest == "Train " + str(key)):
                                                newTime = clock.clock.getTimeObj() + timedelta(minutes = 10)
                                                arrTime = self.timeToSeconds(newTime.strftime("%H:%M"))
                                                values = self.calculateAuthority(self.trainRoutes[key], self.trainRoutes[key][3])
                                                auth = values[0] - 1
                                                speed = float(values[1]) / arrTime

                                                self.meArea.item(item, values = ["Block " + location, self.trainRoutes[key][3], newTime.strftime("%H:%M")])
                                                self.mainScreen.tlArea.item(item, values = ["Block " + location, self.trainRoutes[key][3], newTime.strftime("%H:%M")])

                                                self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [str(key), f"{speed:.3f}", str(auth), self.trainRoutes[key][1]]})
                                                self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
                                                self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})
                                                break
                else:
                #red line
                    '''statements to move the train'''
                    if ((self.trainRoutes[key][0] + 1) == int(location)):
                        self.updateTrainInManualEdit(key, location)
                        updated = True

                    else:
                        if (self.trainRoutes[key][0] in self.redStationLocations):
                            if (self.trainRoutes[key][3] == self.redStationLocations[self.trainRoutes[key][0]]):

                                self.trainRoutes[key].remove(self.trainRoutes[key][3])
                            
                                if (len(self.trainRoutes[key]) == 3):
                                #if there is no more destination backlog go to yard
                                    children = self.meArea.get_children("")
                                    for child in children: 
                                    #iterate for each parent in the Treeview
                                        for item in self.meArea.get_children(child):
                                        #iterate for each child of every parent in the Treeview
                                            dest = self.meArea.item(item, "text")
                                            if (dest == "Train " + str(key)):
                                                newTime = clock.clock.getTimeObj() + timedelta(minutes = 10)
                                                arrTime = self.timeToSeconds(newTime.strftime("%H:%M"))
                                                values = self.calculateAuthority(self.trainRoutes[key], "end")
                                                auth = values[0] - 1
                                                speed = float(values[1]) / arrTime

                                                self.meArea.item(item, values = ["Block " + location, "Yard", newTime.strftime("%H:%M")])
                                                self.mainScreen.tlArea.item(item, values = ["Block " + location, "Yard", newTime.strftime("%H:%M")])

                                                self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [str(key), f"{speed:.3f}", str(auth), self.trainRoutes[key][1]]})
                                                self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
                                                self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})
                                                break
                                else:
                                #otherwise go to next station
                                    children = self.meArea.get_children("")
                                    for child in children: 
                                    #iterate for each parent in the Treeview
                                        for item in self.meArea.get_children(child):
                                        #iterate for each child of every parent in the Treeview
                                            dest = self.meArea.item(item, "text")
                                            if (dest == "Train " + str(key)):
                                                newTime = clock.clock.getTimeObj() + timedelta(minutes = 10)
                                                arrTime = self.timeToSeconds(newTime.strftime("%H:%M"))
                                                values = self.calculateAuthority(self.trainRoutes[key], self.trainRoutes[key][3])
                                                auth = values[0] - 1
                                                speed = float(values[1]) / arrTime

                                                self.meArea.item(item, values = ["Block " + location, self.trainRoutes[key][3], newTime.strftime("%H:%M")])
                                                self.mainScreen.tlArea.item(item, values = ["Block " + location, self.trainRoutes[key][3], newTime.strftime("%H:%M")])

                                                self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [str(key), f"{speed:.3f}", str(auth), self.trainRoutes[key][1]]})
                                                self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
                                                self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[key][1].title(), "block": self.trainRoutes[key][0], "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})
                                                break
                
            if (not updated):
            #case for if this is not the next block for any train
                self.mainScreen.updateMainScreen("TS", [location, line])
                return
            
            if (not (train == 0)):
                del self.trainRoutes[train]

###############################################################################################################################################################

    def updateTrainInManualEdit(self, key, location):
        children = self.meArea.get_children("")

        for child in children: 
        #iterate for each parent in the Treeview
            for item in self.meArea.get_children(child):
                dest = self.meArea.item(item, "text")
                if ("Train " + str(key) == dest):
                    self.meArea.set(item, column = "Location", value = "Block " + str(location))
                    self.mainScreen.tlArea.set(item, column = "Location", value = "Block " + str(location))
                    break
        
        self.trainRoutes[key][0] = int(location)

###############################################################################################################################################################

    def calculateAuthority(self, data, destination):
    #calculate the authority to the next station
        '''can add calculating distance as well'''
        if (data[1] == "green"):
            pos = data[0]
            dir = data[2]

            authority = 0
            dist = 0
            #running total

            found = False
            while (not found):
                #add distance
                if (pos == 101 or pos == 150):
                    dist += 35
                elif (pos == 119 or pos == 149):
                    dist += 40
                elif ((pos in range(27, 63)) or pos == 117 or pos == 118 or (pos in range(120, 148))):
                    dist += 50
                elif (pos in range(89, 101)):
                    dist += 75
                elif (pos == 104):
                    dist += 80
                elif (pos == 87):
                    dist += 86.6
                elif (pos == 107):
                    dist += 90
                elif ((pos in range(1, 13)) or pos == 26 or pos == 63 or pos == 64 or (pos in range(67, 77)) or pos == 86
                       or pos == 88 or pos == 102 or pos == 103 or pos == 105 or pos == 106 or (pos in range(108, 114))
                       or pos == 115 or pos == 116):
                    dist += 100
                elif (pos in range(13, 21)):
                    dist += 150
                elif (pos == 114):
                    dist += 162
                elif (pos == 148):
                    dist += 184
                elif (pos == 25 or pos == 65 or pos == 66):
                    dist += 200
                else:
                    dist += 300

                if (dir == "forward"):
                    if (pos == 100):
                        authority += 1
                        dir = "backward"
                        pos = 85

                    elif (pos == 150):
                        authority += 1
                        dir = "backward"
                        pos = 28

                    else:
                        authority += 1
                        pos += 1
                else:
                    if (pos == 76):
                        authority += 1
                        dir = "forward"
                        pos = 101
                    
                    elif (pos == 1):
                        authority += 1
                        dir = "forward"
                        pos = 13

                    else:
                        authority += 1
                        pos -= 1

                if (pos in self.greenStationLocations):
                    if (self.greenStationLocations[pos] == destination):
                        found = True

                        #add half of the block length for the last block
                        if (pos == 31 or pos == 39 or pos == 48 or pos == 57 or pos == 123 or pos == 132 or pos == 141):
                            dist += 25
                        elif (pos == 96):
                            dist += 37.5
                        elif (pos == 2 or pos == 9 or pos == 73 or pos == 88 or pos == 105):
                            dist += 50
                        elif (pos == 16):
                            dist += 75
                        elif (pos == 114):
                            dist += 81
                        elif (pos == 65):
                            dist += 100
                        elif (pos == 22 or pos == 77):
                            dist += 150


        else:
            pass

        return [authority, dist]

###############################################################################################################################################################

    def manualEdit(self, event):
    #handle user clicks in the manual edit Treeview

        rowID = self.meArea.identify_row(event.y)
        #grab row user clicked in 
        colID = self.meArea.identify_column(event.x)
        #grab column user clicked in
        if (rowID):
            if (colID == "#2"):
            #check that user clicked in destination column
                newDestination = simpledialog.askstring("Manual Edit", "Enter a new destination:")
                #entry box to enter a new destination
                if (newDestination is not None):
                    answer = askyesno(title = "Confirmation", message = "Would you like to change the destination?")
                    #confirmation pop-up, returns True is user clicks "Yes"
                    if (answer):
                        self.meArea.set(rowID, colID, value = newDestination)
                        self.mainScreen.tlArea.set(rowID, colID, value = newDestination)
                        #update main ui train location data

                        temp = self.meArea.item(rowID, "text")
                        train = ""
                        for char in temp:
                            if (char.isdigit()):
                                train += char
                        #grab train number
                        self.trainRoutes[int(train)][3] = newDestination
                        #update the route to show that the next stop was changed
                        values = self.calculateAuthority(self.trainRoutes[int(train)], newDestination)
                        auth = values[0] - 1
                        arrTime = self.timeToSeconds(self.meArea.item(rowID, "values")[2])
                        speed = float(values[1]) / arrTime


                        self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [train, f"{speed:.3f}", str(auth), self.trainRoutes[int(train)][1]]})
                        self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[int(train)][1].title(), "block": self.trainRoutes[int(train)][0], "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
                        self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[int(train)][1].title(), "block": self.trainRoutes[int(train)][0], "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})

            elif (colID == "#3"):
            #check that user clicked in arrival time column
                newTime = simpledialog.askstring("Manual Edit", "Enter a new arrival:")
                #entry box to enter a new time
                if (newTime is not None):
                    answer = askyesno(title = "Confirmation", message = "Would you like to change the arrival time?")
                    #confirmation pop-up, returns True if the user clicks "Yes"
                    if (answer):
                        self.meArea.set(rowID, colID, value = newTime)
                        self.mainScreen.tlArea.set(rowID, colID, value = newTime)
                        #update main ui train location data

                        temp = self.meArea.item(rowID, "text")
                        train = ""
                        for char in temp:
                            if (char.isdigit()):
                                train += char
                        #grab specific train number

                        
                        values = self.calculateAuthority(self.trainRoutes[int(train)], self.trainRoutes[int(train)][3])
                        auth = values[0] - 1
                        arrTime = self.timeToSeconds(newTime)
                        speed = float(values[1]) / arrTime
                        
                        self.mainScreen.send_to_ui("CTC_Test_UI", {"command": "TL", "value": [train, f"{speed:.3f}", str(auth), self.trainRoutes[int(train)][1]]})
                        self.mainScreen.send_to_ui("Track HW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[int(train)][1].title(), "block": self.trainRoutes[int(train)][0], "speed": f"{speed:.3f}", "authority": str(auth), "value_type": "suggested"}})
                        self.mainScreen.send_to_ui("Track SW", {"command": "update_speed_auth", "value": {"track": self.trainRoutes[int(train)][1].title(), "block": self.trainRoutes[int(train)][0], "speed": f"{speed:.2f}", "authority": str(auth), "value_type": "suggested"}})

###############################################################################################################################################################

    def updateAutoEdit(self):
        
        autoFile = filedialog.askopenfilename(title = "Select a file", initialdir = "/", filetypes = [("CSV files", "*.csv")])
        #get using input .csv file
        if (autoFile):
            schedule = pd.read_csv(autoFile)
            #grab text from file
            for i in range(0, len(schedule) - 1):
                dest = schedule.iloc[i, 0].split("-")
                arrTime = schedule.iloc[i, 1]
                line = schedule.iloc[i, 2]
                launchTime = schedule.iloc[i, 3]

                if (launchTime == "00:00"):
                    self.sendDeployData("63", dest[0], arrTime, line)
                    self.updateManualEdit("63", dest, arrTime, line)
                else:
                    self.scheduleBacklog([dest, arrTime, line, launchTime])

###############################################################################################################################################################

    def scheduleBacklog(self, data):
        if (clock.clock.getTime() == data[3]):
            self.sendDeployData("63", data[0][0], data[1], data[2])
            self.updateManualEdit("63", data[0], data[1], data[2])
        else:
            self.root.after(100, lambda: self.scheduleBacklog(data))

###############################################################################################################################################################

    def timeToSeconds(self, arrTimeStr):
    #convert a given time into seconds

        currTimeStr = clock.clock.getTime()

        arrTime = 0
        found = False
        #flag for finding colon
        arrHoursStr = ""
        arrHours = 0
        arrMinsStr = ""
        arrMins = 0
        for char in arrTimeStr:
            if (not found and char.isdigit()):
                arrHoursStr += char
            elif (not found and char == ":"):
                found = True
            elif (found and char.isdigit()):
                arrMinsStr += char
        
        arrHours += (int(arrHoursStr) * 3600)
        arrMins += (int(arrMinsStr) * 60)
        arrTime += (arrHours + arrMins)

        currTime = 0
        found = False
        #flag for finding colon
        currHoursStr = ""
        currHours = 0
        currMinsStr = ""
        currMins = 0
        for char in currTimeStr:
            if (not found and char.isdigit()):
                currHoursStr += char
            elif (not found and char == ":"):
                found = True
            elif (found and char.isdigit()):
                currMinsStr += char
        
        currHours += (int(currHoursStr) * 3600)
        currMins += (int(currMinsStr) * 60)
        currTime += (currHours + currMins)

        return float(arrTime - currTime)