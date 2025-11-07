import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class Header(tk.Frame):
    def __init__(self, parent, data, app=None):
        super().__init__(parent, bg='#1a1a4d', height=80)
        self.pack_propagate(False)
        self.data = data
        self.app = app  # Store the app reference
        
        self.create_widgets()
        
        # Connect callbacks for line changes and data updates
        self.data.on_line_change.append(self.update_fault_led)
        self.data.on_data_update.append(self.update_fault_led)

    def set_log_callback(self, callback):
        """Set the callback function for logging - JUST LIKE YOUR TEST PANEL"""
        self.log_callback = callback
    
    def create_widgets(self):
        # Logo
        logo_img = tk.PhotoImage(file="blt logo.png")
        logo_img_small = logo_img.subsample(12, 12)
        logo_label = tk.Label(self, image=logo_img_small, bg='#4a7c8c')
        logo_label.image = logo_img_small
        logo_label.pack(side=tk.LEFT, padx=5)

        # CENTRALIZED LINE TABS - These control the entire UI
        self.create_line_tabs()

        # Fault LED
        self.fault_led = tk.Label(self, text="Fault", bg='#666666',  # Default to gray (no fault)
                                 fg='white', width=10, height=3, font=('Arial', 10, 'bold'))
        self.fault_led.pack(side=tk.LEFT, padx=5)
        
        # Right side indicators with toggles
        self.create_mode_controls()

        # Maintenance Call Button
        self.create_maintenance_call_button()
        
        # Initial LED update
        self.update_fault_led()

    def update_fault_led(self):
        """Update the Fault LED based on whether any block on the current line is faulted"""
        current_line = self.data.current_line
        has_fault = any(
            row[1] == current_line and row[3] == "Yes"
            for row in self.data.block_data
            if len(row) > 3  # Ensure faulted column exists
        )
        
        # Update LED color: red for fault, gray for no fault
        if has_fault:
            self.fault_led.config(bg='#cc3333')  # Red for fault
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} ALERT: Fault detected on {current_line} line")
        else:
            self.fault_led.config(bg='#666666')  # Gray for no fault

    def create_maintenance_call_button(self):
        """Create maintenance call button with alert functionality"""
        maintenance_frame = tk.Frame(self, bg='#1a1a4d')
        maintenance_frame.pack(side=tk.RIGHT, padx=10)
        
        # Maintenance Call Button
        self.maintenance_button = tk.Button(
            maintenance_frame, 
            text="Maintenance Call", 
            bg='#ff6b35',  # Orange-red color for urgency
            fg='white',
            font=('Arial', 11, 'bold'),
            width=15,
            height=2,
            command=self.request_maintenance
        )
        self.maintenance_button.pack(pady=5)
    
    def request_maintenance(self):
        """Handle maintenance call request"""
        response = messagebox.askyesno(
            "Maintenance Call",
            "Are you sure you want to request maintenance?\n\n"
            "This will alert the maintenance team and log the request.",
            icon='warning'
        )
        if response:
            # Log the action
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.log_callback:
                self.log_callback(f"{current_time} ALERT: Maintenance call requested")
            
            print(f"MAINTENANCE CALL: Request sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show confirmation
            messagebox.showinfo(
                "Maintenance Call Sent",
                "Maintenance team has been alerted.\n"
                "They will respond to your location shortly."
            )
            
    def create_mode_controls(self):
        right_frame = tk.Frame(self, bg='#1a1a4d')
        right_frame.pack(side=tk.RIGHT, padx=10)
        
        # MM LED with toggle
        mm_frame = tk.Frame(right_frame, bg='#1a1a4d')
        mm_frame.pack(side=tk.LEFT, padx=5)
        self.mm_led = tk.Label(mm_frame, text="MM", bg='#666666', fg='white',
                               width=8, height=2, font=('Arial', 10, 'bold'))
        self.mm_led.pack()
        self.mm_toggle = tk.Checkbutton(mm_frame, bg='#1a1a4d', activebackground='#1a1a4d',
                                       command=self.toggle_maintenance)
        self.mm_toggle.pack()

    def toggle_maintenance(self):
        new_mode = not self.data.maintenance_mode
        self.data.set_maintenance_mode(new_mode)
        
        # Log the action
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if new_mode:
            self.mm_led.config(bg='#ffaa33')
            if self.log_callback:
                self.log_callback(f"{current_time} SYSTEM: Maintenance mode activated")
        else:
            self.mm_led.config(bg='#666666')
            if self.log_callback:
                self.log_callback(f"{current_time} SYSTEM: Maintenance mode deactivated")
    

    def create_line_tabs(self):
        """Create centralized line tabs that sync across the UI"""
        tab_frame = tk.Frame(self, bg='#1a1a4d')
        tab_frame.pack(side=tk.LEFT, padx=20)
        
        # Create tab buttons with commands
        self.blue_tab = tk.Button(tab_frame, text="Blue", bg='#6666ff', width=8,
                                 command=lambda: self.data.set_current_line("Blue"))
        self.blue_tab.pack(side=tk.LEFT)
        
        self.green_tab = tk.Button(tab_frame, text="Green", bg='#66cc66', width=8,
                                  command=lambda: self.data.set_current_line("Green"))
        self.green_tab.pack(side=tk.LEFT)
        
        self.red_tab = tk.Button(tab_frame, text="Red", bg='#ff6666', width=8,
                                command=lambda: self.data.set_current_line("Red"))
        self.red_tab.pack(side=tk.LEFT)
        
        # Set initial active tab
        self.update_tab_appearance()
        
        # Connect callback for when line changes
        self.data.on_line_change.append(self.update_tab_appearance)

    def set_line(self, line):
        """Set the current line and update all UI components"""
        print(f"Setting line to: {line}")
        self.data.set_current_line(line)
        self.data.filter_data_by_line(line)
    
    def update_tab_appearance(self):
        """Update tab colors to show active line"""
        active_bg = {'Blue': '#3366ff', 'Green': '#33aa33', 'Red': '#ff3333'}
        inactive_bg = {'Blue': "#a8a8ee", 'Green': "#aadaaa", 'Red': "#eb9595"}
        
        current = self.data.current_line
        print(f"Updating tab appearance for: {current}")
        
        self.blue_tab.config(bg=active_bg['Blue'] if current == "Blue" else inactive_bg['Blue'])
        self.green_tab.config(bg=active_bg['Green'] if current == "Green" else inactive_bg['Green'])
        self.red_tab.config(bg=active_bg['Red'] if current == "Red" else inactive_bg['Red'])