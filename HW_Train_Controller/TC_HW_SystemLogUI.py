#!/usr/bin/env python3
"""
Train Control System - System Log Viewer
Displays Raspberry Pi GPIO Server logs in an attractive Windows UI

This connects to the GPIO server and displays all system events,
button presses, and state changes in real-time.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import json
import threading
from datetime import datetime
from pathlib import Path

# Configuration
PI_HOST = '192.168.1.179'  # ← CHANGE THIS to your Pi's IP
PI_GPIO_PORT = 12348

class SystemLogViewer:
    """Attractive system log viewer for GPIO server events"""
    
    def __init__(self, root, gpio_client=None):
        """
        Initialize the log viewer.
        
        Args:
            root: Tkinter root or Toplevel window
            gpio_client: Optional existing GPIO client connection (from main UI)
        """
        self.root = root
        self.root.title("TRAIN CONTROL SYSTEM LOG")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a2e')
        
        # GPIO Client
        self.external_gpio_client = gpio_client  # Use shared client if provided
        self.gpio_client = None
        self.connected = False
        self.last_state = {}
        
        # Log categories
        self.log_filters = {
            'doors': tk.BooleanVar(value=True),
            'lights': tk.BooleanVar(value=True),
            'brakes': tk.BooleanVar(value=True),
            'speed': tk.BooleanVar(value=True),
            'system': tk.BooleanVar(value=True)
        }
        
        self._createWidgets()
        
        # If no external client provided, create our own connection
        if self.external_gpio_client is None:
            self._connectToGPIOServer()
        else:
            # Use the shared client's state updates
            self.connected = True
            self._updateConnectionStatus(True)
            self._addLogEntry("✓ Using shared GPIO connection", 'system')
        
        # Don't set close protocol if this is a Toplevel (main UI handles it)
        if isinstance(root, tk.Tk):
            self.root.protocol("WM_DELETE_WINDOW", self._onClose)
    
    def _createWidgets(self):
        """Create all UI widgets"""
        # Header
        headerFrame = tk.Frame(self.root, bg='#16213e')
        headerFrame.pack(fill='x')
        
        headerLabel = tk.Label(
            headerFrame,
            text="SYSTEM LOG VIEWER",
            font=('Consolas', 24, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=15
        )
        headerLabel.pack()
        
        # Connection status
        statusFrame = tk.Frame(headerFrame, bg='#16213e')
        statusFrame.pack(fill='x', pady=(0, 10))
        
        self.connectionLabel = tk.Label(
            statusFrame,
            text="● Connecting to GPIO Server...",
            font=('Consolas', 11),
            bg='#e67e22',
            fg='white',
            pady=5
        )
        self.connectionLabel.pack(fill='x')
        
        # Control bar
        controlFrame = tk.Frame(self.root, bg='#0f3460', relief='raised', bd=2)
        controlFrame.pack(fill='x', padx=5, pady=5)
        
        # Filter controls
        filterLabel = tk.Label(
            controlFrame,
            text="FILTERS:",
            font=('Consolas', 10, 'bold'),
            bg='#0f3460',
            fg='#00ff00'
        )
        filterLabel.pack(side='left', padx=(10, 5))
        
        filters = [
            ('Doors', 'doors', '#3498db'),
            ('Lights', 'lights', '#f1c40f'),
            ('Brakes', 'brakes', '#e74c3c'),
            ('Speed', 'speed', '#9b59b6'),
            ('System', 'system', '#95a5a6')
        ]
        
        for label, key, color in filters:
            cb = tk.Checkbutton(
                controlFrame,
                text=label,
                variable=self.log_filters[key],
                font=('Consolas', 9),
                bg='#0f3460',
                fg=color,
                selectcolor='#1a1a2e',
                activebackground='#0f3460',
                activeforeground=color,
                relief='flat'
            )
            cb.pack(side='left', padx=5)
        
        # Clear button
        clearBtn = tk.Button(
            controlFrame,
            text="CLEAR LOG",
            font=('Consolas', 9, 'bold'),
            bg='#c0392b',
            fg='white',
            activebackground='#922b21',
            command=self._clearLog,
            relief='raised',
            bd=2,
            padx=10
        )
        clearBtn.pack(side='right', padx=10)
        
        # Stats display
        statsFrame = tk.Frame(self.root, bg='#0f3460', relief='sunken', bd=2)
        statsFrame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.statsLabel = tk.Label(
            statsFrame,
            text="Events: 0 | Last Update: --:--:--",
            font=('Consolas', 9),
            bg='#0f3460',
            fg='#95a5a6',
            anchor='w',
            padx=10,
            pady=3
        )
        self.statsLabel.pack(fill='x')
        
        # Main log display
        logFrame = tk.Frame(self.root, bg='#1a1a2e', relief='sunken', bd=3)
        logFrame.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        # Create scrolled text widget with custom styling
        self.logText = scrolledtext.ScrolledText(
            logFrame,
            font=('Consolas', 10),
            bg='#0f0f0f',
            fg='#00ff00',
            insertbackground='#00ff00',
            relief='flat',
            wrap='word',
            state='disabled',
            padx=10,
            pady=10
        )
        self.logText.pack(fill='both', expand=True)
        
        # Configure text tags for different log types
        self.logText.tag_config('timestamp', foreground='#95a5a6')
        self.logText.tag_config('doors', foreground='#3498db', font=('Consolas', 10, 'bold'))
        self.logText.tag_config('lights', foreground='#f1c40f', font=('Consolas', 10, 'bold'))
        self.logText.tag_config('brakes', foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        self.logText.tag_config('speed', foreground='#9b59b6', font=('Consolas', 10, 'bold'))
        self.logText.tag_config('system', foreground='#2ecc71', font=('Consolas', 10, 'bold'))
        self.logText.tag_config('error', foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        self.logText.tag_config('info', foreground='#00ff00')
        self.logText.tag_config('value', foreground='#ffffff', font=('Consolas', 10, 'bold'))
        
        # Event counter
        self.event_count = 0
        
        # Add initial welcome message
        self._addLogEntry("System Log Viewer started", 'system')
        if self.external_gpio_client is None:
            self._addLogEntry(f"Connecting to GPIO Server at {PI_HOST}:{PI_GPIO_PORT}", 'system')
    
    def handleStateUpdate(self, new_state):
        """
        Public method to receive state updates from external GPIO client.
        This allows the main UI to pass state updates to the log viewer.
        """
        if not self.last_state:
            # First state update
            self.last_state = new_state
            return
        
        self._handleStateUpdate(new_state)
    
    def _connectToGPIOServer(self):
        """Connect to GPIO server"""
        def connect_thread():
            try:
                self.gpio_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.gpio_client.settimeout(5.0)
                self.gpio_client.connect((PI_HOST, PI_GPIO_PORT))
                self.connected = True
                
                self.root.after(0, lambda: self._updateConnectionStatus(True))
                self.root.after(0, lambda: self._addLogEntry("✓ Connected to GPIO Server", 'system'))
                
                # Start receive thread
                receive_thread = threading.Thread(target=self._receiveLoop, daemon=True)
                receive_thread.start()
            
            except Exception as e:
                self.root.after(0, lambda: self._updateConnectionStatus(False))
                self.root.after(0, lambda: self._addLogEntry(f"✗ Connection failed: {e}", 'error'))
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def _receiveLoop(self):
        """Receive messages from GPIO server"""
        buffer = ""
        while self.connected:
            try:
                data = self.gpio_client.recv(4096).decode('utf-8')
                if not data:
                    self.root.after(0, lambda: self._addLogEntry("GPIO Server disconnected", 'error'))
                    self.connected = False
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self._processMessage(line)
            
            except socket.timeout:
                continue
            except Exception as e:
                self.root.after(0, lambda: self._addLogEntry(f"Receive error: {e}", 'error'))
                self.connected = False
                break
    
    def _processMessage(self, message_str):
        """Process message from GPIO server"""
        try:
            message = json.loads(message_str)
            msg_type = message.get('type')
            
            if msg_type == 'state_update':
                state = message.get('data', {})
                self._handleStateUpdate(state)
            
            elif msg_type == 'log_message':
                # NEW: Handle log messages from Pi
                log_message = message.get('message', '')
                category = message.get('category', 'system')
                
                # Check if this category is enabled
                if category in self.log_filters and self.log_filters[category].get():
                    self.root.after(0, lambda m=log_message, c=category: self._addLogEntry(m, c))
        
        except json.JSONDecodeError:
            pass  # Ignore invalid JSON
    
    def handleLogMessage(self, message, category='system'):
        """
        Public method to receive log messages from external GPIO client.
        This allows the main UI to pass log messages to the log viewer.
        """
        if category in self.log_filters and self.log_filters[category].get():
            self._addLogEntry(message, category)
    
    def _handleStateUpdate(self, new_state):
        """Handle state update and log changes"""
        if not self.last_state:
            # First state update
            self.last_state = new_state
            return
        
        # Check for changes and log them
        changes = []
        
        # Doors
        if new_state.get('leftDoorOpen') != self.last_state.get('leftDoorOpen'):
            status = "OPEN" if new_state['leftDoorOpen'] else "CLOSED"
            changes.append(('doors', f"Left Door: {status}"))
        
        if new_state.get('rightDoorOpen') != self.last_state.get('rightDoorOpen'):
            status = "OPEN" if new_state['rightDoorOpen'] else "CLOSED"
            changes.append(('doors', f"Right Door: {status}"))
        
        # Lights
        if new_state.get('headlightsOn') != self.last_state.get('headlightsOn'):
            status = "ON" if new_state['headlightsOn'] else "OFF"
            changes.append(('lights', f"Headlights: {status}"))
        
        if new_state.get('interiorLightsOn') != self.last_state.get('interiorLightsOn'):
            status = "ON" if new_state['interiorLightsOn'] else "OFF"
            changes.append(('lights', f"Interior Lights: {status}"))
        
        # Brakes
        if new_state.get('serviceBrakeActive') != self.last_state.get('serviceBrakeActive'):
            status = "ENGAGED" if new_state['serviceBrakeActive'] else "RELEASED"
            changes.append(('brakes', f"Service Brake: {status}"))
        
        if new_state.get('emergencyBrakeEngaged') != self.last_state.get('emergencyBrakeEngaged'):
            status = "🚨 ENGAGED 🚨" if new_state['emergencyBrakeEngaged'] else "RELEASED"
            changes.append(('brakes', f"Emergency Brake: {status}"))
        
        if new_state.get('trainHornActive') != self.last_state.get('trainHornActive'):
            status = "SOUNDING" if new_state['trainHornActive'] else "OFF"
            changes.append(('brakes', f"Train Horn: {status}"))
        
        # Drivetrain & Speed
        if new_state.get('drivetrainManualMode') != self.last_state.get('drivetrainManualMode'):
            mode = "MANUAL" if new_state['drivetrainManualMode'] else "AUTOMATIC"
            changes.append(('speed', f"Drivetrain Mode: {mode}"))
        
        if new_state.get('manualSetpointSpeed') != self.last_state.get('manualSetpointSpeed'):
            speed = new_state['manualSetpointSpeed']
            changes.append(('speed', f"Manual Setpoint: {speed} MPH"))
        
        # Log all changes
        for category, message in changes:
            if self.log_filters[category].get():
                self.root.after(0, lambda m=message, c=category: self._addLogEntry(m, c))
        
        # Update last state
        self.last_state = new_state
    
    def _addLogEntry(self, message, category='info'):
        """Add entry to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.logText.config(state='normal')
        
        # Add timestamp
        self.logText.insert('end', f"[{timestamp}] ", 'timestamp')
        
        # Add category indicator
        category_symbols = {
            'doors': '🚪',
            'lights': '💡',
            'brakes': '🛑',
            'speed': '⚡',
            'system': '⚙️',
            'error': '❌'
        }
        
        symbol = category_symbols.get(category, '•')
        self.logText.insert('end', f"{symbol} ", category)
        
        # Add message
        self.logText.insert('end', f"{message}\n", category)
        
        # Scroll to end
        self.logText.see('end')
        
        self.logText.config(state='disabled')
        
        # Update stats
        self.event_count += 1
        self._updateStats(timestamp)
    
    def _updateStats(self, timestamp):
        """Update statistics display"""
        self.statsLabel.config(
            text=f"Events: {self.event_count} | Last Update: {timestamp}"
        )
    
    def _clearLog(self):
        """Clear the log display"""
        self.logText.config(state='normal')
        self.logText.delete('1.0', 'end')
        self.logText.config(state='disabled')
        
        self.event_count = 0
        self._addLogEntry("Log cleared", 'system')
    
    def _updateConnectionStatus(self, connected):
        """Update connection status display"""
        if connected:
            self.connectionLabel.config(
                text=f"● Connected to GPIO Server ({PI_HOST}:{PI_GPIO_PORT})",
                bg='#27ae60'
            )
        else:
            self.connectionLabel.config(
                text=f"● Disconnected from GPIO Server",
                bg='#e74c3c'
            )
    
    def _onClose(self):
        """Clean up on window close"""
        print("\nClosing System Log Viewer...")
        self.connected = False
        
        if self.gpio_client:
            try:
                self.gpio_client.close()
            except:
                pass
        
        self.root.destroy()

def main():
    """Main entry point"""
    print("=" * 60)
    print("TRAIN CONTROL SYSTEM - System Log Viewer")
    print("=" * 60)
    print(f"GPIO Server: {PI_HOST}:{PI_GPIO_PORT}")
    print("=" * 60)
    
    root = tk.Tk()
    app = SystemLogViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()