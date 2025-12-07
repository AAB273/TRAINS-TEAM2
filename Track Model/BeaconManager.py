"""
Beacon Data Management for Track Model
Sends 128-bit beacon arrays to trains when they depart from stations
"""

import random

class BeaconData:
    def __init__(self, block_number, station_name, beacon_array=None):
        """
        Initialize a BeaconData object with a unique 128-bit boolean array.
       
        Args:
            block_number: The block number where this beacon is located
            station_name: Name of the station
            beacon_array: Optional 128-bit boolean array. If None, generates random unique array.
        """
        self.block_number = block_number
        self.station_name = station_name
        
        # Generate or use provided 128-bit boolean array
        if beacon_array is None:
            self.beacon_array = self._generate_unique_beacon_array()
        else:
            assert len(beacon_array) == 128, "Beacon array must be exactly 128 bits"
            self.beacon_array = beacon_array
    
    def _generate_unique_beacon_array(self):
        """
        Generate a unique 128-bit boolean array for this beacon.
        Uses block number as seed for reproducibility.
        """
        # Use block number as seed for consistent generation
        rng = random.Random(self.block_number * 1000 + hash(self.station_name) % 1000)
        return [rng.choice([True, False]) for _ in range(128)]
    
    def to_dict(self):
        """Convert beacon data to dictionary for transmission"""
        return {
            "block_number": self.block_number,
            "station_name": self.station_name,
            "beacon_array": self.beacon_array  # 128-bit boolean array
        }
    
    def __str__(self):
        bits_preview = ''.join(['1' if b else '0' for b in self.beacon_array[:16]]) + "..."
        return f"Beacon at Block {self.block_number} ({self.station_name}): {bits_preview}"


class BeaconManager:
    """Manages 128-bit beacon data for all station blocks"""
    
    def __init__(self):
        # Dictionary mapping block_number -> BeaconData
        self.beacons = {}
        
    def initialize_station_beacons(self, station_location_list):
        """
        Initialize beacon data for all stations from the station_location list.
        
        Args:
            station_location_list: List of tuples (block_number, station_name)
        """
        self.beacons.clear()
        
        for block_number, station_name in station_location_list:
            # Create unique beacon for this station block
            self.beacons[block_number] = BeaconData(block_number, station_name)
        
        print(f"[BeaconManager] Initialized {len(self.beacons)} station beacons with 128-bit arrays")
    
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
    
    def get_beacon_array(self, block_number):
        """
        Get the 128-bit boolean array for a station block
        
        Args:
            block_number: The block number
            
        Returns:
            List of 128 booleans, or None if no beacon at this block
        """
        beacon = self.get_beacon_data(block_number)
        return beacon.beacon_array if beacon else None
    
    def format_beacon_message(self, block_number, train_id):
        """
        Format beacon data as a message to send to Train Model when train departs station
        
        Args:
            block_number: The block number with beacon
            train_id: The train ID that is departing
            
        Returns:
            Dictionary formatted for transmission, or None if no beacon
        """
        beacon = self.get_beacon_data(block_number)
        if beacon:
            return {
                "command": "Beacon Data",
                "train_id": train_id,
                "block_number": block_number,
                "station_name": beacon.station_name,
                "beacon_array": beacon.beacon_array  # 128-bit boolean array
            }
        return None


# Test function
def test_beacon_system():
    """Test the beacon system with 128-bit arrays"""
    manager = BeaconManager()
    
    # Test with sample stations
    test_stations = [
        (2, "PIONEER"),
        (9, "EDGEBROOK"),
        (16, "STATION"),
        (22, "WHITED"),
        (31, "SOUTH BANK"),
        (39, "CENTRAL"),
        (48, "INGLEWOOD"),
        (57, "OVERBROOK"),
        (65, "GLENBURY"),
        (73, "DORMONT"),
        (77, "MT LEBANON"),
        (88, "POPLAR"),
        (96, "CASTLE SHANNON"),
        (105, "DORMONT"),
        (114, "MT LEBANON"),
        (123, "POPLAR"),
        (132, "CASTLE SHANNON"),
        (141, "SOUTH HILLS JUNCTION")
    ]
    
    manager.initialize_station_beacons(test_stations)
    
    # Test beacon retrieval
    for block_num, station_name in test_stations[:3]:
        beacon = manager.get_beacon_data(block_num)
        if beacon:
            print(f"\n✓ {beacon}")
            print(f"  First 32 bits: {''.join(['1' if b else '0' for b in beacon.beacon_array[:32]])}")
            
            # Test message formatting
            message = manager.format_beacon_message(block_num, "Train_1")
            print(f"  Message command: {message['command']}")
            print(f"  Beacon array length: {len(message['beacon_array'])} bits")


if __name__ == "__main__":
    test_beacon_system()