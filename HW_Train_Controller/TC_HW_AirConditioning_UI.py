import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class ACSystemPanel:
    def __init__(self, root, send_message_callback=None):
        self.root = root
        self.root.title("A/C SYSTEM PANEL")
        self.root.geometry("500x750")
        self.root.configure(bg='#2c3e50')
        
        self.send_message_callback = send_message_callback
        self.currentTemp = tk.DoubleVar(value=72.0)
        self.targetTemp = tk.DoubleVar(value=70.0)
        self.systemOn = tk.BooleanVar(value=False)
        
        self._createWidgets()
        self._updateTime()
        self._updateStatus()
        
    def setCurrentTemperature(self, temp):
        self.currentTemp.set(temp)
        self.currentTempLabel.config(text=f"{temp:.0f}°F")
        self._updateStatus()
        
    def _sendCommand(self):
        if self.send_message_callback and self.systemOn.get():
            msg = {
                'command': 'Temp',
                'value': self.targetTemp.get()
            }
            self.send_message_callback(msg)
        
    def _createWidgets(self):
        headerFrame = tk.Frame(self.root, bg='#34495e')
        headerFrame.pack(fill='x')
        
        headerLabel = tk.Label(
            headerFrame,
            text="A/C SYSTEM\nCONTROL PANEL",
            font=('Arial', 22, 'bold'),
            bg='#34495e',
            fg='white',
            pady=15
        )
        headerLabel.pack()
        
        timeFrame = tk.Frame(headerFrame, bg='#2c3e50', relief='raised', bd=3)
        timeFrame.pack(pady=(0, 10))
        
        self.timeLabel = tk.Label(
            timeFrame,
            text="",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white',
            padx=20,
            pady=8
        )
        self.timeLabel.pack()
        
        mainFrame = tk.Frame(self.root, bg='#2c3e50')
        mainFrame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self._createStatusSection(mainFrame)
        self._createCurrentTempSection(mainFrame)
        self._createTargetTempSection(mainFrame)
        self._createControlSection(mainFrame)
        
    def _createStatusSection(self, parent):
        statusFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4)
        statusFrame.pack(fill='x', pady=(0, 15))
        
        statusTitle = tk.Label(
            statusFrame,
            text="SYSTEM STATUS",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white',
            pady=8
        )
        statusTitle.pack()
        
        self.statusLabel = tk.Label(
            statusFrame,
            text="OFFLINE",
            font=('Arial', 24, 'bold'),
            bg='#7f8c8d',
            fg='white',
            relief='sunken',
            bd=3,
            pady=15
        )
        self.statusLabel.pack(fill='x', padx=15, pady=10)
        
    def _createCurrentTempSection(self, parent):
        tempFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4)
        tempFrame.pack(fill='x', pady=(0, 15))
        
        tempTitle = tk.Label(
            tempFrame,
            text="CURRENT CABIN TEMPERATURE",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='#3498db',
            pady=8
        )
        tempTitle.pack()
        
        self.currentTempLabel = tk.Label(
            tempFrame,
            text="72.0°F",
            font=('Arial', 42, 'bold'),
            bg='#2c3e50',
            fg='#e74c3c',
            relief='sunken',
            bd=3,
            pady=20
        )
        self.currentTempLabel.pack(fill='x', padx=15, pady=10)
        
    def _createTargetTempSection(self, parent):
        targetFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4)
        targetFrame.pack(fill='x', pady=(0, 15))
        
        targetTitle = tk.Label(
            targetFrame,
            text="TARGET TEMPERATURE",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='#3498db',
            pady=8
        )
        targetTitle.pack()
        
        self.targetTempLabel = tk.Label(
            targetFrame,
            text="70.0°F",
            font=('Arial', 32, 'bold'),
            bg='#2c3e50',
            fg='#2ecc71',
            relief='sunken',
            bd=3,
            pady=15
        )
        self.targetTempLabel.pack(fill='x', padx=15, pady=(10, 5))
        
        sliderFrame = tk.Frame(targetFrame, bg='#2c3e50')
        sliderFrame.pack(fill='x', padx=30, pady=(5, 10))
        
        tempSlider = tk.Scale(
            sliderFrame,
            from_=60,
            to=80,
            resolution=1.0,
            orient='horizontal',
            variable=self.targetTemp,
            command=self._onTargetTempChange,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            troughcolor='#34495e',
            relief='raised',
            bd=3,
            length=350,
            width=25,
            sliderlength=40,
            showvalue=0
        )
        tempSlider.pack()
        
        # Confirm button
        buttonFrame = tk.Frame(targetFrame, bg='#2c3e50')
        buttonFrame.pack(pady=(5, 15))
        
        self.confirmButton = tk.Button(
            buttonFrame,
            text="CONFIRM TEMPERATURE",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            relief='raised',
            bd=4,
            command=self._onConfirmTemp,
            width=20,
            height=2
        )
        self.confirmButton.pack()
        
    def _createControlSection(self, parent):
        controlFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4)
        controlFrame.pack(fill='x', pady=(0, 10))
        
        controlTitle = tk.Label(
            controlFrame,
            text="POWER CONTROL",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='#3498db',
            pady=8
        )
        controlTitle.pack()
        
        buttonFrame = tk.Frame(controlFrame, bg='#2c3e50')
        buttonFrame.pack(pady=15)
        
        self.powerButton = tk.Button(
            buttonFrame,
            text="TURN ON",
            font=('Arial', 20, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            relief='raised',
            bd=5,
            command=self._togglePower,
            width=15,
            height=2
        )
        self.powerButton.pack()
        
    def _onTargetTempChange(self, value):
        """Called when slider moves - only updates display, doesn't send command"""
        temp = float(value)
        self.targetTempLabel.config(text=f"{temp:.0f}°F")
        # Don't send command yet - wait for confirm button
        
    def _onConfirmTemp(self):
        """Called when user clicks CONFIRM button - sends command to Train Model"""
        temp = float(self.targetTemp.get())
        self.targetTempLabel.config(text=f"{temp:.0f}°F")
        self._updateStatus()
        self._sendCommand()
        print(f"Temperature confirmed: {temp}°F")
        
    def _togglePower(self):
        self.systemOn.set(not self.systemOn.get())
        
        if self.systemOn.get():
            self.powerButton.config(
                text="TURN OFF",
                bg='#e74c3c',
                activebackground='#c0392b'
            )
            print("A/C System: ONLINE")
            self._sendCommand()
        else:
            self.powerButton.config(
                text="TURN ON",
                bg='#27ae60',
                activebackground='#229954'
            )
            print("A/C System: OFFLINE")
            
        self._updateStatus()
        
    def _updateStatus(self):
        if self.systemOn.get():
            current = self.currentTemp.get()
            target = self.targetTemp.get()
            
            if abs(current - target) < 0.5:
                self.statusLabel.config(text="MAINTAINING", bg='#2ecc71')
            elif current > target:
                self.statusLabel.config(text="COOLING", bg='#3498db')
            else:
                self.statusLabel.config(text="HEATING", bg='#e67e22')
        else:
            self.statusLabel.config(text="OFFLINE", bg='#7f8c8d')
        
    def _updateTime(self):
        now = datetime.now()
        timeStr = now.strftime("%#m/%#d/%y %#I:%M %p") if os.name == 'nt' else now.strftime("%-m/%-d/%y %-I:%M %p")
        
        if hasattr(self, 'timeLabel'):
            self.timeLabel.config(text=timeStr)
            
        self.root.after(1000, self._updateTime)

if __name__ == "__main__":
    root = tk.Tk()
    app = ACSystemPanel(root)
    root.mainloop()