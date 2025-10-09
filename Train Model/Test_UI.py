import tkinter as tk
from tkinter import ttk
import socket
import json
from datetime import datetime

class TestUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Control Panel")
        self.root.geometry("400x1100")  # Increased width to accommodate log
        
        self.socket = None
        if self.connect_to_server():
            self.create_widgets()
        else:
            # Show error and retry button
            error_frame = tk.Frame(self.root)
            error_frame.pack(expand=True)
            tk.Label(error_frame, text="Failed to connect to Main UI", fg='red').pack()
            tk.Button(error_frame, text="Retry", command=self.retry_connection).pack()
        
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # 5 second timeout
            self.socket.connect(('localhost', 12345))
            print("Connected to Train GUI")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def retry_connection(self):
        # Clear the window and try again
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__()
                
    def send_command(self, command, value=None):
        """Send a command to the main GUI"""
        if self.socket:
            try:
                message = {'command': command, 'value': value}
                json_message = json.dumps(message)
                self.socket.send(json_message.encode('utf-8'))
                
                # Log the command to terminal instead of UI log
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {command}: {value}"
                self.log_to_terminal(log_entry)  # Changed this line
                
                print(f"Sent: {json_message}")
                self.status_label.config(text=f"Sent: {command} {value}")
            except Exception as e:
                error_msg = f"Send failed: {e}"
                self.log_to_terminal(f"[ERROR] {error_msg}")  # Changed this line
                print(f"Send failed: {e}")
                self.status_label.config(text=error_msg)
    
    def log_to_terminal(self, log_entry):
        """Print log entry to terminal instead of UI log"""
        print(f"TEST UI LOG: {log_entry}")
    
    def log_command(self, log_entry):
        """Add a command to the log (kept for compatibility)"""
        # Now just prints to terminal
        self.log_to_terminal(log_entry)
        
    def create_widgets(self):
        # Create main container with left and right frames
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left frame for controls
        left_frame = tk.Frame(main_container)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Right frame for log (keeping the structure but it will show terminal instructions)
        right_frame = tk.Frame(main_container, width=250)  # Fixed width for log
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        right_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # ===== LEFT FRAME CONTROLS =====
        
        # Train Deployment Section
        deployment_frame = ttk.LabelFrame(left_frame, text="Train Deployment", padding=10)
        deployment_frame.pack(fill='x', padx=10, pady=5)
        
        # Train selection for deployment
        deploy_select_frame = tk.Frame(deployment_frame)
        deploy_select_frame.pack(fill='x', pady=5)
        
        tk.Label(deploy_select_frame, text="Train:").pack(side='left')
        self.deploy_train_var = tk.IntVar(value=1)
        deploy_spinbox = tk.Spinbox(deploy_select_frame, from_=1, to=14, textvariable=self.deploy_train_var, width=5)
        deploy_spinbox.pack(side='left', padx=5)
        
        # Deployment controls
        deploy_control_frame = tk.Frame(deployment_frame)
        deploy_control_frame.pack(fill='x', pady=5)
        
        ttk.Button(deploy_control_frame, text="Deploy Train", 
                  command=self.deploy_train).pack(side='left', padx=2)
        ttk.Button(deploy_control_frame, text="Undeploy Train", 
                  command=self.undeploy_train).pack(side='left', padx=2)
        
        # Bulk deployment controls
        bulk_frame = tk.Frame(deployment_frame)
        bulk_frame.pack(fill='x', pady=5)
        
        ttk.Button(bulk_frame, text="Deploy All Trains", 
                  command=lambda: self.bulk_deploy(True)).pack(side='left', padx=2)
        ttk.Button(bulk_frame, text="Undeploy All Trains", 
                  command=lambda: self.bulk_deploy(False)).pack(side='left', padx=2)
        
        # Power Control
        power_frame = ttk.LabelFrame(left_frame, text="Power Control", padding=10)
        power_frame.pack(fill='x', padx=10, pady=5)
        
        # Custom power entry
        custom_power_frame = tk.Frame(power_frame)
        custom_power_frame.pack(fill='x', pady=5)
        
        tk.Label(custom_power_frame, text="Custom:").pack(side='left')
        self.custom_power_var = tk.StringVar(value="1000")
        custom_power_entry = tk.Entry(custom_power_frame, textvariable=self.custom_power_var, width=8)
        custom_power_entry.pack(side='left', padx=2)
        ttk.Button(custom_power_frame, text="Set", 
                  command=self.set_custom_power).pack(side='left', padx=2)
        
        # Door Control
        door_frame = ttk.LabelFrame(left_frame, text="Door Control", padding=10)
        door_frame.pack(fill='x', padx=10, pady=5)
        
        top_door_frame = ttk.LabelFrame(door_frame,text="Right Door")
        top_door_frame.pack(side='top')
        ttk.Button(top_door_frame, text="Open", 
                  command=lambda: self.send_command('set_right_door', 'open')).pack(side='left', padx=2)
        ttk.Button(top_door_frame, text="Close", 
                  command=lambda: self.send_command('set_right_door', 'close')).pack(side='left', padx=2)
        
        bottom_door_frame = ttk.LabelFrame(door_frame,text="Left Door")
        bottom_door_frame.pack(side='top')
        ttk.Button(bottom_door_frame, text="Open", 
                  command=lambda: self.send_command('set_left_door', 'open')).pack(side='left', padx=2)
        ttk.Button(bottom_door_frame, text="Close", 
                  command=lambda: self.send_command('set_left_door', 'close')).pack(side='left', padx=2)

        # Light Control
        light_frame = ttk.LabelFrame(left_frame, text="Light Control", padding=10)
        light_frame.pack(fill='x', padx=10, pady=5)
        
        light_frame_top = ttk.LabelFrame(light_frame,text = "Headlights")
        light_frame_top.pack(side='top')
        ttk.Button(light_frame_top, text="Turn On", 
                  command=lambda: self.send_command('set_headlights', 'on')).pack(side='left', padx=2)
        ttk.Button(light_frame_top, text="Turn Off", 
                  command=lambda: self.send_command('set_headlights', 'off')).pack(side='left', padx=2)
        
        light_frame_bottom = ttk.LabelFrame(light_frame,text="Interior Cabin Lights")
        light_frame_bottom.pack(side='top')
        ttk.Button(light_frame_bottom, text="Turn On", 
                  command=lambda: self.send_command('set_interior_lights', 'on')).pack(side='left', padx=2)
        ttk.Button(light_frame_bottom, text="Turn Off", 
                  command=lambda: self.send_command('set_interior_lights', 'off')).pack(side='left', padx=2)
        
        # Temp Control
        temp_frame = ttk.LabelFrame(left_frame, text="Interior Cabin Temperature Control", padding=10)
        temp_frame.pack(fill='x',padx=10,pady=5)
        spinbox = ttk.Spinbox(temp_frame,from_= 64, to=75)
        spinbox.pack(padx=5,pady=5)
        ttk.Button(temp_frame,text="Send Temperature",
                                 command=lambda: self.send_command('set_temperature',spinbox.get())).pack(padx=2)

        # Station Announcement
        announcement_frame = ttk.LabelFrame(left_frame, text="Station Announcement",padding=10)
        announcement_frame.pack(fill='x',padx=10,pady=10)

        station_options = ["A","B"]
        station_var = tk.StringVar()
        time_options = ["1","2","3","4","5","6"]
        time_var = tk.StringVar()

        dropdown = ttk.Combobox(announcement_frame, textvariable=station_var, values=station_options,width=10)
        dropdown.pack(pady=10,side='left')
        time_dropdown = ttk.Combobox(announcement_frame, textvariable=time_var, values=time_options,width =10)
        time_dropdown.pack(pady=10,side='left')

        ttk.Button(announcement_frame,text="Send Announcement",
                                 command=lambda: [
                                     self.send_command('set_station',station_var.get()),
                                     self.send_command('set_time_to_station',time_var.get())
                                    ]).pack(padx=2,side='right')
        
        # Activating Brakes
        service_brake_frame = ttk.LabelFrame(left_frame,text="Service Brake Control",padding=10)
        service_brake_frame.pack(fill='x',padx=10,pady=10)

        ttk.Button(service_brake_frame,text="Activate",
                                 command=lambda: self.send_command('set_service_brake','on')).pack(padx=2,side='left')
        ttk.Button(service_brake_frame,text="Deactivate",
                                 command=lambda: self.send_command('set_service_brake','off')).pack(padx=2,side='left')
        
        ttk.Button(left_frame,text="Emergency Brake Deactivation",
                                                command=lambda: self.send_command('emergency_brake','off')).pack(padx=2)
        
        # Status label at bottom of left frame
        self.status_label = tk.Label(left_frame, text="Ready", relief='sunken', bd=1)
        self.status_label.pack(fill='x', padx=10, pady=5, side='bottom')

        # FIXED: This was a duplicate section with wrong variable name
        passenger_frame = ttk.LabelFrame(left_frame, text="Passenger Count Control", padding=10)  
        passenger_frame.pack(fill='x',padx=10,pady=5)
        passenger_spinbox = ttk.Spinbox(passenger_frame, from_=0, to=222) 
        passenger_spinbox.pack(padx=5,pady=5)
        ttk.Button(passenger_frame,text="Set Passenger Count",  
                                 command=lambda: self.send_command('set_passenger_count',passenger_spinbox.get())).pack(padx=2)
        """
        # ===== RIGHT FRAME LOG =====
        
        # Log title - now shows it's going to terminal
        log_title = tk.Label(right_frame, text="Logs → Terminal", font=('Arial', 12, 'bold'))
        log_title.pack(pady=(5, 0))
        
        # Info frame explaining where logs go
        info_frame = tk.Frame(right_frame, relief='sunken', bd=1, bg='#f0f0f0')
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        info_text = tk.Text(
            info_frame, 
            height=30, 
            width=30, 
            state=tk.NORMAL,
            font=('Arial', 10),
            wrap=tk.WORD,
            bg='#f0f0f0',
            relief='flat'
        )
        info_text.pack(side='left', fill='both', expand=True)
        
      
        info_text.insert(tk.END, instructions)
        info_text.config(state=tk.DISABLED)
        
        # Clear terminal button instead of clear log
        clear_button = ttk.Button(right_frame, text="Clear Terminal", command=self.clear_terminal_display)
        clear_button.pack(pady=5)
        
        # Add initial log entry to terminal
        self.log_to_terminal("Test UI initialized - All logs going to terminal")
        
    def clear_terminal_display(self):
        Print a separator to 'clear' the terminal visually
        print("\n" + "="*50)
        print("TERMINAL CLEARED (Visual separator)")
        print("="*50 + "\n")
        self.log_to_terminal("Terminal display cleared")
"""
    def deploy_train(self):
        """Deploy a specific train"""
        train_id = self.deploy_train_var.get()
        self.send_command('deploy_train', train_id)
        self.status_label.config(text=f"Deployed Train {train_id}")
        
    def undeploy_train(self):
        """Undeploy a specific train"""
        train_id = self.deploy_train_var.get()
        self.send_command('undeploy_train', train_id)
        self.status_label.config(text=f"Undeployed Train {train_id}")
        
    def bulk_deploy(self, deploy=True):
        """Deploy or undeploy all trains"""
        action = "deploy_all" if deploy else "undeploy_all"
        self.send_command(action)
        self.status_label.config(text=f"{'Deployed' if deploy else 'Undeployed'} All Trains")
        
    def set_custom_power(self):
        """Set custom power value"""
        try:
            power = int(self.custom_power_var.get())
            self.send_command('set_power', power)
            self.status_label.config(text=f"Set power to {power}")
        except ValueError:
            self.status_label.config(text="Invalid power value")
            
    def refresh_train_list(self):
        """Refresh the list of deployed trains"""
        self.send_command('refresh_trains')
        self.status_label.config(text="Refreshing train list...")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestUI()
    app.run()