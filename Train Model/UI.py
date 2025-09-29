import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime
from PIL import Image, ImageTk

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




#Passenger View/ Test View
switch_view = tk.Frame(root, bg = '#1a1a4d', width = 1270, height = 75)
switch_view.pack(padx=5, pady=3, fill='x')
switch_view.pack_propagate(False)
passenger_tab = tk.Button(switch_view, text="Passenger View", 
                                 bg='#87ceeb', fg='black', font=('Arial', 10),
                                 relief='raised', bd=1, padx=15, pady=3)
passenger_tab.pack(side='left')

test_tab = tk.Button(switch_view, text="Test View", 
                            bg='white', fg='black', font=('Arial', 10),
                            relief='raised', bd=1, padx=15, pady=3)
test_tab.pack(side='left')
#Logo
logo = Image.open(r"/mnt/c/Users/wolfm/OneDrive - University of Pittsburgh/Desktop/Trains GIT Location/TRAINS-TEAM2/Train Model/blt logo.png")  
photo = ImageTk.PhotoImage(logo)
image_label = tk.Label(root, image=logo)
image_label.pack(pady=20)

##########################
#Time
time_frame = tk.Frame(root, bg='#4d4d6d', width=270, height = 80)  
time_frame.pack(side='left', padx=3, pady=3)  
time_frame.pack_propagate(False)
tk.Label(
    time_frame,
    text="Time",
    bg='#4d4d6d',  
    fg='white'      
).pack(padx=5, pady=5)  
###########################
# Train Metrics 
train_metrics_frame = tk.Frame(root, width=300, height=400, bg='#4d4d6d')
train_metrics_frame.pack(fill='x', pady=(0, 3))
train_metrics_frame.pack_propagate(False)
tk.Label(
    train_metrics_frame,
    text="Train Metrics",
    highlightbackground= 'white',
    highlightthickness= 2,
    borderwidth= 2
).pack(padx=5, pady=5)


root.mainloop()

