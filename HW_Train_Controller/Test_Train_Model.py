#!/usr/bin/env python3
"""
Test Train Model - Simulates Train Model for Testing Train Controller HW

This script acts like the Train Model and sends test commands to the 
Train Controller HW interface, including commanded speed values.

Usage:
    python Test_Train_Model.py
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

# Try to import TrainSocketServer from parent directory
try:
    # Get the parent directory (TRAINS-TEAM2)
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from TrainSocketServer import TrainSocketServer
    HAS_SOCKET_SERVER = True
    print(f"✓ TrainSocketServer loaded from {project_root}")
except ImportError as e:
    print("ERROR: TrainSocketServer.py not found!")
    print(f"Error: {e}")
    print(f"\nLooking in parent directory: {Path(__file__).parent.parent}")
    print("\nExpected structure:")
    print("  C:\\Users\\lucas\\Desktop\\TRAINS-TEAM2\\TrainSocketServer.py")
    print("  C:\\Users\\lucas\\Desktop\\TRAINS-TEAM2\\HW_Train_Controller\\Test_Train_Model.py")
    sys.exit(1)

class TestTrainModel:
    """Test Train Model that sends commands to Train Controller HW"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Train Model - Command Sender")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')
        
        # Socket server setup
        self.server = TrainSocketServer(port=12345, ui_id="Train Model")
        self.server.set_allowed_connections(["Train Controller HW"])
        self.server.start_server(self._process_message)
        
        # Try to connect to Train Controller HW
        try:
            self.server.connect_to_ui('localhost', 12347, "Train Controller HW")
            print("✓ Connected to Train Controller HW")
            self.connected = True
        except Exception as e:
            print(f"Note: Train Controller HW not yet running: {e}")
            self.connected = False
        
        # Test values
        self.commandedSpeed = tk.DoubleVar(value=45.0)
        self.commandedAuthority = tk.IntVar(value=100)
        self.actualVelocity = tk.DoubleVar(value=40.0)
        
        # Failure indicators
        self.passengerEmergency = tk.BooleanVar(value=False)
        self.brakeFailure = tk.BooleanVar(value=False)
        self.engineFailure = tk.BooleanVar(value=False)
        self.signalFailure = tk.BooleanVar(value=False)
        
        self._createWidgets()
        
        # Auto-send updates every 2 seconds
        self.auto_send = tk.BooleanVar(value=False)
        self._autoSendLoop()
        
        self.root.protocol("WM_DELETE_WINDOW", self._onClose)
    
    def _process_message(self, message, source_ui_id):
        """Process incoming messages from Train Controller HW"""
        try:
            print(f"Received from {source_ui_id}: {message}")
            
            command = message.get('command')
            value = message.get('value')
            
            # Just log what we receive for now
            if command:
                print(f"  Command: {command} = {value}")
        
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _createWidgets(self):
        """Create the test UI"""
        # Header
        headerFrame = tk.Frame(self.root, bg='#34495e')
        headerFrame.pack(fill='x')
        
        headerLabel = tk.Label(
            headerFrame,
            text="TEST TRAIN MODEL\nCommand Sender",
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg='white',
            pady=15
        )
        headerLabel.pack()
        
        # Connection status
        self.connectionLabel = tk.Label(
            headerFrame,
            text="Waiting for Train Controller HW...",
            font=('Arial', 11),
            bg='#e67e22',
            fg='white',
            pady=5
        )
        self.connectionLabel.pack(fill='x')
        
        # Main content
        mainFrame = tk.Frame(self.root, bg='#2c3e50')
        mainFrame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Speed & Authority Section
        self._createSpeedSection(mainFrame)
        
        # Failure Signals Section
        self._createFailureSection(mainFrame)
        
        # Control Buttons
        self._createControlSection(mainFrame)
    
    def _createSpeedSection(self, parent):
        """Create speed and authority controls"""
        frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3)
        frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            frame,
            text="Speed & Authority Controls",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white',
            pady=10
        ).pack()
        
        # Commanded Speed
        speedFrame = tk.Frame(frame, bg='#34495e')
        speedFrame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            speedFrame,
            text="Commanded Speed (MPH):",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(side='left')
        
        speedEntry = tk.Entry(
            speedFrame,
            textvariable=self.commandedSpeed,
            font=('Arial', 12),
            width=10
        )
        speedEntry.pack(side='right')
        
        speedSlider = tk.Scale(
            frame,
            from_=0,
            to=70,
            orient='horizontal',
            variable=self.commandedSpeed,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            length=500,
            width=20
        )
        speedSlider.pack(pady=5)
        
        # Commanded Authority
        authFrame = tk.Frame(frame, bg='#34495e')
        authFrame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            authFrame,
            text="Commanded Authority (blocks):",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(side='left')
        
        authEntry = tk.Entry(
            authFrame,
            textvariable=self.commandedAuthority,
            font=('Arial', 12),
            width=10
        )
        authEntry.pack(side='right')
        
        authSlider = tk.Scale(
            frame,
            from_=0,
            to=20,
            orient='horizontal',
            variable=self.commandedAuthority,
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            length=500,
            width=20
        )
        authSlider.pack(pady=5)
        
        # Actual Velocity
        velFrame = tk.Frame(frame, bg='#34495e')
        velFrame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            velFrame,
            text="Actual Velocity (MPH):",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(side='left')
        
        velEntry = tk.Entry(
            velFrame,
            textvariable=self.actualVelocity,
            font=('Arial', 12),
            width=10
        )
        velEntry.pack(side='right')
        
        velSlider = tk.Scale(
            frame,
            from_=0,
            to=70,
            orient='horizontal',
            variable=self.actualVelocity,
            font=('Arial', 10),
            bg='#2ecc71',
            fg='white',
            length=500,
            width=20
        )
        velSlider.pack(pady=(5, 15))
    
    def _createFailureSection(self, parent):
        """Create failure signal controls"""
        frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3)
        frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            frame,
            text="Failure Signals (to Train Controller)",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white',
            pady=10
        ).pack()
        
        checkFrame = tk.Frame(frame, bg='#34495e')
        checkFrame.pack(pady=10)
        
        tk.Checkbutton(
            checkFrame,
            text="Passenger Emergency Signal",
            variable=self.passengerEmergency,
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            selectcolor='#e74c3c',
            activebackground='#34495e',
            activeforeground='white'
        ).pack(anchor='w', pady=5, padx=20)
        
        tk.Checkbutton(
            checkFrame,
            text="Brake Failure",
            variable=self.brakeFailure,
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            selectcolor='#e67e22',
            activebackground='#34495e',
            activeforeground='white'
        ).pack(anchor='w', pady=5, padx=20)
        
        tk.Checkbutton(
            checkFrame,
            text="Train Engine Failure",
            variable=self.engineFailure,
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            selectcolor='#f39c12',
            activebackground='#34495e',
            activeforeground='white'
        ).pack(anchor='w', pady=5, padx=20)
        
        tk.Checkbutton(
            checkFrame,
            text="Signal Pickup Failure",
            variable=self.signalFailure,
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            selectcolor='#9b59b6',
            activebackground='#34495e',
            activeforeground='white'
        ).pack(anchor='w', pady=5, padx=20)
    
    def _createControlSection(self, parent):
        """Create control buttons"""
        frame = tk.Frame(parent, bg='#2c3e50')
        frame.pack(fill='x', pady=(0, 10))
        
        # Auto-send toggle
        autoFrame = tk.Frame(frame, bg='#2c3e50')
        autoFrame.pack(pady=10)
        
        tk.Checkbutton(
            autoFrame,
            text="Auto-send updates every 2 seconds",
            variable=self.auto_send,
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white',
            selectcolor='#27ae60',
            activebackground='#2c3e50',
            activeforeground='white'
        ).pack()
        
        # Send buttons
        buttonFrame = tk.Frame(frame, bg='#2c3e50')
        buttonFrame.pack(pady=10)
        
        tk.Button(
            buttonFrame,
            text="SEND ALL VALUES NOW",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            command=self._sendAllValues,
            width=25,
            height=2
        ).pack(pady=5)
        
        tk.Button(
            buttonFrame,
            text="Send Speed Only",
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            command=self._sendSpeedOnly,
            width=25,
            height=1
        ).pack(pady=5)
        
        tk.Button(
            buttonFrame,
            text="Send Authority Only",
            font=('Arial', 12),
            bg='#9b59b6',
            fg='white',
            activebackground='#8e44ad',
            command=self._sendAuthorityOnly,
            width=25,
            height=1
        ).pack(pady=5)
        
        tk.Button(
            buttonFrame,
            text="Send Failures Only",
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            command=self._sendFailuresOnly,
            width=25,
            height=1
        ).pack(pady=5)
    
    def _sendMessage(self, command, value):
        """Send a message to Train Controller HW"""
        if self.server:
            try:
                message = {
                    'command': command,
                    'value': value
                }
                self.server.send_to_ui("Train Controller HW", message)
                print(f"✓ Sent: {command} = {value}")
                
                # Update connection status
                if not self.connected:
                    self.connected = True
                    self.connectionLabel.config(
                        text="✓ Connected to Train Controller HW",
                        bg='#27ae60'
                    )
            except Exception as e:
                print(f"✗ Error sending: {e}")
                self.connected = False
                self.connectionLabel.config(
                    text="✗ Train Controller HW Disconnected",
                    bg='#e74c3c'
                )
    
    def _sendSpeedOnly(self):
        """Send commanded speed"""
        self._sendMessage('Commanded Speed', self.commandedSpeed.get())
    
    def _sendAuthorityOnly(self):
        """Send commanded authority"""
        self._sendMessage('Commanded Authority', self.commandedAuthority.get())
    
    def _sendFailuresOnly(self):
        """Send all failure signals"""
        self._sendMessage('Passenger Emergency Signal', self.passengerEmergency.get())
        self._sendMessage('Brake Failure', self.brakeFailure.get())
        self._sendMessage('Train Engine Failure', self.engineFailure.get())
        self._sendMessage('Signal Pickup Failure', self.signalFailure.get())
    
    def _sendAllValues(self):
        """Send all values to Train Controller HW"""
        # Send speed and authority
        self._sendMessage('Commanded Speed', self.commandedSpeed.get())
        self._sendMessage('Commanded Authority', self.commandedAuthority.get())
        self._sendMessage('Actual Velocity', self.actualVelocity.get())
        
        # Send failure signals
        self._sendMessage('Passenger Emergency Signal', self.passengerEmergency.get())
        self._sendMessage('Brake Failure', self.brakeFailure.get())
        self._sendMessage('Train Engine Failure', self.engineFailure.get())
        self._sendMessage('Signal Pickup Failure', self.signalFailure.get())
        
        print("=" * 50)
        print("Sent all values to Train Controller HW")
        print("=" * 50)
    
    def _autoSendLoop(self):
        """Automatically send updates if auto-send is enabled"""
        if self.auto_send.get():
            self._sendAllValues()
        
        # Schedule next auto-send
        self.root.after(2000, self._autoSendLoop)
    
    def _onClose(self):
        """Clean up on close"""
        print("\nClosing Test Train Model...")
        if self.server:
            self.server.stop_server()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        print("=" * 50)
        print("Test Train Model Started")
        print("=" * 50)
        print("Controls:")
        print("  - Adjust sliders or type values")
        print("  - Click 'SEND ALL VALUES NOW' to send")
        print("  - Or enable 'Auto-send' for continuous updates")
        print("=" * 50)
        
        self.root.mainloop()

if __name__ == "__main__":
    app = TestTrainModel()
    app.run()