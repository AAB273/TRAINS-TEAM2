import CTC_Main_Screen
import CTC_Schedule_Screen
import tkinter as tk
from tkinter import ttk

#test case 1
def testSuggestedAuthority():
    root = tk.Tk()
    #win = tk.Toplevel(root)
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

    suggAuth = scheduleScreen.calculateAuthority([88, "green", "forward"], "Mt. Lebanon")
    print(f"Suggested Authority: {suggAuth}")

    root.mainloop()

testSuggestedAuthority()