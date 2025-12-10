#!/usr/bin/env python3
"""
Train Control GPIO Server for Raspberry Pi 5
Runs on the Pi and accepts commands from remote Windows client

Hardware Setup:
- Left Door Button: GPIO 17 (with pull-up resistor)
- Left Door LED: GPIO 27
- Right Door Button: GPIO 22 (with pull-up resistor)  
- Right Door LED: GPIO 23
- Headlights Button: GPIO 18 (with pull-up resistor)
- Headlights LED: GPIO 19
- Interior Lights Button: GPIO 20 (with pull-up resistor)
- Interior Lights LED: GPIO 21
- Service Brake Button: GPIO 13 (with pull-up resistor)
- Train Horn Button: GPIO 26 (with pull-up resistor)
- Emergency Brake Button: GPIO 7 (with pull-up resistor, 4-prong button)
- Emergency Brake LED: GPIO 8 (optional indicator)
- Drivetrain Mode Button: GPIO 4 (with pull-up resistor, 4-prong button)
- Drivetrain Mode LED: GPIO 10 (indicator - ON = Manual, OFF = Automatic)
- Speed Up Button: GPIO 15 (with pull-up resistor)
- Speed Down Button: GPIO 9 (with pull-up resistor)
- Speed Confirm Button: GPIO 11 (with pull-up resistor)
- Passenger Emergency Signal LED: GPIO 24 (output only)
- Brake Failure LED: GPIO 25 (output only)
- Engine Failure LED: GPIO 5 (output only)
- Signal Failure LED: GPIO 6 (output only)
"""

import socket
import json
import threading
import time
import lgpio

# GPIO Pin Configuration Constants
LEFT_DOOR_BUTTON = 17
LEFT_DOOR_LED = 27
RIGHT_DOOR_BUTTON = 22
RIGHT_DOOR_LED = 23
HEADLIGHTS_BUTTON = 18
HEADLIGHTS_LED = 19
INTERIOR_LIGHTS_BUTTON = 20
INTERIOR_LIGHTS_LED = 21
SERVICE_BRAKE_BUTTON = 13
TRAIN_HORN_BUTTON = 26
EMERGENCY_BRAKE_BUTTON = 7
EMERGENCY_BRAKE_LED = 8
DRIVETRAIN_MODE_BUTTON = 4
DRIVETRAIN_MODE_LED = 10
SPEED_UP_BUTTON = 15
SPEED_DOWN_BUTTON = 9
SPEED_CONFIRM_BUTTON = 11
PASSENGER_EMERGENCY_LED = 24
BRAKE_FAILURE_LED = 25
ENGINE_FAILURE_LED = 5
SIGNAL_FAILURE_LED = 6

