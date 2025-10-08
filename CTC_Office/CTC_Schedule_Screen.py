import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk
from time import strftime
import CTC_Main_Screen

class ScheduleScreen:
#"Schedule" ui screen appearance and data
    '''
    Attributes:
    
    self.root: main Tk() variable for the ui window
    self.frame: main ttk.Frame() that all ui widgets are placed onto
    self.mainScreen: holds the MainScreen object that displays the "Syestem Information" tab
    self.notebook: main notebook that contains the ui tabs
    self.trainNum: number of trains released into the yard
    self.refMap: screen for the reference map image
    self.clockText: a ttk.Label() that holds the current time
    self.clockTimer: contains the call to updateTime, allowing the program to cancel the timer when switching tabs
    '''

    def __init__(self, root: tk.Tk, main: CTC_Main_Screen, frame: ttk.Frame, notebook: ttk.Notebook, refMap: tk.Tk):
    #initialize class variables and create backdrop for schedule screen

        self.root = root  #main variable for the window
        self.frame = frame
        self.mainScreen = main  #variable to hold the data of the schedule screen
        self.refMap = refMap
        self.notebook = notebook  #variable to hold data about the tab buttons
        self.trainNum = 0;  #number of trains that have been sent to the system

        #self.clockText: a variable to allow the time to be updated continuously
        #self.clockTimer: a variable to hold the time for an interrupt to update the clock

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
        locSelect["values"] = ["Station B", "Station C"]
        #for BLUE LINE ONLY
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
        getDeploy = ttk.Button(buttonFrame, text = "Deploy Train", style = "TButton", command = lambda: (self.sendDeployData("1", selectedLocation.get(), arrivalTime.get(), "blue"), self.updateManualEdit("1", selectedLocation.get(), arrivalTime.get(), "blue")))
        getDeploy.pack(pady = 15, side = "top", fill = "x")
        #grab inputs from the Combobox and Entry (if user inputs values)
        autoButton = ttk.Button(buttonFrame, text = "Automatic Mode", style = "TButton")
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

        time = strftime("%I:%M %p")
        self.clockText.configure(text = time)
        self.clockTimer = self.root.after(1000, self.updateTime)

###############################################################################################################################################################
    
    def updateToMain(self, event):
    #update the screen if "System Information" tab is clicked
        if (event.widget.tab(event.widget.select(), "text") == "System Information"):
        #prevents errors on boot
            self.root.after_cancel(self.clockTimer)
            #cancel this call if active
            self.notebook.select(0)

###############################################################################################################################################################

    def dispRefMap(self):
    #display the reference map to the user

        self.refMap.title("Reference Map")
        self.refMap.geometry("1000x500+1201+0")
        #configure the window holding the reference map

        mapOriginalImage = Image.open("CTC_Office/blue_line.png") 
        mapImage = ImageTk.PhotoImage(mapOriginalImage.resize((1000, 500)))
        #create and resize image
        mapImageLabel = ttk.Label(self.refMap, image = mapImage, background = "white")
        mapImageLabel.image = mapImage
        #keep a reference to the image so that it appears on the window
        mapImageLabel.pack()

###############################################################################################################################################################
    
    def sendDeployData(self, location: str, destination: str, time: str, line: str):
    #send user inputs to main screen to update train locations Treeview

        self.trainNum += 1
        #increase of trains on the line
        self.mainScreen.update_train_locations(location, destination, time, line, self.trainNum)

###############################################################################################################################################################

    def updateManualEdit(self, location: str, destination: str, time: str, line: str):
    #update the manual edit tab

        children = self.meArea.get_children("")
        #get a list of the items in the Treeview
        if (not children):
        #if there is no data yet, add first item
            level = self.meArea.insert('', "end", text = line.title())
            self.meArea.insert(level, "end", text = ("Train " + str(self.trainNum)), values = [("Block " + location), destination, time])
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
                        self.meArea.item(item, values = ["Block " + location, destination, time])
                        added = True
                        break
                if (not added and self.meArea.item(child, "text") == line.title()):
                #if train does not exist but is on an existing line, add under that specific line
                    self.meArea.insert(child, "end", text = "Train " + str(self.trainNum), values = [("Block " + location), destination, time])
                    added = True
                    break
            if (not added):
            #if item is not already in the treeview, add a new parent/child set
                level = self.meArea.insert('', "end", text = line.title())
                self.meArea.insert(level, "end", text = "Train " + str(self.trainNum), values = [("Block " + location), destination, time])

        '''
        Write all data to to_test_ui.txt data file so the test ui can read in data changes
        Follows formatting rules specified in README.txt
        '''
        outfile = open("CTC_Office/to_test_ui.txt", "w")
        outfile.write("TL\n")
        outfile.write(str(self.trainNum) + "\n")
        outfile.write("70\n")
        outfile.write("8\n")
        outfile.write(line + "\n")
        outfile.close()

###############################################################################################################################################################

    def manualEdit(self, event):
    #handle user clicks in the maintenance mode Treeview

        row_id = self.meArea.identify_row(event.y)
        #grab row user clicked in 
        col_id = self.meArea.identify_column(event.x)
        #grab column user clicked in
        if (row_id):
            if (col_id == "#2"):
            #check that user clicked in destination column
                newDestination = simpledialog.askstring("Manual Edit", "Enter a new destination:")
                #entry box to enter a new destination
                if (newDestination is not None):
                    answer = askyesno(title = "Confirmation", message = "Would you like to change the destination?")
                    #confirmation pop-up, returns True is user clicks "Yes"
                    if (answer):
                        self.meArea.set(row_id, col_id, value = newDestination)
                        self.mainScreen.tlArea.set(row_id, col_id, value = newDestination)
                        #update main ui train location data
                        
                        '''
                        Write all data to to_test_ui.txt data file so the test ui can read in data changes
                        Follows formatting rules specified in README.txt
                        '''
                        outfile = open("CTC_Office/to_test_ui.txt", "w")
                        outfile.write("TL\n")

                        temp = self.meArea.item(row_id, "text")
                        train = ""
                        for char in temp:
                            if (char.isdigit()):
                                train += char
                        outfile.write(train + "\n")
                        outfile.write("60\n")
                        outfile.write("7\n")
                        outfile.write(self.meArea.item(self.meArea.parent(row_id), "text") + "\n")
                        outfile.close()

            elif (col_id == "#3"):
            #check that user clicked in arrival time column
                newTime = simpledialog.askstring("Manual Edit", "Enter a new arrival:")
                #entry box to enter a new time
                if (newTime is not None):
                    answer = askyesno(title = "Confirmation", message = "Would you like to change the arrival time?")
                    #confirmation pop-up, returns True if the user clicks "Yes"
                    if (answer):
                        self.meArea.set(row_id, col_id, value = newTime)
                        self.mainScreen.tlArea.set(row_id, col_id, value = newTime)
                        #update main ui train location data

                        '''
                        Write all data to to_test_ui.txt data file so the test ui can read in data changes
                        Follows formatting rules specified in README.txt
                        '''
                        outfile = open("CTC_Office/to_test_ui.txt", "w")
                        outfile.write("TL\n")

                        temp = self.meArea.item(row_id, "text")
                        train = ""
                        for char in temp:
                            if (char.isdigit()):
                                train += char
                        #grab specific train number
                        outfile.write(train + "\n")
                        outfile.write("80\n")
                        outfile.write("9\n")
                        outfile.write(self.meArea.item(self.meArea.parent(row_id), "text") + "\n")
                        outfile.close()

            #add outputs to test ui