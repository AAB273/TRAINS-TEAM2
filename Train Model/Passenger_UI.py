import json    
from pathlib import Path 

def loadSocketConfig():
	# Loads socket configuration from config.json file.
	configPath = Path("config.json")
	if configPath.exists():
		with open(configPath, 'r') as f:
			config = json.load(f)
	return config.get("modules", {})


import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font
from tkinter import ttk
from train_data import getTrainManager
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer
from clock import clock
import pygame
import random

class TrainModelPassengerGUI:
	# The main GUI for the train model passenger interface.
	"""
	Attributes:
	mainColor: A string representing the primary background color.
	offColor: A string representing the secondary background color.
	currentTrain: The currently selected train object.
	trainManager: Manager object for handling train data.
	server: Socket server for inter-module communication.
	uiLabels: Dictionary storing all UI label references.
	uiIndicators: Dictionary storing all UI indicator references.
	canvasFrameCircle: Canvas object for temperature display.
	previousFailureSignalPickupState: Boolean tracking signal failure state.
	failureActivationInProgress: Boolean tracking failure activation status.
	previousActiveTrains: Set tracking which trains were active last update.
	"""

	def __init__(self):
		# Initializes the train model passenger GUI and socket connections.
		self.mainColor = '#1a1a4d'
		self.offColor = '#4d4d6d'
		self.currentTrain = None
		self.trainManager = getTrainManager()
		self.currentTrain = self.trainManager.getSelectedTrain() 
		
		# Socket server setup
		moduleConfig = loadSocketConfig()
		trainModelConfig = moduleConfig.get("Train Model", {"port": 12345})
		self.server = TrainSocketServer(port=trainModelConfig["port"], ui_id="Train Model")
		self.server.set_allowed_connections(["Train SW", "Train HW", "Track Model", "Test_UI"])
		self.server.start_server(self._processMessage)
		
		# Connect using ports from config
		trainSwConfig = moduleConfig.get("Train SW", {"port": 12346})
		trainHwConfig = moduleConfig.get("Train HW", {"port": 12347})
		trackModelConfig = moduleConfig.get("Track Model", {"port": 12344})

		pygame.mixer.init()

		self.server.connect_to_ui('localhost', trainSwConfig["port"], "Train SW")
		self.server.connect_to_ui('localhost', trainHwConfig["port"], "Train HW")
		self.server.connect_to_ui('localhost', trackModelConfig["port"], "Track Model")
		self.server.connect_to_ui('localhost', 12349, "Test_UI")
		
		self.uiLabels = {}
		self.uiIndicators = {}
		self.canvasFrameCircle = None

		self.previousFailureSignalPickupState = False
		self.failureActivationInProgress = False
		self.previousActiveTrains = set()
		self.clockSpeed = clock.getSpeed() * 100

		self.setupGUI()
		
	def _socketRefreshTrainSelector(self):
		# Refreshes the train selector UI to show/hide trains based on deployment status.
		print("Socket server requesting train selector refresh")
		self.root.after(0, self.refreshTrainSelector)

	def _animateTemperatureChange(self, targetTemp: float, train=None):
		# Gradually changes temperature using Tkinter's after() method.
		if train is None:
			train = self.currentTrain
			
		if not train:
			return

		currentTemp = train.cabinTemp
		targetTemp = float(targetTemp)
		
		if currentTemp < targetTemp:
			newTemp = currentTemp + 1
			train.setCabinTemp(newTemp)
			if train == self.currentTrain:
				self.updateUIFromTrain(train)
			self.root.after(1000, lambda: self._animateTemperatureChange(targetTemp, train))
		elif currentTemp > targetTemp:
			newTemp = currentTemp - 1
			train.setCabinTemp(newTemp)
			if train == self.currentTrain:
				self.updateUIFromTrain(train)
			self.root.after(1000, lambda: self._animateTemperatureChange(targetTemp, train))
		
		self.server.send_to_ui("Train SW", {
			'command': "Temp",
			'value': currentTemp,
			'train_id': train.trainId
		})
		self.server.send_to_ui("Train HW", {
			'command': "Temp",
			'value': currentTemp,
			'train_id': train.trainId
		})
   
	def _processMessage(self, message: dict, sourceUiId: str):
		# Processes incoming messages from socket server and updates train state accordingly.
		try:
			print(f"Received message from {sourceUiId}: {message}")

			command = message.get('command')
			
			# if command == "Clock":
			# 	self.Clock = message.get('value')
			value = message.get('value')
			trainId = message.get('train_id')
			
			# Determine which train to operate on
			if trainId is not None:
				# Operate on specified train
				train = self.trainManager.getTrain(trainId)
				if not train or not train.deployed:
					print(f"Train {trainId} not deployed or doesn't exist")
					return
			else:
				# Fall back to current train for backward compatibility
				train = self.currentTrain
				if not train:
					print("No current train selected")
					return
			
			# Test Commands
			if command == 'set_power':
				train.lastPowerCommand = train.powerCommand
				train.setPowerCommand(value)
			elif command == 'set_active':
				train.active = value
			elif command == 'set_right_door':
				if value == 'open':
					train.setRightDoor(1)
				elif value == 'close':
					train.setRightDoor(0)
			elif command == 'set_left_door':
				if value == 'open':
					train.setLeftDoor(1)
				elif value == 'close':
					train.setLeftDoor(0)
			elif command == 'set_headlights':
				if value == 'on':
					train.setHeadlights(1)
				else:
					train.setHeadlights(0)
			elif command == 'set_interior_lights':
				if value == 'on':
					train.setInteriorLights(1)
				elif value == 'off':
					train.setInteriorLights(0)
			elif command == 'emergency_brake':
				if value == 'on':
					self.emergencyBrakeActivated(train)
				else:
					train.setEmergencyBrake(0)
			elif command == 'set_service_brake':
				if self.failureBrakeVar.get() and train == self.currentTrain:
					pass
				else:
					if value == 'on':
						train.setServiceBrake(True)
					else:
						train.setServiceBrake(False)
			elif command == 'set_passenger_count':
				train.setPassengerCount(value)
			elif command == 'horn':
				pygame.mixer.Sound('Train Model/diesel-horn-02-98042.mp3').play()
			elif command == 'set_speed_limit':
				train.setSpeedLimit(value)
			elif command == 'set_elevation':
				train.setElevation(value)
			elif command == 'set_grade':
				train.setGrade(value)
			elif command == 'select_train':
				self.onTrainSelected(value)
			elif command == 'set_temperature':
				targetTemp = value
				self._animateTemperatureChange(targetTemp, train)
			elif command == 'set_authority':
				wasActive = train.active if train else False
				train.setAuthority(value)
				self.server.send_to_ui("Train HW",value)
				if not wasActive and train.active:
					print(f"Train {train.trainId} activated - refreshing selector")
					self.refreshTrainSelectorIfNeeded()  
			elif command == 'set_commanded_speed':
				train.setCommandedSpeed(value)
				self.server.send_to_ui("Train HW", {
					'command': "Commanded Speed",
					'value': value,
					'train_id': trainId if trainId else train.trainId
				})
			elif command == 'set_station':
				train.setStation(value)
			elif command == 'set_time_to_station':
				train.setTimeToStation(value)
			elif command == 'deploy_train':
				trainId = value
				trainObj = self.trainManager.getTrain(trainId)
				if trainObj:
					trainObj.deployed = True
					print(f"Deployed train {trainId}")
					self._socketRefreshTrainSelector()
					trainObj.calculateForceSpeedAccelerationDistance()
			elif command == 'undeploy_train':
				trainId = value
				trainObj = self.trainManager.getTrain(trainId)
				if trainObj:
					trainObj.deployed = False
					print(f"Undeployed train {trainId}")
					self._socketRefreshTrainSelector()
			elif command == 'deploy_all':
				for trainId in range(1, 15):
					trainObj = self.trainManager.getTrain(trainId)
					if trainObj:
						trainObj.deployed = True
						self.currentTrain.calculateForceSpeedAccelerationDistance()
				print("Deployed all trains")
				self._socketRefreshTrainSelector()
			elif command == 'undeploy_all':
				for trainId in range(1, 15):
					trainObj = self.trainManager.getTrain(trainId)
					if trainObj:
						trainObj.deployed = False
				print("Undeployed all trains")
				self._socketRefreshTrainSelector()
			elif command == 'refresh_trains':
				self._socketRefreshTrainSelector()

			# MAIN COMMANDS
			elif command == 'Temp':
				targetTemp = value
				self._animateTemperatureChange(targetTemp, train)
			elif command == 'Announcement':
				train.setStation(value)
			elif command == 'Service Brake':
				if self.failureBrakeVar.get() and train == self.currentTrain:
					pass
				else:
					train.setServiceBrake(value)
			elif command == 'Emergency Brake':
				train.setEmergencyBrake(value)
			elif command == 'Left Door Signal':
				train.setLeftDoor(value)
			elif command == 'Right Door Signal':
				train.setRightDoor(value)
			elif command == 'Headlights':
				train.setHeadlights(value)
			elif command == 'Cabin Lights':
				train.setInteriorLights(value)
			elif command == 'Power Command':
				train.setPowerCommand(value)
			elif command == 'Train Horn':
				pygame.mixer.Sound('Train Model/diesel-horn-02-98042.mp3').play()
			elif command == 'Commanded Authority':
				wasActive = train.active if train else False
				train.setAuthority(value)
				self.server.send_to_ui("Train SW", {
					'command': "Commanded Authority",
					'value': value,
					'train_id': trainId if trainId else train.trainId
				})
				self.server.send_to_ui("Train HW", {
					'command': "Commanded Authority",
					'value': value,
					'train_id': trainId if trainId else train.trainId
				})
				if not wasActive and train.active:
					print(f"Train {train.trainId} activated - refreshing selector")
					self.refreshTrainSelectorIfNeeded() 
			elif command == 'Commanded Speed':
				train.setCommandedSpeed(value)
				self.server.send_to_ui("Train SW", {
					'command': "Commanded Speed",
					'value': value,
					'train_id': trainId if trainId else train.trainId
				})
				self.server.send_to_ui("Train HW", {
					'command': "Commanded Speed",
					'value': value,
					'train_id': trainId if trainId else train.trainId
				})
			elif command == 'Block Occupancy':
				train.setBlock(value)
			elif command == 'Passengers Boarding':
				self.updateBoarding(value, train)
			elif command == 'Beacon':
				if train.line == 'Green':
					print(f"Beacon data for train {train.trainId}")
			
			# Update UI if this is the currently selected train
			if train == self.currentTrain:
				self.updateUIFromTrain(train)
				
		except Exception as e:
			print(f"Error processing message: {e}")

	def continuousPhysicsUpdate(self):
		# Continuously updates physics for all active trains and sends speed updates.
		# Process all active trains
		for trainId in range(1, 15):
			train = self.trainManager.getTrain(trainId)
			if train and train.deployed and train.active:
				# If calculateForceSpeedAccelerationDistance needs to be called individually:
				oldSpeed = train.speed
				train.calculateForceSpeedAccelerationDistance()
				newSpeed = train.speed
				
				if oldSpeed != newSpeed:
					# Send updates for this train
					self.server.send_to_ui("Train HW", {
						'command': "Current Speed",
						'value': train.speed,
						'train_id': train.trainId
					})
					self.server.send_to_ui("Train SW", {
						'command': "Current Speed",
						'value': train.speed,
						'train_id': train.trainId
					})
					self.server.send_to_ui("Track Model", {
						'command': 'Current Speed',
						'value': train.speed,
						'train_id': train.trainId
					})
				
				# Update passenger disembarking logic for each train
				# if train.atStation:
				# 	self.updateDisembarking(train)
		
		# Update UI for the currently selected train only
		if self.currentTrain and self.currentTrain.active:
			self.updateUIFromTrain(self.currentTrain)
		
		# Schedule next update
		self.root.after(100, self.continuousPhysicsUpdate)

	def emergencyBrakeActivated(self, train=None):
		# Activates the emergency brake and notifies other modules.
		if train is None:
			train = self.currentTrain
			
		train.setEmergencyBrake(True)
		train.setAcceleration(-2.73)
		self.server.send_to_ui("Train HW", {
			'command': "Passenger Emergency Signal",
			'value': True,
			'train_id': train.trainId
		})
		self.server.send_to_ui("Train SW", {
			'command': "Passenger Emergency Signal",
			'value': True,
			'train_id': train.trainId
		})
		print(f"EMERGENCY BRAKE ACTIVATED for train {train.trainId}!")
		
		if train == self.currentTrain:
			self.updateUIFromTrain(train)

	def failureServiceBrakeVarChanged(self):
		# Handles service brake failure mode activation/deactivation.
		if self.failureBrakeVar.get():
			self.currentTrain.setServiceBrake(0)
			self.server.send_to_ui("Train SW", {'command': "Service Brake Failure", 'value': True})
			self.server.send_to_ui("Train HW", {'command': "Service Brake Failure", 'value': True})
			print(f"Service Brake Failure Activated")
		elif self.failureBrakeVar.get() == 0:
			print(f"Service Brake Deactivated")
			self.server.send_to_ui("Train SW", {'command': "Service Brake Failure", 'value': False})
			self.server.send_to_ui("Train HW", {'command': "Service Brake Failure", 'value': False})

	def failureTrainEngineVarChanged(self):
		# Handles train engine failure mode activation/deactivation.
		if self.failureTrainEngineVar.get():
			self.currentTrain.setEngineFailure(True)
			self.currentTrain.setPowerCommand(0)
			self.currentTrain.setAcceleration(0)
			self.server.send_to_ui("Train SW", {'command': "Train Engine Failure", 'value': True})
			self.server.send_to_ui("Train HW", {'command': "Train Engine Failure", 'value': True})
			print(f"Train Engine Failure Activated")
		elif self.failureTrainEngineVar.get() == 0:
			self.currentTrain.setEngineFailure(False)
			print(f"Train Engine Failure Deactivated")
			self.server.send_to_ui("Train SW", {"Train Engine Failure", 0})
			self.server.send_to_ui("Train HW", {"Train Engine Failure", 0})

	def updateFailureSignal(self):
		# Updates signal pickup failure state when checkbox changes.
		currentState = self.failureSignalPickupVar.get()
		
		# Only proceed if state actually changed
		if currentState == self.previousFailureSignalPickupState:
			return
		
		if currentState and not self.failureActivationInProgress:
			self.activateSignalFailure()
		else:
			self.deactivateSignalFailure()
		
		self.previousFailureSignalPickupState = currentState

	def deactivateSignalFailure(self):
		# Deactivates signal pickup failure mode.
		print(f"Signal Pickup Failure Deactivated")
		self.server.send_to_ui("Train SW", {'command': "Signal Pickup Failure", 'value': False})
		self.server.send_to_ui("Train HW", {'command': "Signal Pickup Failure", 'value': False})

	def activateSignalFailure(self):
		# Activates signal pickup failure mode and resets track parameters.
		print(f"Signal Pickup Failure Activated")
		self.failureActivationInProgress = True
		
		self.currentTrain.speedLimit = 0
		self.currentTrain.grade = 0
		self.currentTrain.elevation = 0
		
		self.server.send_to_ui("Train SW", {'command': "Signal Pickup Failure", 'value': True})
		self.server.send_to_ui("Train HW", {'command': "Signal Pickup Failure", 'value': True})
		
		self.failureActivationInProgress = False
			
	def updateDisembarking(self, train):
		# Updates passenger disembarking when train is stopped with doors open.
		if train and train.active and train.passengerCount != 0:
			if (train.atStation and redundantCheck):
				redundantCheck = True
				passengerCount = train.passengerCount
				disembarking = random.randint(0, passengerCount)
				
				train.setDisembarking(disembarking)
				train.setPassengerCount(passengerCount - disembarking)
				
				self.server.send_to_ui("Track Model", {
					"command": 'Passenger Disembarking', 
					'value': disembarking,
					'train_id': train.trainId
				})
				self.server.send_to_ui('Track Model', {
					'command': 'Train Occupancy', 
					'value': train.passengerCount,
					'train_id': train.trainId
				})

	def updateBoarding(self, boarding: int, train=None):
		# Updates passenger boarding count and sends occupancy update to track model.
		if train is None:
			train = self.currentTrain
			
		MAX_CAPACITY = 222
		if boarding > MAX_CAPACITY:
			train.passengerCount = MAX_CAPACITY
		else:
			train.passengerCount = train.passengerCount + boarding
		
		# Send update to track model
		self.server.send_to_ui("Track Model", {
			'command': 'Train Occupancy',
			'value': train.passengerCount,
			'train_id': train.train_id
		})  


	def updateUIFromTrain(self, train):
		# Updates all UI elements when train data changes.
		# Update speed
		imperialSpeed = train.speed * 2.23964
		self.uiLabels['speed'].config(text=f"{imperialSpeed:.4f} MPH")
		
		# Update acceleration
		imperialAcceleration = train.acceleration * 2.23694
		self.uiLabels['acceleration'].config(text=f"{imperialAcceleration:.4f} MPH²")
		
		# Update passenger count
		self.uiLabels['passengerCount'].config(text=f"Passenger Count: {train.passengerCount}")
		self.uiLabels['crewCount'].config(text=f"Crew Count: {train.crewCount}")

		# SIGNAL PICKUP FAILURE CHECKING
		if self.failureSignalPickupVar.get():
			# Failure active - show ??? values
			self.uiLabels['Commanded Authority'].config(text="Commanded Authority: ??? Blocks")
			self.uiLabels['Commanded Speed'].config(text="Commanded Speed: ??? MPH")
		else:
			self.uiLabels['Commanded Authority'].config(text=f"Commanded Authority: {train.commandedAuthority:.0f} Blocks")
			self.uiLabels['Commanded Speed'].config(text=f"Commanded Speed: {train.commandedSpeed:.0f} MPH")
	
		# Check for failure state changes
		self.updateFailureSignal()

		# Normal operation - show actual values
		imperialSpeedLimit = train.speedLimit / 1.61
		self.uiLabels['Speed Limit'].config(text=f"Speed Limit: {imperialSpeedLimit:.1f} MPH")

		# Update Grade and Elevation
		self.uiLabels['Grade'].config(text=f"Grade: {train.grade}%")
		self.uiLabels['Elevation'].config(text=f"Elevation: {train.elevation}ft")
		# Update cabin temp
		if self.canvasFrameCircle and 'cabin_temp' in self.uiLabels:
			self.canvasFrameCircle.itemconfig(self.uiLabels['cabin_temp'], text=f"{train.cabinTemp:.0f}°F")
		
		# Update dimensions
		imperialHeight = train.height * 3.28084
		imperialLength = train.length * 3.28084
		imperialWidth = train.width * 3.28084
		self.uiLabels['height'].config(text=f"Height: {imperialHeight:.1f}ft")
		self.uiLabels['length'].config(text=f"Length: {imperialLength:.1f}ft")
		self.uiLabels['width'].config(text=f"Width: {imperialWidth:.1f}ft")

		# Update Announcement and Time
		if self.currentTrain.emergencyBrakeActive:
			self.uiLabels['announcement'].config(text=f"EMERGENCY")
		else:
			self.uiLabels['announcement'].config(text=f"{train.announcement} in {train.timeToStation}mins")

		# Update power command and commanded values
		self.uiLabels['power_command'].config(text=f"{train.powerCommand:.0f} Watts")
		
		# Update door and light indicators
		rightDoorColor = 'green' if train.rightDoorOpen else 'red'
		self.uiIndicators['cabin_right_led'].itemconfig(self.uiIndicators['cabin_right_oval'], fill=rightDoorColor)
		
		leftDoorColor = 'green' if train.leftDoorOpen else 'red'
		self.uiIndicators['cabin_left_led'].itemconfig(self.uiIndicators['cabin_left_oval'], fill=leftDoorColor)
		
		headlightColor = 'green' if train.headlightsOn else 'red'
		self.uiIndicators['headlights_led'].itemconfig(self.uiIndicators['headlights_oval'], fill=headlightColor)
		
		interiorColor = 'green' if train.interiorLightsOn else 'red'
		self.uiIndicators['interior_led'].itemconfig(self.uiIndicators['interior_oval'], fill=interiorColor)

	def onTrainSelected(self, trainId: int):
		# Handles train selection from dropdown and updates current train.
		train = self.trainManager.selectTrain(trainId)
		if train and train.active:
			self.currentTrain = train
			self.updateUIFromTrain(train)
			self.trainSelectorVar.set(f"Train {trainId}")
		else:
			print(f"Train {trainId} is not active or doesn't exist")

	def refreshTrainSelectorIfNeeded(self):
		# Checks if active trains have changed and refreshes selector if needed.
		# Get current active trains
		currentActiveTrains = set()
		for trainId in range(1, 15):
			train = self.trainManager.getTrain(trainId)
			if train and train.active:
				currentActiveTrains.add(trainId)
		
		# Compare with previous state
		if currentActiveTrains != self.previousActiveTrains:
			print(f"Active trains changed: {self.previousActiveTrains} -> {currentActiveTrains}")
			self.previousActiveTrains = currentActiveTrains.copy()
			self.refreshTrainSelector()

	def refreshTrainSelector(self):
		# Refreshes the train selector dropdown with currently active trains.
		print("Refreshing train selector dropdown...")
		
		# Get current selection
		currentSelection = self.trainSelectorVar.get()
		
		# Get active trains (from our tracked state or calculate fresh)
		activeTrains = list(self.previousActiveTrains)
		activeTrains.sort()
		
		print(f"Found {len(activeTrains)} active trains: {activeTrains}")
		
		# Only rebuild if we have trains
		if activeTrains:
			# Rebuild menu
			menu = self.trainSelector['menu']
			menu.delete(0, 'end')
			
			for trainId in activeTrains:
				menu.add_command(
					label=f"Train {trainId}", 
					command=lambda tid=trainId: self.onTrainSelected(tid)
				)
			
			# Update selection if needed
			selectedId = None
			if currentSelection.startswith("Train "):
				try:
					selectedId = int(currentSelection.replace("Train ", ""))
				except:
					selectedId = None
			
			# If selected train is no longer active or not set, select first available
			if selectedId not in activeTrains:
				newId = activeTrains[0]
				self.trainSelectorVar.set(f"Train {newId}")
				self.onTrainSelected(newId)
			
			self.trainSelectorLabel.config(text=f"Select Train ({len(activeTrains)} Active)")
		else:
			# No active trains
			menu = self.trainSelector['menu']
			menu.delete(0, 'end')
			self.trainSelectorVar.set("No Trains Active")
			self.trainSelectorLabel.config(text="Select Train (0 Active)")


	def setupGUI(self):
		# Sets up the complete GUI layout and initializes all UI elements.
		self.root = tk.Tk()
		self.root.title("Passenger Train Model GUI")
		self.root.configure(bg=self.mainColor)
		self.root.geometry("900x800") 
		self.root.iconbitmap("blt logo ico.ico") 

		# Train Selector Dropdown Frame 
		trainSelectorContainer = tk.Frame(self.root, bg=self.mainColor, height=30)
		trainSelectorContainer.pack(fill='x', padx=8, pady=3)
		trainSelectorContainer.pack_propagate(False)

		self.trainSelectorLabel = tk.Label(trainSelectorContainer, text="Select Train", bg=self.mainColor, fg='white', font=('Arial', 10, 'bold'))
		self.trainSelectorLabel.pack(side='left', padx=(8, 3))

		# Train Selector
		self.trainSelectorVar = tk.StringVar()
		self.trainSelector = tk.OptionMenu(trainSelectorContainer, self.trainSelectorVar, "Loading...")
		self.trainSelector.config(bg=self.mainColor, fg='white', font=('Arial', 9), width=20)  
		self.trainSelector.pack(side='left', padx=(0, 8))
		self.trainSelector['menu'].config(bg=self.mainColor, fg='white')
        

		# Top Container
		topContainer = tk.Frame(self.root, bg=self.mainColor, highlightbackground="black", highlightthickness=3)
		topContainer.pack(fill='x', padx=8, pady=3)

		# BLT Logo 
		bltLogoImage = Image.open("Train Model/blt logo.png")
		convertedBltLogoImage = bltLogoImage.resize((60, 60))
		convertedBltLogoImage = ImageTk.PhotoImage(convertedBltLogoImage)
		bltLogoFrame = tk.Frame(topContainer, bg=self.mainColor, height=65, width=65)
		bltLogoFrame.pack(fill='x', side='left', pady=2, padx=2)
		bltLogoFrame.pack_propagate(False)
		tk.Label(bltLogoFrame, image=convertedBltLogoImage, bg=self.mainColor).pack(padx=1, pady=1)
		bltLogoFrame.image = convertedBltLogoImage

		# Time Frame
		timeFrame = tk.Frame(topContainer, bg=self.offColor, width=150, height=65, highlightbackground="black", highlightthickness=3)
		timeFrame.pack(side='left', padx=2, pady=2)
		timeFrame.pack_propagate(False)
		self.uiLabels['time'] = tk.Label(timeFrame, text="Time", bg=self.offColor, fg='white', font=('Arial', 16, 'bold'))
		self.uiLabels['time'].pack(padx=3, pady=3)

		# Announcement Frame 
		announcementFrame = tk.Frame(topContainer, bg=self.offColor, width=600, height=65, highlightbackground="black", highlightthickness=3)
		announcementFrame.pack(side='left', padx=2, pady=2)
		announcementFrame.pack_propagate(False)
		self.uiLabels['announcement'] = tk.Label(announcementFrame, text="Awaiting Deployment", bg=self.offColor, fg='white', font=('Arial', 16, 'bold'))
		self.uiLabels['announcement'].pack(padx=3, pady=3)

		# Main frames
		leftFrame = tk.Frame(self.root, bg=self.mainColor)
		leftFrame.pack(side='left', fill='both', padx=8, pady=3)

		rightFrame = tk.Frame(self.root, bg=self.mainColor)
		rightFrame.pack(side='right', fill='both', expand=True, padx=8, pady=3)

		self.convertedAdImages = []
		self.adIndex = 1
		adImages = [
			"Train Model/wendy's_AD.jpg",
			"Train Model/wendy's_AD2.jpg",
			"Train Model/wendy's_AD3.jpg",
			"Train Model/wendy's_AD4.jpg"]
		
		self.convertedAdImages = []

		for adPath in adImages:
			adImage = Image.open(adPath)
			convertedAdImage = adImage.resize((400, 260))
			convertedAdImage = ImageTk.PhotoImage(convertedAdImage)
			self.convertedAdImages.append(convertedAdImage)

		self.currentAdImage = self.convertedAdImages[0]
		advertisement = tk.Frame(rightFrame, height=260, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		advertisement.pack(side='top', padx=2, pady=2, fill='x')
		advertisement.pack_propagate(False)
		self.adLabel = tk.Label(advertisement, image=self.currentAdImage)
		self.adLabel.pack(padx=1, pady=1)
		self.adLabel.image = self.currentAdImage

		# Doors/Lights Frame 
		doorsAndLightsFrame = tk.Frame(rightFrame, height=200, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		doorsAndLightsFrame.pack(side='top', padx=2, pady=2, fill='x')
		doorsAndLightsFrame.pack_propagate(False)

		# Cabin Doors 
		cabinDoorsFrame = tk.Frame(doorsAndLightsFrame, bg=self.offColor)
		cabinDoorsFrame.pack(side='left', padx=3, pady=2, fill='both', expand=True)

		tk.Label(cabinDoorsFrame, text="Right Door", bg=self.offColor, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
		cabinRightLed = tk.Canvas(cabinDoorsFrame, width=120, height=40, bg=self.offColor, highlightthickness=0)
		cabinRightLed.pack(pady=3)
		cabinRightOval = cabinRightLed.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
		self.uiIndicators['cabin_right_led'] = cabinRightLed
		self.uiIndicators['cabin_right_oval'] = cabinRightOval

		thinLine = tk.Frame(cabinDoorsFrame, bg='black', height=1)
		thinLine.pack(pady=8, fill='x', padx=15)

		tk.Label(cabinDoorsFrame, text="Left Door", bg=self.offColor, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
		cabinLeftLed = tk.Canvas(cabinDoorsFrame, width=120, height=40, bg=self.offColor, highlightthickness=0)
		cabinLeftLed.pack(pady=3)
		cabinLeftOval = cabinLeftLed.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
		self.uiIndicators['cabin_left_led'] = cabinLeftLed
		self.uiIndicators['cabin_left_oval'] = cabinLeftOval

		# Lights 
		lightsFrame = tk.Frame(doorsAndLightsFrame, bg=self.offColor)
		lightsFrame.pack(side='left', padx=3, pady=2, fill='both', expand=True)

		tk.Label(lightsFrame, text="Headlights", bg=self.offColor, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
		headlightsLed = tk.Canvas(lightsFrame, width=120, height=40, bg=self.offColor, highlightthickness=0)
		headlightsLed.pack(pady=3)
		headlightsOval = headlightsLed.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
		self.uiIndicators['headlights_led'] = headlightsLed
		self.uiIndicators['headlights_oval'] = headlightsOval

		thinLine = tk.Frame(lightsFrame, bg='black', height=1)
		thinLine.pack(pady=8, fill='x', padx=15)

		tk.Label(lightsFrame, text="Interior Lights", bg=self.offColor, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
		interiorLed = tk.Canvas(lightsFrame, width=120, height=40, bg=self.offColor, highlightthickness=0)
		interiorLed.pack(pady=3)
		interiorOval = interiorLed.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
		self.uiIndicators['interior_led'] = interiorLed
		self.uiIndicators['interior_oval'] = interiorOval

		# Murphy Failure Modes 
		murphyFrame = tk.Frame(rightFrame, height=200, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		murphyFrame.pack(side='top', padx=2, pady=2, fill='both')
		murphyFrame.pack_propagate(False)
		tk.Label(murphyFrame, text="Murphy Failure Modes", bg=self.offColor, fg='white', font=('Arial', 16, 'bold')).pack(pady=3)

		# Separator lines in Murphy frame
		thinLine = tk.Frame(murphyFrame, bg='black', width=400)
		thinLine.pack(pady=2)

		self.failureTrainEngineVar = tk.BooleanVar(value=False)
		trainEngineSwitch = ttk.Checkbutton(murphyFrame, text="Train Engine", variable=self.failureTrainEngineVar, 
										  command=lambda: self.failureTrainEngineVarChanged(),
										  style="Medium.TCheckbutton")
		trainEngineSwitch.pack(pady=6, padx=3, fill='x', expand=True)

		# Separator line
		thinLine = tk.Frame(murphyFrame, bg='black', width=400)
		thinLine.pack(pady=2)

		self.failureSignalPickupVar = tk.BooleanVar(value=False)
		signalPickupSwitch = ttk.Checkbutton(murphyFrame, text="Signal Pickup", variable=self.failureSignalPickupVar,
											 style="Medium.TCheckbutton")
		signalPickupSwitch.pack(pady=6, padx=3, fill='x', expand=True)

		# Separator line
		thinLine = tk.Frame(murphyFrame, bg='black', width=400)
		thinLine.pack(pady=2)

		self.failureBrakeVar = tk.BooleanVar(value=False)
		brakeSwitch = ttk.Checkbutton(murphyFrame, text="Brake", variable=self.failureBrakeVar,
									   command=lambda: self.failureServiceBrakeVarChanged(),
									   style="Medium.TCheckbutton")
		brakeSwitch.pack(pady=6, padx=3, fill='x', expand=True)

		style = ttk.Style()
		style.theme_use('clam')
		style.configure("Medium.TCheckbutton", indicatorsize=16, padding=8, font=('Arial', 12, 'bold'), background=self.offColor, foreground='white')
		style.map("Medium.TCheckbutton", background=[('active', self.mainColor)])

		# Train Metrics 
		trainMetricsFrame = tk.Frame(leftFrame, width=480, height=580, bg=self.mainColor, highlightbackground="black", highlightthickness=3)
		trainMetricsFrame.pack(side='top', padx=2, pady=2)
		trainMetricsFrame.pack_propagate(False)
		tk.Label(trainMetricsFrame, text="Train Metrics", bg=self.offColor, fg='white', highlightbackground='black', highlightthickness=3, 
				 font=('Arial', 9, 'bold')).pack(padx=3, pady=3)

		# Live Metrics 
		liveMetrics = tk.Frame(trainMetricsFrame, width=320, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		liveMetrics.pack(side='right', padx=2, pady=2, fill='y')
		liveMetrics.pack_propagate(False)
		tk.Label(liveMetrics, text="Live Metrics", bg=self.offColor, fg='white', font=('Arial', 16, 'bold')).pack(pady=3)

		tk.Label(liveMetrics, text="Speed", bg=self.offColor, fg='white', font=('Arial', 20, 'bold')).pack(pady=6)
		self.uiLabels['speed'] = tk.Label(liveMetrics, text="0.0 MPH", bg=self.offColor, fg='white', font=('Arial', 18, 'bold'))
		self.uiLabels['speed'].pack(pady=3)

		# Separator line after speed
		thinLine = tk.Frame(liveMetrics, bg='black', width=300)
		thinLine.pack()

		tk.Label(liveMetrics, text="Acceleration", bg=self.offColor, fg='white', font=('Arial', 20, 'bold')).pack(pady=6)
		self.uiLabels['acceleration'] = tk.Label(liveMetrics, text="0.0 MPH²", bg=self.offColor, fg='white', font=('Arial', 18, 'bold'))
		self.uiLabels['acceleration'].pack(pady=3)

		# Separator line after acceleration
		thinLine = tk.Frame(liveMetrics, bg='black', width=300)
		thinLine.pack()

		self.uiLabels['passengerCount'] = tk.Label(liveMetrics, text="Passenger Count: 0", bg=self.offColor, fg='white', font=('Arial', 14, 'bold'))
		self.uiLabels['passengerCount'].pack(pady=8)
		self.uiLabels['crewCount'] = tk.Label(liveMetrics, text="Crew Count: 0", bg=self.offColor, fg='white', font=('Arial', 14, 'bold'))
		self.uiLabels['crewCount'].pack(pady=8)

		# Separator line after crew count
		thinLine = tk.Frame(liveMetrics, bg='black', width=300)
		thinLine.pack()

		self.uiLabels['Speed Limit'] = tk.Label(liveMetrics, text="Speed Limit: 0", bg=self.offColor, fg='white', font=('Arial', 13, 'bold'))
		self.uiLabels['Speed Limit'].pack(pady=8)

		# Separator line after speed limit
		thinLine = tk.Frame(liveMetrics, bg='black', width=300)
		thinLine.pack()

		# Bottom metrics
		bottomLiveMetrics = tk.Frame(liveMetrics, width=320, bg=self.offColor)
		bottomLiveMetrics.pack(side='bottom', fill='x', pady=(0, 15))

		gradeElevationRow = tk.Frame(bottomLiveMetrics, bg=self.offColor)
		gradeElevationRow.pack(fill='x', pady=(0, 25))

		self.uiLabels['Grade'] = tk.Label(gradeElevationRow, text="Grade %: 0", bg=self.offColor, fg='white', font=('Arial', 12, 'bold'))
		self.uiLabels['Grade'].pack(side='left', padx=(12, 3), expand=True)

		self.uiLabels['Elevation'] = tk.Label(gradeElevationRow, text="Elevation (ft): 0", bg=self.offColor, fg='white', font=('Arial', 12, 'bold'))
		self.uiLabels['Elevation'].pack(side='right', padx=(3, 12), expand=True)

		# Separator line after grade/elevation
		thinLineBottom = tk.Frame(bottomLiveMetrics, bg='black', width=300)
		thinLineBottom.pack()

		self.uiLabels['Commanded Authority'] = tk.Label(bottomLiveMetrics, text="Commanded Authority (ft): 0", bg=self.offColor, fg='white', font=('Arial', 11, 'bold'))
		self.uiLabels['Commanded Authority'].pack(pady=8)

		self.uiLabels['Commanded Speed'] = tk.Label(bottomLiveMetrics, text="Commanded Speed (MPH): 0", bg=self.offColor, fg='white', font=('Arial', 11, 'bold'))
		self.uiLabels['Commanded Speed'].pack(pady=3)

		# Cabin Temp
		cabinTempFrame = tk.Frame(trainMetricsFrame, width=120, height=160, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		cabinTempFrame.pack(side='top', padx=2, pady=2)
		cabinTempFrame.pack_propagate(False)
		tk.Label(cabinTempFrame, text="Cabin Temp", bg=self.offColor, fg='white', font=('Arial', 9, 'bold')).pack(padx=3, pady=(8, 3))

		self.canvasFrameCircle = tk.Canvas(cabinTempFrame, width=100, height=140, bg=self.offColor, highlightbackground=self.offColor)
		self.canvasFrameCircle.pack(side='top', expand=True)
		self.canvasFrameCircle.create_oval(8, 8, 92, 92, fill=self.offColor, outline='black', width=2)
		self.uiLabels['cabin_temp'] = self.canvasFrameCircle.create_text(50, 50, text="72°F", font=('Arial', 20, 'bold'), fill='white')

		# Train Dimensions
		trainDimensionsFrame = tk.Frame(trainMetricsFrame, width=120, height=220, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		trainDimensionsFrame.pack(side='top', padx=2, pady=2)
		trainDimensionsFrame.pack_propagate(False)
		tk.Label(trainDimensionsFrame, text="Train Dimensions", bg=self.offColor, fg='white', font=('Arial', 8, 'bold')).pack(padx=3, pady=3)

		self.uiLabels['height'] = tk.Label(trainDimensionsFrame, text="Height: 11.0ft", bg=self.offColor, fg='white', font=('Arial', 10))
		self.uiLabels['height'].pack(padx=1, pady=15)
		self.uiLabels['length'] = tk.Label(trainDimensionsFrame, text="Length: 150.0ft", bg=self.offColor, fg='white', font=('Arial', 10))
		self.uiLabels['length'].pack(padx=1, pady=15)
		self.uiLabels['width'] = tk.Label(trainDimensionsFrame, text="Width: 10.0ft", bg=self.offColor, fg='white', font=('Arial', 10))
		self.uiLabels['width'].pack(padx=1, pady=15)

		# Power Command 
		trainPowerCommand = tk.Frame(trainMetricsFrame, width=120, height=180, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		trainPowerCommand.pack(side='top', padx=2, pady=2)
		trainPowerCommand.pack_propagate(False)
		tk.Label(trainPowerCommand, text="Power Command", bg=self.offColor, fg='white', font=('Arial', 9, 'bold')).pack(padx=3, pady=3)
		self.uiLabels['power_command'] = tk.Label(trainPowerCommand, text="0 Watts", bg=self.offColor, fg='white', font=('Arial', 13))
		self.uiLabels['power_command'].pack(padx=1, pady=25)

		# Emergency Brake 
		emergencyBrake = tk.Frame(leftFrame, width=480, height=80, highlightbackground="black", highlightthickness=2, bg=self.offColor)
		emergencyBrake.pack(side='top', padx=2, pady=2)
		emergencyBrake.pack_propagate(False)
		emergencyBrakeButton = tk.Button(emergencyBrake, text="EMERGENCY BRAKE", bg="red", fg='white', font=('Arial', 20),
										 command=self.emergencyBrakeActivated,
										 relief='raised', bd=1, padx=10, pady=2, height=40)
		emergencyBrakeButton.pack(fill='both')

		self.root.protocol("WM_DELETE_WINDOW", self.onClosing)

	def cycleThroughAds(self):
		# Cycles through advertisement images at regular intervals.
		# Get the next ad index
		self.adIndex = (self.adIndex + 1) % len(self.convertedAdImages)
		
		# Update the ad image
		self.currentAdImage = self.convertedAdImages[self.adIndex]
		
		# Update the label
		if hasattr(self, 'adLabel'):
			self.adLabel.config(image=self.currentAdImage)
			self.adLabel.image = self.currentAdImage
		
		# Schedule next ad change (6000ms = 6 seconds)
		self.root.after(6000, self.cycleThroughAds)  

	def updateTime(self):
		# Continuously updates the time display every second.
		localTime = clock.getTime()
		self.uiLabels['time'].config(text=localTime)
		self.root.after(100, self.updateTime)

	def onClosing(self):
		# Handles application closing and cleanup.
		print("Closing application...")
		self.root.destroy()
		os._exit(0)
	
	def run(self):
		# Starts the application and initializes all scheduled updates.
		# Register observer to update UI when train data changes
		self.currentTrain.addObserver(self.updateUIFromTrain)

		# Initialize the train selector dropdown
		self.root.after(100, self.refreshTrainSelector)

		self.root.after(self.clockSpeed, self.continuousPhysicsUpdate)

		self.root.after(100, self.updateTime)

		self.root.after(5000, self.cycleThroughAds)

		self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
	app = TrainModelPassengerGUI()
	app.run()