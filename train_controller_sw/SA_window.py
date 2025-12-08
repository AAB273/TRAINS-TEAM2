import tkinter as tk
from tkinter import ttk
import math
import time
from SA_display import StationAnnouncementDisplay

class StationAnnouncementWindow(tk.Toplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.title("Station Announcement Display - Expanded View")
        self.geometry("600x800")
        self.callback = callback
        
        self.withdraw()
        
        self.station_display = StationAnnouncementDisplay(self, callback=callback)
        self.station_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
    
    def show_window(self):
        self.deiconify()
        self.lift()
    
    def hide_window(self):
        self.withdraw()
