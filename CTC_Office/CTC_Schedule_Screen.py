import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from time import strftime
import CTC_Main_Screen

class ScheduleScreen:
    def __init__(self, root, main, frame, notebook):
        self.root = root  #main variable for the window
        self.frame = frame
        self.frame_width = 1160  #width of white canvas
        self.frame_height = 885  #height of white canvas
        self.main_screen = main  #variable to hold the data of the schedule screen
        self.notebook = notebook  #variable to hold data about the tab buttons

        #self.clock_text: a variable to allow the time to be updated continuously
        #self.clock_timer: a variable to hold the time for an interrupt to update the clock

        self.create_top_row()  #print to top row of the UI to the window
        self.create_titles()


    def update_schedule_screen(self):
        pass
        
        

    #create the logo, tab, and reference map button
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

        self.notebook.bind("<<NotebookTabChanged>>", self.update_to_main)  #bind the tab switching action to a handler function


    #create the titles of each section on the "System Information" tab
    def create_titles(self):
        pass
        #create a sub-frame for each side of the screen to center all widgets
        left_frame = ttk.Frame(self.frame, style = "white.TFrame")
        left_frame.pack(pady = 125, side = "left", expand = True, fill = "y")
        right_frame = ttk.Frame(self.frame, style = "white.TFrame")
        right_frame.pack(side = "left", expand = True, fill = "y")

        white_text = ttk.Style()  #Style to put white text in each of the titles
        white_text.configure("White.TLabel", foreground = "white", font = ("Arial", 20))

        #create area for manually scheduling a train
        sc_text = ttk.Label(left_frame, text = " Schedule Train ", style = "White.TLabel")
        sc_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")
        sc_text.pack(pady = 50, side = "top")
        
        #enter location
        loc_frame = ttk.Frame(left_frame, style = "white.TFrame")
        loc_frame.pack(pady = 25, side = "top", fill = "x")
        loc_text = ttk.Label(loc_frame, text = "Select a destination:")
        loc_text.pack(padx = 5, pady = 5, fill = "x")

        selected_location = tk.StringVar()
        loc_select = ttk.Combobox(loc_frame, textvariable = selected_location)
        loc_select.pack(padx = 5, pady = 5, fill = "x")

        #enter time
        time_frame = ttk.Frame(left_frame, style = "white.TFrame")
        time_frame.pack(pady = 25, side = "top", fill = "x")
        time_text = ttk.Label(time_frame, text = "Enter a time:")
        time_text.pack(padx = 5, pady = 5, fill = "x")

        time_entry = ttk.Entry(time_frame)
        time_entry.pack(padx = 5, pady = 5, fill = "x")

        #deploy button and auto button
        button_frame = ttk.Frame(left_frame, style = "white.TFrame")
        button_frame.pack(pady = 40, side = "top", expand = True)
        dep_button = ttk.Button(button_frame, text = "Deploy Train", style = "TButton")
        dep_button.pack(pady = 5, side = "top", fill = "x")
        auto_button = ttk.Button(button_frame, text = "Automatic Mode", style = "TButton")
        auto_button.pack(side = "top")

    
        #create area for manually editing train
        me_frame = ttk.Frame(right_frame, style = "white.TFrame")
        me_frame.pack(pady = 160, side = "top")
        me_text = ttk.Label(me_frame, text = " Manual Edit ", style = "White.TLabel")
        me_text.config(relief = "solid", borderwidth = 2, background = "#4d4d6d")
        me_text.pack()

        #create and format the area for the train location information to be displayed
        me_area = ttk.Treeview(me_frame, columns = ("Destination", "Arrival Time")) 
        me_area.heading("#0", text = "Location")
        me_area.heading("Destination", text = "Destination")
        me_area.heading("Arrival Time", text = "Arrival Time")
        me_area.column("#0", width = 150)
        me_area.column("Destination", width = 150)
        me_area.column("Arrival Time", width = 100)
        me_area.pack(side = "left")

        me_scrollbar = ttk.Scrollbar(me_frame, orient = "vertical", command = me_area.yview)
        me_area.configure(yscrollcommand = me_scrollbar.set)
        me_scrollbar.pack(side = "right", fill = "y")


    #update the time variable
    def update_time(self):
        time = strftime("%I:%M %p")
        self.clock_text.configure(text = time)
        self.clock_timer = self.root.after(1000, self.update_time)

    
    #update the screen if "System Information" tab is clicked
    def update_to_main(self, event):
        if (event.widget.tab(event.widget.select(), "text") == "System Information"):
            self.root.after_cancel(self.clock_timer)  #cancel the interrupt timer
            self.notebook.select(0)


    #display the reference map to the user
    def disp_ref_map(self):
        self.main_screen.disp_ref_map()