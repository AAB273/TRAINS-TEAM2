import tkinter as tk
from tkinter import ttk

class CenterPanel(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d')
        self.data = data
        self.create_widgets()

        # Connect line change callback
        self.data.on_line_change.append(self.on_line_changed)
    
    def create_widgets(self):
        # Tab and time
        top_frame = tk.Frame(self, bg='#1a1a4d')
        top_frame.pack(fill=tk.X)
        
        tk.Button(top_frame, text="Main", bg='#cccccc', width=10).pack(side=tk.LEFT)
        tk.Button(top_frame, text="Maintenance", bg='white', width=12).pack(side=tk.LEFT, padx=2)
        
        time_label = tk.Label(top_frame, text="2:15 PM", bg='white', 
                            font=('Arial', 12, 'bold'), width=10)
        time_label.pack(side=tk.RIGHT, padx=10)
        
        # Track diagram canvas
        canvas_frame = tk.Frame(self, bg='white', relief=tk.SUNKEN, borderwidth=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=700, height=540)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Track layout
        self.track_layout()
        
        # Data table with scrollbar
        self.create_fault_table_section()
        
        # Messages section
        self.create_messages_section()
    
    def on_line_changed(self):
        """Handle line changes - update track image and refresh data"""
        self.update_track_image()
        self.create_fault_table()  # Refresh with filtered faults

    def update_track_image(self):
        """Change track image based on selected line"""
        image_files = {
            "Green": "/mnt/c/Users/Home/classes/Fall 2025/Trains/UI Images/GreenRedTrack.png",
            "Red": "/mnt/c/Users/Home/classes/Fall 2025/Trains/UI Images/GreenRedTrack.png", 
            "Blue": "/mnt/c/Users/Home/classes/Fall 2025/Trains/UI Images/BlueTrack.png"
        }
        
        try:
            image_path = image_files.get(self.data.current_line)
            if image_path:
                img = tk.PhotoImage(file=image_path)
                img = img.subsample(2, 2)
                self.track_image = img
                self._draw_centered_image()
        except Exception as e:
            print(f"Could not load track image for {self.data.current_line}: {e}")

    def track_layout(self):
        # Loading the static image of the red and green track
        try:
            image_path = "/mnt/c/Users/Home/classes/Fall 2025/Trains/UI Images/GreenRedTrack.png"
            img = tk.PhotoImage(file=image_path)
            img = img.subsample(2, 2)
            self.track_image = img

            # Draw centered image
            self.canvas.bind("<Configure>", lambda e: self._draw_centered_image())
            self._draw_centered_image()
        except Exception as e:
            print(f"Could not load track image: {e}")
    
    def _draw_centered_image(self):
        """Helper to center the track image on the canvas"""
        if hasattr(self, 'track_image') and self.track_image:
            self.canvas.delete("all")
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            self.canvas.create_image(
                w // 2, h // 2,
                image=self.track_image,
                anchor="center"
            )
    
    def create_fault_table_section(self):
        table_outer_frame = tk.Frame(self, bg='#1a1a4d')
        table_outer_frame.pack(fill=tk.X, pady=5)
        
        # Search bar for fault table
        search_frame = tk.Frame(table_outer_frame, bg='#1a1a4d')
        search_frame.pack(fill=tk.X, pady=2)
        self.fault_search_var = tk.StringVar()
        self.fault_search_var.trace('w', self.filter_fault_table)
        fault_search = tk.Entry(search_frame, textvariable=self.fault_search_var, width=40)
        fault_search.pack(side=tk.LEFT, padx=5)
        tk.Label(search_frame, text="Search faults", bg='#1a1a4d', fg='white').pack(side=tk.LEFT)
        
        table_frame = tk.Frame(table_outer_frame, bg='white', relief=tk.SUNKEN, borderwidth=2, height=150)
        table_frame.pack(fill=tk.X)
        table_frame.pack_propagate(False)
        
        # Create canvas for scrolling
        table_canvas = tk.Canvas(table_frame, bg='white', height=100)
        scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=table_canvas.yview)
        self.fault_table_frame = tk.Frame(table_canvas, bg='white')
        
        self.fault_table_frame.bind("<Configure>", 
                                   lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))
        
        table_canvas.create_window((0, 0), window=self.fault_table_frame, anchor="nw")
        table_canvas.configure(yscrollcommand=scrollbar.set)
        
        table_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_fault_table()
    
    def create_fault_table(self):
        
        # Clear existing widgets
        for widget in self.fault_table_frame.winfo_children():
            widget.destroy()
        
        # Create table headers
        headers = ["Date", "Time", "Track", "Block", "Fault Type", "Status"]
        for i, header in enumerate(headers):
            tk.Label(self.fault_table_frame, text=header, bg='#cccccc', 
                    font=('Arial', 9, 'bold'), borderwidth=1, 
                    relief=tk.RAISED, width=12).grid(row=0, column=i, sticky='ew')
        
        # Data rows
        self.fault_entries = []
        for i, row in enumerate(self.data.fault_data, 1):
            row_entries = []
            for j, value in enumerate(row):
                if self.data.maintenance_mode:

                    #################################################################
                    # Create entry with callback to update data model
                    entry = tk.Entry(self.fault_table_frame, width=12)
                    entry.insert(0, value)
                    entry.grid(row=i, column=j, sticky='ew')
                    
                    # Bind focus out to save changes
                    entry.bind('<FocusOut>', lambda e, row_idx=i-1, col_idx=j: 
                            self.on_fault_data_change(row_idx, col_idx, e.widget.get()))
                    row_entries.append(entry)
                    ####################################################################
                    """"
                    entry = tk.Entry(self.fault_table_frame, width=12)
                    entry.insert(0, value)
                    entry.grid(row=i, column=j, sticky='ew')
                    row_entries.append(entry)
                    """
                else:
                    label = tk.Label(self.fault_table_frame, text=value, bg='white', 
                                    borderwidth=1, relief=tk.GROOVE, width=12)
                    label.grid(row=i, column=j, sticky='ew')
                    row_entries.append(label)
            self.fault_entries.append(row_entries)

    ##################################################################################
    def on_fault_data_change(self, row_index, col_index, new_value):
        """Callback when fault data is edited in maintenance mode"""
        self.data.update_fault_data(row_index, col_index, new_value)
    ##################################################################################

    def filter_fault_table(self, *args):
        search_term = self.fault_search_var.get().lower()
        self.data.filter_fault_data(search_term)
        self.create_fault_table()
    
    def create_messages_section(self):
        msg_frame = tk.LabelFrame(self, text="Messages", bg='#cccccc', 
                                 font=('Arial', 10, 'bold'))
        msg_frame.pack(fill=tk.BOTH, pady=5)
        
        msg_text = tk.Text(msg_frame, height=6, bg='white', font=('Arial', 8))
        msg_text.pack(fill=tk.BOTH, padx=5, pady=5)
        
        messages = [
            "$ railwaycli maintenance --disable",
            "2025-09-17 15:12:43 INFO: Re-enabling automatic train routing...",
            "2025-09-17 15:12:44 INFO: Re-enabling automatic train routing...",
            "2025-09-17 15:12:45 INFO: System returning to NORMAL OPERATION mode.",
            "2025-09-17 15:12:46 INFO: Maintenance mode deactivated."
        ]
        msg_text.insert('1.0', '\n'.join(messages))
        msg_text.config(state='disabled')
    
    def update_mode_ui(self):
        self.create_fault_table()