import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime
# Key Inputs
Speed = 20
Acceleration = 14
Passenger_Count = 0
Crew_Count = 0
######################
root = tk.Tk()
root.title("Passenger Train Model GUI")
root.configure(bg='#1a1a4d')
root.geometry("1000x650")

# Frames
train_metrics_frame = tk.Frame(root, width=300, height=100, bg='#4d4d6d')
train_metrics_frame.pack(pady=50, side=tk.LEFT)
train_metrics_frame.pack_propagate(False)
tk.Label(
    train_metrics_frame,
    text="Train Metrics",
    bg='#4d4d6d',
    fg = 'white',
    relief= 'solid',
    borderwidth= 2
).pack(padx=5, pady=5)


root.mainloop()

