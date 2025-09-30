import tkinter as tk
import time
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import font

# Key Inputs
Velocity = 20
Acceleration = 14
Passenger_Count = 0
Crew_Count = 0
######################
root = tk.Tk()
root.title("Passenger Train Model GUI")
root.configure(bg='#1a1a4d')
root.geometry("1270x950")
###########################################



# Switch View (top)
switch_view = tk.Frame(root, bg='#1a1a4d', width=1270, height=50)
switch_view.pack(padx=5, pady=3, fill='x')
switch_view.pack_propagate(False)

passenger_tab = tk.Button(switch_view, text="Passenger View", 
                         bg='#87ceeb', fg='black', font=('Arial', 10),
                         relief='raised', bd=1, padx=15, pady=3, height=50)
passenger_tab.pack(side='left')

test_tab = tk.Button(switch_view, text="Test View", 
                    bg='white', fg='black', font=('Arial', 10),
                    relief='raised', bd=1, padx=15, pady=3, height=50)
test_tab.pack(side='left')

#Train Selector
selector_frame = tk.Frame(root, bg='#4d4d6d', highlightbackground="black", highlightthickness=4, width=200)
selector_frame.pack(side='right', fill='y', padx=3, pady=3)
selector_frame.pack_propagate(False)
tk.Label(
    selector_frame,
    text="Train #  |  Deployed?",
    bg='#4d4d6d',
    fg='white',
    width=200,
    height=1,
    anchor='n'
).pack(pady=5,padx=5)

# Top Container for time and announcement frames
top_container = tk.Frame(root, bg='#4d4d6d', highlightbackground="black", highlightthickness=4)
top_container.pack(fill='x')  # Only fill horizontally, not vertically

# Time Frame (left side of middle container)
time_frame = tk.Frame(top_container, bg='#4d4d6d', width=270, height=80, highlightbackground="black", highlightthickness=4)
time_frame.pack(side='left', padx=3, pady=3)
time_frame.pack_propagate(False)
tk.Label(
    time_frame,
    text="Time",
    bg='#4d4d6d',
    fg='white'
).pack(padx=5, pady=5)

# Announcement Frame (right side of middle container)
Announcement_frame = tk.Frame(top_container, bg='#4d4d6d', width=950, height=80, highlightbackground="black", highlightthickness=4)
Announcement_frame.pack(side='left', padx=3, pady=3)
Announcement_frame.pack_propagate(False)
tk.Label(
    Announcement_frame,
    text="Arriving to Dormount in 5 seconds",
    bg='#4d4d6d',
    fg='white'
).pack(padx=5, pady=5)
########################################################


####################################


# Train Metrics (bottom - takes remaining space)
train_metrics_frame = tk.Frame(root, width=580, height=700, bg='#1a1a4d',highlightbackground="black", highlightthickness=4)
train_metrics_frame.pack(side='top',padx=3, pady=3)
train_metrics_frame.pack_propagate(False)
tk.Label(
    train_metrics_frame,
    text="Train Metrics",
    bg='#4d4d6d',
    fg='white',
    highlightbackground='black',
    highlightthickness=4,
    width=40,
    height=1,
    anchor='n',
).pack(padx=5, pady=5)

#Right side of Train Metrics
live_metrics = tk.Frame(train_metrics_frame, width=400, highlightbackground="black", highlightthickness=4,bg='#4d4d6d')
live_metrics.pack(side='right',padx=3,pady=3,fill='y')
live_metrics.pack_propagate(False)
tk.Label(
    live_metrics,
    text="Live Metrics",
    bg='#4d4d6d',
    fg='white',
    width=120,
    height=1,
    anchor='n'
).pack(pady=5,padx=5)
#############################################################################

# Left Side of Train Metrics (Cabin Temp, Train Dimensions, Power Command)
cabin_temp_frame = tk.Frame(train_metrics_frame, width=140,height=230,highlightbackground="black", highlightthickness=4,bg='#4d4d6d')
cabin_temp_frame.pack(side='top',padx=3,pady=3)
cabin_temp_frame.pack_propagate(False)
tk.Label(
    cabin_temp_frame,
    text="Cabin Temp",
    bg='#4d4d6d',
    fg='white',
    width=120,
    height=25,
    anchor='n'
).pack(padx=5, pady=5)
temp_circle= tk.Canvas(train_metrics_frame,width=50,height=50,bg='#4d4d6d')

Train_Dimensions_Frame = tk.Frame(train_metrics_frame, width=140,height=230,highlightbackground="black", highlightthickness=4,bg='#4d4d6d')
Train_Dimensions_Frame.pack(side='top',padx=3,pady=3)
Train_Dimensions_Frame.pack_propagate(False)
tk.Label(
    Train_Dimensions_Frame,
    text="Train Dimensions",
    bg='#4d4d6d',
    fg='white',
    width=120,
    height=30,
    anchor='n'
).pack(padx=5, pady=5)

Train_Power_Command = tk.Frame(train_metrics_frame, width=140,height=225,highlightbackground="black", highlightthickness=4,bg='#4d4d6d')
Train_Power_Command.pack(side='top',padx=3,pady=3)
Train_Power_Command.pack_propagate(False)
tk.Label(
    Train_Power_Command,
    text="Power Command",
    bg='#4d4d6d',
    fg='white',
    width=120,
    height=1,
    anchor='n'
).pack(padx=5, pady=5)



#Emergency Brake
emergency_brake = tk.Frame(root,width=580,height=100, highlightbackground="black",highlightthickness=2,bg='#4d4d6d')
emergency_brake.pack(side='top',padx=3,pady=3)
emergency_brake.pack_propagate(False)
emergency_brake_button = tk.Button(
    emergency_brake,
    text="Emergency Brake", 
    bg="red", 
    fg='black', 
    font=('Arial', 10),  
    relief='raised', 
    bd=1, 
    padx=15, 
    pady=3, 
    height=50
)
emergency_brake_button.pack(fill='both')



root.mainloop()