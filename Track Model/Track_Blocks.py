# Block Class

class Block:
    grade: float
    elevation: float
    length: float
    speed_limit: float
    track_heater: bool # Gives the state of a track heater (0 for HEATER OFF, 1 for HEATER ON)
    beacon: bool # Gives the state of a beacon (0 for BEACON INACTIVE, 1 for BEACON ACTIVE)

    def __init__(self, grade=0.0, elevation=0.0, length=0.0, speed_limit=0.0,
                 track_heater=False, beacon=False):
        self.grade = grade
        self.elevation = elevation
        self.length = length
        self.speed_limit = speed_limit
        self.track_heater = track_heater
        self.beacon = beacon
