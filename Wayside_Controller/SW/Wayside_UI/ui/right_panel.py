import tkinter as tk
from tkinter import ttk

class RightPanel(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d', width=250)
        self.pack_propagate(False)
        self.data = data
        self.create_widgets()

        # Connect line change callback
        self.data.on_line_change.append(self.on_line_changed)
    
    def create_widgets(self):
        
        #DELETE TABS HERE
        """
        # Tab buttons
        tab_frame = tk.Frame(self, bg='#1a1a4d')
        tab_frame.pack(fill=tk.X)
        
        tk.Button(tab_frame, text="Blue", bg='#cccccc', width=8).pack(side=tk.LEFT)
        tk.Button(tab_frame, text="Green", bg='#66cc66', width=8).pack(side=tk.LEFT)
        tk.Button(tab_frame, text="Red", bg='#cccccc', width=8).pack(side=tk.LEFT)
        """
        # Block selector
        block_frame = tk.Frame(self, bg='#cccccc')
        block_frame.pack(fill=tk.X, pady=5)
        tk.Label(block_frame, text="Block", bg='#cccccc').pack(side=tk.LEFT, padx=5)
        
        # Update block combo based on current line
        self.block_combo = ttk.Combobox(block_frame, width=10, state='readonly')
        self.block_combo.pack(side=tk.LEFT, padx=5)
        self.update_block_options()

        """
        combo = ttk.Combobox(block_frame, width=10, values=list(range(1, 21)))
        combo.set("15")
        combo.pack(side=tk.LEFT, padx=5)
        """
        # Suggested section
        self.create_suggested_section()
        
        # Commanded section
        self.create_commanded_section()
        
        # Search and block table
        self.create_block_table_section()

    def update_block_options(self):
        """Update block selector based on current line"""
        blocks = [row[2] for row in self.data.block_data]
        self.block_combo['values'] = blocks
        if blocks:
            self.block_combo.set(blocks[0])
    
    def on_line_changed(self):
        """Refresh right panel when line changes"""
        print(f"Right panel: Line changed to {self.data.current_line}")  # Debug
        self.update_block_options()
        self.create_block_table()
    
    def create_suggested_section(self):
        suggested_frame = tk.LabelFrame(self, text="Suggested:", 
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        suggested_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(suggested_frame, text="Authority:", bg='#cccccc').pack(anchor='w', padx=5)
        tk.Label(suggested_frame, text="2 blocks", bg='white', 
                relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=2)
        tk.Label(suggested_frame, text="Speed:", bg='#cccccc').pack(anchor='w', padx=5)
        tk.Label(suggested_frame, text="38 mph", bg='white', 
                relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=2)
    
    def create_commanded_section(self):
        commanded_frame = tk.LabelFrame(self, text="Commanded:", 
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        commanded_frame.pack(fill=tk.X, pady=5)
        
        auth_frame = tk.Frame(commanded_frame, bg='#cccccc')
        auth_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(auth_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)
        tk.Entry(auth_frame, width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(auth_frame, text="↕", width=2).pack(side=tk.LEFT)
        
        speed_frame = tk.Frame(commanded_frame, bg='#cccccc')
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(speed_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)
        tk.Entry(speed_frame, width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(speed_frame, text="↕", width=2).pack(side=tk.LEFT)
    
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
        table_container = tk.Frame(self, bg='white', relief=tk.SUNKEN, borderwidth=2)
        table_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas for scrolling
        canvas = tk.Canvas(table_container, bg='white')
        scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        self.block_table_frame = tk.Frame(canvas, bg='white')
        
        self.block_table_frame.bind("<Configure>", 
                                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.block_table_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_block_table()
    
    def create_block_table(self):
        # Clear existing widgets
        for widget in self.block_table_frame.winfo_children():
            widget.destroy()
        
        # Headers
        headers_frame = tk.Frame(self.block_table_frame, bg='#cccccc')
        headers_frame.pack(fill=tk.X)
        
        tk.Label(headers_frame, text="Occupied", bg='#cccccc', 
                font=('Arial', 8, 'bold'), width=10).pack(side=tk.LEFT)
        tk.Label(headers_frame, text="Line", bg='#cccccc', 
                font=('Arial', 8, 'bold'), width=8).pack(side=tk.LEFT)
        tk.Label(headers_frame, text="Block", bg='#cccccc', 
                font=('Arial', 8, 'bold'), width=8).pack(side=tk.LEFT)
        
        # Data rows - MOVE THE LOOP OUTSIDE THE MODE CHECK
        self.block_combos = []  # Store references to comboboxes
        
        # Loop through all block data
        for row_index, row in enumerate(self.data.block_data):
            row_frame = tk.Frame(self.block_table_frame, bg='white')
            row_frame.pack(fill=tk.X)
            
            if self.data.maintenance_mode:
                # Editable in maintenance mode - OCCUPIED COMBO
                occ_combo = ttk.Combobox(row_frame, values=["Yes", "No"], width=9)
                occ_combo.set(row[0])
                occ_combo.pack(side=tk.LEFT)

                # Bind the change event to update data model
                occ_combo.bind('<<ComboboxSelected>>', 
                    lambda event, idx=row_index, combo=occ_combo:  # idx=row_index captures current value
                    self.on_block_data_change(idx, 0, combo.get()))
                
                # LINE - READ ONLY (track color should not change)
                bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
                tk.Label(row_frame, text=row[1], bg=bg_color, width=8, 
                        borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT)
                
                # Block number (read-only)
                tk.Label(row_frame, text=row[2], bg='white', width=8, 
                        borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT)
                
                # Store combos for potential access
                self.block_combos.append(occ_combo)
                
            else:
                # Read-only in normal mode - shows current data from model
                # FIXED: row is now defined because we're in the same loop
                tk.Label(row_frame, text=row[0], bg='white', width=10, 
                        borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT)
                bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
                tk.Label(row_frame, text=row[1], bg=bg_color, width=8, 
                        borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT)
                tk.Label(row_frame, text=row[2], bg='white', width=8, 
                        borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT)

    def on_block_data_change(self, row_index, col_index, new_value):
        """Callback when any block data is changed in maintenance mode"""
        print(f"Block data changed: row {row_index}, col {col_index}, value '{new_value}'")
        self.data.update_block_data(row_index, col_index, new_value)
        
    def filter_block_table(self, *args):
        search_term = self.block_search_var.get().lower()
        self.data.filter_block_data(search_term)
        self.create_block_table()
    
    def update_mode_ui(self):
        """Refresh block table when mode changes"""
        self.create_block_table()