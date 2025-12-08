#!/usr/bin/env python3
"""
Train Control System - Power Engineer Control Panel
UI for configuring PI controller parameters (Kp, Ki) for both hardware and software versions

This panel has two tabs:
1. Hardware Train Control - Sets Kp/Ki for the TC_HW system (local)
2. Software Train Control - Sends Kp/Ki to the software version via socket
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class PowerEngineerPanel:
    """
    Power Engineer Control Panel with dual-tab interface for controlling
    both hardware and software train controller PI parameters.
    """
    
    def __init__(self, root, send_callback=None):
        """
        Initialize the Power Engineer Panel.
        
        Args:
            root: The main tkinter window
            send_callback: Callback function to send messages to software TC (format: callback(kp, ki))
        """
        self.root = root
        self.root.title("POWER ENGINEER CONTROL PANEL")
        self.root.geometry("900x800")
        self.root.configure(bg='#1a1a2e')
        self.send_callback = send_callback
        
        # Hardware PI Controller Parameters
        self.hw_kp = tk.DoubleVar(value=12.0)  # Proportional gain for hardware TC
        self.hw_ki = tk.DoubleVar(value=2.0)   # Integral gain for hardware TC
        
        # Software PI Controller Parameters (to send)
        self.sw_kp = tk.DoubleVar(value=10.0)
        self.sw_ki = tk.DoubleVar(value=2.0)
        
        # Speed values (for hardware display)
        self.currentSpeed = tk.DoubleVar(value=0.0)
        self.commandedSpeed = tk.DoubleVar(value=0.0)
        
        # Power values (for hardware)
        self.powerOutput = tk.DoubleVar(value=0.0)
        self.maxPower = tk.DoubleVar(value=120.0)
        
        # Error tracking (for hardware)
        self.speedError = tk.DoubleVar(value=0.0)
        self.integralError = tk.DoubleVar(value=0.0)
        
        # Control modes (for hardware)
        self.autoMode = tk.BooleanVar(value=True)
        self.manualPower = tk.DoubleVar(value=0.0)
        
        # Sample time
        self.sampleTime = 0.1
        
        self._createWidgets()
        self._updateTime()
        self._updatePowerCalculation()
        
    def setCurrentSpeed(self, speed):
        """Set the current train speed (hardware)."""
        self.currentSpeed.set(speed)
        self._updatePowerCalculation()
        
    def setCommandedSpeed(self, speed):
        """Set the commanded speed (hardware)."""
        self.commandedSpeed.set(speed)
        self._updatePowerCalculation()
        
    def getPowerOutput(self):
        """Get the current power output (hardware)."""
        return self.powerOutput.get()
    
    def getKp(self):
        """Get hardware Kp value."""
        return self.hw_kp.get()
    
    def getKi(self):
        """Get hardware Ki value."""
        return self.hw_ki.get()
    
    def updateDisplays(self):
        """Update all display labels to match current values."""
        self.kpLabel.config(text=f"{self.hw_kp.get():.1f}")
        self.kiLabel.config(text=f"{self.hw_ki.get():.2f}")
        self._updatePowerCalculation()
    
    def _createWidgets(self):
        """Create all UI widgets including tabbed interface."""
        # Header
        headerFrame = tk.Frame(self.root, bg='#16213e')
        headerFrame.pack(fill='x')
        
        headerLabel = tk.Label(
            headerFrame,
            text="POWER ENGINEER\nCONTROL PANEL",
            font=('Consolas', 22, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=15
        )
        headerLabel.pack()
        
        # Time display
        timeFrame = tk.Frame(headerFrame, bg='#0f3460', relief='raised', bd=3)
        timeFrame.pack(pady=(0, 10))
        
        self.timeLabel = tk.Label(
            timeFrame,
            text="",
            font=('Consolas', 14, 'bold'),
            bg='#0f3460',
            fg='white',
            padx=20,
            pady=8
        )
        self.timeLabel.pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Hardware Control
        self.hw_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.hw_tab, text="Hardware Train Control")
        self._createHardwareTab(self.hw_tab)
        
        # Tab 2: Software Control
        self.sw_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.sw_tab, text="Software Train Control")
        self._createSoftwareTab(self.sw_tab)
        
    def _createHardwareTab(self, parent):
        """Create the hardware control tab."""
        # Main content
        mainFrame = tk.Frame(parent, bg='#1a1a2e')
        mainFrame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Speed monitoring
        self._createSpeedDisplaySection(mainFrame)
        
        # PI Parameters
        self._createHardwarePISection(mainFrame)
        
        # Power output
        self._createPowerOutputSection(mainFrame)
        
        # Error display
        self._createErrorDisplaySection(mainFrame)
        
        # Control mode
        self._createControlModeSection(mainFrame)
        
    def _createSoftwareTab(self, parent):
        """Create the software control tab for sending Kp/Ki to software version."""
        mainFrame = tk.Frame(parent, bg='#1a1a2e')
        mainFrame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Info label
        infoFrame = tk.Frame(mainFrame, bg='#16213e', relief='raised', bd=4)
        infoFrame.pack(fill='x', pady=(0, 20))
        
        infoLabel = tk.Label(
            infoFrame,
            text="Configure PI Controller for Software Train Controller\n(Sends to port 12346)",
            font=('Consolas', 12, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=15
        )
        infoLabel.pack()
        
        # PI Parameters for software
        paramFrame = tk.Frame(mainFrame, bg='#16213e', relief='raised', bd=4)
        paramFrame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            paramFrame,
            text="SOFTWARE PI CONTROLLER PARAMETERS",
            font=('Consolas', 14, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=8
        )
        title.pack()
        
        paramsFrame = tk.Frame(paramFrame, bg='#0f3460')
        paramsFrame.pack(fill='x', padx=10, pady=10)
        
        # Kp for software
        sw_kpFrame = tk.Frame(paramsFrame, bg='#2c3e50', relief='sunken', bd=3)
        sw_kpFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            sw_kpFrame,
            text="Kp (PROPORTIONAL GAIN)",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#3498db',
            pady=5
        ).pack()
        
        self.sw_kpLabel = tk.Label(
            sw_kpFrame,
            text="10.0",
            font=('Consolas', 32, 'bold'),
            bg='#1a1a2e',
            fg='#3498db',
            relief='sunken',
            bd=2,
            pady=15
        )
        self.sw_kpLabel.pack(fill='x', padx=5, pady=5)
        
        self.sw_kpSlider = tk.Scale(
            sw_kpFrame,
            from_=0.0,
            to=20.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.sw_kp,
            command=self._onSwKpChange,
            font=('Consolas', 10),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            troughcolor='#34495e',
            relief='raised',
            bd=2,
            length=300
        )
        self.sw_kpSlider.pack(padx=10, pady=10)
        
        # Ki for software
        sw_kiFrame = tk.Frame(paramsFrame, bg='#2c3e50', relief='sunken', bd=3)
        sw_kiFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            sw_kiFrame,
            text="Ki (INTEGRAL GAIN)",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#e67e22',
            pady=5
        ).pack()
        
        self.sw_kiLabel = tk.Label(
            sw_kiFrame,
            text="2.0",
            font=('Consolas', 32, 'bold'),
            bg='#1a1a2e',
            fg='#e67e22',
            relief='sunken',
            bd=2,
            pady=15
        )
        self.sw_kiLabel.pack(fill='x', padx=5, pady=5)
        
        self.sw_kiSlider = tk.Scale(
            sw_kiFrame,
            from_=0.0,
            to=5.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.sw_ki,
            command=self._onSwKiChange,
            font=('Consolas', 10),
            bg='#e67e22',
            fg='white',
            activebackground='#d35400',
            troughcolor='#34495e',
            relief='raised',
            bd=2,
            length=300
        )
        self.sw_kiSlider.pack(padx=10, pady=10)
        
        # Send button
        sendFrame = tk.Frame(mainFrame, bg='#16213e', relief='raised', bd=4)
        sendFrame.pack(fill='x', pady=20)
        
        self.sendButton = tk.Button(
            sendFrame,
            text="SEND TO SOFTWARE CONTROLLER",
            font=('Consolas', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            relief='raised',
            bd=3,
            pady=15,
            command=self._sendToSoftware
        )
        self.sendButton.pack(padx=20, pady=20)
        
        # Status display
        self.sw_statusLabel = tk.Label(
            sendFrame,
            text="Ready to send parameters",
            font=('Consolas', 11),
            bg='#16213e',
            fg='#95a5a6',
            pady=10
        )
        self.sw_statusLabel.pack()
        
    def _onSwKpChange(self, value):
        """Update software Kp display."""
        kp = float(value)
        self.sw_kpLabel.config(text=f"{kp:.1f}")
        
    def _onSwKiChange(self, value):
        """Update software Ki display."""
        ki = float(value)
        self.sw_kiLabel.config(text=f"{ki:.1f}")
        
    def _sendToSoftware(self):
        """Send Kp and Ki to software train controller."""
        kp = self.sw_kp.get()
        ki = self.sw_ki.get()
        
        if self.send_callback:
            try:
                self.send_callback(kp, ki)
                self.sw_statusLabel.config(
                    text=f"✓ Sent: Kp={kp:.1f}, Ki={ki:.1f}",
                    fg='#27ae60'
                )
                print(f"Sent to Software TC: Kp={kp:.1f}, Ki={ki:.1f}")
                
                # Reset status after 3 seconds
                self.root.after(3000, lambda: self.sw_statusLabel.config(
                    text="Ready to send parameters",
                    fg='#95a5a6'
                ))
            except Exception as e:
                self.sw_statusLabel.config(
                    text=f"✗ Error: {str(e)}",
                    fg='#e74c3c'
                )
                print(f"Error sending to software: {e}")
        else:
            self.sw_statusLabel.config(
                text="✗ No connection callback configured",
                fg='#e74c3c'
            )
    
    def _createSpeedDisplaySection(self, parent):
        """Create speed monitoring display."""
        frame = tk.Frame(parent, bg='#16213e', relief='raised', bd=4)
        frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            frame,
            text="SPEED MONITORING",
            font=('Consolas', 14, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=8
        )
        title.pack()
        
        speedGrid = tk.Frame(frame, bg='#0f3460')
        speedGrid.pack(fill='x', padx=10, pady=10)
        
        # Current Speed
        currentFrame = tk.Frame(speedGrid, bg='#2c3e50', relief='sunken', bd=3)
        currentFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            currentFrame,
            text="CURRENT SPEED",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#3498db',
            pady=5
        ).pack()
        
        self.currentSpeedLabel = tk.Label(
            currentFrame,
            text="0.0 mph",
            font=('Consolas', 32, 'bold'),
            bg='#1a1a2e',
            fg='#3498db',
            relief='sunken',
            bd=2,
            pady=15
        )
        self.currentSpeedLabel.pack(fill='x', padx=5, pady=5)
        
        # Commanded Speed
        commandFrame = tk.Frame(speedGrid, bg='#2c3e50', relief='sunken', bd=3)
        commandFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            commandFrame,
            text="COMMANDED SPEED",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#e67e22',
            pady=5
        ).pack()
        
        self.commandedSpeedLabel = tk.Label(
            commandFrame,
            text="0.0 mph",
            font=('Consolas', 32, 'bold'),
            bg='#1a1a2e',
            fg='#e67e22',
            relief='sunken',
            bd=2,
            pady=15
        )
        self.commandedSpeedLabel.pack(fill='x', padx=5, pady=5)
        
    def _createHardwarePISection(self, parent):
        """Create hardware PI parameter section."""
        frame = tk.Frame(parent, bg='#16213e', relief='raised', bd=4)
        frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            frame,
            text="HARDWARE PI CONTROLLER PARAMETERS",
            font=('Consolas', 14, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=8
        )
        title.pack()
        
        paramsFrame = tk.Frame(frame, bg='#0f3460')
        paramsFrame.pack(fill='x', padx=10, pady=10)
        
        # Kp
        kpFrame = tk.Frame(paramsFrame, bg='#2c3e50', relief='sunken', bd=3)
        kpFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            kpFrame,
            text="Kp (PROPORTIONAL GAIN)",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#3498db',
            pady=5
        ).pack()
        
        self.kpLabel = tk.Label(
            kpFrame,
            text="12.0",
            font=('Consolas', 32, 'bold'),
            bg='#1a1a2e',
            fg='#3498db',
            relief='sunken',
            bd=2,
            pady=15
        )
        self.kpLabel.pack(fill='x', padx=5, pady=5)
        
        self.kpSlider = tk.Scale(
            kpFrame,
            from_=0.0,
            to=20.0,
            resolution=0.1,
            orient='horizontal',
            variable=self.hw_kp,
            command=self._onKpChange,
            font=('Consolas', 10),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            troughcolor='#34495e',
            relief='raised',
            bd=2,
            length=300
        )
        self.kpSlider.pack(padx=10, pady=10)
        
        # Ki
        kiFrame = tk.Frame(paramsFrame, bg='#2c3e50', relief='sunken', bd=3)
        kiFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            kiFrame,
            text="Ki (INTEGRAL GAIN)",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#e67e22',
            pady=5
        ).pack()
        
        self.kiLabel = tk.Label(
            kiFrame,
            text="2.00",
            font=('Consolas', 32, 'bold'),
            bg='#1a1a2e',
            fg='#e67e22',
            relief='sunken',
            bd=2,
            pady=15
        )
        self.kiLabel.pack(fill='x', padx=5, pady=5)
        
        self.kiSlider = tk.Scale(
            kiFrame,
            from_=0.0,
            to=5.0,
            resolution=0.01,
            orient='horizontal',
            variable=self.hw_ki,
            command=self._onKiChange,
            font=('Consolas', 10),
            bg='#e67e22',
            fg='white',
            activebackground='#d35400',
            troughcolor='#34495e',
            relief='raised',
            bd=2,
            length=300
        )
        self.kiSlider.pack(padx=10, pady=10)
        
    def _createPowerOutputSection(self, parent):
        """Create power output display."""
        frame = tk.Frame(parent, bg='#16213e', relief='raised', bd=4)
        frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            frame,
            text="POWER OUTPUT",
            font=('Consolas', 14, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=8
        )
        title.pack()
        
        powerFrame = tk.Frame(frame, bg='#0f3460')
        powerFrame.pack(fill='x', padx=10, pady=10)
        
        self.powerOutputLabel = tk.Label(
            powerFrame,
            text="0.0 kW",
            font=('Consolas', 36, 'bold'),
            bg='#1a1a2e',
            fg='#27ae60',
            relief='sunken',
            bd=3,
            pady=20
        )
        self.powerOutputLabel.pack(fill='x', padx=10, pady=(10, 5))
        
        self.powerBarCanvas = tk.Canvas(
            powerFrame,
            height=30,
            bg='#34495e',
            relief='sunken',
            bd=2
        )
        self.powerBarCanvas.pack(fill='x', padx=10, pady=(5, 10))
        
    def _createErrorDisplaySection(self, parent):
        """Create error display section."""
        frame = tk.Frame(parent, bg='#16213e', relief='raised', bd=4)
        frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            frame,
            text="ERROR TRACKING",
            font=('Consolas', 14, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=8
        )
        title.pack()
        
        errorFrame = tk.Frame(frame, bg='#0f3460')
        errorFrame.pack(fill='x', padx=10, pady=10)
        
        # Speed Error
        speedErrorFrame = tk.Frame(errorFrame, bg='#2c3e50', relief='sunken', bd=3)
        speedErrorFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            speedErrorFrame,
            text="SPEED ERROR",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#f39c12',
            pady=5
        ).pack()
        
        self.speedErrorLabel = tk.Label(
            speedErrorFrame,
            text="+0.0 mph",
            font=('Consolas', 24, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12',
            relief='sunken',
            bd=2,
            pady=10
        )
        self.speedErrorLabel.pack(fill='x', padx=5, pady=5)
        
        # Integral Error
        integralErrorFrame = tk.Frame(errorFrame, bg='#2c3e50', relief='sunken', bd=3)
        integralErrorFrame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(
            integralErrorFrame,
            text="INTEGRAL ERROR",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#9b59b6',
            pady=5
        ).pack()
        
        self.integralErrorLabel = tk.Label(
            integralErrorFrame,
            text="+0.00",
            font=('Consolas', 24, 'bold'),
            bg='#1a1a2e',
            fg='#9b59b6',
            relief='sunken',
            bd=2,
            pady=10
        )
        self.integralErrorLabel.pack(fill='x', padx=5, pady=5)
        
        # Reset button
        resetButton = tk.Button(
            integralErrorFrame,
            text="RESET",
            font=('Consolas', 10, 'bold'),
            bg='#c0392b',
            fg='white',
            activebackground='#a93226',
            command=self._resetIntegralError,
            relief='raised',
            bd=2
        )
        resetButton.pack(pady=5)
        
    def _createControlModeSection(self, parent):
        """Create control mode section."""
        frame = tk.Frame(parent, bg='#16213e', relief='raised', bd=4)
        frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            frame,
            text="CONTROL MODE",
            font=('Consolas', 14, 'bold'),
            bg='#16213e',
            fg='#00ff00',
            pady=8
        )
        title.pack()
        
        self.modeButton = tk.Button(
            frame,
            text="AUTO MODE (PI CONTROL)",
            font=('Consolas', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            relief='raised',
            bd=3,
            pady=10,
            command=self._toggleMode
        )
        self.modeButton.pack(padx=20, pady=10)
        
        manualFrame = tk.Frame(frame, bg='#2c3e50', relief='sunken', bd=3)
        manualFrame.pack(fill='x', padx=10, pady=(5, 10))
        
        tk.Label(
            manualFrame,
            text="MANUAL POWER OVERRIDE",
            font=('Consolas', 11, 'bold'),
            bg='#2c3e50',
            fg='#95a5a6',
            pady=5
        ).pack()
        
        self.manualPowerSlider = tk.Scale(
            manualFrame,
            from_=0.0,
            to=120.0,
            resolution=1.0,
            orient='horizontal',
            variable=self.manualPower,
            command=self._onManualPowerChange,
            font=('Consolas', 10),
            bg='#7f8c8d',
            fg='white',
            activebackground='#636e72',
            troughcolor='#34495e',
            relief='raised',
            bd=2,
            length=700,
            state='disabled'
        )
        self.manualPowerSlider.pack(padx=10, pady=10)
        
    def _onKpChange(self, value):
        """Update hardware Kp display."""
        kp = float(value)
        self.kpLabel.config(text=f"{kp:.1f}")
        self._updatePowerCalculation()
        
    def _onKiChange(self, value):
        """Update hardware Ki display."""
        ki = float(value)
        self.kiLabel.config(text=f"{ki:.2f}")
        self._updatePowerCalculation()
        
    def _onManualPowerChange(self, value):
        """Update manual power."""
        if not self.autoMode.get():
            self.powerOutput.set(float(value))
            self._updatePowerDisplay()
        
    def _toggleMode(self):
        """Toggle control mode."""
        self.autoMode.set(not self.autoMode.get())
        
        if self.autoMode.get():
            self.modeButton.config(
                text="AUTO MODE (PI CONTROL)",
                bg='#27ae60',
                activebackground='#229954'
            )
            self.manualPowerSlider.config(state='disabled', bg='#7f8c8d')
        else:
            self.modeButton.config(
                text="MANUAL MODE (OVERRIDE)",
                bg='#e74c3c',
                activebackground='#c0392b'
            )
            self.manualPowerSlider.config(state='normal', bg='#e67e22')
        
        self._updatePowerCalculation()
        
    def _resetIntegralError(self):
        """Reset integral error."""
        self.integralError.set(0.0)
        self.integralErrorLabel.config(text="0.0")
        self._updatePowerCalculation()
        
    def _updatePowerCalculation(self):
        """Calculate power using PI controller."""
        if not self.autoMode.get():
            self._updatePowerDisplay()
            return
        
        # Initialize cache on first run
        if not hasattr(self, '_power_calc_cache'):
            self._power_calc_cache = {
                'current': None,
                'commanded': None,
                'error': None,
                'integral': None,
                'power': None
            }
        
        cache = self._power_calc_cache
        
        current = self.currentSpeed.get()
        commanded = self.commandedSpeed.get()
        kp = self.hw_kp.get()
        ki = self.hw_ki.get()
        maxPower = self.maxPower.get()
        
        error = commanded - current
        self.speedError.set(error)
        
        # Only update labels if changed significantly (reduce visual jitter and redraws)
        if cache['error'] is None or abs(error - cache['error']) > 0.05:
            self.speedErrorLabel.config(text=f"{error:+.1f} mph")
            cache['error'] = error
        
        if cache['current'] is None or abs(current - cache['current']) > 0.05:
            self.currentSpeedLabel.config(text=f"{current:.1f} mph")
            cache['current'] = current
        
        if cache['commanded'] is None or abs(commanded - cache['commanded']) > 0.05:
            self.commandedSpeedLabel.config(text=f"{commanded:.1f} mph")
            cache['commanded'] = commanded
        
        integral = self.integralError.get()
        integral += error * self.sampleTime
        
        maxIntegral = maxPower / (ki if ki > 0 else 1.0)
        integral = max(-maxIntegral, min(maxIntegral, integral))
        
        self.integralError.set(integral)
        
        if cache['integral'] is None or abs(integral - cache['integral']) > 0.01:
            self.integralErrorLabel.config(text=f"{integral:+.2f}")
            cache['integral'] = integral
        
        pTerm = kp * error
        iTerm = ki * integral
        power = pTerm + iTerm
        
        power = max(0.0, min(maxPower, power))
        
        self.powerOutput.set(power)
        
        # Only update power display if changed significantly (> 0.5 kW to reduce canvas redraws)
        if cache['power'] is None or abs(power - cache['power']) > 0.5:
            self._updatePowerDisplay()
            cache['power'] = power
        
        # Increased from 100ms to 150ms to reduce CPU load
        self.root.after(100, self._updatePowerCalculation)
        
    def _updatePowerDisplay(self):
        """Update power display."""
        power = self.powerOutput.get()
        maxPower = self.maxPower.get()
        
        self.powerOutputLabel.config(text=f"{power:.1f} kW")
        
        self.powerBarCanvas.delete('all')
        canvasWidth = self.powerBarCanvas.winfo_width()
        if canvasWidth <= 1:
            canvasWidth = 800
        
        canvasHeight = 30
        
        barWidth = (power / maxPower) * (canvasWidth - 10) if maxPower > 0 else 0
        
        if power < maxPower * 0.5:
            color = '#27ae60'
        elif power < maxPower * 0.8:
            color = '#f1c40f'
        else:
            color = '#e74c3c'
        
        self.powerBarCanvas.create_rectangle(
            5, 5, barWidth + 5, canvasHeight - 5,
            fill=color,
            outline=''
        )
        
        percentage = (power / maxPower * 100) if maxPower > 0 else 0
        self.powerBarCanvas.create_text(
            canvasWidth / 2, canvasHeight / 2,
            text=f"{percentage:.1f}%",
            font=('Consolas', 12, 'bold'),
            fill='white'
        )
        
    def _updateTime(self):
        """Update time display."""
        now = datetime.now()
        timeStr = now.strftime("%#m/%#d/%y %#I:%M:%S %p") if os.name == 'nt' else now.strftime("%-m/%-d/%y %-I:%M:%S %p")
        
        if hasattr(self, 'timeLabel'):
            self.timeLabel.config(text=timeStr)
            
        self.root.after(1000, self._updateTime)