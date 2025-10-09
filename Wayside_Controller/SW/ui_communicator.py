import tkinter as tk
from tkinter import messagebox
import threading
import time

class UICommunicator:
    def __init__(self, main_ui_app, test_ui_app):
        """
        Connects the Test UI with the Main Railway Control System UI
        """
        self.main_ui = main_ui_app
        self.test_ui = test_ui_app
        self.data = main_ui_app.data  # Reference to shared data model
        
        # Set up communication callbacks
        self.setup_communication()
        
        print("✅ UI Communication established - Test UI can control Main UI")
        
    def setup_communication(self):
        """Set up communication between UIs"""
        # Connect test UI components to main UI data updates
        self.connect_test_to_main()
        
    def connect_test_to_main(self):
        """Connect test UI actions to update main UI data"""
        # Connect track controls (switches, lights, crossings)
        self.connect_track_controls()
        
        # Connect speed/authority controls
        self.connect_speed_authority_controls()
        
        # Connect occupancy controls
        self.connect_occupancy_controls()
        
        # Connect commanded values
        self.connect_commanded_values()
        
        #Connect suggested values
        self.connect_suggested_values()
        
    def connect_track_controls(self):
        """Connect track control components (switches, lights, crossings)"""
        # Get references to test UI components
        test_track_controls = self.test_ui.track_controls
        test_system_monitoring = self.test_ui.system_monitoring
        
        # Override the log callbacks to also update main UI
        original_track_log = test_track_controls.log_callback
        original_monitoring_log = test_system_monitoring.log_callback
        
        def enhanced_track_log(message):
            if original_track_log:
                original_track_log(message)
            self.update_main_ui_from_test_log(message)
            
        def enhanced_monitoring_log(message):
            if original_monitoring_log:
                original_monitoring_log(message)
            self.update_main_ui_from_test_log(message)
            
        test_track_controls.log_callback = enhanced_track_log
        test_system_monitoring.log_callback = enhanced_monitoring_log
        
    def connect_speed_authority_controls(self):
        """Connect speed and authority controls"""
        test_speed_auth = self.test_ui.speed_auth
        
        # Override the log callback to also update main UI
        original_log = test_speed_auth.log_callback
        
        def enhanced_log(message):
            if original_log:
                original_log(message)
            self.update_main_ui_from_test_log(message)
            self.update_main_speed_authority()
            
        test_speed_auth.log_callback = enhanced_log
        
    def connect_occupancy_controls(self):
        """Connect occupancy status controls"""
        test_speed_auth = self.test_ui.speed_auth
        
        # Store original toggle method
        original_toggle = test_speed_auth.toggle_occupancy
        
        def enhanced_toggle():
            original_toggle()
            self.update_main_occupancy()
            
        test_speed_auth.toggle_occupancy = enhanced_toggle
        
    def connect_commanded_values(self):
        """Connect commanded speed and authority values"""
        test_speed_auth = self.test_ui.speed_auth
        
        # Track changes to commanded values in real-time
        self.setup_commanded_value_tracking(test_speed_auth)
        
    def setup_commanded_value_tracking(self, speed_auth):
        """Set up real-time tracking of commanded value changes"""
        # Track speed changes
        if hasattr(speed_auth, 'commanded_speed_var'):
            speed_auth.commanded_speed_var.trace('w', self.on_commanded_speed_change)
        
        # Track authority changes
        if hasattr(speed_auth, 'commanded_auth_var'):
            speed_auth.commanded_auth_var.trace('w', self.on_commanded_authority_change)
        
        # Track track selection changes
        if hasattr(speed_auth, 'commanded_track_var'):
            speed_auth.commanded_track_var.trace('w', self.on_commanded_track_change)
        
        # Track block selection changes
        if hasattr(speed_auth, 'commanded_block_var'):
            speed_auth.commanded_block_var.trace('w', self.on_commanded_block_change)
            
    def on_commanded_speed_change(self, *args):
        """Handle real-time commanded speed changes - ONLY update speed"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            speed = test_speed_auth.commanded_speed_var.get()
            track = test_speed_auth.commanded_track_var.get()
            block = test_speed_auth.commanded_block_var.get()
            
            print(f"🎯 Commanded Speed changed: {track} {block} -> {speed}")
            # ONLY update speed, leave authority unchanged
            self.update_main_commanded_display(track, block, speed=speed)
            
        except Exception as e:
            print(f"Error handling commanded speed change: {e}")
            
    def on_commanded_authority_change(self, *args):
        """Handle real-time commanded authority changes - ONLY update authority"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            authority = test_speed_auth.commanded_auth_var.get()
            track = test_speed_auth.commanded_track_var.get()
            block = test_speed_auth.commanded_block_var.get()
            
            print(f"🎯 Commanded Authority changed: {track} {block} -> {authority}")
            # ONLY update authority, leave speed unchanged
            self.update_main_commanded_display(track, block, authority=authority)
            
        except Exception as e:
            print(f"Error handling commanded authority change: {e}")
            
    def on_commanded_track_change(self, *args):
        """Handle commanded track changes"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            track = test_speed_auth.commanded_track_var.get()
            block = test_speed_auth.commanded_block_var.get()
            
            print(f"🎯 Commanded Track changed: {track} {block}")
            self.update_main_commanded_display(track, block)
            
        except Exception as e:
            print(f"Error handling commanded track change: {e}")
            
    def on_commanded_block_change(self, *args):
        """Handle commanded block changes"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            track = test_speed_auth.commanded_track_var.get()
            block = test_speed_auth.commanded_block_var.get()
            
            print(f"🎯 Commanded Block changed: {track} {block}")
            self.update_main_commanded_display(track, block)
            
        except Exception as e:
            print(f"Error handling commanded block change: {e}")
        
    def update_main_ui_from_test_log(self, log_message):
        """
        Parse test UI log messages and update main UI accordingly
        """
        print(f"🔍 Parsing log message: {log_message}")
        
        try:
            # FIXED: More specific checks with exact string matching
            if "CROSSING: Set -" in log_message:
                self.update_main_crossings(log_message)
            elif "SWITCH: Set to" in log_message:
                self.update_main_switches(log_message)
            elif "LIGHTS: Set to" in log_message:
                self.update_main_lights(log_message)
            elif "SPEED:" in log_message or "AUTHORITY:" in log_message:
                self.update_main_speed_authority()
            elif "OCCUPANCY:" in log_message:
                self.update_main_occupancy()
            else:
                print(f"❓ Unknown log message type: {log_message}")
                
        except Exception as e:
            print(f"Error updating main UI from log: {e}")
    
    def update_main_switches(self, log_message):
        """Update main UI switches based on test UI actions"""
        try:
            print(f"🔧 Processing switch message: {log_message}")
            
            if "Set to" in log_message:
                parts = log_message.split("SWITCH: Set to ")
                if len(parts) > 1:
                    switch_info = parts[1].split(" on ")
                    switch_direction = switch_info[0]
                    track_block = switch_info[1].split(" track, Block ")
                    track = track_block[0]
                    block = track_block[1].strip()
                    
                    print(f"🔄 Switch update: {track} Block {block} -> {switch_direction}")
                    
                    # Update main UI data model
                    self.update_track_data_cross_line("switches", track, block, "direction", switch_direction)
                    self.update_track_data_cross_line("switches", track, block, "condition", f"Set to {switch_direction}")
                    
                    # FORCE LEFT PANEL REFRESH
                    self.force_left_panel_refresh()
                    
                    print(f"✅ Main UI Switch updated: {track} Block {block} -> {switch_direction}")
            
            else:
                print(f"❓ Unknown switch message format: {log_message}")
                    
        except Exception as e:
            print(f"Error updating main switches: {e}")
            
    def update_main_lights(self, log_message):
        """Update main UI lights based on test UI actions"""
        try:
            print(f"💡 Processing light message: {log_message}")  # Debug
            
            if "Set to" in log_message:
                parts = log_message.split("LIGHTS: Set to ")
                if len(parts) > 1:
                    light_info = parts[1].split(" on ")
                    light_color = light_info[0]
                    track_block = light_info[1].split(" track, Block ")
                    track = track_block[0]
                    block = track_block[1].strip()
                    
                    # Update main UI data model
                    self.update_track_data_cross_line("lights", track, block, "signal", light_color)
                    self.update_track_data_cross_line("lights", track, block, "condition", f"Signal: {light_color}")
                    
                    print(f"💡 Main UI Light updated: {track} Block {block} -> {light_color}")
            
            elif "signal" in log_message.lower():
                # Alternative format: "Light signal set to Green on Green track, Block 6"
                if "signal set to" in log_message:
                    parts = log_message.split("signal set to ")
                    if len(parts) > 1:
                        signal_info = parts[1].split(" on ")
                        light_color = signal_info[0]
                        track_block = signal_info[1].split(" track, Block ")
                        track = track_block[0]
                        block = track_block[1].strip()
                        
                        self.update_track_data_cross_line("lights", track, block, "signal", light_color)
                        self.update_track_data_cross_line("lights", track, block, "condition", f"Signal: {light_color}")
                        
                        print(f"💡 Main UI Light updated (alt format): {track} Block {block} -> {light_color}")
            
            else:
                print(f"❓ Unknown light message format: {log_message}")
                    
        except Exception as e:
            print(f"Error updating main lights: {e}")
            print(f"Full error: {e.__class__.__name__}: {e}")
            
    def update_main_crossings(self, log_message):
        """Update main UI crossings based on test UI actions"""
        if "Set -" in log_message:
            parts = log_message.split("CROSSING: Set - ")
            if len(parts) > 1:
                crossing_info = parts[1].split(" on ")
                settings = crossing_info[0]
                track_block = crossing_info[1].split(" track, Block ")
                track = track_block[0]
                block = track_block[1].strip()
                
                # Parse settings
                if "Lights:" in settings and "Crossbar:" in settings:
                    lights_setting = settings.split("Lights: ")[1].split(", Crossbar: ")[0]
                    crossbar_setting = settings.split("Crossbar: ")[1]
                elif "Lights:" in settings and "Bar:" in settings:
                    lights_setting = settings.split("Lights: ")[1].split(", Bar: ")[0]
                    crossbar_setting = settings.split("Bar: ")[1]
                else:
                    print(f"❓ Unknown crossing settings format: {settings}")
                    return
                 
                # Update main UI data model
                self.update_track_data_cross_line("crossings", track, block, "lights", lights_setting)
                self.update_track_data_cross_line("crossings", track, block, "bar", crossbar_setting)
                self.update_track_data_cross_line("crossings", track, block, "condition", f"Lights: {lights_setting}, Bar: {crossbar_setting}")
                
                # FORCE LEFT PANEL REFRESH
                self.force_left_panel_refresh()
                
                print(f"Main UI Crossing updated: {track} Block {block} -> Lights:{lights_setting}, Bar:{crossbar_setting}")
                
            
    def update_main_speed_authority(self):
        """Update main UI speed and authority displays"""
    
        test_speed_auth = self.test_ui.speed_auth
        track = test_speed_auth.commanded_track_var.get()
        block = test_speed_auth.commanded_block_var.get()
        
        # Get current values from test UI
        commanded_speed = test_speed_auth.commanded_speed_var.get()
        commanded_authority = test_speed_auth.commanded_auth_var.get()
        
        # Update main UI commanded display
        self.update_main_commanded_display(track, block, commanded_speed, commanded_authority)
        
        print(f"🎯 Speed/Authority update - Track: {track}, Block: {block}, "
              f"Speed: {commanded_speed}, Authority: {commanded_authority}")
                  
            
    def update_main_occupancy(self):
        """Update main UI occupancy status ONLY"""
        test_speed_auth = self.test_ui.speed_auth
        track = test_speed_auth.commanded_track_var.get()
        block = test_speed_auth.commanded_block_var.get()
        
        # Get current occupancy from test UI block data
        block_data = test_speed_auth.get_block_data(track, block)
        occupied = block_data.get('occupied', False)
        
        # Update main UI block data (occupancy only)
        occupancy_text = "Yes" if occupied else "No"
        self.update_block_data_cross_line(track, block, occupancy_text)
        
        print(f"📍 Occupancy update - Track: {track}, Block: {block}, Occupied: {occupancy_text}")
            
        
    def update_main_commanded_display(self, track, block, speed=None, authority=None):
        """Update main UI commanded values display"""
    
        # Get reference to main UI right panel commanded display
        right_panel = self.main_ui.right_panel
        
        # Update commanded values storage in main UI
        if hasattr(right_panel, 'commanded_values'):
            if track not in right_panel.commanded_values:
                right_panel.commanded_values[track] = {}
            
            if block not in right_panel.commanded_values[track]:
                right_panel.commanded_values[track][block] = {"authority": "0", "speed": "0"}
            
            # Update specific values if provided
            if speed is not None:
                right_panel.commanded_values[track][block]["speed"] = speed
            if authority is not None:
                right_panel.commanded_values[track][block]["authority"] = authority
        
        # If this is the currently selected block in main UI, update the display
        current_track = self.data.current_line
        current_block = getattr(right_panel, 'block_combo', tk.StringVar()).get()
        
        if current_track == track and current_block == block:
            # Update the commanded display in real-time
            if hasattr(right_panel, 'update_commanded_display'):
                right_panel.update_commanded_display()
            else:
                # Fallback: manually update the labels
                if hasattr(right_panel, 'commanded_speed_label') and speed is not None:
                    right_panel.commanded_speed_label.config(text=f"{speed} mph")
                if hasattr(right_panel, 'commanded_auth_label') and authority is not None:
                    right_panel.commanded_auth_label.config(text=f"{authority} blocks")
        
        print(f"Commanded display updated: {track} {block} - Speed: {speed}, Authority: {authority}")
 
    
    # CROSS-LINE UPDATE METHODS
    def update_track_data_cross_line(self, category, track, block, field, new_value):
        """Update track data regardless of current line in main UI"""
        # FIXED KEY GENERATION:
        if category == "switches":
            item_key = f"Switch {block}"
        elif category == "crossings":
            item_key = f"Railway {block}" 
        elif category == "lights":
            item_key = f"Light {block}"
        else:
            item_key = f"{category[:-1].title()} {block}"
        
        # Update the main data store (source of truth)
        if category in self.data.track_data and item_key in self.data.track_data[category]:
            self.data.track_data[category][item_key][field] = new_value
            print(f"✅ Updated main {category} data: {item_key}")
        
        # Also update the filtered data if we're currently viewing that track
        current_line = self.data.current_line
        
        # Check if this item should be in the filtered data for the current line
        if (category in self.data.track_data and 
            item_key in self.data.track_data[category] and
            self.data.track_data[category][item_key].get("line") == current_line):
            
            # Ensure filtered_track_data has this category
            if category not in self.data.filtered_track_data:
                self.data.filtered_track_data[category] = {}
            
            # Update or add to filtered data
            if item_key not in self.data.filtered_track_data[category]:
                # Copy the entire item from main data to filtered data
                self.data.filtered_track_data[category][item_key] = self.data.track_data[category][item_key].copy()
                print(f"✅ Added {item_key} to filtered {category} data")
            else:
                # Update existing filtered data
                self.data.filtered_track_data[category][item_key][field] = new_value
                print(f"✅ Updated filtered {category} data")
        
        # Also update if we're currently viewing the same track as the update
        if track == current_line and category in self.data.filtered_track_data:
            if item_key in self.data.filtered_track_data[category]:
                self.data.filtered_track_data[category][item_key][field] = new_value
                print(f"✅ Updated current line filtered {category} data")
        
        # Force UI refresh
        self.trigger_main_ui_update()
    
    
    def update_block_data_cross_line(self, track, block, new_occupied_status):
        """Update block occupancy regardless of current line in main UI"""
        # Update the original data (source of truth)
        for i, row in enumerate(self.data.block_data_original):
            if row[1] == track and row[2] == block:
                self.data.block_data_original[i][0] = new_occupied_status
                break
        
        # Also update the filtered data if we're currently viewing that track
        if track == self.data.current_line:
            for i, row in enumerate(self.data.block_data):
                if row[1] == track and row[2] == block:
                    self.data.block_data[i][0] = new_occupied_status
                    break
        
        # Force UI refresh
        self.trigger_main_ui_update()
            
    def trigger_main_ui_update(self):
        """Trigger updates in main UI components"""
        # Force UI refresh by triggering line change callback
        if hasattr(self.data, 'on_line_change') and self.data.on_line_change:
            for callback in self.data.on_line_change:
                callback()
        
        # Also trigger maintenance mode callbacks to refresh all panels
        if hasattr(self.data, 'on_maintenance_mode_change') and self.data.on_maintenance_mode_change:
            for callback in self.data.on_maintenance_mode_change:
                callback()
        
        # SPECIFICALLY REFRESH LEFT PANEL DISPLAYS
        if hasattr(self.main_ui, 'left_panel') and hasattr(self.main_ui.left_panel, 'refresh_current_display'):
            self.main_ui.left_panel.refresh_current_display()
        
        # Force UI update
        self.main_ui.root.update_idletasks()
       


    def force_left_panel_refresh(self):
        """Force left panel to completely reload its options and displays"""
        left_panel = self.main_ui.left_panel
        
        # Force reload all options
        if hasattr(left_panel, 'update_crossing_options'):
            left_panel.update_crossing_options()
        if hasattr(left_panel, 'update_switch_options'):
            left_panel.update_switch_options()  
        if hasattr(left_panel, 'update_light_options'):
            left_panel.update_light_options()

    # Add this method to UICommunicator class:
    def update_main_suggested_display(self, track, block, speed=None, authority=None):
        """Update main UI suggested values display"""
        right_panel = self.main_ui.right_panel
        
        # Update suggested values storage in main UI
        if hasattr(right_panel, 'suggested_values'):
            if track not in right_panel.suggested_values:
                right_panel.suggested_values[track] = {}
            
            if block not in right_panel.suggested_values[track]:
                right_panel.suggested_values[track][block] = {"authority": "0", "speed": "0"}
            
            # Update specific values if provided
            if speed is not None:
                right_panel.suggested_values[track][block]["speed"] = speed
            if authority is not None:
                right_panel.suggested_values[track][block]["authority"] = authority
        
        # If this is the currently selected block in main UI, update the display
        current_track = self.data.current_line
        current_block = getattr(right_panel, 'block_combo', tk.StringVar()).get()
        
        if current_track == track and current_block == block:
            # Update the suggested display in real-time
            if hasattr(right_panel, 'update_suggested_display'):
                right_panel.update_suggested_display()
        
        print(f"Suggested display updated: {track} {block} - Speed: {speed}, Authority: {authority}")


        

    ####################################
    # SUGGESTED
    ####################################
    def connect_suggested_values(self):
        """Connect suggested value controls from Test UI to Main UI"""
        test_speed_auth = self.test_ui.speed_auth
        
        # Track suggested speed changes
        if hasattr(test_speed_auth, 'suggested_speed_var'):
            test_speed_auth.suggested_speed_var.trace('w', self.on_suggested_speed_change)
        
        # Track suggested authority changes
        if hasattr(test_speed_auth, 'suggested_auth_var'):
            test_speed_auth.suggested_auth_var.trace('w', self.on_suggested_authority_change)
        
        # Track suggested track selection changes
        if hasattr(test_speed_auth, 'suggested_track_var'):
            test_speed_auth.suggested_track_var.trace('w', self.on_suggested_track_change)
        
        # Track suggested block selection changes
        if hasattr(test_speed_auth, 'suggested_block_var'):
            test_speed_auth.suggested_block_var.trace('w', self.on_suggested_block_change)

    def on_suggested_speed_change(self, *args):
        """Handle real-time suggested speed changes - ONLY update suggested speed"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            speed = test_speed_auth.suggested_speed_var.get()
            track = test_speed_auth.suggested_track_var.get()
            block = test_speed_auth.suggested_block_var.get()
            
            print(f"🎯 Suggested Speed changed: {track} {block} -> {speed}")
            # ONLY update suggested speed, leave authority unchanged
            self.update_main_suggested_display(track, block, speed=speed)
            
        except Exception as e:
            print(f"Error handling suggested speed change: {e}")

    def on_suggested_authority_change(self, *args):
        """Handle real-time suggested authority changes - ONLY update suggested authority"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            authority = test_speed_auth.suggested_auth_var.get()
            track = test_speed_auth.suggested_track_var.get()
            block = test_speed_auth.suggested_block_var.get()
            
            print(f"🎯 Suggested Authority changed: {track} {block} -> {authority}")
            # ONLY update suggested authority, leave speed unchanged
            self.update_main_suggested_display(track, block, authority=authority)
            
        except Exception as e:
            print(f"Error handling suggested authority change: {e}")

    def on_suggested_track_change(self, *args):
        """Handle suggested track changes"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            track = test_speed_auth.suggested_track_var.get()
            block = test_speed_auth.suggested_block_var.get()
            
            print(f"🎯 Suggested Track changed: {track} {block}")
            self.update_main_suggested_display(track, block)
            
        except Exception as e:
            print(f"Error handling suggested track change: {e}")

    def on_suggested_block_change(self, *args):
        """Handle suggested block changes"""
        try:
            test_speed_auth = self.test_ui.speed_auth
            track = test_speed_auth.suggested_track_var.get()
            block = test_speed_auth.suggested_block_var.get()
            
            print(f"🎯 Suggested Block changed: {track} {block}")
            self.update_main_suggested_display(track, block)
            
        except Exception as e:
            print(f"Error handling suggested block change: {e}")

    def update_main_suggested_display(self, track, block, speed=None, authority=None):
        """Update main UI suggested values display"""
        right_panel = self.main_ui.right_panel
        
        # Update suggested values storage in main UI
        if hasattr(right_panel, 'suggested_values'):
            if track not in right_panel.suggested_values:
                right_panel.suggested_values[track] = {}
            
            if block not in right_panel.suggested_values[track]:
                right_panel.suggested_values[track][block] = {"authority": "0", "speed": "0"}
            
            # Update specific values if provided
            if speed is not None:
                right_panel.suggested_values[track][block]["speed"] = speed
            if authority is not None:
                right_panel.suggested_values[track][block]["authority"] = authority
        
        # Also update the shared data model
        if hasattr(self.data, 'suggested_values'):
            if track not in self.data.suggested_values:
                self.data.suggested_values[track] = {}
            
            if block not in self.data.suggested_values[track]:
                self.data.suggested_values[track][block] = {"authority": "0", "speed": "0"}
            
            if speed is not None:
                self.data.suggested_values[track][block]["speed"] = speed
            if authority is not None:
                self.data.suggested_values[track][block]["authority"] = authority
        
        # If this is the currently selected block in main UI, update the display
        current_track = self.data.current_line
        current_block = getattr(right_panel, 'block_combo', tk.StringVar()).get()
        
        if current_track == track and current_block == block:
            # Update the suggested display in real-time
            if hasattr(right_panel, 'update_suggested_display'):
                right_panel.update_suggested_display()
        
        print(f"Suggested display updated: {track} {block} - Speed: {speed}, Authority: {authority}")












####################################
# FOR DEBUGGING PURPOSES
####################################

#    def debug_track_data(self, category, track, block):
#        """Debug method to see what's in the track data"""
#        # FIXED KEY GENERATION:
#        if category == "switches":
#            item_key = f"Switch {block}"
#        elif category == "crossings":
#            item_key = f"Railway {block}"
#        elif category == "lights":
#            item_key = f"Light {block}"
#        else:
#            item_key = f"{category[:-1].title()} {block}"
#            
#        print(f"DEBUG {category.upper()}:")
#        print(f"Looking for: {item_key}")
#        print(f"Current line: {self.data.current_line}")
#        print(f"Update track: {track}")
#        
#        # Check main track_data
#        if category in self.data.track_data:
#            if item_key in self.data.track_data[category]:
#                main_data = self.data.track_data[category][item_key]
#                print(f"Main data: {main_data}")
#            else:
#                print(f"NOT FOUND in main track_data")
#                print(f"Available {category}: {list(self.data.track_data[category].keys())}")
#        else:
#            print(f"Category {category} not in track_data")
#        
#        # Check filtered_track_data
#        if category in self.data.filtered_track_data:
#            if item_key in self.data.filtered_track_data[category]:
#                filtered_data = self.data.filtered_track_data[category][item_key]
#                print(f"   Filtered data: {filtered_data}")
#            else:
#                print(f"NOT FOUND in filtered_track_data")
#                print(f"Available filtered {category}: {list(self.data.filtered_track_data[category].keys())}")
#        else:
#            print(f"Category {category} not in filtered_track_data")

