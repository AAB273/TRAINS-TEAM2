import tkinter as tk
from tkinter import ttk
import socket
import json

class TestUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Control Panel")
        self.root.geometry("450x700")
        
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
                print(f"Sent: {json_message}")
                self.status_label.config(text=f"Sent: {command} {value}")
            except Exception as e:
                print(f"Send failed: {e}")
                self.status_label.config(text=f"Send failed: {e}")
        
    def create_widgets(self):
        # Train Deployment Section
        deployment_frame = ttk.LabelFrame(self.root, text="Train Deployment", padding=10)
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
        power_frame = ttk.LabelFrame(self.root, text="Power Control", padding=10)
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
        door_frame = ttk.LabelFrame(self.root, text="Door Control", padding=10)
        door_frame.pack(fill='x', padx=10, pady=5)
        
        top_door_frame = ttk.LabelFrame(door_frame,text="Right Door")
        top_door_frame.pack(side='top')
        ttk.Button(top_door_frame, text="Open Right Door", 
                  command=lambda: self.send_command('set_right_door', 'open')).pack(side='left', padx=2)
        ttk.Button(top_door_frame, text="Close Right Door", 
                  command=lambda: self.send_command('set_right_door', 'close')).pack(side='left', padx=2)
        
        bottom_door_frame = ttk.LabelFrame(door_frame,text="Left Door")
        bottom_door_frame.pack(side='top')
        ttk.Button(bottom_door_frame, text="Open Left Door", 
                  command=lambda: self.send_command('set_left_door', 'open')).pack(side='left', padx=2)
        ttk.Button(bottom_door_frame, text="Close Left Door", 
                  command=lambda: self.send_command('set_left_door', 'close')).pack(side='left', padx=2)

        # Light Control
        light_frame = ttk.LabelFrame(self.root, text="Light Control", padding=10)
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
        
        #Temp Control
        temp_frame = ttk.LabelFrame(self.root, text="Interior Cabin Temperature Control", padding=10)
        temp_frame.pack(fill='x',padx=10,pady=5)
        spinbox = ttk.Spinbox(temp_frame,from_= 64, to=75)
        spinbox.pack(padx=5,pady=5)
        ttk.Button(temp_frame,text="Send Temperature",
                                 command=lambda: self.send_command('set_temperature',spinbox.get())).pack(padx=2)

        
        
        """
        # Refresh button to update deployed trains list
        refresh_frame = tk.Frame(self.root)
        refresh_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(refresh_frame, text="Refresh Train List", 
                  command=self.refresh_train_list).pack()
        """
        #Status label
        self.status_label = tk.Label(self.root, text="Ready", relief='sunken', bd=1)
        self.status_label.pack(fill='x', padx=10, pady=5)

        

    def test_connection(self):
        """Test if the connection is working"""
        self.send_command('test')
        self.status_label.config(text="Sent test command")
        
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