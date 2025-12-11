"""
Train Data Management System
Handles all train data and state for both Test UI and Passenger UI
All calculations are done in metric, then converted to imperial when displayed onto the UI, except for temperature which is already in farenheight
"""
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from GreenLineData import GreenLine
from RedLineData import RedLine
from BlueLineData import BlueLine


class Train:
	# Represents a single train with all its properties.
	"""
	Attributes:
	trainId: An integer uniquely identifying the train.
	speed: A float representing the current speed in m/s.
	acceleration: A float representing the current acceleration in m/s².
	passengerCount: An integer representing the number of passengers.
	passengersDisembarking: An integer representing passengers currently disembarking.
	crewCount: An integer representing the number of crew members.
	powerCommand: A float representing the power command in watts.
	cabinTemp: A float representing the cabin temperature in fahrenheit.
	grade: A float representing the track grade percentage.
	elevation: An integer representing the elevation in feet.
	speedLimit: A float representing the speed limit in m/s.
	commandedSpeed: A float representing the commanded speed in m/s.
	commandedAuthority: A float representing the commanded authority in blocks.
	distanceLeft: A float representing the distance remaining to station.
	height: A float representing the train height in meters.
	length: A float representing the train length in meters.
	width: A float representing the train width in meters.
	rightDoorOpen: A boolean indicating if the right door is open.
	leftDoorOpen: A boolean indicating if the left door is open.
	headlightsOn: A boolean indicating if headlights are on.
	interiorLightsOn: A boolean indicating if interior lights are on.
	engineFailure: A boolean indicating if engine failure is active.
	signalPickupFailure: A boolean indicating if signal pickup failure is active.
	brakeFailure: A boolean indicating if brake failure is active.
	emergencyBrakeActive: A boolean indicating if emergency brake is active.
	serviceBrakeActive: A boolean indicating if service brake is active.
	deployed: A boolean indicating if the train is deployed.
	active: A boolean indicating if the train is active.
	line: A string representing the line assignment.
	block: An integer representing the current block.
	previousBlock: An integer representing the previous block.
	station: A string representing the current station.
	timeToStation: An integer representing time to next station in minutes.
	"""

	def __init__(self, trainId: int):
		# Initializes a train with default values and the given train ID.
		self.trainId = trainId
		
		self.speed = 0.0
		self.acceleration = 0.0
		self.passengerCount = 0
		self.passengersDisembarking = 0
		self.crewCount = 2
		self.powerCommand = 0.0
		self.cabinTemp = 72.0
		self.grade = 2
		self.elevation = 1
		self.speedLimit = 70
		self.speedLimitMps = self.speedLimit / 3.6
		self.commandedSpeed = 0
		self.commandedAuthority = 0
		self.distanceLeft = None

		self.prevGrade = 0
		self.prevElevation = 0
		self.prevSpeedLimit = 40

		# For physics calculations
		self.lastPowerCommand = 0.0
		self.lastServiceBrake = True
		self.lastEmergencyBrake = False
		
		# Dimensions
		self.height = 3.42
		self.length = 32.2
		self.width = 2.65
		
		# Door states (boolean: True=Open, False=Closed)
		self.rightDoorOpen = False
		self.leftDoorOpen = False
		
		# Light states (boolean: True=On, False=Off)
		self.headlightsOn = False
		self.interiorLightsOn = False
		
		# Murphy failure modes
		self.engineFailure = False
		self.signalPickupFailure = False
		self.brakeFailure = False
		
		# Emergency brake and Service Brake
		self.emergencyBrakeActive = False
		self.serviceBrakeActive = True
		
		# Deployment status
		self.deployed = True
		self.active = False
		
		# Line assignment
		self.line = "green" 
		self.lineData = GreenLine()
		self.block = 63
		self.atStation = False
		self.previousBlock = 63

		# Station
		self.announcement = "Awaiting Deployment"
		self.timeToStation = 0
		self.emergencyAnnouncement = "EMERGENCY"
		
		self.authorityReceived = False

		# Observers (callbacks for UI updates)
		self._observers = []

	def addObserver(self, callback):
		# Registers a callback to be notified of train state changes.
		self._observers.append(callback)
	
	def removeObserver(self, callback):
		# Unregisters a callback from the observer list.
		if callback in self._observers:
			self._observers.remove(callback)
	
	def _notifyObservers(self):
		# Notifies all registered observers of state changes.
		for callback in self._observers:
			callback(self)

	def resetTrain(self):
		"""Reset train to default state while preserving some settings"""
		# Store what to preserve
		trainId = self.trainId
		wasDeployed = self.deployed
		
		# Reset all attributes using setters where possible
		self.setSpeed(0.0)
		self.setAcceleration(0.0)
		self.setPassengerCount(0)
		self.setDisembarking(0)
		self.setCrewCount(2)
		self.setPowerCommand(0.0)
		self.setCabinTemp(72.0)
		self.setGrade(0)
		self.setElevation(0)
		self.setSpeedLimit(40)
		self.setGrade(0)
		self.setElevation(0)
		self.setSpeedLimit(40)
		self.setCommandedSpeed(0)
		self.setAuthority(0)
		self.distanceLeft = None
		
		# Reset physics tracking
		self.lastPowerCommand = 0.0
		self.lastServiceBrake = True
		self.lastEmergencyBrake = False
		
		# Reset dimensions
		self.setHeight(3.42)
		self.setLength(32.2)
		self.setWidth(2.65)
		
		# Reset door states
		self.setRightDoor(False)
		self.setLeftDoor(False)
		
		# Reset light states
		self.setHeadlights(False)
		self.setInteriorLights(False)
		
		# Reset failure modes
		self.setEngineFailure(False)
		self.setSignalPickupFailure(False)
		self.setBrakeFailure(False)
		
		# Reset brakes
		self.setEmergencyBrake(False)
		self.setServiceBrake(True)
		
		# Reset line and position
		self.setLine("green")
		self.block = 63
		self.previousBlock = 63
		self.atStation = False
		
		# Reset station info
		self.setAnnouncement("Awaiting Deployment")
		self.setTimeToStation(0)
		
		# Reset activation flags
		self.authorityReceived = False
		self.active = False
		
		# Notify observers
		self._notifyObservers()
		print(f"Train {trainId} reset to default state")
	
	def setLine(self, value: str):
		# Sets the train's line assignment and initializes line data.
		self.line = value
		if value == 'green':
			self.lineData = GreenLine()
		elif value == 'red':
			self.lineData = RedLine()
		else:
			self.lineData = BlueLine()
		self._notifyObservers()
	
	def setBlock(self, value: int):
		# Updates the current block and retrieves associated speed limit and grade.
		self.previousBlock = self.block
		self.block = value
		self.setSpeedLimit(self.lineData.getValue(value, 'speedLimit'))
		self.setGrade(self.lineData.getValue(value, 'blockGradePercent'))
		stationCheck = self.lineData.getValue(value,'infrastructure') 
		if "STATION" in stationCheck:
			self.atStation = True
		else:
			self.atStation = False
		distanceDict = self.lineData.getDistance(value)
		if distanceDict != None:
			self.distanceLeft = distanceDict['distance']
			print(self.distanceLeft)
		# Line check
		if value == 9 and not ("STATION" in stationCheck):
			self.setLine('red')

			
		
	# Metric setters with validation
	def setSpeedLimit(self, value: float):
		# Sets the speed limit for the train in m/s.
		self.prevSpeedLimit = self.speedLimit
		self.speedLimit = float(value)
		self.speedLimitMps = self.speedLimit / 3.6
		self._notifyObservers()
	
	def setElevation(self, value: float):
		# Sets the elevation of the train in feet.
		self.prevElevation = self.elevation
		self.elevation = float(value)
		self._notifyObservers()

	def setGrade(self, value: float):
		# Sets the grade percentage of the track.
		self.prevGrade = self.grade
		self.grade = float(value)
		self._notifyObservers()
		
	def setSpeed(self, value: float):
		# Sets the current speed of the train in m/s.
		try:
			self.speed = float(value)
			print(f"Actual Speed Sent to Train Model")
			self._notifyObservers()
		except ValueError:
			pass
	
	def setAcceleration(self, value: float):
		# Sets the current acceleration of the train in m/s².
		try:
			self.acceleration = float(value)
			self._notifyObservers()
		except ValueError:
			pass
	
	def setPassengerCount(self, value: int):
		# Sets the passenger count and ensures it is non-negative.
		try:
			self.passengerCount = max(0, int(value))
			print(f"Train Occupancy Sent to Track Model")
			self._notifyObservers()
		except ValueError:
			pass
	
	def setCrewCount(self, value: int):
		# Sets the crew count and ensures it is non-negative.
		try:
			self.crewCount = max(0, int(value))
			self._notifyObservers()
		except ValueError:
			pass
	
	def setPowerCommand(self, value: float):
		# Sets the power command and stores the previous value.
		try:
			self.lastPowerCommand = self.powerCommand
			self.powerCommand = float(value)
			self._notifyObservers()
		except ValueError:
			pass
	
	def setAuthority(self, value: float):
		# Sets the commanded authority and activates train if first authority received.
		try:
			self.commandedAuthority = float(value)
			
			# Check if this is a state change (inactive -> active)
			wasActive = self.active
			
			if not self.authorityReceived:
				self.authorityReceived = True
				self.active = True
				#print(f"Train {self.trainId} received first authority - AUTO ACTIVATING")
				self.serviceBrakeActive = False
				self.announcement = "Traveling From Yard"
			
			# Notify observers
			self._notifyObservers()
			
			# If state changed (was inactive, now active), trigger refresh
			if not wasActive and self.active:
				print(f"Train {self.trainId} became active - should refresh selector")

		except ValueError:
			pass

	def setCommandedSpeed(self, value: float):
		# Sets the commanded speed for the train.
		try:
			self.commandedSpeed = float(value)
			self._notifyObservers()
		except ValueError:
			pass

	def setCabinTemp(self, value: float):
		# Sets the cabin temperature in fahrenheit.
		try:
			self.cabinTemp = float(value)
			self._notifyObservers()
		except ValueError:
			pass
	
	def setHeight(self, value: float):
		# Sets the train height in meters.
		try:
			self.height = float(value)
			self._notifyObservers()
		except ValueError:
			pass
	
	def setLength(self, value: float):
		# Sets the train length in meters.
		try:
			self.length = float(value)
			self._notifyObservers()
		except ValueError:
			pass
	
	def setWidth(self, value: float):
		# Sets the train width in meters.
		try:
			self.width = float(value)
			self._notifyObservers()
		except ValueError:
			pass

	def setAnnouncement(self, announcement: str):
		# Sets the current station name.
		self.announcement = str(announcement)
		self._notifyObservers()
		
	def setTimeToStation(self, minutes: int):
		# Sets the time to next station in minutes.
		try:
			self.timeToStation = max(0, int(minutes))
			self._notifyObservers()
		except ValueError:
			pass
	
	def setServiceBrake(self, value: bool):
		# Sets the service brake state.
		value = bool(value)
		if value:
			self.serviceBrakeActive = True
		else:
			self.serviceBrakeActive = False
		self._notifyObservers()

	def setDisembarking(self, value: int):
		# Sets the number of passengers currently disembarking.
		self.passengersDisembarking = int(value)
		self._notifyObservers()
	
	def setActive(self, active: bool):
		# Sets whether the train should receive physics updates.
		self.active = active

	def calculateForceSpeedAccelerationDistance(self, dt):
		# Calculates train physics based on current state and commands.
		"""
		Physics calculation point:
		Computes force, acceleration, speed, and distance based on power command,
		brake states, grade, and passenger load. Uses trapezoidal integration.
		"""
		# Constants
		EMPTY_TRAIN_MASS = 40900  
		AVG_PASSENGER_MASS = 65.77 
		SERVICE_BRAKE_DECEL = -1.2  
		EMERGENCY_BRAKE_DECEL = -2.73 
		MAX_FORCE = 25715 
		MAX_SPEED = 19.44445183333
		totalMass = EMPTY_TRAIN_MASS + (AVG_PASSENGER_MASS * (self.passengerCount + 2))
		negGradeTrue = False
		MAX_ACCEL = MAX_FORCE / totalMass
		
		# Grade Force 
		if self.grade != 0:
			fGrade = totalMass * 9.8 * (self.grade / 100)
			if self.grade < 0:
				negGradeTrue = True
			else:
				negGradeTrue = False
		else:
			fGrade = 0
		
		# State-based acceleration logic
		if self.emergencyBrakeActive:
			aNew = EMERGENCY_BRAKE_DECEL
			
		elif self.serviceBrakeActive:
			if self.speed > 0:
				aNew = SERVICE_BRAKE_DECEL
			else:
				aNew = 0
				
		elif not self.serviceBrakeActive:
			if not self.atStation and self.powerCommand > 0:
				if self.speed == 0:
					aNew = MAX_ACCEL
				else:
					if self.speed > 1:
						force = self.powerCommand / self.speed
						if negGradeTrue:
							fNet = force + fGrade  
							aNew = fNet / totalMass
						else:
							fNet = force - fGrade  
							aNew = fNet / totalMass
					else:
						aNew = self.acceleration
			else:
				aNew = 0
				
		else:
			aNew = self.acceleration
		
		# Trapezoidal integration for speed
		if hasattr(self, 'accelerationPrev'):
			avgAcceleration = (aNew + self.accelerationPrev) / 2
		else:
			avgAcceleration = aNew

		newSpeed = self.speed + (avgAcceleration * dt)
		
		if newSpeed < 0:
			newSpeed = 0
			aNew = 0
		
		if self.speedLimit != 0 and self.commandedAuthority != 4:
			if newSpeed > self.speedLimitMps:
				newSpeed = self.speedLimitMps
				aNew = 0

		if newSpeed > MAX_SPEED:
			newSpeed = MAX_SPEED
			aNew = 0

		if aNew > MAX_ACCEL:
			aNew = MAX_ACCEL

		# Calculate distance with final speed values
		if hasattr(self, 'speedPrev'):
			avgSpeed = (newSpeed + self.speedPrev) / 2
		else:
			avgSpeed = newSpeed

		distance = avgSpeed * dt
		
		# Update state
		self.accelerationPrev = aNew
		self.speedPrev = self.speed
		self.speed = newSpeed
		self.acceleration = aNew
		if self.distanceLeft != None:
			self.distanceLeft = self.distanceLeft - distance
			if newSpeed > 0.1: #may need to fix depending on how the train stops at a station
				timeSeconds = self.distanceLeft / newSpeed
				timeMinutes = max(0, int(timeSeconds / 60))
				self.setTimeToStation(timeMinutes)
			else:
				if self.distanceLeft <= 0:
					self.setTimeToStation(0)
					self.distanceLeft = 0

		self._notifyObservers()
	
	# Door controls
	def setRightDoor(self, isOpen: bool):
		# Sets the right door state.
		self.rightDoorOpen = bool(isOpen)
		self._notifyObservers()
	
	def setLeftDoor(self, isOpen: bool):
		# Sets the left door state.
		self.leftDoorOpen = bool(isOpen)
		self._notifyObservers()
	
	# Light controls
	def setHeadlights(self, isOn: bool):
		# Sets the headlight state.
		self.headlightsOn = bool(isOn)
		self._notifyObservers()
	
	def setInteriorLights(self, isOn: bool):
		# Sets the interior light state.
		self.interiorLightsOn = bool(isOn)
		self._notifyObservers()
	
	# Failure modes
	def setEngineFailure(self, active: bool):
		# Sets the engine failure state.
		self.engineFailure = bool(active)
		self._notifyObservers()
	
	def setSignalPickupFailure(self, active: bool):
		# Sets the signal pickup failure state.
		self.signalPickupFailure = bool(active)
		self._notifyObservers()
	
	def setBrakeFailure(self, active: bool):
		# Sets the brake failure state.
		self.brakeFailure = bool(active)
		self._notifyObservers()
	
	def setEmergencyBrake(self, active: bool):
		# Sets the emergency brake state.
		self.emergencyBrakeActive = bool(active)
		self._notifyObservers()
	
	def setDeployed(self, deployed: bool):
		# Sets whether the train is deployed.
		self.deployed = bool(deployed)
		self._notifyObservers()
	
	def getStateDict(self) -> dict:
		# Returns a dictionary containing the complete state of the train.
		return {
			'train_id': self.trainId,
			'speed': self.speed,
			'acceleration': self.acceleration,
			'passenger_count': self.passengerCount,
			'passengers_disembarking': self.passengersDisembarking,
			'crew_count': self.crewCount,
			'power_command': self.powerCommand,
			'cabin_temp': self.cabinTemp,
			'grade': self.grade,
			'elevation': self.elevation,
			'speed_limit': self.speedLimit,
			'commanded_speed': self.commandedSpeed,
			'commanded_authority': self.commandedAuthority,
			'distance_left': self.distanceLeft,
			'height': self.height,
			'length': self.length,
			'width': self.width,
			'right_door_open': self.rightDoorOpen,
			'left_door_open': self.leftDoorOpen,
			'headlights_on': self.headlightsOn,
			'interior_lights_on': self.interiorLightsOn,
			'engine_failure': self.engineFailure,
			'signal_pickup_failure': self.signalPickupFailure,
			'brake_failure': self.brakeFailure,
			'emergency_brake_active': self.emergencyBrakeActive,
			'service_brake_active': self.serviceBrakeActive,
			'deployed': self.deployed,
			'line': self.line,
			'block': self.block,
			'previous_block': self.previousBlock,
			'station': self.station,
			'time_to_station': self.timeToStation,
			'emergency_announcement': self.emergencyAnnouncement,
			'authority_received': self.authorityReceived,
			'last_power_command': self.lastPowerCommand,
			'last_service_brake': self.lastServiceBrake,
			'last_emergency_brake': self.lastEmergencyBrake
		}


