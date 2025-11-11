import tkinter as tk
from tkinter import ttk
import CTC_Main_Screen
import CTC_Schedule_Screen
import CTC_Test_UI
import os

#necessary to import the clock from the parent directory#
import sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
import clock

#full background color = #1a1a4d
#box color = #4d4d6d

#to fix: 
#error checking for clicking parents in treeviews
#error checking for inputing time on schedule
#turn station input into combobox on schedule train
#add try/except for inputting files
#when time is at 10x, allow trains to be scheduled at specific times


def main():
    #main function to create ui screens and create the interactions between them

    root = tk.Tk()
    win = tk.Toplevel(root)
    #declaring main window, as well as test ui and reference map windows as subwindows of the main
    root.title("CTC Office")
    root.geometry('1200x925+0+0')
    root.maxsize(1200, 925)
    #edit the title, size, and maximum size of the main window
    root.configure(background = "#1a1a4d")
    #set background color of window
    
    mainNotebook = ttk.Notebook(root)
    mainNotebook.pack(padx = 20, pady = 20, fill = "both")
    #create and pack Notebook object with ui tabs to the main window
    backgoundStyle = ttk.Style()
    backgoundStyle.configure("white.TFrame", background = "white")
    #style for Frame objects to follow
    systemFrame = ttk.Frame(root, style = "white.TFrame", width = 1160, height = 885)
    scheduleFrame = ttk.Frame(root, style = "white.TFrame", width = 1160, height = 885)
    mainNotebook.add(systemFrame, text = "System Information")  
    mainNotebook.add(scheduleFrame, text = "Schedule")
    #create the main tabs for the ui and add them to the Notebook

    
    mainScreen = CTC_Main_Screen.MainScreen(root, 0, systemFrame, mainNotebook)
    scheduleScreen = CTC_Schedule_Screen.ScheduleScreen(root, mainScreen, scheduleFrame, mainNotebook)
    mainScreen.schedule_screen = scheduleScreen
    testUI = CTC_Test_UI.TestUI(win)
    #create the ui objects
    
    programLoop(root, mainScreen, testUI) 
    #run the loop the continuously checks the data file
        
    root.mainloop()
    clock.clock.endTimer()
    #end program by ending mainloop() and ending the clock timer


def programLoop(root: tk.Tk, mainScreen: CTC_Main_Screen, testUI: CTC_Test_UI):
    #continuously poll the data files to check for data changes

    if (os.stat("CTC_Office/CTC_data.txt").st_size != 0):
        mainScreen.updateMainScreen()
    if (os.stat("CTC_Office/to_test_ui.txt").st_size != 0):
        testUI.updateTestUI()
    #check if files have data, then run appropriate methods to update the ui appearance

    root.after(500, programLoop, root, mainScreen, testUI)
    #call function every 0.5 seconds


main()
#main function call