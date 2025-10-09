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

# Global state variables
leftDoorOpen = False
# Status of left door (True = open, False = closed).
rightDoorOpen = False
# Status of right door (True = open, False = closed).
headlightsOn = False
# Status of headlights (True = on, False = off).
interiorLightsOn = False
# Status of interior lights (True = on, False = off).
serviceBrakeActive = False
# Status of service brake (True = engaged, False = released).
trainHornActive = False
# Status of train horn (True = sounding, False = off).
emergencyBrakeEngaged = False
# Status of emergency brake (True = engaged, False = released).
drivetrainManualMode = False
# Drivetrain mode (False = Automatic, True = Manual).
speedUpPressed = False
# Status of speed up button (True = currently pressed, False = not pressed).
speedDownPressed = False
# Status of speed down button (True = currently pressed, False = not pressed).
speedConfirmPressed = False
# Status of speed confirm button (True = currently pressed, False = not pressed).
commandedSpeed = 0
# Commanded speed in MPH - set by Train Model.
commandedAuthority = 0
# Commanded authority in blocks - set by Train Model.
currentSpeed = 0
# Current actual train speed in MPH.
manualSetpointSpeed = 0
# Speed setpoint in manual mode in MPH.
passengerEmergencySignal = False
# Passenger emergency signal status.
brakeFailure = False
# Brake failure indicator status.
engineFailure = False
# Engine failure indicator status.
signalFailure = False
# Signal failure indicator status.

h = None
# GPIO chip handle.

running = True
# Flag to control the button monitoring loop.

acPanel = None
# AC System Panel instance.
announcementPanel = None
# Station Announcement Panel instance.
trackInfoPanel = None
# Track Information Panel instance.

def setup():
	# Initializes GPIO pins for all buttons and LEDs.
	global h
	
	h = lgpio.gpiochip_open(4)
	# Pi 5 uses gpiochip4.
	print(f"GPIO chip handle: {h}")
	
	lgpio.gpio_claim_input(h, LEFT_DOOR_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, RIGHT_DOOR_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, HEADLIGHTS_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, INTERIOR_LIGHTS_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, SERVICE_BRAKE_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, TRAIN_HORN_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, EMERGENCY_BRAKE_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, DRIVETRAIN_MODE_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, SPEED_UP_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, SPEED_DOWN_BUTTON, lgpio.SET_PULL_UP)
	lgpio.gpio_claim_input(h, SPEED_CONFIRM_BUTTON, lgpio.SET_PULL_UP)
	
	lgpio.gpio_claim_output(h, LEFT_DOOR_LED)
	lgpio.gpio_claim_output(h, RIGHT_DOOR_LED)
	lgpio.gpio_claim_output(h, HEADLIGHTS_LED)
	lgpio.gpio_claim_output(h, INTERIOR_LIGHTS_LED)
	lgpio.gpio_claim_output(h, EMERGENCY_BRAKE_LED)
	lgpio.gpio_claim_output(h, DRIVETRAIN_MODE_LED)
	lgpio.gpio_claim_output(h, PASSENGER_EMERGENCY_LED)
	lgpio.gpio_claim_output(h, BRAKE_FAILURE_LED)
	lgpio.gpio_claim_output(h, ENGINE_FAILURE_LED)
	lgpio.gpio_claim_output(h, SIGNAL_FAILURE_LED)
	
	lgpio.gpio_write(h, LEFT_DOOR_LED, 0)
	lgpio.gpio_write(h, RIGHT_DOOR_LED, 0)
	lgpio.gpio_write(h, HEADLIGHTS_LED, 0)
	lgpio.gpio_write(h, INTERIOR_LIGHTS_LED, 0)
	lgpio.gpio_write(h, EMERGENCY_BRAKE_LED, 0)
	lgpio.gpio_write(h, DRIVETRAIN_MODE_LED, 0)
	lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, 0)
	lgpio.gpio_write(h, BRAKE_FAILURE_LED, 0)
	lgpio.gpio_write(h, ENGINE_FAILURE_LED, 0)
	lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 0)
	
	print(f"Passenger Emergency LED configured on GPIO {PASSENGER_EMERGENCY_LED}")
	print("Train Control System Initialized")
	print("=" * 50)

