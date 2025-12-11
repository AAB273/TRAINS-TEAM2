import CTC_Main_Screen
import CTC_Schedule_Screen
import tkinter as tk
from tkinter import ttk


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


### FOR TESTING PURPOSES ONLY ###


mainScreen = CTC_Main_Screen.MainScreen(root, 0, systemFrame, mainNotebook)
scheduleScreen = CTC_Schedule_Screen.ScheduleScreen(root, mainScreen, scheduleFrame, mainNotebook)
mainScreen.schedule_screen = scheduleScreen


def testSuggestedAuthority():

    suggAuth = scheduleScreen.calculateAuthority([63, "green", "forward"], "Castle Shannon")
    print(f"Suggested Authority: {suggAuth[0] - 1}\n")

def testSuggestedAuthoritytoYard():

    suggAuth = scheduleScreen.calculateAuthority([96, "green", "forward"], "end")
    print(f"Suggested Authority: {suggAuth[0] - 1}\n")

def testDistance():

    suggAuth = scheduleScreen.calculateAuthority([63, "green", "forward"], "Castle Shannon")
    print(f"Suggested Authority: {suggAuth[1]}\n")

def testDistanceToYard():

    suggAuth = scheduleScreen.calculateAuthority([96, "green", "forward"], "end")
    print(f"Suggested Authority: {suggAuth[1]}\n")

def testClockInc():
    print(f"{mainScreen.controlClockSpeed("inc")}\n")

def testClockDec():
    print(f"{mainScreen.controlClockSpeed("dec")}\n")

def testLightStates():
    print(f"{mainScreen.updateMainScreen("LS", ["1", "01", "green"])}\n")

def testRRStates():
    print(f"{mainScreen.updateMainScreen("RC", ["1", "1", "green"])}\n")

def testTrackError():
    print(f"{scheduleScreen.updateManualEdit("1", None, None, "red")}\n")

def testTrackErrorTwo():
    print(f"{scheduleScreen.updateManualEdit("1", None, None, "green")}")

testSuggestedAuthority()
testSuggestedAuthoritytoYard()
testDistance()
testDistanceToYard()
testClockInc()
testClockDec()
testLightStates()
testRRStates()
testTrackError()
testTrackErrorTwo()

root.mainloop()