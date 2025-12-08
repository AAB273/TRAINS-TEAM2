class TrainState:
    # Your original states
    AT_STATION = "at_station"
    LEAVING_STATION = "leaving_station" 
    NORMAL_OPERATION = "normal_operation"
    ARRIVING_AT_STATION = "arriving_at_station"
    
    # Recommended additional states
    EMERGENCY_BRAKE = "emergency_brake"
    OUT_OF_SERVICE = "out_of_service"
    DOOR_OBSTRUCTION = "door_obstruction"
    WAITING_FOR_CLEARANCE = "waiting_for_clearance"