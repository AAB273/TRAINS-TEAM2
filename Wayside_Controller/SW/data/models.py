import os
import re

class RailwayData:
    def __init__(self):
        self.maintenance_mode = False
        self.test_mode = False
        self.current_line = "Blue"  # Default line
        
        # Callbacks for UI updates
        self.on_line_change = []
        self.on_maintenance_mode_change = []
        self.on_test_mode_change = []
        self.on_data_update = []  # New: callbacks for live PLC/UI updates
        
        # Add commanded_values for right panel
        self.commanded_values = {
            "Blue": {},
            "Green": {}, 
            "Red": {}
        }
        
        # Initialize data from TXT files
        self.track_data = self.load_all_track_data()
        
        # Initialize fault data (now dynamic based on lines)
        self.fault_data = [
            ["3/16", "14:22:01", "Blue", "3", "Railway Crossing", "Active"],
            ["9/14", "01:11:21", "Blue", "5", "Switch", "Resolved"],
            ["3/17", "09:45:33", "Green", "5", "Railway Crossing", "Active"],
            ["3/17", "10:15:22", "Red", "2", "Railway Crossing", "Resolved"],
        ]
        
        # Initialize block data (now dynamic based on lines)
        self.block_data = self.load_all_block_data()
        
        # Keep original data for filtering
        self.fault_data_original = self.fault_data.copy()
        self.block_data_original = self.block_data.copy()

        self.ensure_faulted_column()  # Ensure all blocks have faulted status

        # Initialize filtered_track_data
        self.filtered_track_data = {}
        self.filter_data_by_line(self.current_line)
        
        # Add blocks to filtered_track_data structure
        self.filtered_track_data["blocks"] = {}
        self.initialize_track_blocks()

        #system log reference
        self.system_log = None

    def ensure_faulted_column(self):
        """Ensure all blocks have the Faulted column (index 3)"""
        for row in self.block_data:
            if len(row) < 4:
                row.append("No")  # Default to not faulted
        for row in self.block_data_original:
            if len(row) < 4:
                row.append("No")  # Default to not faulted

    def initialize_track_blocks(self):
        """Initialize blocks in filtered_track_data with proper structure"""
        self.filtered_track_data["blocks"] = {}
        
        for row in self.block_data:
            if row[1] == self.current_line:  # Only current line
                block_num = str(row[2])
                block_key = f"Block {block_num}"
                
                self.filtered_track_data["blocks"][block_key] = {
                    "number": block_num,
                    "occupied": (row[0] == "Yes"),
                    "position": int(block_num),  # Simple position based on block number
                    "authority": 0,  # Default authority
                    "speed": 0,      # Default speed
                    "next_block": self.get_next_block(block_num),  # Calculate next block
                    "faulted": (row[3] == "Yes") if len(row) > 3 else False
                }

    def get_next_block(self, current_block):
        """Calculate next block number (simple sequential logic)"""
        try:
            current_num = int(current_block)
            return f"Block {current_num + 1}"
        except ValueError:
            return None

    def set_system_log(self, system_log):
        """Set reference to system log for message broadcasting"""
        self.system_log = system_log
    
    def broadcast_message(self, message):
        """Broadcast message to all connected UIs"""
        if self.system_log:
            # This would send to the test UI's system log
            pass

    def load_all_track_data(self):
        """Load track infrastructure data from TXT files, extracting real switch directions."""
        track_data = {
            "switches": {},
            "crossings": {},
            "lights": {}
        }

        txt_files = {
            "Blue": "data/blue_line.txt",
            "Green": "data/green_line.txt",
            "Red": "data/red_line.txt"
        }

        for line, file_path in txt_files.items():
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    for row_line in lines[1:]:
                        row = row_line.strip().split(',')
                        if len(row) >= 3:
                            block = row[1].strip()
                            infrastructure = row[2].strip()

                            # --- SWITCHES ---
                            if 'Switch' in infrastructure:
                                switch_name = f"Switch {block}"
                                directions = self.extract_switch_directions(infrastructure)
                                track_data["switches"][switch_name] = {
                                    "condition": "Normal Operation",
                                    "direction": directions[0] if directions else "Unknown",
                                    "options": directions,  # store list for UI
                                    "line": line
                                }

                            # --- RAILWAY CROSSINGS ---
                            if 'RAILWAY CROSSING' in infrastructure:
                                crossing_name = f"Railway {block}"
                                track_data["crossings"][crossing_name] = {
                                    "condition": "Normal Operation",
                                    "lights": "Off",
                                    "bar": "Opened",
                                    "line": line
                                }

                            # --- LIGHTS ---
                            if 'Light' in infrastructure and 'Switch' not in infrastructure:
                                light_name = f"Light {block}"
                                track_data["lights"][light_name] = {
                                    "condition": "Normal Operation",
                                    "signal": "Green",
                                    "line": line
                                }

            except FileNotFoundError:
                print(f"Warning: {file_path} not found. Skipping {line} line data.")

        return track_data

    def load_all_block_data(self):
        """Load all block data from TXT files"""
        all_block_data = []
        txt_files = {
            "Blue": "data/blue_line.txt",
            "Green": "data/green_line.txt",
            "Red": "data/red_line.txt"
        }
        
        for line, file_path in txt_files.items():
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    # Skip header line
                    for row_line in lines[1:]:
                        row = row_line.strip().split(',')
                        if len(row) >= 2:
                            # Each block starts as unoccupied
                            all_block_data.append(["No", line, row[1]])
            except FileNotFoundError:
                print(f"Warning: {file_path} not found. Skipping {line} block data.")
        
        return all_block_data

    def extract_switch_directions(self, infrastructure_text):
        """
        Extract switch directions directly from the text (e.g., 'Switch (12-13; 1-13)')
        Returns a list like ['12-13', '1-13'].
        """
        if not infrastructure_text:
            return []

        # Look inside parentheses first
        match = re.search(r'\((.*?)\)', infrastructure_text)
        if match:
            inside = match.group(1)
            # Split by ';' or ',' and strip spaces
            options = [opt.strip() for opt in re.split(r'[;,]', inside) if opt.strip()]
            return options

        # If no parentheses, look for patterns like "Switch TO YARD (57-yard)" or "Switch FROM YARD"
        options = []
        # Find patterns like 12-13 or 57-yard or yard-63
        found = re.findall(r'\b[\w]+\s*-\s*[\w]+\b', infrastructure_text)
        for f in found:
            clean = f.replace(" ", "")
            options.append(clean)

        # Add TO/FROM YARD words if they exist
        text_upper = infrastructure_text.upper()
        if "TO YARD" in text_upper:
            options.append("TO YARD")
        if "FROM YARD" in text_upper:
            options.append("FROM YARD")

        return options

    def update_fault_data(self, row_index, col_index, new_value):
        """Update fault data and keep original data in sync"""
        if 0 <= row_index < len(self.fault_data):
            self.fault_data[row_index][col_index] = new_value
            if 0 <= row_index < len(self.fault_data_original):
                self.fault_data_original[row_index][col_index] = new_value
    
    def update_block_data(self, row_index, col_index, new_value):
        """Update block data and keep original data in sync"""
        if 0 <= row_index < len(self.block_data):
            # Ensure row has 4 columns
            if len(self.block_data[row_index]) < 4:
                self.block_data[row_index].append("No")
            
            # Update the value
            self.block_data[row_index][col_index] = new_value
            
            # Keep original in sync
            if 0 <= row_index < len(self.block_data_original):
                if len(self.block_data_original[row_index]) < 4:
                    self.block_data_original[row_index].append("No")
                self.block_data_original[row_index][col_index] = new_value
            
            # Sync to filtered_track_data blocks
            block_num = str(self.block_data[row_index][2])
            line = self.block_data[row_index][1]
            block_key = f"Block {block_num}"
            
            if self.current_line == line and "blocks" in self.filtered_track_data:
                if block_key in self.filtered_track_data["blocks"]:
                    # If occupancy changed (col 0)
                    if col_index == 0:
                        is_occupied = (new_value == "Yes")
                        self.filtered_track_data["blocks"][block_key]["occupied"] = is_occupied
                    
                    # If faulted changed (col 3)
                    elif col_index == 3:
                        is_faulted = (new_value == "Yes")
                        self.filtered_track_data["blocks"][block_key]["faulted"] = is_faulted
            
            # Trigger callbacks
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"Callback error in update_block_data: {e}")
    
    def update_track_data(self, category, name, field, new_value):
        """Update track data and notify callbacks - FIXED VERSION"""
        if category in self.track_data and name in self.track_data[category]:
            self.track_data[category][name][field] = new_value
            
            # Also update filtered_track_data if it's for the current line
            item_line = self.track_data[category][name].get("line")
            if item_line == self.current_line:
                if category in self.filtered_track_data and name in self.filtered_track_data[category]:
                    self.filtered_track_data[category][name][field] = new_value
            
            # Notify listeners that data changed
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def update_block_in_track_data(self, block_num, field, value):
        """Update a specific block in track_data"""
        block_key = f"Block {block_num}"
        if "blocks" in self.filtered_track_data and block_key in self.filtered_track_data["blocks"]:
            self.filtered_track_data["blocks"][block_key][field] = value
            
            # Notify listeners
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"Callback error: {e}")

    def sync_block_occupancy_from_track(self):
        """Sync occupancy from track_data back to block_data"""
        if "blocks" not in self.filtered_track_data:
            return
            
        for block_key, block_info in self.filtered_track_data["blocks"].items():
            block_num = block_info.get("number")
            track_occupied = block_info.get("occupied", False)
            
            # Find and update corresponding block_data entry
            for idx, row in enumerate(self.block_data):
                if row[1] == self.current_line and str(row[2]) == str(block_num):
                    new_occupied_str = "Yes" if track_occupied else "No"
                    if row[0] != new_occupied_str:
                        self.update_block_data(idx, 0, new_occupied_str)
                    break

    def update_track_data_cross_line(self, category, track, block, field, value):
        """Update track data across different lines"""
        item_name = f"{category[:-1].capitalize()} {block}"  # "Light 5", "Switch 3", etc.
        
        # Update in main track_data
        if category in self.track_data and item_name in self.track_data[category]:
            self.track_data[category][item_name][field] = value
            
            # If this is for the current line, update filtered_track_data too
            item_line = self.track_data[category][item_name].get("line")
            if item_line == self.current_line:
                if category in self.filtered_track_data and item_name in self.filtered_track_data[category]:
                    self.filtered_track_data[category][item_name][field] = value
            
            # Trigger updates
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"Callback error: {e}")

    def debug_track_data(self, category, track, block):
        """Debug method to check track data state"""
        item_name = f"{category[:-1].capitalize()} {block}"
        print(f"DEBUG {category}: {item_name}")
        if category in self.track_data and item_name in self.track_data[category]:
            print(f"  Main data: {self.track_data[category][item_name]}")
        if category in self.filtered_track_data and item_name in self.filtered_track_data[category]:
            print(f"  Filtered: {self.filtered_track_data[category][item_name]}")

    def set_current_line(self, line):
        """Set the current active track and then filters the data"""
        if line != self.current_line:
            self.current_line = line
            self.filter_data_by_line(line)
            for callback in self.on_line_change:
                callback()
    
    def filter_data_by_line(self, line):
        """Filter all data to show only the current line"""
        self.current_line = line
        
        # Filter fault data
        self.fault_data = [row for row in self.fault_data_original 
                          if row[2] == line]
        
        # Filter block data  
        self.block_data = [row for row in self.block_data_original 
                          if row[1] == line]
        
        self.filtered_track_data = {
            "switches": {k: v for k, v in self.track_data["switches"].items() 
                        if v.get("line") == line},
            "crossings": {k: v for k, v in self.track_data["crossings"].items() 
                         if v.get("line") == line},
            "lights": {k: v for k, v in self.track_data["lights"].items() 
                      if v.get("line") == line}
        }
        
        # Reinitialize blocks for the new line
        self.filtered_track_data["blocks"] = {}
        self.initialize_track_blocks()

    def set_maintenance_mode(self, mode):
        self.maintenance_mode = mode
        for callback in self.on_maintenance_mode_change:
            callback()
    
    def set_test_mode(self, mode):
        self.test_mode = mode
        for callback in self.on_test_mode_change:
            callback()
    
    def filter_fault_data(self, search_term):
        if not search_term:
            self.fault_data = [row for row in self.fault_data_original 
                              if row[2] == self.current_line]
        else:
            self.fault_data = [row for row in self.fault_data_original 
                              if row[2] == self.current_line and 
                              any(search_term in str(cell).lower() for cell in row)]
        return self.fault_data
    
    def filter_block_data(self, search_term):
        if not search_term:
            self.block_data = [row for row in self.block_data_original 
                              if row[1] == self.current_line]
        else:
            self.block_data = [row for row in self.block_data_original 
                              if row[1] == self.current_line and 
                              any(search_term in str(cell).lower() for cell in row)]
        return self.block_data
    