def checkButtons():
	# Monitors all button states and handles toggling and speed control.
	global leftDoorOpen, rightDoorOpen, headlightsOn, interiorLightsOn
	global serviceBrakeActive, trainHornActive, emergencyBrakeEngaged
	global drivetrainManualMode, manualSetpointSpeed
	global speedUpPressed, speedDownPressed, speedConfirmPressed
	global running
	
	prevLeft = 1
	prevRight = 1
	prevHeadlights = 1
	prevInterior = 1
	prevServiceBrake = 1
	prevTrainHorn = 1
	prevEmergencyBrake = 1
	prevDrivetrain = 1
	prevSpeedUp = 1
	prevSpeedDown = 1
	prevSpeedConfirm = 1
	
	while running:
		leftState = lgpio.gpio_read(h, LEFT_DOOR_BUTTON)
		rightState = lgpio.gpio_read(h, RIGHT_DOOR_BUTTON)
		headlightsState = lgpio.gpio_read(h, HEADLIGHTS_BUTTON)
		interiorState = lgpio.gpio_read(h, INTERIOR_LIGHTS_BUTTON)
		serviceBrakeState = lgpio.gpio_read(h, SERVICE_BRAKE_BUTTON)
		trainHornState = lgpio.gpio_read(h, TRAIN_HORN_BUTTON)
		emergencyBrakeState = lgpio.gpio_read(h, EMERGENCY_BRAKE_BUTTON)
		drivetrainState = lgpio.gpio_read(h, DRIVETRAIN_MODE_BUTTON)
		speedUpState = lgpio.gpio_read(h, SPEED_UP_BUTTON)
		speedDownState = lgpio.gpio_read(h, SPEED_DOWN_BUTTON)
		speedConfirmState = lgpio.gpio_read(h, SPEED_CONFIRM_BUTTON)
		
		speedUpPressed = (speedUpState == 0)
		# Update speed up button pressed state.
		speedDownPressed = (speedDownState == 0)
		# Update speed down button pressed state.
		speedConfirmPressed = (speedConfirmState == 0)
		# Update speed confirm button pressed state.
		
		if prevLeft == 1 and leftState == 0:
			leftDoorOpen = not leftDoorOpen
			lgpio.gpio_write(h, LEFT_DOOR_LED, 1 if leftDoorOpen else 0)
			status = "OPEN" if leftDoorOpen else "CLOSED"
			print(f"Left Door: {status}")
			time.sleep(0.3)
		
		if prevRight == 1 and rightState == 0:
			rightDoorOpen = not rightDoorOpen
			lgpio.gpio_write(h, RIGHT_DOOR_LED, 1 if rightDoorOpen else 0)
			status = "OPEN" if rightDoorOpen else "CLOSED"
			print(f"Right Door: {status}")
			time.sleep(0.3)
		
		if prevHeadlights == 1 and headlightsState == 0:
			headlightsOn = not headlightsOn
			lgpio.gpio_write(h, HEADLIGHTS_LED, 1 if headlightsOn else 0)
			status = "ON" if headlightsOn else "OFF"
			print(f"Headlights: {status}")
			time.sleep(0.3)
		
		if prevInterior == 1 and interiorState == 0:
			interiorLightsOn = not interiorLightsOn
			lgpio.gpio_write(h, INTERIOR_LIGHTS_LED, 1 if interiorLightsOn else 0)
			status = "ON" if interiorLightsOn else "OFF"
			print(f"Interior Lights: {status}")
			time.sleep(0.3)
		
		if serviceBrakeState == 0 and not serviceBrakeActive:
			serviceBrakeActive = True
			print("Service Brake: ENGAGED")
		elif serviceBrakeState == 1 and serviceBrakeActive:
			serviceBrakeActive = False
			print("Service Brake: RELEASED")
		
		if trainHornState == 0 and not trainHornActive:
			trainHornActive = True
			print("Train Horn: SOUNDING")
		elif trainHornState == 1 and trainHornActive:
			trainHornActive = False
			print("Train Horn: OFF")
		
		if prevEmergencyBrake == 1 and emergencyBrakeState == 0:
			emergencyBrakeEngaged = not emergencyBrakeEngaged
			lgpio.gpio_write(h, EMERGENCY_BRAKE_LED, 1 if emergencyBrakeEngaged else 0)
			status = "🚨 ENGAGED 🚨" if emergencyBrakeEngaged else "RELEASED"
			print(f"EMERGENCY BRAKE: {status}")
			time.sleep(0.3)
		
		if prevDrivetrain == 1 and drivetrainState == 0:
			drivetrainManualMode = not drivetrainManualMode
			lgpio.gpio_write(h, DRIVETRAIN_MODE_LED, 1 if drivetrainManualMode else 0)
			mode = "MANUAL" if drivetrainManualMode else "AUTOMATIC"
			print(f"Drivetrain Mode: {mode}")
			if drivetrainManualMode:
				manualSetpointSpeed = commandedSpeed
				print(f"Manual setpoint initialized to: {manualSetpointSpeed} MPH")
			time.sleep(0.3)
		
		if drivetrainManualMode:
			if prevSpeedUp == 1 and speedUpState == 0:
				manualSetpointSpeed = min(manualSetpointSpeed + 5, 70)
				# Max 70 MPH.
				print(f"Manual Speed Setpoint: {manualSetpointSpeed} MPH")
				time.sleep(0.15)
			
			if prevSpeedDown == 1 and speedDownState == 0:
				manualSetpointSpeed = max(manualSetpointSpeed - 5, 0)
				# Min 0 MPH.
				print(f"Manual Speed Setpoint: {manualSetpointSpeed} MPH")
				time.sleep(0.15)
			
			if prevSpeedConfirm == 1 and speedConfirmState == 0:
				print(f"✓ SPEED CONFIRMED: {manualSetpointSpeed} MPH")
				time.sleep(0.3)
		
		prevLeft = leftState
		prevRight = rightState
		prevHeadlights = headlightsState
		prevInterior = interiorState
		prevServiceBrake = serviceBrakeState
		prevTrainHorn = trainHornState
		prevEmergencyBrake = emergencyBrakeState
		prevDrivetrain = drivetrainState
		prevSpeedUp = speedUpState
		prevSpeedDown = speedDownState
		prevSpeedConfirm = speedConfirmState
		
		time.sleep(0.01)

