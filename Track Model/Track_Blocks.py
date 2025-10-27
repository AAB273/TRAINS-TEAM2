# Block Class

class Block:
    def __init__(self, block_number, grade=0.0, elevation=0.0, length=0.0,
                 speed_limit=0.0, track_heater=False, beacon=None,  # Change beacon default to None
                 switch_state=False, crossing=False, signal=None, occupancy=0):
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