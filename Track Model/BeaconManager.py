"""
Beacon Data Management for Track Model
Sends beacon information to trains when they occupy station blocks
"""

class BeaconData:
    def __init__(self, block_number, distance_to_next=None, next_station_name=None):
        """
        Initialize a BeaconData object.
       
        Args:
            block_number: The block number where this beacon is located
            distance_to_next: Distance to the next station (in meters)
            next_station_name: Name of the next station
        """
        self.block_number = block_number
        self.distance_to_next = distance_to_next
        self.next_station_name = next_station_name
    
    def to_dict(self):
        """Convert beacon data to dictionary for transmission"""
        return {
            "block_number": self.block_number,
            "distance_to_next": self.distance_to_next,
            "next_station_name": self.next_station_name
        }
    
    def __str__(self):
        return f"Beacon at Block {self.block_number}: Next station is {self.next_station_name} ({self.distance_to_next}m away)"


class BeaconManager:
    """Manages beacon data for all station blocks"""
    
    def __init__(self):
        # Initialize beacon data for Green Line stations
        self.beacons = {}
        self._initialize_green_line_beacons()
    
    def _initialize_green_line_beacons(self):
        """Initialize beacon data for Green Line stations"""
        
        # Create beacon instances with corrected station data
        # Format: BeaconData(block_number, distance_to_next_station, next_station_name)
        
        # Station beacon data based on Green Line layout
        self.beacons = {
            # Yard to Glenbury
            64: BeaconData(64, 2000, "Glenbury"),
            
            # Glenbury station blocks
            65: BeaconData(65, 800, "Dormont"),  # Glenbury station
            
            # Path to Dormont
            102: BeaconData(102, 800, "Dormont"),
            
            # Dormont station blocks  
            73: BeaconData(73, 700, "Mt Lebanon"),  # Dormont station
            
            # Path to Mt Lebanon
            97: BeaconData(97, 700, "Mt Lebanon"),
            
            # Mt Lebanon station blocks
            38: BeaconData(38, 600, "Poplar"),  # Mt Lebanon station
            39: BeaconData(39, 600, "Poplar"),  # Mt Lebanon station
            
            # Path to Poplar
            72: BeaconData(72, 600, "Poplar"),
            
            # Poplar station blocks
            48: BeaconData(48, 500, "Castle Shannon"),  # Poplar station
            49: BeaconData(49, 500, "Castle Shannon"),  # Poplar station
            
            # Path to Castle Shannon
            80: BeaconData(80, 500, "Castle Shannon"),
            
            # Castle Shannon station blocks
            60: BeaconData(60, 400, "South Hills Junction"),  # Castle Shannon station
            
            # Additional stations on Green Line
            22: BeaconData(22, 1500, "Overbrook"),  # Station before Overbrook
            31: BeaconData(31, 1200, "Inglewood"),  # Overbrook station
            105: BeaconData(105, 1000, "Central"),  # Inglewood station
            114: BeaconData(114, 900, "Whited"),  # Central station
            123: BeaconData(123, 800, "South Bank"),  # Whited station  
            132: BeaconData(132, 700, "Central"),  # South Bank station
            141: BeaconData(141, 0, "End of Line"),  # Final station
        }
        
        print(f"[BeaconManager] Initialized {len(self.beacons)} station beacons")
        for block, beacon in self.beacons.items():
            print(f"  Block {block}: Next station is {beacon.next_station_name} ({beacon.distance_to_next}m)")
    
    def get_beacon_data(self, block_number):
        """
        Get beacon data for a specific block
        
        Args:
            block_number: The block number to get beacon data for
            
        Returns:
            BeaconData object if block has a beacon, None otherwise
        """
        return self.beacons.get(block_number)
    
    def is_station_block(self, block_number):
        """
        Check if a block number is a station block with beacon
        
        Args:
            block_number: The block number to check
            
        Returns:
            True if block has beacon data, False otherwise
        """
        return block_number in self.beacons
    
    def format_beacon_message(self, block_number, train_id):
        """
        Format beacon data as a message to send to Train Model
        
        Args:
            block_number: The block number with beacon
            train_id: The train ID that triggered the beacon
            
        Returns:
            Dictionary formatted for transmission, or None if no beacon
        """
        beacon = self.get_beacon_data(block_number)
        if beacon:
            return {
                "command": "beacon_data",
                "train_id": train_id,
                "block_number": block_number,
                "beacon_info": {
                    "distance_to_next_station": beacon.distance_to_next,
                    "next_station_name": beacon.next_station_name,
                    "current_block": block_number
                }
            }
        return None


# Integration code for UI_Structure.py
def integrate_beacon_manager(ui_structure_instance):
    """
    Add beacon manager integration to UI_Structure class
    This should be called in the __init__ method of UI_Structure
    """
    
    # Create beacon manager instance
    ui_structure_instance.beacon_manager = BeaconManager()
    
    # Override or extend the send_block_occupancy_update method
    original_send = ui_structure_instance.send_block_occupancy_update
    
    def send_with_beacon(block_num, occupancy):
        """Enhanced send that includes beacon data when applicable"""
        # Call original send method
        original_send(block_num, occupancy)
        
        # If block is newly occupied and has beacon data
        if occupancy != 0 and ui_structure_instance.beacon_manager.is_station_block(block_num):
            train_id = f"Train_{occupancy}"
            beacon_message = ui_structure_instance.beacon_manager.format_beacon_message(block_num, train_id)
            
            if beacon_message:
                # Send beacon data to Train Model
                ui_structure_instance.server.send_to_ui("Train Model", beacon_message)
                print(f"📡 Sent beacon data for Block {block_num} to {train_id}")
                print(f"   Next station: {beacon_message['beacon_info']['next_station_name']}")
                print(f"   Distance: {beacon_message['beacon_info']['distance_to_next_station']}m")
                
                # Also send to Train SW for train controller
                ui_structure_instance.server.send_to_ui("Train SW", beacon_message)
    
    # Replace the method
    ui_structure_instance.send_block_occupancy_update = send_with_beacon
    
    print("[BeaconManager] Integrated with UI_Structure")


# Test function
def test_beacon_system():
    """Test the beacon system"""
    manager = BeaconManager()
    
    # Test some station blocks
    test_blocks = [64, 65, 73, 38, 48, 60, 999]
    
    for block in test_blocks:
        if manager.is_station_block(block):
            beacon = manager.get_beacon_data(block)
            print(f"✓ Block {block}: {beacon}")
            
            # Test message formatting
            message = manager.format_beacon_message(block, "Train_1")
            print(f"  Message: {message}")
        else:
            print(f"✗ Block {block}: No beacon data")


if __name__ == "__main__":
    test_beacon_system()


# YardToGlenbury1 = BeaconData(64, 2000, "Glenbury")
# Glenbury1ToDormont1 = BeaconData(102, 800, "Dormont")
# Dormont1ToMtLebanon = BeaconData(97, 700, "Mt Lebanon")
# MtLebanonToPoplar = BeaconData(72, 600, "Poplar")
# PoplarToCastleShannon = BeaconData(80, 500, "Castle Shannon")