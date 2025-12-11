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

        #for plc
        self.plc_filter_active = False
        self.plc_filtered_blocks = []  # Store blocks filtered by PLC
        self.plc_filter_sections = []

        # Initialize section mapping from TXT files
        self.block_to_section = self.load_section_mapping_from_files()
        
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
        
        # Initialize block data (contains occupancy)
        self.block_data = self.load_all_block_data()
        print("Block data loaded from files")
        
        # Keep original data for filtering
        self.block_data_original = self.block_data.copy()

        # Initialize filtered data structures for current line
        self.filtered_light_states = {}
        self.filtered_switch_positions = {}
        self.filtered_railway_crossings = {}
        self.filtered_blocks = {}
        
        self.filter_data_by_line(self.current_line)
        print("Track data filtered for current line")

        # System log reference for broadcasting messages
        self.system_log = None
        
    def load_section_mapping_from_files(self):
        """Load section mapping from TXT files instead of hardcoding"""
        section_mapping = {}
        txt_files = {
            "Green": "Wayside_Controller/SW/data/green_line.txt", 
            "Red": "Wayside_Controller/SW/data/red_line.txt"
        }
        
        for line_name, file_path in txt_files.items():
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    # Check if file has section column (4 columns means it has section)
                    if len(lines) > 0:
                        headers = lines[0].strip().split(',')
                        has_section_column = len(headers) >= 4 and headers[2].lower() == 'section'
                        
                        if has_section_column:
                            # Process data lines (skip header)
                            for row_line in lines[1:]:
                                row = row_line.strip().split(',')
                                if len(row) >= 4:  # Line,Block,Section,Infrastructure
                                    block = row[1].strip()
                                    section = row[2].strip()
                                    if block and section:  # Make sure we have valid data
                                        section_mapping[f"{line_name}-{block}"] = section
                        else:
                            print(f"Warning: {file_path} doesn't have section column.")
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
        return sorted(blocks, key=lambda x: int(x))
    
    def initialize_track_blocks(self):
        """Initialize blocks with proper structure for PLC processing"""
        self.filtered_blocks = {}
        
        for row in self.block_data:
            if row[1] == self.current_line:  # Only current line
                block_num = str(row[2])
                block_key = f"Block {block_num}"
                
                # Get section for this block
                section = self.get_section_for_block(self.current_line, block_num)
                
                # Create block structure with all necessary fields for PLC logic
                self.filtered_blocks[block_key] = {
                    "number": block_num,
                    "section": section,
                    "occupied": (row[0] == "Yes"),  # Convert "Yes"/"No" to boolean
                    "position": int(block_num),     # Simple position based on block number
                    "authority": 0,                 # Default authority (will be set by commands)
                    "speed": 0,                     # Default speed (will be set by commands)
                }


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
                    if len(lines) > 0:
                        headers = lines[0].strip().split(',')
                        has_section_column = len(headers) >= 4 and headers[2].lower() == 'section'
                        
                        # Skip header line (index 0) and process data lines
                        for row_line in lines[1:]:
                            row = row_line.strip().split(',')
                            
                            if has_section_column:
                                # New format with sections: Line,Block,Section,Infrastructure
                                if len(row) >= 4:
                                    block = row[1].strip()
                                    section = row[2].strip()
                                    infrastructure = row[3].strip()
                                else:
                                    continue
                            else:
                                # Old format without sections: Line,Block,Infrastructure
                                if len(row) >= 3:
                                    block = row[1].strip()
                                    section = self.get_section_for_block(line, block)  # Get from mapping
                                    infrastructure = row[2].strip()
                                else:
                                    continue

                            # --- SWITCHES ---
                            if 'Switch' in infrastructure:
                                switch_name = f"Switch {block}"
                                directions = self.extract_switch_directions(infrastructure)
                                
                                #set first direction as the default
                                default_direction = directions[0] if directions else "Unknown"
                                
                                # Initialize numeric position (1 for first/default)
                                numeric_position = 1
                                
                                self.switch_positions[switch_name] = {
                                    "condition": default_direction,
                                    "direction": default_direction,
                                    "options": directions,  # Store all possible directions for UI
                                    "line": line,  # Track which line this switch belongs to
                                    "numeric_position": numeric_position,  # ADD THIS LINE
                                    "section": section  # Store section info
                                }

                            # --- RAILWAY CROSSINGS ---
                            if 'RAILWAY CROSSING' in infrastructure:
                                crossing_name = f"Railway {block}"
                                self.railway_crossings[crossing_name] = {
                                    "condition": "Normal Operation",
                                    "lights": "Off",    # Default state
                                    "bar": "Open",    # Default state  
                                    "line": line,        # Track which line this crossing belongs to
                                    "section": section   # Store section info
                                }

                            # --- LIGHTS ---
                            if 'Light' in infrastructure and 'Switch' not in infrastructure:
                                light_name = f"Light {block}"
                                self.light_states[light_name] = {
                                    "condition": "Normal Operation",
                                    "signal": "Green",  # Default signal state
                                    "line": line,        # Track which line this light belongs to
                                    "section": section   # Store section info
                                }

            except FileNotFoundError:
                print(f"Warning: {file_path} not found. Skipping {line} line data.")

    def load_all_block_data(self):
        """Load all block data from TXT files - each block starts unoccupied"""
        all_block_data = []
        txt_files = {
            "Green": "Wayside_Controller/SW/data/green_line.txt", 
            "Red": "Wayside_Controller/SW/data/red_line.txt"
        }
        
        for line, file_path in txt_files.items():
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    if len(lines) > 0:
                        headers = lines[0].strip().split(',')
                        has_section_column = len(headers) >= 4 and headers[2].lower() == 'section'
                        
                        # Skip header line and process each block
                        for row_line in lines[1:]:
                            row = row_line.strip().split(',')
                            
                            if has_section_column:
                                # New format: Line,Block,Section,Infrastructure
                                if len(row) >= 2:
                                    # Each block starts as unoccupied: 
                                    # ["No", line, block_number, "No"]
                                    block_num = row[1].strip()
                                    all_block_data.append(["No", line, block_num, "No"])
                            else:
                                # Old format: Line,Block,Infrastructure
                                if len(row) >= 2:
                                    block_num = row[1].strip()
                                    all_block_data.append(["No", line, block_num, "No"])
            except FileNotFoundError:
                print(f"Warning: {file_path} not found. Skipping {line} block data.")
        
        return all_block_data

    # ... (rest of your methods remain the same - only need to update the methods above)

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
            # Ensure row has 3 columns (occupied, line, block)
            if len(self.block_data_original[row_index]) < 3:
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
                        if self.app:  # Only if we have app reference
                                self.app.send_occupancy(current_line, block_num, new_value)
                            
                    
            
            # Trigger callbacks to update UI components
            for callback in self.on_data_update:
                callback()
    
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
                
                # For switches, update numeric position when direction changes
                if category == "switch_positions" and field == "direction":
                    # Calculate numeric position (1 for first option, 2 for second, etc.)
                    switch_data = data_dict[name]
                    options = switch_data.get("options", [])
                    if new_value in options:
                        numeric_position = options.index(new_value) + 1  # 1-based index
                        switch_data["numeric_position"] = numeric_position
                        
                        # SEND SWITCH POSITION TO TRACK MODEL HERE
                        if self.app:
                            block = name.split(" ")[1] if " " in name else name
                            item_line = data_dict[name].get("line")
                            self.app.send_switch_to_track_model(item_line, block, numeric_position)
                            print(f"✓ Switch {block} on {item_line} sent to track model with position: {numeric_position}")
                
                # AUTO-SEND TO CTC FOR INFRASTRUCTURE CHANGES
                if self.app:  # Only if we have app reference
                    if category == "light_states" and field == "signal":
                        # Extract block number and send
                        block = name.split(" ")[1] if " " in name else name
                        self.app.send_light_state(item_line, block, new_value)
                
                    elif category == "railway_crossings":
                        # Extract block number and send  
                        block = name.split(" ")[1] if " " in name else name
                        # Get current crossing state
                        crossing_data = data_dict[name]
                        lights_state = crossing_data.get("lights", "Off")
                        bar_state = crossing_data.get("bar", "Open")
                        # Send crossing state to CTC
                        self.app.send_railway_state(item_line, block, bar_state)

                # Notify listeners that data changed
                for callback in self.on_data_update:
                    callback()
                    
    
    def update_block_in_track_data(self, block_num, field, value):
        """Update a specific block in track_data - used by PLC"""
        block_key = f"Block {block_num}"
        if hasattr(self, 'filtered_blocks') and block_key in self.filtered_blocks:
            self.filtered_blocks[block_key][field] = value
            
            # Notify listeners (UI components) that data changed
            for callback in self.on_data_update:
                callback()
                

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
                    callback()
                    

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
        """Filter all data to show only the current line - FIXED for no duplicates"""
        self.current_line = line
        
        if self.plc_filter_active and hasattr(self, 'plc_filter_sections'):
            # Use PLC filter logic
            self.apply_plc_filter()  # This now properly handles deduplication
            self.block_data = self.plc_filtered_blocks
        else:
            # No PLC filter - show all blocks for current line
            self.block_data = []
            seen_blocks = set()
            
            for row in self.block_data_original:
                if row[1] == line:
                    block_num = str(row[2])
                    block_id = f"{line}-{block_num}"
                    
                    if block_id not in seen_blocks:
                        self.block_data.append(row.copy())
                        seen_blocks.add(block_id)
        
        # Filter infrastructure data
        self.filtered_light_states = {
            k: v for k, v in self.light_states.items() 
            if v.get("line") == line and (
                not self.plc_filter_active or 
                v.get("section", "Unknown") in self.plc_filter_sections
            )
        }
        
        self.filtered_switch_positions = {
            k: v for k, v in self.switch_positions.items() 
            if v.get("line") == line and (
                not self.plc_filter_active or 
                v.get("section", "Unknown") in self.plc_filter_sections
            )
        }
        
        self.filtered_railway_crossings = {
            k: v for k, v in self.railway_crossings.items() 
            if v.get("line") == line and (
                not self.plc_filter_active or 
                v.get("section", "Unknown") in self.plc_filter_sections
            )
        }
        
        # Reinitialize blocks for the new line
        self.initialize_track_blocks()
        #print(f"Data filtered for {line} line - {len(self.block_data)} blocks")

    def set_maintenance_mode(self, mode):
        """Set maintenance mode and notify all UI components"""
        self.maintenance_mode = mode
        mode_text = "activated" if mode else "deactivated"
        #print(f"Maintenance mode {mode_text}")
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
    
    def enable_plc_filter(self, sections):
        """
        Enable PLC filtering for specific sections
        sections: list of section letters from PLC
        """
        self.plc_filter_active = True
        self.plc_filter_sections = sections  # Store sections from PLC
        
        # Apply filter and trigger line filtering
        self.apply_plc_filter()
        self.filter_data_by_line(self.current_line)  # This will filter everything
        
    def disable_plc_filter(self):
        """"Disable PLC filtering, show all blocks"""
        self.plc_filter_active = False
        
        # Reset to show all blocks for current line
        self.block_data = [row.copy() for row in self.block_data_original 
                        if row[1] == self.current_line]
        
        # Trigger UI refresh to show all blocks
        for callback in self.on_data_update:
            callback()

    def apply_plc_filter(self):
        """Apply PLC filter without creating duplicate blocks"""
        if not self.plc_filter_active or not self.plc_filter_sections:
            return
        
        # Create a set to track unique blocks we've added
        seen_blocks = set()
        filtered_rows = []
        
        # Get all blocks for current line
        for row in self.block_data_original:
            if row[1] == self.current_line:  # Only current line
                block_num = str(row[2])
                
                # Create unique identifier
                block_id = f"{self.current_line}-{block_num}"
                
                # Skip if we've already seen this block
                if block_id in seen_blocks:
                    continue
                
                # Get section for this block
                section = self.get_section_for_block(self.current_line, block_num)
                
                # Get current occupancy from filtered_blocks
                block_key = f"Block {block_num}"
                is_occupied = False
                
                if block_key in self.filtered_blocks:
                    is_occupied = self.filtered_blocks[block_key].get("occupied", False)
                else:
                    # Fallback to original data
                    is_occupied = (row[0] == "Yes")
                
                # Show if: occupied OR in PLC sections
                should_show = is_occupied or (section in self.plc_filter_sections)
                
                if should_show:
                    # Create new row with current state
                    row_copy = row.copy()
                    row_copy[0] = "Yes" if is_occupied else "No"
                    filtered_rows.append(row_copy)
                    seen_blocks.add(block_id)
        
        # Update the filtered data
        self.plc_filtered_blocks = filtered_rows
        
        # Sync with main block_data for display
        self.block_data = filtered_rows.copy()
        
        #print(f"PLC filter applied: {len(filtered_rows)} blocks shown")