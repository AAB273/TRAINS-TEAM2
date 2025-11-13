import tkinter as tk
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from ui_test.system_log import SystemLog
from ui_test.track_controls import TrackControls
from ui_test.system_monitoring import SystemMonitoring
from ui_test.speed_authority import SpeedAuthorityControl
from ui_test.header import Header
from config.track_config import TrackConfig 
from TrainSocketServer import TrainSocketServer

class RailwayControlSystem:
    def __init__(self, root, shared_data=None):
        self.root = root
        self.root.title("Wayside Controller - Test Interface")
        self.root.geometry("1200x750")
        self.root.configure(bg="#1a1a4d")
        
        # Load track configuration
        self.track_config = TrackConfig()
        
        # Initialize socket server for test UI - FIXED PORT NUMBER
        self.server = TrainSocketServer(port=22342, ui_id="test_ui") 
        self.server.set_allowed_connections(["Track SW"])
        
        # Store shared data reference (if any)
        self.shared_data = shared_data
        
        # Initialize UI components
        self.create_ui()
        
        # Set up log callback
        self.setup_logging()
        
        # Start server with message handler
        self.server.start_server(self._process_message)
        
        # Set up window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("Test UI ready with socket communication")
        
    def _process_message(self, message, source_ui_id):
        """Process incoming messages from Main UI"""
        print(f"Test UI received from {source_ui_id}: {message}")

    def send_to_main_ui(self, message):
        """Send message to Main UI"""
        return self.server.send_to_ui("Track SW", message)

    def on_closing(self):
        """Handle application closing"""
        print("Closing Test UI...")
        self.server.stop_server()
        self.root.destroy()

    def create_ui(self):
        # Create header
        self.header = Header(self.root, self.track_config)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f0f0f5")
        main_frame.pack(fill='both', expand=True, padx=15, pady=8)
        
        # Create ONE SystemLog instance
        self.system_log = SystemLog(main_frame, self)
        
        # Row 1: Speed & Authority + Switches + System Log
        control_row1 = tk.Frame(main_frame, bg="#f0f0f5")
        control_row1.pack(fill='x', pady=3)
        
        self.speed_auth = SpeedAuthorityControl(control_row1, self.track_config)
        self.track_controls = TrackControls(control_row1, self.track_config)
        
        # Row 2: Lights + Crossing
        control_row2 = tk.Frame(main_frame, bg="#f0f0f5")
        control_row2.pack(fill='x', pady=3)
        
        self.system_monitoring = SystemMonitoring(control_row2, self.track_config)
        
        # Connect ALL components to the SAME SystemLog
        self.track_controls.set_log_callback(self.system_log.add_log_entry)
        self.system_monitoring.set_log_callback(self.system_log.add_log_entry)
        self.speed_auth.set_log_callback(self.system_log.add_log_entry)
        
        # Also connect the SystemLog to update shared data AND send socket messages
        self.system_log.set_log_callback(self.add_to_log)
        
        # Connect to Main UI after UI is created
        self.root.after(1000, self._connect_to_main_ui)

    def _connect_to_main_ui(self):
        """Connect to Main UI server"""
        if self.server.connect_to_ui('localhost', 12342, "Track SW"):  # Main UI port
            print("Connected to Main UI")
        else:
            print("Failed to connect to Main UI - make sure Main UI is running")

    def setup_logging(self):
        pass
    
    def add_to_log(self, message):
        print(f"TEST UI LOG: {message}")
        
        # Parse the log message and send appropriate socket message
        self._parse_and_send_log_message(message)
        
        # If we have shared data, update it (for backward compatibility)
        if self.shared_data:
            self.update_shared_data_from_log(message)
    
    def _parse_and_send_log_message(self, log_message):
        """Parse log message and send appropriate socket command"""
        try:
            if "SWITCH:" in log_message:
                parts = log_message.split("SWITCH: Set to ")
                if len(parts) > 1:
                    switch_info = parts[1].split(" on ")
                    switch_direction = switch_info[0]
                    track_block = switch_info[1].split(" track, Block ")
                    track = track_block[0]
                    block = track_block[1]
                    
                    # Send socket message
                    message = {
                        'command': 'update_switch',
                        'value': {
                            'track': track,
                            'block': block,
                            'direction': switch_direction
                        }
                    }
                    self.send_to_main_ui(message)
                    
            elif "LIGHTS:" in log_message:
                parts = log_message.split("LIGHTS: Set to ")
                if len(parts) > 1:
                    light_info = parts[1].split(" on ")
                    light_color = light_info[0]
                    track_block = light_info[1].split(" track, Block ")
                    track = track_block[0]
                    block = track_block[1]
                    
                    message = {
                        'command': 'update_light',
                        'value': {
                            'track': track,
                            'block': block,
                            'color': light_color
                        }
                    }
                    self.send_to_main_ui(message)
                    
            elif "CROSSING:" in log_message:
                parts = log_message.split("CROSSING: Set - ")
                if len(parts) > 1:
                    crossing_info = parts[1].split(" on ")
                    settings = crossing_info[0]
                    track_block = crossing_info[1].split(" track, Block ")
                    track = track_block[0]
                    block = track_block[1]
                    
                    lights_setting = settings.split("Lights: ")[1].split(", Crossbar: ")[0]
                    crossbar_setting = settings.split("Crossbar: ")[1]
                    
                    message = {
                        'command': 'update_crossing',
                        'value': {
                            'track': track,
                            'block': block,
                            'lights': lights_setting,
                            'crossbar': crossbar_setting
                        }
                    }
                    self.send_to_main_ui(message)
                    
            elif "SPEED:" in log_message or "AUTHORITY:" in log_message:
                # Handle speed/authority updates
                self._send_speed_auth_updates(log_message)
                
            elif "OCCUPANCY:" in log_message:
                # Handle occupancy updates
                self._send_occupancy_updates(log_message)
                
        except Exception as e:
            print(f"Error parsing log message: {e}")
    
    def _send_speed_auth_updates(self, log_message):
        """Send speed and authority updates"""
        try:
            # Parse the log message to determine what type of update this is
            if "suggested" in log_message.lower():
                value_type = 'suggested'
                track = self.speed_auth.suggested_track_var.get()
                block = self.speed_auth.suggested_block_var.get()
                speed = self.speed_auth.suggested_speed_var.get()
                authority = self.speed_auth.suggested_auth_var.get()
            else:
                value_type = 'commanded'
                track = self.speed_auth.commanded_track_var.get()
                block = self.speed_auth.commanded_block_var.get()
                speed = self.speed_auth.commanded_speed_var.get()
                authority = self.speed_auth.commanded_auth_var.get()
            
            message = { 'command': 'update_speed_auth', 'value': {
                    'track': track,
                    'block': block,
                    'speed': speed,
                    'authority': authority,
                    'value_type': value_type
                }
            }
            self.send_to_main_ui(message)
            
        except Exception as e:
            print(f"Error sending speed/auth update: {e}")
    
    def _send_occupancy_updates(self, log_message):
        """Send occupancy updates"""
        try:
            track = self.speed_auth.commanded_track_var.get()
            block = self.speed_auth.commanded_block_var.get()
            
            # Parse occupancy status from log message
            if "Occupied" in log_message:
                occupied = True
            elif "Unoccupied" in log_message:
                occupied = False
            else:
                # Get from current state
                block_data = self.speed_auth.get_block_data(track, block)
                occupied = block_data.get('occupied', False)
            
            message = {
                'command': 'update_occupancy',
                'value': {
                    'track': track,
                    'block': block,
                    'occupied': occupied
                }
            }
            self.send_to_main_ui(message)
            
        except Exception as e:
            print(f"Error sending occupancy update: {e}")
    
    def update_shared_data_from_log(self, log_message):
        """Legacy method - keep for backward compatibility"""
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()