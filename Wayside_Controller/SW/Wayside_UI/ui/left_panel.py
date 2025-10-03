import tkinter as tk
from tkinter import ttk

class LeftPanel(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d', width=250)
        self.pack_propagate(False)
        self.data = data
        self.create_widgets()

        # Connect line change callback
        self.data.on_line_change.append(self.on_line_changed)
    
    def create_widgets(self):
        #Tabs are now controlled by header
        
        # Railway Crossing Detail
        self.create_crossing_section()
        
        # Switch Details
        self.create_switch_section()
        
        # Light Detail
        self.create_light_section()
    
    def create_crossing_section(self):
        crossing_frame = tk.LabelFrame(self, text="Railway Crossing Detail", 
                                      bg='#cccccc', font=('Arial', 9, 'bold'))
        crossing_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(crossing_frame, text="Select Crossing:", bg='#cccccc').pack(pady=2)
        self.crossing_selector = ttk.Combobox(crossing_frame, width=18, state='readonly')
        self.crossing_selector.pack(pady=2)
        self.crossing_selector.bind('<<ComboboxSelected>>', self.update_crossing_display)
        
        tk.Label(crossing_frame, text="Condition:", bg='#cccccc').pack()
        self.crossing_condition = tk.Entry(crossing_frame, width=20, state='readonly')
        self.crossing_condition.pack()
        
        tk.Label(crossing_frame, text="Lights:", bg='#cccccc').pack()
        self.crossing_lights = ttk.Combobox(crossing_frame, width=18, 
                                           values=["Red", "Green", "Yellow", "Off"])
        self.crossing_lights.pack()
        self.crossing_lights.bind('<<ComboboxSelected>>', self.update_crossing_lights)
        
        tk.Label(crossing_frame, text="Bar:", bg='#cccccc').pack()
        self.crossing_bar = ttk.Combobox(crossing_frame, width=18, values=["Closed", "Open"])
        self.crossing_bar.pack()

        # Initialize with current line data
        self.update_crossing_options()

    def update_crossing_options(self):
        """Update combobox options based on current line"""
        crossings = list(self.data.filtered_track_data.get("crossings", {}).keys())
        self.crossing_selector['values'] = crossings
        if crossings:
            self.crossing_selector.set(crossings[0])
            self.update_crossing_display()
    
    def create_switch_section(self):
        switch_frame = tk.LabelFrame(self, text="Switch Details", 
                                    bg='#cccccc', font=('Arial', 9, 'bold'))
        switch_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(switch_frame, text="Select Switch:", bg='#cccccc').pack(pady=2)
        self.switch_selector = ttk.Combobox(switch_frame, width=18, state='readonly')
        self.switch_selector.pack(pady=2)
        self.switch_selector.bind('<<ComboboxSelected>>', self.update_switch_display)
        
        tk.Label(switch_frame, text="Condition:", bg='#cccccc').pack()
        self.switch_condition = tk.Entry(switch_frame, width=20, state='readonly')
        self.switch_condition.pack()
        
        tk.Label(switch_frame, text="Direction:", bg='#cccccc').pack()
        self.switch_direction = ttk.Combobox(switch_frame, width=18, 
                                            values=["57-58", "Normal", "Reverse"])
        self.switch_direction.pack()
        self.switch_direction.bind('<<ComboboxSelected>>', self.update_switch_direction)

        # Initialize with current line data
        self.update_switch_options()

    def update_switch_options(self):
        """Update combobox options based on current line"""
        switches = list(self.data.filtered_track_data.get("switches", {}).keys())
        self.switch_selector['values'] = switches
        if switches:
            self.switch_selector.set(switches[0])
            self.update_switch_display()
    
    def create_light_section(self):
        light_frame = tk.LabelFrame(self, text="Light Detail", 
                                   bg='#cccccc', font=('Arial', 9, 'bold'))
        light_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(light_frame, text="Select Light:", bg='#cccccc').pack(pady=2)
        self.light_selector = ttk.Combobox(light_frame, width=18, state='readonly')
        self.light_selector.pack(pady=2)
        self.light_selector.bind('<<ComboboxSelected>>', self.update_light_display)
        
        tk.Label(light_frame, text="Condition:", bg='#cccccc').pack()
        self.light_condition = tk.Entry(light_frame, width=20, state='readonly')
        self.light_condition.pack()
        
        tk.Label(light_frame, text="Signal:", bg='#cccccc').pack()
        self.light_signal = ttk.Combobox(light_frame, width=18, 
                                        values=["Red", "Green", "Yellow"])
        self.light_signal.pack()
        self.light_signal.bind('<<ComboboxSelected>>', self.update_light_signal)

        # Initialize with current line data
        self.update_light_options()
    
    def update_light_options(self):
        """Update combobox options based on current line"""
        lights = list(self.data.filtered_track_data.get("lights", {}).keys())
        self.light_selector['values'] = lights
        if lights:
            self.light_selector.set(lights[0])
            self.update_light_display()
            
    def on_line_changed(self):
        """Update all left panel components when line changes"""
        print(f"Left panel: Line changed to {self.data.current_line}")  # Debug
        self.update_crossing_options()
        self.update_switch_options()
        self.update_light_options()
    
    def update_crossing_display(self, event=None):
        selected = self.crossing_selector.get()
        crossings = self.data.filtered_track_data.get("crossings", {})
        if selected in crossings:
            data = crossings[selected]
            self.crossing_condition.config(state='normal')
            self.crossing_condition.delete(0, tk.END)
            self.crossing_condition.insert(0, data["condition"])
            self.crossing_condition.config(state='readonly')
            self.crossing_lights.set(data["lights"])
            self.crossing_bar.set(data["bar"])
    
    def update_crossing_lights(self, event=None):
        selected = self.crossing_selector.get()
        if selected in self.data.track_data["crossings"]:
            self.data.track_data["crossings"][selected]["lights"] = self.crossing_lights.get()
    
    def update_switch_display(self, event=None):
        selected = self.switch_selector.get()
        switches = self.data.filtered_track_data.get("switches", {})
        if selected in switches:
            data = switches[selected]
            self.switch_condition.config(state='normal')
            self.switch_condition.delete(0, tk.END)
            self.switch_condition.insert(0, data["condition"])
            self.switch_condition.config(state='readonly')
            self.switch_direction.set(data["direction"])
    
    def update_switch_direction(self, event=None):
        selected = self.switch_selector.get()
        if selected in self.data.track_data["switches"]:
            self.data.track_data["switches"][selected]["direction"] = self.switch_direction.get()
    
    def update_light_display(self, event=None):
        selected = self.light_selector.get()
        lights = self.data.filtered_track_data.get("lights", {})
        if selected in lights:
            data = lights[selected]
            self.light_condition.config(state='normal')
            self.light_condition.delete(0, tk.END)
            self.light_condition.insert(0, data["condition"])
            self.light_condition.config(state='readonly')
            self.light_signal.set(data["signal"])
    
    def update_light_signal(self, event=None):
        selected = self.light_selector.get()
        if selected in self.data.track_data["lights"]:
            self.data.track_data["lights"][selected]["signal"] = self.light_signal.get()
    
    def update_mode_ui(self):
        # Refresh UI based on maintenance mode
        pass