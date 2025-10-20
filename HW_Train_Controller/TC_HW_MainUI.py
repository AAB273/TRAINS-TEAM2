#!/usr/bin/env python3
"""
Train Control System for Raspberry Pi 5

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
- Passenger Emergency Signal LED: GPIO 24 (output only - controlled by Train Model)
- Brake Failure LED: GPIO 25 (output only - controlled by Train Model)
- Engine Failure LED: GPIO 5 (output only - controlled by Train Model)
- Signal Failure LED: GPIO 6 (output only - controlled by Train Model)
"""

import lgpio
import time
import tkinter as tk
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TC_HW_AirConditioning_UI import ACSystemPanel
from TC_HW_Announcement_UI import StationAnnouncementPanel
from TC_HW_TrackInfo_UI import TrackInformationPanel


class TrainController:
	# Main Train Controller class that manages all GPIO operations and train state.
	
	"""
	Attributes:
		h: GPIO chip handle for Raspberry Pi 5
		leftDoorOpen: Boolean status of left door
		rightDoorOpen: Boolean status of right door
		headlightsOn: Boolean status of headlights
		interiorLightsOn: Boolean status of interior lights
		serviceBrakeActive: Boolean status of service brake
		trainHornActive: Boolean status of train horn
		emergencyBrakeEngaged: Boolean status of emergency brake
		drivetrainManualMode: Boolean for drivetrain mode (False = Automatic, True = Manual)
		speedUpPressed: Boolean status of speed up button
		speedDownPressed: Boolean status of speed down button
		speedConfirmPressed: Boolean status of speed confirm button
		commandedSpeed: Float commanded speed in MPH from Train Model
		commandedAuthority: Integer commanded authority in blocks from Train Model
		currentSpeed: Float current actual train speed in MPH
		manualSetpointSpeed: Float speed setpoint in manual mode in MPH
		passengerEmergencySignal: Boolean passenger emergency signal status
		brakeFailure: Boolean brake failure indicator status
		engineFailure: Boolean engine failure indicator status
		signalFailure: Boolean signal failure indicator status
		running: Boolean flag to control the button monitoring loop
		buttonThread: Thread object for monitoring button states
	"""
	
	def __init__(self):
		# Initializes the Train Controller with default values.
		self.h = None
		# GPIO chip handle.
		
		self.leftDoorOpen = False
		# Status of left door (True = open, False = closed).
		self.rightDoorOpen = False
		# Status of right door (True = open, False = closed).
		self.headlightsOn = False
		# Status of headlights (True = on, False = off).
		self.interiorLightsOn = False
		# Status of interior lights (True = on, False = off).
		self.serviceBrakeActive = False
		# Status of service brake (True = engaged, False = released).
		self.trainHornActive = False
		# Status of train horn (True = sounding, False = off).
		self.emergencyBrakeEngaged = False
		# Status of emergency brake (True = engaged, False = released).
		self.drivetrainManualMode = False
		# Drivetrain mode (False = Automatic, True = Manual).
		self.speedUpPressed = False
		# Status of speed up button (True = currently pressed, False = not pressed).
		self.speedDownPressed = False
		# Status of speed down button (True = currently pressed, False = not pressed).
		self.speedConfirmPressed = False
		# Status of speed confirm button (True = currently pressed, False = not pressed).
		self.commandedSpeed = 0
		# Commanded speed in MPH set by Train Model.
		self.commandedAuthority = 0
		# Commanded authority in blocks set by Train Model.
		self.currentSpeed = 0
		# Current actual train speed in MPH.
		self.manualSetpointSpeed = 0
		# Speed setpoint in manual mode in MPH.
		self.passengerEmergencySignal = False
		# Passenger emergency signal status.
		self.brakeFailure = False
		# Brake failure indicator status.
		self.engineFailure = False
		# Engine failure indicator status.
		self.signalFailure = False
		# Signal failure indicator status.
		self.running = False
		# Flag to control the button monitoring loop.
		self.buttonThread = None
		# Thread for monitoring button states.
		
	def setup(self):
		# Initializes GPIO pins for all buttons and LEDs.
		self.h = lgpio.gpiochip_open(4)
		# Pi 5 uses gpiochip4.
		print(f"GPIO chip handle: {self.h}")
		
		lgpio.gpio_claim_input(self.h, self.LEFT_DOOR_BUTTON, lgpio.SET_PULL_UP)
		# Configure left door button as input.
		lgpio.gpio_claim_input(self.h, self.RIGHT_DOOR_BUTTON, lgpio.SET_PULL_UP)
		# Configure right door button as input.
		lgpio.gpio_claim_input(self.h, self.HEADLIGHTS_BUTTON, lgpio.SET_PULL_UP)
		# Configure headlights button as input.
		lgpio.gpio_claim_input(self.h, self.INTERIOR_LIGHTS_BUTTON, lgpio.SET_PULL_UP)
		# Configure interior lights button as input.
		lgpio.gpio_claim_input(self.h, self.SERVICE_BRAKE_BUTTON, lgpio.SET_PULL_UP)
		# Configure service brake button as input.
		lgpio.gpio_claim_input(self.h, self.TRAIN_HORN_BUTTON, lgpio.SET_PULL_UP)
		# Configure train horn button as input.
		lgpio.gpio_claim_input(self.h, self.EMERGENCY_BRAKE_BUTTON, lgpio.SET_PULL_UP)
		# Configure emergency brake button as input.
		lgpio.gpio_claim_input(self.h, self.DRIVETRAIN_MODE_BUTTON, lgpio.SET_PULL_UP)
		# Configure drivetrain mode button as input.
		lgpio.gpio_claim_input(self.h, self.SPEED_UP_BUTTON, lgpio.SET_PULL_UP)
		# Configure speed up button as input.
		lgpio.gpio_claim_input(self.h, self.SPEED_DOWN_BUTTON, lgpio.SET_PULL_UP)
		# Configure speed down button as input.
		lgpio.gpio_claim_input(self.h, self.SPEED_CONFIRM_BUTTON, lgpio.SET_PULL_UP)
		# Configure speed confirm button as input.
		
		lgpio.gpio_claim_output(self.h, self.LEFT_DOOR_LED)
		# Configure left door LED as output.
		lgpio.gpio_claim_output(self.h, self.RIGHT_DOOR_LED)
		# Configure right door LED as output.
		lgpio.gpio_claim_output(self.h, self.HEADLIGHTS_LED)
		# Configure headlights LED as output.
		lgpio.gpio_claim_output(self.h, self.INTERIOR_LIGHTS_LED)
		# Configure interior lights LED as output.
		lgpio.gpio_claim_output(self.h, self.EMERGENCY_BRAKE_LED)
		# Configure emergency brake LED as output.
		lgpio.gpio_claim_output(self.h, self.DRIVETRAIN_MODE_LED)
		# Configure drivetrain mode LED as output.
		lgpio.gpio_claim_output(self.h, self.PASSENGER_EMERGENCY_LED)
		# Configure passenger emergency LED as output.
		lgpio.gpio_claim_output(self.h, self.BRAKE_FAILURE_LED)
		# Configure brake failure LED as output.
		lgpio.gpio_claim_output(self.h, self.ENGINE_FAILURE_LED)
		# Configure engine failure LED as output.
		lgpio.gpio_claim_output(self.h, self.SIGNAL_FAILURE_LED)
		# Configure signal failure LED as output.
		
		lgpio.gpio_write(self.h, self.LEFT_DOOR_LED, 0)
		# Initialize left door LED to off.
		lgpio.gpio_write(self.h, self.RIGHT_DOOR_LED, 0)
		# Initialize right door LED to off.
		lgpio.gpio_write(self.h, self.HEADLIGHTS_LED, 0)
		# Initialize headlights LED to off.
		lgpio.gpio_write(self.h, self.INTERIOR_LIGHTS_LED, 0)
		# Initialize interior lights LED to off.
		lgpio.gpio_write(self.h, self.EMERGENCY_BRAKE_LED, 0)
		# Initialize emergency brake LED to off.
		lgpio.gpio_write(self.h, self.DRIVETRAIN_MODE_LED, 0)
		# Initialize drivetrain mode LED to off.
		lgpio.gpio_write(self.h, self.PASSENGER_EMERGENCY_LED, 0)
		# Initialize passenger emergency LED to off.
		lgpio.gpio_write(self.h, self.BRAKE_FAILURE_LED, 0)
		# Initialize brake failure LED to off.
		lgpio.gpio_write(self.h, self.ENGINE_FAILURE_LED, 0)
		# Initialize engine failure LED to off.
		lgpio.gpio_write(self.h, self.SIGNAL_FAILURE_LED, 0)
		# Initialize signal failure LED to off.
		
		print(f"Passenger Emergency LED configured on GPIO {self.PASSENGER_EMERGENCY_LED}")
		print("Train Control System Initialized")
		print("=" * 50)
		
	def startButtonMonitoring(self):
		# Starts the button monitoring thread.
		self.running = True
		# Set running flag to true.
		self.buttonThread = threading.Thread(target=self._checkButtons, daemon=True)
		# Create daemon thread for button monitoring.
		self.buttonThread.start()
		# Start the button monitoring thread.
		
	def _checkButtons(self):
		# Monitors all button states and handles toggling and speed control.
		prevLeft = 1
		# Previous state of left door button.
		prevRight = 1
		# Previous state of right door button.
		prevHeadlights = 1
		# Previous state of headlights button.
		prevInterior = 1
		# Previous state of interior lights button.
		prevServiceBrake = 1
		# Previous state of service brake button.
		prevTrainHorn = 1
		# Previous state of train horn button.
		prevEmergencyBrake = 1
		# Previous state of emergency brake button.
		prevDrivetrain = 1
		# Previous state of drivetrain mode button.
		prevSpeedUp = 1
		# Previous state of speed up button.
		prevSpeedDown = 1
		# Previous state of speed down button.
		prevSpeedConfirm = 1
		# Previous state of speed confirm button.
		
		while self.running:
			leftState = lgpio.gpio_read(self.h, self.LEFT_DOOR_BUTTON)
			# Read current left door button state.
			rightState = lgpio.gpio_read(self.h, self.RIGHT_DOOR_BUTTON)
			# Read current right door button state.
			headlightsState = lgpio.gpio_read(self.h, self.HEADLIGHTS_BUTTON)
			# Read current headlights button state.
			interiorState = lgpio.gpio_read(self.h, self.INTERIOR_LIGHTS_BUTTON)
			# Read current interior lights button state.
			serviceBrakeState = lgpio.gpio_read(self.h, self.SERVICE_BRAKE_BUTTON)
			# Read current service brake button state.
			trainHornState = lgpio.gpio_read(self.h, self.TRAIN_HORN_BUTTON)
			# Read current train horn button state.
			emergencyBrakeState = lgpio.gpio_read(self.h, self.EMERGENCY_BRAKE_BUTTON)
			# Read current emergency brake button state.
			drivetrainState = lgpio.gpio_read(self.h, self.DRIVETRAIN_MODE_BUTTON)
			# Read current drivetrain mode button state.
			speedUpState = lgpio.gpio_read(self.h, self.SPEED_UP_BUTTON)
			# Read current speed up button state.
			speedDownState = lgpio.gpio_read(self.h, self.SPEED_DOWN_BUTTON)
			# Read current speed down button state.
			speedConfirmState = lgpio.gpio_read(self.h, self.SPEED_CONFIRM_BUTTON)
			# Read current speed confirm button state.
			
			self.speedUpPressed = (speedUpState == 0)
			# Update speed up button pressed state.
			self.speedDownPressed = (speedDownState == 0)
			# Update speed down button pressed state.
			self.speedConfirmPressed = (speedConfirmState == 0)
			# Update speed confirm button pressed state.
			
			if prevLeft == 1 and leftState == 0:
				self.leftDoorOpen = not self.leftDoorOpen
				# Toggle left door state.
				lgpio.gpio_write(self.h, self.LEFT_DOOR_LED, 1 if self.leftDoorOpen else 0)
				# Update left door LED.
				status = "OPEN" if self.leftDoorOpen else "CLOSED"
				# Determine status string.
				print(f"Left Door: {status}")
				time.sleep(0.3)
				# Debounce delay.
			
			if prevRight == 1 and rightState == 0:
				self.rightDoorOpen = not self.rightDoorOpen
				# Toggle right door state.
				lgpio.gpio_write(self.h, self.RIGHT_DOOR_LED, 1 if self.rightDoorOpen else 0)
				# Update right door LED.
				status = "OPEN" if self.rightDoorOpen else "CLOSED"
				# Determine status string.
				print(f"Right Door: {status}")
				time.sleep(0.3)
				# Debounce delay.
			
			if prevHeadlights == 1 and headlightsState == 0:
				self.headlightsOn = not self.headlightsOn
				# Toggle headlights state.
				lgpio.gpio_write(self.h, self.HEADLIGHTS_LED, 1 if self.headlightsOn else 0)
				# Update headlights LED.
				status = "ON" if self.headlightsOn else "OFF"
				# Determine status string.
				print(f"Headlights: {status}")
				time.sleep(0.3)
				# Debounce delay.
			
			if prevInterior == 1 and interiorState == 0:
				self.interiorLightsOn = not self.interiorLightsOn
				# Toggle interior lights state.
				lgpio.gpio_write(self.h, self.INTERIOR_LIGHTS_LED, 1 if self.interiorLightsOn else 0)
				# Update interior lights LED.
				status = "ON" if self.interiorLightsOn else "OFF"
				# Determine status string.
				print(f"Interior Lights: {status}")
				time.sleep(0.3)
				# Debounce delay.
			
			if serviceBrakeState == 0 and not self.serviceBrakeActive:
				self.serviceBrakeActive = True
				# Engage service brake.
				print("Service Brake: ENGAGED")
			elif serviceBrakeState == 1 and self.serviceBrakeActive:
				self.serviceBrakeActive = False
				# Release service brake.
				print("Service Brake: RELEASED")
			
			if trainHornState == 0 and not self.trainHornActive:
				self.trainHornActive = True
				# Activate train horn.
				print("Train Horn: SOUNDING")
			elif trainHornState == 1 and self.trainHornActive:
				self.trainHornActive = False
				# Deactivate train horn.
				print("Train Horn: OFF")
			
			if prevEmergencyBrake == 1 and emergencyBrakeState == 0:
				self.emergencyBrakeEngaged = not self.emergencyBrakeEngaged
				# Toggle emergency brake state.
				lgpio.gpio_write(self.h, self.EMERGENCY_BRAKE_LED, 1 if self.emergencyBrakeEngaged else 0)
				# Update emergency brake LED.
				status = "🚨 ENGAGED 🚨" if self.emergencyBrakeEngaged else "RELEASED"
				# Determine status string.
				print(f"EMERGENCY BRAKE: {status}")
				time.sleep(0.3)
				# Debounce delay.
			
			if prevDrivetrain == 1 and drivetrainState == 0:
				self.drivetrainManualMode = not self.drivetrainManualMode
				# Toggle drivetrain mode.
				lgpio.gpio_write(self.h, self.DRIVETRAIN_MODE_LED, 1 if self.drivetrainManualMode else 0)
				# Update drivetrain mode LED.
				mode = "MANUAL" if self.drivetrainManualMode else "AUTOMATIC"
				# Determine mode string.
				print(f"Drivetrain Mode: {mode}")
				if self.drivetrainManualMode:
					self.manualSetpointSpeed = self.commandedSpeed
					# Initialize manual setpoint to commanded speed.
					print(f"Manual setpoint initialized to: {self.manualSetpointSpeed} MPH")
				time.sleep(0.3)
				# Debounce delay.
			
			if self.drivetrainManualMode:
				if prevSpeedUp == 1 and speedUpState == 0:
					self.manualSetpointSpeed = min(self.manualSetpointSpeed + 5, 70)
					# Increase manual setpoint by 5 MPH up to max 70 MPH.
					print(f"Manual Speed Setpoint: {self.manualSetpointSpeed} MPH")
					time.sleep(0.15)
					# Debounce delay.
				
				if prevSpeedDown == 1 and speedDownState == 0:
					self.manualSetpointSpeed = max(self.manualSetpointSpeed - 5, 0)
					# Decrease manual setpoint by 5 MPH down to min 0 MPH.
					print(f"Manual Speed Setpoint: {self.manualSetpointSpeed} MPH")
					time.sleep(0.15)
					# Debounce delay.
				
				if prevSpeedConfirm == 1 and speedConfirmState == 0:
					print(f"✓ SPEED CONFIRMED: {self.manualSetpointSpeed} MPH")
					time.sleep(0.3)
					# Debounce delay.
			
			prevLeft = leftState
			# Store current left door state.
			prevRight = rightState
			# Store current right door state.
			prevHeadlights = headlightsState
			# Store current headlights state.
			prevInterior = interiorState
			# Store current interior lights state.
			prevServiceBrake = serviceBrakeState
			# Store current service brake state.
			prevTrainHorn = trainHornState
			# Store current train horn state.
			prevEmergencyBrake = emergencyBrakeState
			# Store current emergency brake state.
			prevDrivetrain = drivetrainState
			# Store current drivetrain mode state.
			prevSpeedUp = speedUpState
			# Store current speed up state.
			prevSpeedDown = speedDownState
			# Store current speed down state.
			prevSpeedConfirm = speedConfirmState
			# Store current speed confirm state.
			
			time.sleep(0.01)
			# Small delay between reads.
	
	def getServiceBrakeState(self) -> bool:
		# Returns the current state of the service brake.
		return self.serviceBrakeActive
	
	def getTrainHornState(self) -> bool:
		# Returns the current state of the train horn.
		return self.trainHornActive
	
	def getEmergencyBrakeState(self) -> bool:
		# Returns the current state of the emergency brake.
		return self.emergencyBrakeEngaged
	
	def getDrivetrainMode(self) -> str:
		# Returns the current drivetrain mode as a string.
		return "MANUAL" if self.drivetrainManualMode else "AUTOMATIC"
	
	def isManualMode(self) -> bool:
		# Returns whether the drivetrain is in manual mode.
		return self.drivetrainManualMode
	
	def getCommandedSpeed(self) -> float:
		# Returns the commanded speed from Train Model.
		return self.commandedSpeed
	
	def getCommandedAuthority(self) -> int:
		# Returns the commanded authority from Train Model.
		return self.commandedAuthority
	
	def getCurrentSpeed(self) -> float:
		# Returns the current actual speed of the train.
		return self.currentSpeed
	
	def getManualSetpointSpeed(self) -> float:
		# Returns the manual mode speed setpoint.
		return self.manualSetpointSpeed
	
	def getTargetSpeed(self) -> float:
		# Returns the target speed based on current mode.
		if self.drivetrainManualMode:
			return self.manualSetpointSpeed
		else:
			return self.commandedSpeed
	
	def getLeftDoorState(self) -> bool:
		# Returns the state of the left door.
		return self.leftDoorOpen
	
	def getRightDoorState(self) -> bool:
		# Returns the state of the right door.
		return self.rightDoorOpen
	
	def getHeadlightsState(self) -> bool:
		# Returns the state of the headlights.
		return self.headlightsOn
	
	def getInteriorLightsState(self) -> bool:
		# Returns the state of the interior lights.
		return self.interiorLightsOn
	
	def getSpeedUpPressed(self) -> bool:
		# Returns whether the speed up button is currently pressed.
		return self.speedUpPressed
	
	def getSpeedDownPressed(self) -> bool:
		# Returns whether the speed down button is currently pressed.
		return self.speedDownPressed
	
	def getSpeedConfirmPressed(self) -> bool:
		# Returns whether the speed confirm button is currently pressed.
		return self.speedConfirmPressed
	
	def setCommandedSpeed(self, speed: float):
		# Sets the commanded speed from Train Model.
		self.commandedSpeed = max(0, min(speed, 70))
		# Clamp speed between 0 and 70 MPH.
		print(f"Commanded Speed set to: {self.commandedSpeed} MPH")
	
	def setCommandedAuthority(self, authority: int):
		# Sets the commanded authority from Train Model.
		self.commandedAuthority = max(0, authority)
		# Ensure authority is non-negative.
		print(f"Commanded Authority set to: {self.commandedAuthority} blocks")
	
	def setCurrentSpeed(self, speed: float):
		# Sets the current actual speed of the train.
		self.currentSpeed = max(0, min(speed, 70))
		# Clamp speed between 0 and 70 MPH.
	
	def setPassengerEmergency(self, state: bool):
		# Sets passenger emergency signal state from Train Model.
		self.passengerEmergencySignal = state
		# Store the state.
		value = 1 if state else 0
		# Convert boolean to GPIO value.
		result = lgpio.gpio_write(self.h, self.PASSENGER_EMERGENCY_LED, value)
		# Write to passenger emergency LED.
		status = "ACTIVE ⚠️" if state else "CLEARED"
		# Determine status string.
		print(f"Passenger Emergency Signal: {status} (GPIO {self.PASSENGER_EMERGENCY_LED} set to {value}, result: {result})")
	
	def setBrakeFailure(self, state: bool):
		# Sets brake failure indicator state from Train Model.
		self.brakeFailure = state
		# Store the state.
		lgpio.gpio_write(self.h, self.BRAKE_FAILURE_LED, 1 if state else 0)
		# Write to brake failure LED.
		status = "FAILURE ⚠️" if state else "OK"
		# Determine status string.
		print(f"Brake System: {status}")
	
	def setEngineFailure(self, state: bool):
		# Sets engine failure indicator state from Train Model.
		self.engineFailure = state
		# Store the state.
		lgpio.gpio_write(self.h, self.ENGINE_FAILURE_LED, 1 if state else 0)
		# Write to engine failure LED.
		status = "FAILURE ⚠️" if state else "OK"
		# Determine status string.
		print(f"Engine System: {status}")
	
	def setSignalFailure(self, state: bool):
		# Sets signal failure indicator state from Train Model.
		self.signalFailure = state
		# Store the state.
		lgpio.gpio_write(self.h, self.SIGNAL_FAILURE_LED, 1 if state else 0)
		# Write to signal failure LED.
		status = "FAILURE ⚠️" if state else "OK"
		# Determine status string.
		print(f"Signal System: {status}")
	
	def cleanup(self):
		# Cleans up GPIO resources on exit.
		self.running = False
		# Stop the button monitoring loop.
		time.sleep(0.1)
		# Give thread time to exit.
		
		lgpio.gpio_write(self.h, self.LEFT_DOOR_LED, 0)
		# Turn off left door LED.
		lgpio.gpio_write(self.h, self.RIGHT_DOOR_LED, 0)
		# Turn off right door LED.
		lgpio.gpio_write(self.h, self.HEADLIGHTS_LED, 0)
		# Turn off headlights LED.
		lgpio.gpio_write(self.h, self.INTERIOR_LIGHTS_LED, 0)
		# Turn off interior lights LED.
		lgpio.gpio_write(self.h, self.EMERGENCY_BRAKE_LED, 0)
		# Turn off emergency brake LED.
		lgpio.gpio_write(self.h, self.DRIVETRAIN_MODE_LED, 0)
		# Turn off drivetrain mode LED.
		lgpio.gpio_write(self.h, self.PASSENGER_EMERGENCY_LED, 0)
		# Turn off passenger emergency LED.
		lgpio.gpio_write(self.h, self.BRAKE_FAILURE_LED, 0)
		# Turn off brake failure LED.
		lgpio.gpio_write(self.h, self.ENGINE_FAILURE_LED, 0)
		# Turn off engine failure LED.
		lgpio.gpio_write(self.h, self.SIGNAL_FAILURE_LED, 0)
		# Turn off signal failure LED.
		
		lgpio.gpiochip_close(self.h)
		# Close GPIO chip handle.
		print("GPIO cleaned up. Goodbye!")
	
	LEFT_DOOR_BUTTON = 17
	# GPIO pin for left door button input.
	LEFT_DOOR_LED = 27
	# GPIO pin for left door LED output.
	RIGHT_DOOR_BUTTON = 22
	# GPIO pin for right door button input.
	RIGHT_DOOR_LED = 23
	# GPIO pin for right door LED output.
	HEADLIGHTS_BUTTON = 18
	# GPIO pin for headlights button input.
	HEADLIGHTS_LED = 19
	# GPIO pin for headlights LED output.
	INTERIOR_LIGHTS_BUTTON = 20
	# GPIO pin for interior lights button input.
	INTERIOR_LIGHTS_LED = 21
	# GPIO pin for interior lights LED output.
	SERVICE_BRAKE_BUTTON = 13
	# GPIO pin for service brake button input.
	TRAIN_HORN_BUTTON = 26
	# GPIO pin for train horn button input.
	EMERGENCY_BRAKE_BUTTON = 7
	# GPIO pin for emergency brake button input.
	EMERGENCY_BRAKE_LED = 8
	# GPIO pin for emergency brake LED output.
	DRIVETRAIN_MODE_BUTTON = 4
	# GPIO pin for drivetrain mode button input.
	DRIVETRAIN_MODE_LED = 10
	# GPIO pin for drivetrain mode LED output.
	SPEED_UP_BUTTON = 15
	# GPIO pin for speed up button input.
	SPEED_DOWN_BUTTON = 9
	# GPIO pin for speed down button input.
	SPEED_CONFIRM_BUTTON = 11
	# GPIO pin for speed confirm button input.
	PASSENGER_EMERGENCY_LED = 24
	# GPIO pin for passenger emergency LED output.
	BRAKE_FAILURE_LED = 25
	# GPIO pin for brake failure LED output.
	ENGINE_FAILURE_LED = 5
	# GPIO pin for engine failure LED output.
	SIGNAL_FAILURE_LED = 6
	# GPIO pin for signal failure LED output.


