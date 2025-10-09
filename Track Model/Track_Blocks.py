# Block Class

class Block:
    def __init__(self, block_number, grade=0.0, elevation=0.0, length=0.0,
                 speed_limit=0.0, track_heater=False, beacon=False,
                 switch_state=False, crossing=False, signal=None, occupancy=0):
        self.block_number = block_number
        self.grade = grade
        self.elevation = elevation
        self.length = length
        self.speed_limit = speed_limit
        
        # Change track_heater from boolean to 2-bit list [is_on, is_working]
        # [0, 0] = Off, Not working | [0, 1] = Off, Working | [1, 1] = On, Working
        if isinstance(track_heater, list) and len(track_heater) == 2:
            self.track_heater = track_heater
        else:
            # Convert old boolean to new 2-bit system
            # If heater was True: [1, 1] (On and Working), if False: [0, 1] (Off but Working)
            self.track_heater = [1, 1] if track_heater else [0, 1]
        
        self.beacon = beacon
        self.switch_state = switch_state
        self.crossing = crossing
        self.signal = signal
        self.occupancy = occupancy

