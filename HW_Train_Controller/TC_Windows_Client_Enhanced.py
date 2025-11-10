#!/usr/bin/env python3
"""
Train Control System - Windows Hardware Controller UI
Connects to BOTH Raspberry Pi GPIO Server AND Train Model (both on Windows)

Architecture:
    Windows Laptop:
    ┌─────────────────────────────────────────┐
    │  Train Model UI  ←→  Train Controller  │
    │  (Port 12345)        HW UI (This)      │
    └─────────────────────────────────────────┘
                    ↕ Socket (Port 12348)
            Raspberry Pi (GPIO Server)

Features:
- GPIO control via Pi server (port 12348)
- Train Model communication via TrainSocketServer (port 12345)
- Full UI with speed/authority displays
- LED controls
- Real-time status monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading
import time
from datetime import datetime
import sys
import os
from pathlib import Path

# Try to import TrainSocketServer
try:
    # Try relative import first (if in TRAINS-TEAM2 structure)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from TrainSocketServer import TrainSocketServer
    HAS_SOCKET_SERVER = True
except ImportError:
    print("Warning: TrainSocketServer not found. Train Model communication disabled.")
    print("Make sure TrainSocketServer.py is in the parent directory.")
    HAS_SOCKET_SERVER = False

# Try to load config
def load_socket_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("modules", {})
    return {}

# CONFIGURATION
PI_HOST = '192.168.1.179'  # ← CHANGE THIS to your Pi's IP
PI_GPIO_PORT = 12348

# Load Train Controller port from config, or use default
module_config = load_socket_config()
train_controller_config = module_config.get("Train Controller HW", {"port": 12347})
TRAIN_CONTROLLER_PORT = train_controller_config["port"]

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
        """Connect to GPIO server"""
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
        """Send command to set LED state"""
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

class EnhancedTrainControlUI:
    """Enhanced Windows UI with GPIO and Train Model integration via TrainSocketServer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TRAIN CONTROL SYSTEM - Windows Hardware Controller")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # GPIO client for Raspberry Pi
        self.gpio_client = None
        
        # TrainSocketServer for Train Model communication
        self.socket_server = None
        self.train_model_connected = False
        
        # GPIO State from Pi
        self.gpio_state = {
            'leftDoorOpen': False,
            'rightDoorOpen': False,
            'headlightsOn': False,
            'interiorLightsOn': False,
            'serviceBrakeActive': False,
            'trainHornActive': False,
            'emergencyBrakeEngaged': False,
            'drivetrainManualMode': False,
            'manualSetpointSpeed': 0,
            'speedUpPressed': False,
            'speedDownPressed': False,
            'speedConfirmPressed': False
        }
        
        # Train Model data
        self.commandedSpeed = 0.0
        self.commandedAuthority = 0
        self.currentSpeed = 0.0
        
        # LED control variables
        self.passengerEmergency = tk.BooleanVar(value=False)
        self.brakeFailure = tk.BooleanVar(value=False)
        self.engineFailure = tk.BooleanVar(value=False)
        self.signalFailure = tk.BooleanVar(value=False)
        
        self._createWidgets()
        self._setupTrainModel()
        self._connectToGPIOServer()
        
        # Start update loop
        self._updateDisplay()
        
        self.root.protocol("WM_DELETE_WINDOW", self._onClose)
    
    def _createWidgets(self):
        """Create all UI widgets"""
        # Header with connection status
        headerFrame = tk.Frame(self.root, bg='#1e5a8e')
        headerFrame.pack(fill='x')
        
        headerLabel = tk.Label(
            headerFrame,
            text="TRAIN CONTROL SYSTEM\nEnhanced Windows Client",
            font=('Arial', 24, 'bold'),
            bg='#1e5a8e',
            fg='white',
            pady=10
        )
        headerLabel.pack()
        
        # Connection status indicators
        statusFrame = tk.Frame(headerFrame, bg='#1e5a8e')
        statusFrame.pack(fill='x', pady=(0, 10))
        
        leftStatus = tk.Frame(statusFrame, bg='#1e5a8e')
        leftStatus.pack(side='left', fill='x', expand=True)
        
        self.gpioConnectionLabel = tk.Label(
            leftStatus,
            text="GPIO: Connecting...",
            font=('Arial', 11),
            bg='#e67e22',
            fg='white',
            pady=5
        )
        self.gpioConnectionLabel.pack(side='left', padx=(20, 5), fill='x', expand=True)
        
        self.trainModelConnectionLabel = tk.Label(
            leftStatus,
            text="Train Model: Connecting...",
            font=('Arial', 11),
            bg='#e67e22',
            fg='white',
            pady=5
        )
        self.trainModelConnectionLabel.pack(side='right', padx=(5, 20), fill='x', expand=True)
        
        # Main content notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#2c3e50', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 11, 'bold'))
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self._createDashboardTab()
        self._createHardwareStatusTab()
        self._createLEDControlTab()
    
    def _createDashboardTab(self):
        """Create main dashboard with speed displays"""
        frame = tk.Frame(self.notebook, bg='#1e3c72')
        self.notebook.add(frame, text='Dashboard')
        
        # Speed display section
        speedSection = tk.Frame(frame, bg='#2c5aa0', relief='raised', bd=5)
        speedSection.pack(fill='both', expand=True, padx=20, pady=20)
        
        speedTitle = tk.Label(
            speedSection,
            text="CURRENT SPEED",
            font=('Arial', 24, 'bold'),
            bg='#2c5aa0',
            fg='white',
            pady=10
        )
        speedTitle.pack()
        
        self.speedDisplayLabel = tk.Label(
            speedSection,
            text="0",
            font=('Arial', 100, 'bold'),
            bg='#1a1a2e',
            fg='#00ff00',
            width=4,
            relief='sunken',
            bd=5
        )
        self.speedDisplayLabel.pack(padx=30, pady=20)
        
        speedUnit = tk.Label(
            speedSection,
            text="MPH",
            font=('Arial', 20, 'bold'),
            bg='#2c5aa0',
            fg='white',
            pady=10
        )
        speedUnit.pack()
        
        # Info boxes
        infoFrame = tk.Frame(frame, bg='#1e3c72')
        infoFrame.pack(fill='both', padx=20, pady=(0, 20))
        
        leftInfo = tk.Frame(infoFrame, bg='#1e3c72')
        leftInfo.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.cmdSpeedBox = self._createInfoBox(leftInfo, "COMMANDED SPEED", "0 MPH", '#3498db')
        self.cmdAuthorityBox = self._createInfoBox(leftInfo, "COMMANDED AUTHORITY", "0 BLOCKS", '#9b59b6')
        
        rightInfo = tk.Frame(infoFrame, bg='#1e3c72')
        rightInfo.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.manualSetpointBox = self._createInfoBox(rightInfo, "MANUAL SETPOINT", "-- MPH", '#e67e22')
        self.drivetrainModeBox = self._createInfoBox(rightInfo, "DRIVETRAIN MODE", "AUTOMATIC", '#27ae60')
    
    def _createInfoBox(self, parent, title, default_text, color):
        """Create info display box"""
        frame = tk.Frame(parent, bg=color, relief='raised', bd=4)
        frame.pack(fill='both', expand=True, pady=10)
        
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
            text=default_text,
            font=('Arial', 28, 'bold'),
            bg='#1a1a2e',
            fg='white',
            pady=20,
            relief='sunken',
            bd=3
        )
        valueLabel.pack(padx=15, pady=(0, 15))
        
        return valueLabel
    
    def _createHardwareStatusTab(self):
        """Create hardware status monitoring tab"""
        frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(frame, text='Hardware Status')
        
        title = tk.Label(
            frame,
            text="Hardware Button & Switch Status (Live from Pi)",
            font=('Arial', 18, 'bold'),
            bg='#2980b9',
            fg='white',
            relief='raised',
            bd=4,
            padx=20,
            pady=10
        )
        title.pack(pady=(20, 30))
        
        # Grid layout for status displays
        gridFrame = tk.Frame(frame, bg='#2c3e50', relief='raised', bd=4)
        gridFrame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create status labels in columns
        self.statusLabels = {}
        
        col1 = tk.Frame(gridFrame, bg='#2c3e50')
        col1.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        col2 = tk.Frame(gridFrame, bg='#2c3e50')
        col2.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        col3 = tk.Frame(gridFrame, bg='#2c3e50')
        col3.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Column 1: Doors & Lights
        self.statusLabels['leftDoor'] = self._createStatusLabel(col1, "Left Door", '#3498db')
        self.statusLabels['rightDoor'] = self._createStatusLabel(col1, "Right Door", '#3498db')
        self.statusLabels['headlights'] = self._createStatusLabel(col1, "Headlights", '#f1c40f')
        self.statusLabels['interiorLights'] = self._createStatusLabel(col1, "Interior Lights", '#f1c40f')
        
        # Column 2: Brakes & Horn
        self.statusLabels['serviceBrake'] = self._createStatusLabel(col2, "Service Brake", '#e74c3c')
        self.statusLabels['trainHorn'] = self._createStatusLabel(col2, "Train Horn", '#f39c12')
        self.statusLabels['emergencyBrake'] = self._createStatusLabel(col2, "Emergency Brake", '#c0392b')
        
        # Column 3: Drive Controls
        self.statusLabels['drivetrainMode'] = self._createStatusLabel(col3, "Drivetrain", '#27ae60')
        self.statusLabels['speedUp'] = self._createStatusLabel(col3, "Speed Up", '#16a085')
        self.statusLabels['speedDown'] = self._createStatusLabel(col3, "Speed Down", '#d35400')
        self.statusLabels['speedConfirm'] = self._createStatusLabel(col3, "Confirm", '#8e44ad')
    
    def _createStatusLabel(self, parent, label, color):
        """Create a status display label"""
        frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3)
        frame.pack(fill='x', pady=6)
        
        titleLabel = tk.Label(
            frame,
            text=label,
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white',
            anchor='w',
            padx=10,
            pady=4
        )
        titleLabel.pack(fill='x')
        
        valueLabel = tk.Label(
            frame,
            text="--",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#95a5a6',
            pady=8,
            relief='sunken',
            bd=2
        )
        valueLabel.pack(fill='x', padx=8, pady=(0, 8))
        
        return valueLabel
    
    def _createLEDControlTab(self):
        """Create LED control tab"""
        frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(frame, text='LED Controls')
        
        title = tk.Label(
            frame,
            text="LED Output Controls (Simulate Train Model Signals)",
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
        controlFrame.pack(fill='both', expand=True, padx=40, pady=20)
        
        self._createLEDControl(controlFrame, "Passenger Emergency Signal", self.passengerEmergency,
                              lambda: self._setLED('passenger_emergency', self.passengerEmergency.get()), '#e74c3c')
        self._createLEDControl(controlFrame, "Brake Failure", self.brakeFailure,
                              lambda: self._setLED('brake_failure', self.brakeFailure.get()), '#e67e22')
        self._createLEDControl(controlFrame, "Engine Failure", self.engineFailure,
                              lambda: self._setLED('engine_failure', self.engineFailure.get()), '#f39c12')
        self._createLEDControl(controlFrame, "Signal Failure", self.signalFailure,
                              lambda: self._setLED('signal_failure', self.signalFailure.get()), '#9b59b6')
    
    def _createLEDControl(self, parent, label, variable, command, color):
        """Create LED control widget"""
        frame = tk.Frame(parent, bg='#aed6f1', relief='raised', bd=3)
        frame.pack(fill='x', padx=15, pady=15)
        
        labelWidget = tk.Label(
            frame,
            text=label,
            font=('Arial', 18, 'bold'),
            bg='#aed6f1',
            fg='#1e5a8e',
            anchor='w',
            padx=20
        )
        labelWidget.pack(side='left', fill='x', expand=True)
        
        statusFrame = tk.Frame(frame, bg='#34495e', relief='sunken', bd=2)
        statusFrame.pack(side='left', padx=15)
        
        statusLabel = tk.Label(
            statusFrame,
            text="OFF",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='white',
            width=8,
            padx=15,
            pady=8
        )
        statusLabel.pack()
        
        def updateStatus(*args):
            if variable.get():
                statusLabel.config(text="ON", bg=color)
            else:
                statusLabel.config(text="OFF", bg='#34495e')
        
        variable.trace('w', updateStatus)
        
        button = tk.Button(
            frame,
            text="TOGGLE",
            font=('Arial', 16, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            relief='raised',
            bd=4,
            padx=30,
            pady=12,
            command=lambda: self._toggleLED(variable, command)
        )
        button.pack(side='right', padx=20)
    
    def _setupTrainModel(self):
        """Setup TrainSocketServer for Train Model communication"""
        if not HAS_SOCKET_SERVER:
            print("TrainSocketServer not available - Train Model integration disabled")
            return
        
        try:
            # Create socket server on our port
            self.socket_server = TrainSocketServer(port=TRAIN_CONTROLLER_PORT, ui_id="Train Controller HW")
            
            # Set allowed connections (Train Model can connect to us)
            self.socket_server.set_allowed_connections(["Train Model"])
            
            # Start our server
            self.socket_server.start_server(self._processTrainModelMessage)
            
            # Try to connect to Train Model (it might already be running)
            try:
                # Try to connect to Train Model on port 12345 (or from config)
                train_model_config = module_config.get("Train Model", {"port": 12345})
                train_model_port = train_model_config["port"]
                
                self.socket_server.connect_to_ui('localhost', train_model_port, "Train Model")
                print(f"✓ Connected to Train Model on port {train_model_port}")
                self.train_model_connected = True
            except Exception as e:
                print(f"Note: Train Model not yet running (will connect when available): {e}")
                self.train_model_connected = False
            
        except Exception as e:
            print(f"Error setting up Train Model communication: {e}")
            self.socket_server = None
    
    def _processTrainModelMessage(self, message, source_ui_id):
        """Process incoming messages from Train Model"""
        try:
            if source_ui_id != "Train Model":
                return
            
            self.train_model_connected = True
            
            command = message.get('command')
            value = message.get('value')
            
            if command == 'Commanded Speed':
                self.commandedSpeed = float(value)
            
            elif command == 'Commanded Authority':
                self.commandedAuthority = int(value)
            
            elif command == 'Actual Velocity':
                self.currentSpeed = float(value)
            
            elif command == 'Passenger Emergency Signal':
                self.passengerEmergency.set(bool(value))
                self._setLED('passenger_emergency', bool(value))
            
            elif command == 'Brake Failure':
                self.brakeFailure.set(bool(value))
                self._setLED('brake_failure', bool(value))
            
            elif command == 'Train Engine Failure':
                self.engineFailure.set(bool(value))
                self._setLED('engine_failure', bool(value))
            
            elif command == 'Signal Pickup Failure':
                self.signalFailure.set(bool(value))
                self._setLED('signal_failure', bool(value))
        
        except Exception as e:
            print(f"Error processing Train Model message: {e}")
    
    def _sendToTrainModel(self, command, value):
        """Send message to Train Model"""
        if self.socket_server and self.train_model_connected:
            try:
                message = {
                    'command': command,
                    'value': value
                }
                self.socket_server.send_to_ui("Train Model", message)
            except Exception as e:
                print(f"Error sending to Train Model: {e}")
                self.train_model_connected = False
    
    def _connectToGPIOServer(self):
        """Connect to Raspberry Pi GPIO server"""
        self.gpio_client = GPIOClient(PI_HOST, PI_GPIO_PORT)
        self.gpio_client.state_update_callback = self._onGPIOStateUpdate
        
        def connect_thread():
            if self.gpio_client.connect():
                self.root.after(0, lambda: self._updateConnectionStatus('gpio', True))
            else:
                self.root.after(0, lambda: self._updateConnectionStatus('gpio', False))
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def _updateConnectionStatus(self, connection_type, connected):
        """Update connection status display"""
        if connection_type == 'gpio':
            if connected:
                self.gpioConnectionLabel.config(
                    text=f"✓ GPIO Connected ({PI_HOST})",
                    bg='#27ae60'
                )
            else:
                self.gpioConnectionLabel.config(
                    text=f"✗ GPIO Failed ({PI_HOST})",
                    bg='#e74c3c'
                )
        
        elif connection_type == 'train_model':
            if connected:
                self.trainModelConnectionLabel.config(
                    text=f"✓ Train Model Connected",
                    bg='#27ae60'
                )
            else:
                self.trainModelConnectionLabel.config(
                    text=f"⚬ Train Model Waiting...",
                    bg='#95a5a6'
                )
    
    def _onGPIOStateUpdate(self, state):
        """Handle state update from GPIO server"""
        self.gpio_state.update(state)
        self.root.after(0, self._updateHardwareStatus)
        
        # Send relevant updates to Train Model
        if self.socket_server and self.train_model_connected:
            # Send manual setpoint speed
            if state.get('drivetrainManualMode'):
                self._sendToTrainModel('Manual Setpoint Speed', state.get('manualSetpointSpeed', 0))
            
            # Send emergency brake status
            if state.get('emergencyBrakeEngaged'):
                self._sendToTrainModel('Emergency Brake', True)
            else:
                self._sendToTrainModel('Emergency Brake', False)
            
            # Send service brake status
            if state.get('serviceBrakeActive'):
                self._sendToTrainModel('Service Brake', True)
            else:
                self._sendToTrainModel('Service Brake', False)
    
    def _updateHardwareStatus(self):
        """Update hardware status displays from GPIO state"""
        state = self.gpio_state
        
        # Doors
        self._updateStatusDisplay('leftDoor', state['leftDoorOpen'], "OPEN", "CLOSED", '#3498db')
        self._updateStatusDisplay('rightDoor', state['rightDoorOpen'], "OPEN", "CLOSED", '#3498db')
        
        # Lights
        self._updateStatusDisplay('headlights', state['headlightsOn'], "ON", "OFF", '#f1c40f')
        self._updateStatusDisplay('interiorLights', state['interiorLightsOn'], "ON", "OFF", '#f1c40f')
        
        # Brakes
        self._updateStatusDisplay('serviceBrake', state['serviceBrakeActive'], "ENGAGED", "RELEASED", '#e74c3c')
        self._updateStatusDisplay('emergencyBrake', state['emergencyBrakeEngaged'], "🚨 ENGAGED", "RELEASED", '#c0392b')
        
        # Horn
        self._updateStatusDisplay('trainHorn', state['trainHornActive'], "SOUNDING", "OFF", '#f39c12')
        
        # Drivetrain
        self._updateStatusDisplay('drivetrainMode', state['drivetrainManualMode'], "MANUAL", "AUTOMATIC", '#e74c3c', '#27ae60')
        
        # Speed buttons
        self._updateStatusDisplay('speedUp', state['speedUpPressed'], "PRESSED", "", '#16a085')
        self._updateStatusDisplay('speedDown', state['speedDownPressed'], "PRESSED", "", '#d35400')
        self._updateStatusDisplay('speedConfirm', state['speedConfirmPressed'], "PRESSED", "", '#8e44ad')
    
    def _updateStatusDisplay(self, key, condition, active_text, inactive_text, active_color, inactive_color='#2c3e50'):
        """Update a status display label"""
        if key in self.statusLabels:
            if condition:
                self.statusLabels[key].config(text=active_text, bg=active_color, fg='white')
            else:
                self.statusLabels[key].config(text=inactive_text, bg=inactive_color, fg='#95a5a6')
    
    def _toggleLED(self, variable, command):
        """Toggle LED and send command"""
        variable.set(not variable.get())
        command()
    
    def _setLED(self, led_name, state):
        """Send LED control command to Pi"""
        if self.gpio_client and self.gpio_client.connected:
            self.gpio_client.send({
                'type': 'set_led',
                'led': led_name,
                'state': state
            })
        else:
            messagebox.showwarning("Not Connected", "Not connected to GPIO server")
    
    def _updateDisplay(self):
        """Update display periodically"""
        # Update speed display
        speed = int(self.currentSpeed)
        self.speedDisplayLabel.config(text=str(speed))
        
        # Color based on mode
        if self.gpio_state.get('drivetrainManualMode'):
            self.speedDisplayLabel.config(fg='#ffa500')
        else:
            self.speedDisplayLabel.config(fg='#00ff00')
        
        # Update info boxes
        self.cmdSpeedBox.config(text=f"{int(self.commandedSpeed)} MPH")
        self.cmdAuthorityBox.config(text=f"{self.commandedAuthority} BLOCKS")
        
        # Manual setpoint
        if self.gpio_state.get('drivetrainManualMode'):
            setpoint = self.gpio_state.get('manualSetpointSpeed', 0)
            self.manualSetpointBox.config(text=f"{setpoint} MPH", fg='#ffa500')
        else:
            self.manualSetpointBox.config(text="-- MPH", fg='#666666')
        
        # Drivetrain mode
        mode = "MANUAL" if self.gpio_state.get('drivetrainManualMode') else "AUTOMATIC"
        self.drivetrainModeBox.config(text=mode)
        
        # Check connections
        if self.gpio_client and not self.gpio_client.connected:
            self._updateConnectionStatus('gpio', False)
        
        # Update Train Model connection status
        if self.socket_server:
            self._updateConnectionStatus('train_model', self.train_model_connected)
        
        self.root.after(100, self._updateDisplay)
    
    def _onClose(self):
        """Clean up on window close"""
        print("\nClosing application...")
        
        if self.gpio_client:
            self.gpio_client.disconnect()
        
        if self.socket_server:
            self.socket_server.stop_server()
        
        self.root.destroy()

def main():
    """Main entry point"""
    print("=" * 60)
    print("TRAIN CONTROL SYSTEM - Windows Hardware Controller")
    print("=" * 60)
    print(f"GPIO Server (Pi): {PI_HOST}:{PI_GPIO_PORT}")
    print(f"Train Controller Port: {TRAIN_CONTROLLER_PORT}")
    if HAS_SOCKET_SERVER:
        print("Train Model integration: ENABLED")
    else:
        print("Train Model integration: DISABLED (TrainSocketServer not found)")
    print("=" * 60)
    
    root = tk.Tk()
    app = EnhancedTrainControlUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
