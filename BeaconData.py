class BeaconData:
    def __init__(self,beacon_number, distance_to_next=None, next_station_name=None):
       
        self.block_number = beacon_number
        self.distance_to_next = distance_to_next
        self.next_station_name = next_station_name