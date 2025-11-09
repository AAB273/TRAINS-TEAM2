#!/usr/bin/env python3
"""
Train Control System for Windows - Remote GPIO Control

This version runs on WINDOWS and connects to the Raspberry Pi GPIO Server remotely.
The Pi runs TC_GPIO_Server.py which handles all the actual GPIO hardware.

Connection Architecture:
    Windows (This File)  ↔  Raspberry Pi (TC_GPIO_Server.py)
          ↕
    Train Model (Windows)
"""

import json
import socket
import threading
from pathlib import Path
import time
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TC_HW_AirConditioning_UI import ACSystemPanel
from TC_HW_Announcement_UI import StationAnnouncementPanel
from TC_HW_TrackInfo_UI import TrackInformationPanel
from TC_HW_SystemLogUI import SystemLogViewer
from TrainSocketServer import TrainSocketServer

# CONFIGURATION - SET YOUR PI'S IP ADDRESS HERE
PI_HOST = '192.168.1.179'  # ← CHANGE THIS to your Pi's IP address
PI_GPIO_PORT = 12348

def load_socket_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("modules", {})
    return {}

# Global state variables (mirrored from Pi)
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

running = True
acPanel = None
announcementPanel = None
trackInfoPanel = None
systemLogViewer = None

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
        self.log_message_callback = None
    
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
            
            elif msg_type == 'log_message':
                # Forward log messages to callback
                if self.log_message_callback:
                    self.log_message_callback(
                        message.get('message', ''),
                        message.get('category', 'system')
                    )
        
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
    
    def disconnect(self):
        """Disconnect from GPIO server"""
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

# Simulated GPIO functions (these just update local state, Pi handles real GPIO)
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

def cleanupAll():
    global acPanel, announcementPanel, trackInfoPanel, systemLogViewer
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
        if systemLogViewer and systemLogViewer.root.winfo_exists():
            systemLogViewer.root.destroy()
    except:
        pass

def main():
    global acPanel, announcementPanel, trackInfoPanel, systemLogViewer
    
    print("=" * 60)
    print("Train Control System - Windows Hardware Controller")
    print("=" * 60)
    print(f"Connecting to GPIO Server at {PI_HOST}:{PI_GPIO_PORT}")
    print("=" * 60)
    
    root = tk.Tk()
    speedDisplay = TrainSpeedDisplayUI(root)
    
    acRoot = tk.Toplevel(root)
    acPanel = ACSystemPanel(acRoot)
    
    announcementRoot = tk.Toplevel(root)
    announcementPanel = StationAnnouncementPanel(announcementRoot)
    
    trackInfoRoot = tk.Toplevel(root)
    trackInfoPanel = TrackInformationPanel(trackInfoRoot)
    
    # Create System Log Viewer window
    systemLogRoot = tk.Toplevel(root)
    systemLogViewer = SystemLogViewer(systemLogRoot, gpio_client=speedDisplay.gpio_client)
    
    root.mainloop()

class TrainSpeedDisplayUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("TRAIN SPEED CONTROL DISPLAY")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e3c72')
        
        # GPIO Client Setup
        self.gpio_client = GPIOClient(PI_HOST, PI_GPIO_PORT)
        self.gpio_client.state_update_callback = self._onGPIOStateUpdate
        self.gpio_client.log_message_callback = self._onGPIOLogMessage
        
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
        train_controller_hw_config = module_config.get("Train Controller HW", {"port": 12347})
        self.server = TrainSocketServer(port=train_controller_hw_config["port"], ui_id="Train Controller HW")
        self.server.set_allowed_connections(["Train Model"])
        self.server.start_server(self._process_message)
        
        # Try to connect to Train Model
        try:
            self.server.connect_to_ui('localhost', 12345, "Train Model")
            print("✓ Connected to Train Model")
            self.train_model_connected = True
        except:
            print("Note: Train Model not yet running")
            self.train_model_connected = False

        self._createWidgets()
        self._updateDisplay()
        
        self.root.protocol("WM_DELETE_WINDOW", self._onClose)
    
    def _onGPIOStateUpdate(self, state):
        """Handle state update from GPIO server"""
        global leftDoorOpen, rightDoorOpen, headlightsOn, interiorLightsOn
        global serviceBrakeActive, trainHornActive, emergencyBrakeEngaged
        global drivetrainManualMode, manualSetpointSpeed
        global speedUpPressed, speedDownPressed, speedConfirmPressed
        global systemLogViewer
        
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
        
        # Forward state updates to System Log Viewer
        if systemLogViewer:
            try:
                systemLogViewer.handleStateUpdate(state)
            except:
                pass
        
        # Send relevant updates to Train Model
        if self.server and self.train_model_connected:
            try:
                if drivetrainManualMode:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Manual Setpoint Speed',
                        'value': manualSetpointSpeed
                    })
                
                if emergencyBrakeEngaged:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Emergency Brake',
                        'value': True
                    })
                elif not emergencyBrakeEngaged:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Emergency Brake',
                        'value': False
                    })
                
                if serviceBrakeActive:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Service Brake',
                        'value': True
                    })
                elif not serviceBrakeActive:
                    self.server.send_to_ui("Train Model", {
                        'command': 'Service Brake',
                        'value': False
                    })
            except:
                pass
    
    def _onGPIOLogMessage(self, message, category):
        """Handle log message from GPIO server"""
        global systemLogViewer
        
        # Forward log messages to System Log Viewer
        if systemLogViewer:
            try:
                systemLogViewer.handleLogMessage(message, category)
            except:
                pass
    
    def _updateConnectionStatus(self, connected):
        """Update GPIO connection status"""
        if connected:
            self.connectionLabel.config(
                text=f"✓ GPIO Connected ({PI_HOST})",
                bg='#27ae60'
            )
        else:
            self.connectionLabel.config(
                text=f"✗ GPIO Failed ({PI_HOST})",
                bg='#e74c3c'
            )
    
    def _process_message(self, message, source_ui_id):
        """Process incoming messages from Train Model"""
        try:
            print(f"Received from {source_ui_id}: {message}")
            
            if source_ui_id != "Train Model":
                return
            
            self.train_model_connected = True
            
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
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('passenger_emergency', value)
            
            elif command == 'Brake Failure':
                global brakeFailure
                brakeFailure = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('brake_failure', value)
            
            elif command == 'Train Engine Failure':
                global engineFailure
                engineFailure = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('engine_failure', value)
            
            elif command == 'Signal Pickup Failure':
                global signalFailure
                signalFailure = value
                if self.gpio_client and self.gpio_client.connected:
                    self.gpio_client.setLED('signal_failure', value)
        
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
            pady=15
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
            "0 MPH"
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
            text="Physical buttons on Raspberry Pi control the system\n" +
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
        
        # Check connection status
        if self.gpio_client and not self.gpio_client.connected:
            self._updateConnectionStatus(False)
        
        self.root.after(100, self._updateDisplay)
    
    def _onClose(self):
        print("\nClosing application...")
        if self.gpio_client:
            self.gpio_client.disconnect()
        if self.server:
            self.server.stop_server()
        cleanupAll()
        self.root.destroy()

if __name__ == "__main__":
    main()