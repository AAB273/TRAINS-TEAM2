import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import CTC_Main_Screen
import CTC_Schedule_Screen

#full background color = #1a1a4d
#box color = #4d4d6d


def main():
    #declaring the variable to represent the window and configuring the window
    root = tk.Tk()
    root.title("CTC Office")  #title of the window
    root.geometry('1200x925+0+0')  #size of the window
    root.maxsize(1200, 925)  #set the maximum size of the window
    root.configure(background = "#1a1a4d")
    
    main_notebook = ttk.Notebook(root)  #create the tab buttons at the top of the screen
    main_notebook.pack()  #place the notebook on the window
    backgound_style = ttk.Style()  #configure the color of the tabs
    backgound_style.configure("TFrame", background = "#1a1a4d")  #set the color of the style object
    system_frame = ttk.Frame(root, style = "TFrame", width = 1200, height = 925)  #create the System Information tab
    schedule_frame = ttk.Frame(root, style = "TFrame", width = 1200, height = 925)  #create the Schedule tab

    #create the canvases for making the UI screens on
    system_canvas = tk.Canvas(system_frame, bg = "white", width = 1160, height = 885)
    system_canvas.pack(padx = 20, pady = 20)
    schedule_canvas = tk.Canvas(schedule_frame, bg = "white", width = 1160, height = 885)
    schedule_canvas.pack(padx = 20, pady = 20)

    #add both tabs to the notebook
    main_notebook.add(system_frame, text = "System Information")  
    main_notebook.add(schedule_frame, text = "Schedule")

    main_screen = CTC_Main_Screen.MainScreen(root, 0, system_canvas, main_notebook)
    schedule_screen = CTC_Schedule_Screen.ScheduleScreen(root, main_screen, schedule_canvas, main_notebook)
    main_screen.schedule_screen = schedule_screen

    main_screen.create_main_screen()
        
    root.mainloop()  #checks for keystrokes



    


main()  #main function call