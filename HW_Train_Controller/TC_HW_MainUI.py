#!/usr/bin/env python3
"""
Train Control System for Windows - Remote GPIO Control

This version runs on WINDOWS and connects to the Raspberry Pi GPIO Server remotely.
The Pi runs TC_GPIO_Server.py which handles all the actual GPIO hardware.

Connection Architecture:
    Windows (This File)  ←→  Raspberry Pi (TC_GPIO_Server.py)
          ↕
    Train Model (Windows)
"""

import json
import socket
import threading
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TC_HW_AirConditioning_UI import ACSystemPanel
from TC_HW_Announcement_UI import StationAnnouncementPanel
from TC_HW_TrackInfo_UI import TrackInformationPanel
from TC_HW_PowerEngineer_UI import PowerEngineerPanel
from TC_HW_SystemLogUI import SystemLogViewer
from TrainSocketServer import TrainSocketServer

# CONFIGURATION - SET YOUR PI'S IP ADDRESS HERE
PI_HOST = '172.20.10.4'  # ← CHANGE THIS to your Pi's IP address
PI_GPIO_PORT = 12348

def load_socket_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("modules", {})
    return {}

# Global state variables (mirrored from Pi)
selectedLine = None  # Will be set by line selection dialog: 'GREEN' or 'RED'
beacon1 = False  # RED LINE: Switch at block 27 (to blocks 76-72)
beacon2 = False  # RED LINE: Switch at block 38 (to blocks 71-67)
leftDoorOpen = False
rightDoorOpen = False
headlightsOn = False
interiorLightsOn = False
serviceBrakeActive = True  # Train starts with brakes engaged for safety
trainHornActive = False
emergencyBrakeEngaged = False
drivetrainManualMode = False
speedUpPressed = False
speedDownPressed = False
speedConfirmPressed = False
commandedSpeed = 0  # Internal commanded speed (authority-adjusted)
displayCommandedSpeed = 0  # Raw commanded speed for display (not authority-adjusted)
commandedAuthority = 0
currentSpeed = 0
manualSetpointSpeed = 0
previousCommandedSpeed = 0.0  # Track previous commanded speed for detecting reductions
passengerEmergencySignal = False
brakeFailure = False
engineFailure = False
signalFailure = False
mult_value = 1.0  # MULT value from CTC (default 1.0x speed until CTC connects)

running = True
acPanel = None
announcementPanel = None
trackInfoPanel = None
powerEngineerPanel = None
systemLogViewer = None
speedDisplay = None  # Main UI instance for GPIO access
returningToYard = False  # Flag to indicate train is returning to yard

# PI Controller state
integralError = 0.0
prevError = 0.0  # Previous error for trapezoidal integration
lastUpdateTime = None
sampleTime = 0.1  # 100ms update rate
lastSentPower = None  # Track last power sent to avoid duplicates

# PRELOADED TRACK INFORMATION
# Complete route starting from block 63 (YARD):
# 63→150 (forward), then 28→1 (backward through F to A), then 13→62 (forward through D back to yard)
# This creates a continuous loop through the entire Green Line
# YARD (block 63) is only visited on initialization, then the train enters the main loop at GLENBURY
preloadedTrackInformation = {
    'segments': [
        # INITIALIZATION SEGMENT (YARD to first loop station)
        {
            'from_station': 'YARD',
            'to_station': 'GLENBURY',
            'distance': 200.0 + 100.0,  # meters + half of block 65 (200m block)
            'from_block': 63,
            'to_block': 65,
            'station_block_half_length': 100.0
        },
        # MAIN LOOP BEGINS HERE - will restart at index 1 after completion
        {
            'from_station': 'GLENBURY',
            'to_station': 'DORMONT',
            'distance': 100.0 + 200.0 + 100.0 + 100.0 + 100.0 + 100.0 + 100.0 + 50.0,  # blocks 65, 66, 67, 68, 69, 70, 71, 72, 73
            'from_block': 65,
            'to_block': 73,
            'station_block_half_length': 50.0
        },
        {
            'from_station': 'DORMONT',
            'to_station': 'MT LEBANON',
            'distance': 400.0 + 150.0,  # meters + half of block 77 (300m block)
            'from_block': 73,
            'to_block': 77,
            'station_block_half_length': 150.0
        },
        {
            'from_station': 'MT LEBANON',
            'to_station': 'POPLAR',
            'distance': 2886.6 + 50.0,  # meters + half of block 88 (100m block)
            'from_block': 77,
            'to_block': 88,
            'station_block_half_length': 50.0
        },
        {
            'from_station': 'POPLAR',
            'to_station': 'CASTLE SHANNON',
            'distance': 625.0 + 37.5,  # meters + half of block 96 (75m block)
            'from_block': 88,
            'to_block': 96,
            'station_block_half_length': 37.5
        },
        {
            'from_station': 'CASTLE SHANNON',
            'to_station': 'DORMONT',
            'distance': 690.0 + 50.0,  # meters + half of block 105 (100m block)
            'from_block': 96,
            'to_block': 105,
            'station_block_half_length': 50.0
        },
        {
            'from_station': 'DORMONT',
            'to_station': 'GLENBURY',
            'distance': 890.0 + 81.0,  # meters + half of block 114 (162m block)
            'from_block': 105,
            'to_block': 114,
            'station_block_half_length': 81.0
        },
        {
            'from_station': 'GLENBURY',
            'to_station': 'OVERBROOK',
            'distance': 652.0 + 25.0,  # meters + half of block 123 (50m block)
            'from_block': 114,
            'to_block': 123,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'OVERBROOK',
            'to_station': 'INGLEWOOD',
            'distance': 450.0 + 25.0,  # meters + half of block 132 (50m block)
            'from_block': 123,
            'to_block': 132,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'INGLEWOOD',
            'to_station': 'CENTRAL',
            'distance': 450.0 + 25.0,  # meters + half of block 141 (50m block)
            'from_block': 132,
            'to_block': 141,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'CENTRAL',
            'to_station': 'WHITED',
            'distance': 1609.0 + 150.0,  # meters + half of block 22 (300m block)
            'from_block': 141,
            'to_block': 22,
            'station_block_half_length': 150.0
        },
        {
            'from_station': 'WHITED',
            'to_station': 'LLC PLAZA',
            'distance': 1200.0 + 75.0,  # meters + half of block 16 (150m block)
            'from_block': 22,
            'to_block': 16,
            'station_block_half_length': 75.0
        },
        {
            'from_station': 'LLC PLAZA',
            'to_station': 'EDGEBROOK',
            'distance': 900.0 + 50.0,  # meters + half of block 9 (100m block)
            'from_block': 16,
            'to_block': 9,
            'station_block_half_length': 50.0
        },
        {
            'from_station': 'EDGEBROOK',
            'to_station': 'PIONEER',
            'distance': 700.0 + 50.0,  # meters + half of block 2 (100m block)
            'from_block': 9,
            'to_block': 2,
            'station_block_half_length': 50.0
        },
        {
            'from_station': 'PIONEER',
            'to_station': 'LLC PLAZA',
            'distance': 650.0 + 75.0,  # meters + half of block 16 (150m block)
            'from_block': 2,
            'to_block': 16,
            'station_block_half_length': 75.0
        },
        {
            'from_station': 'LLC PLAZA',
            'to_station': 'WHITED',
            'distance': 1050.0 + 150.0,  # meters + half of block 22 (300m block)
            'from_block': 16,
            'to_block': 22,
            'station_block_half_length': 150.0
        },
        {
            'from_station': 'WHITED',
            'to_station': 'SOUTH BANK',
            'distance': 1400.0 + 25.0,  # meters + half of block 31 (50m block)
            'from_block': 22,
            'to_block': 31,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'SOUTH BANK',
            'to_station': 'CENTRAL',
            'distance': 400.0 + 25.0,  # meters + half of block 39 (50m block)
            'from_block': 31,
            'to_block': 39,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'CENTRAL',
            'to_station': 'INGLEWOOD',
            'distance': 450.0 + 25.0,  # meters + half of block 48 (50m block)
            'from_block': 39,
            'to_block': 48,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'INGLEWOOD',
            'to_station': 'OVERBROOK',
            'distance': 450.0 + 25.0,  # meters + half of block 57 (50m block)
            'from_block': 48,
            'to_block': 57,
            'station_block_half_length': 25.0
        },
        {
            'from_station': 'OVERBROOK',
            'to_station': 'GLENBURY',
            'distance': 500.0 + 100.0,  # meters + half of block 65 (200m block)
            'from_block': 57,
            'to_block': 65,
            'station_block_half_length': 100.0
        }
        # MAIN LOOP ENDS HERE - restarts at segment index 1 (GLENBURY → DORMONT)
    ]
}

# RED LINE PRELOADED TRACK INFORMATION
# Route: YARD (Block 8) → SHADYSIDE (7) → HERRON AVE (16) [initialization]
# Main Loop: HERRON AVE (16) → SWISSVILLE → ... → SHADYSIDE (7) → HERRON AVE (16)
# YARD (block 8) is only visited on initialization, then the train enters the main loop at HERRON AVE
redLineTrackInformation = {
    'segments': [
        # INITIALIZATION SEGMENTS (YARD to first loop station)
        # YARD to SHADYSIDE (Block 8 backwards to Block 7)
        {
            'from_station': 'YARD',
            'to_station': 'SHADYSIDE',
            'distance': 37.5,
            'from_block': 8,
            'to_block': 7,
            'station_block_half_length': 37.5
        },
        # SHADYSIDE to HERRON AVE (Block 7 backwards through blocks 6,5,4,3,2,1, then jump to 15, then to 16)
        {
            'from_station': 'SHADYSIDE',
            'to_station': 'HERRON AVE',
            'distance': 37.5 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 60.0 + 25.0,  # blocks 7,6,5,4,3,2,1, jump to 15, then 16
            'from_block': 7,
            'to_block': 16,
            'station_block_half_length': 25.0
        },
        # MAIN LOOP BEGINS HERE - will restart at index 2 after completion
        # HERRON AVE to SWISSVILLE (Block 16 forward to Block 21)
        {
            'from_station': 'HERRON AVE',
            'to_station': 'SWISSVILLE',
            'distance': 25.0 + 200.0 + 400.0 + 400.0 + 200.0 + 50.0,  # blocks 16, 17, 18, 19, 20, 21
            'from_block': 16,
            'to_block': 21,
            'station_block_half_length': 50.0
        },
        # SWISSVILLE to PENN STATION (Block 21 forward to Block 25 - underground)
        {
            'from_station': 'SWISSVILLE',
            'to_station': 'PENN STATION',
            'distance': 325.0,
            'from_block': 21,
            'to_block': 25,
            'station_block_half_length': 25.0
        },
        # PENN STATION to STEEL PLAZA (Block 25 forward to Block 35 - underground)
        {
            'from_station': 'PENN STATION',
            'to_station': 'STEEL PLAZA',
            'distance': 520.0,
            'from_block': 25,
            'to_block': 35,
            'station_block_half_length': 25.0
        },
        # STEEL PLAZA to FIRST AVE (Block 35 forward to Block 45 - underground)
        {
            'from_station': 'STEEL PLAZA',
            'to_station': 'FIRST AVE',
            'distance': 520.0,
            'from_block': 35,
            'to_block': 45,
            'station_block_half_length': 25.0
        },
        # FIRST AVE to STATION SQUARE (Block 45 forward to Block 48 - underground then surface)
        {
            'from_station': 'FIRST AVE',
            'to_station': 'STATION SQUARE',
            'distance': 212.5,
            'from_block': 45,
            'to_block': 48,
            'station_block_half_length': 37.5
        },
        # STATION SQUARE to SOUTH HILLS JUNCTION (Block 48 forward to Block 60)
        {
            'from_station': 'STATION SQUARE',
            'to_station': 'SOUTH HILLS JUNCTION',
            'distance': 743.2,
            'from_block': 48,
            'to_block': 60,
            'station_block_half_length': 37.5
        },
        # SOUTH HILLS JUNCTION back to block 15 (Block 60 forward to 66, then jump to 52 and backwards to 15)
        {
            'from_station': 'SOUTH HILLS JUNCTION',
            'to_station': 'HERRON AVE',
            'distance': 37.5 + 75.0 + 75.0 + 75.0 + 75.0 + 75.0 + 75.0 + 43.2 + 50.0 + 50.0 + 50.0 + 50.0 + 75.0 + 75.0 + 75.0 + 75.0 + 75.0 + 75.0 + 50.0 + 60.0 + 60.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 200.0 + 50.0 + 60.0 + 25.0,  # 60→66, jump to 52, then 52→15, then to 16
            'from_block': 60,
            'to_block': 16,
            'station_block_half_length': 25.0
        },
        # HERRON AVE to SHADYSIDE via YARD (Block 16→15→1, then 1→2→3→4→5→6→7(SHADYSIDE)→8→9(YARD)→10→11→12→13→14→15→16)
        # This is the return route that passes through the YARD (blocks 8-9)
        # SHADYSIDE station is at block 7, but train continues through to complete the route
        {
            'from_station': 'HERRON AVE',
            'to_station': 'SHADYSIDE',
            'distance': 25.0 + 60.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 50.0 + 37.5,  # blocks 16→15→1→2→3→4→5→6→7 (arrive at SHADYSIDE)
            'from_block': 16,
            'to_block': 7,
            'station_block_half_length': 37.5
        },
        # SHADYSIDE continuing past yard back to HERRON AVE (7→8→9→10→11→12→13→14→15→16)
        # Train passes through blocks 8-9 (YARD) with authority=1 check at block 9
        {
            'from_station': 'SHADYSIDE',
            'to_station': 'HERRON AVE',
            'distance': 37.5 + 75.0 + 75.0 + 75.0 + 75.0 + 75.0 + 70.0 + 60.0 + 60.0 + 25.0,  # blocks 7→8→9→10→11→12→13→14→15→16
            'from_block': 7,
            'to_block': 16,
            'station_block_half_length': 25.0
        }
        # MAIN LOOP ENDS HERE - restarts at segment index 2 (HERRON AVE → SWISSVILLE)
    ]
}