class TrainSpeedDisplayUI:
	# Speed display UI for train control system.
	
	"""
	Attributes:
		root: The main tkinter window
		controller: Reference to TrainController instance
		speedLabel: Label widget displaying current speed
		cmdSpeedValue: Label widget displaying commanded speed
		cmdAuthorityValue: Label widget displaying commanded authority
		manualSetpointValue: Label widget displaying manual setpoint speed
		modeValue: Label widget displaying drivetrain mode
		acPanel: Reference to AC System Panel window
		announcementPanel: Reference to Station Announcement Panel window
		trackInfoPanel: Reference to Track Information Panel window
	"""
	
	def __init__(self, root, controller):
		# Initializes the speed display UI with controller reference.
		self.root = root
		# Main tkinter window.
		self.controller = controller
		# Reference to TrainController instance.
		self.root.title("TRAIN SPEED CONTROL DISPLAY")
		self.root.geometry("900x700")
		self.root.configure(bg='#1e3c72')
		
		self._createWidgets()
		# Create all UI widgets.
		self._updateDisplay()
		# Start display update loop.
		
		self.root.protocol("WM_DELETE_WINDOW", self._onClose)
		# Set window close handler.
	
	def _createWidgets(self):
		# Creates all UI widgets for the speed display.
		headerFrame = tk.Frame(self.root, bg='#0f1e3d')
		# Frame for header section.
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="TRAIN SPEED CONTROL",
			font=('Arial', 28, 'bold'),
			bg='#0f1e3d',
			fg='white',
			pady=20
		)
		# Label for main header title.
		headerLabel.pack()
		
		mainFrame = tk.Frame(self.root, bg='#1e3c72')
		# Frame for main content area.
		mainFrame.pack(fill='both', expand=True, padx=30, pady=20)
		
		speedFrame = tk.Frame(mainFrame, bg='#2c5aa0', relief='raised', bd=5)
		# Frame for speedometer section.
		speedFrame.pack(fill='both', expand=True, pady=(0, 15))
		
		speedTitle = tk.Label(
			speedFrame,
			text="SPEEDOMETER",
			font=('Arial', 20, 'bold'),
			bg='#2c5aa0',
			fg='white',
			pady=10
		)
		# Label for speedometer title.
		speedTitle.pack()
		
		self.speedLabel = tk.Label(
			speedFrame,
			text="0",
			font=('Arial', 80, 'bold'),
			bg='#1a1a2e',
			fg='#00ff00',
			width=5,
			relief='sunken',
			bd=5
		)
		# Label displaying current speed value.
		self.speedLabel.pack(padx=30, pady=20)
		
		speedUnit = tk.Label(
			speedFrame,
			text="MPH",
			font=('Arial', 18, 'bold'),
			bg='#2c5aa0',
			fg='white',
			pady=5
		)
		# Label for speed unit indicator.
		speedUnit.pack()
		
		infoFrame = tk.Frame(mainFrame, bg='#1e3c72')
		# Frame for information boxes.
		infoFrame.pack(fill='both', expand=True)
		
		leftFrame = tk.Frame(infoFrame, bg='#1e3c72')
		# Frame for left column of info boxes.
		leftFrame.pack(side='left', fill='both', expand=True, padx=(0, 7))
		
		self._createInfoBox(
			leftFrame,
			"COMMANDED SPEED",
			"cmdSpeedValue",
			"#3498db",
			"70 MPH"
		)
		# Create commanded speed info box.
		
		self._createInfoBox(
			leftFrame,
			"COMMANDED AUTHORITY",
			"cmdAuthorityValue",
			"#9b59b6",
			"0 BLOCKS"
		)
		# Create commanded authority info box.
		
		rightFrame = tk.Frame(infoFrame, bg='#1e3c72')
		# Frame for right column of info boxes.
		rightFrame.pack(side='right', fill='both', expand=True, padx=(7, 0))
		
		self._createInfoBox(
			rightFrame,
			"MANUAL SETPOINT",
			"manualSetpointValue",
			"#e67e22",
			"-- MPH"
		)
		# Create manual setpoint info box.
		
		self._createInfoBox(
			rightFrame,
			"DRIVETRAIN MODE",
			"modeValue",
			"#27ae60",
			"AUTOMATIC"
		)
		# Create drivetrain mode info box.
		
		instructionsFrame = tk.Frame(mainFrame, bg='#34495e', relief='raised', bd=3)
		# Frame for instructions section.
		instructionsFrame.pack(fill='x', pady=(15, 0))
		
		instructions = tk.Label(
			instructionsFrame,
			text="Speed Up (GPIO 15) | Speed Down (GPIO 9) | Confirm (GPIO 11)\n" +
				 "Speed controls only active in MANUAL mode",
			font=('Arial', 11),
			bg='#34495e',
			fg='white',
			pady=12
		)
		# Label displaying user instructions.
		instructions.pack()
	
	def _createInfoBox(self, parent, title: str, valueAttr: str, color: str, defaultText: str):
		# Creates an info display box with title and value.
		frame = tk.Frame(parent, bg=color, relief='raised', bd=4)
		# Frame for info box container.
		frame.pack(fill='both', expand=True, pady=7)
		
		titleLabel = tk.Label(
			frame,
			text=title,
			font=('Arial', 14, 'bold'),
			bg=color,
			fg='white',
			pady=8
		)
		# Label for info box title.
		titleLabel.pack()
		
		valueLabel = tk.Label(
			frame,
			text=defaultText,
			font=('Arial', 24, 'bold'),
			bg='#1a1a2e',
			fg='white',
			pady=15,
			relief='sunken',
			bd=3
		)
		# Label for info box value display.
		valueLabel.pack(padx=15, pady=(0, 15))
		
		setattr(self, valueAttr, valueLabel)
		# Store reference to value label as instance attribute.
	
	def _updateDisplay(self):
		# Updates all display values from controller state.
		currentSpeedValue = self.controller.getCurrentSpeed()
		# Get current speed from controller.
		commandedSpeedValue = self.controller.getCommandedSpeed()
		# Get commanded speed from controller.
		commandedAuthorityValue = self.controller.getCommandedAuthority()
		# Get commanded authority from controller.
		manualSetpoint = self.controller.getManualSetpointSpeed()
		# Get manual setpoint from controller.
		mode = self.controller.getDrivetrainMode()
		# Get drivetrain mode from controller.
		isManual = self.controller.isManualMode()
		# Check if in manual mode.
		
		self.speedLabel.config(text=f"{int(currentSpeedValue)}")
		# Update speedometer display.
		
		if isManual:
			self.speedLabel.config(fg='#ffa500')
			# Orange color for manual mode.
		else:
			self.speedLabel.config(fg='#00ff00')
			# Green color for automatic mode.
		
		self.cmdSpeedValue.config(text=f"{int(commandedSpeedValue)} MPH")
		# Update commanded speed display.
		
		self.cmdAuthorityValue.config(text=f"{commandedAuthorityValue} BLOCKS")
		# Update commanded authority display.
		
		if isManual:
			self.manualSetpointValue.config(
				text=f"{int(manualSetpoint)} MPH",
				fg='#ffa500'
			)
			# Show manual setpoint in orange when active.
		else:
			self.manualSetpointValue.config(
				text="-- MPH",
				fg='#666666'
			)
			# Show inactive manual setpoint in gray.
		
		self.modeValue.config(text=mode)
		# Update mode text display.
		if isManual:
			self.modeValue.config(bg='#e74c3c', fg='yellow')
			# Red background with yellow text for manual mode.
		else:
			self.modeValue.config(bg='#1a1a2e', fg='white')
			# Dark background with white text for automatic mode.
		
		self.root.after(100, self._updateDisplay)
		# Schedule next update in 100ms.
	
	def _onClose(self):
		# Cleans up GPIO and closes all windows.
		print("\nCleaning up...")
		self.controller.cleanup()
		# Clean up GPIO resources.
		
		try:
			if hasattr(self, 'acPanel') and self.acPanel.root.winfo_exists():
				self.acPanel.root.destroy()
				# Close AC panel window if it exists.
		except:
			pass
		try:
			if hasattr(self, 'announcementPanel') and self.announcementPanel.root.winfo_exists():
				self.announcementPanel.root.destroy()
				# Close announcement panel window if it exists.
		except:
			pass
		try:
			if hasattr(self, 'trackInfoPanel') and self.trackInfoPanel.root.winfo_exists():
				self.trackInfoPanel.root.destroy()
				# Close track info panel window if it exists.
		except:
			pass
		
		self.root.destroy()
		# Destroy main window.


def main():
	# Main program entry point with all Tkinter UIs.
	controller = TrainController()
	# Create train controller instance.
	controller.setup()
	# Initialize GPIO hardware.
	controller.startButtonMonitoring()
	# Start button monitoring thread.
	
	root = tk.Tk()
	# Create main tkinter window.
	speedDisplay = TrainSpeedDisplayUI(root, controller)
	# Create speed display UI with controller reference.
	
	acRoot = tk.Toplevel(root)
	# Create AC system window.
	speedDisplay.acPanel = ACSystemPanel(acRoot)
	# Initialize AC system panel.
	
	announcementRoot = tk.Toplevel(root)
	# Create announcement window.
	speedDisplay.announcementPanel = StationAnnouncementPanel(announcementRoot)
	# Initialize station announcement panel.
	
	trackInfoRoot = tk.Toplevel(root)
	# Create track info window.
	speedDisplay.trackInfoPanel = TrackInformationPanel(trackInfoRoot)
	# Initialize track information panel.
	
	root.mainloop()
	# Start tkinter event loop.


if __name__ == "__main__":
	main()