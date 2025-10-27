"""
Train Data Management System
Handles all train data and state for both Test UI and Passenger UI
All calculations are done in metric, then converted to imperial when displayed onto the UI, except for temperature which is already in farenheight
"""
import numpy as np
import time

class TrainState:
    """Train finite state machine states"""
    AT_STATION = "at_station"
    LEAVING_STATION = "leaving_station"
    NORMAL_OPERATION = "normal_operation"
    ARRIVING_AT_STATION = "arriving_at_station"
    EMERGENCY_BRAKE = "emergency_brake"
    ENGINE_FAILURE = "engine_failure"

class TrainStateMachine:
    """Manages train state transitions and behaviors"""
    def __init__(self, train):
        self.train = train
        self.current_state = TrainState.AT_STATION
        self.previous_state = None
        self.state_entry_time = 0
        #self.station_dwell_time = 15  # seconds at station
        
    def transition_to(self, new_state):
        """Handle state transitions with validation"""
        if self.current_state == new_state:
            return
            
        print(f"Train {self.train.train_id}: {self.current_state} -> {new_state}")
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_entry_time = time.time()
        
    def update_state_based_on_conditions(self):
        """Auto-transition based on train conditions and timers"""
        
        # Emergency conditions (highest priority)
        if self.train.emergency_brake_active:
            if self.current_state != TrainState.EMERGENCY_BRAKE:
                self.transition_to(TrainState.EMERGENCY_BRAKE)
            return
            
        # State-specific transitions
        if self.current_state == TrainState.AT_STATION:
            # Stay at station for dwell time, then depart
            if self.train.right_door_open == False and self.train.left_door_open == False and self.train.service_brake_active == False and self.train.power_command > 0:
                self.transition_to(TrainState.LEAVING_STATION)
                
        elif self.current_state == TrainState.LEAVING_STATION:
            # Transition to normal operation when reaching cruising speed
            if self.train.speed > (self.train.speed_limit * 0.05):
                self.transition_to(TrainState.NORMAL_OPERATION)
                
        elif self.current_state == TrainState.NORMAL_OPERATION:
            # Check if approaching station (simplified - you'd use actual station distance)
            if (self.train.service_brake_active and 
                self.train.power_command == 0 and 
                self.train.speed < (self.speed_limit * 0.3)):  # Only when slowing down significantly
                self.transition_to(TrainState.ARRIVING_AT_STATION)
                
        elif self.current_state == TrainState.ARRIVING_AT_STATION:
            # Transition to at_station when nearly stopped
            if self.train.speed < 0.1:  # Almost stopped (less than 0.1 m/s)
                self.transition_to(TrainState.AT_STATION)
                
        elif self.current_state == TrainState.EMERGENCY_BRAKE:
            # Can only leave emergency brake if manually reset
            if not self.train.emergency_brake_active and self.train.speed == 0:
                # Return to previous state or default to AT_STATION
                self.transition_to(TrainState.AT_STATION)
                    
        elif self.current_state == TrainState.ENGINE_FAILURE:
            # Can only leave out_of_service if engine failure is fixed
            if not self.train.engine_failure:
                self.transition_to(TrainState.AT_STATION)