def getServiceBrakeState() -> bool:
	# Returns the current state of the service brake.
	return serviceBrakeActive

def getTrainHornState() -> bool:
	# Returns the current state of the train horn.
	return trainHornActive

def getEmergencyBrakeState() -> bool:
	# Returns the current state of the emergency brake.
	return emergencyBrakeEngaged

def getDrivetrainMode() -> str:
	# Returns the current drivetrain mode as a string.
	if drivetrainManualMode:
		return "MANUAL"
	else:
		return "AUTOMATIC"

def isManualMode() -> bool:
	# Returns whether the drivetrain is in manual mode.
	return drivetrainManualMode

def setCommandedSpeed(speed: float):
	# Sets the commanded speed from Train Model.
	global commandedSpeed
	commandedSpeed = max(0, min(speed, 70))
	# Clamp between 0-70 MPH.
	print(f"Commanded Speed set to: {commandedSpeed} MPH")

def setCommandedAuthority(authority: int):
	# Sets the commanded authority from Train Model.
	global commandedAuthority
	commandedAuthority = max(0, authority)
	print(f"Commanded Authority set to: {commandedAuthority} blocks")

def setCurrentSpeed(speed: float):
	# Sets the current actual speed of the train.
	global currentSpeed
	currentSpeed = max(0, min(speed, 70))

def getCommandedSpeed() -> float:
	# Returns the commanded speed from Train Model.
	return commandedSpeed

def getCommandedAuthority() -> int:
	# Returns the commanded authority from Train Model.
	return commandedAuthority

def getCurrentSpeed() -> float:
	# Returns the current actual speed of the train.
	return currentSpeed

def getManualSetpointSpeed() -> float:
	# Returns the manual mode speed setpoint.
	return manualSetpointSpeed

def getTargetSpeed() -> float:
	# Returns the target speed based on mode.
	if drivetrainManualMode:
		return manualSetpointSpeed
	else:
		return commandedSpeed

def getLeftDoorState() -> bool:
	# Returns the state of the left door.
	return leftDoorOpen

def getRightDoorState() -> bool:
	# Returns the state of the right door.
	return rightDoorOpen

def getHeadlightsState() -> bool:
	# Returns the state of the headlights.
	return headlightsOn

def getInteriorLightsState() -> bool:
	# Returns the state of the interior lights.
	return interiorLightsOn

def getSpeedUpPressed() -> bool:
	# Returns whether the speed up button is currently pressed.
	return speedUpPressed

def getSpeedDownPressed() -> bool:
	# Returns whether the speed down button is currently pressed.
	return speedDownPressed

def getSpeedConfirmPressed() -> bool:
	# Returns whether the speed confirm button is currently pressed.
	return speedConfirmPressed

