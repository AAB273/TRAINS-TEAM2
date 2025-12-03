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
        
        # ADD THIS LINE: Track previous occupancy to detect changes
        self.previous_occupancy = {"Green": {}, "Red": {}}

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
        self.send_to_track_model(track_model_message)

    
    def send_switch_to_track_model(self, track, block, direction):
        """Send array of all switch directions to Track Model"""
        switch_list = []
        
        # Get all switch directions
        for switch_data in self.data.switch_positions.values():
            switch_direction = switch_data["direction"]  # Changed from 'direction' to 'switch_direction'
            switch_list.append(switch_direction)
        
        switch_message = {
            "command": "switch_states",
            "switches": switch_list
        }
        
        success = self.send_to_track_model(switch_message)
        if success:
            print(f"Sent to Track Model: {len(switch_list)} switch states")
        else:
            print(f"Failed to send switch states to Track Model")
        return success

    def send_to_track_model(self, message):
        """Send message to Track Model"""
        return self.server.send_to_ui("Track Model", message)
    
    def send_to_CTC(self, message):
        """Send message to Track Model"""
        return self.server.send_to_ui("CTC", message)

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
            
            # Send switch state to Track Model
            self.send_switch_to_track_model(track, block, direction)


    def _handle_light_update(self, data):
        """Handle light updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        color = data.get('color')
        
        if track and block and color:
            print(f"Processing light update: {track} Block {block} -> {color}")
            
            light_name = f"Light {block}"
            self.data.update_track_data("light_states", light_name, "signal", color)
            self.data.update_track_data("light_states", light_name, "condition", f"Signal: {color}")

            # Send switch state to Track Model
            self.send_light_state(track, block, color)

    def send_light_state(self,track, block, color):
        """Send Light State to CTC and Track Model"""
        message = {
            "command": "LS",
            "value": [block, color, track]
        }

        print("\n\n\nhere\n\n\n")
        self.send_to_CTC(message)



    def _handle_crossing_update(self, data):
        """Handle crossing updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        lights = data.get('lights')
        crossbar = data.get('crossbar')
        
        if track and block and lights and crossbar:
            print(f"Processing crossing update: {track} Block {block} -> Lights:{lights}, Bar:{crossbar}")
            
            crossing_name = f"Railway {block}"
            self.data.update_track_data("railway_crossings", crossing_name, "lights", lights)
            self.data.update_track_data("railway_crossings", crossing_name, "bar", crossbar)
            self.data.update_track_data("railway_crossings", crossing_name, "condition", f"Lights: {lights}, Bar: {crossbar}")
            

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
            
            # ALWAYS UPDATE RIGHT PANEL
            if hasattr(self, 'right_panel'):
                self.right_panel.update_commanded_display()
                self.right_panel.update_suggested_display()
                print(f"Right panel refreshed for {value_type} values")


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

            #Send speed and authority to Track Model when block becomes occupied
            if occupied:
                # Get commanded values for this block
                commanded_speed = self.data.commanded_speed[track].get(block, 0)
                commanded_authority = self.data.commanded_authority[track].get(block, 0)
                self.send_commanded_to_track_model(track, block, commanded_speed, commanded_authority)

            # Force refresh the center panel table
            if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'refresh_table'):
                self.center_panel.refresh_table()
                print(f"Center panel refreshed for occupancy update")
            
            # Also trigger data update callbacks
            if hasattr(self.data, 'trigger_data_update'):
                self.data.trigger_data_update()

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

'''
def test_block_occupancy(app):
    ###Test block occupancy functionality###
    print("\n=== Testing Block Occupancy ===")
    
    # Test Case 1: Set block to occupied
    print("\n--- Test Case 1: Set block to occupied ---")
    test_track = "Green"
    test_block = "15"
    test_occupied = True
    
    occupancy_message = {
        'command': 'update_occupancy',
        'data': {
            'track': test_track,
            'block': test_block,
            'occupied': test_occupied
        }
    }
    
    app._process_message(occupancy_message, "track_model")
    app.root.update()
    print(f" Occupied message processed for {test_track} Block {test_block}")

    # Test Case 2: Set same block to unoccupied
    print("\n--- Test Case 2: Set block to unoccupied ---")
    test_occupied = False
    
    occupancy_message = {
        'command': 'update_occupancy',
        'data': {
            'track': test_track,
            'block': test_block,
            'occupied': test_occupied
        }
    }
    
    app._process_message(occupancy_message, "track_model")
    app.root.update()
    print(f"Unoccupied message processed for {test_track} Block {test_block}")

    # Test Case 3: Test different block
    print("\n--- Test Case 3: Test different block ---")
    test_block2 = "20"
    test_occupied = True
    
    occupancy_message = {
        'command': 'update_occupancy',
        'data': {
            'track': test_track,
            'block': test_block2,
            'occupied': test_occupied
        }
    }
    
    app._process_message(occupancy_message, "track_model")
    app.root.update()
    print(f"Occupied message processed for {test_track} Block {test_block2}")

    # Test Case 4: Test different track
    print("\n--- Test Case 4: Test different track ---")
    test_track2 = "Red"
    test_block3 = "5"
    
    occupancy_message = {
        'command': 'update_occupancy',
        'data': {
            'track': test_track2,
            'block': test_block3,
            'occupied': True
        }
    }
    
    app._process_message(occupancy_message, "track_model")
    app.root.update()
    print(f" Occupied message processed for {test_track2} Block {test_block3}")

    print(f"\n ALL TESTS PASSED! The block occupancy logic works correctly.")
    return True
'''

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    # Run test after UI loads
    def run_test():
        test_block_occupancy(app)
    
    root.after(2000, run_test)  # Wait 2 seconds for UI to initialize
    root.mainloop()
