import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui_test.system_log import SystemLog

class CenterPanel(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d')
        self.data = data
        self.log_callback = None  # Direct callback for logging
        
        self.create_widgets()

        # Connect line change callback
        self.data.on_line_change.append(self.on_line_changed)
        self.data.on_data_update.append(self.refresh_ui)
    
    def set_log_callback(self, callback):
        """Set the callback function for logging"""
        self.log_callback = callback
    
    def refresh_ui(self):
        """Called externally to refresh all UI elements."""
        self._draw_centered_image()  # redraw track image

    def create_widgets(self):
        # Tab and time
        top_frame = tk.Frame(self, bg='#1a1a4d')
        top_frame.pack(fill=tk.X)
        
        tk.Button(top_frame, text="Main", bg="#ffffff", width=10).pack(side=tk.LEFT)
        
        # Create time label
        self.time_label = tk.Label(top_frame, text="", bg='white', 
                                 font=('Arial', 12, 'bold'), width=10)
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # Start the clock
        self.update_clock()
        
        # Track diagram canvas
        canvas_frame = tk.Frame(self, bg='white', relief=tk.SUNKEN, borderwidth=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=700, height=540)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Track layout - load initial image based on current line
        self.track_layout()
        
        # Messages section - Using SystemLog
        self.create_messages_section()
    
    def update_clock(self):
        """Update the time display every second"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        # Update every 1000 milliseconds (1 second)
        self.after(1000, self.update_clock)
    
    def on_line_changed(self):
        """Handle line changes - update track image and refresh data"""
        self.update_track_image()
        # Log line change using direct callback
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} INFO: Line changed to {self.data.current_line}")

    def update_track_image(self):
        """Change track image based on selected line"""
        image_files = {
            "Green": "Wayside_Controller/SW/data/Red and Green Line.png",
            "Red": "Wayside_Controller/SW/data/Red and Green Line.png", 
            "Blue": "Wayside_Controller/SW/data/Blue Line.png"
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
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} ERROR: Could not load track image for {self.data.current_line}")

    def track_layout(self):
        """Load the initial track image based on current line"""
        image_files = {
            "Green": "Wayside_Controller/SW/data/Red and Green Line.png",
            "Red": "Wayside_Controller/SW/data/Red and Green Line.png", 
            "Blue": "Wayside_Controller/SW/data/Blue Line.png"
        }
        
        try:
            image_path = image_files.get(self.data.current_line, 
                                       "Wayside_Controller/SW/data/Red and Green Line.png")
            img = tk.PhotoImage(file=image_path)
            img = img.subsample(2, 2)
            self.track_image = img

            # Draw centered image
            self.canvas.bind("<Configure>", lambda e: self._draw_centered_image())
            self._draw_centered_image()
        except Exception as e:
            print(f"Could not load track image: {e}")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} ERROR: Could not load track image")
    
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
    
    def create_messages_section(self):
        """Create system log using your SystemLog class"""
        # Create a frame for the system log
        msg_frame = tk.Frame(self, bg='#1a1a4d')
        msg_frame.pack(fill=tk.X, pady=(0, 8))

        # Make SystemLog smaller so it fits better in the main UI
        self.system_log = SystemLog(msg_frame)
        self.system_log.log_text.config(height=8) 
        
        # Set our callback to use the system log directly (NO RECURSION)
        self.set_log_callback(self.system_log.add_log_entry)
        
        # Initialize with startup message - USING DIRECT CALLBACK
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} SYSTEM: Wayside Controller initialized and ready")
            self.log_callback(f"{current_time} INFO: Current line set to {self.data.current_line}")
    
    def update_mode_ui(self):
        """Refresh UI when mode changes"""
        mode_name = "MAINTENANCE" if self.data.maintenance_mode else "NORMAL OPERATION"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_callback:
            self.log_callback(f"{current_time} SYSTEM: Mode changed to {mode_name}")