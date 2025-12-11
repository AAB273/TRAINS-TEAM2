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
from datetime import datetime

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
            data = message.get('value')
            
            # Check if message is from CTC and it's a switch command
            if source_ui_id == "CTC":
                if command == "SW":
                    self.handle_ctc_switch(data)
                elif command == "MAINT":  # Maintenance request from CTC
                    self.handle_ctc_maintenance(data)
                elif command == 'update_speed_auth':
                    self.handle_speed_auth_update(data)
                return  # Stop processing here
            
            if command == 'update_switch':
                self.handle_switch_update(data)
            elif command == 'update_light':
                self.handle_light_update(data)
            elif command == 'update_crossing':
                self.handle_crossing_update(data)
            elif command == 'update_speed_auth':
                self.handle_speed_auth_update(data)
            elif command == 'update_occupancy':
                self.handle_occupancy_update(data)
            
                
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def handle_ctc_maintenance(self):
        """Handle maintenance mode request from CTC"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{current_time} CTC: Maintenance Request Received"
            
            #print(f"CTC maintenance request received")
            
            # Send to UI log via callback
            if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'log_callback'):
                self.center_panel.log_callback(log_message)
                
        except Exception as e:
            error_msg = f"Error processing CTC maintenance command: {e}"
            print(f"✗ {error_msg}")
            
            # Log the error
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{current_time} ERROR: Failed to process CTC maintenance request"
            if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'log_callback'):
                self.center_panel.log_callback(log_message)

    def handle_ctc_switch(self, data):
        """Log CTC switch command without updating the switch"""
        try:
            # Parse the data - CTC sends: [block, track] (NO direction!)
            if isinstance(data, list) and len(data) >= 2:
                block = str(data[0])
                track = str(data[1])
                
                #print(f"CTC wants to switch: Block {block} on {track} track")
                
                # Just log to UI, don't update the switch
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Different message since no direction specified
                log_message = f"{current_time} CTC REQUEST: Toggle Switch {block} on {track} track"
                
                # Send to UI log via callback
                if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'log_callback'):
                    self.center_panel.log_callback(log_message)
                
                #print(f"✓ CTC switch request logged: {log_message}")
                
            else:
                error_msg = f"Invalid CTC switch data format: {data}"
                #print(f"✗ {error_msg}")
                
                # Still log the error
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"{current_time} ERROR: Invalid CTC switch command format"
                if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'log_callback'):
                    self.center_panel.log_callback(log_message)
                    
        except Exception as e:
            error_msg = f"Error processing CTC switch command: {e}"
            print(f"✗ {error_msg}")
            
            # Log the error
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{current_time} ERROR: Failed to process CTC switch command"
            if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'log_callback'):
                self.center_panel.log_callback(log_message)

    def send_commanded_to_track_model(self, track, block, speed, authority):
        """Send commanded speed and authority to Track Model"""
        track_model_message = {
            "command": "Speed and Authority",
            "block_number": block,
            "commanded_speed": speed,
            "commanded_authority": authority,
        }
        self.send_to_track_model(track_model_message)

    def send_switch_to_track_model(self, track, block, position):
        """Send only switches in PLC-controlled sections to Track Model"""
        # Build array of PLC-controlled switch positions
        switch_list = []
        
        # Add track identifier as first element (0 for Green, 1 for Red)
        track_id = 0 if track == "Green" else 1 if track == "Red" else 2
        switch_list.append(track_id)
        
        # Get all switches for the current track in PLC sections
        switches = []
        
        # Get PLC sections - similar to how your models class does it
        plc_sections = []
        if hasattr(self.data, 'plc_filter_active') and self.data.plc_filter_active:
            plc_sections = getattr(self.data, 'plc_filter_sections', [])
        
        #print(f"PLC sections for switch filtering: {plc_sections}")
        
        for switch_name, switch_data in self.data.switch_positions.items():
            if switch_data.get("line") == track:
                # Get switch block number
                switch_block_num = int(switch_name.split(" ")[1])
                
                # Get section for this block using the same method as your models class
                section = self.data.get_section_for_block(track, str(switch_block_num))
                
                # Include if section is in PLC sections
                if section in plc_sections:
                    # Extract block number and convert to integer for sorting
                    switches.append((switch_block_num, switch_data.get("numeric_position", 1) - 1))
                    #print(f"  Including switch {switch_block_num}: section={section} in PLC sections")
        
        # Sort by block number (smallest first)
        switches.sort(key=lambda x: x[0])
        
        # Add positions in sorted order
        for block_num, pos in switches:
            switch_list.append(pos)
        
        switch_message = {
            "command": "switch_states",
            "value": switch_list  # This will be [track_id, pos1, pos2, ...] for PLC switches only
        }
        
        #print(f"Sending PLC switches to track model: {switch_message}")
        #print(f"  Number of switches included: {len(switches)}")
        #print(f"  Switch blocks: {[s[0] for s in switches]}")
        
        return self.send_to_track_model(switch_message)

    def send_to_track_model(self, message):
        """Send message to Track Model"""
        return self.server.send_to_ui("Track Model", message)
    
    def send_to_CTC(self, message):
        """Send message to Track Model"""
        return self.server.send_to_ui("CTC", message)

    def handle_switch_update(self, data):
        """Handle switch updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        direction = data.get('direction')
        
        if track and block and direction:
            #print(f"Processing switch update: {track} Block {block} -> {direction}")
            
            switch_name = f"Switch {block}"
            self.data.update_track_data("switch_positions", switch_name, "direction", direction)
            self.data.update_track_data("switch_positions", switch_name, "condition", f"Set to {direction}")
            
            # Send switch state to Track Model
            self.send_switch_to_track_model(track, block, direction)


    def handle_light_update(self, data):
        """Handle light updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        color = data.get('color')
        
        if track and block and color:
            #print(f"Processing light update: {track} Block {block} -> {color}")
            
            light_name = f"Light {block}"
            self.data.update_track_data("light_states", light_name, "signal", color)
            self.data.update_track_data("light_states", light_name, "condition", f"Signal: {color}")

           
    def send_light_state(self,track, block, color):
        """Send Light State to CTC and Track Model"""
        if (color == 'Red'):
            color_ctc = "00"
        elif (color == 'Yellow'):
            color_ctc = "01"
        elif (color == 'Green'):
            color_ctc = "10"
        else:
            color_ctc ="11"

        message = {
            "command": "LS",
            "value": [block, color_ctc, track]
        }

        self.send_to_CTC(message)

        # Send ALL light states to Track Model in [{'0','1'}, {'0','1'}, ...] format
        self.send_all_lights_to_track_model(track)

    def send_all_lights_to_track_model(self, track):
        """Send ALL light states for a track to Track Model in [{'0','1'}, ...] format"""
        # Build array of all light states
        light_list = []
        
        # Get all lights for this track, sorted by block number
        lights = []
        for light_name, light_data in self.data.light_states.items():
            if light_data.get("line") == track:
                block_num = int(light_name.split(" ")[1])
                signal = light_data.get("signal", "Green")
                # Convert signal to {'0','1'} format
                if signal == 'Red':
                    color_set = ['0','0']
                elif signal == 'Yellow':
                    color_set = ['0','1']
                elif signal == 'Green':
                    color_set = ['1','0']
                else:  # super green
                    color_set = ['1','1']
                lights.append((block_num, color_set))
        
        # Sort by block number (smallest first)
        lights.sort(key=lambda x: x[0])
        
        # Add color sets in sorted order
        for block_num, color_set in lights:
            light_list.append(color_set)
        
        # Send to Track Model
        track_model_message = {
            "command": "light_states",
            "value": light_list  # [['0','1'], ['0','1'], ...] in block order
        }
        
        self.send_to_track_model(track_model_message)

    def send_occupancy(self, track, block, occupied):
        """Send Occupany to CTC"""
        if (occupied == 'Yes'):
            message = {
                "command": "TL",
                "value": [block, track]
            }
            self.send_to_CTC(message)

       
    
    def send_railway_state(self, track, block, bar):
        """Send Light State to CTC and Track Model"""
        if (bar == 'Closed'):
            booly = "1"
        else:
            booly = "0"
            
        message = {
            "command": "RC",
            "value": [block, booly, track]
        }
        
        self.send_to_CTC(message)
        self.send_rc_to_track_model(track)
    
    def send_rc_to_track_model(self, track):
        """Send all railway crossing states to Track Model"""
        # Build array of all railway crossing states
        rc_list = []
        
        # Get all railway crossings for the current track
        crossings = []
        for crossing_name, crossing_data in self.data.railway_crossings.items():
            if crossing_data.get("line") == track:
                # Extract block number and convert to integer for sorting
                block_num = int(crossing_name.split(" ")[1])
                # Get crossing state (0 for Open, 1 for Closed)
                bar_state = crossing_data.get("bar", "Open")
                state = 1 if bar_state == "Closed" else 0
                crossings.append((block_num, state))
        
        # Sort by block number (smallest first)
        crossings.sort(key=lambda x: x[0])
        
        # Add states in sorted order
        for block_num, state in crossings:
            rc_list.append(state)
        
        rc_message = {
            "command": "rc_states",  # Or "railway_crossing_states"
            "value": rc_list  # This will be [state1, state2, ...] in block order
        }
        
        #print(f"Sending all railway crossings to track model: {rc_message}")
        return self.send_to_track_model(rc_message)


    def handle_crossing_update(self, data):
        """Handle crossing updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        lights = data.get('lights')
        crossbar = data.get('crossbar')
        
        if track and block and lights and crossbar:
            #print(f"Processing crossing update: {track} Block {block} -> Lights:{lights}, Bar:{crossbar}")
            
            crossing_name = f"Railway {block}"
            self.data.update_track_data("railway_crossings", crossing_name, "lights", lights)
            self.data.update_track_data("railway_crossings", crossing_name, "bar", crossbar)
            self.data.update_track_data("railway_crossings", crossing_name, "condition", f"Lights: {lights}, Bar: {crossbar}")

    def handle_speed_auth_update(self, data):
        """Handle speed/authority updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        speed = data.get('speed')
        authority = data.get('authority')
        value_type = data.get('value_type')  # 'commanded' or 'suggested'
        #print(f"Processing {value_type} update: {track} Block {block} -> Speed:{speed}, Auth:{authority}")

        if track and block and value_type:
            #print(f"Processing {value_type} update: {track} Block {block} -> Speed:{speed}, Auth:{authority}")
            
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
<<<<<<< HEAD
=======
                if block == "63":  # ONLY for block 63!
                    print(f"CTC sent suggested values for block 63 - forwarding to Track Model as commanded")
                    
                    # Use suggested values or defaults
                    set_speed = "25"
                    set_authority = "3"
                    
                    # Send to Track Model as commanded values
                    self.send_commanded_to_track_model(track, block, set_speed, set_authority)
                
>>>>>>> 65de30f8a3fe9626c6983f0caa63d76dee914acd
            
            # ALWAYS UPDATE RIGHT PANEL
            if hasattr(self, 'right_panel'):
                self.right_panel.update_commanded_display()
                self.right_panel.update_suggested_display()
                #print(f"Right panel refreshed for {value_type} values")


    def handle_occupancy_update(self, data):
        """Handle occupancy updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        occupied = data.get('occupied')
        
        if track and block and occupied is not None:
            #print(f"Processing occupancy update: {track} Block {block} -> {occupied}")
            
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
            
            # Get PLC sections to check if block is in PLC-controlled area
            plc_sections = []
            if hasattr(self.data, 'plc_filter_active') and self.data.plc_filter_active:
                plc_sections = getattr(self.data, 'plc_filter_sections', [])
            
            # Get section for this block
            section = self.data.get_section_for_block(track, block)
            
            #print(f"Block {block} on {track}: section={section}, in PLC sections={section in plc_sections}")
            
            # Send speed and authority to Track Model when:
            # 1. Block becomes occupied AND
            # 2. Block is in PLC-controlled section
            if occupied and section in plc_sections:
                # Get commanded values for this block
                commanded_speed = self.data.commanded_speed[track].get(block, 0)
                commanded_authority = self.data.commanded_authority[track].get(block, 0)
                
                #print(f"Sending commanded values for occupied PLC block {block}: speed={commanded_speed}, authority={commanded_authority}")
                self.send_commanded_to_track_model(track, block, commanded_speed, commanded_authority)


            # Force refresh the center panel table
            if hasattr(self, 'center_panel') and hasattr(self.center_panel, 'refresh_table'):
                self.center_panel.refresh_table()
                #print(f"Center panel refreshed for occupancy update")
            
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


if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()
