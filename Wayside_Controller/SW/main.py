import json          
from pathlib import Path  
import tkinter as tk
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from ui.header import Header
from ui.left_panel import LeftPanel
from ui.center_panel import CenterPanel
from ui.right_panel import RightPanel
from data.models import RailwayData
from TrainSocketServer import TrainSocketServer

def load_socket_config():  
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("modules", {})
    return {}

class RailwayControlSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Wayside Controller")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a4d')
        
        self.data = RailwayData()

        # Add this line - gives RailwayData a reference to the main app
        self.data.app = self
        
        # Load socket configuration first
        module_config = load_socket_config().get("Track SW", {"port": 2})
        
        # Initialize socket server with the loaded configuration
        self.server = TrainSocketServer(
            port=module_config["port"],
            ui_id="Track SW"
        )

        # FIX: Set ALL allowed connections in ONE call
        self.server.set_allowed_connections(["test_ui", "Track Model", "CTC"])
        self.server.start_server(self._process_message)
        
        # FIX: Connect with correct parameters
        self.server.connect_to_ui('localhost', 22342, "test_ui")
        self.server.connect_to_ui('localhost', 12341, "CTC")
        self.server.connect_to_ui('localhost', 12344, "Track Model")

        self.create_ui()
        self.setup_logging()
        
        # Set up window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _process_message(self, message, source_ui_id):
        """Process incoming messages from Test UI"""
        try:
            print(f"Main UI received from {source_ui_id}: {message}")
            
            command = message.get('command')
            data = message.get('value', {})
            
            if command == 'update_switch':
                self._handle_switch_update(data)
            elif command == 'update_light':
                self._handle_light_update(data)
            elif command == 'update_crossing':
                self._handle_crossing_update(data)
            elif command == 'update_speed_auth':
                self._handle_speed_auth_update(data)
            elif command == 'update_occupancy':
                self._handle_occupancy_update(data)
                
        except Exception as e:
            print(f"Error processing message: {e}")

    def send_commanded_to_track_model(self, track, block, speed, authority):
        """Send commanded speed and authority to Track Model"""
        track_model_message = {
            "command": "Speed and Authority",
            "block_number": block,
            "commanded_speed": speed,
            "commanded_authority": authority,
        }
        success = self.send_to_track_model(track_model_message)
        if success:
            print(f"Sent to Track Model: Block {block}, Speed:{speed}, Auth:{authority}")
        else:
            print(f"Failed to send to Track Model: Block {block}")
        return success

    def send_to_track_model(self, message):
        """Send message to Track Model"""
        return self.server.send_to_ui("Track Model", message)

    def _handle_switch_update(self, data):
        """Handle switch updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        direction = data.get('direction')
        
        if track and block and direction:
            print(f"Processing switch update: {track} Block {block} -> {direction}")
            
            switch_name = f"Switch {block}"
            self.data.update_track_data("switch_positions", switch_name, "direction", direction)
            self.data.update_track_data("switch_positions", switch_name, "condition", f"Set to {direction}")
            
            print(f"Switch updated successfully")

    def _handle_light_update(self, data):
        """Handle light updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        color = data.get('color')
        
        if track and block and color:
            print(f"💡 Processing light update: {track} Block {block} -> {color}")
            
            light_name = f"Light {block}"
            self.data.update_track_data("light_states", light_name, "signal", color)
            self.data.update_track_data("light_states", light_name, "condition", f"Signal: {color}")
            
            print(f"Light updated successfully")

    def _handle_crossing_update(self, data):
        """Handle crossing updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        lights = data.get('lights')
        crossbar = data.get('crossbar')
        
        if track and block and lights and crossbar:
            print(f" Processing crossing update: {track} Block {block} -> Lights:{lights}, Bar:{crossbar}")
            
            crossing_name = f"Railway {block}"
            self.data.update_track_data("railway_crossings", crossing_name, "lights", lights)
            self.data.update_track_data("railway_crossings", crossing_name, "bar", crossbar)
            self.data.update_track_data("railway_crossings", crossing_name, "condition", f"Lights: {lights}, Bar: {crossbar}")
            
            print(f" Crossing updated successfully")

    def _handle_speed_auth_update(self, data):
        """Handle speed/authority updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        speed = data.get('speed')
        authority = data.get('authority')
        value_type = data.get('value_type')  # 'commanded' or 'suggested'
        
        if track and block and value_type:
            print(f"Processing {value_type} update: {track} Block {block} -> Speed:{speed}, Auth:{authority}")
            
            if value_type == 'commanded':
                if speed is not None:
                    self.data.commanded_speed[track][block] = speed
                if authority is not None:
                    self.data.commanded_authority[track][block] = authority
                        
            elif value_type == 'suggested':
                if speed is not None:
                    self.data.suggested_speed[track][block] = speed
                if authority is not None:
                    self.data.suggested_authority[track][block] = authority
            
            # Update displays if we're viewing that track/block
            if hasattr(self, 'right_panel'):
                current_track = self.data.current_line
                current_block = self.right_panel.block_combo.get() if hasattr(self.right_panel, 'block_combo') else None
                
                if track == current_track and block == current_block:
                    self.right_panel.update_commanded_display()
                    self.right_panel.update_suggested_display()
            
            print(f"{value_type.capitalize()} values updated successfully")

    def _handle_occupancy_update(self, data):
        """Handle occupancy updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        occupied = data.get('occupied')
        
        if track and block and occupied is not None:
            print(f"Processing occupancy update: {track} Block {block} -> {occupied}")
            
            # Find the block in the original data and update it
            found = False
            for idx, row in enumerate(self.data.block_data_original):
                if row[1] == track and str(row[2]) == str(block):
                    new_occupied = "Yes" if occupied else "No"
                    self.data.update_block_data(idx, 0, new_occupied)
                    found = True
                    break
            
            if not found:
                print(f"Block {block} not found on {track} track")
            else:
                print(f"Occupancy update initiated")

    def send_to_test_ui(self, message):
        """Send message to Test UI"""
        return self.server.send_to_ui("test_ui", message)

    def on_closing(self):
        """Handle application closing"""
        print("Closing Main UI...")
        self.server.stop_server()
        self.root.destroy()

    def setup_logging(self):
        """Set up the direct callback logging system"""
        if hasattr(self.center_panel, 'log_callback') and self.center_panel.log_callback:
            log_callback = self.center_panel.log_callback
            
            for panel in [self.header, self.left_panel, self.right_panel]:
                if hasattr(panel, 'set_log_callback'):
                    panel.set_log_callback(log_callback)

    def create_ui(self):
        self.header = Header(self.root, self.data, app=self)
        self.header.pack(fill=tk.X, padx=10, pady=5)
        
        main_frame = tk.Frame(self.root, bg='#1a1a4d')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.left_panel = LeftPanel(main_frame, self.data)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.center_panel = CenterPanel(main_frame, self.data)
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.right_panel = RightPanel(main_frame, self.data)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        self.connect_panel_updates()

    def connect_panel_updates(self):
        for panel in [self.center_panel, self.right_panel, self.left_panel]:
            self.data.on_maintenance_mode_change.append(panel.update_mode_ui)

        self.data.on_line_change.append(self.right_panel.on_line_changed) 
        self.data.on_line_change.append(self.header.update_tab_appearance)

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()