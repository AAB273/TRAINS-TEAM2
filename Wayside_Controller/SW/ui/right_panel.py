import tkinter as tk
from tkinter import ttk
from datetime import datetime

class RightPanel(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d', width=300)
        self.pack_propagate(False)
        self.data = data
        self.log_callback = None
        
        # Initialize current block info first
        self.current_block_info = {}
        # Store commanded values for each block by line
        self.commanded_values = {
            "Blue": {},
            "Green": {}, 
            "Red": {}
        }

        #Store suggested values for each block by line
        self.suggested_values = {
            "Blue": {},
            "Green": {},
            "Red": {}
        }
        
        
        
        # Ensure all blocks have faulted column
        self.ensure_faulted_column()
        
        self.create_widgets()

        # Connect callbacks
        self.data.on_line_change.append(self.on_line_changed)
        self.data.on_data_update.append(self.refresh_ui)
    
    def ensure_faulted_column(self):
        """Ensure all blocks have the Faulted column (index 3)"""
        for row in self.data.block_data:
            if len(row) < 4:
                row.append("No")  # Default to not faulted
        for row in self.data.block_data_original:
            if len(row) < 4:
                row.append("No")  # Default to not faulted
    
    def set_log_callback(self, callback):
        """Set the callback function for logging"""
        self.log_callback = callback
    
    def refresh_ui(self):
        """Refresh all UI elements when data changes"""
        self.update_block_options()
        self.create_block_table()
        self.update_current_block_info()
        self.update_suggested_display()
        self.update_commanded_display()

    def create_widgets(self):
        # Block selector
        block_frame = tk.Frame(self, bg='#cccccc')
        block_frame.pack(fill=tk.X, pady=5)
        tk.Label(block_frame, text="Block", bg='#cccccc').pack(side=tk.LEFT, padx=5)
        
        self.block_combo = ttk.Combobox(block_frame, width=10, state='readonly')
        self.block_combo.pack(side=tk.LEFT, padx=5)
        self.block_combo.bind('<<ComboboxSelected>>', self.on_block_selected)
        
        # Current block info section
        self.create_current_block_section()
        
        # Suggested section
        self.create_suggested_section()
        
        # Commanded Display section
        self.create_commanded_display_section()
        
        # Commanded section (input)
        self.create_commanded_section()
        
        # Search and block table
        self.create_block_table_section()
        
        # Initialize
        self.update_block_options()

    def update_block_options(self):
        """Update block selector based on current line"""
        # row format: [occupied, line, block, faulted]
        blocks = sorted([row[2] for row in self.data.block_data if row[1] == self.data.current_line], key=int)
        self.block_combo['values'] = blocks
        if blocks:
            # Preserve selection if possible
            current_selection = self.block_combo.get()
            if current_selection in blocks:
                self.block_combo.set(current_selection)
            else:
                self.block_combo.set(blocks[0])
            self.update_current_block_info()

    def on_block_selected(self, event):
        """When a new block is selected from dropdown"""
        self.update_current_block_info()
        self.update_suggested_display()
        self.update_commanded_display()

    def update_current_block_info(self):
        """Update the current block information display"""
        selected_block = self.block_combo.get()
        if selected_block:
            # row format: [occupied, line, block, faulted]
            for row in self.data.block_data:
                if row[1] == self.data.current_line and str(row[2]) == str(selected_block):
                    self.current_block_info = {
                        'block': row[2],
                        'line': row[1],
                        'occupied': row[0],
                        'faulted': row[3] if len(row) > 3 else 'No'
                    }
                    self.update_current_block_display()
                    break

    def create_current_block_section(self):
        """Display current selected block information"""
        self.current_block_frame = tk.LabelFrame(self, text="Current Block:", 
                                               bg='#cccccc', font=('Arial', 10, 'bold'))
        self.current_block_frame.pack(fill=tk.X, pady=5)
        
        # Block number
        block_frame = tk.Frame(self.current_block_frame, bg='#cccccc')
        block_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(block_frame, text="Block #:", bg='#cccccc', width=10).pack(side=tk.LEFT)
        self.block_num_label = tk.Label(block_frame, text="", bg='white', width=8,
                                      relief=tk.SUNKEN, anchor='w')
        self.block_num_label.pack(side=tk.LEFT, padx=2)
        
        # Occupied status
        occupied_frame = tk.Frame(self.current_block_frame, bg='#cccccc')
        occupied_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(occupied_frame, text="Occupied:", bg='#cccccc', width=10).pack(side=tk.LEFT)
        self.occupied_label = tk.Label(occupied_frame, text="", bg='white', width=8,
                                     relief=tk.SUNKEN, anchor='w')
        self.occupied_label.pack(side=tk.LEFT, padx=2)
        
        # Faulted status
        faulted_frame = tk.Frame(self.current_block_frame, bg='#cccccc')
        faulted_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(faulted_frame, text="Faulted:", bg='#cccccc', width=10).pack(side=tk.LEFT)
        self.faulted_label = tk.Label(faulted_frame, text="", bg='white', width=8,
                                     relief=tk.SUNKEN, anchor='w')
        self.faulted_label.pack(side=tk.LEFT, padx=2)

    def update_current_block_display(self):
        """Update the current block display with current data"""
        if hasattr(self, 'block_num_label') and hasattr(self, 'occupied_label'):
            if self.current_block_info:
                self.block_num_label.config(text=self.current_block_info['block'])
                
                # Occupied display
                occupied_text = "Yes" if self.current_block_info['occupied'] == "Yes" else "No"
                occupied_color = '#ffcccc' if self.current_block_info['occupied'] == "Yes" else '#ccffcc'
                self.occupied_label.config(text=occupied_text, bg=occupied_color)
                
                # Faulted display
                faulted_text = self.current_block_info.get('faulted', 'No')
                faulted_color = '#ffcccc' if faulted_text == "Yes" else '#ccffcc'
                self.faulted_label.config(text=faulted_text, bg=faulted_color)

    def create_suggested_section(self):
        suggested_frame = tk.LabelFrame(self, text="Suggested:", 
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        suggested_frame.pack(fill=tk.X, pady=5)
        
        # Suggested Authority
        auth_frame = tk.Frame(suggested_frame, bg='#cccccc')
        auth_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(auth_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)
        self.suggested_auth_label = tk.Label(auth_frame, text="0 blocks", bg='white', 
                relief=tk.SUNKEN, width=12, anchor='w')
        self.suggested_auth_label.pack(side=tk.LEFT, padx=2)
        
        # Suggested Speed
        speed_frame = tk.Frame(suggested_frame, bg='#cccccc')
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(speed_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)
        self.suggested_speed_label = tk.Label(speed_frame, text="0 mph", bg='white', 
                relief=tk.SUNKEN, width=12, anchor='w')
        self.suggested_speed_label.pack(side=tk.LEFT, padx=2)

    def update_suggested_display(self):
        """UPDATED: Now shows actual values from Test UI instead of placeholders"""
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line:
            # FIRST priority: Check if we have values from Test UI via shared data
            if hasattr(self.data, 'suggested_values'):
                data_line_values = self.data.suggested_values.get(current_line, {})
                data_block_values = data_line_values.get(selected_block)
                
                if data_block_values:
                    # Use values from Test UI
                    self.suggested_auth_label.config(text=f"{data_block_values['authority']} blocks")
                    self.suggested_speed_label.config(text=f"{data_block_values['speed']} mph")
                    
                    # Also update our local suggested_values to stay in sync
                    if current_line not in self.suggested_values:
                        self.suggested_values[current_line] = {}
                    self.suggested_values[current_line][selected_block] = data_block_values.copy()
                    
                else:
                    # SECOND priority: Check our local storage
                    line_values = self.suggested_values.get(current_line, {})
                    block_values = line_values.get(selected_block)
                    
                    if block_values:
                        # Use manually set suggested values
                        self.suggested_auth_label.config(text=f"{block_values['authority']} blocks")
                        self.suggested_speed_label.config(text=f"{block_values['speed']} mph")
                    else:
                        # No values found - show defaults
                        self.suggested_auth_label.config(text="0 blocks")
                        self.suggested_speed_label.config(text="0 mph")
            else:
                # Fallback to our local storage
                line_values = self.suggested_values.get(current_line, {})
                block_values = line_values.get(selected_block)
                
                if block_values:
                    self.suggested_auth_label.config(text=f"{block_values['authority']} blocks")
                    self.suggested_speed_label.config(text=f"{block_values['speed']} mph")
                else:
                    # No values found anywhere
                    self.suggested_auth_label.config(text="0 blocks")
                    self.suggested_speed_label.config(text="0 mph")
        else:
            self.suggested_auth_label.config(text="N/A")
            self.suggested_speed_label.config(text="N/A")

    def create_commanded_display_section(self):
        """Display the current commanded values for the selected block"""
        self.commanded_display_frame = tk.LabelFrame(self, text="Current Commanded:", 
                                                   bg='#cccccc', font=('Arial', 10, 'bold'))
        self.commanded_display_frame.pack(fill=tk.X, pady=5)
        
        # Commanded Authority Display
        auth_display_frame = tk.Frame(self.commanded_display_frame, bg='#cccccc')
        auth_display_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(auth_display_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)
        self.commanded_auth_label = tk.Label(auth_display_frame, text="0 blocks", bg='#e6f7ff', 
                                           relief=tk.SUNKEN, width=12, anchor='w')
        self.commanded_auth_label.pack(side=tk.LEFT, padx=2)
        
        # Commanded Speed Display
        speed_display_frame = tk.Frame(self.commanded_display_frame, bg='#cccccc')
        speed_display_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(speed_display_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)
        self.commanded_speed_label = tk.Label(speed_display_frame, text="0 mph", bg='#e6f7ff', 
                                            relief=tk.SUNKEN, width=12, anchor='w')
        self.commanded_speed_label.pack(side=tk.LEFT, padx=2)

    def create_commanded_section(self):
        """Input for new commanded values"""
        commanded_frame = tk.LabelFrame(self, text="Set New Command:", 
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        commanded_frame.pack(fill=tk.X, pady=5)
        
        # Commanded Authority
        auth_frame = tk.Frame(commanded_frame, bg='#cccccc')
        auth_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(auth_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)
        
        self.auth_entry = tk.Entry(auth_frame, width=8)
        self.auth_entry.insert(0, "0")
        self.auth_entry.pack(side=tk.LEFT, padx=2)
        
        auth_btn_frame = tk.Frame(auth_frame, bg='#cccccc')
        auth_btn_frame.pack(side=tk.LEFT, padx=2)
        
        tk.Button(auth_btn_frame, text="▲", width=2, 
                 command=lambda: self.increment_auth(1)).pack(side=tk.TOP)
        tk.Button(auth_btn_frame, text="▼", width=2,
                 command=lambda: self.increment_auth(-1)).pack(side=tk.BOTTOM)
        
        # Commanded Speed
        speed_frame = tk.Frame(commanded_frame, bg='#cccccc')
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(speed_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)
        
        self.speed_entry = tk.Entry(speed_frame, width=8)
        self.speed_entry.insert(0, "0")
        self.speed_entry.pack(side=tk.LEFT, padx=2)
        
        speed_btn_frame = tk.Frame(speed_frame, bg='#cccccc')
        speed_btn_frame.pack(side=tk.LEFT, padx=2)
        
        tk.Button(speed_btn_frame, text="▲", width=2,
                 command=lambda: self.increment_speed(1)).pack(side=tk.TOP)
        tk.Button(speed_btn_frame, text="▼", width=2,
                 command=lambda: self.increment_speed(-1)).pack(side=tk.BOTTOM)
        
        # Send Command Button
        send_btn = tk.Button(commanded_frame, text="Send Command", bg='#2e8b57', fg='white',
                           command=self.send_command)
        send_btn.pack(fill=tk.X, padx=5, pady=5)

    def update_commanded_display(self):
        """Update the commanded display with values for current block - FIXED VERSION"""
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line:
            # FIRST priority: Check if we have manually commanded values
            line_values = self.commanded_values.get(current_line, {})
            block_values = line_values.get(selected_block)
            
            if block_values:
                # Use manually commanded values (these should override everything)
                self.commanded_auth_label.config(text=f"{block_values['authority']} blocks")
                self.commanded_speed_label.config(text=f"{block_values['speed']} mph")
                
                # Also ensure these values are in the track_data for PLC
                block_key = f"Block {selected_block}"
                if "blocks" in self.data.filtered_track_data and block_key in self.data.filtered_track_data["blocks"]:
                    try:
                        self.data.filtered_track_data["blocks"][block_key]["authority"] = int(block_values['authority'])
                        self.data.filtered_track_data["blocks"][block_key]["speed"] = int(block_values['speed'])
                    except ValueError:
                        # If conversion fails, keep the string values
                        pass
                
            else:
                # SECOND priority: Check RailwayData commanded_values
                data_line_values = self.data.commanded_values.get(current_line, {})
                data_block_values = data_line_values.get(selected_block)
                
                if data_block_values:
                    # Use values from RailwayData
                    self.commanded_auth_label.config(text=f"{data_block_values['authority']} blocks")
                    self.commanded_speed_label.config(text=f"{data_block_values['speed']} mph")
                    
                    # Also update our local commanded_values to stay in sync
                    if current_line not in self.commanded_values:
                        self.commanded_values[current_line] = {}
                    self.commanded_values[current_line][selected_block] = data_block_values.copy()
                    
                else:
                    # THIRD priority: Fallback to PLC-calculated values
                    block_key = f"Block {selected_block}"
                    track_blocks = self.data.filtered_track_data.get("blocks", {})
                    
                    if block_key in track_blocks:
                        block_data = track_blocks[block_key]
                        authority = block_data.get("authority", 0)
                        speed = block_data.get("speed", 0)
                        
                        self.commanded_auth_label.config(text=f"{authority} blocks")
                        self.commanded_speed_label.config(text=f"{speed} mph")
                    else:
                        # No values found anywhere
                        self.commanded_auth_label.config(text="0 blocks")
                        self.commanded_speed_label.config(text="0 mph")

    def increment_auth(self, delta):
        """Increment/decrement authority value"""
        current = int(self.auth_entry.get())
        new_val = max(0, current + delta)
        self.auth_entry.delete(0, tk.END)
        self.auth_entry.insert(0, str(new_val))

    def increment_speed(self, delta):
        """Increment/decrement speed value"""
        current = int(self.speed_entry.get())
        new_val = max(0, current + delta)
        self.speed_entry.delete(0, tk.END)
        self.speed_entry.insert(0, str(new_val))
        

    def send_command(self):
        """Send commanded speed and authority to train - FIXED VERSION"""
        authority = self.auth_entry.get()
        speed = self.speed_entry.get()
        block = self.block_combo.get()
        current_line = self.data.current_line
        
        if current_line not in self.commanded_values:
            self.commanded_values[current_line] = {}
        
        # Store in BOTH locations for consistency
        self.commanded_values[current_line][block] = {
            "authority": authority,
            "speed": speed
        }
        
        # Also store in RailwayData commanded_values
        if current_line not in self.data.commanded_values:
            self.data.commanded_values[current_line] = {}
        
        self.data.commanded_values[current_line][block] = {
            "authority": authority,
            "speed": speed
        }
        
        # Update track_data immediately so PLC can work with it
        block_key = f"Block {block}"
        if "blocks" in self.data.filtered_track_data and block_key in self.data.filtered_track_data["blocks"]:
            try:
                self.data.filtered_track_data["blocks"][block_key]["authority"] = int(authority)
                self.data.filtered_track_data["blocks"][block_key]["speed"] = int(speed)
            except ValueError:
                # Handle conversion errors
                print(f"Error converting authority/speed to integer: {authority}, {speed}")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} COMMAND: Block {block} on {current_line} - Authority: {authority} blocks, Speed: {speed} mph")

        self.update_commanded_display()
        

    def create_block_table_section(self):
        # Search
        search_frame = tk.Frame(self, bg='#1a1a4d')
        search_frame.pack(fill=tk.X, pady=5)
        self.block_search_var = tk.StringVar()
        self.block_search_var.trace('w', self.filter_block_table)
        block_search = tk.Entry(search_frame, textvariable=self.block_search_var, width=20)
        block_search.pack(side=tk.LEFT, padx=5)
        tk.Label(search_frame, text="Search", bg='#1a1a4d', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Create scrollable table
        table_container = tk.LabelFrame(self, text="Block Status", bg='#1a1a4d', fg='white', font=('Arial', 10, 'bold'))
        table_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        canvas_frame = tk.Frame(table_container, bg='#1a1a4d')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        x_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        y_scrollbar = tk.Scrollbar(canvas_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        self.table_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0,
                                     xscrollcommand=x_scrollbar.set,
                                     yscrollcommand=y_scrollbar.set)
        self.table_canvas.pack(side="left", fill="both", expand=True)
        
        x_scrollbar.config(command=self.table_canvas.xview)
        y_scrollbar.config(command=self.table_canvas.yview)
        
        self.block_table_frame = tk.Frame(self.table_canvas, bg='white')
        self.table_canvas.create_window((0, 0), window=self.block_table_frame, anchor="nw")
        
        self.block_table_frame.bind("<Configure>", self._on_frame_configure)
        self.table_canvas.bind("<Configure>", self._on_canvas_configure)
        self.table_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.block_table_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self.create_block_table()
    
    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        """Reset the canvas window to fill the canvas"""
        self.table_canvas.itemconfig("all", width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for the block table"""
        self.table_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_block_table(self):
        # Clear existing widgets
        for widget in self.block_table_frame.winfo_children():
            widget.destroy()
        
        # Headers using GRID with wider columns
        headers_frame = tk.Frame(self.block_table_frame, bg='#cccccc')
        headers_frame.pack(fill=tk.X)
        
        # Configure grid columns with specific widths
        headers_frame.columnconfigure(0, weight=1, minsize=80)  # Line - wider
        headers_frame.columnconfigure(1, weight=1, minsize=60)  # Block - wider
        headers_frame.columnconfigure(2, weight=1, minsize=80)  # Occupied - wider
        headers_frame.columnconfigure(3, weight=1, minsize=70)  # Faulted - wider
        
        # Header labels using grid with proper width
        tk.Label(headers_frame, text="Line", bg='#cccccc', width=10,
                font=('Arial', 9, 'bold'), anchor='center').grid(row=0, column=0, sticky='ew', padx=1)
        tk.Label(headers_frame, text="Block", bg='#cccccc', width=8,
                font=('Arial', 9, 'bold'), anchor='center').grid(row=0, column=1, sticky='ew', padx=1)
        tk.Label(headers_frame, text="Occupied", bg='#cccccc', width=10,
                font=('Arial', 9, 'bold'), anchor='center').grid(row=0, column=2, sticky='ew', padx=1)
        tk.Label(headers_frame, text="Faulted", bg='#cccccc', width=8,
                font=('Arial', 9, 'bold'), anchor='center').grid(row=0, column=3, sticky='ew', padx=1)
        
        # Data rows - Format: [occupied, line, block, faulted]
        self.block_combos = []
        self.faulted_combos = []
        
        line_blocks = [row for row in self.data.block_data if row[1] == self.data.current_line]
        
        for row_index, row in enumerate(line_blocks):
            row_frame = tk.Frame(self.block_table_frame, bg='white')
            row_frame.pack(fill=tk.X)
            
            # Configure grid columns for this row with same widths as headers
            row_frame.columnconfigure(0, weight=1, minsize=80)
            row_frame.columnconfigure(1, weight=1, minsize=60)
            row_frame.columnconfigure(2, weight=1, minsize=80)
            row_frame.columnconfigure(3, weight=1, minsize=70)
            
            # Get actual index in full block_data
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
                
                # COLUMN 3: OCCUPIED COMBO (editable)
                occ_combo = ttk.Combobox(row_frame, values=["Yes", "No"], 
                                    font=('Arial', 9), width=8,
                                    state="readonly")
                occ_combo.set(row[0])
                occ_combo.grid(row=0, column=2, sticky='ew', padx=1, ipady=2)
                occ_combo.bind('<<ComboboxSelected>>', 
                    lambda event, idx=actual_index, combo=occ_combo: 
                    self.on_block_data_change(idx, 0, combo.get()))
                self.block_combos.append(occ_combo)
                
                # COLUMN 4: FAULTED COMBO (editable)
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
                # NORMAL MODE: All columns are READ-ONLY
                # COLUMN 1: LINE
                bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
                line_label = tk.Label(row_frame, text=row[1], bg=bg_color, fg='white',
                        font=('Arial', 9, 'bold'), width=10,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                line_label.grid(row=0, column=0, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 2: BLOCK
                block_label = tk.Label(row_frame, text=str(row[2]), bg='#2c2c2c', fg='white',
                        font=('Arial', 9, 'bold'), width=8,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                block_label.grid(row=0, column=1, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 3: OCCUPIED
                occupied_color = '#ff6666' if row[0] == "Yes" else '#ccffcc'
                occupied_label = tk.Label(row_frame, text=row[0], bg=occupied_color, fg='black',
                        font=('Arial', 9, 'bold'), width=10,
                        borderwidth=1, relief=tk.RAISED, anchor='center')
                occupied_label.grid(row=0, column=2, sticky='ew', padx=1, ipady=3)
                
                # COLUMN 4: FAULTED
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
        self.data.update_block_data(row_index, col_index, new_value)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        block_num = self.data.block_data[row_index][2]
        
        if col_index == 0:
            field_name = "occupancy"
        elif col_index == 3:
            field_name = "fault status"
        else:
            field_name = f"column {col_index}"
        
        if self.log_callback:
            self.log_callback(f"{current_time} UPDATE: Block {block_num} {field_name} changed to '{new_value}' on {self.data.current_line} track")
        
        self.update_current_block_info()
        
    def filter_block_table(self, *args):
        search_term = self.block_search_var.get().lower()
        self.data.filter_block_data(search_term)
        self.create_block_table()
    
    def update_mode_ui(self):
        """Refresh block table when mode changes"""
        self.create_block_table()
        self.update_current_block_info()
    
    def on_line_changed(self):
        """Refresh right panel when line changes"""
        self.refresh_ui()

#########################################################################
    def update_commanded_from_external(self, track, block, speed, authority):
        """Update commanded values from external sources (like Test UI)"""
        if track == self.data.current_line and block == self.block_combo.get():
            # Update our local storage
            if track not in self.commanded_values:
                self.commanded_values[track] = {}
            
            self.commanded_values[track][block] = {
                "authority": str(authority),
                "speed": str(speed)
            }
            
            # Update the display immediately
            self.update_commanded_display()

    def update_suggested_from_external(self, track, block, speed, authority):
        """Update suggested values from external sources (like Test UI)"""
        if track == self.data.current_line and block == self.block_combo.get():
            # Update our local storage
            if track not in self.suggested_values:
                self.suggested_values[track] = {}
            
            self.suggested_values[track][block] = {
                "authority": str(authority),
                "speed": str(speed)
            }
            
            # Update the display immediately
            self.update_suggested_display()