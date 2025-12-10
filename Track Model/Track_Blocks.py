# Block Class

class Block:
    # Represents a single track block with physical and operational attributes.
    
    """
    Attributes:
        block_number: Unique identifier for the block
        grade: Block gradient in percentage
        elevation: Block elevation in meters
        length: Block length in meters
        speed_limit: Speed limit in km/hr
        track_heater: 2-bit list [on/off, working/broken]
        beacon: 128-bit list for train communication
        switch_state: Boolean indicating switch position
        crossing: Boolean indicating presence of railroad crossing
        signal: Signal state for traffic control
        occupancy: Train occupancy status (0=empty, 1=occupied)
    """
    
    def __init__(self, block_number, grade=0.0, elevation=0.0, length=0.0,
                 speed_limit=0.0, track_heater=False, beacon=None,
                 switch_state=False, crossing=False, signal=None, occupancy=0):
        # Initializes a track block with all physical and operational parameters.
        self.block_number = block_number
        self.grade = grade
        self.elevation = elevation
        self.length = length
        self.speed_limit = speed_limit
        
        # Track heater as 2-bit list
        if isinstance(track_heater, list) and len(track_heater) == 2:
            self.track_heater = track_heater
        else:
            self.track_heater = [1, 1] if track_heater else [0, 1]
        
        # Beacon as 128-bit list (default to all zeros)
        if beacon is None or not isinstance(beacon, list) or len(beacon) != 128:
            self.beacon = [0] * 128  # Default: 128 zeros
        else:
            self.beacon = beacon
        
        self.switch_state = switch_state
        self.crossing = crossing
        self.signal = signal
        self.occupancy = occupancy