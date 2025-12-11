"""
PLC Controller for Track Hardware - Green Line Sections A-J and Z
ACTUALLY INTEGRATES with Track_HW test_data to read inputs and control outputs

Sections Covered:
- Section A: Blocks 1-3 (includes Light 1)
- Section B: Blocks 4-6
- Section C: Blocks 7-12 (includes Switch 12-13)
- Section D: Blocks 13-16 (includes Light 13)
- Section E: Blocks 17-20 (includes Railway Crossing 19, Light 19)
- Section F: Blocks 21-28 (includes Switch 28-29, Light 28)
- Section G: Blocks 29-32
- Section H: Blocks 33-35
- Section I: Blocks 36-57 (includes Switch 57-Yard, Light 57)
- Section J: Blocks 58-62 (includes Switch 62-Yard)
- Section Z: Block 150
- Block 63 included for yard connection
"""

class PLCController:
    def __init__(self, log_callback=None):
        """
        Initialize PLC Controller for Green Line Sections A-J and Z
        
        Args:
            log_callback: Function to log messages to UI message_log
        """
        self.log = log_callback if log_callback else print
        
        # Reference to test_data - will be set by PLCManager
        self.test_data = None
        
        # Track line
        self.track = "Green"
        
        # =====================================================================
        # BLOCK DEFINITIONS - Sections A through J and Z
        # =====================================================================
        self.sections = {
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
            'Z': [150]
        }
        
        # All blocks in scope (A-J + Z + block 63)
        self.all_blocks = []
        for section_blocks in self.sections.values():
            self.all_blocks.extend(section_blocks)
        self.all_blocks.append(63)  # Include block 63 for yard connection
        
        # =====================================================================
        # INFRASTRUCTURE DEFINITIONS
        # =====================================================================
        
        # Switch locations with their track_data names
        self.switch_info = {
            12: {
                'name': 'Switch 12-13',
                'positions': ['Section D → A', 'Section D → C'],
                'connects': [13, 1],
                'numeric_positions': [0, 1]
            },
            28: {
                'name': 'Switch 28-29',
                'positions': ['Section F → G', 'Section Z → F'],
                'connects': [29, 150],
                'numeric_positions': [0, 1]
            },
            57: {
                'name': 'Switch 57-Yard',
                'positions': ['Section I → Yard', 'Section Yard → I'],
                'connects': [58, 'Yard'],
                'numeric_positions': [0, 1]
            },
            62: {
                'name': 'Switch 62-Yard',
                'positions': ['Section Yard → K', 'Section K → Yard'],
                'connects': [63, 'Yard'],
                'numeric_positions': [0, 1]
            }
        }
        
        # Light locations with their track_data names
        self.light_info = {
            1: {'name': 'Light 1', 'section': 'A'},
            13: {'name': 'Light 13', 'section': 'D'},
            19: {'name': 'Light 19', 'section': 'E'},
            28: {'name': 'Light 28', 'section': 'F'},
            57: {'name': 'Light 57', 'section': 'I'}
        }
        
        # Railway crossing locations
        self.crossing_info = {
            19: {'name': 'Railway Crossing: 19', 'section': 'E'}
        }
        
        self.log("PLC Controller initialized for Green Line Sections A-J and Z")

    # =========================================================================
    # INPUT READERS - Read actual data from test_data
    # =========================================================================
    
    def get_block_occupancy(self, block):
        """
        Read block occupancy from test_data.block_data
        
        Args:
            block: Block number
            
        Returns:
            Boolean - True if occupied
        """
        if not self.test_data:
            return False
        
        # block_data format: [Occupied, Line, Block, Section]
        for row in self.test_data.block_data:
            if str(row[2]) == str(block) and row[1] == self.track:
                return row[0] == "Yes"
        return False
    
    def get_block_fault(self, block):
        """
        Read block fault status from test_data.track_data
        Check if any infrastructure on this block has a fault
        
        Args:
            block: Block number
            
        Returns:
            Boolean - True if fault
        """
        if not self.test_data:
            return False
        
        track_data = self.test_data.track_data
        
        # Check switches for fault
        if block in self.switch_info:
            switch_name = self.switch_info[block]['name']
            if switch_name in track_data.get("switches", {}):
                return track_data["switches"][switch_name].get("fault", False)
        
        # Check lights for fault
        if block in self.light_info:
            light_name = self.light_info[block]['name']
            if light_name in track_data.get("lights", {}):
                return track_data["lights"][light_name].get("fault", False)
        
        # Check crossings for fault
        if block in self.crossing_info:
            crossing_name = self.crossing_info[block]['name']
            if crossing_name in track_data.get("crossings", {}):
                return track_data["crossings"][crossing_name].get("fault", False)
        
        return False
    
    def get_switch_position(self, block):
        """
        Read current switch position from test_data.track_data
        
        Args:
            block: Block number where switch is located
            
        Returns:
            Integer - 0 for first position, 1 for second position
        """
        if not self.test_data or block not in self.switch_info:
            return 0
        
        switch_name = self.switch_info[block]['name']
        track_data = self.test_data.track_data
        
        if switch_name in track_data.get("switches", {}):
            return track_data["switches"][switch_name].get("numeric_position", 0)
        return 0
    
    def get_light_state(self, block):
        """
        Read current light state from test_data.track_data
        
        Args:
            block: Block number where light is located
            
        Returns:
            String - 'Red', 'Yellow', 'Green', or 'Super Green'
        """
        if not self.test_data or block not in self.light_info:
            return 'Green'
        
        light_name = self.light_info[block]['name']
        track_data = self.test_data.track_data
        
        if light_name in track_data.get("lights", {}):
            return track_data["lights"][light_name].get("signal", "Green")
        return 'Green'
    
    def get_crossing_state(self, block):
        """
        Read current crossing state from test_data.track_data
        
        Args:
            block: Block number where crossing is located
            
        Returns:
            String - 'Active' or 'Inactive'
        """
        if not self.test_data or block not in self.crossing_info:
            return 'Inactive'
        
        crossing_name = self.crossing_info[block]['name']
        track_data = self.test_data.track_data
        
        if crossing_name in track_data.get("crossings", {}):
            bar = track_data["crossings"][crossing_name].get("bar", "Open")
            return 'Active' if bar == 'Closed' else 'Inactive'
        return 'Inactive'

    # =========================================================================
    # OUTPUT WRITERS - Write actual data to test_data and send to Track Model/CTC
    # =========================================================================
    
    def set_block_occupancy(self, block, occupied):
        """
        Update block occupancy in test_data.block_data
        
        Args:
            block: Block number
            occupied: Boolean - True if occupied
        """
        if not self.test_data:
            return
        
        occupied_str = "Yes" if occupied else "No"
        
        # Update block_data
        for i, row in enumerate(self.test_data.block_data):
            if str(row[2]) == str(block) and row[1] == self.track:
                old_value = row[0]
                self.test_data.block_data[i][0] = occupied_str
                if old_value != occupied_str:
                    self.log(f"Block {block}: Occupancy -> {occupied_str}")
                break
        
        # Send to CTC
        if hasattr(self.test_data, 'send_occupancy'):
            self.test_data.send_occupancy(self.track, str(block), occupied_str)
    
    def set_light_state(self, block, state):
        """
        Update light state in test_data.track_data and send to Track Model/CTC
        
        Args:
            block: Block number where light is located
            state: 'Red', 'Yellow', 'Green', or 'Super Green'
        """
        if not self.test_data or block not in self.light_info:
            return
        
        light_name = self.light_info[block]['name']
        track_data = self.test_data.track_data
        
        # Update track_data
        if "lights" not in track_data:
            track_data["lights"] = {}
        if light_name not in track_data["lights"]:
            track_data["lights"][light_name] = {"condition": "Normal", "signal": "Green", "fault": False}
        
        old_state = track_data["lights"][light_name].get("signal", "Green")
        track_data["lights"][light_name]["signal"] = state
        
        if old_state != state:
            self.log(f"Light {block}: {old_state} -> {state}")
        
        # Send to Track Model and CTC
        if hasattr(self.test_data, 'send_light_state'):
            self.test_data.send_light_state(self.track, str(block), state)
    
    def set_switch_position(self, block, position):
        """
        Update switch position in test_data.track_data and send to Track Model
        
        Args:
            block: Block number where switch is located
            position: 0 for first position, 1 for second position
        """
        if not self.test_data or block not in self.switch_info:
            return False
        
        # Safety check
        if not self.check_switch_safety(block):
            return False
        
        switch_name = self.switch_info[block]['name']
        positions = self.switch_info[block]['positions']
        direction = positions[position] if position < len(positions) else positions[0]
        
        track_data = self.test_data.track_data
        
        # Update track_data
        if "switches" not in track_data:
            track_data["switches"] = {}
        if switch_name not in track_data["switches"]:
            track_data["switches"][switch_name] = {"condition": "Normal", "direction": positions[0], "numeric_position": 0, "fault": False}
        
        old_position = track_data["switches"][switch_name].get("numeric_position", 0)
        old_direction = positions[old_position] if old_position < len(positions) else positions[0]
        
        track_data["switches"][switch_name]["direction"] = direction
        track_data["switches"][switch_name]["numeric_position"] = position
        
        if old_position != position:
            self.log(f"Switch {block}: {old_direction} -> {direction}")
        
        # Send to Track Model
        if hasattr(self.test_data, 'send_switch_to_track_model'):
            self.test_data.send_switch_to_track_model(self.track, str(block), direction)
        
        return True
    
    def set_crossing_state(self, block, state):
        """
        Update crossing state in test_data.track_data and send to Track Model/CTC
        
        Args:
            block: Block number where crossing is located
            state: 'Active' or 'Inactive'
        """
        if not self.test_data or block not in self.crossing_info:
            return
        
        crossing_name = self.crossing_info[block]['name']
        bar = 'Closed' if state == 'Active' else 'Open'
        lights = 'On' if state == 'Active' else 'Off'
        
        track_data = self.test_data.track_data
        
        # Update track_data
        if "crossings" not in track_data:
            track_data["crossings"] = {}
        if crossing_name not in track_data["crossings"]:
            track_data["crossings"][crossing_name] = {"condition": "Normal", "bar": "Open", "lights": "Off", "fault": False}
        
        old_bar = track_data["crossings"][crossing_name].get("bar", "Open")
        track_data["crossings"][crossing_name]["bar"] = bar
        track_data["crossings"][crossing_name]["lights"] = lights
        
        if old_bar != bar:
            self.log(f"Railway Crossing {block}: Bar {bar.upper()}")
        
        # Send to Track Model and CTC
        if hasattr(self.test_data, 'send_railway_state'):
            self.test_data.send_railway_state(self.track, str(block), bar)
            
    def receive_ctc_authority(self, block, authority_value, destination_hint=0):
        """ Process CTC authority message destination_hint: 0=normal, 1=station, 2=yard, 3=back to yard"""
        self.log(f"CTC Authority received: Block {block}, Authority {authority_value}, Destination hint: {destination_hint}")
    
    # Store CTC's original authority
        self.ctc_authority_received[block] = {
            'original': authority_value,
            'destination': destination_hint
        }
    
    # If destination hint is 3 (back to yard), handle specially
        if destination_hint == 3:
            self.log(f"TRAIN DESTINATION: Block {block} going back to YARD")
            self.handle_yard_return(block, authority_value)
        else:
        # Normal progression - set initial authority
            self.block_authority[block] = authority_value
        
        # Propagate authority forward
            self.propagate_authority_forward(block, authority_value)
    
    # Update track model authority array
        self.update_track_model_authority_array()

    def handle_yard_return(self, start_block, authority_value):
        """Special handling for trains returning to yard"""
    # Find blocks on the path to yard (assuming block 57 is yard connection)
        yard_path = self.find_path_to_yard(start_block)
    
        if not yard_path:
            self.log(f"ERROR: Could not find path to yard from block {start_block}")
            return
    
        self.log(f"Yard return path: {yard_path}")
    
    # Set decreasing authority along the path
        current_auth = authority_value
        for i, block in enumerate(yard_path):
        # Blocks 9 and 58 get authority 1 if present in path
            if block in [9, 58]:
                self.block_authority[block] = 1
            else:
                self.block_authority[block] = current_auth
                current_auth = max(0, current_auth - 1)
    
    # Block 55 (before switch to yard) gets authority 1
        if 55 in self.block_authority:
            self.block_authority[55] = 1

    def find_path_to_yard(self, start_block):
        """Find path from start_block to yard (block 57)
        Simple implementation - adjust based on your actual track layout
        """
    # This is a simplified path finder - you'll need to customize based on your track layout
        try:
            start_block = int(start_block)
            if start_block < 57:
            # Blocks before yard
                return list(range(start_block, 58))
            else:
            # Blocks after yard
                return list(range(start_block, 56, -1)) + [57]
        except:
            return []

    def propagate_authority_forward(self, start_block, authority_value):
        """ Propagate decreasing authority forward from start block """
        try:
            start = int(start_block)
            current_auth = authority_value
        
        # Propagate forward 3 blocks (or until authority reaches 0)
            for i in range(3):
                next_block = start + i + 1
            
            # Check if block exists in our system
                if next_block in self.all_blocks:
                    self.block_authority[next_block] = current_auth - 1
                    current_auth -= 1
            
                if current_auth <= 0:
                    break
        except Exception as e:
            self.log(f"Error propagating authority: {e}")

    def update_authority_for_occupancy(self):
        """
        Update authority values based on block occupancy
        Reset speed to 25 mph for unoccupied blocks
        """
        if not self.test_data:
            return
    
    # Reset authority array
        self.track_model_authority_array = []
    
    # Process all blocks in order
        for block in sorted(self.all_blocks):
        # Check if block is occupied
            occupied = self.get_block_occupancy(block)
        
            if occupied:
            # Occupied block - get current authority or use default
                current_auth = self.block_authority.get(block, 0)
            # Decrease authority for next cycle
                if current_auth > 0:
                    self.block_authority[block] = current_auth - 1
            
                self.track_model_authority_array.append({
                'block': block,
                'authority': current_auth,
                'speed': 0,  # Stop or slow speed for occupied blocks
                'occupied': True
                })
            
            # Log the progression
                if current_auth == 0:
                    self.log(f"Block {block}: Train arrived, authority = 0")
                else:
                    self.log(f"Block {block}: Authority decreasing to {current_auth - 1}")
        
            else:
            # Unoccupied block - reset speed to 25 mph
            # Check if this block has pending authority from CTC
                if block in self.block_authority:
                # Use the decreasing authority value
                    auth_value = self.block_authority[block]
                    self.track_model_authority_array.append({
                    'block': block,
                    'authority': auth_value,
                    'speed': 25,  # Default speed for unoccupied blocks
                    'occupied': False
                    })
                else:
                # No authority assigned, default to 0
                    self.track_model_authority_array.append({
                    'block': block,
                    'authority': 0,
                    'speed': 25,  # Reset to 25 mph for unoccupied blocks
                    'occupied': False
                    })
    def send_authority_to_track_model(self):
        """
        Send authority array for all blocks to Track Model
        """
        if not self.test_data or not hasattr(self.test_data, 'send_to_track_model'):
            return
    
    # Ensure we have updated authority data
        self.update_authority_for_occupancy()
    
    # Create the authority array message
        authority_array = []
        for item in self.track_model_authority_array:
            authority_array.append({
            'block': item['block'],
            'authority': item['authority'],
            'suggested_speed': item['speed']
            })
    
    # Send to Track Model
        track_model_message = {
        "command": "authority_array",
        "value": authority_array,
        "timestamp": time.time(),
        "line": self.track
        }
    
        try:
            self.test_data.send_to_track_model(track_model_message)
            self.log(f"Sent authority array for {len(authority_array)} blocks to Track Model")
        except Exception as e:
            self.log(f"Error sending authority array to Track Model: {e}")

    def update_track_model_authority_array(self):
        """
        Update and send the authority array immediately
        """
        self.update_authority_for_occupancy()
        self.send_authority_to_track_model()
    # =========================================================================
    # PLC SAFETY LOGIC
    # =========================================================================
    
    def check_switch_safety(self, block):
        """
        Check if it's safe to change a switch
        
        Args:
            block: Block number where switch is located
            
        Returns:
            Boolean - True if safe to change
        """
        # Cannot change switch if the switch block is occupied
        if self.get_block_occupancy(block):
            self.log(f"SAFETY: Cannot change switch {block} - block OCCUPIED")
            return False
        
        # Cannot change switch if there's a fault
        if self.get_block_fault(block):
            self.log(f"SAFETY: Cannot change switch {block} - FAULT detected")
            return False
        
        # Check adjacent blocks for approaching trains
        if block in self.switch_info:
            connects = self.switch_info[block].get('connects', [])
            for connected in connects:
                if isinstance(connected, int) and self.get_block_occupancy(connected):
                    self.log(f"SAFETY: Cannot change switch {block} - train approaching from block {connected}")
                    return False
        
        return True

    # =========================================================================
    # PLC CONTROL LOGIC - Automatic calculations
    # =========================================================================
    def run_cycle_quiet(self):
        """Run PLC cycle - only logs state changes"""
    # Existing light logic
        for block in self.light_info.keys():
            current_state = self.get_light_state(block)
            calculated_state = self.calculate_light_state(block)
            if current_state != calculated_state:
                self.set_light_state(block, calculated_state)
    
    # Existing crossing logic
        for block in self.crossing_info.keys():
            current_state = self.get_crossing_state(block)
            calculated_state = self.calculate_crossing_state(block)
            if current_state != calculated_state:
                self.set_crossing_state(block, calculated_state)
    
    # NEW: Update authority based on occupancy
        self.update_authority_for_occupancy()
    
    # NEW: Send authority array to Track Model
        self.send_authority_to_track_model()
    
    # Existing switch safety check
        for block in self.switch_info.keys():
            if self.get_block_fault(block):
                self.log(f"ALERT: Switch {block} has FAULT")
    
    def calculate_light_state(self, block):
        """
        Calculate what the light state should be based on occupancy
        
        Args:
            block: Block number where light is located
            
        Returns:
            String - 'Red', 'Yellow', 'Green', or 'Super Green'
        """
        # If there's a fault on this block, always Red
        if self.get_block_fault(block):
            return 'Red'
        
        # If this block is occupied, Red
        if self.get_block_occupancy(block):
            return 'Red'
        
        # Define which blocks are "ahead" for each light
        blocks_ahead_map = {
            1: [2, 3, 4],           # Light 1 (Section A)
            13: [14, 15, 16, 17],   # Light 13 (Section D)
            19: [20, 21, 22],       # Light 19 (Section E - at crossing)
            28: [29, 30, 31],       # Light 28 (Section F - at switch)
            57: [58, 59, 60]        # Light 57 (Section I - at yard switch)
        }
        
        check_blocks = blocks_ahead_map.get(block, [])
        
        # Count clear blocks ahead
        blocks_ahead_clear = 0
        for check_block in check_blocks:
            if not self.get_block_occupancy(check_block) and not self.get_block_fault(check_block):
                blocks_ahead_clear += 1
            else:
                break  # Stop counting if we hit an occupied/faulted block
        
        # Determine light color based on blocks ahead clear
        if blocks_ahead_clear == 0:
            return 'Red'
        elif blocks_ahead_clear == 1:
            return 'Yellow'
        elif blocks_ahead_clear == 2:
            return 'Green'
        else:
            return 'Super Green'
    
    def calculate_crossing_state(self, block):
        """
        Calculate railway crossing state based on approaching trains
        
        Args:
            block: Block number where crossing is located
            
        Returns:
            String - 'Active' or 'Inactive'
        """
        # If there's a fault, activate crossing for safety
        if self.get_block_fault(block):
            return 'Active'
        
        # Check if train is on the crossing block
        if self.get_block_occupancy(block):
            return 'Active'
        
        # Check approaching blocks (2 blocks before and after crossing at block 19)
        approaching_blocks = [17, 18, 20, 21]
        
        for approach_block in approaching_blocks:
            if self.get_block_occupancy(approach_block):
                return 'Active'
        
        return 'Inactive'

    # =========================================================================
    # MAIN PLC CYCLE
    # =========================================================================
    
    def main(self):
        """
        Main entry point - runs PLC logic cycle
        Called by PLCManager.run_plc()
        
        This method:
        1. Reads current state from test_data
        2. Applies PLC logic
        3. Updates test_data with new states
        4. Sends outputs to Track Model and CTC
        """
        self.log("=" * 50)
        self.log("PLC CYCLE - Green Line Sections A-J, Z")
        self.log("=" * 50)
        
        # Get reference to test_data from global scope
        try:
            import __main__
            if hasattr(__main__, 'test_data'):
                self.test_data = __main__.test_data
                self.log("Connected to Track HW test_data")
            else:
                self.log("WARNING: test_data not found - running in simulation mode")
        except:
            self.log("WARNING: Could not access test_data - running in simulation mode")
        
        # =====================================================================
        # READ CURRENT STATE
        # =====================================================================
        self.log("\n--- Reading Current State ---")
        
        # Read occupancy for all blocks in scope
        occupied_blocks = []
        for block in self.all_blocks:
            if self.get_block_occupancy(block):
                occupied_blocks.append(block)
        
        if occupied_blocks:
            self.log(f"Occupied blocks: {occupied_blocks}")
        else:
            self.log("No blocks occupied")
        
        # Check for faults
        faulted_blocks = []
        for block in list(self.switch_info.keys()) + list(self.light_info.keys()) + list(self.crossing_info.keys()):
            if self.get_block_fault(block):
                faulted_blocks.append(block)
        
        if faulted_blocks:
            self.log(f"FAULTS detected on blocks: {faulted_blocks}")
        
        # =====================================================================
        # APPLY PLC LOGIC
        # =====================================================================
        self.log("\n--- Applying PLC Logic ---")
        
        # Process LIGHTS - Calculate and set appropriate states
        for block in self.light_info.keys():
            current_state = self.get_light_state(block)
            calculated_state = self.calculate_light_state(block)
            
            if current_state != calculated_state:
                self.set_light_state(block, calculated_state)
        
        # Process RAILWAY CROSSINGS - Activate/deactivate based on approaching trains
        for block in self.crossing_info.keys():
            current_state = self.get_crossing_state(block)
            calculated_state = self.calculate_crossing_state(block)
            
            if current_state != calculated_state:
                self.set_crossing_state(block, calculated_state)
        
        # Process SWITCHES - Check for safety issues (don't auto-change, just report)
        for block in self.switch_info.keys():
            if self.get_block_fault(block):
                self.log(f"ALERT: Switch {block} has FAULT - manual intervention required")
            elif self.get_block_occupancy(block):
                self.log(f"ALERT: Switch {block} is OCCUPIED - locked")
        
        # =====================================================================
        # REPORT FINAL STATE
        # =====================================================================
        self.log("\n--- Final State ---")
        
        # Report lights
        self.log("LIGHTS:")
        for block, info in self.light_info.items():
            state = self.get_light_state(block)
            fault = " [FAULT]" if self.get_block_fault(block) else ""
            self.log(f"  Block {block} ({info['section']}): {state}{fault}")
        
        # Report switches
        self.log("SWITCHES:")
        for block, info in self.switch_info.items():
            position = self.get_switch_position(block)
            direction = info['positions'][position]
            fault = " [FAULT]" if self.get_block_fault(block) else ""
            safe = " [SAFE]" if self.check_switch_safety(block) else " [LOCKED]"
            self.log(f"  Block {block}: {direction}{fault}{safe}")
        
        # Report crossings
        self.log("CROSSINGS:")
        for block, info in self.crossing_info.items():
            state = self.get_crossing_state(block)
            bar = "CLOSED" if state == 'Active' else "OPEN"
            fault = " [FAULT]" if self.get_block_fault(block) else ""
            self.log(f"  Block {block}: Bar {bar}{fault}")
        
        self.log("\n" + "=" * 50)
        self.log("PLC CYCLE COMPLETE")
        self.log("=" * 50)