def setPassengerEmergency(state: bool):
	# Sets passenger emergency signal state from Train Model.
	global passengerEmergencySignal
	passengerEmergencySignal = state
	value = 1 if state else 0
	result = lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, value)
	status = "ACTIVE ⚠️" if state else "CLEARED"
	print(f"Passenger Emergency Signal: {status} (GPIO {PASSENGER_EMERGENCY_LED} set to {value}, result: {result})")

def setBrakeFailure(state: bool):
	# Sets brake failure indicator state from Train Model.
	global brakeFailure
	brakeFailure = state
	lgpio.gpio_write(h, BRAKE_FAILURE_LED, 1 if state else 0)
	status = "FAILURE ⚠️" if state else "OK"
	print(f"Brake System: {status}")

def setEngineFailure(state: bool):
	# Sets engine failure indicator state from Train Model.
	global engineFailure
	engineFailure = state
	lgpio.gpio_write(h, ENGINE_FAILURE_LED, 1 if state else 0)
	status = "FAILURE ⚠️" if state else "OK"
	print(f"Engine System: {status}")

def setSignalFailure(state: bool):
	# Sets signal failure indicator state from Train Model.
	global signalFailure
	signalFailure = state
	lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 1 if state else 0)
	status = "FAILURE ⚠️" if state else "OK"
	print(f"Signal System: {status}")

def cleanup():
	# Cleans up GPIO on exit and closes all windows.
	global running
	running = False
	# Stop the button monitoring thread.
	time.sleep(0.1)
	# Give thread time to exit.
	lgpio.gpio_write(h, LEFT_DOOR_LED, 0)
	lgpio.gpio_write(h, RIGHT_DOOR_LED, 0)
	lgpio.gpio_write(h, HEADLIGHTS_LED, 0)
	lgpio.gpio_write(h, INTERIOR_LIGHTS_LED, 0)
	lgpio.gpio_write(h, EMERGENCY_BRAKE_LED, 0)
	lgpio.gpio_write(h, DRIVETRAIN_MODE_LED, 0)
	lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, 0)
	lgpio.gpio_write(h, BRAKE_FAILURE_LED, 0)
	lgpio.gpio_write(h, ENGINE_FAILURE_LED, 0)
	lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 0)
	lgpio.gpiochip_close(h)
	print("GPIO cleaned up. Goodbye!")

def cleanupAll():
	# Cleans up all resources and closes all windows.
	cleanup()
	try:
		if acPanel and acPanel.root.winfo_exists():
			acPanel.root.destroy()
	except:
		pass
	try:
		if announcementPanel and announcementPanel.root.winfo_exists():
			announcementPanel.root.destroy()
	except:
		pass
	try:
		if trackInfoPanel and trackInfoPanel.root.winfo_exists():
			trackInfoPanel.root.destroy()
	except:
		pass

def main():
	# Main program with all Tkinter UIs.
	global acPanel, announcementPanel, trackInfoPanel
	
	setup()
	
	buttonThread = threading.Thread(target=checkButtons, daemon=True)
	# Start button monitoring in background thread.
	buttonThread.start()
	
	root = tk.Tk()
	# Main speed control window.
	speedDisplay = TrainSpeedDisplayUI(root)
	
	acRoot = tk.Toplevel(root)
	# AC System window.
	acPanel = ACSystemPanel(acRoot)
	
	announcementRoot = tk.Toplevel(root)
	# Station Announcement window.
	announcementPanel = StationAnnouncementPanel(announcementRoot)
	
	trackInfoRoot = tk.Toplevel(root)
	# Track Information window.
	trackInfoPanel = TrackInformationPanel(trackInfoRoot)
	
	root.mainloop()

