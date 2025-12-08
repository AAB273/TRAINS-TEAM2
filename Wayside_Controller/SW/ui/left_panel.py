import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.plc_dialog import PLCDialog  # Import from separate file
import os

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
        """Refresh all UI elements when data changes externally"""
        self.refresh_current_display()
                
        # ALSO refresh dropdowns when PLC filter changes
        # This ensures switches/lights dropdowns show filtered items
        self.update_crossing_options()
        self.update_switch_options()
        self.update_light_options()

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

        # Initialize PLC instance
        from ui.plc_engine import PLCProgram
        self.plc_instance = PLCProgram(self.data, self.log_callback)
        self.plc_running = False
        
        # AUTO-LOAD DEFAULT PLC FILE
        default_path = "Wayside_Controller/SW/auto_plc_logic.py"
        if os.path.exists(default_path):
            self.selected_plc_file = default_path
            self.plc_instance.plc_file = default_path
            print(f"Auto-loaded PLC from: {default_path}")
        else:
            self.selected_plc_file = None
        
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

        #check if in maintenance mode
        if not self.data.maintenance_mode:
            messagebox.showwarning("Maintenance Mode Required", 
                                "PLC operations can only be performed in Maintenance Mode.")
            return
    
        from ui.plc_engine import PLCProgram
        if not hasattr(self, "plc_instance"):
            self.plc_instance = PLCProgram(self.data, self.log_callback)
            self.plc_running = False

        #  Make sure a PLC file was uploaded
        if not hasattr(self, "selected_plc_file") or not self.selected_plc_file:
            messagebox.showwarning("PLC File Missing", "Please upload a PLC program first.")
            return

        # Pass uploaded PLC path to the PLC engine
        self.plc_instance.plc_file = self.selected_plc_file

        if not self.plc_running:
            # Starting PLC
            self.plc_instance.start()
            self.plc_status.config(text="Running", bg="#FFD700", fg="darkorange")
            self.plc_running = True

        else:
            # Stopping PLC - disable filter
            self.plc_instance.stop()
            
            # Disable PLC filter in data model
            if hasattr(self.data, 'plc_filter_active'):
                self.data.disable_plc_filter()
            
            self.plc_status.config(text="Stopped", bg="#FF9999", fg="darkred")
            self.plc_running = False

    # ------------------------------
    # RAILWAY CROSSINGS
    # ------------------------------
    def create_crossing_section(self, parent):
        crossing_frame = tk.LabelFrame(parent, text="Railway Crossing Details", 
                                    bg='#cccccc', font=('Arial', 9, 'bold'))
        crossing_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(crossing_frame, text="Select Crossing:", bg='#cccccc').pack(pady=2)
        self.crossing_selector = ttk.Combobox(crossing_frame, width=18, state='readonly')
        self.crossing_selector.pack(pady=2)
        self.crossing_selector.bind('<<ComboboxSelected>>', self.update_crossing_display)
        
        tk.Label(crossing_frame, text="Condition:", bg='#cccccc').pack()
        self.crossing_condition = tk.Entry(crossing_frame, width=20, state='readonly')
        self.crossing_condition.pack(pady=2)
        
        tk.Label(crossing_frame, text="Status:", bg='#cccccc').pack()
        self.crossing_status = tk.StringVar()
        self.crossing_status_dropdown = ttk.Combobox(crossing_frame, 
                                                    textvariable=self.crossing_status,
                                                    width=18,  # REMOVE: state='readonly',
                                                    values=["Active", "Inactive"])
        self.crossing_status_dropdown.pack(pady=2)

        # Set button
        tk.Button(crossing_frame, text="Set", command=self.set_crossing, 
                bg='#4a7c8c', fg='white', width=10).pack(pady=5)

        # Initialize options
        self.update_crossing_options()

    def update_crossing_display(self, event=None):
        selected = self.crossing_selector.get()
        crossings = self.data.filtered_railway_crossings
        if selected in crossings:
            data = crossings[selected]
            self.crossing_condition.config(state='normal')
            self.crossing_condition.delete(0, tk.END)
            self.crossing_condition.insert(0, data["condition"])
            self.crossing_condition.config(state='readonly')
            
            # Determine status based on bar and lights
            bar = data.get("bar", "Open")
            lights = data.get("lights", "Off")
            
            # Set status based on current state
            if bar == "Closed" and lights == "On":
                self.crossing_status.set("Active")
            else:
                self.crossing_status.set("Inactive")

    def update_crossing_options(self):
        """Populate crossing dropdowns based on current line"""
        crossings = list(self.data.filtered_railway_crossings.keys())
        self.crossing_selector['values'] = crossings
        if crossings:
            self.crossing_selector.set(crossings[0])
            self.update_crossing_display()
        else:
            self.crossing_selector.set('')
            self.crossing_condition.config(state='normal')
            self.crossing_condition.delete(0, tk.END)
            self.crossing_condition.config(state='readonly')
            self.crossing_status.set(text="")


    def set_crossing(self):
        """Set crossing status - automatically syncs bar and lights"""
        
        # Check if in maintenance mode
        if not self.data.maintenance_mode:
            messagebox.showwarning("Maintenance Mode Required", 
                                "Crossing controls can only be modified in Maintenance Mode.")
            return
        
        selected = self.crossing_selector.get()
        if selected:
            # Get selected status
            new_status = self.crossing_status.get()
            
            # Set bar and lights based on status
            if new_status == "Active":
                new_bar = "Closed"
                new_lights = "On"
            else:  # "Inactive"
                new_bar = "Open" 
                new_lights = "Off"
            
            # Update model with synchronized values
            self.data.update_track_data("railway_crossings", selected, "lights", new_lights)
            self.data.update_track_data("railway_crossings", selected, "bar", new_bar)
            self.data.update_track_data("railway_crossings", selected, "condition", 
                                    f"Lights: {new_lights}, Bar: {new_bar}")
            
            # Log the action
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} UPDATE: Crossing {selected} - Status: {new_status} (Bar: {new_bar}, Lights: {new_lights}) on {self.data.current_line} track")
        
    
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
        """Populate switch dropdowns based on current line WITHOUT resetting selection"""
        switches = list(self.data.filtered_switch_positions.keys())
        
        # Store current selection BEFORE updating
        current_selection = self.switch_selector.get()
        
        # Update the dropdown values
        self.switch_selector['values'] = switches
        
        # Restore previous selection if it still exists
        if current_selection in switches:
            self.switch_selector.set(current_selection)
            self.update_switch_display()
        elif switches:
            # Only set to first if no previous selection
            self.switch_selector.set(switches[0])
            self.update_switch_display()
        else:
            self.switch_selector.set('')
            self.switch_condition.config(state='normal')
            self.switch_condition.delete(0, tk.END)
            self.switch_condition.config(state='readonly')

    def update_switch_display(self, event=None):
        selected = self.switch_selector.get()
        switches = self.data.filtered_switch_positions
        if selected in switches:
            data = switches[selected]
            
            # Get current direction
            current_raw_dir = data.get("direction", "")
            
            # Update condition display
            self.switch_condition.config(state='normal')
            self.switch_condition.delete(0, tk.END)
            self.switch_condition.insert(0, data["condition"])
            self.switch_condition.config(state='readonly')

            # Get raw options (block numbers)
            raw_options = data.get("options", [])
            
            # Create display options with section information
            display_options = []
            self.current_switch_mapping = {}
            
            for option in raw_options:
                display_name = self.convert_to_section_display(option)
                display_options.append(display_name)
                self.current_switch_mapping[display_name] = option
            
            # Update UI with section-based display
            self.switch_direction['values'] = display_options
            
            # Set current selection
            current_display_dir = self.convert_to_section_display(current_raw_dir)
            self.switch_direction.set(current_display_dir)

    def convert_to_section_display(self, raw_direction):
        """Convert raw block direction to section-based display name"""
        if '-' in raw_direction:
            parts = raw_direction.split('-')
            if parts[0].isdigit() and parts[1].isdigit():
                # Both are block numbers (e.g., "12-13")
                from_block, to_block = parts
                from_section = self.data.get_section_for_block(self.data.current_line, int(from_block))
                to_section = self.data.get_section_for_block(self.data.current_line, int(to_block))
                return f"Section {from_section} → Section {to_section}"
            elif parts[0].isdigit():
                # From block to yard (e.g., "57-yard")
                from_block = parts[0]
                from_section = self.data.get_section_for_block(self.data.current_line, int(from_block))
                return f"Section {from_section} → Yard"
            else:
                # From yard to block (e.g., "yard-63")
                to_block = parts[1]
                to_section = self.data.get_section_for_block(self.data.current_line, int(to_block))
                return f"Yard → Section {to_section}"
        else:
            # Handle "TO YARD", "FROM YARD" etc.
            return raw_direction.replace("_", " ").title()

    def set_switch(self):
        """Set switch direction and update model - log raw block numbers"""
        if not self.data.maintenance_mode:
            messagebox.showwarning("Maintenance Mode Required", 
                                "Switch controls can only be modified in Maintenance Mode.")
            return
            
        selected = self.switch_selector.get()
        if selected:
            display_direction = self.switch_direction.get()
            raw_direction = self.current_switch_mapping.get(display_direction, display_direction)
            
            # Update model
            self.data.update_track_data("switch_positions", selected, "direction", raw_direction)
            self.data.update_track_data("switch_positions", selected, "condition", f"Set to {display_direction}")
            self.update_switch_display()

            # Get original switch name for logging
            if hasattr(self, 'selector_mapping') and selected in self.selector_mapping:
                original_switch = self.selector_mapping[selected]
            else:
                original_switch = selected
            
            # Send to track model
            block = original_switch.split(" ")[1] if " " in original_switch else original_switch
            if hasattr(self.data, 'app') and self.data.app:
                self.data.app.send_switch_to_track_model(self.data.current_line, block, raw_direction)
            
            # SIMPLE TERMINAL OUTPUT - just the raw values
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} UPDATE: Switch {original_switch} set to {raw_direction}")
            
            print(f"Switch {original_switch} set to {raw_direction}")
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
        lights = list(self.data.filtered_light_states.keys())  # Changed from filtered_track_data
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
        lights = self.data.filtered_light_states  # Changed from filtered_track_data
        if selected in lights:
            data = lights[selected]
            self.light_condition.config(state='normal')
            self.light_condition.delete(0, tk.END)
            self.light_condition.insert(0, data["condition"])
            self.light_condition.config(state='readonly')
            self.light_signal.set(data["signal"])

    def set_light(self):
        """Set light signal and update model"""
        # Check if in maintenance mode
        if not self.data.maintenance_mode:
            messagebox.showwarning("Maintenance Mode Required", 
                                "Light controls can only be modified in Maintenance Mode.")
            return
        
        selected = self.light_selector.get()
        if selected:
            new_signal = self.light_signal.get()
            self.data.update_track_data("light_states", selected, "signal", new_signal)  # Changed category
            self.data.update_track_data("light_states", selected, "condition", f"Signal: {new_signal}")  # Changed category
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
                
                # Update main UI data model - use new variable names
                self.update_track_data_cross_line("switch_positions", track, block, "direction", switch_direction)  # Changed category
                self.update_track_data_cross_line("switch_positions", track, block, "condition", f"Set to {switch_direction}")  # Changed category
                
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
                
                # Update main UI data model - use new variable names
                self.update_track_data_cross_line("railway_crossings", track, block, "lights", lights_setting)  # Changed category
                self.update_track_data_cross_line("railway_crossings", track, block, "bar", crossbar_setting)  # Changed category
                self.update_track_data_cross_line("railway_crossings", track, block, "condition", f"Lights: {lights_setting}, Bar: {crossbar_setting}")  # Changed category
                
                # FORCE LEFT PANEL REFRESH
                self.force_left_panel_refresh()
        else:
            print(f"Unknown crossing message format: {log_message}")

    def force_left_panel_refresh(self):
        """Force refresh of left panel displays"""
        self.refresh_current_display()