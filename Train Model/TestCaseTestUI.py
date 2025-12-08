import tkinter as tk
from tkinter import ttk
import json
import os, sys
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from TrainSocketServer import TrainSocketServer
from datetime import datetime

class TestUI:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Control Panel")
        self.root.geometry("460x800")
        
        self.server = TrainSocketServer(port=12349, ui_id="Test_UI")
        self.server.set_allowed_connections(["Train Model", "ui_3"])
        
        # Start server with minimal handler
        def empty_handler(message, source_ui_id):
            print(f"Test UI received: {message} from {source_ui_id}")
        
        self.server.start_server(empty_handler)
        self.server.connect_to_ui('localhost', 12345, "Train Model")
        
        # Initialize with train 1 selected
        self.selected_train_id = 1
        
        self.create_widgets()
        
    def send_to_ui(self, command, value=None):
        """Send command to the target UI with selected train ID"""
        message = {'command': command}
        if value is not None:
            message['value'] = value
        
        # Always include the selected train ID in the message
        message['train_id'] = self.selected_train_id
        
        # Always send to Train_Model_Passenger_UI
        target_ui = "Train Model"
        success = self.server.send_to_ui(target_ui, message)
        
        if success:
            print(f"Sent {command} to {target_ui} for train {self.selected_train_id}")
            self.status_label.config(text=f"Sent: {command} to Train {self.selected_train_id}")
        else:
            print(f"Failed to send {command} to {target_ui}")
            self.status_label.config(text=f"Failed: {command}")
        return success
    
    def log_to_terminal(self, log_entry):
        """Print log entry to terminal instead of UI log"""
        print(f"TEST UI LOG: {log_entry}")
    
    def log_command(self, log_entry):
        """Add a command to the log (kept for compatibility)"""
        self.log_to_terminal(log_entry)
    
    def on_train_selected(self, event=None):
        """Handle train selection from dropdown"""
        train_str = self.train_selector_var.get()
        if train_str and train_str != "No Train Selected":
            try:
                train_id = int(train_str)
                self.selected_train_id = train_id
                self.status_label.config(text=f"Selected: Train {train_id}")
                self.current_selection_label.config(text=f"Currently controlling: Train {train_id}")
                print(f"Selected Train {train_id}")
            except ValueError:
                print(f"Invalid train selection: {train_str}")
    
    def create_widgets(self):
        # Create main container without scrolling
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # ===== TRAIN SELECTION SECTION =====
        selection_frame = ttk.LabelFrame(main_container, text="Train Selection", padding=6)
        selection_frame.pack(fill='x', padx=5, pady=2)
        
        # Train selector dropdown
        selector_frame = tk.Frame(selection_frame)
        selector_frame.pack(fill='x', pady=2)
        
        tk.Label(selector_frame, text="Select Train:").pack(side='left', padx=(0, 5))
        
        # Create train list (1-14)
        train_options = [str(i) for i in range(1, 15)]  # Convert to strings for combobox
        self.train_selector_var = tk.StringVar(value=train_options[0])
        self.train_selector = ttk.Combobox(selector_frame, textvariable=self.train_selector_var, 
                                          values=train_options, state="readonly", width=10)
        self.train_selector.pack(side='left')
        self.train_selector.bind('<<ComboboxSelected>>', self.on_train_selected)
        
        # Current selection display
        current_frame = tk.Frame(selection_frame)
        current_frame.pack(fill='x', pady=2)
        self.current_selection_label = tk.Label(current_frame, text=f"Currently controlling: Train {self.train_selector_var.get()}", 
                                                font=('Arial', 9, 'bold'))
        self.current_selection_label.pack()
        
        # ===== POWER CONTROL =====
        power_frame = ttk.LabelFrame(main_container, text="Power Control", padding=6)
        power_frame.pack(fill='x', padx=5, pady=2)
        
        power_control_frame = tk.Frame(power_frame)
        power_control_frame.pack(fill='x', pady=2)
        
        tk.Label(power_control_frame, text="Custom:").pack(side='left')
        self.custom_power_var = tk.StringVar(value="1000")
        custom_power_entry = tk.Entry(power_control_frame, textvariable=self.custom_power_var, width=6)
        custom_power_entry.pack(side='left', padx=2)
        ttk.Button(power_control_frame, text="Set", 
                  command=self.set_custom_power, width=5).pack(side='left', padx=2)
        
        # ===== AUTHORITY CONTROL =====
        authority_frame = ttk.LabelFrame(main_container, text="Authority Control", padding=6)
        authority_frame.pack(fill='x', padx=5, pady=2)
        
        authority_control_frame = tk.Frame(authority_frame)
        authority_control_frame.pack(fill='x', pady=2)
        
        tk.Label(authority_control_frame, text="Authority (ft):").pack(side='left')
        self.custom_authority_var = tk.StringVar(value="100")
        custom_authority_entry = tk.Entry(authority_control_frame, textvariable=self.custom_authority_var, width=6)
        custom_authority_entry.pack(side='left', padx=2)
        ttk.Button(authority_control_frame, text="Set", 
                  command=self.set_custom_authority, width=5).pack(side='left', padx=2)
        
        # ===== COMMANDED SPEED CONTROL =====
        speed_frame = ttk.LabelFrame(main_container, text="Commanded Speed Control", padding=6)
        speed_frame.pack(fill='x', padx=5, pady=2)
        
        speed_control_frame = tk.Frame(speed_frame)
        speed_control_frame.pack(fill='x', pady=2)
        
        tk.Label(speed_control_frame, text="Speed (MPH):").pack(side='left')
        self.commanded_speed_var = tk.StringVar(value="0")
        speed_entry = tk.Entry(speed_control_frame, textvariable=self.commanded_speed_var, width=6)
        speed_entry.pack(side='left', padx=2)
        ttk.Button(speed_control_frame, text="Send", 
                  command=self.send_commanded_speed, width=6).pack(side='left', padx=2)
        
        # ===== BLOCK OCCUPANCY =====
        block_frame = ttk.LabelFrame(main_container, text="Block Occupancy", padding=6)
        block_frame.pack(fill='x', padx=5, pady=2)
        
        block_control_frame = tk.Frame(block_frame)
        block_control_frame.pack(fill='x', pady=2)
        
        tk.Label(block_control_frame, text="Block Number:").pack(side='left')
        self.block_var = tk.StringVar(value="63")
        block_entry = tk.Entry(block_control_frame, textvariable=self.block_var, width=6)
        block_entry.pack(side='left', padx=2)
        ttk.Button(block_control_frame, text="Set", 
                  command=self.set_block, width=5).pack(side='left', padx=2)
        
        # ===== SERVICE BRAKE CONTROL =====
        service_brake_frame = ttk.LabelFrame(main_container, text="Service Brake", padding=6)
        service_brake_frame.pack(fill='x', padx=5, pady=2)

        brake_control_frame = tk.Frame(service_brake_frame)
        brake_control_frame.pack(fill='x', pady=2)

        ttk.Button(brake_control_frame, text="Activate", width=8,
                  command=lambda: self.send_to_ui('set_service_brake', True)).pack(side='left', padx=2)
        ttk.Button(brake_control_frame, text="Deactivate", width=8,
                  command=lambda: self.send_to_ui('set_service_brake', False)).pack(side='left', padx=2)
        
        # ===== EMERGENCY BRAKE =====
        emergency_frame = tk.Frame(main_container)
        emergency_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(emergency_frame, text="EMERGENCY BRAKE (Activate)", width=22,
                  command=lambda: self.send_to_ui('set_emergency_brake', True)).pack(pady=2)
        ttk.Button(emergency_frame, text="Emergency Brake (Deactivate)", width=22,
                  command=lambda: self.send_to_ui('set_emergency_brake', False)).pack(pady=2)
        
        # ===== DOORS CONTROL =====
        doors_frame = ttk.LabelFrame(main_container, text="Doors", padding=6)
        doors_frame.pack(fill='x', padx=5, pady=2)
        
        left_door_frame = tk.Frame(doors_frame)
        left_door_frame.pack(fill='x', pady=2)
        tk.Label(left_door_frame, text="Left Door:").pack(side='left', padx=(0, 5))
        ttk.Button(left_door_frame, text="Open", width=6,
                  command=lambda: self.send_to_ui('set_left_door', True)).pack(side='left', padx=2)
        ttk.Button(left_door_frame, text="Close", width=6,
                  command=lambda: self.send_to_ui('set_left_door', False)).pack(side='left', padx=2)
        
        right_door_frame = tk.Frame(doors_frame)
        right_door_frame.pack(fill='x', pady=2)
        tk.Label(right_door_frame, text="Right Door:").pack(side='left', padx=(0, 5))
        ttk.Button(right_door_frame, text="Open", width=6,
                  command=lambda: self.send_to_ui('set_right_door', True)).pack(side='left', padx=2)
        ttk.Button(right_door_frame, text="Close", width=6,
                  command=lambda: self.send_to_ui('set_right_door', False)).pack(side='left', padx=2)
        
        # ===== LIGHTS CONTROL =====
        lights_frame = ttk.LabelFrame(main_container, text="Lights", padding=6)
        lights_frame.pack(fill='x', padx=5, pady=2)
        
        headlights_frame = tk.Frame(lights_frame)
        headlights_frame.pack(fill='x', pady=2)
        tk.Label(headlights_frame, text="Headlights:").pack(side='left', padx=(0, 5))
        ttk.Button(headlights_frame, text="On", width=6,
                  command=lambda: self.send_to_ui('set_headlights', True)).pack(side='left', padx=2)
        ttk.Button(headlights_frame, text="Off", width=6,
                  command=lambda: self.send_to_ui('set_headlights', False)).pack(side='left', padx=2)
        
        interior_frame = tk.Frame(lights_frame)
        interior_frame.pack(fill='x', pady=2)
        tk.Label(interior_frame, text="Interior Lights:").pack(side='left', padx=(0, 5))
        ttk.Button(interior_frame, text="On", width=6,
                  command=lambda: self.send_to_ui('set_interior_lights', True)).pack(side='left', padx=2)
        ttk.Button(interior_frame, text="Off", width=6,
                  command=lambda: self.send_to_ui('set_interior_lights', False)).pack(side='left', padx=2)
        
        # ===== TRAIN HORN =====
        train_horn = ttk.Button(main_container, text="Train Horn", 
                               command=lambda: self.send_to_ui("horn"))
        train_horn.pack(fill='x', padx=5, pady=5)
        
        # ===== SPEED PRESETS =====
        speed_preset_frame = ttk.LabelFrame(main_container, text="Speed Presets", padding=6)
        speed_preset_frame.pack(fill='x', padx=5, pady=2)
        
        speed_buttons_frame = tk.Frame(speed_preset_frame)
        speed_buttons_frame.pack(fill='x', pady=2)
        
        speed_options = [10, 20, 30, 40, 50, 60]
        for speed in speed_options:
            ttk.Button(speed_buttons_frame, text=f"{speed} MPH", width=8,
                      command=lambda s=speed: self.send_to_ui('set_commanded_speed', s)).pack(side='left', padx=1)
        
        # ===== STATUS LABEL =====
        status_frame = tk.Frame(main_container)
        status_frame.pack(fill='x', padx=5, pady=3)
        self.status_label = tk.Label(status_frame, text=f"Ready - Controlling Train {self.selected_train_id}", 
                                     relief='sunken', bd=1, anchor='w')
        self.status_label.pack(fill='x', ipady=2)

    def send_commanded_speed(self):
        """Send commanded speed value"""
        try:
            speed = float(self.commanded_speed_var.get())
            self.send_to_ui('set_commanded_speed', speed)
            self.status_label.config(text=f"Set commanded speed to {speed} MPH for Train {self.selected_train_id}")
        except ValueError:
            self.status_label.config(text="Invalid speed value")
        
    def set_custom_power(self):
        """Set custom power value"""
        try:
            power = int(self.custom_power_var.get())
            self.send_to_ui('set_power', power)
            self.status_label.config(text=f"Set power to {power} for Train {self.selected_train_id}")
        except ValueError:
            self.status_label.config(text="Invalid power value")
            
    def set_custom_authority(self):
        """Set custom authority value"""
        try:
            authority = int(self.custom_authority_var.get())
            self.send_to_ui('set_authority', authority)
            self.status_label.config(text=f"Set authority to {authority} ft for Train {self.selected_train_id}")
        except ValueError:
            self.status_label.config(text="Invalid authority value")
    
    def set_block(self):
        """Set block occupancy"""
        try:
            block = int(self.block_var.get())
            self.send_to_ui('set_block', block)
            self.status_label.config(text=f"Set block to {block} for Train {self.selected_train_id}")
        except ValueError:
            self.status_label.config(text="Invalid block value")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestUI()
    app.run()