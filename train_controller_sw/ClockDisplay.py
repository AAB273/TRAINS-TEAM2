import tkinter as tk
from tkinter import ttk
import math
import time

class ClockDisplay(tk.Label):
    """
    Clock display that can be controlled externally via:
    - set_time(time_str): Set the displayed time from external source
    - set_speed_multiplier(mult): Control update speed (1x or 10x)
    
    Can operate in two modes:
    1. External mode (default): Display time set via set_time()
    2. Internal mode: Generate own time (legacy behavior)
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, font=("Arial", 18), bg="black", fg="lime", *args, **kwargs)
        
        # Configuration
        self.speed_multiplier = 1  # 1x or 10x speed
        self.use_external_time = True  # Use time from external source (TIME command)
        self.external_time_str = "00:00:00"
        self.external_date_str = "0000-00-00"
        
        # Start updating display
        self.update_display()

    def set_time(self, time_str):
        """
        Set the time to display from external source (TIME command)
        
        Args:
            time_str (str): Time string in format "HH:MM:SS" or "YYYY-MM-DD HH:MM:SS"
        """
        try:
            # Handle different time formats
            if ' ' in time_str:
                # Format: "YYYY-MM-DD HH:MM:SS"
                parts = time_str.split(' ')
                self.external_date_str = parts[0]
                self.external_time_str = parts[1]
            elif len(time_str) == 8 and time_str.count(':') == 2:
                # Format: "HH:MM:SS" (time only)
                self.external_time_str = time_str
                # Keep existing date
            else:
                # Unknown format, just use it as-is
                self.external_time_str = time_str
                
            self.use_external_time = True
        except Exception as e:
            print(f"[ClockDisplay] Error setting time: {e}")

    def set_speed_multiplier(self, multiplier):
        """
        Set the speed multiplier for the clock update rate
        
        Args:
            multiplier (int): Speed multiplier (1 or 10)
        """
        if multiplier in [1, 10]:
            self.speed_multiplier = multiplier
            print(f"[ClockDisplay] Speed multiplier set to {multiplier}x")
        else:
            print(f"[ClockDisplay] Invalid multiplier: {multiplier} (must be 1 or 10)")

    def use_internal_time(self):
        """Switch to using system time (legacy behavior)"""
        self.use_external_time = False
        print("[ClockDisplay] Switched to internal system time")

    def use_external_time_mode(self):
        """Switch to using externally set time (TIME command)"""
        self.use_external_time = True
        print("[ClockDisplay] Switched to external time mode")

    def update_display(self):
        """Update the clock display"""
        try:
            if self.use_external_time:
                # Use externally set time (from TIME command)
                display_text = f"{self.external_date_str}\n{self.external_time_str}"
            else:
                # Use system time (legacy behavior)
                current_time = time.strftime("%H:%M:%S")
                current_date = time.strftime("%Y-%m-%d")
                display_text = f"{current_date}\n{current_time}"
            
            # Update the label text
            self.config(text=display_text)
            
        except Exception as e:
            print(f"[ClockDisplay] Error updating display: {e}")
        
        # Schedule next update
        # Update interval is affected by speed multiplier
        # At 1x: update every 1000ms
        # At 10x: update every 100ms (10x faster visual updates)
        update_interval = int(1000 / self.speed_multiplier)
        self.after(update_interval, self.update_display)