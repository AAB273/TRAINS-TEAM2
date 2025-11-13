import tkinter as tk
from tkinter import ttk
from datetime import datetime

class RightPanel(tk.Frame):
    def __init__(self, parent, data):
        """Right panel for block information, commands, and status table"""
        super().__init__(parent, bg='#1a1a4d', width=300)
        self.pack_propagate(False)  # Prevent frame from shrinking
        self.data = data
        self.log_callback = None  # Will be set by main application
        
        # Store information about currently selected block
        self.current_block_info = {}
        
        # CHANGED: Separate dictionaries for authority and speed instead of combined values
        # This makes data structure clearer and easier to maintain
        self.commanded_authority = {"Blue": {}, "Green": {}, "Red": {}}
        self.commanded_speed = {"Blue": {}, "Green": {}, "Red": {}}
        self.suggested_authority = {"Blue": {}, "Green": {}, "Red": {}}
        self.suggested_speed = {"Blue": {}, "Green": {}, "Red": {}}
        
        # Ensure all blocks have faulted column for consistency
        self.ensure_faulted_column()
        
        # Build all UI components
        self.create_widgets()

        # HARDCODE the yard to station commands
        self.set_yard_to_station_commands()

        # Connect callbacks for real-time updates
        self.data.on_line_change.append(self.on_line_changed)  # When line changes
        self.data.on_data_update.append(self.refresh_ui)       # When data updates
    
    def ensure_faulted_column(self):
        """Ensure all blocks have the Faulted column (index 3) for data consistency"""
        for row in self.data.block_data:
            if len(row) < 4:
                row.append("No")  # Default to not faulted
        for row in self.data.block_data_original:
            if len(row) < 4:
                row.append("No")  # Default to not faulted
    
    def set_log_callback(self, callback):
        """Set the callback function for logging messages to system log"""
        self.log_callback = callback
    
    def refresh_ui(self):
        """Refresh all UI elements when data changes externally"""
        print("DEBUG: RightPanel refresh_ui called")
        self.update_block_options()        # Update dropdown
        self.create_block_table()          # Refresh status table
        self.update_current_block_info()   # Update block details
        self.update_suggested_display()    # Update suggested values
        self.update_commanded_display()    # Update commanded values

    def create_widgets(self):
        """Create all UI components in the right panel"""
        # Block selector - choose which block to view/modify
        block_frame = tk.Frame(self, bg='#cccccc')
        block_frame.pack(fill=tk.X, pady=5)
        tk.Label(block_frame, text="Block", bg='#cccccc').pack(side=tk.LEFT, padx=5)
        
        self.block_combo = ttk.Combobox(block_frame, width=10, state='readonly')
        self.block_combo.pack(side=tk.LEFT, padx=5)
        self.block_combo.bind('<<ComboboxSelected>>', self.on_block_selected)
        
        # Create various sections of the panel
        self.create_current_block_section()       # Block details display
        self.create_suggested_section()           # Suggested values from CTC
        self.create_commanded_display_section()   # Current commanded values
        self.create_commanded_section()           # Input for new commands
        self.create_block_table_section()         # Block status table
        
        # Initialize with current data
        self.update_block_options()

    def update_block_options(self):
        """Update block selector dropdown based on current line"""
        # row format: [occupied, line, block, faulted]
        # Filter blocks for current line and sort numerically
        blocks = sorted([row[2] for row in self.data.block_data if row[1] == self.data.current_line], key=int)
        self.block_combo['values'] = blocks
        if blocks:
            # Preserve selection if possible, otherwise select first block
            current_selection = self.block_combo.get()
            if current_selection in blocks:
                self.block_combo.set(current_selection)
            else:
                self.block_combo.set(blocks[0])
            self.update_current_block_info()  # Update display for selected block

    def on_block_selected(self, event):
        """When a new block is selected from dropdown, update all displays"""
        self.update_current_block_info()    # Update block details
        self.update_suggested_display()     # Update suggested values
        self.update_commanded_display()     # Update commanded values

    def update_current_block_info(self):
        """Update the current block information from data model"""
        selected_block = self.block_combo.get()
        if selected_block:
            # Find the block data for current line and selected block
            # row format: [occupied, line, block, faulted]
            for row in self.data.block_data:
                if row[1] == self.data.current_line and str(row[2]) == str(selected_block):
                    self.current_block_info = {
                        'block': row[2],
                        'line': row[1],
                        'occupied': row[0],
                        'faulted': row[3] if len(row) > 3 else 'No'  # Handle missing faulted data
                    }
                    self.update_current_block_display()  # Update UI
                    break

    def create_current_block_section(self):
        """Display current selected block information (read-only)"""
        self.current_block_frame = tk.LabelFrame(self, text="Current Block:", 
                                               bg='#cccccc', font=('Arial', 10, 'bold'))
        self.current_block_frame.pack(fill=tk.X, pady=5)
        
        # Create labels for block number, occupied status, and faulted status
        labels = [
            ("Block #:", "block_num_label"),    # Block number display
            ("Occupied:", "occupied_label"),    # Occupancy status (Yes/No)
            ("Faulted:", "faulted_label")       # Fault status (Yes/No)
        ]
        
        for label_text, attr_name in labels:
            frame = tk.Frame(self.current_block_frame, bg='#cccccc')
            frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=label_text, bg='#cccccc', width=10).pack(side=tk.LEFT)
            # Create display label with sunken relief for data display look
            label = tk.Label(frame, text="", bg='white', width=8, relief=tk.SUNKEN, anchor='w')
            label.pack(side=tk.LEFT, padx=2)
            setattr(self, attr_name, label)  # Store reference for later updates

    def update_current_block_display(self):
        """Update the current block display with current data and colors"""
        if hasattr(self, 'block_num_label') and hasattr(self, 'occupied_label'):
            if self.current_block_info:
                # Update block number
                self.block_num_label.config(text=self.current_block_info['block'])
                
                # Occupied display with color coding
                occupied_text = "Yes" if self.current_block_info['occupied'] == "Yes" else "No"
                occupied_color = '#ffcccc' if self.current_block_info['occupied'] == "Yes" else '#ccffcc'
                self.occupied_label.config(text=occupied_text, bg=occupied_color)
                
                # Faulted display with color coding
                faulted_text = self.current_block_info.get('faulted', 'No')
                faulted_color = '#ffcccc' if faulted_text == "Yes" else '#ccffcc'
                self.faulted_label.config(text=faulted_text, bg=faulted_color)

    def create_suggested_section(self):
        """Display suggested authority and speed from CTC office"""
        suggested_frame = tk.LabelFrame(self, text="Suggested:", 
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        suggested_frame.pack(fill=tk.X, pady=5)
        
        # Create authority and speed display labels
        labels = [
            ("Authority:", "suggested_auth_label"),   # Suggested authority from CTC
            ("Speed:", "suggested_speed_label")       # Suggested speed from CTC
        ]
        
        for label_text, attr_name in labels:
            frame = tk.Frame(suggested_frame, bg='#cccccc')
            frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=label_text, bg='#cccccc').pack(side=tk.LEFT)
            # Set default text based on field type
            default_text = "0 blocks" if "Authority" in label_text else "0 mph"
            label = tk.Label(frame, text=default_text, bg='white', relief=tk.SUNKEN, width=12, anchor='w')
            label.pack(side=tk.LEFT, padx=2)
            setattr(self, attr_name, label)  # Store reference for updates

    def update_suggested_display(self):
        """Update suggested values display from CTC office"""
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line:
            # FIRST priority: Check if we have values from shared data (CTC input)
            if hasattr(self.data, 'suggested_authority'):
                data_auth = self.data.suggested_authority.get(current_line, {}).get(selected_block)
                data_speed = self.data.suggested_speed.get(current_line, {}).get(selected_block)
                
                if data_auth is not None:
                    # Use values from shared data (CTC office)
                    self.suggested_auth_label.config(text=f"{data_auth} blocks")
                    self.suggested_speed_label.config(text=f"{data_speed} mph")
                    
                    # Also update our local suggested dictionaries to stay in sync
                    self.suggested_authority[current_line][selected_block] = data_auth
                    self.suggested_speed[current_line][selected_block] = data_speed
                    
                else:
                    # SECOND priority: Check our local storage
                    local_auth = self.suggested_authority.get(current_line, {}).get(selected_block)
                    local_speed = self.suggested_speed.get(current_line, {}).get(selected_block)
                    
                    if local_auth is not None:
                        # Use manually set suggested values
                        self.suggested_auth_label.config(text=f"{local_auth} blocks")
                        self.suggested_speed_label.config(text=f"{local_speed} mph")
                    else:
                        # No values found - show defaults
                        self.suggested_auth_label.config(text="0 blocks")
                        self.suggested_speed_label.config(text="0 mph")
            else:
                # Fallback to our local storage
                local_auth = self.suggested_authority.get(current_line, {}).get(selected_block)
                local_speed = self.suggested_speed.get(current_line, {}).get(selected_block)
                
                if local_auth is not None:
                    self.suggested_auth_label.config(text=f"{local_auth} blocks")
                    self.suggested_speed_label.config(text=f"{local_speed} mph")
                else:
                    # No values found anywhere - show defaults
                    self.suggested_auth_label.config(text="0 blocks")
                    self.suggested_speed_label.config(text="0 mph")
        else:
            # No block selected - show N/A
            self.suggested_auth_label.config(text="N/A")
            self.suggested_speed_label.config(text="N/A")

    def create_commanded_display_section(self):
        """Display the current commanded values sent to trains"""
        self.commanded_display_frame = tk.LabelFrame(self, text="Current Commanded:", 
                                                   bg='#cccccc', font=('Arial', 10, 'bold'))
        self.commanded_display_frame.pack(fill=tk.X, pady=5)
        
        # Create authority and speed display for commanded values
        labels = [
            ("Authority:", "commanded_auth_label"),   # Commanded authority to train
            ("Speed:", "commanded_speed_label")       # Commanded speed to train
        ]
        
        for label_text, attr_name in labels:
            frame = tk.Frame(self.commanded_display_frame, bg='#cccccc')
            frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=label_text, bg='#cccccc').pack(side=tk.LEFT)
            # Light blue background for commanded values
            default_text = "0 blocks" if "Authority" in label_text else "0 mph"
            label = tk.Label(frame, text=default_text, bg='#e6f7ff', relief=tk.SUNKEN, width=12, anchor='w')
            label.pack(side=tk.LEFT, padx=2)
            setattr(self, attr_name, label)  # Store reference for updates

    def create_commanded_section(self):
        """Input section for setting new commanded values"""
        commanded_frame = tk.LabelFrame(self, text="Set New Command:", 
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        commanded_frame.pack(fill=tk.X, pady=5)
        
        # Create authority and speed input fields with increment buttons
        inputs = [
            ("Authority:", "auth_entry", self.increment_auth),   # Authority input
            ("Speed:", "speed_entry", self.increment_speed)      # Speed input
        ]
        
        for label_text, entry_name, btn_cmd in inputs:
            frame = tk.Frame(commanded_frame, bg='#cccccc')
            frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=label_text, bg='#cccccc').pack(side=tk.LEFT)
            
            # Create entry field for manual input
            entry = tk.Entry(frame, width=8)
            entry.insert(0, "0")  # Default value
            entry.pack(side=tk.LEFT, padx=2)
            setattr(self, entry_name, entry)  # Store reference
            
            # Create up/down buttons for easy increment/decrement
            btn_frame = tk.Frame(frame, bg='#cccccc')
            btn_frame.pack(side=tk.LEFT, padx=2)
            
            # Up button to increment value
            tk.Button(btn_frame, text="▲", width=2, command=lambda cmd=btn_cmd: cmd(1)).pack(side=tk.TOP)
            # Down button to decrement value
            tk.Button(btn_frame, text="▼", width=2, command=lambda cmd=btn_cmd: cmd(-1)).pack(side=tk.BOTTOM)
        
        # Send command button to apply the values
        tk.Button(commanded_frame, text="Send Command", bg='#2e8b57', fg='white',
                 command=self.send_command).pack(fill=tk.X, padx=5, pady=5)

    def update_commanded_display(self):
        """Update commanded display with values for current block - FIXED VERSION"""
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line:
            # ALWAYS use the shared data from RailwayData - don't use local storage
            data_auth = self.data.commanded_authority.get(current_line, {}).get(selected_block)
            data_speed = self.data.commanded_speed.get(current_line, {}).get(selected_block)
            
            if data_auth is not None or data_speed is not None:
                # Use values from RailwayData (this allows Test UI to override)
                auth_text = f"{data_auth} blocks" if data_auth is not None else "0 blocks"
                speed_text = f"{data_speed} mph" if data_speed is not None else "0 mph"
                
                self.commanded_auth_label.config(text=auth_text)
                self.commanded_speed_label.config(text=speed_text)
                
                # Also update our local commanded dictionaries to stay in sync
                if data_auth is not None:
                    self.commanded_authority[current_line][selected_block] = data_auth
                if data_speed is not None:
                    self.commanded_speed[current_line][selected_block] = data_speed
                
            else:
                # Fallback to PLC-calculated values from track data
                block_key = f"Block {selected_block}"
                if hasattr(self.data, 'filtered_blocks') and block_key in self.data.filtered_blocks:
                    block_data = self.data.filtered_blocks[block_key]
                    authority = block_data.get("authority", 0)
                    speed = block_data.get("speed", 0)
                    
                    self.commanded_auth_label.config(text=f"{authority} blocks")
                    self.commanded_speed_label.config(text=f"{speed} mph")
                else:
                    # No values found anywhere - show defaults
                    self.commanded_auth_label.config(text="0 blocks")
                    self.commanded_speed_label.config(text="0 mph")

    def increment_auth(self, delta):
        """Increment/decrement authority value in the input field"""
        try:
            current = int(self.auth_entry.get())
            new_val = max(0, current + delta)  # Ensure non-negative
            self.auth_entry.delete(0, tk.END)
            self.auth_entry.insert(0, str(new_val))
        except ValueError:
            # Handle invalid input
            self.auth_entry.delete(0, tk.END)
            self.auth_entry.insert(0, "0")

    def increment_speed(self, delta):
        """Increment/decrement speed value in the input field"""
        try:
            current = int(self.speed_entry.get())
            new_val = max(0, current + delta)  # Ensure non-negative
            self.speed_entry.delete(0, tk.END)
            self.speed_entry.insert(0, str(new_val))
        except ValueError:
            # Handle invalid input
            self.speed_entry.delete(0, tk.END)
            self.speed_entry.insert(0, "0")

    def send_command(self):
        """Send commanded speed and authority to train and update data models - FIXED VERSION"""
        authority = self.auth_entry.get()
        speed = self.speed_entry.get()
        block = self.block_combo.get()
        current_line = self.data.current_line
        
        # Store in BOTH locations for consistency, but RailwayData is the source of truth
        # Local storage for this panel
        self.commanded_authority[current_line][block] = authority
        self.commanded_speed[current_line][block] = speed
        
        # SHARED data storage is the source of truth (this allows Test UI to override)
        self.data.commanded_authority[current_line][block] = authority
        self.data.commanded_speed[current_line][block] = speed
        
        # Update track_data immediately so PLC can work with it
        block_key = f"Block {block}"
        if hasattr(self.data, 'filtered_blocks') and block_key in self.data.filtered_blocks:
            try:
                # Convert to integers for PLC processing
                self.data.filtered_blocks[block_key]["authority"] = int(authority)
                self.data.filtered_blocks[block_key]["speed"] = int(speed)
            except ValueError:
                # Handle conversion errors gracefully
                print(f"Warning: Could not convert commanded values to integers: {authority}, {speed}")
        
        # SEND TO TRACK MODEL VIA MAIN UI
        if hasattr(self.data, 'app') and self.data.app:
            self.data.app.send_commanded_to_track_model(current_line, block, speed, authority)
                
        # Log the command action
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} COMMAND: Block {block} on {current_line} - Authority: {authority} blocks, Speed: {speed} mph")

        # Update the display to show the new commanded values
        self.update_commanded_display()

    def create_block_table_section(self):
        """Create the search and block status table section"""
        # Search frame with label
        search_frame = tk.Frame(self, bg='#1a1a4d')
        search_frame.pack(fill=tk.X, pady=5)
        self.block_search_var = tk.StringVar()
        self.block_search_var.trace('w', self.filter_block_table)  # Real-time filtering
        block_search = tk.Entry(search_frame, textvariable=self.block_search_var, width=20)
        block_search.pack(side=tk.LEFT, padx=5)
        tk.Label(search_frame, text="Search", bg='#1a1a4d', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Create scrollable table container
        table_container = tk.LabelFrame(self, text="Block Status", bg='#1a1a4d', fg='white', font=('Arial', 10, 'bold'))
        table_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Simplified scrollable table setup
        canvas_frame = tk.Frame(table_container, bg='#1a1a4d')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollbars for table
        x_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        y_scrollbar = tk.Scrollbar(canvas_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        # Canvas for scrolling
        self.table_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0,
                                     xscrollcommand=x_scrollbar.set,
                                     yscrollcommand=y_scrollbar.set)
        self.table_canvas.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbars
        x_scrollbar.config(command=self.table_canvas.xview)
        y_scrollbar.config(command=self.table_canvas.yview)
        
        # Frame inside canvas for table content
        self.block_table_frame = tk.Frame(self.table_canvas, bg='white')
        self.table_canvas.create_window((0, 0), window=self.block_table_frame, anchor="nw")
        
        # Bind events for proper scrolling
        self.block_table_frame.bind("<Configure>", self._on_frame_configure)
        self.table_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Create the initial block table
        self.create_block_table()
    
    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame when it changes size"""
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        """Reset the canvas window to fill the canvas when it changes size"""
        self.table_canvas.itemconfig("all", width=event.width)
    
    def create_block_table(self):
        """Create the block status table with current data"""
        # Clear existing widgets in the table
        for widget in self.block_table_frame.winfo_children():
            widget.destroy()
        
        # Create headers using GRID with consistent column widths
        headers_frame = tk.Frame(self.block_table_frame, bg='#cccccc')
        headers_frame.pack(fill=tk.X)
        
        # Configure grid columns with specific widths
        headers_frame.columnconfigure(0, weight=1, minsize=80)  # Line - wider
        headers_frame.columnconfigure(1, weight=1, minsize=60)  # Block - wider
        headers_frame.columnconfigure(2, weight=1, minsize=80)  # Occupied - wider
        headers_frame.columnconfigure(3, weight=1, minsize=70)  # Faulted - wider
        
        # Header labels
        headers = ["Line", "Block", "Occupied", "Faulted"]
        widths = [10, 8, 10, 8]  # Corresponding widths
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            tk.Label(headers_frame, text=header, bg='#cccccc', width=width,
                    font=('Arial', 9, 'bold'), anchor='center').grid(row=0, column=i, sticky='ew', padx=1)
        
        # Data rows - Format: [occupied, line, block, faulted]
        self.block_combos = []  # Store references to comboboxes for maintenance mode
        self.faulted_combos = []  # Store references to faulted comboboxes
        
        # Get blocks for current line only
        line_blocks = [row for row in self.data.block_data if row[1] == self.data.current_line]
        
        for row_index, row in enumerate(line_blocks):
            row_frame = tk.Frame(self.block_table_frame, bg='white')
            row_frame.pack(fill=tk.X)
            
            # Configure grid columns for this row with same widths as headers
            for i in range(4):
                row_frame.columnconfigure(i, weight=1)
            
            # Get actual index in full block_data for callbacks
            actual_index = self.data.block_data.index(row)
            
            if self.data.maintenance_mode:
                # MAINTENANCE MODE: Line and Block are VISIBLE READ-ONLY, Occupied and Faulted are EDITABLE
                
                # COLUMN 1: LINE (read-only but clearly visible)
                bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
                line_label = tk.Label(row_frame, text=row[1], bg=bg_color, fg='white',
                        font=('Arial', 9, 'bold'), width=10,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                line_label.grid(row=0, column=0, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 2: BLOCK (read-only but clearly visible)
                block_label = tk.Label(row_frame, text=str(row[2]), bg='#2c2c2c', fg='white',
                        font=('Arial', 9, 'bold'), width=8,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                block_label.grid(row=0, column=1, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 3: OCCUPIED COMBO (editable in maintenance mode)
                occ_combo = ttk.Combobox(row_frame, values=["Yes", "No"], 
                                    font=('Arial', 9), width=8,
                                    state="readonly")
                occ_combo.set(row[0])
                occ_combo.grid(row=0, column=2, sticky='ew', padx=1, ipady=2)
                occ_combo.bind('<<ComboboxSelected>>', 
                    lambda event, idx=actual_index, combo=occ_combo: 
                    self.on_block_data_change(idx, 0, combo.get()))
                self.block_combos.append(occ_combo)
                
                # COLUMN 4: FAULTED COMBO (editable in maintenance mode)
                faulted_value = row[3] if len(row) > 3 else "No"
                faulted_combo = ttk.Combobox(row_frame, values=["Yes", "No"],
                                        font=('Arial', 9), width=8,
                                        state="readonly")
                faulted_combo.set(faulted_value)
                faulted_combo.grid(row=0, column=3, sticky='ew', padx=1, ipady=2)
                faulted_combo.bind('<<ComboboxSelected>>', 
                    lambda event, idx=actual_index, combo=faulted_combo: 
                    self.on_block_data_change(idx, 3, combo.get()))
                self.faulted_combos.append(faulted_combo)
                
            else:
                # NORMAL MODE: All columns are READ-ONLY with color coding
                # COLUMN 1: LINE with line-specific color
                bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
                line_label = tk.Label(row_frame, text=row[1], bg=bg_color, fg='white',
                        font=('Arial', 9, 'bold'), width=10,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                line_label.grid(row=0, column=0, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 2: BLOCK with dark background
                block_label = tk.Label(row_frame, text=str(row[2]), bg='#2c2c2c', fg='white',
                        font=('Arial', 9, 'bold'), width=8,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                block_label.grid(row=0, column=1, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 3: OCCUPIED with color coding (red for occupied, green for free)
                occupied_color = '#ff6666' if row[0] == "Yes" else '#ccffcc'
                occupied_label = tk.Label(row_frame, text=row[0], bg=occupied_color, fg='black',
                        font=('Arial', 9, 'bold'), width=10,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                occupied_label.grid(row=0, column=2, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 4: FAULTED with color coding (red for faulted, green for normal)
                faulted_value = row[3] if len(row) > 3 else "No"
                faulted_color = '#ff6666' if faulted_value == "Yes" else '#ccffcc'
                faulted_label = tk.Label(row_frame, text=faulted_value, bg=faulted_color, fg='black',
                        font=('Arial', 9, 'bold'), width=8,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                faulted_label.grid(row=0, column=3, sticky='ew', padx=1, ipady=3)
        
        # Update the scroll region after creating the table
        self._on_frame_configure()

    def on_block_data_change(self, row_index, col_index, new_value):
        """Callback when any block data is changed in maintenance mode"""
        # Update the data model
        self.data.update_block_data(row_index, col_index, new_value)
        
        # Log the change
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        block_num = self.data.block_data[row_index][2]
        
        # Determine which field was changed for logging
        if col_index == 0:
            field_name = "occupancy"
        elif col_index == 3:
            field_name = "fault status"
        else:
            field_name = f"column {col_index}"
        
        if self.log_callback:
            self.log_callback(f"{current_time} UPDATE: Block {block_num} {field_name} changed to '{new_value}' on {self.data.current_line} track")
        
        # Update the current block info display
        self.update_current_block_info()
        
    def filter_block_table(self, *args):
        """Filter block table based on search term"""
        search_term = self.block_search_var.get().lower()
        self.data.filter_block_data(search_term)
        self.create_block_table()  # Recreate table with filtered data
    
    def update_mode_ui(self):
        """Refresh block table when maintenance mode changes"""
        self.create_block_table()           # Recreate table with appropriate editability
        self.update_current_block_info()    # Update current block display
    
    def on_line_changed(self):
        """Refresh right panel when line changes"""
        self.refresh_ui()  # Refresh all UI elements for new line

    # Add this method to your right_panel.py class

    def update_commanded_from_external(self, track, block, speed, authority):
        """Update commanded values from external source (Test UI) without conflict"""
        # Store in both locations for consistency
        self.commanded_authority[track][block] = authority
        self.commanded_speed[track][block] = speed
        
        # Shared data storage for other components
        self.data.commanded_authority[track][block] = authority
        self.data.commanded_speed[track][block] = speed
        
        # Update track_data immediately so PLC can work with it
        block_key = f"Block {block}"
        if hasattr(self.data, 'filtered_blocks') and block_key in self.data.filtered_blocks:
            try:
                # Convert to integers for PLC processing
                self.data.filtered_blocks[block_key]["authority"] = int(authority)
                self.data.filtered_blocks[block_key]["speed"] = int(speed)
            except ValueError:
                # Handle conversion errors gracefully
                print(f"Warning: Could not convert commanded values to integers: {authority}, {speed}")
        
        # Update the display
        self.update_commanded_display()


    def set_yard_to_station_commands(self):
        """Hardcode commanded authority and speed from yard (63) to station (96) and back to yard (57)"""
        current_line = "Green"
        
        # Outbound: Yard (63) to Station (96) - decreasing authority
        blocks_outbound = list(range(63, 97))  # 63 to 96
        authority = len(blocks_outbound) - 1  # Start with full authority
        
        for block_num in blocks_outbound:
            self.commanded_authority[current_line][str(block_num)] = str(authority)
            self.commanded_speed[current_line][str(block_num)] = "31" if authority > 0 else "0"
            authority -= 1
        
        # Return: Station (96) back to Yard (57) - decreasing authority  
        blocks_return = list(range(96, 56, -1))  # 96 down to 57
        authority = len(blocks_return) - 1  # Start with full authority
        
        for block_num in blocks_return:
            self.commanded_authority[current_line][str(block_num)] = str(authority)
            self.commanded_speed[current_line][str(block_num)] = "31" if authority > 0 else "0"
            authority -= 1
        
        # Set final destinations to 0 authority
        self.commanded_authority[current_line]["96"] = "0"  # Station - stop here
        self.commanded_speed[current_line]["96"] = "0"
        
        self.commanded_authority[current_line]["57"] = "0"  # Yard - stop here  
        self.commanded_speed[current_line]["57"] = "0"
        
        print("DEBUG: Hardcoded commanded values set for yard-station route")

    def update_commanded_display(self):
        """Update commanded display with HARDCODED values for section path"""
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line == "Green":
            # HARDCODED VALUES for K->L->M->N->O>P>Q>N>R>s>t>U>V>W>X>Y>Z>F>E>D>C>B>A>D>E>F>G>H>I>yard
            hardcoded_values = {
                # K section (Yard to Dormont)
                "63": {"auth": "33", "speed": "31"},
                "64": {"auth": "32", "speed": "31"},
                "65": {"auth": "31", "speed": "31"},
                "66": {"auth": "30", "speed": "31"},
                "67": {"auth": "29", "speed": "31"},
                "68": {"auth": "28", "speed": "31"},
                
                # L section
                "69": {"auth": "27", "speed": "31"},
                "70": {"auth": "26", "speed": "31"},
                "71": {"auth": "25", "speed": "31"},
                "72": {"auth": "24", "speed": "31"},
                "73": {"auth": "23", "speed": "31"},
            
                # M section
                "74": {"auth": "22", "speed": "31"},
                "75": {"auth": "21", "speed": "31"},
                "76": {"auth": "20", "speed": "31"},
                
                # N section (Mt Lebanon to Poplar)
                "77": {"auth": "19", "speed": "31"},
                "78": {"auth": "18", "speed": "31"},
                "79": {"auth": "17", "speed": "31"},
                "80": {"auth": "16", "speed": "31"},
                "81": {"auth": "15", "speed": "31"},
                "82": {"auth": "14", "speed": "31"},
                "83": {"auth": "13", "speed": "31"},
                "84": {"auth": "12", "speed": "31"},
                "85": {"auth": "11", "speed": "31"},
                
                # O section (Poplar)
                "86": {"auth": "10", "speed": "31"},
                "87": {"auth": "9", "speed": "31"},
                "88": {"auth": "8", "speed": "31"},
                
                # P section (Castle Shannon)
                "89": {"auth": "7", "speed": "31"},
                "90": {"auth": "6", "speed": "31"},
                "91": {"auth": "5", "speed": "31"},
                "92": {"auth": "4", "speed": "31"},
                "93": {"auth": "3", "speed": "31"},
                "94": {"auth": "2", "speed": "31"},
                "95": {"auth": "1", "speed": "31"},
                "96": {"auth": "0", "speed": "31"},
                "97": {"auth": "16", "speed": "31"},
                
                # Q section
                "98": {"auth": "15", "speed": "31"},
                "99": {"auth": "14", "speed": "31"},
                "100": {"auth": "13", "speed": "31"},
                
                # Back through N section
                "85": {"auth": "12", "speed": "31"},  # Back through switch
                "84": {"auth": "11", "speed": "31"},
                "83": {"auth": "10", "speed": "31"},
                
                # R section
                "101": {"auth": "9", "speed": "31"},
                
                # S section
                "102": {"auth": "8", "speed": "31"},
                "103": {"auth": "7", "speed": "31"},
                "104": {"auth": "6", "speed": "31"},
                
                # T section
                "105": {"auth": "5", "speed": "31"},
                "106": {"auth": "4", "speed": "31"},
                "107": {"auth": "3", "speed": "31"},
                "108": {"auth": "2", "speed": "31"},
                "109": {"auth": "1", "speed": "31"},
                
                # U section
                "110": {"auth": "0", "speed": "0"},  # Stop point
                "111": {"auth": "0", "speed": "0"},
                "112": {"auth": "0", "speed": "0"},
                "113": {"auth": "0", "speed": "0"},
                "114": {"auth": "0", "speed": "0"},
                "115": {"auth": "0", "speed": "0"},
                "116": {"auth": "0", "speed": "0"},
                
                # Yard return blocks
                "57": {"auth": "0", "speed": "0"},  # Yard stop
                "58": {"auth": "0", "speed": "0"},
                "59": {"auth": "0", "speed": "0"},
                "60": {"auth": "0", "speed": "0"},
                "61": {"auth": "0", "speed": "0"},
                "62": {"auth": "0", "speed": "0"}
            }
            
            if selected_block in hardcoded_values:
                # Use hardcoded values
                auth = hardcoded_values[selected_block]["auth"]
                speed = hardcoded_values[selected_block]["speed"]
                self.commanded_auth_label.config(text=f"{auth} blocks")
                self.commanded_speed_label.config(text=f"{speed} mph")
            else:
                # For other blocks, show defaults
                self.commanded_auth_label.config(text="0 blocks")
                self.commanded_speed_label.config(text="0 mph")
        else:
            # For other lines or no selection, show defaults
            self.commanded_auth_label.config(text="0 blocks")
            self.commanded_speed_label.config(text="0 mph")