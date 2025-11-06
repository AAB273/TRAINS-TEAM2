#!/usr/bin/env python3
"""
Train Control System Comprehensive Test UI
Tests all inputs and outputs for the hardware train controller
"""

import tkinter as tk
from tkinter import ttk
import sys
import threading

try:
	from TC_HW_MainUI import (
		setup, cleanup, checkButtons,
		setPassengerEmergency, 
		setBrakeFailure, 
		setEngineFailure, 
		setSignalFailure,
		getServiceBrakeState,
		getTrainHornState,
		getEmergencyBrakeState,
		setCommandedSpeed,
		setCommandedAuthority,
		setCurrentSpeed,
		getCommandedSpeed,
		getCommandedAuthority,
		getCurrentSpeed,
		getManualSetpointSpeed,
		getDrivetrainMode,
		isManualMode,
		getLeftDoorState,
		getRightDoorState,
		getHeadlightsState,
		getInteriorLightsState,
		getSpeedUpPressed,
		getSpeedDownPressed,
		getSpeedConfirmPressed,
		leftDoorOpen,
		rightDoorOpen,
		headlightsOn,
		interiorLightsOn,
		drivetrainManualMode
	)
	import TC_HW_MainUI
except ImportError as e:
	print(f"Error: Could not import TC_HW_MainUI - {e}")
	sys.exit(1)

