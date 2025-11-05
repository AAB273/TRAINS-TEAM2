#!/usr/bin/env python3
"""
Train Control System for Raspberry Pi 5 - WITH SOCKET SERVER

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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory for TrainSocketServer

from TC_HW_AirConditioning_UI import ACSystemPanel
from TC_HW_Announcement_UI import StationAnnouncementPanel
from TC_HW_TrackInfo_UI import TrackInformationPanel
from TrainSocketServer import TrainSocketServer

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
rightDoorOpen = False
headlightsOn = False
interiorLightsOn = False
serviceBrakeActive = False
trainHornActive = False
emergencyBrakeEngaged = False
drivetrainManualMode = False
speedUpPressed = False
speedDownPressed = False
speedConfirmPressed = False
commandedSpeed = 0
commandedAuthority = 0
currentSpeed = 0
manualSetpointSpeed = 0
passengerEmergencySignal = False
brakeFailure = False
engineFailure = False
signalFailure = False

h = None
running = True
acPanel = None
announcementPanel = None
trackInfoPanel = None

def setup():
	global h
	
	h = lgpio.gpiochip_open(4)
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
		speedDownPressed = (speedDownState == 0)
		speedConfirmPressed = (speedConfirmState == 0)
		
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
				print(f"Manual Speed Setpoint: {manualSetpointSpeed} MPH")
				time.sleep(0.2)
			
			if prevSpeedDown == 1 and speedDownState == 0:
				manualSetpointSpeed = max(manualSetpointSpeed - 5, 0)
				print(f"Manual Speed Setpoint: {manualSetpointSpeed} MPH")
				time.sleep(0.2)
		
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
		
		time.sleep(0.05)

def getCurrentSpeed():
	return currentSpeed

def getCommandedSpeed():
	return commandedSpeed

def getCommandedAuthority():
	return commandedAuthority

def getManualSetpointSpeed():
	return manualSetpointSpeed

def getDrivetrainMode():
	return "MANUAL" if drivetrainManualMode else "AUTOMATIC"

def isManualMode():
	return drivetrainManualMode

def cleanup():
	global running, h
	running = False
	time.sleep(0.2)
	
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
	global acPanel, announcementPanel, trackInfoPanel
	
	setup()
	
	buttonThread = threading.Thread(target=checkButtons, daemon=True)
	buttonThread.start()
	
	root = tk.Tk()
	speedDisplay = TrainSpeedDisplayUI(root)
	
	acRoot = tk.Toplevel(root)
	acPanel = ACSystemPanel(acRoot)
	
	announcementRoot = tk.Toplevel(root)
	announcementPanel = StationAnnouncementPanel(announcementRoot)
	
	trackInfoRoot = tk.Toplevel(root)
	trackInfoPanel = TrackInformationPanel(trackInfoRoot)
	
	root.mainloop()

class TrainSpeedDisplayUI:
	
	def __init__(self, root):
		self.root = root
		self.root.title("TRAIN SPEED CONTROL DISPLAY")
		self.root.geometry("900x700")
		self.root.configure(bg='#1e3c72')
		
		# Socket Server Setup
		self.server = TrainSocketServer(port=7, ui_id="Train HW")
		self.server.set_allowed_connections(["Train HW"])
		self.server.start_server(self._process_message)
		self.server.connect_to_ui('localhost', 5, "Train Model")

		self._createWidgets()
		self._updateDisplay()
		
		self.root.protocol("WM_DELETE_WINDOW", self._onClose)
	
	def _process_message(self, message, source_ui_id):
		"""Process incoming messages from other UIs"""
		try:
			print(f"Received from {source_ui_id}: {message}")
			
			command = message.get('command')
			value = message.get('value')
			
			if command == 'Commanded Speed':
				global commandedSpeed
				commandedSpeed = value
			
			elif command == 'Commanded Authority':
				global commandedAuthority
				commandedAuthority = value
			
			elif command == 'Actual Velocity':
				global currentSpeed
				currentSpeed = value
			
			elif command == 'Passenger Emergency Signal':
				global passengerEmergencySignal
				passengerEmergencySignal = value
				lgpio.gpio_write(h, PASSENGER_EMERGENCY_LED, 1 if value else 0)
			
			elif command == 'Brake Failure':
				global brakeFailure
				brakeFailure = value
				lgpio.gpio_write(h, BRAKE_FAILURE_LED, 1 if value else 0)
			
			elif command == 'Train Engine Failure':
				global engineFailure
				engineFailure = value
				lgpio.gpio_write(h, ENGINE_FAILURE_LED, 1 if value else 0)
			
			elif command == 'Signal Pickup Failure':
				global signalFailure
				signalFailure = value
				lgpio.gpio_write(h, SIGNAL_FAILURE_LED, 1 if value else 0)
		
		except Exception as e:
			print(f"Error processing message: {e}")
	
	def _createWidgets(self):
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
		currentSpeedValue = getCurrentSpeed()
		commandedSpeedValue = getCommandedSpeed()
		commandedAuthorityValue = getCommandedAuthority()
		manualSetpoint = getManualSetpointSpeed()
		mode = getDrivetrainMode()
		isManual = isManualMode()
		
		self.speedLabel.config(text=f"{int(currentSpeedValue)}")
		
		if isManual:
			self.speedLabel.config(fg='#ffa500')
		else:
			self.speedLabel.config(fg='#00ff00')
		
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
		print("\nClosing application...")
		self.server.stop_server()
		cleanupAll()
		self.root.destroy()

if __name__ == "__main__":
	main()