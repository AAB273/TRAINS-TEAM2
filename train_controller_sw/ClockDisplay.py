import tkinter as tk
from tkinter import ttk
import math
import time

class ClockDisplay(tk.Label):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, font=("Arial", 18), bg="black", fg="lime", *args, **kwargs)
        self.update_time()  # Start updating

    def update_time(self):
        # Get current local time and date
        current_time = time.strftime("%H:%M:%S")   # 24-hour time
        current_date = time.strftime("%Y-%m-%d")   # YYYY-MM-DD

        # Update the label text
        self.config(text=f"{current_date}\n{current_time}")

        # Call this function again after 1000 ms (1 second)
        self.after(1000, self.update_time)