###########################################################3
    def update_block_field(self, block_num, field, value):
        """Update a specific field in a block within filtered_track_data"""
        block_key = f"Block {block_num}"
        
        if "blocks" in self.filtered_track_data and block_key in self.filtered_track_data["blocks"]:
            self.filtered_track_data["blocks"][block_key][field] = value
            
            # If updating occupancy, also sync to block_data
            if field == "occupied":
                new_occupied_str = "Yes" if value else "No"
                for idx, row in enumerate(self.block_data):
                    if row[1] == self.current_line and str(row[2]) == str(block_num):
                        if row[0] != new_occupied_str:
                            self.block_data[idx][0] = new_occupied_str  # FIXED: was row_index, now idx
                            if idx < len(self.block_data_original):
                                self.block_data_original[idx][0] = new_occupied_str
                        break
            
            # If updating faulted, also sync to block_data
            if field == "faulted":
                new_faulted_str = "Yes" if value else "No"
                for idx, row in enumerate(self.block_data):
                    if row[1] == self.current_line and str(row[2]) == str(block_num):
                        # Ensure row has 4 columns
                        if len(row) < 4:
                            row.append("No")
                        if len(row) > 3 and row[3] != new_faulted_str:
                            self.block_data[idx][3] = new_faulted_str
                            if idx < len(self.block_data_original):
                                if len(self.block_data_original[idx]) < 4:
                                    self.block_data_original[idx].append("No")
                                self.block_data_original[idx][3] = new_faulted_str
                        break