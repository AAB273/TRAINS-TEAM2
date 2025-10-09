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
        self.track_heater = track_heater
        self.beacon = beacon

        # Additional diagram attributes for Test_UI
        self.switch_state = switch_state
        self.crossing = crossing
        self.signal = signal
        self.occupancy = occupancy