class ComprehensiveTestUI:
	# Train Controller Test UI for all train control inputs and outputs.
	
	"""
	Attributes:
		root: The main tkinter window
		notebook: ttk Notebook widget for organizing test categories
		passengerEmergency: BooleanVar for passenger emergency signal
		brakeFailure: BooleanVar for brake failure indicator
		engineFailure: BooleanVar for engine failure indicator
		signalFailure: BooleanVar for signal failure indicator
		serviceBrake: BooleanVar for service brake status
		trainHorn: BooleanVar for train horn status
		emergencyBrake: BooleanVar for emergency brake status
		commandedSpeedVar: DoubleVar for commanded speed input
		commandedAuthorityVar: IntVar for commanded authority input
		currentSpeedVar: DoubleVar for current speed input
	"""
	
	def __init__(self, root):
		# Initializes the Train Controller Test UI.
		self.root = root
		self.root.title("TRAIN CONTROLLER TEST UI")
		self.root.geometry("1000x800")
		self.root.configure(bg='#2c3e50')
		
		setup()
		# Initialize GPIO.
		
		self.buttonThread = threading.Thread(target=checkButtons, daemon=True)
		# Start button monitoring thread.
		self.buttonThread.start()
		
		self.passengerEmergency = tk.BooleanVar(value=False)
		self.brakeFailure = tk.BooleanVar(value=False)
		self.engineFailure = tk.BooleanVar(value=False)
		self.signalFailure = tk.BooleanVar(value=False)
		self.serviceBrake = tk.BooleanVar(value=False)
		self.trainHorn = tk.BooleanVar(value=False)
		self.emergencyBrake = tk.BooleanVar(value=False)
		self.leftDoor = tk.BooleanVar(value=False)
		self.rightDoor = tk.BooleanVar(value=False)
		self.headlights = tk.BooleanVar(value=False)
		self.interiorLights = tk.BooleanVar(value=False)
		self.drivetrainMode = tk.BooleanVar(value=False)
		self.speedUp = tk.BooleanVar(value=False)
		self.speedDown = tk.BooleanVar(value=False)
		self.speedConfirm = tk.BooleanVar(value=False)
		
		self.commandedSpeedVar = tk.DoubleVar(value=0.0)
		self.commandedAuthorityVar = tk.IntVar(value=0)
		self.currentSpeedVar = tk.DoubleVar(value=0.0)
		
		self._createWidgets()
		self._monitorButtonStates()
		
		self.root.protocol("WM_DELETE_WINDOW", self._onClose)
	
	def _createWidgets(self):
		# Creates all UI widgets.
		headerFrame = tk.Frame(self.root, bg='#1e5a8e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="TRAIN CONTROLLER TEST UI",
			font=('Arial', 24, 'bold'),
			bg='#1e5a8e',
			fg='white',
			pady=15
		)
		headerLabel.pack()
		
		style = ttk.Style()
		style.theme_use('default')
		style.configure('TNotebook', background='#2c3e50', borderwidth=0)
		style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 11, 'bold'))
		
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
		
		self._createOutputsTab()
		self._createInputsTab()
	
	def _createOutputsTab(self):
		# Creates the tab for testing output LEDs.
		frame = tk.Frame(self.notebook, bg='#34495e')
		self.notebook.add(frame, text='Output LEDs')
		
		title = tk.Label(
			frame,
			text="LED Indicator Controls (Outputs from Train Model)",
			font=('Arial', 18, 'bold'),
			bg='#2980b9',
			fg='white',
			relief='raised',
			bd=4,
			padx=20,
			pady=10
		)
		title.pack(pady=(20, 30))
		
		controlFrame = tk.Frame(frame, bg='#d6eaf8', relief='raised', bd=4)
		controlFrame.pack(fill='both', expand=True, padx=20, pady=10)
		
		self._createLEDControl(
			controlFrame, 
			"Passenger Emergency Signal",
			self.passengerEmergency,
			self._togglePassengerEmergency,
			'#e74c3c'
		)
		
		self._createLEDControl(
			controlFrame,
			"Brake Failure",
			self.brakeFailure,
			self._toggleBrakeFailure,
			'#e67e22'
		)
		
		self._createLEDControl(
			controlFrame,
			"Engine Failure",
			self.engineFailure,
			self._toggleEngineFailure,
			'#f39c12'
		)
		
		self._createLEDControl(
			controlFrame,
			"Signal Failure",
			self.signalFailure,
			self._toggleSignalFailure,
			'#9b59b6'
		)
		
		instructionsFrame = tk.Frame(frame, bg='#5dade2', relief='raised', bd=3)
		instructionsFrame.pack(fill='x', pady=(20, 10), padx=20)
		
		instructions = tk.Label(
			instructionsFrame,
			text="Toggle these to simulate signals from Train Model",
			font=('Arial', 12),
			bg='#5dade2',
			fg='white',
			pady=10
		)
		instructions.pack()
	
	def _createInputsTab(self):
		# Creates the tab for monitoring input buttons.
		frame = tk.Frame(self.notebook, bg='#34495e')
		self.notebook.add(frame, text='Input Buttons')
		
		title = tk.Label(
			frame,
			text="Hardware Button Status (Inputs to Train Model)",
			font=('Arial', 18, 'bold'),
			bg='#2980b9',
			fg='white',
			relief='raised',
			bd=4,
			padx=20,
			pady=10
		)
		title.pack(pady=(20, 30))
		
		statusFrame = tk.Frame(frame, bg='#2c3e50', relief='raised', bd=4)
		statusFrame.pack(fill='both', expand=True, padx=20, pady=10)
		
		leftCol = tk.Frame(statusFrame, bg='#2c3e50')
		leftCol.pack(side='left', fill='both', expand=True, padx=10, pady=10)
		
		middleCol = tk.Frame(statusFrame, bg='#2c3e50')
		middleCol.pack(side='left', fill='both', expand=True, padx=10, pady=10)
		
		rightCol = tk.Frame(statusFrame, bg='#2c3e50')
		rightCol.pack(side='left', fill='both', expand=True, padx=10, pady=10)
		
		self._createButtonStatus(leftCol, "Service Brake", "serviceBrakeStatus", self.serviceBrake, '#e74c3c', 'GPIO 13')
		self._createButtonStatus(leftCol, "Train Horn", "trainHornStatus", self.trainHorn, '#f39c12', 'GPIO 26')
		self._createButtonStatus(leftCol, "Emergency Brake", "emergencyBrakeStatus", self.emergencyBrake, '#c0392b', 'GPIO 7')
		
		self._createButtonStatus(middleCol, "Left Door", "leftDoorStatus", self.leftDoor, '#3498db', 'GPIO 17')
		self._createButtonStatus(middleCol, "Right Door", "rightDoorStatus", self.rightDoor, '#3498db', 'GPIO 22')
		self._createButtonStatus(middleCol, "Headlights", "headlightsStatus", self.headlights, '#f1c40f', 'GPIO 18')
		self._createButtonStatus(middleCol, "Interior Lights", "interiorLightsStatus", self.interiorLights, '#f1c40f', 'GPIO 20')
		
		self._createButtonStatus(rightCol, "Drivetrain Mode", "drivetrainStatus", self.drivetrainMode, '#27ae60', 'GPIO 4')
		self._createButtonStatus(rightCol, "Speed Up", "speedUpStatus", self.speedUp, '#16a085', 'GPIO 15')
		self._createButtonStatus(rightCol, "Speed Down", "speedDownStatus", self.speedDown, '#d35400', 'GPIO 9')
		self._createButtonStatus(rightCol, "Speed Confirm", "speedConfirmStatus", self.speedConfirm, '#8e44ad', 'GPIO 11')
		
		instructionsFrame = tk.Frame(frame, bg='#5dade2', relief='raised', bd=3)
		instructionsFrame.pack(fill='x', pady=(20, 10), padx=20)
		
		instructions = tk.Label(
			instructionsFrame,
			text="Press physical buttons to see status updates in real-time\n" +
				 "Speed buttons only work in MANUAL mode (press Drivetrain Mode button first)",
			font=('Arial', 11),
			bg='#5dade2',
			fg='white',
			pady=10
		)
		instructions.pack()
	
	def _createSpeedControlTab(self):
		# Creates the tab for speed and authority control.
		frame = tk.Frame(self.notebook, bg='#34495e')
		self.notebook.add(frame, text='Speed Control')
		
		title = tk.Label(
			frame,
			text="Speed & Authority Control (Simulate Train Model)",
			font=('Arial', 18, 'bold'),
			bg='#2980b9',
			fg='white',
			relief='raised',
			bd=4,
			padx=20,
			pady=10
		)
		title.pack(pady=(20, 30))
		
		mainFrame = tk.Frame(frame, bg='#2c3e50', relief='raised', bd=4)
		mainFrame.pack(fill='both', expand=True, padx=20, pady=10)
		
		self._createSpeedInput(mainFrame, "Commanded Speed (MPH)", self.commandedSpeedVar, 0, 70, self._updateCommandedSpeed, '#3498db')
		self._createSpeedInput(mainFrame, "Commanded Authority (Blocks)", self.commandedAuthorityVar, 0, 20, self._updateCommandedAuthority, '#9b59b6')
		self._createSpeedInput(mainFrame, "Current Speed (MPH)", self.currentSpeedVar, 0, 70, self._updateCurrentSpeed, '#2ecc71')
		
		buttonFrame = tk.Frame(mainFrame, bg='#2c3e50')
		buttonFrame.pack(pady=20)
		
		resetBtn = tk.Button(
			buttonFrame,
			text="RESET ALL TO 0",
			font=('Arial', 14, 'bold'),
			bg='#e74c3c',
			fg='white',
			activebackground='#c0392b',
			relief='raised',
			bd=3,
			command=self._resetAllSpeeds,
			width=20,
			height=2
		)
		resetBtn.pack()
		
		instructionsFrame = tk.Frame(frame, bg='#5dade2', relief='raised', bd=3)
		instructionsFrame.pack(fill='x', pady=(20, 10), padx=20)
		
		instructions = tk.Label(
			instructionsFrame,
			text="Adjust sliders to simulate Train Model commands\n" +
				 "Use Speed Up (GPIO 15), Speed Down (GPIO 9), Confirm (GPIO 11) for manual control",
			font=('Arial', 11),
			bg='#5dade2',
			fg='white',
			pady=10
		)
		instructions.pack()
	
	def _createStatusTab(self):
		# Creates the tab for real-time system status.
		frame = tk.Frame(self.notebook, bg='#34495e')
		self.notebook.add(frame, text='System Status')
		
		title = tk.Label(
			frame,
			text="Real-Time System Status",
			font=('Arial', 18, 'bold'),
			bg='#2980b9',
			fg='white',
			relief='raised',
			bd=4,
			padx=20,
			pady=10
		)
		title.pack(pady=(20, 30))
		
		statusFrame = tk.Frame(frame, bg='#2c3e50', relief='raised', bd=4)
		statusFrame.pack(fill='both', expand=True, padx=20, pady=10)
		
		self.statusCommandedSpeed = self._createStatusDisplay(statusFrame, "Commanded Speed", "0 MPH", '#3498db')
		self.statusCommandedAuthority = self._createStatusDisplay(statusFrame, "Commanded Authority", "0 Blocks", '#9b59b6')
		self.statusCurrentSpeed = self._createStatusDisplay(statusFrame, "Current Speed", "0 MPH", '#2ecc71')
		self.statusManualSetpoint = self._createStatusDisplay(statusFrame, "Manual Setpoint", "0 MPH", '#e67e22')
		self.statusDrivetrainMode = self._createStatusDisplay(statusFrame, "Drivetrain Mode", "AUTOMATIC", '#27ae60')
		
		self._updateStatusDisplay()
	
	def _createLEDControl(self, parent, label, variable, command, color):
		# Creates a control row for an LED.
		frame = tk.Frame(parent, bg='#aed6f1', relief='raised', bd=3)
		frame.pack(fill='x', padx=15, pady=10)
		
		labelWidget = tk.Label(
			frame,
			text=label,
			font=('Arial', 16, 'bold'),
			bg='#aed6f1',
			fg='#1e5a8e',
			anchor='w',
			padx=15
		)
		labelWidget.pack(side='left', fill='x', expand=True)
		
		statusFrame = tk.Frame(frame, bg='#34495e', relief='sunken', bd=2)
		statusFrame.pack(side='left', padx=10)
		
		statusLabel = tk.Label(
			statusFrame,
			textvariable=variable,
			font=('Arial', 12, 'bold'),
			bg='#34495e',
			fg='white',
			width=8,
			padx=10,
			pady=5
		)
		statusLabel.pack()
		
		def updateStatus(*args):
			if variable.get():
				statusLabel.config(text="ON", bg=color)
			else:
				statusLabel.config(text="OFF", bg='#34495e')
		
		variable.trace('w', updateStatus)
		updateStatus()
		
		button = tk.Button(
			frame,
			text="TOGGLE",
			font=('Arial', 14, 'bold'),
			bg='#3498db',
			fg='white',
			activebackground='#2980b9',
			relief='raised',
			bd=3,
			padx=20,
			pady=8,
			command=command
		)
		button.pack(side='right', padx=15)
	
	def _createButtonStatus(self, parent, label, attrName, variable, color, gpioLabel):
		# Creates a button status display.
		frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3)
		frame.pack(fill='x', pady=8)
		
		titleFrame = tk.Frame(frame, bg='#34495e')
		titleFrame.pack(fill='x')
		
		titleLabel = tk.Label(
			titleFrame,
			text=label,
			font=('Arial', 14, 'bold'),
			bg='#34495e',
			fg='white',
			anchor='w',
			padx=10,
			pady=5
		)
		titleLabel.pack(side='left')
		
		gpioLabel = tk.Label(
			titleFrame,
			text=f"({gpioLabel})",
			font=('Arial', 10),
			bg='#34495e',
			fg='#95a5a6',
			anchor='e',
			padx=10
		)
		gpioLabel.pack(side='right')
		
		statusLabel = tk.Label(
			frame,
			text="INACTIVE",
			font=('Arial', 16, 'bold'),
			bg='#2c3e50',
			fg='#95a5a6',
			pady=10,
			relief='sunken',
			bd=2
		)
		statusLabel.pack(fill='x', padx=10, pady=(0, 10))
		
		setattr(self, attrName, statusLabel)
		
		if variable:
			def updateButtonStatus(*args):
				if variable.get():
					statusLabel.config(text="ACTIVE", bg=color, fg='white')
				else:
					statusLabel.config(text="INACTIVE", bg='#2c3e50', fg='#95a5a6')
			
			variable.trace('w', updateButtonStatus)
	
	def _createSpeedInput(self, parent, label, variable, minVal, maxVal, command, color):
		# Creates a speed/authority input control.
		frame = tk.Frame(parent, bg=color, relief='raised', bd=3)
		frame.pack(fill='x', padx=20, pady=15)
		
		titleLabel = tk.Label(
			frame,
			text=label,
			font=('Arial', 14, 'bold'),
			bg=color,
			fg='white',
			pady=8
		)
		titleLabel.pack()
		
		valueLabel = tk.Label(
			frame,
			textvariable=variable,
			font=('Arial', 24, 'bold'),
			bg='#1a1a2e',
			fg='white',
			pady=10,
			width=10
		)
		valueLabel.pack(pady=(5, 10))
		
		sliderFrame = tk.Frame(frame, bg='#2c3e50')
		sliderFrame.pack(fill='x', padx=20, pady=(0, 15))
		
		slider = tk.Scale(
			sliderFrame,
			from_=minVal,
			to=maxVal,
			resolution=0.5 if isinstance(variable, tk.DoubleVar) else 1,
			orient='horizontal',
			variable=variable,
			command=command,
			font=('Arial', 12, 'bold'),
			bg=color,
			fg='white',
			activebackground='#2c3e50',
			troughcolor='#1a1a2e',
			relief='raised',
			bd=2,
			length=600,
			width=20,
			sliderlength=40,
			showvalue=0
		)
		slider.pack()
	
	def _createStatusDisplay(self, parent, label, defaultValue, color):
		# Creates a status display row.
		frame = tk.Frame(parent, bg=color, relief='raised', bd=3)
		frame.pack(fill='x', padx=20, pady=10)
		
		titleLabel = tk.Label(
			frame,
			text=label,
			font=('Arial', 14, 'bold'),
			bg=color,
			fg='white',
			anchor='w',
			padx=15,
			pady=8
		)
		titleLabel.pack(fill='x')
		
		valueLabel = tk.Label(
			frame,
			text=defaultValue,
			font=('Arial', 20, 'bold'),
			bg='#1a1a2e',
			fg='white',
			anchor='w',
			padx=15,
			pady=12
		)
		valueLabel.pack(fill='x', padx=10, pady=(0, 10))
		
		return valueLabel
	
	def _togglePassengerEmergency(self):
		# Toggles passenger emergency signal.
		newState = not self.passengerEmergency.get()
		self.passengerEmergency.set(newState)
		setPassengerEmergency(newState)
	
	def _toggleBrakeFailure(self):
		# Toggles brake failure indicator.
		newState = not self.brakeFailure.get()
		self.brakeFailure.set(newState)
		setBrakeFailure(newState)
	
	def _toggleEngineFailure(self):
		# Toggles engine failure indicator.
		newState = not self.engineFailure.get()
		self.engineFailure.set(newState)
		setEngineFailure(newState)
	
	def _toggleSignalFailure(self):
		# Toggles signal failure indicator.
		newState = not self.signalFailure.get()
		self.signalFailure.set(newState)
		setSignalFailure(newState)
	
	def _updateCommandedSpeed(self, value):
		# Updates commanded speed.
		speed = float(value)
		setCommandedSpeed(speed)
	
	def _updateCommandedAuthority(self, value):
		# Updates commanded authority.
		authority = int(float(value))
		setCommandedAuthority(authority)
	
	def _updateCurrentSpeed(self, value):
		# Updates current speed.
		speed = float(value)
		setCurrentSpeed(speed)
	
	def _resetAllSpeeds(self):
		# Resets all speeds and authority to 0.
		self.commandedSpeedVar.set(0)
		self.commandedAuthorityVar.set(0)
		self.currentSpeedVar.set(0)
		setCommandedSpeed(0)
		setCommandedAuthority(0)
		setCurrentSpeed(0)
	
	def _monitorButtonStates(self):
		# Monitors button states and updates display.
		import TC_HW_MainUI
		
		brakeState = getServiceBrakeState()
		hornState = getTrainHornState()
		emergencyState = getEmergencyBrakeState()
		
		self.serviceBrake.set(brakeState)
		self.trainHorn.set(hornState)
		self.emergencyBrake.set(emergencyState)
		
		self.leftDoor.set(TC_HW_MainUI.leftDoorOpen)
		self.rightDoor.set(TC_HW_MainUI.rightDoorOpen)
		self.headlights.set(TC_HW_MainUI.headlightsOn)
		self.interiorLights.set(TC_HW_MainUI.interiorLightsOn)
		self.drivetrainMode.set(TC_HW_MainUI.drivetrainManualMode)
		
		self.speedUp.set(TC_HW_MainUI.speedUpPressed)
		self.speedDown.set(TC_HW_MainUI.speedDownPressed)
		self.speedConfirm.set(TC_HW_MainUI.speedConfirmPressed)
		
		self.root.after(50, self._monitorButtonStates)
	
	def _updateStatusDisplay(self):
		# Updates the system status tab.
		commandedSpeed = getCommandedSpeed()
		commandedAuthority = getCommandedAuthority()
		currentSpeed = getCurrentSpeed()
		manualSetpoint = getManualSetpointSpeed()
		mode = getDrivetrainMode()
		
		self.statusCommandedSpeed.config(text=f"{int(commandedSpeed)} MPH")
		self.statusCommandedAuthority.config(text=f"{commandedAuthority} Blocks")
		self.statusCurrentSpeed.config(text=f"{int(currentSpeed)} MPH")
		self.statusManualSetpoint.config(text=f"{int(manualSetpoint)} MPH")
		self.statusDrivetrainMode.config(text=mode)
		
		self.root.after(100, self._updateStatusDisplay)
	
	def _onClose(self):
		# Cleans up GPIO and closes window.
		print("\nCleaning up...")
		cleanup()
		self.root.destroy()

if __name__ == "__main__":
	root = tk.Tk()
	app = ComprehensiveTestUI(root)
	root.mainloop()