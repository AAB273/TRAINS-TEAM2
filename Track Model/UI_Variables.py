import pandas as pd
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