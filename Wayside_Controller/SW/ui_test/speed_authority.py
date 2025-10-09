import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class SpeedAuthorityControl:
    def __init__(self, parent, track_config):
        self.parent = parent
        self.track_config = track_config
        self.log_callback = None
        
        # Store block-specific data
        self.block_data = {}
        self.modified_blocks = set()
        
        self.create_speed_authority_controls()
    
    def set_log_callback(self, callback):
        self.log_callback = callback
    
    def get_block_key(self, track, block):
        return f"{track}_{block}"
    
    def get_block_data(self, track, block):
        """Get data for specific block - COMPLETELY DYNAMIC"""
        key = self.get_block_key(track, block)
        if key not in self.block_data:
            # Get defaults from track config
            track_data = self.track_config.tracks.get(track, {})
            self.block_data[key] = {
                'suggested_speed': track_data.get("suggested_speed", "0"),
                'suggested_authority': track_data.get("suggested_authority", "0"),
                'commanded_speed': track_data.get("commanded_speed", "0"),
                'commanded_authority': track_data.get("commanded_authority", "0"),
                'occupied': False
            }
        return self.block_data[key]
    
    def save_block_data(self, track, block, data):
        key = self.get_block_key(track, block)
        self.block_data[key] = data
    
    def is_block_modified(self, track, block):
        key = self.get_block_key(track, block)
        return key in self.modified_blocks
    
    def create_speed_authority_controls(self):
        # Suggested Values Card
        suggested_card = tk.Frame(self.parent, bg="white", relief='raised', bd=2, padx=15, pady=15)
        suggested_card.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(suggested_card, text="Suggested Values", font=("Arial", 16, "bold"), 
                bg="white", fg="#2d2d86").pack(anchor='w', pady=(0, 15))
        
        # Track selection - DYNAMIC
        input_frame = tk.Frame(suggested_card, bg="white")
        input_frame.pack(fill='x', pady=5)
        
        tk.Label(input_frame, text="Track:", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, sticky='w', pady=8)
        self.suggested_track_var = tk.StringVar()
        track_names = self.track_config.get_track_names()
        self.suggested_track_dropdown = ttk.Combobox(input_frame, textvariable=self.suggested_track_var, 
                                                   values=track_names, state="readonly", width=15)
        self.suggested_track_dropdown.grid(row=0, column=1, sticky='w', pady=8, padx=(10, 0))
        
        tk.Label(input_frame, text="Block Number:", font=("Arial", 12, "bold"), bg="white").grid(row=1, column=0, sticky='w', pady=8)
        self.suggested_block_var = tk.StringVar()
        self.suggested_block_dropdown = ttk.Combobox(input_frame, textvariable=self.suggested_block_var, 
                                                   state="readonly", width=15)
        self.suggested_block_dropdown.grid(row=1, column=1, sticky='w', pady=8, padx=(10, 0))
        
        # Display values with controls - SAME FORMAT AS COMMANDED
        values_frame = tk.Frame(suggested_card, bg="white")
        values_frame.pack(fill='x', pady=15)
        
        # Suggested Speed control
        speed_frame = tk.Frame(values_frame, bg="white")
        speed_frame.pack(fill='x', pady=10)
        tk.Label(speed_frame, text="Speed:", font=("Arial", 12, "bold"), bg="white").pack(side='left')
        self.suggested_speed_var = tk.StringVar(value="0")
        tk.Label(speed_frame, textvariable=self.suggested_speed_var,
                font=("Arial", 12, "bold"), bg="white", fg="#4d4dff").pack(side='left', padx=(10, 0))
        ttk.Button(speed_frame, text="Set Speed", command=self.set_suggested_speed, width=10).pack(side='right', padx=(10, 0))

        # Suggested Authority control
        auth_frame = tk.Frame(values_frame, bg="white")
        auth_frame.pack(fill='x', pady=10)
        tk.Label(auth_frame, text="Authority:", font=("Arial", 12, "bold"), bg="white").pack(side='left')
        self.suggested_auth_var = tk.StringVar(value="0")
        tk.Label(auth_frame, textvariable=self.suggested_auth_var,
                font=("Arial", 12, "bold"), bg="white", fg="#4d4dff").pack(side='left', padx=(10, 0))
        ttk.Button(auth_frame, text="Set Authority", command=self.set_suggested_authority, width=10).pack(side='right', padx=(10, 0))

        # Commanded Values Card
        commanded_card = tk.Frame(self.parent, bg="white", relief='raised', bd=2, padx=15, pady=15)
        commanded_card.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(commanded_card, text="Commanded Values", font=("Arial", 16, "bold"), 
                bg="white", fg="#2d2d86").pack(anchor='w', pady=(0, 15))
        
        # Commanded track selection - DYNAMIC
        cmd_input_frame = tk.Frame(commanded_card, bg="white")
        cmd_input_frame.pack(fill='x', pady=5)
        
        tk.Label(cmd_input_frame, text="Track:", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, sticky='w', pady=8)
        self.commanded_track_var = tk.StringVar()
        self.commanded_track_dropdown = ttk.Combobox(cmd_input_frame, textvariable=self.commanded_track_var, 
                                                   values=track_names, state="readonly", width=15)
        self.commanded_track_dropdown.grid(row=0, column=1, sticky='w', pady=8, padx=(10, 0))
        
        tk.Label(cmd_input_frame, text="Block Number:", font=("Arial", 12, "bold"), bg="white").grid(row=1, column=0, sticky='w', pady=8)
        self.commanded_block_var = tk.StringVar()
        self.commanded_block_dropdown = ttk.Combobox(cmd_input_frame, textvariable=self.commanded_block_var, 
                                                   state="readonly", width=15)
        self.commanded_block_dropdown.grid(row=1, column=1, sticky='w', pady=8, padx=(10, 0))
        
        # Block Occupancy Status
        occupancy_frame = tk.Frame(commanded_card, bg="white")
        occupancy_frame.pack(fill='x', pady=10)
        
        tk.Label(occupancy_frame, text="Block Status:", font=("Arial", 12, "bold"), bg="white").pack(side='left')
        self.occupancy_var = tk.StringVar(value="Unoccupied")
        self.occupancy_label = tk.Label(occupancy_frame, textvariable=self.occupancy_var, 
                                      font=("Arial", 12, "bold"), bg="green", fg="white", padx=10, pady=2)
        self.occupancy_label.pack(side='left', padx=(10, 0))
        
        ttk.Button(occupancy_frame, text="Toggle Status", command=self.toggle_occupancy, width=12).pack(side='left', padx=(10, 0))
        
        # Commanded values with controls
        cmd_values_frame = tk.Frame(commanded_card, bg="white")
        cmd_values_frame.pack(fill='x', pady=15)
        
        # Speed control
        cmd_speed_frame = tk.Frame(cmd_values_frame, bg="white")
        cmd_speed_frame.pack(fill='x', pady=10)
        tk.Label(cmd_speed_frame, text="Speed:", font=("Arial", 12, "bold"), bg="white").pack(side='left')
        self.commanded_speed_var = tk.StringVar(value="0")
        tk.Label(cmd_speed_frame, textvariable=self.commanded_speed_var, 
                font=("Arial", 12, "bold"), bg="white", fg="#4d4dff").pack(side='left', padx=(10, 0))
        ttk.Button(cmd_speed_frame, text="Set Speed", command=self.set_commanded_speed, width=10).pack(side='right', padx=(10, 0))
        
        # Authority control
        cmd_auth_frame = tk.Frame(cmd_values_frame, bg="white")
        cmd_auth_frame.pack(fill='x', pady=10)
        tk.Label(cmd_auth_frame, text="Authority:", font=("Arial", 12, "bold"), bg="white").pack(side='left')
        self.commanded_auth_var = tk.StringVar(value="0")
        tk.Label(cmd_auth_frame, textvariable=self.commanded_auth_var, 
                font=("Arial", 12, "bold"), bg="white", fg="#4d4dff").pack(side='left', padx=(10, 0))
        ttk.Button(cmd_auth_frame, text="Set Authority", command=self.set_commanded_authority, width=10).pack(side='right', padx=(10, 0))
        
        # Bind events
        self.suggested_track_dropdown.bind('<<ComboboxSelected>>', self.on_suggested_track_change)
        self.suggested_block_dropdown.bind('<<ComboboxSelected>>', self.on_suggested_block_change)
        self.commanded_track_dropdown.bind('<<ComboboxSelected>>', self.on_commanded_track_change)
        self.commanded_block_dropdown.bind('<<ComboboxSelected>>', self.on_commanded_block_change)
        
        # Initialize with first track if available
        if track_names:
            self.suggested_track_var.set(track_names[0])
            self.commanded_track_var.set(track_names[0])
            self.on_suggested_track_change()
            self.on_commanded_track_change()
    
    def update_occupancy_display(self, occupied):
        if occupied:
            self.occupancy_var.set("Occupied")
            self.occupancy_label.config(bg="red")
        else:
            self.occupancy_var.set("Unoccupied")
            self.occupancy_label.config(bg="green")
    
    def toggle_occupancy(self):
        track = self.commanded_track_var.get()
        block = self.commanded_block_var.get()
        
        if not track or not block:
            messagebox.showwarning("Input Error", "Please select both track and block")
            return
        
        block_data = self.get_block_data(track, block)
        current_occupied = block_data.get('occupied', False)
        new_occupied = not current_occupied
        
        # ONLY update occupancy
        block_data['occupied'] = new_occupied
        self.save_block_data(track, block, block_data)
        
        # Update ONLY occupancy display
        self.update_occupancy_display(new_occupied)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Occupied" if new_occupied else "Unoccupied"
        if self.log_callback:
            self.log_callback(f"{current_time} OCCUPANCY: Block {block} on {track} track set to {status}")
    
    def on_suggested_track_change(self, event=None):
        track = self.suggested_track_var.get()
        blocks = self.track_config.get_available_blocks(track)
        self.suggested_block_dropdown['values'] = blocks
        if blocks:
            self.suggested_block_var.set(blocks[0])
            self.commanded_track_var.set(track)
            self.commanded_block_dropdown['values'] = blocks
            self.commanded_block_var.set(blocks[0])
    
    def on_suggested_block_change(self, event=None):
        self.commanded_block_var.set(self.suggested_block_var.get())
    
    def on_commanded_track_change(self, event=None):
        track = self.commanded_track_var.get()
        blocks = self.track_config.get_available_blocks(track)
        self.commanded_block_dropdown['values'] = blocks
        if blocks:
            self.commanded_block_var.set(blocks[0])
            self.suggested_track_var.set(track)
            self.suggested_block_dropdown['values'] = blocks
            self.suggested_block_var.set(blocks[0])
    
    def on_commanded_block_change(self, event=None):
        self.suggested_block_var.set(self.commanded_block_var.get())
    
    def fetch_all_data(self):
        track = self.suggested_track_var.get()
        block = self.suggested_block_var.get()
        
        if not track or not block:
            messagebox.showwarning("Input Error", "Please select both track and block")
            return
        
        block_data = self.get_block_data(track, block)
        
        # Update displays with current values (no syncing)
        self.suggested_speed_var.set(block_data.get('suggested_speed', '0'))
        self.suggested_auth_var.set(block_data.get('suggested_authority', '0'))
        self.commanded_speed_var.set(block_data.get('commanded_speed', '0'))
        self.commanded_auth_var.set(block_data.get('commanded_authority', '0'))
        
        # Update occupancy
        occupied = block_data.get('occupied', False)
        self.update_occupancy_display(occupied)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} DATA: Fetched current data for {track} track, Block {block}")
            
    def set_suggested_speed(self):
        track = self.suggested_track_var.get()
        block = self.suggested_block_var.get()
        
        if not track or not block:
            messagebox.showwarning("Input Error", "Please select both track and block")
            return

        current_speed = self.suggested_speed_var.get()
        new_speed = simpledialog.askfloat("Set Suggested Speed", 
                                        f"Enter new suggested speed (mph) for {track} track, Block {block}:",
                                        initialvalue=float(current_speed) if current_speed.replace('.', '').isdigit() else 0)
        if new_speed is not None:
            self.suggested_speed_var.set(f"{new_speed}")
            block_data = self.get_block_data(track, block)
            block_data['suggested_speed'] = f"{new_speed}"
            self.save_block_data(track, block, block_data)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} SPEED: Set suggested speed to {new_speed} mph on {track} track, Block {block}")

    def set_suggested_authority(self):
        track = self.suggested_track_var.get()
        block = self.suggested_block_var.get()
        
        if not track or not block:
            messagebox.showwarning("Input Error", "Please select both track and block")
            return

        current_auth = self.suggested_auth_var.get()
        new_auth = simpledialog.askinteger("Set Suggested Authority", 
                                        f"Enter new suggested authority (blocks) for {track} track, Block {block}:",
                                        initialvalue=int(current_auth) if current_auth.isdigit() else 0)
        if new_auth is not None:
            self.suggested_auth_var.set(f"{new_auth}")
            block_data = self.get_block_data(track, block)
            block_data['suggested_authority'] = f"{new_auth}"
            self.save_block_data(track, block, block_data)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} AUTHORITY: Set suggested authority to {new_auth} blocks on {track} track, Block {block}")
            
    def set_commanded_speed(self):
        track = self.commanded_track_var.get()
        block = self.commanded_block_var.get()
        
        current_speed = self.commanded_speed_var.get()
        new_speed = simpledialog.askfloat("Set Commanded Speed", 
                                        f"Enter new commanded speed (mph) for {track} track, Block {block}:",
                                        initialvalue=float(current_speed) if current_speed.replace('.', '').isdigit() else 0)
        if new_speed is not None:
            # Update ONLY speed display
            self.commanded_speed_var.set(f"{new_speed}")
            
            block_data = self.get_block_data(track, block)
            
            # CRITICAL: ONLY update commanded speed, leave everything else unchanged
            block_data['commanded_speed'] = f"{new_speed}"
            
            # DO NOT update suggested speed - keep it separate
            # block_data['suggested_speed'] remains unchanged
            
            self.save_block_data(track, block, block_data)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} SPEED: Set commanded speed to {new_speed} mph on {track} track, Block {block}")


    def set_commanded_authority(self):
        track = self.commanded_track_var.get()
        block = self.commanded_block_var.get()
        
        if not track or not block:
            messagebox.showwarning("Input Error", "Please select both track and block")
            return
        
        current_auth = self.commanded_auth_var.get()
        new_auth = simpledialog.askinteger("Set Commanded Authority", 
                                        f"Enter new commanded authority (blocks) for {track} track, Block {block}:",
                                        initialvalue=int(current_auth) if current_auth.isdigit() else 0)
        if new_auth is not None:
            # Update ONLY authority display
            self.commanded_auth_var.set(f"{new_auth}")
            
            block_data = self.get_block_data(track, block)
            
            # CRITICAL: ONLY update commanded authority, leave everything else unchanged
            block_data['commanded_authority'] = f"{new_auth}"
            
            # DO NOT update suggested authority - keep it separate
            # block_data['suggested_authority'] remains unchanged
            
            self.save_block_data(track, block, block_data)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} AUTHORITY: Set commanded authority to {new_auth} blocks on {track} track, Block {block}")
