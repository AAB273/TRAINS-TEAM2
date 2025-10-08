#!/usr/bin/env python3
"""
Train Control System for Raspberry Pi
Hardware Setup:
- Left Door Button: GPIO 17 (with pull-up resistor)
- Left Door LED: GPIO 27
- Right Door Button: GPIO 22 (with pull-up resistor)  
- Right Door LED: GPIO 23
- Passenger Emergency Signal LED: GPIO 24 (output only - controlled by external signal)
- Brake Failure LED: GPIO 25 (output only - controlled by external signal)
- Engine Failure LED: GPIO 5 (output only - controlled by external signal)
- Signal Failure LED: GPIO 6 (output only - controlled by external signal)
"""

import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
LEFT_DOOR_BUTTON = 17
LEFT_DOOR_LED = 27
RIGHT_DOOR_BUTTON = 22
RIGHT_DOOR_LED = 23
PASSENGER_EMERGENCY_LED = 24
BRAKE_FAILURE_LED = 25
ENGINE_FAILURE_LED = 5
SIGNAL_FAILURE_LED = 6

# States
left_door_open = False
right_door_open = False
passenger_emergency_signal = False
brake_failure = False
engine_failure = False
signal_failure = False

def setup():
    """Initialize GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup buttons with internal pull-up resistors
    GPIO.setup(LEFT_DOOR_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_DOOR_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Setup LEDs as outputs
    GPIO.setup(LEFT_DOOR_LED, GPIO.OUT)
    GPIO.setup(RIGHT_DOOR_LED, GPIO.OUT)
    GPIO.setup(PASSENGER_EMERGENCY_LED, GPIO.OUT)
    
    # Initialize LEDs to OFF
    GPIO.output(LEFT_DOOR_LED, GPIO.LOW)
    GPIO.output(RIGHT_DOOR_LED, GPIO.LOW)
    GPIO.output(PASSENGER_EMERGENCY_LED, GPIO.LOW)
    
    print("Train Control System Initialized")
    print("=" * 50)

def toggle_left_door(channel):
    """Toggle left door state"""
    global left_door_open
    left_door_open = not left_door_open
    GPIO.output(LEFT_DOOR_LED, GPIO.HIGH if left_door_open else GPIO.LOW)
    status = "OPEN" if left_door_open else "CLOSED"
    print(f"Left Door: {status}")

def toggle_right_door(channel):
    """Toggle right door state"""
    global right_door_open
    right_door_open = not right_door_open
    GPIO.output(RIGHT_DOOR_LED, GPIO.HIGH if right_door_open else GPIO.LOW)
    status = "OPEN" if right_door_open else "CLOSED"
    print(f"Right Door: {status}")

def set_passenger_emergency(state):
    """
    Set passenger emergency signal state.
    This would typically be called by an external system when a passenger
    triggers an emergency alert.
    
    Args:
        state (bool): True to activate emergency signal, False to clear
    """
    global passenger_emergency_signal
    passenger_emergency_signal = state
    GPIO.output(PASSENGER_EMERGENCY_LED, GPIO.HIGH if state else GPIO.LOW)
    status = "ACTIVE ⚠️" if state else "CLEARED"
    print(f"Passenger Emergency Signal: {status}")

def main():
    """Main program loop"""
    setup()
    
    # Add event detection for button presses (falling edge, since we use pull-up)
    # Debounce time of 300ms to prevent multiple triggers
    GPIO.add_event_detect(LEFT_DOOR_BUTTON, GPIO.FALLING, 
                         callback=toggle_left_door, bouncetime=300)
    GPIO.add_event_detect(RIGHT_DOOR_BUTTON, GPIO.FALLING, 
                         callback=toggle_right_door, bouncetime=300)
    
    print("Door controls active. Press buttons to toggle doors.")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        # Keep program running
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        cleanup()

def cleanup():
    """Clean up GPIO on exit"""
    GPIO.output(LEFT_DOOR_LED, GPIO.LOW)
    GPIO.output(RIGHT_DOOR_LED, GPIO.LOW)
    GPIO.output(PASSENGER_EMERGENCY_LED, GPIO.LOW)
    GPIO.cleanup()
    print("GPIO cleaned up. Goodbye!")

if __name__ == "__main__":
    main()
