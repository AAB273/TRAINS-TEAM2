import pandas as pd
import random
from Track_Blocks import Block

class TrackDataManager:
    def __init__(self):
        # ---------------- Core Data ----------------
        self.blocks = []
        self.active_trains = []
        self.train_occupancy = []
        self.commanded_speed = []
        self.commanded_authority = []
        self.environmental_temp = None

        # ADD THIS: Bidirectional block directions
        self.bidirectional_directions = {
            "Blocks 13-28": 0,  # 0 = left, 1 = right
            "Blocks 77-85": 0
        }

        # ---------------- Switch Routing Configurations ----------------
        # GREEN LINE SWITCHES
        self.switch_routing_green = {
            12: {"normal": 13, "reverse": 13},    # Switch housed at 12: (12-13; 1-13)
            28: {"normal": 29, "reverse": 150},   # Switch housed at 28: (28-29; 150-28)
            57: {"normal": 58, "reverse": 151},   # Switch at 58: controls 57→58 (normal) or 57→yard 151 (reverse)
            62: {"normal": 63, "reverse": 63},    # Switch housed at 62: from main line or yard to 63
            76: {"normal": 78, "reverse": 101},   # Switch housed at 76: controls junction at 77 (76-77-78 or 76-77-101)
            85: {"normal": 86, "reverse": 100}    # Switch housed at 85: (85-86; 100-85)
        }
        
        # RED LINE SWITCHES
        # Based on Excel: Switch notation (X-Y; Z-W) means block can route to Y (normal) or W (reverse)
        self.switch_routing_red = {
            9: {"normal": 10, "reverse": 75},     # Yard: continue to 10 (normal) or to yard block 75 (reverse)
            15: {"normal": 16, "reverse": 1},     # Loop switch: 15→16 (normal) or 15→1 (reverse, closes loop)
            27: {"normal": 28, "reverse": 76},    # Branch: 27→28 (normal) or 27→76 (reverse, to end section)
            32: {"normal": 33, "reverse": 72},    # Branch: 32→33 (normal) or 32→72 (reverse, backward jump)
            38: {"normal": 39, "reverse": 71},    # Branch: 38→39 (normal) or 38→71 (reverse, backward jump)
            43: {"normal": 44, "reverse": 67},    # Branch: 43→44 (normal) or 43→67 (reverse, backward jump)
            52: {"normal": 53, "reverse": 66},    # Loop switch: 52→53 (normal) or 52→66 (reverse, forward jump)
            # Bidirectional entries for loop switches (allows entering from either direction)
            1: {"normal": 2, "reverse": 16},      # From block 1: go to 2 (normal) or to 16 via switch 15 (reverse)
            16: {"normal": 17, "reverse": 15},    # From block 16: go to 17 (normal) or to 15 (reverse, can then go to 1)
            53: {"normal": 54, "reverse": 52},    # From block 53: go to 54 (normal) or back to 52 via switch (reverse)
            66: {"normal": 67, "reverse": 52},    # From block 66: go to 67 (normal) or back to 52 via switch (reverse)
        }

        # ---------------- Infrastructure Sets ----------------
        self.switch_blocks = set()
        self.crossing_blocks = set()
        self.station_blocks = set()
        self.switch_states = {}  # Dictionary to track switch states {block_num: direction}

        # Traffic light blocks (hardcoded based on track layout)
        # Green Line: {1, 62, 76, 100, 150}
        # Red Line: {1, 10, 15, 28, 32, 39, 43, 53, 66, 67, 71, 72, 76}
        self.green_line_lights = {1, 62, 76, 100, 150}
        self.red_line_lights = {1, 10, 15, 28, 32, 39, 43, 53, 66, 67, 71, 72, 76}
        self.light_states = {1, 10, 15, 28, 32, 39, 43, 53, 62, 66, 67, 71, 72, 76, 100, 150}  # Combined for backward compatibility

        # ---------------- Default Track Setup ----------------
        self._create_default_blocks()
        num_blocks = len(self.blocks)

        # ---------------- Station Data ----------------
        # station_location stays as a short list of stations
        self.station_location = [(10, "Station B"), (15, "Station C")]

        # Make full-length lists for all blocks
        self.ticket_sales = [0] * num_blocks
        self.passengers_boarding = [0] * num_blocks
        self.passengers_disembarking = [0] * num_blocks

        # Pre-fill default station data into full-length lists
        for block_num, _ in self.station_location:
            idx = block_num - 1  # zero-based index
            self.ticket_sales[idx] = 0
            self.passengers_boarding[idx] = 0
            self.passengers_disembarking[idx] = 0


    # ---------------- Excel Data Loading ----------------
    def load_excel_data(self, track_path=None, train_path=None):
        """Load data from Excel files; fallback to defaults if missing."""
        if not track_path:  # Only check track_path
            self._create_default_blocks()
            return True

        try:
            track_df = pd.read_excel(track_path)
            
            # Clear old data
            self.blocks = []

            # Load track data
            for _, row in track_df.iterrows():
                b = Block(
                    grade=row.get("Block Grade (%)", 0.0),
                    elevation=row.get("ELEVATION (M)", 0.0),
                    length=row.get("Block Length (m)", 0.0),
                    speed_limit=row.get("Speed Limit (Km/Hr)", 0.0),
                    track_heater=False,
                    beacon=False,
                )
                b.failure_mode = None
                b.traversable = True
                self.blocks.append(b)

            # Load train data if provided
            if train_path:
                train_df = pd.read_excel(train_path)
                self.active_trains = train_df["Train ID"].tolist() if "Train ID" in train_df else []
                self.train_occupancy = train_df["Occupancy"].tolist() if "Occupancy" in train_df else []
                self.commanded_speed = train_df["Commanded Speed"].tolist() if "Commanded Speed" in train_df else []
                self.commanded_authority = train_df["Commanded Authority"].tolist() if "Commanded Authority" in train_df else []

            return True

        except Exception as e:
            # print(f"❌ Error loading Excel data: {e}")
            self._create_default_blocks()
            return False

    def _create_default_blocks(self):
        """Create 15 default track blocks."""
        from Track_Blocks import Block
        self.blocks = []
        for i in range(15):
            block = Block(
                block_number=i+1, 
                length=50, 
                grade=0, 
                elevation=0, 
                speed_limit=50, 
                track_heater=[0, 1],  # OFF but WORKING
                beacon=[0]*128  # Default 128-bit beacon
            )
            # Initialize failure mode attributes
            block.failure_mode = None
            block.traversable = True
            self.blocks.append(block)

    # ---------------- Infrastructure Management ----------------
    def populate_infrastructure_sets(self):
        """Populate switch_blocks, crossing_blocks, and station_blocks from loaded Excel data"""
        # Clear existing sets
        self.switch_blocks.clear()
        self.crossing_blocks.clear()
        self.station_blocks.clear()
        
        # Get infrastructure data from data manager
        infra_map = getattr(self, "infrastructure_data", {})
        
        # print("[TrackDataManager] Populating infrastructure sets from Excel data...")
        
        for block_num, infrastructure in infra_map.items():
            infrastructure_upper = str(infrastructure).upper()
            
            # Check for switches
            if "SWITCH" in infrastructure_upper:
                self.switch_blocks.add(block_num)
                # print(f"   Found switch at block {block_num}")
                
                # Initialize switch direction for this block
                if 1 <= block_num <= len(self.blocks):
                    block = self.blocks[block_num - 1]
                    if not hasattr(block, 'switch_direction'):
                        # SPECIAL CASE: Block 62 must default to 'reverse' for yard spawning
                        if block_num == 62:
                            block.switch_direction = 'reverse'  # Yard→63 position
                        else:
                            block.switch_direction = 'normal'  # Default direction
                    # Also initialize in switch_states dictionary
                    self.switch_states[block_num] = getattr(block, 'switch_direction', 'normal')
            
            # Check for crossings
            if "CROSSING" in infrastructure_upper:
                self.crossing_blocks.add(block_num)
                # print(f"   Found crossing at block {block_num}")
            
            # Check for stations
            if "STATION" in infrastructure_upper:
                self.station_blocks.add(block_num)
                # print(f"  🚉 Found station at block {block_num}")
        
        # print(f"[TrackDataManager] Infrastructure summary:")
        # print(f"  Switches: {sorted(self.switch_blocks)}")
        # print(f"  Crossings: {sorted(self.crossing_blocks)}")
        # print(f"  Stations: {sorted(self.station_blocks)}")
        # print(f"  Signals (hardcoded): {sorted(self.light_states)}")

    def initialize_station_ticket_sales(self):
        """Initialize random ticket sales and boarding/disembarking for all stations."""
        # print("🎫 === INITIALIZING STATION DATA ===")
        
        # Ensure arrays are the correct length
        num_blocks = len(self.blocks)
        self.ticket_sales = [0] * num_blocks
        self.passengers_boarding = [0] * num_blocks
        self.passengers_disembarking = [0] * num_blocks
        
        for block_num, station_name in self.station_location:
            idx = block_num - 1
            if 0 <= idx < num_blocks:
                # Generate random ticket sales between 0-70
                ticket_count = random.randint(0, 70)
                self.ticket_sales[idx] = ticket_count
                
                # Generate random boarding count (0 to ticket_sales)
                boarding_count = random.randint(0, ticket_count)
                self.passengers_boarding[idx] = boarding_count
                
                # print(f"   Station {station_name} (Block {block_num}): {ticket_count} tickets, {boarding_count} boarding")
        
        # print("   === STATION DATA INITIALIZATION COMPLETE ===\n")

    def update_station_ticket_sales(self):
        """Update ticket sales for all stations - called during refresh"""
        for block_num, station_name in self.station_location:
            idx = block_num - 1
            if 0 <= idx < len(self.ticket_sales):
                current_tickets = self.ticket_sales[idx]
                
                # Only increase if below max
                if current_tickets < 50:
                    # Generate random increase between 0 and 7
                    new_tickets = random.randint(0, 7)
                    
                    # Add new tickets but don't exceed max of 50
                    self.ticket_sales[idx] = min(current_tickets + new_tickets, 50)
                    
                    if new_tickets > 0:
                        pass
                        # print(f"🎫 {station_name} (Block {block_num}): {current_tickets} → {self.ticket_sales[idx]} (+{new_tickets})")

    def update_station_boarding_data(self):
        """Update boarding data for all stations - called during refresh"""
        for block_num, _ in self.station_location:
            idx = block_num - 1
            if 0 <= idx < len(self.passengers_boarding):
                # Boarding data increases as more passengers arrive
                current_boarding = self.passengers_boarding[idx]
                current_tickets = self.ticket_sales[idx]
                
                # Passengers waiting can board (transfer from tickets to boarding)
                if current_tickets > 0:
                    # Random number of passengers decide to board (0 to min(3, available))
                    boarding_now = random.randint(0, min(3, current_tickets))
                    if boarding_now > 0:
                        self.passengers_boarding[idx] += boarding_now
                        self.ticket_sales[idx] -= boarding_now

    def initialize_bidirectional_directions(self, line="Green Line"):
        """Initialize bidirectional block directions based on the current line (Green or Red)."""
        if line == "Red Line":
            # Red Line bidirectional blocks
            self.bidirectional_directions = {
                "Blocks 1-15": 0,
                "Blocks 16-27": 0,
                "Blocks 28-32": 0,
                "Blocks 33-37": 0,
                "Blocks 38-43": 0,
                "Blocks 44-52": 0,
                "Blocks 53-66": 0,
                "Blocks 67-71": 0,
                "Blocks 72-76": 0
            }
        else:
            # Green Line bidirectional blocks
            self.bidirectional_directions = {
                "Blocks 13-28": 0,  # 0 = left, 1 = right
                "Blocks 77-85": 0
            }

    def get_current_switch_routing(self, line="Green Line"):
        """Get the switch routing for the current line."""
        if "Red" in line:
            return self.switch_routing_red
        else:
            return self.switch_routing_green

    # ---------------- Data Access ----------------
    def get_data(self):
        """Return current data in dict form for UI."""
        return {
            "blocks": self.blocks,
            "environmental_temp": self.environmental_temp,
            "active_trains": self.active_trains,
            "train_occupancy": self.train_occupancy,
            "commanded_speed": self.commanded_speed,
            "commanded_authority": self.commanded_authority,
            "station_location": self.station_location,
            "ticket_sales": self.ticket_sales,
            "passengers_boarding": self.passengers_boarding,
            "passengers_disembarking": self.passengers_disembarking,
            "switch_blocks": self.switch_blocks,
            "crossing_blocks": self.crossing_blocks,
            "station_blocks": self.station_blocks,
            "light_states": self.light_states,
        }
    
    def collect_outputs_to_send(self):
        """Collect all block data for output transmission."""
        outputs_to_send = [
            "ticket_sales", "passengers_disembarking", "occupancy",
            "commanded_speed", "commanded_authority", "beacon",
            "failure_mode", "passengers_boarding", "traversable"
        ]
        
        data_to_send = []
        for b in self.blocks:
            block_data = {}
            for attr in outputs_to_send:
                # Handle attributes stored in manager vs block
                if attr in ["ticket_sales", "passengers_boarding", "passengers_disembarking"]:
                    block_idx = b.block_number - 1
                    if 0 <= block_idx < len(getattr(self, attr, [])):
                        block_data[attr] = getattr(self, attr)[block_idx]
                    else:
                        block_data[attr] = 0
                else:
                    block_data[attr] = getattr(b, attr, None)
            data_to_send.append(block_data)
        
        return data_to_send

    # ---------------- Helper Accessors ----------------
    def get_active_trains(self):
        """Convenience method to quickly fetch active train list."""
        return self.get_data()["active_trains"]

    def get_blocks(self):
        """Get current track block list."""
        return self.get_data()["blocks"]