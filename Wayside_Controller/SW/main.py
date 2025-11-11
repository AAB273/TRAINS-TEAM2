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

class RailwayControlSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Wayside Controller")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a4d')
        
        self.data = RailwayData()
        
        # Initialize socket server for main UI
        self.server = TrainSocketServer(port=12345, ui_id="main_ui")
        self.server.set_allowed_connections(["test_ui"])
        
        self.create_ui()
        self.setup_logging()
        
        # Start server with message handler
        self.server.start_server(self._process_message)
        
        # Set up window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _process_message(self, message, source_ui_id):
        """Process incoming messages from Test UI"""
        try:
            print(f"Main UI received from {source_ui_id}: {message}")
            
            command = message.get('command')
            data = message.get('data', {})
            
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

    def _handle_switch_update(self, data):
        """Handle switch updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        direction = data.get('direction')
        
        if track and block and direction:
            print(f"🔄 Processing switch update: {track} Block {block} -> {direction}")
            
            # Use the CORRECT method - update_track_data instead of update_track_data_cross_line
            switch_name = f"Switch {block}"
            self.data.update_track_data("switch_positions", switch_name, "direction", direction)
            self.data.update_track_data("switch_positions", switch_name, "condition", f"Set to {direction}")
            
            print(f"✅ Switch updated successfully")

    def _handle_light_update(self, data):
        """Handle light updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        color = data.get('color')
        
        if track and block and color:
            print(f"💡 Processing light update: {track} Block {block} -> {color}")
            
            # Use the CORRECT method - update_track_data instead of update_track_data_cross_line
            light_name = f"Light {block}"
            self.data.update_track_data("light_states", light_name, "signal", color)
            self.data.update_track_data("light_states", light_name, "condition", f"Signal: {color}")
            
            print(f"✅ Light updated successfully")

    def _handle_crossing_update(self, data):
        """Handle crossing updates from Test UI"""
        track = data.get('track')
        block = data.get('block')
        lights = data.get('lights')
        crossbar = data.get('crossbar')
        
        if track and block and lights and crossbar:
            print(f"🚧 Processing crossing update: {track} Block {block} -> Lights:{lights}, Bar:{crossbar}")
            
            # Use the CORRECT method - update_track_data instead of update_track_data_cross_line
            crossing_name = f"Railway {block}"
            self.data.update_track_data("railway_crossings", crossing_name, "lights", lights)
            self.data.update_track_data("railway_crossings", crossing_name, "bar", crossbar)
            self.data.update_track_data("railway_crossings", crossing_name, "condition", f"Lights: {lights}, Bar: {crossbar}")
            
            print(f"✅ Crossing updated successfully")

    def _handle_speed_auth_update(self, data):
        """Handle speed/authority updates from Test UI - SIMPLE VERSION"""
        track = data.get('track')
        block = data.get('block')
        speed = data.get('speed')
        authority = data.get('authority')
        value_type = data.get('value_type')  # 'commanded' or 'suggested'
        
        if track and block and value_type:
            print(f"🎯 Processing {value_type} update: {track} Block {block} -> Speed:{speed}, Auth:{authority}")
            
            if value_type == 'commanded':
                # Simply update the shared data - this will override everything
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
            
            print(f"✅ {value_type.capitalize()} values updated successfully")

    def _handle_occupancy_update(self, data):
        """Handle occupancy updates from Test UI - ROBUST VERSION"""
        track = data.get('track')
        block = data.get('block')
        occupied = data.get('occupied')
        
        if track and block and occupied is not None:
            print(f"📍 DEBUG: Processing occupancy update: {track} Block {block} -> {occupied}")
            
            # Find the block in the original data and update it
            found = False
            for idx, row in enumerate(self.data.block_data_original):
                if row[1] == track and str(row[2]) == str(block):
                    # Update occupancy status - this will trigger all the updates
                    new_occupied = "Yes" if occupied else "No"
                    print(f"📍 DEBUG: Found block at index {idx}: {row}")
                    print(f"📍 DEBUG: Calling update_block_data({idx}, 0, '{new_occupied}')")
                    self.data.update_block_data(idx, 0, new_occupied)
                    found = True
                    break
            
            if not found:
                print(f"❌ Block {block} not found on {track} track in block_data_original")
                print(f"❌ Available {track} blocks:")
                for idx, row in enumerate(self.data.block_data_original):
                    if row[1] == track:
                        print(f"  - Index {idx}: Block {row[2]} -> {row}")
            else:
                print(f"✅ Occupancy update initiated")

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
        
        # Connect to Test UI after UI is created
        self.root.after(1000, self._connect_to_test_ui)

    def _connect_to_test_ui(self):
        """Connect to Test UI server"""
        if self.server.connect_to_ui('localhost', 12346, "test_ui"):
            print("✅ Connected to Test UI")
        else:
            print("❌ Failed to connect to Test UI - make sure Test UI is running")
    
    def connect_panel_updates(self):
        for panel in [self.center_panel, self.right_panel, self.left_panel]:
            self.data.on_maintenance_mode_change.append(panel.update_mode_ui)

        self.data.on_line_change.append(self.right_panel.on_line_changed) 
        self.data.on_line_change.append(self.header.update_tab_appearance)

    def debug_block_data(self, track, block):
        """Debug method to check block data state"""
        print(f"🔍 DEBUG: Checking block data for {track} Block {block}")
        
        # Check block_data_original
        for idx, row in enumerate(self.data.block_data_original):
            if row[1] == track and str(row[2]) == str(block):
                print(f"🔍 DEBUG: block_data_original[{idx}]: {row}")
                break
        
        # Check block_data (filtered)
        for idx, row in enumerate(self.data.block_data):
            if row[1] == track and str(row[2]) == str(block):
                print(f"🔍 DEBUG: block_data[{idx}]: {row}")
                break
        
        # Check filtered_blocks
        block_key = f"Block {block}"
        if hasattr(self.data, 'filtered_blocks') and block_key in self.data.filtered_blocks:
            print(f"🔍 DEBUG: filtered_blocks['{block_key}']: {self.data.filtered_blocks[block_key]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()