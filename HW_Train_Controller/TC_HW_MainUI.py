#!/usr/bin/env python3
"""
Train Control System for Raspberry Pi 5
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

import lgpio
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

# GPIO chip handle
h = None

def setup():
    """Initialize GPIO pins"""
    global h
    
    # Open GPIO chip
    h = lgpio.gpiochip_open(4)  # Pi 5 uses gpiochip4
    
    # Setup buttons as inputs with pull-up resistors
    lgpio.gpio_claim_input(h, LEFT_DOOR_BUTTON, lgpio.SET_PULL_UP)
    lgpio.gpio_claim_input(h, RIGHT_DOOR_BUTTON, lgpio.SET_PULL_UP)
    
    # Setup LEDs as outputs
    lgpio.gpio_claim_output(h, LEFT_DOOR_LED)
    lgpio.gpio_claim_output(h, RIGHT_DOOR_LED)
    lgpio.gpio_claim_output(h, PASSENGER_EMERGENCY_LED)
    lgpio.gpio_claim_output(h, BRAKE_FAILURE_LED)
    lgpio.gpio_claim_output(h, ENGINE_FAILURE_LED)
    lgpio.gpio_claim_output(h, SIGNAL_FAILURE_LED)
    
    # Initialize LEDs to OFF
    lgpio.gpio_write(h, LEFT_DOOR_LED, 0)
    lgpio.gpio_write(h, RIGHT_DOOR_LED, 0)
    lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, 0)
    lgpio.gpio_write(h, BRAKE_FAILURE_LED, 0)
    lgpio.gpio_write(h, ENGINE_FAILURE_LED, 0)
    lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 0)
    
    print("Train Control System Initialized")
    print("=" * 50)

def check_buttons():
    """Check button states and handle door toggling"""
    global left_door_open, right_door_open
    
    # Track previous button states for edge detection
    prev_left = 1
    prev_right = 1
    
    while True:
        # Read button states (0 = pressed, 1 = not pressed due to pull-up)
        left_state = lgpio.gpio_read(h, LEFT_DOOR_BUTTON)
        right_state = lgpio.gpio_read(h, RIGHT_DOOR_BUTTON)
        
        # Left button pressed (falling edge)
        if prev_left == 1 and left_state == 0:
            left_door_open = not left_door_open
            lgpio.gpio_write(h, LEFT_DOOR_LED, 1 if left_door_open else 0)
            status = "OPEN" if left_door_open else "CLOSED"
            print(f"Left Door: {status}")
            time.sleep(0.3)  # Debounce
        
        # Right button pressed (falling edge)
        if prev_right == 1 and right_state == 0:
            right_door_open = not right_door_open
            lgpio.gpio_write(h, RIGHT_DOOR_LED, 1 if right_door_open else 0)
            status = "OPEN" if right_door_open else "CLOSED"
            print(f"Right Door: {status}")
            time.sleep(0.3)  # Debounce
        
        prev_left = left_state
        prev_right = right_state
        
        time.sleep(0.01)  # Small delay to prevent CPU spinning

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
    lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, 1 if state else 0)
    status = "ACTIVE ⚠️" if state else "CLEARED"
    print(f"Passenger Emergency Signal: {status}")

def set_brake_failure(state):
    """
    Set brake failure indicator state.
    
    Args:
        state (bool): True to indicate brake failure, False to clear
    """
    global brake_failure
    brake_failure = state
    lgpio.gpio_write(h, BRAKE_FAILURE_LED, 1 if state else 0)
    status = "FAILURE ⚠️" if state else "OK"
    print(f"Brake System: {status}")

def set_engine_failure(state):
    """
    Set engine failure indicator state.
    
    Args:
        state (bool): True to indicate engine failure, False to clear
    """
    global engine_failure
    engine_failure = state
    lgpio.gpio_write(h, ENGINE_FAILURE_LED, 1 if state else 0)
    status = "FAILURE ⚠️" if state else "OK"
    print(f"Engine System: {status}")

def set_signal_failure(state):
    """
    Set signal failure indicator state.
    
    Args:
        state (bool): True to indicate signal failure, False to clear
    """
    global signal_failure
    signal_failure = state
    lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 1 if state else 0)
    status = "FAILURE ⚠️" if state else "OK"
    print(f"Signal System: {status}")

def main():
    """Main program loop"""
    setup()
    
    print("Door controls active. Press buttons to toggle doors.")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        # Keep checking buttons
        check_buttons()
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        cleanup()

def cleanup():
    """Clean up GPIO on exit"""
    lgpio.gpio_write(h, LEFT_DOOR_LED, 0)
    lgpio.gpio_write(h, RIGHT_DOOR_LED, 0)
    lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, 0)
    lgpio.gpio_write(h, BRAKE_FAILURE_LED, 0)
    lgpio.gpio_write(h, ENGINE_FAILURE_LED, 0)
    lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 0)
    lgpio.gpiochip_close(h)
    print("GPIO cleaned up. Goodbye!")

if __name__ == "__main__":
    main()