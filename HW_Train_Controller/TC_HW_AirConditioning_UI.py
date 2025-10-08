import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class ACSystemPanel:
	# UI panel for train cabin air conditioning system.
	
	"""
	Attributes:
		root: The main tkinter window
		currentTemp: DoubleVar holding the current cabin temperature
		targetTemp: DoubleVar holding the target temperature setting
		systemOn: BooleanVar indicating if AC system is on or off
		currentTempLabel: Label displaying current temperature
		targetTempLabel: Label displaying target temperature
		statusLabel: Label displaying system status
		powerButton: Button to toggle AC system power
		timeLabel: Label showing current time
	"""
	
	def __init__(self, root):
		# Initializes the AC system panel.
		self.root = root
		self.root.title("A/C SYSTEM PANEL")
		self.root.geometry("500x750")
		self.root.configure(bg='#2c3e50')
		
		self.currentTemp = tk.DoubleVar(value=72.0)
		self.targetTemp = tk.DoubleVar(value=70.0)
		self.systemOn = tk.BooleanVar(value=False)
		
		self._createWidgets()
		self._updateTime()
		self._updateStatus()
		
	def setCurrentTemperature(self, temp):
		# Sets the current cabin temperature from sensor.
		self.currentTemp.set(temp)
		self._updateStatus()
		
	def _createWidgets(self):
		# Creates all UI widgets for the panel.
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
		# Creates the system status display section.
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
		# Creates the current temperature display section.
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
			# In full simulation will be inputted from Train Model.
			font=('Arial', 42, 'bold'),
			bg='#2c3e50',
			fg='#e74c3c',
			relief='sunken',
			bd=3,
			pady=20
		)
		self.currentTempLabel.pack(fill='x', padx=15, pady=10)
		
	def _createTargetTempSection(self, parent):
		# Creates the target temperature control section.
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
		sliderFrame.pack(fill='x', padx=30, pady=(5, 15))
		
		tempSlider = tk.Scale(
			sliderFrame,
			from_=60,
			to=80,
			resolution=0.5,
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
		
	def _createControlSection(self, parent):
		# Creates the power control section.
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
		# Updates target temperature display when slider changes.
		temp = float(value)
		self.targetTempLabel.config(text=f"{temp:.1f}°F")
		self._updateStatus()
		
	def _togglePower(self):
		# Toggles the AC system power on or off.
		self.systemOn.set(not self.systemOn.get())
		
		if self.systemOn.get():
			self.powerButton.config(
				text="TURN OFF",
				bg='#e74c3c',
				activebackground='#c0392b'
			)
			print("A/C System: ONLINE")
		else:
			self.powerButton.config(
				text="TURN ON",
				bg='#27ae60',
				activebackground='#229954'
			)
			print("A/C System: OFFLINE")
			
		self._updateStatus()
		
	def _updateStatus(self):
		# Updates the system status display.
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
		# Updates the time display.
		now = datetime.now()
		timeStr = now.strftime("%#m/%#d/%y %#I:%M %p") if os.name == 'nt' else now.strftime("%-m/%-d/%y %-I:%M %p")
		
		if hasattr(self, 'timeLabel'):
			self.timeLabel.config(text=timeStr)
			
		self.root.after(1000, self._updateTime)

if __name__ == "__main__":
	root = tk.Tk()
	app = ACSystemPanel(root)
	root.mainloop()