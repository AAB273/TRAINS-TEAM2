import tkinter as tk
from ui_test.system_log import SystemLog
from ui_test.track_controls import TrackControls
from ui_test.system_monitoring import SystemMonitoring
from ui_test.speed_authority import SpeedAuthorityControl
from ui_test.header import Header
from config.track_config import TrackConfig 


class RailwayControlSystem:
    def __init__(self, root, shared_data=None):
        self.root = root
        
        if isinstance(root, tk.Tk):
            self.root.title("Wayside Controller Software UI")
            self.root.geometry("1200x750")
        else:
            self.root.title("Wayside Controller - Test Interface")
            self.root.geometry("1200x750")
            
        self.root.configure(bg="#1a1a4d")
        
        # Load track configuration
        self.track_config = TrackConfig()
        
        # Store shared data reference
        self.shared_data = shared_data
        
        # Initialize UI components
        self.create_ui()
        
        # Set up log callback
        self.setup_logging()
        
        print("🧪 Test UI ready" + (" with shared data" if shared_data else " in standalone mode"))
        
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
        
        # Also connect the SystemLog to update shared data
        self.system_log.set_log_callback(self.add_to_log)
    
    def setup_logging(self):
        pass
    
    def add_to_log(self, message):
        print(f"TEST UI LOG: {message}")
        
        # If we have shared data, update it
        if self.shared_data:
            self.update_shared_data_from_log(message)
    
    def update_shared_data_from_log(self, log_message):
        """Update shared data model based on test UI actions"""
        if "SWITCH:" in log_message:
            parts = log_message.split("SWITCH: Set to ")
            if len(parts) > 1:
                switch_info = parts[1].split(" on ")
                switch_direction = switch_info[0]
                track_block = switch_info[1].split(" track, Block ")
                track = track_block[0]
                block = track_block[1]
                
                # Update shared data
                switch_key = f"Switch {block}"
                self.shared_data.update_track_data("switches", switch_key, "direction", switch_direction)
                print(f"🔗 Updated shared data: {switch_key} -> {switch_direction}")
                
        elif "LIGHTS:" in log_message:
            parts = log_message.split("LIGHTS: Set to ")
            if len(parts) > 1:
                light_info = parts[1].split(" on ")
                light_color = light_info[0]
                track_block = light_info[1].split(" track, Block ")
                track = track_block[0]
                block = track_block[1]
                
                # Update shared data
                light_key = f"Light {block}"
                self.shared_data.update_track_data("lights", light_key, "signal", light_color)
                print(f"🔗 Updated shared data: {light_key} -> {light_color}")
                
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
                
                crossing_key = f"Railway {block}"
                self.shared_data.update_track_data("crossings", crossing_key, "lights", lights_setting)
                self.shared_data.update_track_data("crossings", crossing_key, "bar", crossbar_setting)
                print(f"🔗 Updated shared data: {crossing_key} -> Lights:{lights_setting}, Bar:{crossbar_setting}")
                    

    
    def configure_blue_line(self, blue_line_data):
        self.track_config.set_track_data("Blue", blue_line_data)
        
    def load_track_configuration(self, track_name, config_file_path):
        self.track_config.load_track_from_file(track_name, config_file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()