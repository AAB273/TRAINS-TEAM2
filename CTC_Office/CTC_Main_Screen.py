import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from time import strftime
import CTC_Schedule_Screen as Sch


class MainScreen:
    def __init__(self, root, schedule, frame, notebook):
        self.root = root  #main variable for the window
        self.frame = frame
        self.frame_width = 1160  #width of white canvas
        self.frame_height = 885  #height of white canvas
        self.schedule_screen = schedule  #variable to hold the data of the schedule screen
        self.notebook = notebook  #variable to hold data about the tab buttons
        #self.clock_text: a variable to allow the time to be updated
        #self.clock_timer: a variable to hold the time for an interrupt to update the clock

        #self.tpArea: contains the treeview for the throughput data
        self.totalPassengers = 0  #number of passengers on a line
        self.numberOfTrains = 1  #number of trains on a line

        #self.lsArea: contains the treeview for the light state data



        self.create_top_row()  #print the logo, reference map button, time
        self.create_titles()  #print the titles of each section to the window


    #update any data according to the data file
    def update_main_screen(self):
        infile = open("CTC_Office/CTC_data.txt", "r")  #read in the data file text
        data = infile.readline()  #grab the first line to see what data needs to be updated

        if (data.strip() == "LS"):  #case for light switch data
            #grab location, light state, and line info
            location = infile.readline().strip()
            state = infile.readline().strip()
            line = infile.readline().strip()
            
            #get actual light states from the binary code
            if (state == "00"):
                state = "red"
            elif (state == "01"):
                state = "yellow"
            elif (state == "10"):
                state = "green"
            else:
                state = "supergreen"

            #update or create line
            children = self.ls_area.get_children("")
            if (not children):  #if there is nothing added yet, add the first parent/child
                level = self.ls_area.insert('', "end", text = line.title())
                self.ls_area.insert(level, "end", text = "Block " + location, values = {state})
            else:
                added = False  #flag for adding a new light state
                for child in children:  #iterate for each parent in the treeview
                    for item in self.ls_area.get_children(child):  #iterate for each child of every parent in the treeview
                        loc = self.ls_area.item(item, "text")  #grab the location text
                        if ((loc == ("Block " + location))):  #check if the location already exists
                            self.ls_area.item(item, values = {state})  #update the light state
                            added = True  #change flag
                            break
                if (not added):  #if value is not already in the treeview, add a new parent/child set
                    level = self.ls_area.insert('', "end", text = line.title())
                    self.ls_area.insert(level, "end", text = "Block " + location, values = {state})

        elif (data.strip() == "TP"):  #throughput data
            #grab data and update total passengers on line
            tickets = int(infile.readline().strip())
            disemb = int(infile.readline().strip())
            line = infile.readline().strip()
            self.totalPassengers += (tickets - disemb)  #add new passengers to total

            children = self.tp_area.get_children("")
            if (not children):  #if there is no data yet, add first child
                self.tp_area.insert("", "end", text = line.title(), values = {self.totalPassengers/self.numberOfTrains})
            else:
                for child in children:  #iterate for each child in the treeview
                    text = self.tp_area.item(child, "text")  #grab the line text of the child
                    if (text == line.title()):  #update if already exists
                        self.tp_area.item(child, values = {self.totalPassengers/self.numberOfTrains})
                        break
                    else:  #add new if it does not exist yet
                        self.tp_area.insert("", "end", text = line.title(), values = {self.totalPassengers/self.numberOfTrains})
                        break
        
        #close read-in file, then blank the data file
        infile.close()
        reset = open("CTC_Office/CTC_data.txt", "w")
        reset.close()

        
    def create_top_row(self):
        #sub-frame used to center the top row of widgets
        top_frame = ttk.Frame(self.frame, style = "white.TFrame")
        top_frame.pack(side = "top", anchor = "n", expand = True, fill = "x")

       #create the BLT logo
        blt_original_image = Image.open("CTC_Office/blt logo.png")  #create a image variable of the logo
        blt_original_image = blt_original_image.resize((75, 75))  #resize the image
        blt_image = ImageTk.PhotoImage(blt_original_image)  #create a TKinter image variable from the origninal image
        blt_image_label = ttk.Label(top_frame, image = blt_image, background = "white")  #create an image widget
        blt_image_label.image = blt_image  #keep a reference to the image so that it appears on the window
        blt_image_label.pack(side = "left", anchor = "nw")  #pack the label to the top left corner of the top_row sub-frame

        #create a button to display the reference map
        center_frame = ttk.Frame(top_frame)  #create another sub-frame to center the button
        center_frame.pack(side="left", anchor = "n", expand=True)  #pck the button in the center of the top row
        button_style = ttk.Style()
        button_style.configure("TButton", font = ("Arial", 15))  #change text style
        map_button = ttk.Button(center_frame, text = "Reference Map", style = "TButton", command = lambda: self.disp_ref_map())
        map_button.pack(pady = 5, anchor = "n")  #pack in the top-center of the center_frame sub-frame

        #create a label for the time
        self.clock_text = ttk.Label(top_frame, text = "", font = ("Arial", 20, "bold"), background = "white")  #create the text
        self.clock_text.pack(side = "right", anchor = "ne")  #pack to the top-right corner of the top_row sub-frame
        self.update_time()  #run the function to continually update the time

        self.notebook.bind("<<NotebookTabChanged>>", self.update_to_schedule)  #bind the tab switching action to a handler function


    #create the titles of each section on the "System Information" tab
    def create_titles(self):
        #create a sub-frame for each side of the screen to center all widgets
        left_frame = ttk.Frame(self.frame, style = "white.TFrame")
        left_frame.pack(side = "left", expand = True, fill = "y")
        right_frame = ttk.Frame(self.frame, style = "white.TFrame")
        right_frame.pack(side = "left", expand = True, fill = "y")

        white_text = ttk.Style()  #Style to put white text in each of the titles
        white_text.configure("White.TLabel", foreground = "white", font = ("Arial", 20))

        #train location area
        tl_frame = ttk.Frame(left_frame, style = "white.TFrame")  #sub-frame to store the train location area
        tl_frame.pack(pady = 5, side = "top", expand = True)  #pack into the left sub-frame
        tl_text = ttk.Label(tl_frame, text = " Train Locations ", style = "White.TLabel")  #create title widget
        tl_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")
        tl_text.pack(side = "top")  #add to frame
        #create and format the area for the train location information to be displayed
        tl_area = ttk.Treeview(tl_frame, columns = ("Destination", "Arrival Time")) 
        tl_area.heading("#0", text = "Location")
        tl_area.heading("Destination", text = "Destination")
        tl_area.heading("Arrival Time", text = "Arrival Time")
        tl_area.column("#0", width = 150)
        tl_area.column("Destination", width = 150)
        tl_area.column("Arrival Time", width = 100)
        tl_area.pack(side = "left")

        tl_scrollbar = ttk.Scrollbar(tl_frame, orient = "vertical", command = tl_area.yview)
        tl_area.configure(yscrollcommand = tl_scrollbar.set)
        tl_scrollbar.pack(side = "right", fill = "y")

        #track state area
        ts_frame = ttk.Frame(left_frame, style = "white.TFrame")  #sub-frame to store the track state area
        ts_frame.pack(pady = 5, side = "top", expand = True)  #pack into the left sub-frame
        ts_text =  ttk.Label(ts_frame, text = " Track State ", style = "White.TLabel")
        ts_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        ts_text.pack(side = "top")
        #create and format the area for the track state information to be displayed
        ts_area = ttk.Treeview(ts_frame, columns = ("Maintenance"))
        ts_area.heading("#0", text = "Location")
        ts_area.heading("Maintenance", text = "Maintenance")
        ts_area.column("#0", width = 200)
        ts_area.column("Maintenance", width = 200)
        ts_area.pack(side = "left")

        ts_scrollbar = ttk.Scrollbar(ts_frame, orient = "vertical", command = ts_area.yview)
        ts_area.configure(yscrollcommand = ts_scrollbar.set)
        ts_scrollbar.pack(side = "right", fill = "y")

        #maintenance mode area
        mm_frame = ttk.Frame(left_frame, style = "white.TFrame")  #sub-frame to store the maintenance mode area
        mm_frame.pack(pady = 5, side = "top", expand = True)  #pack into the left sub-frame
        mm_text =  ttk.Label(mm_frame, text = " Maintenance Mode ", style = "White.TLabel")
        mm_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        mm_text.pack(side = "top")
        #create and format the area for the maintenance mode information to be displayed
        mm_area = ttk.Treeview(mm_frame, columns = ("Direction", "Switch"))
        mm_area.heading("#0", text = "Location")
        mm_area.heading("Direction", text = "Block pointed towards")
        mm_area.heading("Switch", text = "Switch?")
        mm_area.column("#0", width = 150)
        mm_area.column("Direction", width = 150)
        mm_area.column("Switch", width = 100)
        mm_area.pack(side = "left")

        mm_scrollbar = ttk.Scrollbar(mm_frame, orient = "vertical", command = mm_area.yview)
        mm_area.configure(yscrollcommand = mm_scrollbar.set)
        mm_scrollbar.pack(side = "right", fill = "y")

        #thoughput area
        tp_frame = ttk.Frame(right_frame, style = "white.TFrame")  #sub-frame to store the maintenance mode area
        tp_frame.pack(pady = 5, side = "top", expand = True)  #pack into the left sub-frame
        tp_text =  ttk.Label(tp_frame, text = " Throughput ", style = "White.TLabel")
        tp_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        tp_text.pack(side = "top")
        #create and format the area for the throughput information to be displayed
        self.tp_area = ttk.Treeview(tp_frame, columns = ("Throughput"), height = 2)  #only 2 lines max, so no need to show extra
        self.tp_area.heading("#0", text = "Line")
        self.tp_area.heading("Throughput", text = "Throughput")
        self.tp_area.column("#0", width = 200)
        self.tp_area.column("Throughput", width = 200)
        self.tp_area.pack(side = "top")

        #light states area
        ls_frame = ttk.Frame(right_frame, style = "white.TFrame")  #sub-frame to store the maintenance mode area
        ls_frame.pack(pady = 5, side = "top", expand = True)  #pack into the left sub-frame
        ls_text =  ttk.Label(ls_frame, text = " Light States ", style = "White.TLabel")
        ls_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        ls_text.pack(side = "top")
        #create and format the area for the light state information to be displayed
        self.ls_area = ttk.Treeview(ls_frame, columns = ("State"))
        self.ls_area.heading("#0", text = "Location")
        self.ls_area.heading("State", text = "State")
        self.ls_area.column("#0", width = 200)
        self.ls_area.column("State", width = 200)
        self.ls_area.pack(side = "left")

        ls_scrollbar = ttk.Scrollbar(ls_frame, orient = "vertical", command = self.ls_area.yview)
        self.ls_area.configure(yscrollcommand = ls_scrollbar.set)
        ls_scrollbar.pack(side = "right", fill = "y")
        
        #railway crossings area
        rc_frame = ttk.Frame(right_frame, style = "white.TFrame")  #sub-frame to store the maintenance mode area
        rc_frame.pack(pady = 5, side = "top", expand = True)  #pack into the left sub-frame
        rc_text =  ttk.Label(rc_frame, text = " Railway Crossings ", style = "White.TLabel")
        rc_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")        
        rc_text.pack(side = "top")
        #create and format the area for the railrway crossing information to be displayed
        rc_area = ttk.Treeview(rc_frame, columns = ("State"))
        rc_area.heading("#0", text = "Location")
        rc_area.heading("State", text = "State")
        rc_area.column("#0", width = 200)
        rc_area.column("State", width = 200)
        rc_area.pack(side = "left")

        rc_scrollbar = ttk.Scrollbar(rc_frame, orient = "vertical", command = rc_area.yview)
        rc_area.configure(yscrollcommand = rc_scrollbar.set)
        rc_scrollbar.pack(side = "right", fill = "y")
        

    #update the time variable
    def update_time(self):
        time = strftime("%I:%M %p")
        self.clock_text.configure(text = time)
        self.clock_timer = self.root.after(1000, self.update_time)

    
    #update the screen if "Schedule" tab is clicked
    def update_to_schedule(self, event):
        if (event.widget.tab(event.widget.select(), "text") == "Schedule"):  #prevents errors on boot
            self.root.after_cancel(self.clock_timer)  #cancel the interrupt timer
            self.notebook.select(1)
        

    #display the reference map to the user
    def disp_ref_map(self):
        ref_map = tk.Tk()
        ref_map.title("Reference Map")
        ref_map.geometry("500x925+1201+0")
        ref_map.mainloop()