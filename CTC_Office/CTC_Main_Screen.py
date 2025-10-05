import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from time import strftime
import CTC_Schedule_Screen as Sch

class MainScreen:
    def __init__(self, root, schedule, canvas, notebook):
        self.root = root  #main variable for the window
        self.canvas = canvas
        self.canvas_width = 1160  #width of white canvas
        self.canvas_height = 885  #height of white canvas
        self.schedule_screen = schedule  #variable to hold the data of the schedule screen
        self.notebook = notebook  #variable to hold data about the tab buttons

        #self.canvas: a white screen add shapes to
        #self.clock_time: a variable to allow the time to be updated
    

    def create_main_screen(self):
        self.create_top_row()
        self.create_titles()  #print the titles of each section to the window

        
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

        self.notebook.bind("<<NotebookTabChanged>>", self.update_to_schedule)  #bind the tab switching action to a handler function


    #create the titles of each section on the "System Information" tab
    def create_titles(self):
        #train location area
        tl_text = self.canvas.create_text(125, 100, text = " Train Locations ", anchor = "nw", font = ("Arial", 20), fill = "white")  #write title text
        tl_rect = self.canvas.create_rectangle((self.canvas.bbox(tl_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(tl_text)  #place the text over the rectangle
        
        tl_area = self.canvas.create_rectangle((self.canvas.bbox(tl_rect)[0] + 1, self.canvas.bbox(tl_rect)[3] + 5, self.canvas.bbox(tl_rect)[0] + 400, self.canvas.bbox(tl_rect)[3] + 200), fill = "white", outline = "black")  #area for location data to appear

        #track state area
        ts_text = self.canvas.create_text(125, self.canvas.bbox(tl_area)[3] + 10, text = " Track State ", anchor = "nw", font = ("Arial", 20), fill = "white")
        ts_rect = self.canvas.create_rectangle((self.canvas.bbox(ts_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(ts_text)  #place the text over the rectangle
        ts_area = self.canvas.create_rectangle((self.canvas.bbox(ts_rect)[0] + 1, self.canvas.bbox(ts_rect)[3] + 5, self.canvas.bbox(ts_rect)[0] + 400, self.canvas.bbox(ts_rect)[3] + 200), fill = "white", outline = "black")  #area for location data to appear

        #maintenance mode area
        mm_text = self.canvas.create_text(125, self.canvas.bbox(ts_area)[3] + 10, text = " Maintenance Mode ", anchor = "nw", font = ("Arial", 20), fill = "white")  #write title text
        mm_rect = self.canvas.create_rectangle((self.canvas.bbox(mm_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(mm_text)  #place the text over the rectangle
        mm_area = self.canvas.create_rectangle((self.canvas.bbox(mm_rect)[0] + 1, self.canvas.bbox(mm_rect)[3] + 5, self.canvas.bbox(mm_rect)[0] + 400, self.canvas.bbox(mm_rect)[3] + 200), fill = "white", outline = "black")  #area for location data to appear

        #thoughput area
        tp_area = self.canvas.create_rectangle((self.canvas_width - 400 - 125, self.canvas.bbox(tl_area)[1], self.canvas_width - 125, self.canvas.bbox(tl_area)[1] + 100), fill = "white", outline = "black")  #area for location data to appear
        tp_text = self.canvas.create_text(self.canvas.bbox(tp_area)[0] + 2, self.canvas.bbox(tp_area)[1] - 5, text = " Throughputs ", anchor = "sw", font = ("Arial", 20), fill = "white")  #write title text
        tp_rect = self.canvas.create_rectangle((self.canvas.bbox(tp_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(tp_text)  #place the text over the rectangle

        #light states area
        ls_text = self.canvas.create_text(self.canvas.bbox(tp_text)[0], self.canvas.bbox(tp_area)[3] + 10, text = " Light State ", anchor = "nw", font = ("Arial", 20), fill = "white")
        ls_rect = self.canvas.create_rectangle((self.canvas.bbox(ls_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(ls_text)  #place the text over the rectangle
        ls_area = self.canvas.create_rectangle((self.canvas.bbox(ls_rect)[0] + 1, self.canvas.bbox(ls_rect)[3] + 5, self.canvas.bbox(ls_rect)[0] + 400, self.canvas.bbox(ls_rect)[3] + 200), fill = "white", outline = "black")  #area for location data to appear
        
        #railway crossings area
        rc_text = self.canvas.create_text(self.canvas.bbox(tp_text)[0], self.canvas.bbox(ls_area)[3] + 10, text = " Railway Crossings ", anchor = "nw", font = ("Arial", 20), fill = "white")
        rc_rect = self.canvas.create_rectangle((self.canvas.bbox(rc_text)), fill = "#4d4d6d", outline = "black")  #create rectangle border
        self.canvas.tag_raise(rc_text)  #place the text over the rectangle
        rc_area = self.canvas.create_rectangle((self.canvas.bbox(rc_rect)[0] + 1, self.canvas.bbox(rc_rect)[3] + 5, self.canvas.bbox(rc_rect)[0] + 400, self.canvas.bbox(rc_rect)[3] + 200), fill = "white", outline = "black")  #area for location data to appear
        


    #update the time variable
    def update_time(self):
        time = strftime("%I:%M %p")
        self.canvas.itemconfig(self.clock_text, text = time)
        self.root.after(1000, self.update_time)

    
    #update the screen if "Schedule" tab is clicked
    def update_to_schedule(self, event):
        #prevents the screen from appearing blank on first launch
        if (event.widget.tab(event.widget.select(), "text") == "Schedule"):
            self.canvas.delete("all")
            self.schedule_screen.create_schedule_screen()
        else:
            return
        

    #display the reference map to the user
    def disp_ref_map(self):
        ref_map = tk.Tk()
        ref_map.title("Reference Map")
        ref_map.geometry("500x925+1201+0")

        ref_map.mainloop()