class GPIOServer:
    def __init__(self, host='10.6.3.77', port=12348):
        self.host = host
        self.port = port
        self.running = True
        self.h = None
        
        # GPIO State variables
        self.leftDoorOpen = False
        self.rightDoorOpen = False
        self.headlightsOn = False
        self.interiorLightsOn = False
        self.serviceBrakeActive = True  # Train starts with brakes engaged for safety
        self.trainHornActive = False
        self.emergencyBrakeEngaged = False
        self.drivetrainManualMode = False
        self.speedUpPressed = False
        self.speedDownPressed = False
        self.speedConfirmPressed = False
        self.manualSetpointSpeed = 0
        
        # Previous button states for edge detection
        self.prevStates = {}
        
        # Connected clients
        self.clients = []
        self.clients_lock = threading.Lock()
        
        self.setupGPIO()
        
    def setupGPIO(self):
        """Initialize GPIO pins"""
        self.h = lgpio.gpiochip_open(4)
        self.log(f"GPIO chip handle: {self.h}", 'system')
        
        # Configure input pins with pull-up resistors
        lgpio.gpio_claim_input(self.h, LEFT_DOOR_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, RIGHT_DOOR_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, HEADLIGHTS_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, INTERIOR_LIGHTS_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, SERVICE_BRAKE_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, TRAIN_HORN_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, EMERGENCY_BRAKE_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, DRIVETRAIN_MODE_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, SPEED_UP_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, SPEED_DOWN_BUTTON, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.h, SPEED_CONFIRM_BUTTON, lgpio.SET_PULL_UP)
        
        # Configure output pins
        lgpio.gpio_claim_output(self.h, LEFT_DOOR_LED)
        lgpio.gpio_claim_output(self.h, RIGHT_DOOR_LED)
        lgpio.gpio_claim_output(self.h, HEADLIGHTS_LED)
        lgpio.gpio_claim_output(self.h, INTERIOR_LIGHTS_LED)
        lgpio.gpio_claim_output(self.h, EMERGENCY_BRAKE_LED)
        lgpio.gpio_claim_output(self.h, DRIVETRAIN_MODE_LED)
        lgpio.gpio_claim_output(self.h, PASSENGER_EMERGENCY_LED)
        lgpio.gpio_claim_output(self.h, BRAKE_FAILURE_LED)
        lgpio.gpio_claim_output(self.h, ENGINE_FAILURE_LED)
        lgpio.gpio_claim_output(self.h, SIGNAL_FAILURE_LED)
        
        # Initialize all LEDs to OFF
        lgpio.gpio_write(self.h, LEFT_DOOR_LED, 0)
        lgpio.gpio_write(self.h, RIGHT_DOOR_LED, 0)
        lgpio.gpio_write(self.h, HEADLIGHTS_LED, 0)
        lgpio.gpio_write(self.h, INTERIOR_LIGHTS_LED, 0)
        lgpio.gpio_write(self.h, EMERGENCY_BRAKE_LED, 0)
        lgpio.gpio_write(self.h, DRIVETRAIN_MODE_LED, 0)
        lgpio.gpio_write(self.h, PASSENGER_EMERGENCY_LED, 0)
        lgpio.gpio_write(self.h, BRAKE_FAILURE_LED, 0)
        lgpio.gpio_write(self.h, ENGINE_FAILURE_LED, 0)
        lgpio.gpio_write(self.h, SIGNAL_FAILURE_LED, 0)
        
        # Initialize previous states
        self.prevStates = {
            'left_door': 1, 'right_door': 1, 'headlights': 1, 'interior': 1,
            'service_brake': 1, 'train_horn': 1, 'emergency_brake': 1,
            'drivetrain': 1, 'speed_up': 1, 'speed_down': 1, 'speed_confirm': 1
        }
        
        self.log("GPIO Server Initialized", 'system')
        print("=" * 50)
    
    def log(self, message, category='system'):
        """Log message to terminal AND broadcast to all clients"""
        # Print to Pi terminal
        print(message)
        
        # Send to all connected clients
        log_msg = {
            'type': 'log_message',
            'message': message,
            'category': category
        }
        
        with self.clients_lock:
            disconnected = []
            for client in self.clients:
                try:
                    client.sendall((json.dumps(log_msg) + '\n').encode('utf-8'))
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                if client in self.clients:
                    self.clients.remove(client)
    
    def checkButtons(self):
        """Monitor all button inputs and update states"""
        while self.running:
            # Read all button states
            leftState = lgpio.gpio_read(self.h, LEFT_DOOR_BUTTON)
            rightState = lgpio.gpio_read(self.h, RIGHT_DOOR_BUTTON)
            headlightsState = lgpio.gpio_read(self.h, HEADLIGHTS_BUTTON)
            interiorState = lgpio.gpio_read(self.h, INTERIOR_LIGHTS_BUTTON)
            serviceBrakeState = lgpio.gpio_read(self.h, SERVICE_BRAKE_BUTTON)
            trainHornState = lgpio.gpio_read(self.h, TRAIN_HORN_BUTTON)
            emergencyBrakeState = lgpio.gpio_read(self.h, EMERGENCY_BRAKE_BUTTON)
            drivetrainState = lgpio.gpio_read(self.h, DRIVETRAIN_MODE_BUTTON)
            speedUpState = lgpio.gpio_read(self.h, SPEED_UP_BUTTON)
            speedDownState = lgpio.gpio_read(self.h, SPEED_DOWN_BUTTON)
            speedConfirmState = lgpio.gpio_read(self.h, SPEED_CONFIRM_BUTTON)
            
            # Update pressed states
            self.speedUpPressed = (speedUpState == 0)
            self.speedDownPressed = (speedDownState == 0)
            self.speedConfirmPressed = (speedConfirmState == 0)
            
            # Detect button press edges (falling edge, 1→0 transition)
            stateChanged = False
            
            # Left Door
            if self.prevStates['left_door'] == 1 and leftState == 0:
                self.leftDoorOpen = not self.leftDoorOpen
                lgpio.gpio_write(self.h, LEFT_DOOR_LED, 1 if self.leftDoorOpen else 0)
                self.log(f"Left Door: {'OPEN' if self.leftDoorOpen else 'CLOSED'}", 'doors')
                stateChanged = True
                time.sleep(0.3)
            
            # Right Door
            if self.prevStates['right_door'] == 1 and rightState == 0:
                self.rightDoorOpen = not self.rightDoorOpen
                lgpio.gpio_write(self.h, RIGHT_DOOR_LED, 1 if self.rightDoorOpen else 0)
                self.log(f"Right Door: {'OPEN' if self.rightDoorOpen else 'CLOSED'}", 'doors')
                stateChanged = True
                time.sleep(0.3)
            
            # Headlights
            if self.prevStates['headlights'] == 1 and headlightsState == 0:
                self.headlightsOn = not self.headlightsOn
                lgpio.gpio_write(self.h, HEADLIGHTS_LED, 1 if self.headlightsOn else 0)
                self.log(f"Headlights: {'ON' if self.headlightsOn else 'OFF'}", 'lights')
                stateChanged = True
                time.sleep(0.3)
            
            # Interior Lights
            if self.prevStates['interior'] == 1 and interiorState == 0:
                self.interiorLightsOn = not self.interiorLightsOn
                lgpio.gpio_write(self.h, INTERIOR_LIGHTS_LED, 1 if self.interiorLightsOn else 0)
                self.log(f"Interior Lights: {'ON' if self.interiorLightsOn else 'OFF'}", 'lights')
                stateChanged = True
                time.sleep(0.3)
            
            # Service Brake (continuous state)
            if serviceBrakeState == 0 and not self.serviceBrakeActive:
                self.serviceBrakeActive = True
                self.log("Service Brake: ENGAGED", 'brakes')
                stateChanged = True
            elif serviceBrakeState == 1 and self.serviceBrakeActive:
                self.serviceBrakeActive = False
                self.log("Service Brake: RELEASED", 'brakes')
                stateChanged = True
            
            # Train Horn (continuous state)
            if trainHornState == 0 and not self.trainHornActive:
                self.trainHornActive = True
                self.log("Train Horn: SOUNDING", 'brakes')
                stateChanged = True
            elif trainHornState == 1 and self.trainHornActive:
                self.trainHornActive = False
                self.log("Train Horn: OFF", 'brakes')
                stateChanged = True
            
            # Emergency Brake
            if self.prevStates['emergency_brake'] == 1 and emergencyBrakeState == 0:
                self.emergencyBrakeEngaged = not self.emergencyBrakeEngaged
                lgpio.gpio_write(self.h, EMERGENCY_BRAKE_LED, 1 if self.emergencyBrakeEngaged else 0)
                self.log(f"EMERGENCY BRAKE: {'🚨 ENGAGED 🚨' if self.emergencyBrakeEngaged else 'RELEASED'}", 'brakes')
                stateChanged = True
                time.sleep(0.3)
            
            # Drivetrain Mode
            if self.prevStates['drivetrain'] == 1 and drivetrainState == 0:
                self.drivetrainManualMode = not self.drivetrainManualMode
                lgpio.gpio_write(self.h, DRIVETRAIN_MODE_LED, 1 if self.drivetrainManualMode else 0)
                self.log(f"Drivetrain Mode: {'MANUAL' if self.drivetrainManualMode else 'AUTOMATIC'}", 'speed')
                stateChanged = True
                time.sleep(0.3)
            
            # Speed buttons (only in manual mode)
            if self.drivetrainManualMode:
                if self.prevStates['speed_up'] == 1 and speedUpState == 0:
                    self.manualSetpointSpeed = min(self.manualSetpointSpeed + 5, 70)
                    self.log(f"Manual Speed Setpoint: {self.manualSetpointSpeed} MPH", 'speed')
                    stateChanged = True
                    time.sleep(0.2)
                
                if self.prevStates['speed_down'] == 1 and speedDownState == 0:
                    self.manualSetpointSpeed = max(self.manualSetpointSpeed - 5, 0)
                    self.log(f"Manual Speed Setpoint: {self.manualSetpointSpeed} MPH", 'speed')
                    stateChanged = True
                    time.sleep(0.2)
            
            # Update previous states
            self.prevStates['left_door'] = leftState
            self.prevStates['right_door'] = rightState
            self.prevStates['headlights'] = headlightsState
            self.prevStates['interior'] = interiorState
            self.prevStates['service_brake'] = serviceBrakeState
            self.prevStates['train_horn'] = trainHornState
            self.prevStates['emergency_brake'] = emergencyBrakeState
            self.prevStates['drivetrain'] = drivetrainState
            self.prevStates['speed_up'] = speedUpState
            self.prevStates['speed_down'] = speedDownState
            self.prevStates['speed_confirm'] = speedConfirmState
            
            # Broadcast state update to all clients if something changed
            if stateChanged:
                self.broadcastState()
            
            time.sleep(0.05)
    
    def getState(self):
        """Return current GPIO state as dictionary"""
        return {
            'leftDoorOpen': self.leftDoorOpen,
            'rightDoorOpen': self.rightDoorOpen,
            'headlightsOn': self.headlightsOn,
            'interiorLightsOn': self.interiorLightsOn,
            'serviceBrakeActive': self.serviceBrakeActive,
            'trainHornActive': self.trainHornActive,
            'emergencyBrakeEngaged': self.emergencyBrakeEngaged,
            'drivetrainManualMode': self.drivetrainManualMode,
            'manualSetpointSpeed': self.manualSetpointSpeed,
            'speedUpPressed': self.speedUpPressed,
            'speedDownPressed': self.speedDownPressed,
            'speedConfirmPressed': self.speedConfirmPressed
        }
    
    def setLED(self, led_name, state):
        """Set LED state based on command from client"""
        led_map = {
            'passenger_emergency': PASSENGER_EMERGENCY_LED,
            'brake_failure': BRAKE_FAILURE_LED,
            'engine_failure': ENGINE_FAILURE_LED,
            'signal_failure': SIGNAL_FAILURE_LED,
            'left_door': LEFT_DOOR_LED,
            'right_door': RIGHT_DOOR_LED
        }
        
        if led_name in led_map:
            pin = led_map[led_name]
            lgpio.gpio_write(self.h, pin, 1 if state else 0)
            self.log(f"LED {led_name}: {'ON' if state else 'OFF'}", 'system')
            
            # Update internal door state when doors are controlled via setLED
            if led_name == 'left_door':
                self.leftDoorOpen = state
            elif led_name == 'right_door':
                self.rightDoorOpen = state
            
            return True
        return False
    
    def broadcastState(self):
        """Send current state to all connected clients"""
        state_msg = {
            'type': 'state_update',
            'data': self.getState()
        }
        
        with self.clients_lock:
            disconnected = []
            for client in self.clients:
                try:
                    client.sendall((json.dumps(state_msg) + '\n').encode('utf-8'))
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                if client in self.clients:
                    self.clients.remove(client)
    
    def handleClient(self, client_socket, address):
        """Handle individual client connection"""
        self.log(f"Client connected from {address}", 'system')
        
        with self.clients_lock:
            self.clients.append(client_socket)
        
        # Send initial state
        try:
            initial_state = {
                'type': 'state_update',
                'data': self.getState()
            }
            client_socket.sendall((json.dumps(initial_state) + '\n').encode('utf-8'))
        except:
            pass
        
        buffer = ""
        try:
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self.processCommand(line, client_socket)
        
        except Exception as e:
            self.log(f"Client error: {e}", 'error')
        
        finally:
            with self.clients_lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()
            self.log(f"Client disconnected from {address}", 'system')
    
    def processCommand(self, command_str, client_socket):
        """Process command from client"""
        try:
            command = json.loads(command_str)
            cmd_type = command.get('type')
            
            if cmd_type == 'set_led':
                led_name = command.get('led')
                state = command.get('state')
                success = self.setLED(led_name, state)
                
                response = {
                    'type': 'response',
                    'success': success
                }
                client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
            
            elif cmd_type == 'set_headlights':
                # Control headlights from main UI (for underground sections)
                state = command.get('state')
                self.headlightsOn = bool(state)
                lgpio.gpio_write(self.h, HEADLIGHTS_LED, 1 if state else 0)
                self.log(f"Headlights: {'ON' if state else 'OFF'} (Auto)", 'lights')
                self.broadcastState()
            
            elif cmd_type == 'set_interior_lights':
                # Control interior lights from main UI (for underground sections)
                state = command.get('state')
                self.interiorLightsOn = bool(state)
                lgpio.gpio_write(self.h, INTERIOR_LIGHTS_LED, 1 if state else 0)
                self.log(f"Interior Lights: {'ON' if state else 'OFF'} (Auto)", 'lights')
                self.broadcastState()
            
            elif cmd_type == 'get_state':
                state_msg = {
                    'type': 'state_update',
                    'data': self.getState()
                }
                client_socket.sendall((json.dumps(state_msg) + '\n').encode('utf-8'))
        
        except json.JSONDecodeError:
            self.log(f"Invalid JSON received: {command_str}", 'error')
        except Exception as e:
            self.log(f"Error processing command: {e}", 'error')
    
    def start(self):
        """Start the GPIO server"""
        # Start button monitoring thread
        button_thread = threading.Thread(target=self.checkButtons, daemon=True)
        button_thread.start()
        
        # Start server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        self.log(f"GPIO Server listening on {self.host}:{self.port}", 'system')
        self.log("Waiting for Windows client connection...", 'system')
        
        try:
            while self.running:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handleClient,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
        
        except KeyboardInterrupt:
            self.log("\nShutting down server...", 'system')
        
        finally:
            self.cleanup()
            server_socket.close()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.running = False
        time.sleep(0.2)
        
        if self.h is not None:
            lgpio.gpio_write(self.h, LEFT_DOOR_LED, 0)
            lgpio.gpio_write(self.h, RIGHT_DOOR_LED, 0)
            lgpio.gpio_write(self.h, HEADLIGHTS_LED, 0)
            lgpio.gpio_write(self.h, INTERIOR_LIGHTS_LED, 0)
            lgpio.gpio_write(self.h, EMERGENCY_BRAKE_LED, 0)
            lgpio.gpio_write(self.h, DRIVETRAIN_MODE_LED, 0)
            lgpio.gpio_write(self.h, PASSENGER_EMERGENCY_LED, 0)
            lgpio.gpio_write(self.h, BRAKE_FAILURE_LED, 0)
            lgpio.gpio_write(self.h, ENGINE_FAILURE_LED, 0)
            lgpio.gpio_write(self.h, SIGNAL_FAILURE_LED, 0)
            lgpio.gpiochip_close(self.h)
        
        self.log("GPIO cleaned up. Goodbye!", 'system')

if __name__ == "__main__":
    server = GPIOServer()
    server.start()