class Train:
    """Represents a single train with all its properties"""
    def __init__(self, train_id):
        self.train_id = train_id
        
        # State Machine
        self.state_machine = TrainStateMachine(self)
        
        # Metrics - All Values come from blue line for testing
        self.speed = 0.0
        self.acceleration = 0.0
        self.passenger_count = 0
        self.passengers_disembarking = 0
        self.crew_count = 2
        self.power_command = 0.0
        self.cabin_temp = 72.0
        self.grade = 0
        self.elevation = 0
        self.speed_limit = 50
        self.commanded_speed = 0
        self.commanded_authority = 0

        # For physics calculations
        self.last_power_command = 0.0
        self.last_service_brake = True
        self.last_emergency_brake = False
        
        # Dimensions
        self.height = 3.42
        self.length = 32.2
        self.width = 2.65
        
        # Door states (boolean: True=Open, False=Closed)
        self.right_door_open = False
        self.left_door_open = False
        
        # Light states (boolean: True=On, False=Off)
        self.headlights_on = False
        self.interior_lights_on = False
        
        # Murphy failure modes
        self.engine_failure = False
        self.signal_pickup_failure = False
        self.brake_failure = False
        
        # Emergency brake and Service Brake
        self.emergency_brake_active = False
        self.service_brake_active = True
        
        # Deployment status
        self.deployed = False
        
        # Line assignment
        self.line = "blue"  # blue for testing

        # Station
        self.station = ""
        self.time_to_station = 0
        self.emergency_announcement = "EMERGENCY"
        
        # Observers (callbacks for UI updates)
        self._observers = []
    
    def update_physics_continuously(self):
        """Update train physics based on current state and commands"""
        # Only recalculate if something has changed or we're in a moving state
        state_changed = (
            self.power_command != self.last_power_command or
            self.service_brake_active != self.last_service_brake or
            self.emergency_brake_active != self.last_emergency_brake or
            self.state_machine.current_state in [TrainState.LEAVING_STATION, 
                                               TrainState.NORMAL_OPERATION,
                                               TrainState.ARRIVING_AT_STATION]
        )
        
        if state_changed:
            self.calculate_force_speed_acceleration_()
            
            # Store current state for comparison
            self.last_power_command = self.power_command
            self.last_service_brake = self.service_brake_active
            self.last_emergency_brake = self.emergency_brake_active
    
    def update_state(self):
        """Update the train's state machine"""
        self.state_machine.update_state_based_on_conditions()
    
    def add_observer(self, callback):
        """Register a callback to be notified of changes"""
        self._observers.append(callback)
    
    def remove_observer(self, callback):
        """Unregister a callback"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self):
        """Notify all observers of changes"""
        for callback in self._observers:
            callback(self)
    
    # Metric setters with validation
    def set_speed_limit(self, value):
        self.speed_limit = float(value)
        self._notify_observers()
    
    def set_elevation(self, value):
        self.elevation = float(value)
        self._notify_observers()

    def set_grade(self, value):
        self.grade = float(value)
        self._notify_observers()
        
    def set_speed(self, value):
        try:
            self.speed = float(value)
            print(f"Actual Speed Sent to Train Model")
            self._notify_observers()
        except ValueError:
            pass
    
    def set_acceleration(self, value):
        try:
            self.acceleration = float(value)
            self._notify_observers()
        except ValueError:
            pass
    
    def set_passenger_count(self, value):
        try:
            self.passenger_count = max(0, int(value))
            print(f"Train Occupancy Sent to Track Model")
            self._notify_observers()
        except ValueError:
            pass
    
    def set_crew_count(self, value):
        try:
            self.crew_count = max(0, int(value))
            self._notify_observers()
        except ValueError:
            pass
    
    def set_power_command(self, value):
        try:
            self.last_power_command = self.power_command
            self.power_command = float(value)
            self._notify_observers()
        except ValueError:
            pass
    
    def set_cabin_temp(self, value):
        try:
            self.cabin_temp = float(value)
            self._notify_observers()
        except ValueError:
            pass
    
    def set_height(self, value):
        try:
            self.height = float(value)
            self._notify_observers()
        except ValueError:
            pass
    
    def set_length(self, value):
        try:
            self.length = float(value)
            self._notify_observers()
        except ValueError:
            pass
    
    def set_width(self, value):
        try:
            self.width = float(value)
            self._notify_observers()
        except ValueError:
            pass

    def set_station(self, station_name):
        self.station = str(station_name)
        self._notify_observers()
        
    def set_time_to_station(self, minutes):
        try:
            self.time_to_station = max(0, int(minutes))
            self._notify_observers()
        except ValueError:
            pass
    
    def set_service_brake(self, value):
        value = bool(value)
        if value:
            self.service_brake_active = 1
        else:
            self.service_brake_active = 0
        self._notify_observers()

    def set_disembarking(self, value):
        self.passengers_disembarking = int(value)
        self._notify_observers()

    def calculate_force_speed_acceleration_(self, dt=1.0):
        """
        Calculate train physics based on current state and commands
        """
        # Constants
        EMPTY_TRAIN_MASS = 40900  
        AVG_PASSENGER_MASS = 65.77 
        SERVICE_BRAKE_DECEL = -1.2  
        EMERGENCY_BRAKE_DECEL = -2.73 
        MAX_FORCE = 25715 
        total_mass = EMPTY_TRAIN_MASS + (AVG_PASSENGER_MASS * (self.passenger_count + 2))

        # State-based acceleration logic
        current_state = self.state_machine.current_state
        
        if current_state == TrainState.EMERGENCY_BRAKE:
            a = EMERGENCY_BRAKE_DECEL
            
        elif current_state == TrainState.AT_STATION:
            a = 0  # Stationary at station
            
        elif current_state == TrainState.LEAVING_STATION:
            # Gradual acceleration when leaving station
            if self.power_command > 0:
                a = MAX_FORCE / total_mass
            else:
                a = 0
                
        elif current_state == TrainState.ARRIVING_AT_STATION:
            # Controlled deceleration when arriving
            a = SERVICE_BRAKE_DECEL
            
        elif self.service_brake_active:
            if self.speed > 0:
                a = SERVICE_BRAKE_DECEL
            else:
                a = 0
                
        elif self.power_command > 0 and self.speed > 0:
            # Normal operation
            force = self.power_command / self.speed
            a = force / total_mass
        else:
            a = self.acceleration
        
        # INTEGRATE: Update speed using acceleration
        new_speed = self.speed + (a * dt)
        
        # Apply speed limits
        if new_speed > self.speed_limit:
            new_speed = self.speed_limit
            
        # Ensure speed doesn't go negative
        if new_speed < 0:
            new_speed = 0
            if current_state not in [TrainState.AT_STATION, TrainState.EMERGENCY_BRAKE]:
                a = 0  # No acceleration when stopped (except in specific states)
        
        # Update state
        self.speed = new_speed
        self.acceleration = a
        self._notify_observers()

    # Door controls
    def set_right_door(self, is_open):
        """Set right door state (True=Open, False=Closed)"""
        self.right_door_open = bool(is_open)
        self._notify_observers()
    
    def set_left_door(self, is_open):
        """Set left door state (True=Open, False=Closed)"""
        self.left_door_open = bool(is_open)
        self._notify_observers()
    
    # Light controls
    def set_headlights(self, is_on):
        """Set headlight state (True=On, False=Off)"""
        self.headlights_on = bool(is_on)
        self._notify_observers()
    
    def set_interior_lights(self, is_on):
        """Set interior light state (True=On, False=Off)"""
        self.interior_lights_on = bool(is_on)
        self._notify_observers()
    
    # Failure modes
    def set_engine_failure(self, active):
        self.engine_failure = bool(active)
        self._notify_observers()
    
    def set_signal_pickup_failure(self, active):
        self.signal_pickup_failure = bool(active)
        self._notify_observers()
    
    def set_brake_failure(self, active):
        self.brake_failure = bool(active)
        self._notify_observers()
    
    def set_emergency_brake(self, active):
        self.emergency_brake_active = bool(active)
        self._notify_observers()
    
    def set_deployed(self, deployed):
        self.deployed = bool(deployed)
        self._notify_observers()
    
    def get_state_dict(self):
        """Return all train data as a dictionary"""
        return {
            'train_id': self.train_id,
            'speed': self.speed,
            'acceleration': self.acceleration,
            'passenger_count': self.passenger_count,
            'crew_count': self.crew_count,
            'power_command': self.power_command,
            'cabin_temp': self.cabin_temp,
            'height': self.height,
            'length': self.length,
            'width': self.width,
            'right_door_open': self.right_door_open,
            'left_door_open': self.left_door_open,
            'headlights_on': self.headlights_on,
            'interior_lights_on': self.interior_lights_on,
            'engine_failure': self.engine_failure,
            'signal_pickup_failure': self.signal_pickup_failure,
            'brake_failure': self.brake_failure,
            'emergency_brake_active': self.emergency_brake_active,
            'deployed': self.deployed,
            'current_state': self.state_machine.current_state
        }

class TrainManager:
    """Manages all trains in the system"""
    
    def __init__(self, num_trains=14):
        self.trains = {i+1: Train(i+1) for i in range(num_trains)}
        self.selected_train_id = 1
    
    def get_train(self, train_id):
        """Get a specific train"""
        return self.trains.get(train_id)
    
    def get_selected_train(self):
        """Get the currently selected train"""
        return self.trains.get(self.selected_train_id)
    
    def select_train(self, train_id):
        """Select a train by ID"""
        if train_id in self.trains:
            self.selected_train_id = train_id
            return self.trains[train_id]
        return None
    
    def get_all_trains(self):
        """Get dictionary of all trains"""
        return self.trains

    
# Global singleton instance
_train_manager = None

def get_train_manager():
    """Get the global TrainManager instance"""
    global _train_manager
    if _train_manager is None:
        _train_manager = TrainManager()
    return _train_manager