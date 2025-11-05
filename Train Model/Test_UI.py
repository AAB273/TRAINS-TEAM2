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
        self.root.geometry("460x910")
        
        self.server = TrainSocketServer(port=12346, ui_id="Test_UI")
        self.server.set_allowed_connections(["Train_Model_Passenger_UI", "ui_3"])
        
        # Start server with minimal handler
        def empty_handler(message, source_ui_id):
            print(f"Test UI received: {message} from {source_ui_id}")
        
        self.server.start_server(empty_handler)
        self.server.connect_to_ui('localhost', 12345, "Train_Model_Passenger_UI")
        
        self.create_widgets()
        #else:
            # Show error and retry button
        #    error_frame = tk.Frame(self.root)
         #   error_frame.pack(expand=True)
        ##    tk.Label(error_frame, text="Failed to connect to Main UI", fg='red').pack()
        #    tk.Button(error_frame, text="Retry", command=self.retry_connection).pack()
    
    def send_to_ui(self, command, value=None):
        """Send command to the target UI (creates dict for socket server)"""
        message = {'command': command}
        if value is not None:
            message['value'] = value
        
        # Always send to Train_Model_Passenger_UI
        target_ui = "Train_Model_Passenger_UI"
        success = self.server.send_to_ui(target_ui, message)
        
        if success:
            print(f"Sent {command} to {target_ui}")
            self.status_label.config(text=f"Sent: {command}")
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
        
    def create_widgets(self):
        # Create main container without scrolling
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # ===== MAIN CONTROLS =====
        
        # Train Deployment Section - Compact layout
        deployment_frame = ttk.LabelFrame(main_container, text="Train Deployment", padding=6)
        deployment_frame.pack(fill='x', padx=5, pady=2)
        
        # Train selection and controls in one row
        deploy_control_frame = tk.Frame(deployment_frame)
        deploy_control_frame.pack(fill='x', pady=2)
        
        tk.Label(deploy_control_frame, text="Train:").pack(side='left')
        self.deploy_train_var = tk.IntVar(value=1)
        deploy_spinbox = tk.Spinbox(deploy_control_frame, from_=1, to=14, textvariable=self.deploy_train_var, width=4)
        deploy_spinbox.pack(side='left', padx=2)
        
        ttk.Button(deploy_control_frame, text="Deploy", 
                  command=self.deploy_train, width=7).pack(side='left', padx=1)
        ttk.Button(deploy_control_frame, text="Undeploy", 
                  command=self.undeploy_train, width=7).pack(side='left', padx=1)
        
        # Power Control - Compact
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
        
        # Door Control - Compact side-by-side layout
        door_frame = ttk.LabelFrame(main_container, text="Door Control", padding=6)
        door_frame.pack(fill='x', padx=5, pady=2)
        
        door_row_frame = tk.Frame(door_frame)
        door_row_frame.pack(fill='x', pady=2)
        
        # Right Door
        right_door_frame = tk.Frame(door_row_frame)
        right_door_frame.pack(side='left', padx=3)
        tk.Label(right_door_frame, text="Right:").pack()
        door_btn_frame1 = tk.Frame(right_door_frame)
        door_btn_frame1.pack()
        ttk.Button(door_btn_frame1, text="Open", 
                  command=lambda: self.send_to_ui('set_right_door', 'open'), width=5).pack(side='left', padx=1)
        ttk.Button(door_btn_frame1, text="Close", 
                  command=lambda: self.send_to_ui('set_right_door', 'close'), width=5).pack(side='left', padx=1)
        
        # Left Door
        left_door_frame = tk.Frame(door_row_frame)
        left_door_frame.pack(side='left', padx=3)
        tk.Label(left_door_frame, text="Left:").pack()
        door_btn_frame2 = tk.Frame(left_door_frame)
        door_btn_frame2.pack()
        ttk.Button(door_btn_frame2, text="Open", 
                  command=lambda: self.send_to_ui('set_left_door', 'open'), width=5).pack(side='left', padx=1)
        ttk.Button(door_btn_frame2, text="Close", 
                  command=lambda: self.send_to_ui('set_left_door', 'close'), width=5).pack(side='left', padx=1)
        
        #State Control
        states_frame = ttk.LabelFrame(main_container, text="Train State Control", padding=6)
        states_frame.pack(fill='x', padx=5, pady=2)
        
        state_leaving_station = tk.Frame(states_frame)
        state_leaving_station.pack(fill='x', pady=2)
        
        ttk.Button(state_leaving_station, text="Leaving Station",
                   command=lambda:[self.send_to_ui('set_headlights','on'), self.send_to_ui('set_left_door','close'),
                                   self.send_to_ui('set_right_door','close')]).pack(side='left')
        
        # Temp Control - Compact
        temp_frame = ttk.LabelFrame(main_container, text="Temperature Control", padding=6)
        temp_frame.pack(fill='x', padx=5, pady=2)
        
        temp_control_frame = tk.Frame(temp_frame)
        temp_control_frame.pack(fill='x', pady=2)
        
        tk.Label(temp_control_frame, text="Temp (64-75):").pack(side='left')
        self.temp_spinbox = ttk.Spinbox(temp_control_frame, from_=64, to=75, width=4)
        self.temp_spinbox.pack(side='left', padx=2)
        ttk.Button(temp_control_frame, text="Set", 
                  command=lambda: self.send_to_ui('set_temperature', self.temp_spinbox.get()), width=5).pack(side='left', padx=2)

        # Station Announcement - Compact
        announcement_frame = ttk.LabelFrame(main_container, text="Station Announcement", padding=6)
        announcement_frame.pack(fill='x', padx=5, pady=2)

        announcement_control_frame = tk.Frame(announcement_frame)
        announcement_control_frame.pack(fill='x', pady=2)

        station_options = ["A","B"]
        self.station_var = tk.StringVar()
        time_options = ["1","2","3","4","5","6"]
        self.time_var = tk.StringVar()

        tk.Label(announcement_control_frame, text="Station:").pack(side='left')
        station_dropdown = ttk.Combobox(announcement_control_frame, textvariable=self.station_var, 
                                       values=station_options, width=3, state="readonly")
        station_dropdown.pack(side='left', padx=2)
        
        tk.Label(announcement_control_frame, text="Time:").pack(side='left')
        time_dropdown = ttk.Combobox(announcement_control_frame, textvariable=self.time_var, 
                                    values=time_options, width=3, state="readonly")
        time_dropdown.pack(side='left', padx=2)

        ttk.Button(announcement_control_frame, text="Send", width=6,
                  command=lambda: [
                      self.send_to_ui('set_station', self.station_var.get()),
                      self.send_to_ui('set_time_to_station', self.time_var.get())
                  ]).pack(side='left', padx=2)
        
        # Service Brake Control - Compact
        service_brake_frame = ttk.LabelFrame(main_container, text="Service Brake", padding=6)
        service_brake_frame.pack(fill='x', padx=5, pady=2)

        brake_control_frame = tk.Frame(service_brake_frame)
        brake_control_frame.pack(fill='x', pady=2)

        ttk.Button(brake_control_frame, text="Activate", width=8,
                  command=lambda: self.send_to_ui('set_service_brake','on')).pack(side='left', padx=2)
        ttk.Button(brake_control_frame, text="Deactivate", width=8,
                  command=lambda: self.send_to_ui('set_service_brake','off')).pack(side='left', padx=2)
        
        # Emergency Brake
        emergency_frame = tk.Frame(main_container)
        emergency_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(emergency_frame, text="Emergency Brake Deactivate", width=22,
                  command=lambda: self.send_to_ui('emergency_brake','off')).pack(pady=2)
        
        # Passenger Count Control - Compact
        passenger_frame = ttk.LabelFrame(main_container, text="Passenger Count", padding=6)  
        passenger_frame.pack(fill='x', padx=5, pady=2)
        
        passenger_control_frame = tk.Frame(passenger_frame)
        passenger_control_frame.pack(fill='x', pady=2)
        
        tk.Label(passenger_control_frame, text="Count (0-222):").pack(side='left')
        self.passenger_spinbox = ttk.Spinbox(passenger_control_frame, from_=0, to=222, width=4)
        self.passenger_spinbox.pack(side='left', padx=2)
        ttk.Button(passenger_control_frame, text="Set", width=5,
                  command=lambda: self.send_to_ui('set_passenger_count', self.passenger_spinbox.get())).pack(side='left', padx=2)
        

        
        # Beacon Data Control - Compact grid layout with individual buttons
        beacon_data_frame = ttk.LabelFrame(main_container, text="Beacon Data", padding=6)
        beacon_data_frame.pack(fill='x', padx=5, pady=2)
        
        # Input fields row
        beacon_input_frame = tk.Frame(beacon_data_frame)
        beacon_input_frame.pack(fill='x', pady=2)
        
        # Grade
        grade_frame = tk.Frame(beacon_input_frame)
        grade_frame.pack(side='left', padx=2)
        tk.Label(grade_frame, text="Grade %:").pack()
        self.grade_var = tk.StringVar()
        grade_entry = ttk.Entry(grade_frame, textvariable=self.grade_var, width=6)
        grade_entry.pack()
        
        # Speed Limit
        speed_frame = tk.Frame(beacon_input_frame)
        speed_frame.pack(side='left', padx=2)
        tk.Label(speed_frame, text="Speed Limit (MPH):").pack()
        self.speed_limit_var = tk.StringVar()
        speed_entry = ttk.Entry(speed_frame, textvariable=self.speed_limit_var, width=6)
        speed_entry.pack()
        
        # Elevation
        elevation_frame = tk.Frame(beacon_input_frame)
        elevation_frame.pack(side='left', padx=2)
        tk.Label(elevation_frame, text='Elevation (ft):').pack()
        self.elevation_var = tk.StringVar()
        elevation_entry = ttk.Entry(elevation_frame, textvariable=self.elevation_var, width=8)
        elevation_entry.pack()
        
        # Individual beacon buttons in a compact row
        beacon_buttons_frame = tk.Frame(beacon_data_frame)
        beacon_buttons_frame.pack(fill='x', pady=2)
        
        ttk.Button(beacon_buttons_frame, text="Send Grade", width=12,
                  command=lambda: self.send_to_ui('set_grade', self.grade_var.get())).pack(side='left', padx=1)
        ttk.Button(beacon_buttons_frame, text="Send Speed Limit", width=12,
                  command=lambda: self.send_to_ui('set_speed_limit', self.speed_limit_var.get())).pack(side='left', padx=1)
        ttk.Button(beacon_buttons_frame, text="Send Elevation", width=12,
                  command=lambda: self.send_to_ui('set_elevation', self.elevation_var.get())).pack(side='left', padx=1)
        
        #Train 
        train_horn = ttk.Button(main_container,text="Train Horn", command=lambda:self.send_to_ui("Train_Model_Passenger_UI", "horn"))
        train_horn.pack(fill='x',padx=5,pady=5)
        # Status label at bottom
        status_frame = tk.Frame(main_container)
        status_frame.pack(fill='x', padx=5, pady=3)
        self.status_label = tk.Label(status_frame, text="Ready", relief='sunken', bd=1, anchor='w')
        self.status_label.pack(fill='x', ipady=2)



    def deploy_train(self):
        """Deploy a specific train"""
        train_id = self.deploy_train_var.get()
        self.send_to_ui('deploy_train', train_id)
        self.status_label.config(text=f"Deployed Train {train_id}")
        
    def undeploy_train(self):
        """Undeploy a specific train"""
        train_id = self.deploy_train_var.get()
        self.send_to_ui('undeploy_train', train_id)
        self.status_label.config(text=f"Undeployed Train {train_id}")
        
    def bulk_deploy(self, deploy=True):
        """Deploy or undeploy all trains"""
        action = "deploy_all" if deploy else "undeploy_all"
        self.send_to_ui(action)
        self.status_label.config(text=f"{'Deployed' if deploy else 'Undeployed'} All Trains")
        
    def set_custom_power(self):
        """Set custom power value"""
        try:
            power = int(self.custom_power_var.get())
            self.send_to_ui('set_power', power)
            self.status_label.config(text=f"Set power to {power}")
        except ValueError:
            self.status_label.config(text="Invalid power value")
            
    def refresh_train_list(self):
        """Refresh the list of deployed trains"""
        self.send_to_ui('refresh_trains')
        self.status_label.config(text="Refreshing train list...")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestUI()
    app.run()