class TrainManager:
	# Manages all trains in the system.
	"""
	Attributes:
	trains: A dictionary mapping train IDs to Train objects.
	selectedTrainId: An integer representing the currently selected train ID.
	"""
	
	def __init__(self, numTrains: int = 14):
		# Initializes the train manager with the specified number of trains.
		self.trains = {i + 1: Train(i + 1) for i in range(numTrains)}
		self.selectedTrainId = 1
	
	def getTrain(self, trainId: int) -> Train:
		# Returns a specific train by ID.
		return self.trains.get(trainId)
	
	def getSelectedTrain(self) -> Train:
		# Returns the currently selected train.
		return self.trains.get(self.selectedTrainId)
	
	def selectTrain(self, trainId: int) -> Train:
		# Selects a train by ID and returns it.
		if trainId in self.trains:
			self.selectedTrainId = trainId
			return self.trains[trainId]
		return None
	
	def getAllTrains(self) -> dict:
		# Returns a dictionary of all trains.
		return self.trains
	
	def getDeployedTrains(self) -> list:
		# Returns a list of currently deployed trains.
		return [train for train in self.trains.values() if train.deployed]
	
	def updateAllPhysics(self, dt: float = 0.1):
		# Updates physics for all deployed trains.
		for train in self.getDeployedTrains():
			train.calculateForceSpeedAccelerationDistance(dt)

	
# Global singleton instance
_trainManager = None

def getTrainManager() -> TrainManager:
	# Returns the global TrainManager instance.
	global _trainManager
	if _trainManager is None:
		_trainManager = TrainManager()
	return _trainManager