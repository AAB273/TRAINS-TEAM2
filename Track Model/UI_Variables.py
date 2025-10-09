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

        print("Initialized station_location:", self.station_location)
        print("Initialized ticket_sales:", self.ticket_sales)
        print("Initialized passengers_boarding:", self.passengers_boarding)
        print("Initialized passengers_disembarking:", self.passengers_disembarking)


    # ---------------- Excel Data Loading ----------------
    def load_excel_data(self, track_path=None, train_path=None):
        """Load data from Excel files; fallback to defaults if missing."""
        if not track_path or not train_path:
            print("No Excel files provided. Using default blank data.")
            self._create_default_blocks()
            return True

        try:
            track_df = pd.read_excel(track_path)
            train_df = pd.read_excel(train_path)

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
                self.blocks.append(b)

            # Load train data
            self.active_trains = train_df["Train ID"].tolist() if "Train ID" in train_df else []
            self.train_occupancy = train_df["Occupancy"].tolist() if "Occupancy" in train_df else []
            self.commanded_speed = train_df["Commanded Speed"].tolist() if "Commanded Speed" in train_df else []
            self.commanded_authority = train_df["Commanded Authority"].tolist() if "Commanded Authority" in train_df else []

            print("Excel data loaded successfully.")
            return True

        except Exception as e:
            print(f"❌ Error loading Excel data: {e}")
            self._create_default_blocks()
            return False

    def _create_default_blocks(self):
        """Create 15 default track blocks."""
        from Track_Blocks import Block
        self.blocks = [
            Block(block_number=i+1, length=50, grade=0, elevation=0, speed_limit=50, track_heater=[0, 1])
            for i in range(15)
        ]


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

    # ---------------- Helper Accessors ----------------
    def get_active_trains(self):
        """Convenience method to quickly fetch active train list."""
        return self.get_data()["active_trains"]

    def get_blocks(self):
        """Get current track block list."""
        return self.get_data()["blocks"]