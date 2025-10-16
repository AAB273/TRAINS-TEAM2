import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SystemMonitoring:
    def __init__(self, parent, track_config):
        self.parent = parent
        self.track_config = track_config
        self.log_callback = None  # Direct callback for logging
        
        # Store current settings for status persistence
        self.lights_settings = {}  # Format: {(track, block): color}
        self.crossing_settings = {}  # Format: {(track, block): (lights_status, crossbar_status)}
        
        self.create_system_monitoring()

    def set_log_callback(self, callback):
        """Set the callback function for logging"""
        self.log_callback = callback

    def create_system_monitoring(self):
        # Lights Control Card
        lights_card = tk.Frame(self.parent, bg="white", relief='raised', bd=2, padx=12, pady=12)
        lights_card.pack(side='left', fill='both', expand=True, padx=3)
        
        tk.Label(lights_card, text="Lights Control", font=("Arial", 14, "bold"), 
                bg="white", fg="#2d2d86").pack(anchor='w', pady=(0, 12))
        
        # Lights inputs
        lights_input_frame = tk.Frame(lights_card, bg="white")
        lights_input_frame.pack(fill='x', pady=8)
        
        # Track row
        track_frame = tk.Frame(lights_input_frame, bg="white")
        track_frame.pack(fill='x', pady=4)
        tk.Label(track_frame, text="Track:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.lights_track_var = tk.StringVar(value="Green")
        self.lights_track_dropdown = ttk.Combobox(track_frame, textvariable=self.lights_track_var, 
                                                values=["Green", "Red", "Blue"], state="readonly", width=10)
        self.lights_track_dropdown.pack(side='left', padx=(8, 0))
        
        # Block row
        block_frame = tk.Frame(lights_input_frame, bg="white")
        block_frame.pack(fill='x', pady=4)
        tk.Label(block_frame, text="Block #:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.lights_block_var = tk.StringVar(value="")
        self.lights_block_dropdown = ttk.Combobox(block_frame, textvariable=self.lights_block_var, 
                                                state="readonly", width=10)
        self.lights_block_dropdown.pack(side='left', padx=(8, 0))
        
        # Light Color row
        color_frame = tk.Frame(lights_input_frame, bg="white")
        color_frame.pack(fill='x', pady=4)
        tk.Label(color_frame, text="Light Color:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.lights_color_var = tk.StringVar(value="Green")
        self.lights_color_dropdown = ttk.Combobox(color_frame, textvariable=self.lights_color_var, 
                                                values=["Red", "Yellow", "Green", "Super Green"], state="readonly", width=10)
        self.lights_color_dropdown.pack(side='left', padx=(8, 0))
        
        # Status row
        status_frame = tk.Frame(lights_input_frame, bg="white")
        status_frame.pack(fill='x', pady=8)
        tk.Label(status_frame, text="Status:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.lights_status_var = tk.StringVar(value="No lights set")
        lights_status_label = tk.Label(status_frame, textvariable=self.lights_status_var, 
                                     font=("Arial", 10), bg="white", fg="#2d2d86")
        lights_status_label.pack(side='left', padx=(8, 0))
        
        ttk.Button(lights_card, text="Set Lights", command=self.set_lights, width=12).pack(pady=8)
        
        # Bind events
        self.lights_track_dropdown.bind('<<ComboboxSelected>>', self.on_lights_track_change)
        self.lights_block_dropdown.bind('<<ComboboxSelected>>', self.on_lights_block_change)
        
        # Initialize
        self.on_lights_track_change()
        
        # Railway Crossing Card
        crossing_card = tk.Frame(self.parent, bg="white", relief='raised', bd=2, padx=12, pady=12)
        crossing_card.pack(side='left', fill='both', expand=True, padx=3)
        
        tk.Label(crossing_card, text="Railway Crossing", font=("Arial", 14, "bold"), 
                bg="white", fg="#2d2d86").pack(anchor='w', pady=(0, 12))
        
        # Crossing inputs
        crossing_input_frame = tk.Frame(crossing_card, bg="white")
        crossing_input_frame.pack(fill='x', pady=8)
        
        # Track row
        crossing_track_frame = tk.Frame(crossing_input_frame, bg="white")
        crossing_track_frame.pack(fill='x', pady=4)
        tk.Label(crossing_track_frame, text="Track:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.crossing_track_var = tk.StringVar(value="Green")
        self.crossing_track_dropdown = ttk.Combobox(crossing_track_frame, textvariable=self.crossing_track_var, 
                                                  values=["Green", "Red", "Blue"], state="readonly", width=10)
        self.crossing_track_dropdown.pack(side='left', padx=(8, 0))
        
        # Block row
        crossing_block_frame = tk.Frame(crossing_input_frame, bg="white")
        crossing_block_frame.pack(fill='x', pady=4)
        tk.Label(crossing_block_frame, text="Block #:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.crossing_block_var = tk.StringVar(value="")
        self.crossing_block_dropdown = ttk.Combobox(crossing_block_frame, textvariable=self.crossing_block_var, 
                                                  state="readonly", width=10)
        self.crossing_block_dropdown.pack(side='left', padx=(8, 0))
        
        # Crossing controls
        crossing_controls_frame = tk.Frame(crossing_card, bg="white")
        crossing_controls_frame.pack(fill='x', pady=12)
        
        # Lights control row
        lights_control_frame = tk.Frame(crossing_controls_frame, bg="white")
        lights_control_frame.pack(fill='x', pady=4)
        tk.Label(lights_control_frame, text="Lights:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.crossing_lights_var = tk.StringVar(value="Off")
        ttk.Combobox(lights_control_frame, textvariable=self.crossing_lights_var, 
                   values=["Off", "On"], state="readonly", width=6).pack(side='left', padx=(8, 0))
        
        # Crossbar control row
        crossbar_control_frame = tk.Frame(crossing_controls_frame, bg="white")
        crossbar_control_frame.pack(fill='x', pady=4)
        tk.Label(crossbar_control_frame, text="Crossbar:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.crossing_crossbar_var = tk.StringVar(value="Open")
        ttk.Combobox(crossbar_control_frame, textvariable=self.crossing_crossbar_var, 
                   values=["Open", "closed"], state="readonly", width=6).pack(side='left', padx=(8, 0))
        
        # Crossing status row
        crossing_status_frame = tk.Frame(crossing_controls_frame, bg="white")
        crossing_status_frame.pack(fill='x', pady=8)
        tk.Label(crossing_status_frame, text="Status:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.crossing_status_var = tk.StringVar(value="No crossing set")
        crossing_status_label = tk.Label(crossing_status_frame, textvariable=self.crossing_status_var, 
                                       font=("Arial", 10), bg="white", fg="#2d2d86")
        crossing_status_label.pack(side='left', padx=(8, 0))
        
        ttk.Button(crossing_card, text="Set Crossing", command=self.set_crossing, width=12).pack(pady=8)
        
        # Bind crossing track change event
        self.crossing_track_dropdown.bind('<<ComboboxSelected>>', self.on_crossing_track_change)
        self.crossing_block_dropdown.bind('<<ComboboxSelected>>', self.on_crossing_block_change)
        
        # Initialize crossing
        self.on_crossing_track_change()

    def get_light_blocks_for_track(self, track):
        """Get blocks that have lights for a specific track"""
        return self.track_config.get_blocks_with_lights(track)

    def get_crossing_blocks_for_track(self, track):
        """Get blocks that have railway crossings for a specific track"""
        return self.track_config.get_blocks_with_crossings(track)

    def on_lights_track_change(self, event=None):
        track = self.lights_track_var.get()
        # Get blocks that have lights for this track
        light_blocks = self.get_light_blocks_for_track(track)
        
        if light_blocks:
            self.lights_block_dropdown['values'] = light_blocks
            self.lights_block_var.set(light_blocks[0])
            self.on_lights_block_change()
        else:
            self.lights_block_dropdown['values'] = []
            self.lights_block_var.set("")
            self.lights_status_var.set("No lights available")

    def on_lights_block_change(self, event=None):
        track = self.lights_track_var.get()
        block = self.lights_block_var.get()
        
        if block:
            # Check if we have a saved setting for this track/block
            key = (track, block)
            if key in self.lights_settings:
                # Restore the saved color and status
                saved_color = self.lights_settings[key]
                self.lights_color_var.set(saved_color)
                self.lights_status_var.set(f"Lights: {saved_color}")
            else:
                # No saved setting, show ready status
                self.lights_status_var.set(f"Ready - Block {block}")
        else:
            self.lights_status_var.set("No lights set")

    def on_crossing_track_change(self, event=None):
        track = self.crossing_track_var.get()
        # Get blocks that have railway crossings for this track
        crossing_blocks = self.get_crossing_blocks_for_track(track)
        
        if crossing_blocks:
            self.crossing_block_dropdown['values'] = crossing_blocks
            self.crossing_block_var.set(crossing_blocks[0])
            self.on_crossing_block_change()
        else:
            self.crossing_block_dropdown['values'] = []
            self.crossing_block_var.set("")
            self.crossing_status_var.set("No crossings available")

    def on_crossing_block_change(self, event=None):
        track = self.crossing_track_var.get()
        block = self.crossing_block_dropdown.get()
        
        if block:
            # Check if we have a saved setting for this track/block
            key = (track, block)
            if key in self.crossing_settings:
                # Restore the saved settings and status
                lights_status, crossbar_status = self.crossing_settings[key]
                self.crossing_lights_var.set(lights_status)
                self.crossing_crossbar_var.set(crossbar_status)
                self.crossing_status_var.set(f"Lights: {lights_status}, Crossbar: {crossbar_status}")
            else:
                # No saved setting, show ready status
                self.crossing_status_var.set(f"Ready - Block {block}")
        else:
            self.crossing_status_var.set("No crossing set")

    def set_lights(self):
        track = self.lights_track_var.get()
        block = self.lights_block_var.get()
        color = self.lights_color_var.get()
        
        if not block:
            messagebox.showwarning("Input Error", "Please select a block number")
            return
        
        # Save the setting for persistence
        key = (track, block)
        self.lights_settings[key] = color
        
        # Update status display
        self.lights_status_var.set(f"Lights: {color}")
        
        messagebox.showinfo("Lights Set", 
                          f"Lights configured for:\nTrack: {track}\nBlock: {block}\nColor: {color}")
        
        # Log the action - use the direct callback
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} LIGHTS: Set to {color} on {track} track, Block {block}")

    def set_crossing(self):
        track = self.crossing_track_var.get()
        block = self.crossing_block_var.get()
        lights_status = self.crossing_lights_var.get()
        crossbar_status = self.crossing_crossbar_var.get()
        
        if not block:
            messagebox.showwarning("Input Error", "Please select a block number")
            return
        
        # Save the setting for persistence
        key = (track, block)
        self.crossing_settings[key] = (lights_status, crossbar_status)
        
        # Update status display
        self.crossing_status_var.set(f"Lights: {lights_status}, Crossbar: {crossbar_status}")
        
        messagebox.showinfo("Crossing Set", 
                          f"Railway Crossing configured:\nTrack: {track}\nBlock: {block}\n"
                          f"Lights: {lights_status}\nCrossbar: {crossbar_status}")
        
        # Log the action - use the direct callback
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} CROSSING: Set - Lights: {lights_status}, Crossbar: {crossbar_status} on {track} track, Block {block}")