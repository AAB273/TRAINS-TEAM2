import os
import re

class RailwayData:
    def __init__(self):
        """Data model for railway control system - manages track data, blocks, and commands"""
        self.maintenance_mode = False
        self.current_line = "Blue"  # Default line
        
        # Callbacks for UI updates
        self.on_line_change = []  # Called when line changes
        self.on_maintenance_mode_change = []  # Called when maintenance mode changes
        self.on_data_update = []  # Called when any data updates (PLC/UI updates)
        
        # Command and suggestion storage
        self.commanded_authority = {"Blue": {}, "Green": {}, "Red": {}}
        self.commanded_speed = {"Blue": {}, "Green": {}, "Red": {}}
        self.suggested_authority = {"Blue": {}, "Green": {}, "Red": {}}
        self.suggested_speed = {"Blue": {}, "Green": {}, "Red": {}}
        
        # SEPARATE variables for track infrastructure (no longer nested under track_data)
        self.light_states = {}
        self.switch_positions = {}
        self.railway_crossings = {}
        
        # Initialize data from TXT files
        self.load_all_track_data()  # This will populate the separate variables
        print("📊 Track data loaded from files")
        
        # Initialize block data (contains occupancy AND fault status)
        self.block_data = self.load_all_block_data()
        print("🔧 Block data loaded from files")
        
        # Keep original data for filtering
        self.block_data_original = self.block_data.copy()

        self.ensure_faulted_column()  # Ensure all blocks have faulted status
        print("✅ Faulted column ensured for all blocks")

        # Initialize filtered data structures for current line
        self.filtered_light_states = {}
        self.filtered_switch_positions = {}
        self.filtered_railway_crossings = {}
        self.filtered_blocks = {}
        
        self.filter_data_by_line(self.current_line)
        print("🎯 Track data filtered for current line")

        # System log reference for broadcasting messages
        self.system_log = None

    def ensure_faulted_column(self):
        """Ensure all blocks have the Faulted column (index 3) for data consistency"""
        for row in self.block_data:
            if len(row) < 4:
                row.append("No")  # Default to not faulted
        for row in self.block_data_original:
            if len(row) < 4:
                row.append("No")  # Default to not faulted

    def initialize_track_blocks(self):
        """Initialize blocks with proper structure for PLC processing"""
        self.filtered_blocks = {}
        
        for row in self.block_data:
            if row[1] == self.current_line:  # Only current line
                block_num = str(row[2])
                block_key = f"Block {block_num}"
                
                # Create block structure with all necessary fields for PLC logic
                self.filtered_blocks[block_key] = {
                    "number": block_num,
                    "occupied": (row[0] == "Yes"),  # Convert "Yes"/"No" to boolean
                    "position": int(block_num),     # Simple position based on block number
                    "authority": 0,                 # Default authority (will be set by commands)
                    "speed": 0,                     # Default speed (will be set by commands)
                    "next_block": self.get_next_block(block_num),  # Calculate next block
                    "faulted": (row[3] == "Yes") if len(row) > 3 else False  # Fault status from block data
                }

    def get_next_block(self, current_block):
        """Calculate next block number (simple sequential logic)"""
        try:
            current_num = int(current_block)
            return f"Block {current_num + 1}"  # Simple increment for sequential blocks
        except ValueError:
            return None  # Handle non-numeric block numbers

    def set_system_log(self, system_log):
        """Set reference to system log for message broadcasting"""
        self.system_log = system_log
        print("📝 System log reference set")

    def load_all_track_data(self):
        """Load track infrastructure data from TXT files into separate variables."""
        # Clear existing data
        self.light_states = {}
        self.switch_positions = {}
        self.railway_crossings = {}

        # Map line names to their data files
        txt_files = {
            "Blue": "data/blue_line.txt",
            "Green": "data/green_line.txt", 
            "Red": "data/red_line.txt"
        }

        for line, file_path in txt_files.items():
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    # Skip header line (index 0) and process data lines
                    for row_line in lines[1:]:
                        row = row_line.strip().split(',')
                        if len(row) >= 3:  # Ensure we have at least block and infrastructure data
                            block = row[1].strip()
                            infrastructure = row[2].strip()

                            # --- SWITCHES ---
                            if 'Switch' in infrastructure:
                                switch_name = f"Switch {block}"
                                directions = self.extract_switch_directions(infrastructure)
                                self.switch_positions[switch_name] = {
                                    "condition": "Normal Operation",
                                    "direction": directions[0] if directions else "Unknown",
                                    "options": directions,  # Store all possible directions for UI
                                    "line": line  # Track which line this switch belongs to
                                }

                            # --- RAILWAY CROSSINGS ---
                            if 'RAILWAY CROSSING' in infrastructure:
                                crossing_name = f"Railway {block}"
                                self.railway_crossings[crossing_name] = {
                                    "condition": "Normal Operation",
                                    "lights": "Off",    # Default state
                                    "bar": "Opened",    # Default state  
                                    "line": line        # Track which line this crossing belongs to
                                }

                            # --- LIGHTS ---
                            if 'Light' in infrastructure and 'Switch' not in infrastructure:
                                light_name = f"Light {block}"
                                self.light_states[light_name] = {
                                    "condition": "Normal Operation",
                                    "signal": "Green",  # Default signal state
                                    "line": line        # Track which line this light belongs to
                                }

            except FileNotFoundError:
                print(f"⚠️ Warning: {file_path} not found. Skipping {line} line data.")

    def load_all_block_data(self):
        """Load all block data from TXT files - each block starts unoccupied and not faulted"""
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
                    # Skip header line and process each block
                    for row_line in lines[1:]:
                        row = row_line.strip().split(',')
                        if len(row) >= 2:  # Need at least block number
                            # Each block starts as unoccupied and not faulted: 
                            # ["No", line, block_number, "No"]
                            all_block_data.append(["No", line, row[1], "No"])
            except FileNotFoundError:
                print(f"⚠️ Warning: {file_path} not found. Skipping {line} block data.")
        
        return all_block_data

    def extract_switch_directions(self, infrastructure_text):
        """
        Extract switch directions directly from the text (e.g., 'Switch (12-13; 1-13)')
        Returns a list like ['12-13', '1-13'].
        """
        if not infrastructure_text:
            return []

        # Look inside parentheses first - most common format
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
            clean = f.replace(" ", "")  # Remove spaces
            options.append(clean)

        # Add TO/FROM YARD words if they exist in the text
        text_upper = infrastructure_text.upper()
        if "TO YARD" in text_upper:
            options.append("TO YARD")
        if "FROM YARD" in text_upper:
            options.append("FROM YARD")

        return options

    
    def update_block_data(self, row_index, col_index, new_value):
        """Update block data and keep original data in sync - FIXED VERSION"""
        if 0 <= row_index < len(self.block_data_original):
            # Ensure row has 4 columns (occupied, line, block, faulted)
            if len(self.block_data_original[row_index]) < 4:
                self.block_data_original[row_index].append("No")
            
            # Store the old value for comparison
            old_value = self.block_data_original[row_index][col_index]
            
            # Only update if the value is actually changing
            if old_value == new_value:
                print(f"🔄 DEBUG: No change needed - block_data_original[{row_index}][{col_index}] already '{new_value}'")
                return
            
            # Update the value in the original data (source of truth)
            self.block_data_original[row_index][col_index] = new_value
            print(f"📝 DEBUG: Updated block_data_original[{row_index}][{col_index}] from '{old_value}' to '{new_value}'")
            
            # Also update the filtered data if we're currently viewing that line
            current_line = self.block_data_original[row_index][1]
            if current_line == self.current_line:
                # Find the corresponding row in block_data and update it
                for idx, filtered_row in enumerate(self.block_data):
                    if (filtered_row[1] == current_line and 
                        str(filtered_row[2]) == str(self.block_data_original[row_index][2])):
                        if len(filtered_row) < 4:
                            filtered_row.append("No")
                        filtered_row[col_index] = new_value
                        print(f"📝 DEBUG: Also updated block_data[{idx}][{col_index}] to '{new_value}'")
                        break
            else:
                print(f"📝 DEBUG: Not updating block_data (current: {self.current_line}, target: {current_line})")
            
            # Sync to filtered_blocks for PLC processing
            block_num = str(self.block_data_original[row_index][2])
            line = self.block_data_original[row_index][1]
            block_key = f"Block {block_num}"
            
            if self.current_line == line and hasattr(self, 'filtered_blocks'):
                if block_key in self.filtered_blocks:
                    # If occupancy changed (col 0)
                    if col_index == 0:
                        is_occupied = (new_value == "Yes")
                        self.filtered_blocks[block_key]["occupied"] = is_occupied
                        print(f"📝 DEBUG: Updated filtered_blocks['{block_key}']['occupied'] to {is_occupied}")
                    
                    # If faulted changed (col 3)
                    elif col_index == 3:
                        is_faulted = (new_value == "Yes")
                        self.filtered_blocks[block_key]["faulted"] = is_faulted
                        print(f"📝 DEBUG: Updated filtered_blocks['{block_key}']['faulted'] to {is_faulted}")
            
            # Trigger callbacks to update UI components
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"❌ Callback error in update_block_data: {e}")
    
    def update_track_data(self, category, name, field, new_value):
        """Update track data and notify callbacks - used for switches, crossings, lights"""
        # Map category names to the correct instance variables
        category_map = {
            "switch_positions": self.switch_positions,
            "railway_crossings": self.railway_crossings, 
            "light_states": self.light_states
        }
        
        if category in category_map:
            data_dict = category_map[category]
            if name in data_dict:
                # Update main data
                data_dict[name][field] = new_value
                
                # Also update filtered data if it's for the current line
                item_line = data_dict[name].get("line")
                if item_line == self.current_line:
                    # Map category to filtered variable names
                    filtered_map = {
                        "switch_positions": self.filtered_switch_positions,
                        "railway_crossings": self.filtered_railway_crossings,
                        "light_states": self.filtered_light_states
                    }
                    if category in filtered_map and name in filtered_map[category]:
                        filtered_map[category][name][field] = new_value
                
                # Notify listeners that data changed
                for callback in self.on_data_update:
                    try:
                        callback()
                    except Exception as e:
                        print(f"❌ Callback error: {e}")
    
    def update_block_in_track_data(self, block_num, field, value):
        """Update a specific block in track_data - used by PLC"""
        block_key = f"Block {block_num}"
        if hasattr(self, 'filtered_blocks') and block_key in self.filtered_blocks:
            self.filtered_blocks[block_key][field] = value
            
            # Notify listeners (UI components) that data changed
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"❌ Callback error: {e}")

    def sync_block_occupancy_from_track(self):
        """Sync occupancy from track_data back to block_data - ensures consistency"""
        if not hasattr(self, 'filtered_blocks'):
            return
            
        for block_key, block_info in self.filtered_blocks.items():
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
        """Update track data across different lines - used for cross-line operations"""
        item_name = f"{category[:-1].capitalize()} {block}"  # "Light 5", "Switch 3", etc.
        
        # Map category names to the correct instance variables
        category_map = {
            "switch_positions": self.switch_positions,
            "railway_crossings": self.railway_crossings,
            "light_states": self.light_states
        }
        
        if category in category_map:
            data_dict = category_map[category]
            if item_name in data_dict:
                data_dict[item_name][field] = value
                
                # If this is for the current line, update filtered data too
                item_line = data_dict[item_name].get("line")
                if item_line == self.current_line:
                    filtered_map = {
                        "switch_positions": self.filtered_switch_positions,
                        "railway_crossings": self.filtered_railway_crossings,
                        "light_states": self.filtered_light_states
                    }
                    if category in filtered_map and item_name in filtered_map[category]:
                        filtered_map[category][item_name][field] = value
                
                # Trigger UI updates
                for callback in self.on_data_update:
                    try:
                        callback()
                    except Exception as e:
                        print(f"❌ Callback error: {e}")

    def set_current_line(self, line):
        """Set the current active track and filter data to show only that line"""
        if line != self.current_line:
            self.current_line = line
            print(f"🔄 Switching to {line} line")
            self.filter_data_by_line(line)  # Filter all data for new line
            # Notify all listeners that line changed
            for callback in self.on_line_change:
                callback()
    
    def filter_data_by_line(self, line):
        """Filter all data to show only the current line - FIXED VERSION"""
        self.current_line = line
        
        # Debug: Check what's in block_data_original for this line
        green_blocks = [row for row in self.block_data_original if row[1] == "Green"]
        print(f"📊 DEBUG: block_data_original has {len(green_blocks)} Green blocks")
        for row in green_blocks[:3]:  # Show first 3 blocks
            print(f"📊 DEBUG:   Block {row[2]}: {row}")
        
        # Filter block data to show only current line blocks  
        # This creates a COPY of the original data for the current line
        self.block_data = [row.copy() for row in self.block_data_original if row[1] == line]
        print(f"📊 DEBUG: Filtered {len(self.block_data)} blocks for {line} line from block_data_original")
        
        # Show what we filtered
        for row in self.block_data[:3]:  # Show first 3 blocks
            print(f"📊 DEBUG:   Filtered Block {row[2]}: {row}")
        
        # Filter track infrastructure data into separate filtered variables
        self.filtered_light_states = {k: v for k, v in self.light_states.items() 
                                    if v.get("line") == line}
        self.filtered_switch_positions = {k: v for k, v in self.switch_positions.items() 
                                        if v.get("line") == line}
        self.filtered_railway_crossings = {k: v for k, v in self.railway_crossings.items() 
                                        if v.get("line") == line}
        
        # Reinitialize blocks for the new line
        self.filtered_blocks = {}
        self.initialize_track_blocks()
        print(f"✅ Data filtered for {line} line")

    def set_maintenance_mode(self, mode):
        """Set maintenance mode and notify all UI components"""
        self.maintenance_mode = mode
        mode_text = "activated" if mode else "deactivated"
        print(f"🔧 Maintenance mode {mode_text}")
        for callback in self.on_maintenance_mode_change:
            callback()
    
    def filter_block_data(self, search_term):
        """Filter block data based on search term"""
        if not search_term:
            # No search term - show all blocks for current line
            self.block_data = [row for row in self.block_data_original 
                              if row[1] == self.current_line]
        else:
            # Filter blocks that match search term in any cell
            self.block_data = [row for row in self.block_data_original 
                              if row[1] == self.current_line and 
                              any(search_term in str(cell).lower() for cell in row)]
        return self.block_data

    def update_block_field(self, block_num, field, value):
        """Update a specific field in a block within filtered_track_data"""
        block_key = f"Block {block_num}"
        
        if hasattr(self, 'filtered_blocks') and block_key in self.filtered_blocks:
            self.filtered_blocks[block_key][field] = value
            
            # If updating occupancy, also sync to block_data
            if field == "occupied":
                new_occupied_str = "Yes" if value else "No"
                for idx, row in enumerate(self.block_data):
                    if row[1] == self.current_line and str(row[2]) == str(block_num):
                        if row[0] != new_occupied_str:
                            self.block_data[idx][0] = new_occupied_str
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