class TrainSpeedDisplayUI:
	# Speed display UI for train control.
	
	"""
	Attributes:
		root: The main tkinter window
		speedLabel: Label displaying current speed
		cmdSpeedValue: Label displaying commanded speed
		cmdAuthorityValue: Label displaying commanded authority
		manualSetpointValue: Label displaying manual setpoint speed
		modeValue: Label displaying drivetrain mode
	"""
	
	def __init__(self, root):
		# Initializes the speed display UI.
		self.root = root
		self.root.title("TRAIN SPEED CONTROL DISPLAY")
		self.root.geometry("900x700")
		self.root.configure(bg='#1e3c72')
		
		self._createWidgets()
		self._updateDisplay()
		
		self.root.protocol("WM_DELETE_WINDOW", self._onClose)
	
	def _createWidgets(self):
		# Creates all UI widgets.
		headerFrame = tk.Frame(self.root, bg='#0f1e3d')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="TRAIN SPEED CONTROL",
			font=('Arial', 28, 'bold'),
			bg='#0f1e3d',
			fg='white',
			pady=20
		)
		headerLabel.pack()
		
		mainFrame = tk.Frame(self.root, bg='#1e3c72')
		mainFrame.pack(fill='both', expand=True, padx=30, pady=20)
		
		speedFrame = tk.Frame(mainFrame, bg='#2c5aa0', relief='raised', bd=5)
		speedFrame.pack(fill='both', expand=True, pady=(0, 15))
		
		speedTitle = tk.Label(
			speedFrame,
			text="SPEEDOMETER",
			font=('Arial', 20, 'bold'),
			bg='#2c5aa0',
			fg='white',
			pady=10
		)
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
		self.speedLabel.pack(padx=30, pady=20)
		
		speedUnit = tk.Label(
			speedFrame,
			text="MPH",
			font=('Arial', 18, 'bold'),
			bg='#2c5aa0',
			fg='white',
			pady=5
		)
		speedUnit.pack()
		
		infoFrame = tk.Frame(mainFrame, bg='#1e3c72')
		infoFrame.pack(fill='both', expand=True)
		
		leftFrame = tk.Frame(infoFrame, bg='#1e3c72')
		leftFrame.pack(side='left', fill='both', expand=True, padx=(0, 7))
		
		self._createInfoBox(
			leftFrame,
			"COMMANDED SPEED",
			"cmdSpeedValue",
			"#3498db",
			"70 MPH"
		)
		
		self._createInfoBox(
			leftFrame,
			"COMMANDED AUTHORITY",
			"cmdAuthorityValue",
			"#9b59b6",
			"0 BLOCKS"
		)
		
		rightFrame = tk.Frame(infoFrame, bg='#1e3c72')
		rightFrame.pack(side='right', fill='both', expand=True, padx=(7, 0))
		
		self._createInfoBox(
			rightFrame,
			"MANUAL SETPOINT",
			"manualSetpointValue",
			"#e67e22",
			"-- MPH"
		)
		
		self._createInfoBox(
			rightFrame,
			"DRIVETRAIN MODE",
			"modeValue",
			"#27ae60",
			"AUTOMATIC"
		)
		
		instructionsFrame = tk.Frame(mainFrame, bg='#34495e', relief='raised', bd=3)
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
		instructions.pack()
	
	def _createInfoBox(self, parent, title: str, valueAttr: str, color: str, defaultText: str):
		# Creates an info display box.
		frame = tk.Frame(parent, bg=color, relief='raised', bd=4)
		frame.pack(fill='both', expand=True, pady=7)
		
		titleLabel = tk.Label(
			frame,
			text=title,
			font=('Arial', 14, 'bold'),
			bg=color,
			fg='white',
			pady=8
		)
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
		valueLabel.pack(padx=15, pady=(0, 15))
		
		setattr(self, valueAttr, valueLabel)
	
	def _updateDisplay(self):
		# Updates all display values.
		currentSpeedValue = getCurrentSpeed()
		commandedSpeedValue = getCommandedSpeed()
		commandedAuthorityValue = getCommandedAuthority()
		manualSetpoint = getManualSetpointSpeed()
		mode = getDrivetrainMode()
		isManual = isManualMode()
		
		self.speedLabel.config(text=f"{int(currentSpeedValue)}")
		
		if isManual:
			self.speedLabel.config(fg='#ffa500')
			# Orange for manual.
		else:
			self.speedLabel.config(fg='#00ff00')
			# Green for automatic.
		
		self.cmdSpeedValue.config(text=f"{int(commandedSpeedValue)} MPH")
		
		self.cmdAuthorityValue.config(text=f"{commandedAuthorityValue} BLOCKS")
		
		if isManual:
			self.manualSetpointValue.config(
				text=f"{int(manualSetpoint)} MPH",
				fg='#ffa500'
			)
		else:
			self.manualSetpointValue.config(
				text="-- MPH",
				fg='#666666'
			)
		
		self.modeValue.config(text=mode)
		if isManual:
			self.modeValue.config(bg='#e74c3c', fg='yellow')
		else:
			self.modeValue.config(bg='#1a1a2e', fg='white')
		
		self.root.after(100, self._updateDisplay)
	
	def _onClose(self):
		# Cleans up GPIO and closes all windows.
		print("\nCleaning up...")
		cleanupAll()
		self.root.destroy()

if __name__ == "__main__":
	main()