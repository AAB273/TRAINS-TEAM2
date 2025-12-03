import os
import re

class RailwayData:
    def __init__(self):
        """Data model for railway control system - manages track data, blocks, and commands"""
        self.maintenance_mode = False
        self.current_line = "Green"  # Default line
        self.app = None
        
        # Callbacks for UI updates
        self.on_line_change = []  # Called when line changes
        self.on_maintenance_mode_change = []  # Called when maintenance mode changes
        self.on_data_update = []  # Called when any data updates (PLC/UI updates)

        #Section mapping based on  datasheet
        self.block_to_section = self.create_section_mapping()
        
        # Command and suggestion storage
        self.commanded_authority = {"Green": {}, "Red": {}}
        self.commanded_speed = {"Green": {}, "Red": {}}
        self.suggested_authority = {"Green": {}, "Red": {}}
        self.suggested_speed = {"Green": {}, "Red": {}}
        
        # SEPARATE variables for track infrastructure (no longer nested under track_data)
        self.light_states = {}
        self.switch_positions = {}
        self.railway_crossings = {}
        
        # Initialize data from TXT files
        self.load_all_track_data()  # This will populate the separate variables
        print("Track data loaded from files")
        
        # Initialize block data (contains occupancy AND fault status)
        self.block_data = self.load_all_block_data()
        print("Block data loaded from files")
        
        # Keep original data for filtering
        self.block_data_original = self.block_data.copy()

        self.ensure_faulted_column()  # Ensure all blocks have faulted status
        print("Faulted column ensured for all blocks")

        # Initialize filtered data structures for current line
        self.filtered_light_states = {}
        self.filtered_switch_positions = {}
        self.filtered_railway_crossings = {}
        self.filtered_blocks = {}
        
        self.filter_data_by_line(self.current_line)
        print("Track data filtered for current line")

        # System log reference for broadcasting messages
        self.system_log = None
        
    def create_section_mapping(self):
        """Create mapping from block numbers to section letters based on your data"""
        section_mapping = {}
        
        # Green Line sections (from your data)
        sections = {
            'A': [1, 2, 3],
            'B': [4, 5, 6], 
            'C': [7, 8, 9, 10, 11, 12],
            'D': [13, 14, 15, 16],
            'E': [17, 18, 19, 20],
            'F': [21, 22, 23, 24, 25, 26, 27, 28],
            'G': [29, 30, 31, 32],
            'H': [33, 34, 35],
            'I': [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57],
            'J': [58, 59, 60, 61, 62],
            'K': [63, 64, 65, 66, 67, 68],
            'L': [69, 70, 71, 72, 73],
            'M': [74, 75, 76],
            'N': [77, 78, 79, 80, 81, 82, 83, 84, 85],
            'O': [86, 87, 88],
            'P': [89, 90, 91, 92, 93, 94, 95, 96, 97],
            'Q': [98, 99, 100],
            'R': [101],
            'S': [102, 103, 104],
            'T': [105, 106, 107, 108, 109],
            'U': [110, 111, 112, 113, 114, 115, 116],
            'V': [117, 118, 119, 120, 121],
            'W': [122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141],
            'X': [144, 145, 146],
            'Y': [147, 148, 149],
            'Z': [150]
        }
        
        for section, blocks in sections.items():
            for block in blocks:
                section_mapping[f"Green-{block}"] = section
                # Add Red line if you have similar data for Red line
                # section_mapping[f"Red-{block}"] = section  
        
        return section_mapping
    
    def get_section_for_block(self, line, block_number):
        """Get section letter for a specific block"""
        return self.block_to_section.get(f"{line}-{block_number}", "Unknown")
    
    def get_blocks_in_section(self, line, section):
        """Get all blocks in a specific section"""
        blocks = []
        for key, sect in self.block_to_section.items():
            if sect == section and key.startswith(line):
                # Extract block number from key (format: "Green-1")
                block_num = key.split('-')[1]
                blocks.append(block_num)
        return blocks
    
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
        print("System log reference set")

    def load_all_track_data(self):
        """Load track infrastructure data from TXT files into separate variables."""
        # Clear existing data
        self.light_states = {}
        self.switch_positions = {}
        self.railway_crossings = {}

        # Map line names to their data files
        txt_files = {
            "Green": "Wayside_Controller/SW/data/green_line.txt", 
            "Red": "Wayside_Controller/SW/data/red_line.txt"
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
                print(f"Warning: {file_path} not found. Skipping {line} line data.")

    def load_all_block_data(self):
        """Load all block data from TXT files - each block starts unoccupied and not faulted"""
        all_block_data = []
        txt_files = {
            "Green": "Wayside_Controller/SW/data/green_line.txt", 
            "Red": "Wayside_Controller/SW/data/red_line.txt"
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
                print(f"Warning: {file_path} not found. Skipping {line} block data.")
        
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
                return
            
            # Update the value in the original data (source of truth)
            self.block_data_original[row_index][col_index] = new_value
            
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
                        break
            else:
                print(f"Not updating block_data (current: {self.current_line}, target: {current_line})")
            
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
                    
                    # If faulted changed (col 3)
                    elif col_index == 3:
                        is_faulted = (new_value == "Yes")
                        self.filtered_blocks[block_key]["faulted"] = is_faulted
            
            # Trigger callbacks to update UI components
            for callback in self.on_data_update:
                try:
                    callback()
                except Exception as e:
                    print(f"Callback error in update_block_data: {e}")
    
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
                
                # AUTO-SEND TO CTC FOR INFRASTRUCTURE CHANGES
                if self.app:  # Only if we have app reference
                    if category == "light_states" and field == "signal":
                        # Extract block number and send
                        block = name.split(" ")[1] if " " in name else name
                        self.app.send_light_state(item_line, block, new_value)
                        
                    elif category == "switch_positions" and field == "direction":
                        # Extract block number and send  
                        block = name.split(" ")[1] if " " in name else name
                        # Send switch state to CTC
                        ctc_message = {
                            "command": "SW",
                            "value": [block, new_value, item_line]
                        }
                        self.app.send_to_CTC(ctc_message)

                # Notify listeners that data changed
                for callback in self.on_data_update:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Callback error: {e}")
    
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
                    print(f"Callback error: {e}")

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
                        print(f"Callback error: {e}")

    def set_current_line(self, line):
        """Set the current active track and filter data to show only that line"""
        if line != self.current_line:
            self.current_line = line
            print(f"Switching to {line} line")
            self.filter_data_by_line(line)  # Filter all data for new line
            # Notify all listeners that line changed
            for callback in self.on_line_change:
                callback()
    
    def filter_data_by_line(self, line):
        """Filter all data to show only the current line - FIXED VERSION"""
        self.current_line = line
        
        # Filter block data to show only current line blocks  
        # This creates a COPY of the original data for the current line
        self.block_data = [row.copy() for row in self.block_data_original if row[1] == line]
        
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
        print(f"Data filtered for {line} line")

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



    #for PLC program
    @property
    def filtered_track_data(self):
        """Provide the track data structure expected by PLC code"""
        return {
            "crossings": self.filtered_railway_crossings,
            "switches": self.filtered_switch_positions,
            "lights": self.filtered_light_states, 
            "blocks": self.filtered_blocks
        }