# Automatic mode position tracking variables
autoModeEnabled = True  # Set to True to enable automatic mode station stopping
currentSegmentIndex = 0  # Which segment we're currently traveling through
distanceTraveledInSegment = 0.0  # How far we've traveled in current segment (meters)
distanceToNextStation = preloadedTrackInformation['segments'][0]['distance']  # Distance remaining to next station
lastPositionUpdateTime = None  # For calculating displacement

# Underground sections - blocks where headlights and interior lights should be ON
# GREEN LINE
greenLineUndergroundBlocks = {36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 
                      53, 54, 55, 56, 57, 122, 123, 124, 125, 126, 127, 128, 129, 130, 
                      131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 142, 143}

# RED LINE - Blocks 24-46 are underground according to the data, plus branch blocks
redLineUndergroundBlocks = {24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
                            67, 68, 69, 70, 71, 72, 73, 74, 75, 76}

# Station door side mapping - which doors open at each station
# Format: station_name: 'left', 'right', or 'both'
# GREEN LINE
greenLineStationDoorSides = {
    'PIONEER': 'left',
    'EDGEBROOK': 'left',
    'LLC PLAZA': 'both',
    'WHITED': 'both',
    'SOUTH BANK': 'left',
    'CENTRAL': 'right',
    'INGLEWOOD': 'right',  # Block 48
    'OVERBROOK': 'right',  # Block 57, 123
    'GLENBURY': 'right',   # Block 65, 114
    'DORMONT': 'right',    # Block 73, 105
    'MT LEBANON': 'both',
    'POPLAR': 'left',
    'CASTLE SHANNON': 'left'
}

# RED LINE
redLineStationDoorSides = {
    'SHADYSIDE': 'both',
    'HERRON AVE': 'both',
    'SWISSVILLE': 'both',
    'PENN STATION': 'both',
    'STEEL PLAZA': 'both',
    'FIRST AVE': 'both',
    'STATION SQUARE': 'both',
    'SOUTH HILLS JUNCTION': 'both'
}

# Will be set based on selected line
UNDERGROUND_BLOCKS = greenLineUndergroundBlocks
STATION_DOOR_SIDES = greenLineStationDoorSides

# Special case: INGLEWOOD at block 132 uses left door instead of right
STATION_DOOR_EXCEPTIONS = {
    132: 'left'  # INGLEWOOD at block 132 uses left door
}

# Current block tracking - will be set based on selected line
currentBlock = 63  # Default to Green Line yard
lastUndergroundState = False  # Track if we were underground last update

# Automatic mode control parameters
DECELERATION_DISTANCE = 200.0  # Start decelerating 200m before station (meters)
STATION_STOP_THRESHOLD = 5.0  # Consider "at station" when within 5m
STATION_DWELL_TIME = 30.0  # Time to wait at station (seconds) - will be adjusted by mult_value
stationDwellStartTime = None  # Track when we arrived at station
isAtStation = False  # Flag to track if we're stopped at a station

# Position tracking counter for debug output
_position_print_counter = 0
_diagnostic_counter = 0
_holding_print_counter = 0
_decel_print_counter = 0

