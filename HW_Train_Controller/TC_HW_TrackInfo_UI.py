import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class TrackInformationPanel:
	# UI panel for track information display.
	
	"""
	Attributes:
		root: The main tkinter window
		trackMap: PhotoImage of the track layout
		currentBlock: IntVar holding the current block number
		blockData: Dictionary containing track information for each block
		notebook: ttk Notebook widget for tabs
		blockLabel: Label displaying current block number
		slopeLabel: Label displaying slope grade
		speedLabel: Label displaying speed limit
		switchLabel: Label displaying switch information
		stationLabel: Label displaying nearest station
		timeLabelTrack: Label showing time on Track Info tab
		timeLabelTest: Label showing time on Test Mode tab
	"""
	
	def __init__(self, root):
		# Initializes the track information panel.
		self.root = root
		self.root.title("TRACK INFORMATION PANEL")
		self.root.geometry("1200x750")
		self.root.configure(bg='#7cb9e8')
		
		self.currentBlock = tk.IntVar(value=1)
		self.trackMap = None
		
		self.blockData = {
			1: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station B or Station C'},
			2: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station B or Station C'},
			3: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station B or Station C'},
			4: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station B or Station C'},
			5: {'slope': 0.0, 'speed': 40, 'switch': 6, 'station': 'Station B or Station C'},
			6: {'slope': 0.0, 'speed': 35, 'switch': None, 'station': 'Station B'},
			7: {'slope': 0.0, 'speed': 35, 'switch': None, 'station': 'Station B'},
			8: {'slope': 0.0, 'speed': 35, 'switch': None, 'station': 'Station B'},
			9: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station B'},
			10: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station B'},
			11: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station C'},
			12: {'slope': 0.0, 'speed': 35, 'switch': None, 'station': 'Station C'},
			13: {'slope': 0.0, 'speed': 35, 'switch': None, 'station': 'Station C'},
			14: {'slope': 0.0, 'speed': 35, 'switch': None, 'station': 'Station C'},
			15: {'slope': 0.0, 'speed': 40, 'switch': None, 'station': 'Station C'}
		}
		# Track data for each block including slope, speed, switch, and station.
		
		self._createWidgets()
		self._updateTime()
		self._updateTrackInfo()
	
	def beaconReceiver(self, blockNumber):
		# Receives block number from beacon signal.
		if blockNumber in self.blockData:
			self.currentBlock.set(blockNumber)
			self._updateTrackInfo()
		else:
			print(f"Invalid block number: {blockNumber}")
		
	def _createWidgets(self):
		# Creates all UI widgets for the panel.
		style = ttk.Style()
		style.theme_use('default')
		style.configure('TNotebook', background='#7cb9e8', borderwidth=0)
		style.configure('TNotebook.Tab', padding=[30, 10], font=('Arial', 11, 'bold'))
		
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill='both', expand=True)
		
		self._createTrackInfoTab()
		self._createTestModeTab()
		
	def _createTrackInfoTab(self):
		# Creates the Track Information display tab.
		frame = tk.Frame(self.notebook, bg='#7cb9e8')
		self.notebook.add(frame, text='Track Info')
		
		headerFrame = tk.Frame(frame, bg='#1e5a8e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="TRACK INFORMATION PANEL",
			font=('Arial', 24, 'bold'),
			bg='#1e5a8e',
			fg='white',
			pady=15
		)
		headerLabel.pack()
		
		timeFrame = tk.Frame(headerFrame, bg='#15406b', relief='raised', bd=3)
		timeFrame.pack(pady=(0, 10))
		
		self.timeLabelTrack = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#15406b',
			fg='white',
			padx=20,
			pady=8
		)
		self.timeLabelTrack.pack()
		
		mainFrame = tk.Frame(frame, bg='#7cb9e8')
		mainFrame.pack(fill='both', expand=True, padx=20, pady=20)
		
		self._createMapSection(mainFrame)
		self._createInfoSection(mainFrame)
		
	def _createTestModeTab(self):
		# Creates the Test Mode tab with block selector.
		frame = tk.Frame(self.notebook, bg='#e8f4f8')
		self.notebook.add(frame, text='Test Mode')
		
		headerFrame = tk.Frame(frame, bg='#1e5a8e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="TRACK INFORMATION PANEL",
			font=('Arial', 24, 'bold'),
			bg='#1e5a8e',
			fg='white',
			pady=15
		)
		headerLabel.pack()
		
		timeFrame = tk.Frame(headerFrame, bg='#15406b', relief='raised', bd=3)
		timeFrame.pack(pady=(0, 10))
		
		self.timeLabelTest = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#15406b',
			fg='white',
			padx=20,
			pady=8
		)
		self.timeLabelTest.pack()
		
		title = tk.Label(
			frame,
			text="Test Mode",
			font=('Arial', 24, 'bold'),
			bg='#2980b9',
			fg='white',
			relief='raised',
			bd=4,
			padx=40,
			pady=15
		)
		title.pack(pady=30)
		
		controlFrame = tk.Frame(frame, bg='#5dade2', relief='raised', bd=4)
		controlFrame.pack(fill='x', padx=40, pady=20)
		
		controlTitle = tk.Label(
			controlFrame,
			text="BLOCK SELECTOR",
			font=('Arial', 18, 'bold'),
			bg='#5dade2',
			fg='white',
			pady=15
		)
		controlTitle.pack()
		
		sliderFrame = tk.Frame(controlFrame, bg='#aed6f1')
		sliderFrame.pack(fill='x', padx=30, pady=20)
		
		blockSlider = tk.Scale(
			sliderFrame,
			from_=1,
			to=15,
			orient='horizontal',
			variable=self.currentBlock,
			command=self._onBlockChange,
			font=('Arial', 14, 'bold'),
			bg='#3498db',
			fg='white',
			activebackground='#2980b9',
			troughcolor='#1e5a8e',
			relief='raised',
			bd=3,
			length=700,
			width=35,
			sliderlength=50
		)
		blockSlider.pack()
		
		infoDisplay = tk.Frame(frame, bg='#d6eaf8', relief='raised', bd=4)
		infoDisplay.pack(fill='both', expand=True, padx=40, pady=(20, 40))
		
		infoTitle = tk.Label(
			infoDisplay,
			text="CURRENT BLOCK INFORMATION",
			font=('Arial', 18, 'bold'),
			bg='#d6eaf8',
			fg='#1e5a8e',
			pady=15
		)
		infoTitle.pack()
		
		self._createTestInfoLabels(infoDisplay)
		
	def _createTestInfoLabels(self, parent):
		# Creates info labels for test mode display.
		infoContainer = tk.Frame(parent, bg='#d6eaf8')
		infoContainer.pack(fill='both', expand=True, padx=30, pady=(0, 20))
		
		self.testBlockLabel = self._createTestLabel(infoContainer, "BLOCK:", "1")
		self.testSlopeLabel = self._createTestLabel(infoContainer, "SLOPE:", "0.0%")
		self.testSpeedLabel = self._createTestLabel(infoContainer, "SPEED LIMIT:", "40 mph")
		self.testSwitchLabel = self._createTestLabel(infoContainer, "SWITCH STATUS:", "None")
		self.testStationLabel = self._createTestLabel(infoContainer, "NEAREST STATION:", "Station B or Station C")
		
	def _createTestLabel(self, parent, labelText, valueText):
		# Creates a formatted test info label.
		frame = tk.Frame(parent, bg='#5dade2', relief='raised', bd=3)
		frame.pack(fill='x', pady=8)
		
		title = tk.Label(
			frame,
			text=labelText,
			font=('Arial', 14, 'bold'),
			bg='#5dade2',
			fg='white',
			anchor='w',
			padx=10,
			pady=5
		)
		title.pack(fill='x')
		
		value = tk.Label(
			frame,
			text=valueText,
			font=('Arial', 20, 'bold'),
			bg='#aed6f1',
			fg='#1e5a8e',
			anchor='w',
			padx=15,
			pady=10
		)
		value.pack(fill='x')
		
		return value
		
	def _createMapSection(self, parent):
		# Creates the track map display section.
		mapFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4)
		mapFrame.pack(side='left', fill='both', expand=True, padx=(0, 10))
		
		mapTitle = tk.Label(
			mapFrame,
			text="TRACK MAP",
			font=('Arial', 18, 'bold'),
			bg='#34495e',
			fg='white',
			pady=10
		)
		mapTitle.pack()
		
		try:
			self.trackMap = tk.PhotoImage(file='HW_Train_Controller/blue_line.png')
			
			mapLabel = tk.Label(
				mapFrame,
				image=self.trackMap,
				bg='white',
				relief='sunken',
				bd=3
			)
			mapLabel.pack(padx=15, pady=15)
		except Exception as e:
			errorLabel = tk.Label(
				mapFrame,
				text=f"Error loading track map:\n{str(e)}",
				font=('Arial', 14),
				bg='#34495e',
				fg='#e74c3c',
				pady=50
			)
			errorLabel.pack(fill='both', expand=True, padx=15, pady=15)
			
	def _createInfoSection(self, parent):
		# Creates the track information display section.
		infoFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4)
		infoFrame.pack(side='right', fill='both', padx=(10, 0))
		
		infoTitle = tk.Label(
			infoFrame,
			text="CURRENT TRACK INFO",
			font=('Arial', 18, 'bold'),
			bg='#34495e',
			fg='white',
			pady=10
		)
		infoTitle.pack()
		
		infoContainer = tk.Frame(infoFrame, bg='#2c3e50')
		infoContainer.pack(fill='both', expand=True, padx=15, pady=15)
		
		self.blockLabel = self._createInfoLabel(infoContainer, "BLOCK:", "1")
		self.slopeLabel = self._createInfoLabel(infoContainer, "SLOPE:", "0.0%")
		self.speedLabel = self._createInfoLabel(infoContainer, "SPEED LIMIT:", "40 mph")
		self.switchLabel = self._createInfoLabel(infoContainer, "SWITCH STATUS:", "None")
		self.stationLabel = self._createInfoLabel(infoContainer, "NEAREST STATION:", "Station B or Station C")
		
	def _createInfoLabel(self, parent, labelText, valueText):
		# Creates a formatted info label with title and value.
		frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3)
		frame.pack(fill='x', pady=8)
		
		title = tk.Label(
			frame,
			text=labelText,
			font=('Arial', 14, 'bold'),
			bg='#34495e',
			fg='#3498db',
			anchor='w',
			padx=10,
			pady=5
		)
		title.pack(fill='x')
		
		value = tk.Label(
			frame,
			text=valueText,
			font=('Arial', 20, 'bold'),
			bg='#2c3e50',
			fg='white',
			anchor='w',
			padx=15,
			pady=10
		)
		value.pack(fill='x')
		
		return value
		
	def _onBlockChange(self, value):
		# Updates track information when block selection changes in test mode.
		self._updateTrackInfo()
		self._updateTestInfo()
		
	def _updateTrackInfo(self):
		# Updates all track information labels based on current block.
		block = self.currentBlock.get()
		data = self.blockData.get(block, {})
		
		self.blockLabel.config(text=str(block))
		
		slope = data.get('slope', 0.0)
		self.slopeLabel.config(text=f"{slope:+.1f}%")
		
		speed = data.get('speed', 0)
		self.speedLabel.config(text=f"{speed} mph")
		
		switch = data.get('switch')
		if switch:
			self.switchLabel.config(text=f"To Block {switch}")
		else:
			self.switchLabel.config(text="None")
			
		station = data.get('station', 'Unknown')
		self.stationLabel.config(text=station)
		
	def _updateTestInfo(self):
		# Updates test mode information labels.
		block = self.currentBlock.get()
		data = self.blockData.get(block, {})
		
		self.testBlockLabel.config(text=str(block))
		
		slope = data.get('slope', 0.0)
		self.testSlopeLabel.config(text=f"{slope:+.1f}%")
		
		speed = data.get('speed', 0)
		self.testSpeedLabel.config(text=f"{speed} mph")
		
		switch = data.get('switch')
		if switch:
			self.testSwitchLabel.config(text=f"To Block {switch}")
		else:
			self.testSwitchLabel.config(text="None")
			
		station = data.get('station', 'Unknown')
		self.testStationLabel.config(text=station)
		
	def _updateTime(self):
		# Updates the time display on all tabs.
		now = datetime.now()
		timeStr = now.strftime("%#m/%#d/%y %#I:%M %p") if os.name == 'nt' else now.strftime("%-m/%-d/%y %-I:%M %p")
		
		if hasattr(self, 'timeLabelTrack'):
			self.timeLabelTrack.config(text=timeStr)
		if hasattr(self, 'timeLabelTest'):
			self.timeLabelTest.config(text=timeStr)
			
		self.root.after(1000, self._updateTime)

if __name__ == "__main__":
	root = tk.Tk()
	app = TrackInformationPanel(root)
	root.mainloop()