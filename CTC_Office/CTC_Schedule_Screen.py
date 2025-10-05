import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from time import strftime
import CTC_Main_Screen

class ScheduleScreen:
    def __init__(self, root, main, canvas, notebook):
        self.root = root  #main variable for the window
        self.canvas = canvas
        self.canvas_width = 1160  #width of white canvas
        self.canvas_height = 885  #height of white canvas
        self.main_screen = main  #variable to hold the data of the schedule screen
        self.notebook = notebook  #variable to hold data about the tab buttons

        #self.clock_time: a variable to allow the time to be updated continuously


    def create_schedule_screen(self):
        self.create_top_row()  #print to top row of the UI to the window
        self.create_titles()
        

    #create the logo, tab, and reference map button
    def create_top_row(self):
        #create the BLT logo
        blt_original_image = Image.open("CTC_Office/blt logo.png")  #create a image variable of the logo
        blt_original_image = blt_original_image.resize((75, 75))  #resize the image
        blt_image = ImageTk.PhotoImage(blt_original_image)  #create a TKinter image variable from the origninal image
        
        self.canvas.create_image(0, 0, image = blt_image, anchor = 'nw')
        self.canvas.image = blt_image  #keep the image as a reference to save
        
        #create a label for the time
        self.clock_text = self.canvas.create_text(self.canvas_width - 5, 0, text = "", anchor = 'ne', font = ("Arial", 20, "bold"), fill = "black")  #create the text
        self.update_time()  #run the function to continually update the time

        #create a button to display the reference map
        button_style = ttk.Style()
        button_style.configure("TButton", font = ("Arial", 15))
        map_button = ttk.Button(self.canvas, text = "Reference Map", style = "TButton", command = lambda: self.disp_ref_map())
        map_button.place(x = 500, y = 5, anchor = "nw")

        self.notebook.bind("<<NotebookTabChanged>>", self.update_to_main)  #bind the tab switching to a handler function


    #create the titles of each section on the "System Information" tab
    def create_titles(self):
        #create area for manually scheduling a train
        st_text = self.canvas.create_text(self.canvas_width - 400 - 125, 100, text = " Schedule Train ", anchor = "nw", font = ("Arial", 20), fill = "white")  #write title text
        st_rect = self.canvas.create_rectangle((self.canvas.bbox(st_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(st_text)  #place the text over the rectangle
        #widgets added for scheduling, as well as the buttons for deployment and auto scheduling

        #create area for manually editing train
        me_text = self.canvas.create_text(125, 100, text = " Schedule Train ", anchor = "nw", font = ("Arial", 20), fill = "white")  #write title text
        me_rect = self.canvas.create_rectangle((self.canvas.bbox(me_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(me_text)  #place the text over the rectangle


    #update the time variable
    def update_time(self):
        time = strftime("%I:%M %p")
        self.canvas.itemconfig(self.clock_text, text = time)
        self.root.after(1000, self.update_time)

    
    #update the screen if "System Information" tab is clicked
    def update_to_main(self, event):
        self.canvas.delete("all")
        self.main_screen.create_main_screen()


    #display the reference map to the user
    def disp_ref_map(self):
        self.main_screen.disp_ref_map()