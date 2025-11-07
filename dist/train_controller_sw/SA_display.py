import tkinter as tk
from tkinter import ttk
import math
import time
from ClockDisplay import ClockDisplay

class StationAnnouncementDisplay(tk.Frame):
    def __init__(self, parent, callback=None, expand_callback=None):
        super().__init__(parent, bg="grey", relief=tk.RAISED, bd=2)
        self.callback = callback
        self.expand_callback = expand_callback
        self.is_expanded = False
        
        main_frame = tk.Frame(self, bg="grey", padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with expand button
        header_frame = tk.Frame(main_frame, bg="lightgrey", relief=tk.RAISED)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        expand_btn = tk.Button(header_frame, text="➤", font=("Arial", 14, "bold"),
                              command=self.toggle_expand, bg="lightgrey", relief=tk.FLAT,
                              cursor="hand2")
        expand_btn.pack(side=tk.LEFT, padx=5)
        
        title_label = tk.Label(header_frame, text="Station Announcement Display", 
                              font=("Arial", 14, "bold"), bg="lightgrey", padx=10, pady=5)
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        line_frame = tk.Frame(main_frame, bg="grey")
        line_frame.pack(pady=10)
        
        tk.Label(line_frame, text="Select Line:", font=("Arial", 12), bg="grey").pack(side=tk.LEFT, padx=5)
        
        self.line_var = tk.StringVar(value="Red Line")
        line_combo = ttk.Combobox(line_frame, textvariable=self.line_var, 
                                 values=["Red Line", "Blue Line", "Green Line", "Emergency Announcement"], 
                                 state="readonly", width=15)
        line_combo.pack(side=tk.LEFT, padx=5)
        line_combo.bind("<<ComboboxSelected>>", self.on_line_change)
        
        station_frame = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=2)
        station_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(station_frame, text="Select Station:", font=("Arial", 11, "bold"), 
                bg="white").pack(pady=5)
        
        scrollbar = tk.Scrollbar(station_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.station_listbox = tk.Listbox(station_frame, yscrollcommand=scrollbar.set, 
                                         font=("Arial", 10), height=10)
        self.station_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.station_listbox.yview)
        
        self.stations = {
            "Red Line": ["Shadyside", "Herron Ave", "Swissville", "Penn Station", 
                        "Steel Plaza", "First Ave", "Station Square", "South Hills Jct"],
            "Blue Line": ["Station A", "Station B"],
            "Green Line": ["Pioneer", "Edgebrook", "Whited", "South Bank", "Central", 
                          "Inglewood", "Overbrook", "Glenbury", "Dormont", "Mt Lebanon"]
        }
        
        self.populate_stations()
        
        button_frame = tk.Frame(main_frame, bg="grey")
        button_frame.pack(pady=10)
        
        announce_btn = tk.Button(button_frame, text="ANNOUNCE", font=("Arial", 12, "bold"), 
                                bg="darkgreen", fg="white", padx=20, pady=8, 
                                command=self.announce_station)
        announce_btn.pack()
        
        datetime_frame = tk.Frame(main_frame, bg="lightblue")
        datetime_frame.pack(pady=5)

        #current date and time: 
        self.clock = ClockDisplay(datetime_frame)
        self.clock.pack(padx=10, pady=10)
    
    def toggle_expand(self):
        if self.expand_callback:
            self.expand_callback()
    
    def populate_stations(self):
        self.station_listbox.delete(0, tk.END)
        line = self.line_var.get()
        for station in self.stations.get(line, []):
            self.station_listbox.insert(tk.END, station)
    
    def on_line_change(self, event):
        line = self.line_var.get()
        self.station_listbox.delete(0, tk.END)
        
        # Hide any previous emergency widgets
        if hasattr(self, "emergency_text"):
            self.emergency_text.pack_forget()
            self.emergency_label.pack_forget()

        if line == "Emergency Announcement":
            # Show emergency input box
        
    # Create a subframe so it can expand properly
            self.emergency_frame = tk.Frame(self, bg="grey")
            self.emergency_frame.pack(fill="both", expand=True, pady=5)

            self.emergency_label = tk.Label(
                self.emergency_frame, 
                text="Enter Emergency Message:",
                font=("Arial", 11, "bold"), 
                bg="grey", fg="white"
            )
            self.emergency_label.pack(pady=(5, 2))

            self.emergency_text = tk.Text(
                self.emergency_frame,
                height=3, width=40,
                font=("Arial", 10),
                bg="white",
                fg="black",
                insertbackground="black"   # ensures cursor visible
            )
            self.emergency_text.pack(pady=5)
        else:
            self.populate_stations()

    
    def announce_station(self):
        line = self.line_var.get()
        if line == "Emergency Announcement":
            message = self.emergency_text.get("1.0", tk.END).strip()
            if message:
                print(f"EMERGENCY ANNOUNCEMENT OUTPUT: '{message}'")
                if self.callback:
                    self.callback(line, message)
        else:
            selection = self.station_listbox.curselection()
            if selection:
                station = self.station_listbox.get(selection[0])
                print(f"ANNOUNCEMENT OUTPUT: Line='{line}', Station='{station}'")
                if self.callback:
                    self.callback(line, station)