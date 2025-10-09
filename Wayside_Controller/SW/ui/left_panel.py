import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.plc_dialog import PLCDialog  # Import from separate file

class LeftPanel(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d', width=250)
        self.pack_propagate(False)
        self.data = data
        self.log_callback = None  # Add direct callback
        
        self.create_widgets()

        # Connect line change callback
        self.data.on_line_change.append(self.on_line_changed)
        self.data.on_data_update.append(self.refresh_ui)
    
    def set_log_callback(self, callback):
        """Set the callback function for logging - JUST LIKE YOUR TEST PANEL"""
        self.log_callback = callback

    def refresh_ui(self):
        self.refresh_current_display()


    def create_widgets(self):
        # Create a frame for the main content that can scroll if needed
        main_frame = tk.Frame(self, bg='#1a1a4d')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Railway Crossing Section
        self.create_crossing_section(main_frame)
        
        # Switch Section
        self.create_switch_section(main_frame)
        
        # Light Section
        self.create_light_section(main_frame)
        
        # PLC Control Section at the bottom
        self.create_plc_section(main_frame)

    def create_plc_section(self, parent):
        """Create PLC control section at the bottom of the left panel"""
        plc_frame = tk.LabelFrame(parent, text="PLC Controls", 
                                 bg='#cccccc', font=('Arial', 9, 'bold'))
        plc_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Initialize PLC dialog
        self.plc_dialog = PLCDialog(self)
        
        # PLC Upload button
        upload_btn = tk.Button(plc_frame, text="Upload PLC Program", 
                              bg='#4a7c8c', fg='white', font=('Arial', 10, 'bold'),
                              command=self.plc_dialog.show, width=20, height=2)
        upload_btn.pack(pady=8, padx=10)
        
        # Run PLC button
        run_btn = tk.Button(plc_frame, text="Run PLC", 
                           bg='#2e8b57', fg='white', font=('Arial', 10, 'bold'),
                           command=self.run_plc, width=20, height=2)
        run_btn.pack(pady=8, padx=10)
        
        # Status indicator
        status_frame = tk.Frame(plc_frame, bg='#cccccc')
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="Status:", bg='#cccccc', 
                font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.plc_status = tk.Label(status_frame, text="Ready", bg='#90EE90', 
                                  fg='darkgreen', font=('Arial', 9, 'bold'),
                                  width=8, relief=tk.SUNKEN)
        self.plc_status.pack(side=tk.RIGHT, padx=5)

    def run_plc(self):
        """Start or stop the uploaded PLC program"""
        from ui.plc_engine import PLCProgram
        if not hasattr(self, "plc_instance"):
            self.plc_instance = PLCProgram(self.data, self.log_callback)
            self.plc_running = False

        # ✅ Make sure a PLC file was uploaded
        if not hasattr(self, "selected_plc_file") or not self.selected_plc_file:
            messagebox.showwarning("PLC File Missing", "Please upload a PLC program first.")
            return

        # Pass uploaded PLC path to the PLC engine
        self.plc_instance.plc_file = self.selected_plc_file

        if not self.plc_running:
            self.plc_instance.start()
            self.plc_status.config(text="Running", bg="#FFD700", fg="darkorange")
            self.plc_running = True
        else:
            self.plc_instance.stop()
            self.plc_status.config(text="Stopped", bg="#FF9999", fg="darkred")
            self.plc_running = False

    # ------------------------------
    # RAILWAY CROSSINGS
    # ------------------------------
    def create_crossing_section(self, parent):
        crossing_frame = tk.LabelFrame(parent, text="Railway Crossing Detail", 
                                      bg='#cccccc', font=('Arial', 9, 'bold'))
        crossing_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(crossing_frame, text="Select Crossing:", bg='#cccccc').pack(pady=2)
        self.crossing_selector = ttk.Combobox(crossing_frame, width=18, state='readonly')
        self.crossing_selector.pack(pady=2)
        self.crossing_selector.bind('<<ComboboxSelected>>', self.update_crossing_display)
        
        tk.Label(crossing_frame, text="Condition:", bg='#cccccc').pack()
        self.crossing_condition = tk.Entry(crossing_frame, width=20, state='readonly')
        self.crossing_condition.pack(pady=2)
        
        tk.Label(crossing_frame, text="Lights:", bg='#cccccc').pack()
        self.crossing_lights = ttk.Combobox(crossing_frame, width=18, 
                                           values=["On", "Off"])
        self.crossing_lights.pack(pady=2)
        
        tk.Label(crossing_frame, text="Bar:", bg='#cccccc').pack()
        self.crossing_bar = ttk.Combobox(crossing_frame, width=18, values=["Closed", "Open"])
        self.crossing_bar.pack(pady=2)

        # Set button
        tk.Button(crossing_frame, text="Set", command=self.set_crossing, 
                 bg='#4a7c8c', fg='white', width=10).pack(pady=5)

        # Initialize options
        self.update_crossing_options()

    def update_crossing_options(self):
        """Populate crossing dropdowns based on current line"""
        crossings = list(self.data.filtered_track_data.get("crossings", {}).keys())
        self.crossing_selector['values'] = crossings
        if crossings:
            self.crossing_selector.set(crossings[0])
            self.update_crossing_display()
        else:
            self.crossing_selector.set('')
            self.crossing_condition.config(state='normal')
            self.crossing_condition.delete(0, tk.END)
            self.crossing_condition.config(state='readonly')

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

    def set_crossing(self):
        """Set crossing lights/bar and update model"""
        selected = self.crossing_selector.get()
        if selected:
            new_light = self.crossing_lights.get()
            new_bar = self.crossing_bar.get()
            # Update model
            self.data.update_track_data("crossings", selected, "lights", new_light)
            self.data.update_track_data("crossings", selected, "bar", new_bar)
            self.data.update_track_data("crossings", selected, "condition", f"Lights: {new_light}, Bar: {new_bar}")
            self.update_crossing_display()

            # Log the action - use the direct callback - JUST LIKE YOUR TEST PANEL
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} UPDATE: Crossing {selected} set - Lights: {new_light}, Bar: {new_bar} on {self.data.current_line} track")
    # ------------------------------
    # SWITCHES
    # ------------------------------
    def create_switch_section(self, parent):
        switch_frame = tk.LabelFrame(parent, text="Switch Details", 
                                    bg='#cccccc', font=('Arial', 9, 'bold'))
        switch_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(switch_frame, text="Select Switch:", bg='#cccccc').pack(pady=2)
        self.switch_selector = ttk.Combobox(switch_frame, width=18, state='readonly')
        self.switch_selector.pack(pady=2)
        self.switch_selector.bind('<<ComboboxSelected>>', self.update_switch_display)
        
        tk.Label(switch_frame, text="Condition:", bg='#cccccc').pack()
        self.switch_condition = tk.Entry(switch_frame, width=20, state='readonly')
        self.switch_condition.pack(pady=2)
        
        tk.Label(switch_frame, text="Direction:", bg='#cccccc').pack()
        self.switch_direction = ttk.Combobox(switch_frame, width=18)
        self.switch_direction.pack(pady=2)

        # Set button
        tk.Button(switch_frame, text="Set", command=self.set_switch,
                 bg='#4a7c8c', fg='white', width=10).pack(pady=5)

        self.update_switch_options()

    def update_switch_options(self):
        """Populate switch dropdowns based on current line"""
        switches = list(self.data.filtered_track_data.get("switches", {}).keys())
        self.switch_selector['values'] = switches
        if switches:
            self.switch_selector.set(switches[0])
            self.update_switch_display()
        else:
            self.switch_selector.set('')
            self.switch_condition.config(state='normal')
            self.switch_condition.delete(0, tk.END)
            self.switch_condition.config(state='readonly')

    def update_switch_display(self, event=None):
        selected = self.switch_selector.get()
        switches = self.data.filtered_track_data.get("switches", {})
        if selected in switches:
            data = switches[selected]
            self.switch_condition.config(state='normal')
            self.switch_condition.delete(0, tk.END)
            self.switch_condition.insert(0, data["condition"])
            self.switch_condition.config(state='readonly')

            # Use only the true options from the model
            options = data.get("options", [])
            self.switch_direction['values'] = options
            current_dir = data.get("direction", options[0] if options else "")
            self.switch_direction.set(current_dir)

    def set_switch(self):
        """Set switch direction and update model"""
        selected = self.switch_selector.get()
        if selected:
            new_direction = self.switch_direction.get()
            self.data.update_track_data("switches", selected, "direction", new_direction)
            self.data.update_track_data("switches", selected, "condition", f"Set to {new_direction}")
            self.update_switch_display()

            # Log the action - use the direct callback - JUST LIKE YOUR TEST PANEL
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} UPDATE: Switch {selected} set to {new_direction} on {self.data.current_line} track")

    # ------------------------------
    # LIGHTS
    # ------------------------------
    def create_light_section(self, parent):
        light_frame = tk.LabelFrame(parent, text="Light Detail", 
                                   bg='#cccccc', font=('Arial', 9, 'bold'))
        light_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(light_frame, text="Select Light:", bg='#cccccc').pack(pady=2)
        self.light_selector = ttk.Combobox(light_frame, width=18, state='readonly')
        self.light_selector.pack(pady=2)
        self.light_selector.bind('<<ComboboxSelected>>', self.update_light_display)
        
        tk.Label(light_frame, text="Condition:", bg='#cccccc').pack()
        self.light_condition = tk.Entry(light_frame, width=20, state='readonly')
        self.light_condition.pack(pady=2)
        
        tk.Label(light_frame, text="Signal:", bg='#cccccc').pack()
        self.light_signal = ttk.Combobox(light_frame, width=18, 
                                        values=[ "Super Green", "Green", "Red", "Yellow", "Off"])
        self.light_signal.pack(pady=2)

        # Set button
        tk.Button(light_frame, text="Set", command=self.set_light,
                 bg='#4a7c8c', fg='white', width=10).pack(pady=5)

        self.update_light_options()

    def update_light_options(self):
        """Populate light dropdowns based on current line"""
        lights = list(self.data.filtered_track_data.get("lights", {}).keys())
        self.light_selector['values'] = lights
        if lights:
            self.light_selector.set(lights[0])
            self.update_light_display()
        else:
            self.light_selector.set('')
            self.light_condition.config(state='normal')
            self.light_condition.delete(0, tk.END)
            self.light_condition.config(state='readonly')

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

    def set_light(self):
        """Set light signal and update model"""
        selected = self.light_selector.get()
        if selected:
            new_signal = self.light_signal.get()
            self.data.update_track_data("lights", selected, "signal", new_signal)
            self.data.update_track_data("lights", selected, "condition", f"Signal: {new_signal}")
            self.update_light_display()
            
            # Log the action - use the direct callback - JUST LIKE YOUR TEST PANEL
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} UPDATE: Light {selected} set to {new_signal} on {self.data.current_line} track")

    # ------------------------------
    # GENERAL
    # ------------------------------
    def on_line_changed(self):
        """Update all sections when line changes"""
        self.update_crossing_options()
        self.update_switch_options()
        self.update_light_options()

    def update_mode_ui(self):
        """Refresh UI based on maintenance/test mode"""
        pass

    # ------------------------------
    # FOR COMMUNICATION
    # ------------------------------
    def refresh_current_display(self):
        """Refresh the display for currently selected items in all sections"""
        # Refresh crossing display if something is selected
        if self.crossing_selector.get():
            self.update_crossing_display()
        
        # Refresh switch display if something is selected  
        if self.switch_selector.get():
            self.update_switch_display()
            
        # Refresh light display if something is selected
        if self.light_selector.get():
            self.update_light_display()

    def update_main_switches(self, log_message):
        """Update main UI switches based on test UI actions"""
        if "Set to" in log_message:
            parts = log_message.split("SWITCH: Set to ")
            if len(parts) > 1:
                switch_info = parts[1].split(" on ")
                switch_direction = switch_info[0]
                track_block = switch_info[1].split(" track, Block ")
                track = track_block[0]
                block = track_block[1].strip()
                
                print(f"Switch update: {track} Block {block} -> {switch_direction}")
                
                # Update main UI data model
                self.update_track_data_cross_line("switches", track, block, "direction", switch_direction)
                self.update_track_data_cross_line("switches", track, block, "condition", f"Set to {switch_direction}")
                
                # FORCE LEFT PANEL REFRESH
                self.force_left_panel_refresh()
        else:
            print(f"Unknown switch message format: {log_message}")

    def update_main_crossings(self, log_message):
        """Update main UI crossings based on test UI actions"""
        if "Set -" in log_message:
            parts = log_message.split("CROSSING: Set - ")
            if len(parts) > 1:
                crossing_info = parts[1].split(" on ")
                settings = crossing_info[0]
                track_block = crossing_info[1].split(" track, Block ")
                track = track_block[0]
                block = track_block[1].strip()
                
                # Parse settings
                if "Lights:" in settings and "Crossbar:" in settings:
                    lights_setting = settings.split("Lights: ")[1].split(", Crossbar: ")[0]
                    crossbar_setting = settings.split("Crossbar: ")[1]
                elif "Lights:" in settings and "Bar:" in settings:
                    lights_setting = settings.split("Lights: ")[1].split(", Bar: ")[0]
                    crossbar_setting = settings.split("Bar: ")[1]
                else:
                    print(f"Unknown crossing settings format: {settings}")
                    return
                
                print(f"Crossing update: {track} Block {block} -> Lights:{lights_setting}, Bar:{crossbar_setting}")
                
                # Update main UI data model
                self.update_track_data_cross_line("crossings", track, block, "lights", lights_setting)
                self.update_track_data_cross_line("crossings", track, block, "bar", crossbar_setting)
                self.update_track_data_cross_line("crossings", track, block, "condition", f"Lights: {lights_setting}, Bar: {crossbar_setting}")
                
                # FORCE LEFT PANEL REFRESH
                self.force_left_panel_refresh()
        else:
            print(f"Unknown crossing message format: {log_message}")