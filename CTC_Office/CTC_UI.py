import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import CTC_Main_Screen
import CTC_Schedule_Screen
import CTC_Test_UI
import os

#full background color = #1a1a4d
#box color = #4d4d6d


def main():
    #declaring the variable to represent the window and configuring the window
    root = tk.Tk()
    win = tk.Toplevel(root)
    root.title("CTC Office")  #title of the window
    root.geometry('1200x925+0+0')  #size of the window
    root.maxsize(1200, 925)  #set the maximum size of the window
    root.configure(background = "#1a1a4d")
    
    main_notebook = ttk.Notebook(root)  #create the tab buttons at the top of the screen
    main_notebook.pack(padx = 20, pady = 20, fill = "both")  #place the notebook on the window
    backgound_style = ttk.Style()  #configure the color of the tabs
    backgound_style.configure("white.TFrame", background = "white")  #set the color of the style object
    system_frame = ttk.Frame(root, style = "white.TFrame", width = 1160, height = 885)  #create the System Information tab
    schedule_frame = ttk.Frame(root, style = "white.TFrame", width = 1160, height = 885)  #create the Schedule tab

    #add both tabs to the notebook
    main_notebook.add(system_frame, text = "System Information")  
    main_notebook.add(schedule_frame, text = "Schedule")

    main_screen = CTC_Main_Screen.MainScreen(root, 0, system_frame, main_notebook)
    schedule_screen = CTC_Schedule_Screen.ScheduleScreen(root, main_screen, schedule_frame, main_notebook)
    main_screen.schedule_screen = schedule_screen

    test_ui = CTC_Test_UI.TestUI(win)
    
    programLoop(root, main_screen)
        
    root.mainloop()  #checks for keystrokes


def programLoop(root, main_screen):
    if (os.stat("CTC_Office/CTC_data.txt").st_size != 0):
        main_screen.update_main_screen()

    root.after(500, programLoop, root, main_screen)


main()  #main function call