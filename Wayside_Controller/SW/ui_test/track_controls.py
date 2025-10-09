import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


class TrackControls:
    def __init__(self, parent, track_config):
        self.parent = parent
        self.track_config = track_config
        self.log_callback = None
        
        # Store current settings for status persistence
        self.switch_settings = {}  # Format: {(track, block): switch_direction}
        
        self.create_track_controls()
    
    def set_log_callback(self, callback):
        self.log_callback = callback
    
    def create_track_controls(self):
        # Switches Control Card
        switches_card = tk.Frame(self.parent, bg="white", relief='raised', bd=2, padx=12, pady=12)
        switches_card.pack(side='left', fill='both', expand=True, padx=3)
        
        tk.Label(switches_card, text="Switches Control", font=("Arial", 14, "bold"), 
                bg="white", fg="#2d2d86").pack(anchor='w', pady=(0, 12))
        
        # Switch inputs
        switch_input_frame = tk.Frame(switches_card, bg="white")
        switch_input_frame.pack(fill='x', pady=10)
        
        tk.Label(switch_input_frame, text="Track:", font=("Arial", 11, "bold"), bg="white").grid(row=0, column=0, sticky='w', pady=8)
        self.switches_track_var = tk.StringVar(value="Green")
        self.switches_track_dropdown = ttk.Combobox(switch_input_frame, textvariable=self.switches_track_var, 
                                                  values=["Green", "Red", "Blue"], state="readonly", width=12)
        self.switches_track_dropdown.grid(row=0, column=1, sticky='w', pady=8, padx=(10, 0))
        
        tk.Label(switch_input_frame, text="Block #:", font=("Arial", 11, "bold"), bg="white").grid(row=1, column=0, sticky='w', pady=8)
        self.switches_block_var = tk.StringVar(value="")
        self.switches_block_dropdown = ttk.Combobox(switch_input_frame, textvariable=self.switches_block_var, 
                                                  state="readonly", width=12)
        self.switches_block_dropdown.grid(row=1, column=1, sticky='w', pady=8, padx=(10, 0))
        
        # Switch options
        switch_options_frame = tk.Frame(switches_card, bg="white")
        switch_options_frame.pack(fill='x', pady=15)
        
        tk.Label(switch_options_frame, text="Switch Direction:", font=("Arial", 12, "bold"), 
                bg="white").pack(anchor='w', pady=(0, 10))
        
        self.switch_var = tk.StringVar()
        self.switch_radio_frame = tk.Frame(switch_options_frame, bg="white")
        self.switch_radio_frame.pack(fill='x', pady=5)
        
        # Current switch status display
        status_frame = tk.Frame(switches_card, bg="white")
        status_frame.pack(fill='x', pady=10)
        
        tk.Label(status_frame, text="Current Status:", font=("Arial", 12, "bold"), bg="white").pack(anchor='w')
        self.switch_status_var = tk.StringVar(value="No switch set")
        status_label = tk.Label(status_frame, textvariable=self.switch_status_var, 
                              font=("Arial", 11), bg="white", fg="#2d2d86")
        status_label.pack(anchor='w', pady=5)
        
        ttk.Button(switches_card, text="Set Switches", command=self.set_switches, width=15).pack(pady=10)
        
        # Bind track change event
        self.switches_track_dropdown.bind('<<ComboboxSelected>>', self.on_switches_track_change)
        self.switches_block_dropdown.bind('<<ComboboxSelected>>', self.on_switches_block_change)
        
        # Initialize with default track
        self.on_switches_track_change()
    
    def get_switch_options_for_block(self, track, block):
        """Get the available switch directions for a specific track and block"""
        # Use the track_config method instead of hardcoded values
        return self.track_config.get_switch_options(track, block)
    
    def on_switches_track_change(self, event=None):
        track = self.switches_track_var.get()
        # Get blocks that have switches for this track
        switch_blocks = self.track_config.get_blocks_with_switches(track)
        
        if switch_blocks:
            self.switches_block_dropdown['values'] = switch_blocks
            self.switches_block_var.set(switch_blocks[0])
            self.on_switches_block_change()
        else:
            self.switches_block_dropdown['values'] = []
            self.switches_block_var.set("")
            self.switch_status_var.set("No switches available")
    
    def on_switches_block_change(self, event=None):
        track = self.switches_track_var.get()
        block = self.switches_block_var.get()
        
        # Clear existing radio buttons
        for widget in self.switch_radio_frame.winfo_children():
            widget.destroy()
        
        if not block:
            tk.Label(self.switch_radio_frame, text="Select a block with switches", 
                    bg="white", fg="gray", font=("Arial", 10)).pack(anchor='w', pady=5)
            self.switch_status_var.set("No block selected")
            return
        
        # Get available switch directions for this track and block
        switch_options = self.get_switch_options_for_block(track, block)
        
        if switch_options:
            # Check if we have a saved setting for this track/block
            key = (track, block)
            saved_switch = self.switch_settings.get(key)
            
            # Create radio buttons for each switch direction
            for i, option in enumerate(switch_options):
                tk.Radiobutton(self.switch_radio_frame, text=option, variable=self.switch_var, 
                             value=option, bg="white", font=("Arial", 11)).pack(anchor='w', pady=3)
            
            # Select appropriate option
            if saved_switch and saved_switch in switch_options:
                # Use saved setting
                self.switch_var.set(saved_switch)
                self.switch_status_var.set(f"Set to: {saved_switch}")
            else:
                # Select first option by default
                self.switch_var.set(switch_options[0])
                self.switch_status_var.set(f"Ready - Block {block}")
        else:
            tk.Label(self.switch_radio_frame, text="No switches available for this block", 
                    bg="white", fg="gray", font=("Arial", 10)).pack(anchor='w', pady=5)
            self.switch_status_var.set("No switches available")
    
    def set_switches(self):
        if not self.switch_var.get():
            messagebox.showwarning("No Selection", "Please select a switch direction")
            return
            
        selected_switch = self.switch_var.get()
        track = self.switches_track_var.get()
        block = self.switches_block_var.get()
        
        # Save the setting for persistence
        key = (track, block)
        self.switch_settings[key] = selected_switch
        
        # Parse the switch direction for display
        parts = selected_switch.split('-')
        if len(parts) == 2:
            from_block, to_block = parts
            direction_text = f"from Block {from_block} to Block {to_block}"
        else:
            direction_text = selected_switch
        
        # Update status display
        self.switch_status_var.set(f"Set to: {selected_switch}")
        
        # Show confirmation
        messagebox.showinfo("Switches Set", 
                          f"Switches configured {direction_text}\n"
                          f"Track: {track}\nBlock: {block}")
        
        # Log the action
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_callback(f"{current_time} SWITCH: Set to {selected_switch} on {track} track, Block {block}")

           