class GPIOClient:
    """Client that connects to Raspberry Pi GPIO Server"""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = True
        self.buffer = ""
        self.state_update_callback = None
    
    def connect(self):
        """Connect to GPIO server on Pi"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ Connected to GPIO Server at {self.host}:{self.port}")
            
            # Start receive thread
            receive_thread = threading.Thread(target=self.receiveLoop, daemon=True)
            receive_thread.start()
            
            return True
        
        except Exception as e:
            print(f"✗ GPIO Server connection failed: {e}")
            self.connected = False
            return False
    
    def receiveLoop(self):
        """Receive messages from GPIO server"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("GPIO Server disconnected")
                    self.connected = False
                    break
                
                self.buffer += data
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    if line:
                        self.processMessage(line)
            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"GPIO receive error: {e}")
                self.connected = False
                break
    
    def processMessage(self, message_str):
        """Process message from GPIO server"""
        try:
            message = json.loads(message_str)
            msg_type = message.get('type')
            
            if msg_type == 'state_update':
                if self.state_update_callback:
                    self.state_update_callback(message.get('data', {}))
        
        except json.JSONDecodeError:
            print(f"Invalid JSON from GPIO server: {message_str}")
    
    def setLED(self, led_name, state):
        """Send command to set LED state on Pi"""
        if not self.connected:
            return False
        
        command = {
            'type': 'set_led',
            'led': led_name,
            'state': state
        }
        
        try:
            self.socket.sendall((json.dumps(command) + '\n').encode('utf-8'))
            return True
        except:
            self.connected = False
            return False
    
    def setHeadlights(self, state):
        """Control headlights (for underground sections)"""
        if not self.connected:
            return False
        
        command = {
            'type': 'set_headlights',
            'state': state
        }
        
        try:
            self.socket.sendall((json.dumps(command) + '\n').encode('utf-8'))
            return True
        except:
            self.connected = False
            return False
    
    def setInteriorLights(self, state):
        """Control interior lights (for underground sections)"""
        if not self.connected:
            return False
        
        command = {
            'type': 'set_interior_lights',
            'state': state
        }
        
        try:
            self.socket.sendall((json.dumps(command) + '\n').encode('utf-8'))
            return True
        except:
            self.connected = False
            return False
    
    def setEmergencyBrake(self, state):
        """Control emergency brake (for failure modes)"""
        if not self.connected:
            return False
        
        command = {
            'type': 'set_emergency_brake',
            'state': state
        }
        
        try:
            self.socket.sendall((json.dumps(command) + '\n').encode('utf-8'))
            return True
        except:
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from GPIO server"""
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

# Helper functions
def getCurrentSpeed():
    """Get current speed in MPH (converted from m/s for display)"""
    MS_TO_MPH = 2.23694  # 1 m/s = 2.23694 mph
    return currentSpeed * MS_TO_MPH

def getCommandedSpeed():
    """Return the display commanded speed (raw from track, not authority-adjusted)"""
    return displayCommandedSpeed 

def getCommandedAuthority():
    return commandedAuthority

def getManualSetpointSpeed():
    return manualSetpointSpeed

def getDrivetrainMode():
    return "MANUAL" if drivetrainManualMode else "AUTOMATIC"

def isManualMode():
    return drivetrainManualMode

def getDistanceToNextStation():
    """Get distance to next station in meters"""
    return distanceToNextStation

def getNextStationName():
    """Get the name of the next station"""
    # If returning to yard, always show YARD
    if returningToYard:
        return "YARD"
    
    # Check if we're on RED LINE at a switch point with beacon active OR in alternative route blocks
    if selectedLine == 'RED':
        # Beacon1 alternative route blocks: 27 (switch), 76, 75, 74, 73, 72 (NOT 32 - that's back on main)
        if beacon1 and currentBlock in [27, 76, 75, 74, 73, 72]:
            print(f"[BEACON DEBUG] ✓ ALTERNATIVE ROUTE 1: Block={currentBlock}, Beacon1={beacon1}")
            return "ALTERNATIVE ROUTE (Blocks 76-72)"
        
        # Beacon2 alternative route blocks: 38 (switch), 71, 70, 69, 68, 67 (NOT 39 - that's back on main)
        if beacon2 and currentBlock in [38, 71, 70, 69, 68, 67]:
            print(f"[BEACON DEBUG] ✓ ALTERNATIVE ROUTE 2: Block={currentBlock}, Beacon2={beacon2}")
            return "ALTERNATIVE ROUTE (Blocks 71-67)"
        
        # Debug when at beacon blocks but beacon not active
        if currentBlock == 27:
            print(f"[BEACON DEBUG] At Block 27 but Beacon1={beacon1}")
        elif currentBlock == 38:
            print(f"[BEACON DEBUG] At Block 38 but Beacon2={beacon2}")
    
    if currentSegmentIndex < len(preloadedTrackInformation['segments']):
        return preloadedTrackInformation['segments'][currentSegmentIndex]['to_station']
    # Return appropriate looping station based on selected line
    # Both lines loop back to their first station
    if selectedLine == 'RED':
        return "SHADYSIDE"  # Red Line loops: YARD → SHADYSIDE
    else:
        return "GLENBURY"  # Green Line loops: YARD → GLENBURY

def shouldStartDecelerating():
    """Check if train should start decelerating for station approach"""
    return distanceToNextStation <= DECELERATION_DISTANCE and not isAtStation

def updatePositionTracking():
    """
    Update position tracking for automatic mode based on current velocity and time.
    Uses continuous integration: displacement = velocity × time
    Also controls headlights and interior lights based on underground sections.
    """
    global distanceTraveledInSegment, distanceToNextStation, lastPositionUpdateTime
    global currentSegmentIndex, isAtStation, stationDwellStartTime, systemLogViewer
    global _position_print_counter
    global currentBlock, lastUndergroundState
    global serviceBrakeActive, returningToYard, commandedSpeed
    
    if not autoModeEnabled:
        return
    
    # Calculate current block based on segment and distance traveled
    def getCurrentBlockNumber():
        """Determine current block based on position in route"""
        global beacon1, beacon2
        
        if selectedLine == 'GREEN':
            # GREEN LINE Route order: 63→150 (forward), jump to 28, 28→1 (backward), jump to 13, 13→63 (forward loop back to yard)
            route_order = list(range(63, 151)) + list(range(28, 0, -1)) + list(range(13, 64))
        else:  # RED LINE
            # RED LINE Route - Complex with switches
            # Main route: 8→7→...→1 → jump to 16 → 17...→66 → jump to 52 → 51...→16 → jump to 1 → ...→8 (loop)
            # This is handled segment by segment since switches can redirect
            
            if currentSegmentIndex >= len(preloadedTrackInformation['segments']):
                return 8  # Default to Red Line yard
            
            segment = preloadedTrackInformation['segments'][currentSegmentIndex]
            from_block = segment['from_block']
            to_block = segment['to_block']
            
            # Calculate progress through segment (0.0 to 1.0)
            total_distance = segment['distance']
            progress = min(1.0, distanceTraveledInSegment / total_distance) if total_distance > 0 else 0.0
            
            # Determine route for this specific segment
            if from_block == 8 and to_block == 7:
                # YARD to SHADYSIDE
                return 8 if progress < 0.5 else 7
            elif from_block == 7 and to_block == 16:
                # Two segments have this pattern:
                # - Index 1 (initialization): 7→6→5→4→3→2→1→15→16
                # - Index 10 (return with yard): 7→8→9→10→11→12→13→14→15→16
                print(f"[ROUTE DEBUG] from_block=7, to_block=16, currentSegmentIndex={currentSegmentIndex}")
                if currentSegmentIndex == 1:
                    # SHADYSIDE to HERRON AVE - Initialization (7→6→5→4→3→2→1→15→16)
                    blocks = [7, 6, 5, 4, 3, 2, 1, 15, 16]
                    print(f"[ROUTE DEBUG] Using INITIALIZATION route: 7→6→5→4→3→2→1→15→16")
                else:
                    # SHADYSIDE to HERRON AVE - Return through YARD (7→8→9→10→11→12→13→14→15→16)
                    blocks = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
                    print(f"[ROUTE DEBUG] Using RETURN route: 7→8→9→10→11→12→13→14→15→16")
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            elif from_block == 16 and to_block == 21:
                # HERRON AVE to SWISSVILLE (16→17→18→19→20→21)
                blocks = [16, 17, 18, 19, 20, 21]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            elif from_block == 21 and to_block == 25:
                # SWISSVILLE to PENN STATION (21→22→23→24→25)
                blocks = [21, 22, 23, 24, 25]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            elif from_block == 25 and to_block == 35:
                # PENN STATION to STEEL PLAZA (25→26→27→28→29→30→31→32→33→34→35)
                
                # If beacon1 active and we're IN alternative route blocks
                if beacon1 and currentBlock in [76, 75, 74, 73, 72]:
                    alt_blocks = [76, 75, 74, 73, 72]
                    current_idx = alt_blocks.index(currentBlock)
                    
                    # If at the END of alternative route (block 72), rejoin main at block 32
                    if currentBlock == 72:
                        print("[ALT ROUTE 1] Completed alternative route, rejoining main at block 32")
                        return 32
                    
                    # Otherwise continue through alternative blocks
                    next_idx = current_idx + 1
                    next_block = alt_blocks[next_idx]
                    print(f"[ALT ROUTE 1] Continuing: {currentBlock} → {next_block}")
                    return next_block
                
                blocks = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                current = blocks[idx]
                
                # Check for switch at block 27
                if current == 27 and beacon1:
                    # Switch activated! Redirect to branch 76→72
                    print("[SWITCH] Beacon 1 detected at block 27 - taking branch to blocks 76-72")
                    return 76  # Enter branch
                    
                return current
            
            elif from_block == 35 and to_block == 45:
                # STEEL PLAZA to FIRST AVE (35→36→37→38→39→40→41→42→43→44→45)
                
                # If beacon2 active and we're IN alternative route blocks
                if beacon2 and currentBlock in [71, 70, 69, 68, 67]:
                    alt_blocks = [71, 70, 69, 68, 67]
                    current_idx = alt_blocks.index(currentBlock)
                    
                    # If at the END of alternative route (block 67), rejoin main at block 38
                    if currentBlock == 67:
                        print("[ALT ROUTE 2] Completed alternative route, rejoining main at block 38")
                        return 38
                    
                    # Otherwise continue through alternative blocks
                    next_idx = current_idx + 1
                    next_block = alt_blocks[next_idx]
                    print(f"[ALT ROUTE 2] Continuing: {currentBlock} → {next_block}")
                    return next_block
                
                blocks = [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                current = blocks[idx]
                
                # Check for switch at block 38
                if current == 38 and beacon2:
                    # Switch activated! Redirect to branch 71→67
                    print("[SWITCH] Beacon 2 detected at block 38 - taking branch to blocks 71-67")
                    return 71  # Enter branch
                    
                return current
            elif from_block == 45 and to_block == 48:
                # FIRST AVE to STATION SQUARE (45→46→47→48)
                blocks = [45, 46, 47, 48]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            elif from_block == 48 and to_block == 60:
                # STATION SQUARE to SOUTH HILLS JUNCTION (48→49→50→51→52→53→54→55→56→57→58→59→60)
                blocks = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            elif from_block == 60 and to_block == 16:
                # SOUTH HILLS JUNCTION back to HERRON AVE (complex return path)
                # 60→61→62→63→64→65→66→52→51→...→15→16
                blocks = [60, 61, 62, 63, 64, 65, 66, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 15, 16]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            elif from_block == 16 and to_block == 7:
                # HERRON AVE to SHADYSIDE (16→15→1→2→3→4→5→6→7)
                # This is the return route coming back to SHADYSIDE
                blocks = [16, 15, 1, 2, 3, 4, 5, 6, 7]
                idx = min(int(progress * len(blocks)), len(blocks) - 1)
                return blocks[idx]
            else:
                return from_block  # Fallback
        
        # GREEN LINE logic
        if currentSegmentIndex >= len(preloadedTrackInformation['segments']):
            return 63  # Default to start
        
        segment = preloadedTrackInformation['segments'][currentSegmentIndex]
        from_block = segment['from_block']
        to_block = segment['to_block']
        
        # Calculate progress through segment (0.0 to 1.0)
        total_distance = segment['distance']
        progress = min(1.0, distanceTraveledInSegment / total_distance) if total_distance > 0 else 0.0
        
        # Handle segments with jumps explicitly
        if from_block == 2 and to_block == 16:
            # PIONEER to LLC PLAZA: 2→1→13→14→15→16
            blocks = [2, 1, 13, 14, 15, 16]
            idx = min(int(progress * len(blocks)), len(blocks) - 1)
            return blocks[idx]
        elif from_block == 16 and to_block == 22:
            # LLC PLAZA to WHITED: 16→17→18→19→20→21→22
            blocks = [16, 17, 18, 19, 20, 21, 22]
            idx = min(int(progress * len(blocks)), len(blocks) - 1)
            return blocks[idx]
        elif from_block == 22 and to_block == 31:
            # WHITED to SOUTH BANK: 22→23→24→25→26→27→28→29→30→31
            # This crosses the junction where route_order goes 28→1→13→29
            blocks = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
            idx = min(int(progress * len(blocks)), len(blocks) - 1)
            return blocks[idx]
        elif from_block == 57 and to_block == 65:
            # OVERBROOK to GLENBURY (completes the loop): 57→58→59→60→61→62→63→64→65
            # This segment includes block 58 where yard return can be triggered
            blocks = [57, 58, 59, 60, 61, 62, 63, 64, 65]
            idx = min(int(progress * len(blocks)), len(blocks) - 1)
            return blocks[idx]
        
        # For all other segments, use route_order calculation
        try:
            from_idx = route_order.index(from_block)
            to_idx = route_order.index(to_block)
            
            # Determine current block index
            if to_idx > from_idx:
                # Forward path
                blocks_in_segment = to_idx - from_idx
                block_offset = int(progress * blocks_in_segment)
                current_idx = from_idx + block_offset
            else:
                # Wrapping path - this shouldn't happen now that we handle jumps explicitly
                total_blocks = (len(route_order) - from_idx) + to_idx
                block_offset = int(progress * total_blocks)
                current_idx = (from_idx + block_offset) % len(route_order)
            
            return route_order[current_idx]
        except (ValueError, IndexError):
            return from_block  # Fallback
    
    # Update current block
    if not hasattr(updatePositionTracking, 'prevBlock'):
        updatePositionTracking.prevBlock = currentBlock
    
    prevBlock = updatePositionTracking.prevBlock
    currentBlock = getCurrentBlockNumber()
    
    # Debug: Print block changes
    if currentBlock != prevBlock:
        print(f"[BLOCK CHANGE] Block {prevBlock} → {currentBlock}")
        updatePositionTracking.prevBlock = currentBlock
        
        # YARD RETURN LOGIC - Check for special blocks with authority 1
        if commandedAuthority == 1:
            # RED LINE: Return to yard if entering block 9 with authority 1
            if selectedLine == 'RED' and currentBlock == 9:
                returningToYard = True
                commandedSpeed = 0.0  # Stop the train completely
                
                print(f"⚠️  RED LINE: Authority 1 detected at block 9 - RETURNING TO YARD")
                print(f"🛑 STOPPING ALL MOVEMENT - Service brake ENGAGED")
                
                # Engage service brake to stop the train
                serviceBrakeActive = True
                
                # Send service brake command to Train Model
                if 'speedDisplay' in globals():
                    sd = globals()['speedDisplay']
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Service Brake',
                            'value': True,
                            'train_id': 1
                        })
                        print(f"[YARD RETURN] Service brake command sent to Train Model")
                        
                        # Send announcement for yard return
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Announcement',
                            'value': "Returning to yard. All movement terminated.",
                            'train_id': 1
                        })
                        print(f"📢 Announcement: Returning to yard")
                
                # Log to system log
                yard_msg = "RED LINE: Train returning to yard from block 9 (Authority 1)"
                if systemLogViewer:
                    systemLogViewer.handleLogMessage(yard_msg, 'system')
            
            # GREEN LINE: Return to yard if entering block 58 with authority 1
            elif selectedLine == 'GREEN' and currentBlock == 58:
                returningToYard = True
                commandedSpeed = 0.0  # Stop the train completely
                
                print(f"⚠️  GREEN LINE: Authority 1 detected at block 58 - RETURNING TO YARD")
                print(f"🛑 STOPPING ALL MOVEMENT - Service brake ENGAGED")
                
                # Engage service brake to stop the train
                serviceBrakeActive = True
                
                # Send service brake command to Train Model
                if 'speedDisplay' in globals():
                    sd = globals()['speedDisplay']
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Service Brake',
                            'value': True,
                            'train_id': 1
                        })
                        print(f"[YARD RETURN] Service brake command sent to Train Model")
                        
                        # Send announcement for yard return
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Announcement',
                            'value': "Returning to yard. All movement terminated.",
                            'train_id': 1
                        })
                        print(f"📢 Announcement: Returning to yard")
                
                # Log to system log
                yard_msg = "GREEN LINE: Train returning to yard from block 58 (Authority 1)"
                if systemLogViewer:
                    systemLogViewer.handleLogMessage(yard_msg, 'system')
    
    # Check underground status and control lights
    isUnderground = currentBlock in UNDERGROUND_BLOCKS
    
    # Inform driver of underground status on block changes
    if currentBlock != prevBlock and (isUnderground or prevBlock in UNDERGROUND_BLOCKS):
        if isUnderground:
            print(f"📍 Inside underground tunnel (Block {currentBlock})")
        else:
            print(f"📍 Exiting underground tunnel - returning to surface (Block {currentBlock})")
    
    # Only send commands when state changes
    if isUnderground != lastUndergroundState:
        # Access gpio_client through the global speedDisplay instance
        print(f"[LIGHT DEBUG] Underground state changed: {lastUndergroundState} → {isUnderground}")
        try:
            print(f"[LIGHT DEBUG] Checking speedDisplay in globals: {'speedDisplay' in globals()}")
            if 'speedDisplay' in globals():
                sd = globals()['speedDisplay']
                print(f"[LIGHT DEBUG] speedDisplay found: {sd is not None}")
                print(f"[LIGHT DEBUG] Has gpio_client: {hasattr(sd, 'gpio_client')}")
                if hasattr(sd, 'gpio_client'):
                    print(f"[LIGHT DEBUG] gpio_client exists: {sd.gpio_client is not None}")
                    print(f"[LIGHT DEBUG] gpio_client connected: {sd.gpio_client.connected if sd.gpio_client else False}")
                
                if hasattr(sd, 'gpio_client') and sd.gpio_client and sd.gpio_client.connected:
                    if isUnderground:
                        sd.gpio_client.setHeadlights(True)
                        sd.gpio_client.setInteriorLights(True)
                        print(f"💡 Headlights & cabin lights turned ON for tunnel safety")
                        
                        # Send to Train Model
                        if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Headlights',
                                'value': True,
                                'train_id': 1
                            })
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Cabin Lights',
                                'value': True,
                                'train_id': 1
                            })
                    else:
                        sd.gpio_client.setHeadlights(False)
                        sd.gpio_client.setInteriorLights(False)
                        print(f"💡 Headlights & cabin lights turned OFF")
                        
                        # Send to Train Model
                        if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Headlights',
                                'value': False,
                                'train_id': 1
                            })
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Cabin Lights',
                                'value': False,
                                'train_id': 1
                            })
                else:
                    print(f"[LIGHT DEBUG] GPIO client not ready!")
        except Exception as e:
            print(f"⚠️  Warning: Unable to control lights - {e}")
            import traceback
            traceback.print_exc()
        
        lastUndergroundState = isUnderground
    
    currentTime = time.time()
    
    # If returning to yard, don't update position - train is stopped
    if returningToYard:
        return
    
    # Initialize timing on first call
    if lastPositionUpdateTime is None:
        lastPositionUpdateTime = currentTime
        print(f"Position tracking initialized")
        print(f"Starting segment: {preloadedTrackInformation['segments'][0]['from_station']} → {preloadedTrackInformation['segments'][0]['to_station']}")
        print(f"Initial distance to station: {distanceToNextStation:.1f}m")
        return
    
    # Calculate time elapsed since last update
    dt = currentTime - lastPositionUpdateTime
    lastPositionUpdateTime = currentTime
    
    # TIME ACCELERATION: Use time scale from CTC (mult_value)
    global mult_value
    dt = dt * mult_value
    
    # If we're at a station, don't update position
    if isAtStation:
        # Check if dwell time is complete
        if stationDwellStartTime is not None:
            dwellElapsed = currentTime - stationDwellStartTime
            if dwellElapsed >= STATION_DWELL_TIME:
                # Don't release brake if returning to yard
                if returningToYard:
                    print(f"[YARD RETURN] Keeping service brake engaged - train at yard")
                    return
                
                # RELEASE SERVICE BRAKE before departing
                serviceBrakeActive = False
                print(f"🟢 Service brake RELEASED for departure")
                
                # Send service brake command to Train Model
                if 'speedDisplay' in globals():
                    sd = globals()['speedDisplay']
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Service Brake',
                            'value': False,
                            'train_id': 1
                        })
                        print(f"[AUTO BRAKE] Service brake release sent to Train Model")
                
                # Close doors before departing
                if 'speedDisplay' in globals():
                    sd = globals()['speedDisplay']
                    if hasattr(sd, 'gpio_client') and sd.gpio_client and sd.gpio_client.connected:
                        # Close both doors via GPIO server
                        sd.gpio_client.setLED('left_door', False)
                        sd.gpio_client.setLED('right_door', False)
                        print(f"🚪 Doors closing")
                        
                        # Send door commands to Train Model
                        if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Left Door Signal',
                                'value': False,
                                'train_id': 1
                            })
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Right Door Signal',
                                'value': False,
                                'train_id': 1
                            })
                
                # Move to next segment
                departure_msg = f"Departing {preloadedTrackInformation['segments'][currentSegmentIndex]['to_station']}"
                print(departure_msg)
                
                # Send to System Log UI
                if systemLogViewer:
                    systemLogViewer.handleLogMessage(departure_msg, 'system')
                
                currentSegmentIndex += 1
                
                # Check if we've reached the end
                if currentSegmentIndex >= len(preloadedTrackInformation['segments']):
                    # Both lines loop - restart at the main loop beginning (after YARD initialization)
                    if selectedLine == 'RED':
                        loop_msg = "Completed Red Line loop - Continuing to SWISSVILLE"
                        currentSegmentIndex = 2  # Restart at HERRON AVE → SWISSVILLE (main loop start)
                    else:
                        loop_msg = "Completed Green Line loop - Continuing to DORMONT"
                        currentSegmentIndex = 1  # Restart at GLENBURY → DORMONT (main loop start)
                    
                    print(loop_msg)
                    
                    # Send to System Log UI
                    if systemLogViewer:
                        systemLogViewer.handleLogMessage(loop_msg, 'system')
                    
                    # Reset for next segment
                    distanceTraveledInSegment = 0.0
                    distanceToNextStation = preloadedTrackInformation['segments'][currentSegmentIndex]['distance']
                    isAtStation = False
                    stationDwellStartTime = None
                    
                    # Send announcement for next station
                    next_station = preloadedTrackInformation['segments'][currentSegmentIndex]['to_station']
                    if 'speedDisplay' in globals():
                        sd = globals()['speedDisplay']
                        if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                            announcement_text = f"Travelling to {next_station}"
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Announcement',
                                'value': announcement_text,
                                'train_id': 1
                            })
                            print(f"📢 Announcement: {announcement_text}")
                    return
                
                # Send departure announcement to Train Model (port 12345)
                next_station = preloadedTrackInformation['segments'][currentSegmentIndex]['to_station']
                if 'speedDisplay' in globals():
                    sd = globals()['speedDisplay']
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        announcement_text = f"Travelling to {next_station}"
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Announcement',
                            'value': announcement_text,
                            'train_id': 1
                        })
                        print(f"📢 Announcement: {announcement_text}")
                
                # Reset for next segment
                distanceTraveledInSegment = 0.0
                distanceToNextStation = preloadedTrackInformation['segments'][currentSegmentIndex]['distance']
                isAtStation = False
                stationDwellStartTime = None
        return
    
    # Calculate displacement: distance = velocity × time
    # currentSpeed is in m/s, dt is in seconds
    displacement = currentSpeed * dt
    
    # Update position tracking
    distanceTraveledInSegment += displacement
    distanceToNextStation = preloadedTrackInformation['segments'][currentSegmentIndex]['distance'] - distanceTraveledInSegment
    
    # Debug output showing position updates (reduced frequency to avoid spam)
    # Print approximately every second (every 10 updates at 100ms intervals)
    _position_print_counter += 1
    if _position_print_counter >= 10:
        _position_print_counter = 0
        # Convert meters to feet for display (1 meter = 3.28084 feet)
        distanceTraveledFeet = distanceTraveledInSegment * 3.28084
        distanceToNextStationFeet = distanceToNextStation * 3.28084
        print(f"Speed: {currentSpeed:.2f} m/s, Traveled: {distanceTraveledFeet:.1f}ft, Remaining: {distanceToNextStationFeet:.1f}ft to {preloadedTrackInformation['segments'][currentSegmentIndex]['to_station']}")
    
    # Check if we've reached the station
    if distanceToNextStation <= STATION_STOP_THRESHOLD:
        isAtStation = True
        stationDwellStartTime = currentTime
        distanceToNextStation = 0.0
        currentStation = preloadedTrackInformation['segments'][currentSegmentIndex]['to_station']
        
        arrival_msg = f"*** ARRIVED AT {currentStation} ***"
        print(arrival_msg)
        
        # Send arrival announcement to Train Model (port 12345)
        if 'speedDisplay' in globals():
            sd = globals()['speedDisplay']
            if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                announcement_text = f"Arrived at {currentStation}"
                sd.server.send_to_ui("Train Model", {
                    'command': 'Announcement',
                    'value': announcement_text,
                    'train_id': 1
                })
                print(f"📢 Announcement: {announcement_text}")
        
        # ENGAGE SERVICE BRAKE at station
        serviceBrakeActive = True
        print(f"🛑 Service brake ENGAGED at {currentStation}")
        
        # Send service brake command to Train Model
        if 'speedDisplay' in globals():
            sd = globals()['speedDisplay']
            if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                sd.server.send_to_ui("Train Model", {
                    'command': 'Service Brake',
                    'value': True,
                    'train_id': 1
                })
                print(f"[AUTO BRAKE] Service brake command sent to Train Model")
        
        # Control door LEDs based on station platform side
        print(f"[DOOR DEBUG] At station {currentStation}, checking door control")
        print(f"[DOOR DEBUG] speedDisplay in globals: {'speedDisplay' in globals()}")
        if 'speedDisplay' in globals():
            sd = globals()['speedDisplay']
            print(f"[DOOR DEBUG] speedDisplay found: {sd is not None}")
            print(f"[DOOR DEBUG] Has gpio_client: {hasattr(sd, 'gpio_client')}")
            if hasattr(sd, 'gpio_client'):
                print(f"[DOOR DEBUG] gpio_client connected: {sd.gpio_client.connected if sd.gpio_client else False}")
            
            if hasattr(sd, 'gpio_client') and sd.gpio_client and sd.gpio_client.connected:
                # Check for block-specific exceptions first
                door_side = STATION_DOOR_EXCEPTIONS.get(currentBlock)
                if not door_side:
                    # Use station default
                    door_side = STATION_DOOR_SIDES.get(currentStation, 'both')
                
                print(f"[DOOR DEBUG] Door side for {currentStation} at block {currentBlock}: {door_side}")
                
                # Turn on appropriate door LEDs by sending commands directly to GPIO server
                if door_side == 'left' or door_side == 'both':
                    result = sd.gpio_client.setLED('left_door', True)
                    print(f"[DOOR DEBUG] Left door command sent, result: {result}")
                    print(f"🚪 Left door opening")
                    
                    # Send to Train Model
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Left Door Signal',
                            'value': True,
                            'train_id': 1
                        })
                
                if door_side == 'right' or door_side == 'both':
                    result = sd.gpio_client.setLED('right_door', True)
                    print(f"[DOOR DEBUG] Right door command sent, result: {result}")
                    print(f"🚪 Right door opening")
                    
                    # Send to Train Model
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Right Door Signal',
                            'value': True,
                            'train_id': 1
                        })
            else:
                print(f"[DOOR DEBUG] GPIO client not ready!")
        
        # Send to System Log UI
        if systemLogViewer:
            systemLogViewer.handleLogMessage(arrival_msg, 'system')

def calculatePowerCommand():
    """
    Calculate power command using PI controller.
    Uses Kp and Ki from PowerEngineer panel.
    
    In AUTOMATIC mode, handles station approach and stopping:
    - Decelerates as train approaches station
    - Stops at station
    - Maintains stop during dwell time
    - Uses service brake when commanded speed is reduced to slow down safely
    
    Commanded speed is in MPH, current speed is in m/s.
    
    Returns:
        Power in kW (kilowatts)
    """
    global integralError, lastUpdateTime, powerEngineerPanel, prevError
    global _diagnostic_counter, _holding_print_counter, _decel_print_counter
    global previousCommandedSpeed, serviceBrakeActive, returningToYard
    
    if not powerEngineerPanel:
        return 0.0
    
    # Conversion constants
    MPH_TO_MS = 0.44704  # 1 mph = 0.44704 m/s
    MS_TO_MPH = 2.23694  # 1 m/s = 2.23694 mph
    
    # Update position tracking for automatic mode
    updatePositionTracking()
    
    # Diagnostic output (first 5 calls only to avoid spam)
    if _diagnostic_counter < 5:
        _diagnostic_counter += 1
        print(f"[DIAGNOSTIC {_diagnostic_counter}] commandedSpeed: {commandedSpeed} MPH, currentSpeed: {currentSpeed} m/s, drivetrainManualMode: {drivetrainManualMode}, autoModeEnabled: {autoModeEnabled}")
    
    # Get commanded speed
    if drivetrainManualMode:
        # In manual mode, use manual setpoint speed (in MPH, convert to m/s)
        commandedSpeedMPH = manualSetpointSpeed
        
        # MANUAL MODE SPEED LIMIT ENFORCEMENT
        # Unless authority is 4, manual speed cannot exceed the track speed limit
        if commandedAuthority != 4:
            # displayCommandedSpeed is the raw track speed limit (authority-unadjusted)
            # Limit manual setpoint to not exceed track speed limit
            if commandedSpeedMPH > displayCommandedSpeed:
                commandedSpeedMPH = displayCommandedSpeed
                print(f"[MANUAL MODE] Speed limited to track limit: {displayCommandedSpeed:.1f} MPH (Authority={commandedAuthority})")
        
        commandedSpeedMS = commandedSpeedMPH * MPH_TO_MS
    else:
        # In automatic mode, use commanded speed from track (already in MPH, convert to m/s)
        commandedSpeedMPH = commandedSpeed
        commandedSpeedMS = commandedSpeedMPH * MPH_TO_MS
        
        # AUTOMATIC MODE STATION LOGIC
        if autoModeEnabled and not emergencyBrakeEngaged:
            if isAtStation:
                # Force stop at station
                commandedSpeedMS = 0.0
                commandedSpeedMPH = 0.0
                # Print holding message occasionally (not every 100ms)
                _holding_print_counter += 1
                if _holding_print_counter >= 20:
                    _holding_print_counter = 0
                    print(f"Holding at station: {getNextStationName()}")
            elif shouldStartDecelerating():
                # Calculate deceleration profile for smooth stop
                # Use simple linear deceleration based on distance remaining
                distToStation = getDistanceToNextStation()
                
                # Target deceleration: v² = v₀² + 2a·d
                # Solving for target velocity to reach 0 at station
                # v = sqrt(2 * decel * distance)
                DECEL_RATE = 1.0  # m/s² - comfortable deceleration
                
                if distToStation > 0:
                    targetSpeed = (2 * DECEL_RATE * distToStation) ** 0.5
                    # Limit to current commanded speed (don't accelerate)
                    commandedSpeedMS = min(commandedSpeedMS, targetSpeed)
                    commandedSpeedMPH = commandedSpeedMS * MS_TO_MPH
                    
                    # Print deceleration status (reduced frequency)
                    _decel_print_counter += 1
                    if _decel_print_counter >= 5:
                        _decel_print_counter = 0
                        print(f"Decelerating for {getNextStationName()}: {distToStation:.1f}m, target {commandedSpeedMPH:.1f} MPH")
                else:
                    commandedSpeedMS = 0.0
                    commandedSpeedMPH = 0.0
    
    # Get current actual speed (in m/s from Train Model)
    currentSpeedMS = currentSpeed
    currentSpeedMPH = currentSpeedMS * MS_TO_MPH  # Convert for display only
    
    # SPEED REDUCTION DETECTION - Use service brake to slow down
    # Service brake deceleration is approximately -2.67 m/s²
    # Only apply if commanded speed dropped significantly and we're going faster than commanded
    SPEED_REDUCTION_THRESHOLD = 5.0  # MPH - significant speed reduction
    SERVICE_BRAKE_DURATION = 0.5  # seconds to apply brake
    
    if not hasattr(calculatePowerCommand, '_speed_reduction_brake_time'):
        calculatePowerCommand._speed_reduction_brake_time = 0.0
        calculatePowerCommand._last_check_time = time.time()
    
    current_time = time.time()
    dt_check = current_time - calculatePowerCommand._last_check_time
    calculatePowerCommand._last_check_time = current_time
    
    # Detect commanded speed reduction (not at station, not in manual mode)
    if not drivetrainManualMode and not isAtStation and not emergencyBrakeEngaged:
        speedReduction = previousCommandedSpeed - commandedSpeedMPH
        
        if speedReduction > SPEED_REDUCTION_THRESHOLD and currentSpeedMPH > commandedSpeedMPH + 3.0:
            # Significant speed reduction detected and we're going too fast
            # Apply service brake briefly to slow down
            if calculatePowerCommand._speed_reduction_brake_time <= 0:
                # Start brake application
                calculatePowerCommand._speed_reduction_brake_time = SERVICE_BRAKE_DURATION
                print(f"⚠️  Speed reduced from {previousCommandedSpeed:.1f} to {commandedSpeedMPH:.1f} MPH - applying service brake to slow down")
                
                # Apply service brake via GPIO
                if 'speedDisplay' in globals():
                    sd = globals()['speedDisplay']
                    if hasattr(sd, 'gpio_client') and sd.gpio_client and sd.gpio_client.connected:
                        sd.gpio_client.setServiceBrake(True)
                        serviceBrakeActive = True
                        
                        # Send to Train Model
                        if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                            sd.server.send_to_ui("Train Model", {
                                'command': 'Service Brake',
                                'value': True,
                                'train_id': 1
                            })
    
    # Count down brake time and release when done
    if calculatePowerCommand._speed_reduction_brake_time > 0:
        calculatePowerCommand._speed_reduction_brake_time -= dt_check
        
        if calculatePowerCommand._speed_reduction_brake_time <= 0:
            # Don't release brake if returning to yard
            if returningToYard:
                calculatePowerCommand._speed_reduction_brake_time = 0.0
                print(f"[YARD RETURN] Keeping service brake engaged - train at yard")
                return 0.0
            
            # Release service brake
            calculatePowerCommand._speed_reduction_brake_time = 0.0
            
            if 'speedDisplay' in globals():
                sd = globals()['speedDisplay']
                if hasattr(sd, 'gpio_client') and sd.gpio_client and sd.gpio_client.connected:
                    sd.gpio_client.setServiceBrake(False)
                    serviceBrakeActive = False
                    print(f"🟢 Service brake released - now controlling to {commandedSpeedMPH:.1f} MPH with power")
                    
                    # Send to Train Model
                    if hasattr(sd, 'server') and sd.server and sd.train_model_connected:
                        sd.server.send_to_ui("Train Model", {
                            'command': 'Service Brake',
                            'value': False,
                            'train_id': 1
                        })
    
    # DEBUG: Print speeds every 20 calls
    if not hasattr(calculatePowerCommand, '_speed_debug_counter'):
        calculatePowerCommand._speed_debug_counter = 0
    calculatePowerCommand._speed_debug_counter += 1
    if calculatePowerCommand._speed_debug_counter % 20 == 0:
        print(f"[SPEED DEBUG] Commanded={commandedSpeedMPH:.1f} MPH ({commandedSpeedMS:.2f}m/s), Current={currentSpeedMPH:.1f} MPH ({currentSpeedMS:.2f}m/s), Error={commandedSpeedMS - currentSpeedMS:.2f}m/s")
    
    # SERVICE BRAKE CONTROL:
    # Service brake controlled by:
    # 1. GPIO hardware button (manual control)
    # 2. Automatic station stops
    # 3. Speed reduction detection (above)
    # The PI controller controls speed through POWER COMMANDS
    
    # Calculate velocity error in METRIC (m/s)
    velocityError = commandedSpeedMS - currentSpeedMS
    
    # Get PI gains from PowerEngineer panel
    kp = powerEngineerPanel.hw_kp.get()
    ki = powerEngineerPanel.hw_ki.get()
    maxPower = powerEngineerPanel.maxPower.get()
    
    # TRAPEZOIDAL INTEGRATION (per control law document)
    # u_k = u_{k-1} + (T/2)(e_k + e_{k-1})
    # where u_k is the integral term
    
    # Calculate power WITHOUT integral term first (for anti-windup check)
    pTerm = kp * velocityError
    powerWithoutIntegral = pTerm
    
    # ANTI-WINDUP: Only update integral if P^cmd < P^max
    if powerWithoutIntegral < maxPower:
        # Update integral using trapezoidal rule
        # u_k = u_{k-1} + (T/2)(e_k + e_{k-1})
        integralError += (sampleTime / 2.0) * (velocityError + prevError)
    # else: at power limit - don't integrate (anti-windup)
    
    # Store current error for next iteration
    prevError = velocityError
    
    # Calculate PI control output
    # P^cmd = Kp * e_k + Ki * u_k
    iTerm = ki * integralError
    power = pTerm + iTerm
    
    # Limit power to max and ensure non-negative
    power = max(0.0, min(maxPower, power))
    
    # Update PowerEngineer panel displays (convert to MPH for display)
    powerEngineerPanel.setCurrentSpeed(currentSpeedMPH)
    powerEngineerPanel.setCommandedSpeed(commandedSpeedMPH)
    powerEngineerPanel.speedError.set(velocityError * MS_TO_MPH)  # Convert error to MPH for display
    powerEngineerPanel.integralError.set(integralError)
    powerEngineerPanel.powerOutput.set(power)
    
    return power

def cleanupAll():
    global acPanel, announcementPanel, trackInfoPanel, powerEngineerPanel, systemLogViewer
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
    try:
        if powerEngineerPanel and powerEngineerPanel.root.winfo_exists():
            powerEngineerPanel.root.destroy()
    except:
        pass
    try:
        if systemLogViewer and systemLogViewer.root.winfo_exists():
            systemLogViewer.root.destroy()
    except:
        pass

def selectTrainLine():
    """
    Display a dialog for the user to select which train line to operate.
    Returns 'GREEN' or 'RED' based on user selection.
    """
    global selectedLine, preloadedTrackInformation, UNDERGROUND_BLOCKS, STATION_DOOR_SIDES, currentBlock, distanceToNextStation
    
    selection_made = [False]  # Use list to allow modification in nested function
    
    def select_line(line):
        global selectedLine, preloadedTrackInformation, UNDERGROUND_BLOCKS, STATION_DOOR_SIDES, currentBlock, distanceToNextStation
        selectedLine = line
        
        if line == 'GREEN':
            # preloadedTrackInformation is already set to Green Line by default
            UNDERGROUND_BLOCKS = greenLineUndergroundBlocks
            STATION_DOOR_SIDES = greenLineStationDoorSides
            currentBlock = 63  # Green Line yard
            print(f"\n[LINE SELECTION] GREEN LINE Selected")
            print(f"[INIT] Underground lighting system loaded: {len(UNDERGROUND_BLOCKS)} underground blocks")
            print(f"[INIT] Station door system loaded: {len(STATION_DOOR_SIDES)} stations configured")
            print(f"[INIT] Complete route: 22 station stops including 2 visits to LLC PLAZA")
            print(f"[INIT] Starting at block {currentBlock} (Underground: {currentBlock in UNDERGROUND_BLOCKS})")
        else:  # RED
            preloadedTrackInformation = redLineTrackInformation
            UNDERGROUND_BLOCKS = redLineUndergroundBlocks
            STATION_DOOR_SIDES = redLineStationDoorSides
            currentBlock = 8  # Red Line yard
            print(f"\n[LINE SELECTION] RED LINE Selected")
            print(f"[INIT] RED LINE - Underground lighting system loaded: {len(UNDERGROUND_BLOCKS)} underground blocks")
            print(f"[INIT] RED LINE - Station door system loaded: {len(STATION_DOOR_SIDES)} stations configured")
            print(f"[INIT] RED LINE - Complete route with switch logic for beacons")
            print(f"[INIT] Starting at block {currentBlock} (Underground: {currentBlock in UNDERGROUND_BLOCKS})")
        
        distanceToNextStation = preloadedTrackInformation['segments'][0]['distance']
        selection_made[0] = True
        dialog.destroy()
    
    # Create selection dialog
    dialog = tk.Tk()
    dialog.title("Train Line Selection")
    dialog.geometry("400x250")
    dialog.configure(bg='#1e3c72')
    dialog.resizable(False, False)
    
    # Center the window
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    # Title
    title_label = tk.Label(
        dialog,
        text="SELECT TRAIN LINE",
        font=('Arial', 20, 'bold'),
        bg='#1e3c72',
        fg='white',
        pady=20
    )
    title_label.pack()
    
    # Button frame
    button_frame = tk.Frame(dialog, bg='#1e3c72')
    button_frame.pack(expand=True)
    
    # Green Line button
    green_button = tk.Button(
        button_frame,
        text="GREEN LINE\nHW",
        font=('Arial', 15, 'bold'),
        bg='#27ae60',
        fg='white',
        activebackground='#229954',
        activeforeground='white',
        width=12,
        height=2,
        command=lambda: select_line('GREEN')
    )
    green_button.pack(side='left', padx=10)
    
    # Red Line button
    red_button = tk.Button(
        button_frame,
        text="RED LINE\nHW",
        font=('Arial', 15, 'bold'),
        bg='#e74c3c',
        fg='white',
        activebackground='#c0392b',
        activeforeground='white',
        width=12,
        height=2,
        command=lambda: select_line('RED')
    )
    red_button.pack(side='left', padx=10)
    
    # Prevent closing without selection
    def on_closing():
        if not selection_made[0]:
            print("\n[ERROR] Line selection is required to proceed!")
            return
        dialog.destroy()
    
    dialog.protocol("WM_DELETE_WINDOW", on_closing)
    dialog.mainloop()
    
    if not selection_made[0]:
        print("\n[ERROR] No line selected. Exiting...")
        import sys
        sys.exit(1)
    
    return selectedLine

def main():
    global powerEngineerPanel, speedDisplay
    
    print("=" * 60)
    print("Train Control System - Windows Hardware Controller")
    print("=" * 60)
    
    # First, let user select which line to operate
    selectTrainLine()
    
    print(f"Connecting to GPIO Server at {PI_HOST}:{PI_GPIO_PORT}")
    print("=" * 60)
    
    root = tk.Tk()
    speedDisplay = TrainSpeedDisplayUI(root)
    
    # Create PowerEngineer panel with send callback (will be set up after speedDisplay is created)
    powerEngineerRoot = tk.Toplevel(root)
    
    # Define callback for sending PID to software TC
    def send_pid_callback(kp, ki):
        if hasattr(speedDisplay, '_sendPIDToSoftwareTC'):
            speedDisplay._sendPIDToSoftwareTC(kp, ki)
    
    powerEngineerPanel = PowerEngineerPanel(powerEngineerRoot, send_callback=send_pid_callback)
    # Set PI controller gains for hardware train control
    powerEngineerPanel.hw_kp.set(15.0)
    powerEngineerPanel.hw_ki.set(3.0)
    # Update UI displays to show the new values
    powerEngineerPanel.updateDisplays()
    # Show panel on startup instead of hiding it
    print("✓ Power Engineer Panel initialized (Kp=15.0, Ki=3.0, MaxPower=120kW)")
    
    root.mainloop()

class TrainSpeedDisplayUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("TRAIN HARDWARE CONTROL SYSTEM")
        self.root.geometry("1000x750")
        self.root.configure(bg='#1e3c72')
        
        # GPIO Client Setup
        self.gpio_client = GPIOClient(PI_HOST, PI_GPIO_PORT)
        self.gpio_client.state_update_callback = self._onGPIOStateUpdate
        
        # Try to connect to GPIO server
        def connect_gpio():
            if self.gpio_client.connect():
                self.root.after(0, lambda: self._updateConnectionStatus(True))
            else:
                self.root.after(0, lambda: self._updateConnectionStatus(False))
        
        gpio_thread = threading.Thread(target=connect_gpio, daemon=True)
        gpio_thread.start()
        
        # Socket Server Setup for Train Model
        module_config = load_socket_config()
        train_controller_hw_config = module_config.get("Train HW", {"port": 12347})
        
        # Start our server that listens for incoming connections (Train Model, Train SW, CTC)
        self.server = TrainSocketServer(port=train_controller_hw_config["port"], ui_id="Train HW")
        self.server.set_allowed_connections(["Train Model", "Train SW", "CTC"])
        self.server.start_server(self._process_message)
        print(f"✓ Train Controller HW server started on port {train_controller_hw_config['port']}")
        print(f"✓ Waiting for connections from: Train Model, Train SW, CTC")
        
        # Connect to Train Model (it should already be running on port 12345)
        self.train_model_connected = False
        self.software_tc_connected = False
        self.ctc_connected = False
        train_model_config = module_config.get("Train Model", {"port": 12345})
        
        def connect_train_model():
            try:
                time.sleep(1)  # Give it a moment
                self.server.connect_to_ui('localhost', train_model_config["port"], "Train Model")
                print(f"✓ Connected to Train Model")
                self.train_model_connected = True
                
                # Send initial service brake state to release train
                time.sleep(0.5)
                print(f"\n[INIT] Sending Service Brake: {serviceBrakeActive} to Train Model")
                self.server.send_to_ui("Train Model", {
                    'command': 'Service Brake',
                    'value': serviceBrakeActive,
                    'train_id': 1
                })
                print(f"[INIT] Service brake command sent\n")
                
            except Exception as e:
                print(f"Note: Train Model not yet running - {e}")
                self.train_model_connected = False
        
        # Try to connect in background
        train_model_thread = threading.Thread(target=connect_train_model, daemon=True)
        train_model_thread.start()
        
        # Also try to connect to Software TC (Train SW) if it's running
        self._connectToSoftwareTC()
        
        # CTC should connect TO us on our server port (12347)
        # We don't connect to CTC - we wait for CTC to connect to us

        self._createWidgets()
        self._updateDisplay()
        self._startPowerCalculationLoop()
        
        self.root.protocol("WM_DELETE_WINDOW", self._onClose)
    
    def _onGPIOStateUpdate(self, state):
        """Handle state update from GPIO server"""
        global leftDoorOpen, rightDoorOpen, headlightsOn, interiorLightsOn
        global serviceBrakeActive, trainHornActive, emergencyBrakeEngaged
        global drivetrainManualMode, manualSetpointSpeed
        global speedUpPressed, speedDownPressed, speedConfirmPressed
        
        # Track previous values to detect changes
        prev_emergency = emergencyBrakeEngaged
        prev_service = serviceBrakeActive
        prev_manual_mode = drivetrainManualMode
        prev_manual_speed = manualSetpointSpeed
        prev_left_door = leftDoorOpen
        prev_right_door = rightDoorOpen
        prev_headlights = headlightsOn
        prev_interior_lights = interiorLightsOn
        prev_train_horn = trainHornActive
        
        # Update local state
        leftDoorOpen = state.get('leftDoorOpen', False)
        rightDoorOpen = state.get('rightDoorOpen', False)
        headlightsOn = state.get('headlightsOn', False)
        interiorLightsOn = state.get('interiorLightsOn', False)
        serviceBrakeActive = state.get('serviceBrakeActive', False)
        trainHornActive = state.get('trainHornActive', False)
        emergencyBrakeEngaged = state.get('emergencyBrakeEngaged', False)
        drivetrainManualMode = state.get('drivetrainManualMode', False)
        manualSetpointSpeed = state.get('manualSetpointSpeed', 0)
        speedUpPressed = state.get('speedUpPressed', False)
        speedDownPressed = state.get('speedDownPressed', False)
        speedConfirmPressed = state.get('speedConfirmPressed', False)
        
        # Send relevant updates to Train Model ONLY when they change
        if self.server and self.train_model_connected:
            try:
                # Send manual setpoint speed when in manual mode and it changed
                if drivetrainManualMode and (manualSetpointSpeed != prev_manual_speed or drivetrainManualMode != prev_manual_mode):
                    self.server.send_to_ui("Train Model", {
                        'command': 'Manual Setpoint Speed',
                        'value': manualSetpointSpeed,
                        'train_id': 1
                    })
                
                # Send emergency brake state changes
                if emergencyBrakeEngaged != prev_emergency:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Emergency Brake',
                        'value': emergencyBrakeEngaged,
                        'train_id': 1
                    })
                
                # Send service brake state changes
                if serviceBrakeActive != prev_service:
                    print(f"\n[GPIO BRAKE CHANGE] Service Brake: {prev_service} → {serviceBrakeActive}")
                    self.server.send_to_ui("Train Model", {
                        'command': 'Service Brake',
                        'value': serviceBrakeActive,
                        'train_id': 1
                    })
                    print(f"[GPIO BRAKE SENT] Command sent to Train Model\n")
                
                # Send left door state changes
                if leftDoorOpen != prev_left_door:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Left Door Signal',
                        'value': leftDoorOpen,
                        'train_id': 1
                    })
                
                # Send right door state changes
                if rightDoorOpen != prev_right_door:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Right Door Signal',
                        'value': rightDoorOpen,
                        'train_id': 1
                    })
                
                # Send headlights state changes
                if headlightsOn != prev_headlights:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Headlights',
                        'value': headlightsOn,
                        'train_id': 1
                    })
                
                # Send interior lights state changes
                if interiorLightsOn != prev_interior_lights:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Cabin Lights',
                        'value': interiorLightsOn,
                        'train_id': 1
                    })
                
                # Send train horn state changes
                if trainHornActive != prev_train_horn:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Train Horn',
                        'value': trainHornActive,
                        'train_id': 1
                    })
            except Exception as e:
                print(f"Error sending to Train Model: {e}")
                self.train_model_connected = False
    
    def _updateConnectionStatus(self, connected):
        """Update GPIO connection status"""
        if connected:
            self.connectionLabel.config(
                text=f"● Connected to GPIO Server ({PI_HOST}:{PI_GPIO_PORT})",
                bg='#27ae60'
            )
        else:
            self.connectionLabel.config(
                text="● Disconnected from GPIO Server",
                bg='#e74c3c'
            )
    
    def _process_message(self, message, source_ui_id):
        """Process incoming messages from Train Model"""
        # Declare all globals at function level
        global commandedSpeed, displayCommandedSpeed, previousCommandedSpeed, commandedAuthority
        global serviceBrakeActive, currentSpeed, passengerEmergencySignal
        global brakeFailure, engineFailure, signalFailure, acPanel
        global preloadedTrackInformation, distanceToNextStation
        global beacon1, beacon2, emergencyBrakeEngaged, returningToYard
        global mult_value
        
        try:
            command = message.get('command')
            
            # DEBUG: Print all messages to see what's being received
            print(f"[DEBUG] Received message from {source_ui_id}: command={command}, message={message}")
            
            # DEBUG: Print all beacon-related messages
            if command in ['Beacon1', 'Beacon2']:
                print(f"[DEBUG] Received {command} from {source_ui_id}: {message}")
            
            # Silently process routine messages
            
            # Track if Train Model is connected (for any message from Train Model)
            if source_ui_id == "Train Model":
                self.train_model_connected = True
            
            value = message.get('value')
            
            if command == 'Commanded Speed':
                # Commanded speed comes from Track Model in MPH (already converted)
                
                # If returning to yard, ignore commanded speed updates - keep it at 0
                if returningToYard:
                    print(f"[YARD RETURN] Ignoring Commanded Speed update (returningToYard=True)")
                    return  # Don't update commanded speed when returning to yard
                
                # Track previous commanded speed to detect reductions
                if 'previousCommandedSpeed' not in globals():
                    previousCommandedSpeed = 0.0
                
                previousCommandedSpeed = commandedSpeed
                
                # Store the raw commanded speed for display
                displayCommandedSpeed = float(value)
                
                # Apply authority-based limiting to internal commanded speed
                if commandedAuthority == 0:
                    commandedSpeed = 0.0  # Authority 0: stop
                elif commandedAuthority == 1:
                    commandedSpeed = displayCommandedSpeed * 0.5  # Authority 1: 50%
                elif commandedAuthority == 2:
                    commandedSpeed = displayCommandedSpeed * 0.75  # Authority 2: 75%
                elif commandedAuthority == 3:
                    commandedSpeed = displayCommandedSpeed  # Authority 3: 100%
                else:
                    commandedSpeed = displayCommandedSpeed  # Default: 100%
            
            elif command == 'Commanded Authority':
                # If returning to yard, ignore authority updates - keep speed at 0
                if returningToYard:
                    print(f"[YARD RETURN] Ignoring Commanded Authority update (returningToYard=True)")
                    return  # Don't update commanded speed when returning to yard
                
                prev_authority = commandedAuthority
                commandedAuthority = value
                
                # Recalculate internal commanded speed based on new authority
                if commandedAuthority == 0:
                    # Authority 0: Emergency stop
                    if not isAtStation:
                        # NOT at station - EMERGENCY STOP via service brake
                        print(f"⚠️  AUTHORITY 0 - IMMEDIATE STOP (not at station)")
                        commandedSpeed = 0.0
                        
                        # Engage service brake immediately
                        serviceBrakeActive = True
                        
                        # Send to Train Model
                        if self.server and self.train_model_connected:
                            self.server.send_to_ui("Train Model", {
                                'command': 'Service Brake',
                                'value': True,
                                'train_id': 1
                            })
                            print(f"[AUTHORITY 0] Service brake ENGAGED for emergency stop")
                    else:
                        # At station - ignore authority 0 (station logic already handles stopping)
                        print(f"[AUTHORITY 0] At station - ignoring (station logic handles stop)")
                        commandedSpeed = 0.0
                
                elif commandedAuthority == 1:
                    # Authority 1: 50% of commanded speed
                    commandedSpeed = displayCommandedSpeed * 0.5
                    print(f"[AUTHORITY 1] Speed limited to 50% → {commandedSpeed:.1f} MPH")
                
                elif commandedAuthority == 2:
                    # Authority 2: 75% of commanded speed
                    commandedSpeed = displayCommandedSpeed * 0.75
                    print(f"[AUTHORITY 2] Speed limited to 75% → {commandedSpeed:.1f} MPH")
                
                elif commandedAuthority == 3:
                    # Authority 3: 100% of commanded speed (full speed)
                    commandedSpeed = displayCommandedSpeed
                    print(f"[AUTHORITY 3] Full speed allowed → {commandedSpeed:.1f} MPH")
                
                else:
                    # Unknown authority - default to full speed
                    commandedSpeed = displayCommandedSpeed
                
                # Release service brake if transitioning from authority 0 to non-zero
                # But NOT if returning to yard
                if prev_authority == 0 and commandedAuthority > 0 and serviceBrakeActive and not isAtStation and not returningToYard:
                    print(f"🟢 AUTHORITY {commandedAuthority} - Releasing emergency stop brake")
                    
                    serviceBrakeActive = False
                    
                    # Send to Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'Service Brake',
                            'value': False,
                            'train_id': 1
                        })
                        print(f"[AUTHORITY {commandedAuthority}] Service brake released")
            
            elif command == 'Current Speed':
                # Update current speed from Train Model - critical for PI controller feedback!
                currentSpeed = float(value)
            
            elif command == 'Passenger Emergency Signal':
                passengerEmergencySignal = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('passenger_emergency', value)
                
                # Activate or deactivate emergency brake based on passenger emergency
                if value and not emergencyBrakeEngaged:
                    print("⚠️  PASSENGER EMERGENCY - Activating Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(True)
                    emergencyBrakeEngaged = True
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'on',
                            'train_id': 1
                        })
                elif not value and emergencyBrakeEngaged:
                    print("✓ PASSENGER EMERGENCY CLEARED - Releasing Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(False)
                    emergencyBrakeEngaged = False
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'off',
                            'train_id': 1
                        })
            
            elif command == 'Service Brake Failure':
                # Handle Service Brake Failure (sent from Passenger UI)
                brakeFailure = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('brake_failure', value)
                
                # Activate or deactivate emergency brake based on brake failure
                if value and not emergencyBrakeEngaged:
                    print("⚠️  BRAKE FAILURE - Activating Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(True)
                    emergencyBrakeEngaged = True
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'on',
                            'train_id': 1
                        })
                elif not value and emergencyBrakeEngaged:
                    print("✓ BRAKE FAILURE CLEARED - Releasing Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(False)
                    emergencyBrakeEngaged = False
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'off',
                            'train_id': 1
                        })
            
            elif command == 'Train Engine Failure':
                engineFailure = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('engine_failure', value)
                
                # Activate or deactivate emergency brake based on engine failure
                if value and not emergencyBrakeEngaged:
                    print("⚠️  ENGINE FAILURE - Activating Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(True)
                    emergencyBrakeEngaged = True
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'on',
                            'train_id': 1
                        })
                elif not value and emergencyBrakeEngaged:
                    print("✓ ENGINE FAILURE CLEARED - Releasing Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(False)
                    emergencyBrakeEngaged = False
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'off',
                            'train_id': 1
                        })
            
            elif command == 'Signal Pickup Failure':
                signalFailure = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('signal_failure', value)
                
                # Activate or deactivate emergency brake based on signal failure
                if value and not emergencyBrakeEngaged:
                    print("⚠️  SIGNAL PICKUP FAILURE - Activating Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(True)
                    emergencyBrakeEngaged = True
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'on',
                            'train_id': 1
                        })
                elif not value and emergencyBrakeEngaged:
                    print("✓ SIGNAL PICKUP FAILURE CLEARED - Releasing Emergency Brake")
                    if self.gpio_client and self.gpio_client.connected:
                        self.gpio_client.setEmergencyBrake(False)
                    emergencyBrakeEngaged = False
                    
                    # Notify Train Model
                    if self.server and self.train_model_connected:
                        self.server.send_to_ui("Train Model", {
                            'command': 'emergency_brake',
                            'value': 'off',
                            'train_id': 1
                        })
            
            elif command == 'Temp':
                # Update AC panel with current temperature from Train Model
                if acPanel is not None:
                    try:
                        acPanel.setCurrentTemperature(float(value))
                    except:
                        pass  # AC panel may not be open yet
            
            elif command == 'Beacon Data':
                # Receive beacon data from Train Model/Passenger UI
                received_beacon = value
                
                if received_beacon and 'segments' in received_beacon:
                    preloadedTrackInformation = received_beacon
                    # Reset distance to first segment
                    distanceToNextStation = preloadedTrackInformation['segments'][0]['distance']
                    
                    print("[BEACON DATA] Received station information:")
                    for segment in preloadedTrackInformation['segments']:
                        print(f"  - {segment['from_station']} → {segment['to_station']}: {segment['distance']}m")
                    print("[BEACON DATA] Automatic mode station stopping enabled")
            
            elif command == 'Beacon1':
                # RED LINE: Switch at block 27 (to blocks 76-72)
                global beacon1
                beacon1 = bool(value)
                print(f"[BEACON1] Received: {beacon1} (Switch at block 27)")
                print(f"[BEACON1] Current state: selectedLine={selectedLine}, currentBlock={currentBlock}, beacon1={beacon1}")
                if selectedLine == 'RED' and currentBlock == 27:
                    print(f"[BEACON1] ✓ Conditions met for alternative route display!")
            
            elif command == 'Beacon2':
                # RED LINE: Switch at block 38 (to blocks 71-67)
                global beacon2
                beacon2 = bool(value)
                print(f"[BEACON2] Received: {beacon2} (Switch at block 38)")
                print(f"[BEACON2] Current state: selectedLine={selectedLine}, currentBlock={currentBlock}, beacon2={beacon2}")
                if selectedLine == 'RED' and currentBlock == 38:
                    print(f"[BEACON2] ✓ Conditions met for alternative route display!")
            
            elif command == 'MULT':
                # MULT command from CTC - updates time scale
                global mult_value, STATION_DWELL_TIME
                mult_value = float(value)
                
                # Recalculate STATION_DWELL_TIME to maintain 30 real-world seconds
                # At 1.0x: 30 seconds simulation time = 30 seconds real time
                # At 10.0x: 3 seconds simulation time = 30 seconds real time
                STATION_DWELL_TIME = 30.0 / mult_value
                
                print(f"[CTC] Received MULT command from {source_ui_id}: value={mult_value}")
                print(f"[CTC] Updated STATION_DWELL_TIME to {STATION_DWELL_TIME:.1f} seconds (30s real-world time)")

        
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _createWidgets(self):
        # Header
        headerFrame = tk.Frame(self.root, bg='#0f1e3d')
        headerFrame.pack(fill='x')
        
        headerLabel = tk.Label(
            headerFrame,
            text="TRAIN HARDWARE CONTROL SYSTEM",
            font=('Arial', 24, 'bold'),
            bg='#0f1e3d',
            fg='white',
            pady=12
        )
        headerLabel.pack()
        
        # Connection status
        self.connectionLabel = tk.Label(
            headerFrame,
            text="Connecting to GPIO Server...",
            font=('Arial', 11),
            bg='#e67e22',
            fg='white',
            pady=5
        )
        self.connectionLabel.pack(fill='x')
        
        # Main content frame
        mainFrame = tk.Frame(self.root, bg='#1e3c72')
        mainFrame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Top row: Speed displays
        speedFrame = tk.Frame(mainFrame, bg='#1e3c72')
        speedFrame.pack(fill='x', pady=(0, 10))
        
        # Current Speed
        currentSpeedBox = tk.Frame(speedFrame, bg='#2c5aa0', relief='raised', bd=4)
        currentSpeedBox.pack(side='left', fill='both', expand=True, padx=(0, 3))
        
        tk.Label(
            currentSpeedBox,
            text="CURRENT SPEED",
            font=('Arial', 14, 'bold'),
            bg='#2c5aa0',
            fg='white',
            pady=5
        ).pack()
        
        self.currentSpeedValue = tk.Label(
            currentSpeedBox,
            text="0.0 MPH",
            font=('Arial', 36, 'bold'),
            bg='#1a1a2e',
            fg='#00ff00',
            pady=10,
            relief='sunken',
            bd=3
        )
        self.currentSpeedValue.pack(padx=10, pady=(0, 10))
        
        # Commanded Speed
        commandedSpeedBox = tk.Frame(speedFrame, bg='#3498db', relief='raised', bd=4)
        commandedSpeedBox.pack(side='left', fill='both', expand=True, padx=(3, 3))
        
        tk.Label(
            commandedSpeedBox,
            text="COMMANDED SPEED",
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white',
            pady=5
        ).pack()
        
        self.commandedSpeedValue = tk.Label(
            commandedSpeedBox,
            text="0.0 MPH",
            font=('Arial', 36, 'bold'),
            bg='#1a1a2e',
            fg='white',
            pady=10,
            relief='sunken',
            bd=3
        )
        self.commandedSpeedValue.pack(padx=10, pady=(0, 10))
        
        # Commanded Authority
        commandedAuthorityBox = tk.Frame(speedFrame, bg='#9b59b6', relief='raised', bd=4)
        commandedAuthorityBox.pack(side='right', fill='both', expand=True, padx=(3, 0))
        
        tk.Label(
            commandedAuthorityBox,
            text="COMMANDED AUTHORITY",
            font=('Arial', 14, 'bold'),
            bg='#9b59b6',
            fg='white',
            pady=5
        ).pack()
        
        self.commandedAuthorityValue = tk.Label(
            commandedAuthorityBox,
            text="0 blocks",
            font=('Arial', 30, 'bold'),
            bg='#1a1a2e',
            fg='#ffff00',
            pady=10,
            relief='sunken',
            bd=3
        )
        self.commandedAuthorityValue.pack(padx=10, pady=(0, 10))
        
        # Middle row: Mode, Manual Setpoint, and Time Scale
        modeFrame = tk.Frame(mainFrame, bg='#1e3c72')
        modeFrame.pack(fill='x', pady=10)
        
        # Drivetrain Mode
        modeBox = tk.Frame(modeFrame, bg='#27ae60', relief='raised', bd=4)
        modeBox.pack(side='left', fill='both', expand=True, padx=(0, 3))
        
        tk.Label(
            modeBox,
            text="DRIVETRAIN MODE",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            pady=5
        ).pack()
        
        self.modeValue = tk.Label(
            modeBox,
            text="AUTOMATIC",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='white',
            pady=12,
            relief='sunken',
            bd=3
        )
        self.modeValue.pack(padx=10, pady=(0, 10))
        
        # Manual Setpoint
        manualBox = tk.Frame(modeFrame, bg='#e67e22', relief='raised', bd=4)
        manualBox.pack(side='left', fill='both', expand=True, padx=(3, 3))
        
        tk.Label(
            manualBox,
            text="MANUAL SETPOINT",
            font=('Arial', 14, 'bold'),
            bg='#e67e22',
            fg='white',
            pady=5
        ).pack()
        
        self.manualSetpointValue = tk.Label(
            manualBox,
            text="-- MPH",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#666666',
            pady=12,
            relief='sunken',
            bd=3
        )
        self.manualSetpointValue.pack(padx=10, pady=(0, 10))
        
        # Time Scale (from CTC)
        timeScaleBox = tk.Frame(modeFrame, bg='#8e44ad', relief='raised', bd=4)
        timeScaleBox.pack(side='right', fill='both', expand=True, padx=(3, 0))
        
        tk.Label(
            timeScaleBox,
            text="TIME SCALE",
            font=('Arial', 14, 'bold'),
            bg='#8e44ad',
            fg='white',
            pady=5
        ).pack()
        
        self.timeScaleValue = tk.Label(
            timeScaleBox,
            text="1.0x",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#00ffff',
            pady=12,
            relief='sunken',
            bd=3
        )
        self.timeScaleValue.pack(padx=10, pady=(0, 10))
        
        # Auto Mode Info Row
        autoFrame = tk.Frame(mainFrame, bg='#1e3c72')
        autoFrame.pack(fill='x', pady=10)
        
        # Next Station
        stationBox = tk.Frame(autoFrame, bg='#16a085', relief='raised', bd=4)
        stationBox.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(
            stationBox,
            text="NEXT STATION",
            font=('Arial', 14, 'bold'),
            bg='#16a085',
            fg='white',
            pady=5
        ).pack()
        
        self.nextStationValue = tk.Label(
            stationBox,
            text="DORMONT",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='white',
            pady=12,
            relief='sunken',
            bd=3
        )
        self.nextStationValue.pack(padx=10, pady=(0, 10))
        
        # Distance to Station
        distanceBox = tk.Frame(autoFrame, bg='#d35400', relief='raised', bd=4)
        distanceBox.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(
            distanceBox,
            text="DISTANCE TO STATION",
            font=('Arial', 14, 'bold'),
            bg='#d35400',
            fg='white',
            pady=5
        ).pack()
        
        self.distanceToStationValue = tk.Label(
            distanceBox,
            text="0 m",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#00ff00',
            pady=12,
            relief='sunken',
            bd=3
        )
        self.distanceToStationValue.pack(padx=10, pady=(0, 10))
        
        # Control Panels Launch Section
        panelFrame = tk.Frame(mainFrame, bg='#34495e', relief='raised', bd=4)
        panelFrame.pack(fill='x', pady=(10, 0))
        
        tk.Label(
            panelFrame,
            text="CONTROL PANELS",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white',
            pady=8
        ).pack()
        
        buttonFrame = tk.Frame(panelFrame, bg='#34495e')
        buttonFrame.pack(pady=(0, 10))
        
        # Launch buttons
        btnStyle = {
            'font': ('Arial', 11, 'bold'),
            'width': 18,
            'height': 2,
            'bg': '#3498db',
            'fg': 'white',
            'activebackground': '#2980b9',
            'activeforeground': 'white',
            'cursor': 'hand2'
        }
        
        # Power Engineer button removed - panel auto-launches on startup
        
        tk.Button(
            buttonFrame,
            text="A/C System",
            command=self._launchACPanel,
            **btnStyle
        ).grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(
            buttonFrame,
            text="Announcements",
            command=self._launchAnnouncementPanel,
            **btnStyle
        ).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(
            buttonFrame,
            text="System Log",
            command=self._launchSystemLogViewer,
            **btnStyle
        ).grid(row=0, column=2, padx=5, pady=5)
    
    def _launchPowerEngineer(self):
        """Show Power Engineer Panel"""
        global powerEngineerPanel
        if powerEngineerPanel and powerEngineerPanel.root.winfo_exists():
            powerEngineerPanel.root.deiconify()
            powerEngineerPanel.root.lift()
            print("✓ Power Engineer Panel shown")
        else:
            print("Power Engineer Panel not available")
    
    def _launchACPanel(self):
        """Launch A/C System Panel"""
        global acPanel
        if acPanel is None or not tk.Toplevel.winfo_exists(acPanel.root):
            acRoot = tk.Toplevel(self.root)
            
            def send_ac_message(message):
                if self.server and self.train_model_connected:
                    self.server.send_to_ui("Train Model", message)
                    print(f"AC Panel → Train Model: {message}")
            
            acPanel = ACSystemPanel(acRoot, send_message_callback=send_ac_message)
            print("✓ Launched A/C System Panel")
        else:
            acPanel.root.lift()
            print("A/C System Panel already open")
    
    def _launchAnnouncementPanel(self):
        """Launch Station Announcement Panel"""
        global announcementPanel
        if announcementPanel is None or not tk.Toplevel.winfo_exists(announcementPanel.root):
            announcementRoot = tk.Toplevel(self.root)
            announcementPanel = StationAnnouncementPanel(announcementRoot, parent=self)
            print("✓ Launched Announcement Panel")
        else:
            announcementPanel.root.lift()
            print("Announcement Panel already open")
    
    def _launchSystemLogViewer(self):
        """Launch System Log Viewer"""
        global systemLogViewer
        if systemLogViewer is None or not tk.Toplevel.winfo_exists(systemLogViewer.root):
            try:
                systemLogRoot = tk.Toplevel(self.root)
                systemLogViewer = SystemLogViewer(systemLogRoot, self.gpio_client)
                print("✓ Launched System Log Viewer")
            except Exception as e:
                print(f"Warning: SystemLogViewer initialization issue: {e}")
                print("System will continue without log viewer window")
                systemLogViewer = None
        else:
            systemLogViewer.root.lift()
            print("System Log Viewer already open")
    
    def _updateDisplay(self):
        """Update all display elements (optimized to only update on changes)"""
        # Initialize cache on first run
        if not hasattr(self, '_display_cache'):
            self._display_cache = {
                'currentSpeed': None,
                'commandedSpeed': None,
                'authority': None,
                'mode': None,
                'isManual': None,
                'manualSetpoint': None,
                'nextStation': None,
                'distToStation': None,
                'isAtStation': None,
                'beacon1': None,
                'beacon2': None,
                'currentBlock': None,
                'timeScale': None
            }
        
        cache = self._display_cache
        
        # Get current values
        currentSpeedMPH = getCurrentSpeed()
        commandedSpeedMPH = getCommandedSpeed()
        authority = getCommandedAuthority()
        isManual = isManualMode()
        mode = getDrivetrainMode()
        
        # Only update speed displays if changed (with small threshold to avoid floating point jitter)
        if cache['currentSpeed'] is None or abs(currentSpeedMPH - cache['currentSpeed']) > 0.05:
            self.currentSpeedValue.config(text=f"{currentSpeedMPH:.1f} MPH")
            cache['currentSpeed'] = currentSpeedMPH
        
        if cache['commandedSpeed'] is None or abs(commandedSpeedMPH - cache['commandedSpeed']) > 0.05:
            self.commandedSpeedValue.config(text=f"{commandedSpeedMPH:.1f} MPH")
            cache['commandedSpeed'] = commandedSpeedMPH
        
        if cache['authority'] != authority:
            self.commandedAuthorityValue.config(text=f"{int(authority)} blocks")
            cache['authority'] = authority
        
        # Update time scale display
        global mult_value
        if cache['timeScale'] != mult_value:
            self.timeScaleValue.config(text=f"{mult_value:.1f}x")
            cache['timeScale'] = mult_value
        
        # Update mode display only if changed
        if cache['isManual'] != isManual or cache['mode'] != mode:
            self.modeValue.config(text=mode)
            if isManual:
                self.modeValue.config(bg='#e74c3c', fg='yellow')
            else:
                self.modeValue.config(bg='#1a1a2e', fg='white')
            cache['mode'] = mode
            cache['isManual'] = isManual
        
        # Update manual setpoint display
        if isManual:
            manualSpeed = getManualSetpointSpeed()
            if cache['manualSetpoint'] != manualSpeed:
                self.manualSetpointValue.config(text=f"{manualSpeed} MPH", fg='#ffff00')
                cache['manualSetpoint'] = manualSpeed
        else:
            if cache['manualSetpoint'] is not None:
                self.manualSetpointValue.config(text="-- MPH", fg='#666666')
                cache['manualSetpoint'] = None
        
        # Update station information (show in both manual and automatic modes)
        if autoModeEnabled:
            nextStation = getNextStationName()
            distToStation = getDistanceToNextStation()
            
            # Debug output every time we're at a beacon block
            if currentBlock in [27, 38]:
                print(f"[DISPLAY DEBUG] At beacon block {currentBlock}: beacon1={beacon1}, beacon2={beacon2}, nextStation={nextStation}")
            
            # Check if beacons or current block changed - force station name update
            if (cache['beacon1'] != beacon1 or cache['beacon2'] != beacon2 or 
                cache['currentBlock'] != currentBlock or cache['nextStation'] != nextStation):
                
                # Debug when updating
                if currentBlock in [27, 38]:
                    print(f"[DISPLAY DEBUG] Updating display: {cache['nextStation']} → {nextStation}")
                
                self.nextStationValue.config(text=nextStation)
                cache['nextStation'] = nextStation
                cache['beacon1'] = beacon1
                cache['beacon2'] = beacon2
                cache['currentBlock'] = currentBlock
                
                # Highlight alternative route in orange
                if "ALTERNATIVE ROUTE" in nextStation:
                    self.nextStationValue.config(fg='#ffa500')  # Orange for alternative route
                else:
                    # Reset to normal color (or yellow if at station)
                    if isAtStation:
                        self.nextStationValue.config(fg='#ffff00')
                    else:
                        self.nextStationValue.config(fg='white')
            
            # Only update distance if changed significantly (> 1 foot to reduce jitter)
            distToStationFeet = distToStation * 3.28084
            if cache['distToStation'] is None or abs(distToStationFeet - cache['distToStation']) > 1.0:
                decelDistanceFeet = DECELERATION_DISTANCE * 3.28084
                
                if distToStationFeet < 3.28084:
                    self.distanceToStationValue.config(text=f"{distToStationFeet:.1f} ft", fg='#ff0000')
                elif distToStationFeet < decelDistanceFeet:
                    self.distanceToStationValue.config(text=f"{int(distToStationFeet)} ft", fg='#ffa500')
                else:
                    self.distanceToStationValue.config(text=f"{int(distToStationFeet)} ft", fg='#00ff00')
                cache['distToStation'] = distToStationFeet
            
            # Highlight next station display if at station
            if cache['isAtStation'] != isAtStation:
                if isAtStation:
                    self.nextStationValue.config(fg='#ffff00')
                else:
                    self.nextStationValue.config(fg='white')
                cache['isAtStation'] = isAtStation
        else:
            # Auto mode not enabled, show disabled
            if cache['nextStation'] != 'DISABLED':
                self.nextStationValue.config(text="AUTO MODE DISABLED")
                self.distanceToStationValue.config(text="-- m", fg='#666666')
                cache['nextStation'] = 'DISABLED'
                cache['distToStation'] = None
        
        # Check connection status (only occasionally)
        if not hasattr(self, '_conn_check_counter'):
            self._conn_check_counter = 0
        self._conn_check_counter += 1
        if self._conn_check_counter >= 10:  # Check every 10 cycles
            if self.gpio_client and not self.gpio_client.connected:
                self._updateConnectionStatus(False)
            self._conn_check_counter = 0
        
        # Schedule next update - REDUCED from 100ms to 200ms for performance
        self.root.after(200, self._updateDisplay)
    
    def _startPowerCalculationLoop(self):
        """Start the continuous power calculation and transmission loop"""
        self._calculateAndSendPower()
    
    def _calculateAndSendPower(self):
        """Calculate power using PI controller and send to Train Model"""
        global powerEngineerPanel, lastSentPower
        
        if self.server and self.train_model_connected and powerEngineerPanel:
            try:
                # Calculate power command using PI controller
                powerKW = calculatePowerCommand()
                
                # Convert kW to Watts for Train Model
                powerWatts = powerKW * 1000.0
                
                # Time-based throttling: only send every 3 seconds
                current_time = time.time()
                if not hasattr(self, '_last_power_send_time'):
                    self._last_power_send_time = 0
                
                # Send if: (1) 3 seconds elapsed OR (2) power changed significantly AND at least 0.5s passed
                time_since_last_send = current_time - self._last_power_send_time
                power_changed = lastSentPower is None or abs(powerWatts - lastSentPower) > 100
                
                # SAFETY: Do not send power if service brake is active
                if serviceBrakeActive:
                    # Service brake engaged - force power to zero
                    if lastSentPower != 0:
                        self.server.send_to_ui("Train Model", {
                            'command': 'Power Command',
                            'value': 0,
                            'train_id': 1
                        })
                        lastSentPower = 0
                        self._last_power_send_time = current_time
                        print("⚠️  Service brake active - power command set to ZERO")
                elif time_since_last_send >= 3.0 or (power_changed and time_since_last_send >= 0.5):
                    self.server.send_to_ui("Train Model", {
                        'command': 'Power Command',
                        'value': powerWatts,
                        'train_id': 1
                    })
                    lastSentPower = powerWatts
                    self._last_power_send_time = current_time
                
            except Exception as e:
                print(f"Error calculating/sending power: {e}")
        
        # Schedule next calculation (100ms interval)
        self.root.after(100, self._calculateAndSendPower)
    
    def _connectToSoftwareTC(self):
        """Connect to software train controller using TrainSocketServer"""
        def connect_thread():
            try:
                time.sleep(2)  # Give software TC time to start
                self.server.connect_to_ui('localhost', 12346, "Train SW")
                self.software_tc_connected = True
                print("✓ Connected to Software TC (Train SW) on port 12346")
            except Exception as e:
                print(f"✗ Could not connect to Software TC: {e}")
                self.software_tc_connected = False
        
        # Run in thread to avoid blocking
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _sendPIDToSoftwareTC(self, kp, ki):
        """Send Kp and Ki values to software train controller"""
        if not self.software_tc_connected:
            return  # Silently skip if not connected
        
        try:
            message = {
                'command': 'PID Parameters',
                'kp': float(kp),
                'ki': float(ki)
            }
            self.server.send_to_ui("Train SW", message)
            print(f"✓ Sent PID to Software TC: Kp={kp:.1f}, Ki={ki:.1f}")
        except Exception as e:
            print(f"✗ Error sending PID to Software TC: {e}")
            self.software_tc_connected = False
    
    def _onClose(self):
        print("\nClosing application...")
        if self.gpio_client:
            self.gpio_client.disconnect()
        if self.server:
            self.server.stop_server()
        cleanupAll()
        self.root.destroy()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[KEYBOARD INTERRUPT] Shutting down...")
        cleanupAll()
        import sys
        sys.exit(0)