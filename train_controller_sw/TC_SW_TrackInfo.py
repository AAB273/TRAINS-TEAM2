import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class TrackInformationPanel:
	# UI panel for track information display with Green and Red lines.
	
	"""
	Attributes:
		root: The main tkinter window
		trackMap: PhotoImage of the track layout
		currentBlock: IntVar holding the current block number
		currentLine: StringVar holding the current line
		blockData: Dictionary containing track information for each line and block
		notebook: ttk Notebook widget for tabs
		timeLabels: Dict of time labels for each tab
		testLine: StringVar holding the selected line in test mode
	"""
	
	def __init__(self, root):
		# Initializes the track information panel.
		self.root = root
		self.root.title("TRACK INFORMATION PANEL")
		self.root.geometry("1400x800")
		self.root.configure(bg='#7cb9e8')
		
		self.currentBlock = tk.IntVar(value=1)
		self.currentLine = tk.StringVar(value='Green Line')
		self.testLine = tk.StringVar(value='Green Line')
		self.trackMap = None
		self.timeLabels = {}
		self.infoLabels = {}
		self.testInfoLabels = {}
		
		# Track data for Green and Red lines
		self.blockData = {
			'Green Line': {
				1: {'slope': 0.5, 'speed': 27.96, 'switch': None, 'station': 'None'},
				2: {'slope': 1.0, 'speed': 27.96, 'switch': 'Left', 'station': 'Pioneer'},
				3: {'slope': 1.5, 'speed': 27.96, 'switch': None, 'station': 'None'},
				9: {'slope': -5.0, 'speed': 27.96, 'switch': 'Left', 'station': 'Edgebrook'},
				16: {'slope': 0.0, 'speed': 43.50, 'switch': 'Left/Right', 'station': 'Station'},
				22: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'Whited'},
				31: {'slope': 0.0, 'speed': 18.64, 'switch': None, 'station': 'South Bank'},
				39: {'slope': 0.0, 'speed': 18.64, 'switch': None, 'station': 'Central (Underground)'},
				48: {'slope': 0.0, 'speed': 18.64, 'switch': None, 'station': 'Inglewood (Underground)'},
				57: {'slope': 0.0, 'speed': 18.64, 'switch': None, 'station': 'Overbrook (Underground)'},
				65: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'Glenbury'},
				73: {'slope': 0.0, 'speed': 24.85, 'switch': None, 'station': 'Dormont'},
				77: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'Mt Lebanon'},
				88: {'slope': 0.0, 'speed': 15.53, 'switch': None, 'station': 'Poplar'},
				96: {'slope': 0.0, 'speed': 15.53, 'switch': None, 'station': 'Castle Shannon'}
			},
			'Red Line': {
				1: {'slope': 0.5, 'speed': 24.85, 'switch': None, 'station': 'None'},
				7: {'slope': 0.5, 'speed': 24.85, 'switch': 'Left/Right', 'station': 'Shadyside'},
				16: {'slope': -0.5, 'speed': 24.85, 'switch': 'Left/Right', 'station': 'Herron Ave'},
				21: {'slope': 0.0, 'speed': 34.17, 'switch': None, 'station': 'Swissville'},
				25: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'Penn Station (Underground)'},
				35: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'Steel Plaza (Underground)'},
				45: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'First Ave (Underground)'},
				48: {'slope': 0.0, 'speed': 43.50, 'switch': None, 'station': 'Station Square'},
				60: {'slope': 0.0, 'speed': 34.17, 'switch': None, 'station': 'South Hills Junction'}
			}
		}
		
		self._createWidgets()
		self._updateTime()
		self._updateTrackInfo()
	
	def beaconReceiver(self, blockNumber, line='Green Line'):
		# Receives block number from beacon signal.
		self.currentLine.set(line)
		if blockNumber in self.blockData.get(line, {}):
			self.currentBlock.set(blockNumber)
			self._updateTrackInfo()
		else:
			print(f"Invalid block number: {blockNumber} for {line}")
		
	def _createWidgets(self):
		# Creates all UI widgets for the panel.
		style = ttk.Style()
		style.theme_use('default')
		style.configure('TNotebook', background='#7cb9e8', borderwidth=0)
		style.configure('TNotebook.Tab', padding=[20, 8], font=('Arial', 10, 'bold'))
		
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill='both', expand=True)
		
		# Create info tabs for each line
		self._createTrackInfoTab('Green Line', '#2d7a2d')
		self._createTrackInfoTab('Red Line', '#c0392b')
		
		# Create single test mode tab
		self._createTestModeTab()
		
	def _createTrackInfoTab(self, line_name, line_color):
		# Creates the Track Information display tab for a specific line.
		frame = tk.Frame(self.notebook, bg='#7cb9e8')
		self.notebook.add(frame, text=f'{line_name} Info')
		
		headerFrame = tk.Frame(frame, bg='#1e5a8e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text=f"TRACK INFORMATION - {line_name.upper()}",
			font=('Arial', 18, 'bold'),
			bg='#1e5a8e',
			fg='white',
			pady=10
		)
		headerLabel.pack()
		
		timeFrame = tk.Frame(headerFrame, bg='#15406b', relief='raised', bd=2)
		timeFrame.pack(pady=(0, 8))
		
		timeLabel = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 12, 'bold'),
			bg='#15406b',
			fg='white',
			padx=15,
			pady=5
		)
		timeLabel.pack()
		self.timeLabels[line_name] = timeLabel
		
		mainFrame = tk.Frame(frame, bg='#7cb9e8')
		mainFrame.pack(fill='both', expand=True, padx=15, pady=10)
		
		# Info Section only
		self._createInfoSection(mainFrame, line_name, line_color)
		
	def _createTestModeTab(self):
		# Creates a single test mode tab with line selector.
		frame = tk.Frame(self.notebook, bg='#7cb9e8')
		self.notebook.add(frame, text='Test Mode')
		
		headerFrame = tk.Frame(frame, bg='#1e5a8e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="TEST MODE - ALL LINES",
			font=('Arial', 18, 'bold'),
			bg='#1e5a8e',
			fg='white',
			pady=10
		)
		headerLabel.pack()
		
		timeFrame = tk.Frame(headerFrame, bg='#15406b', relief='raised', bd=2)
		timeFrame.pack(pady=(0, 8))
		
		timeLabel = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 12, 'bold'),
			bg='#15406b',
			fg='white',
			padx=15,
			pady=5
		)
		timeLabel.pack()
		self.timeLabels['Test Mode'] = timeLabel
		
		mainFrame = tk.Frame(frame, bg='#7cb9e8')
		mainFrame.pack(fill='both', expand=True, padx=15, pady=10)
		
		# Line Selector - more compact
		selectorFrame = tk.Frame(mainFrame, bg='#34495e', relief='raised', bd=3)
		selectorFrame.pack(fill='x', pady=(0, 8))
		
		selectorTitle = tk.Label(
			selectorFrame,
			text="SELECT LINE",
			font=('Arial', 12, 'bold'),
			bg='#34495e',
			fg='white',
			pady=5
		)
		selectorTitle.pack()
		
		buttonFrame = tk.Frame(selectorFrame, bg='#2c3e50')
		buttonFrame.pack(fill='x', padx=15, pady=8)
		
		# Line buttons - more compact
		greenBtn = tk.Button(
			buttonFrame,
			text="Green Line",
			font=('Arial', 11, 'bold'),
			bg='#2d7a2d',
			fg='white',
			activebackground='#1e5a1e',
			relief='raised',
			bd=2,
			padx=15,
			pady=8,
			command=lambda: self._switchTestLine('Green Line')
		)
		greenBtn.pack(side='left', expand=True, padx=5)
		
		redBtn = tk.Button(
			buttonFrame,
			text="Red Line",
			font=('Arial', 11, 'bold'),
			bg='#c0392b',
			fg='white',
			activebackground='#922b21',
			relief='raised',
			bd=2,
			padx=15,
			pady=8,
			command=lambda: self._switchTestLine('Red Line')
		)
		redBtn.pack(side='left', expand=True, padx=5)
		
		# Test controls frame - more compact
		testFrame = tk.Frame(mainFrame, bg='#e8f4f8', relief='raised', bd=3)
		testFrame.pack(fill='both', expand=True)
		
		self.testTitleLabel = tk.Label(
			testFrame,
			text="TEST MODE - GREEN LINE",
			font=('Arial', 12, 'bold'),
			bg='#2d7a2d',
			fg='white',
			relief='raised',
			bd=2,
			padx=20,
			pady=8
		)
		self.testTitleLabel.pack(pady=8)
		
		controlFrame = tk.Frame(testFrame, bg='#5dade2', relief='raised', bd=3)
		controlFrame.pack(fill='x', padx=30, pady=8)
		
		controlTitle = tk.Label(
			controlFrame,
			text="BLOCK SELECTOR",
			font=('Arial', 12, 'bold'),
			bg='#5dade2',
			fg='white',
			pady=8
		)
		controlTitle.pack()
		
		sliderFrame = tk.Frame(controlFrame, bg='#aed6f1')
		sliderFrame.pack(fill='x', padx=20, pady=10)
		
		# Get initial block range
		blocks = list(self.blockData['Green Line'].keys())
		min_block = min(blocks) if blocks else 1
		max_block = max(blocks) if blocks else 15
		
		self.blockSlider = tk.Scale(
			sliderFrame,
			from_=min_block,
			to=max_block,
			orient='horizontal',
			command=self._onTestBlockChange,
			font=('Arial', 10, 'bold'),
			bg='#3498db',
			fg='white',
			activebackground='#2980b9',
			troughcolor='#1e5a8e',
			relief='raised',
			bd=2,
			length=300,
			width=25,
			sliderlength=35
		)
		self.blockSlider.pack()
		self.blockSlider.set(min_block)
		
		infoDisplay = tk.Frame(testFrame, bg='#d6eaf8', relief='raised', bd=3)
		infoDisplay.pack(fill='both', expand=True, padx=30, pady=(8, 15))
		
		infoTitle = tk.Label(
			infoDisplay,
			text="CURRENT BLOCK INFORMATION",
			font=('Arial', 13, 'bold'),
			bg='#d6eaf8',
			fg='#1e5a8e',
			pady=10
		)
		infoTitle.pack()
		
		self._createTestInfoLabels(infoDisplay)
		
		# Initialize test display
		self._updateTestInfo(min_block, 'Green Line')
		
	def _switchTestLine(self, line_name):
		# Switches the active line in test mode.
		self.testLine.set(line_name)
		
		# Update title with line-specific color
		colors = {
			'Green Line': '#2d7a2d',
			'Red Line': '#c0392b'
		}
		
		self.testTitleLabel.config(
			text=f"TEST MODE - {line_name.upper()}",
			bg=colors[line_name]
		)
		
		# Update slider range
		blocks = list(self.blockData[line_name].keys())
		min_block = min(blocks) if blocks else 1
		max_block = max(blocks) if blocks else 15
		
		self.blockSlider.config(from_=min_block, to=max_block)
		self.blockSlider.set(min_block)
		
		# Update display
		self._updateTestInfo(min_block, line_name)
		
	def _createInfoSection(self, parent, line_name, line_color):
		# Creates the track information display section.
		# Track map section - more compact
		mapFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3, width=550)
		mapFrame.pack(side='left', fill='both', padx=(0, 8))
		mapFrame.pack_propagate(False)
		
		mapTitle = tk.Label(
			mapFrame,
			text=f"TRACK MAP",
			font=('Arial', 12, 'bold'),
			bg='#34495e',
			fg='white',
			pady=6
		)
		mapTitle.pack()
		
		mapContainer = tk.Frame(mapFrame, bg='#2c3e50')
		mapContainer.pack(fill='both', expand=True, padx=8, pady=8)
		
		# Try to load track map image using tkinter's PhotoImage
		try:
			track_map_path = r"train_controller_sw/trackmap.png"
			photo = tk.PhotoImage(file=track_map_path)
			
			# Zoom to smaller size to fit
			photo = photo.zoom(1, 1)
			photo = photo.subsample(2, 2)
			
			mapLabel = tk.Label(mapContainer, image=photo, bg='#2c3e50')
			mapLabel.image = photo  # Keep a reference
			mapLabel.pack(padx=5, pady=5)
		except Exception as e:
			# If image can't be loaded, show placeholder
			placeholderLabel = tk.Label(
				mapContainer,
				text="Track Map\nNot Found",
				font=('Arial', 10),
				bg='#2c3e50',
				fg='#95a5a6',
				justify='center',
				pady=60
			)
			placeholderLabel.pack(fill='both', expand=True)
		
		# Info section - more compact
		infoFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=3)
		infoFrame.pack(side='right', fill='both', expand=True, padx=(8, 0))
		
		infoTitle = tk.Label(
			infoFrame,
			text=f"CURRENT TRACK INFO\n{line_name}",
			font=('Arial', 14, 'bold'),
			bg='#34495e',
			fg='white',
			pady=8
		)
		infoTitle.pack()
		
		infoContainer = tk.Frame(infoFrame, bg='#2c3e50')
		infoContainer.pack(fill='both', expand=True, padx=15, pady=10)
		
		# Create info labels for this line
		if line_name not in self.infoLabels:
			self.infoLabels[line_name] = {}
		
		self.infoLabels[line_name]['block'] = self._createInfoLabel(infoContainer, "BLOCK:", "1")
		self.infoLabels[line_name]['slope'] = self._createInfoLabel(infoContainer, "SLOPE:", "0.0%")
		self.infoLabels[line_name]['speed'] = self._createInfoLabel(infoContainer, "SPEED LIMIT:", "40 mph")
		self.infoLabels[line_name]['switch'] = self._createInfoLabel(infoContainer, "SWITCH STATUS:", "None")
		self.infoLabels[line_name]['station'] = self._createInfoLabel(infoContainer, "NEAREST STATION:", "Unknown")
		
	def _createTestInfoLabels(self, parent):
		# Creates info labels for test mode display.
		infoContainer = tk.Frame(parent, bg='#d6eaf8')
		infoContainer.pack(fill='both', expand=True, padx=20, pady=(0, 15))
		
		self.testInfoLabels['block'] = self._createTestLabel(infoContainer, "BLOCK:", "1")
		self.testInfoLabels['slope'] = self._createTestLabel(infoContainer, "SLOPE:", "0.0%")
		self.testInfoLabels['speed'] = self._createTestLabel(infoContainer, "SPEED LIMIT:", "40 mph")
		self.testInfoLabels['switch'] = self._createTestLabel(infoContainer, "SWITCH STATUS:", "None")
		self.testInfoLabels['station'] = self._createTestLabel(infoContainer, "NEAREST STATION:", "Unknown")
		
	def _createTestLabel(self, parent, labelText, valueText):
		# Creates a formatted test info label - more compact.
		frame = tk.Frame(parent, bg='#5dade2', relief='raised', bd=2)
		frame.pack(fill='x', pady=4)
		
		title = tk.Label(
			frame,
			text=labelText,
			font=('Arial', 10, 'bold'),
			bg='#5dade2',
			fg='white',
			anchor='w',
			padx=8,
			pady=3
		)
		title.pack(fill='x')
		
		value = tk.Label(
			frame,
			text=valueText,
			font=('Arial', 14, 'bold'),
			bg='#aed6f1',
			fg='#1e5a8e',
			anchor='w',
			padx=12,
			pady=6
		)
		value.pack(fill='x')
		
		return value
		
	def _createInfoLabel(self, parent, labelText, valueText):
		# Creates a formatted info label with title and value - more compact.
		frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=2)
		frame.pack(fill='x', pady=6)
		
		title = tk.Label(
			frame,
			text=labelText,
			font=('Arial', 11, 'bold'),
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
			font=('Arial', 16, 'bold'),
			bg='#2c3e50',
			fg='white',
			anchor='w',
			padx=12,
			pady=8
		)
		value.pack(fill='x')
		
		return value
		
	def _onTestBlockChange(self, value):
		# Updates track information when block selection changes in test mode.
		block = int(float(value))
		line = self.testLine.get()
		self._updateTestInfo(block, line)
		
	def _updateTrackInfo(self):
		# Updates all track information labels based on current block.
		line = self.currentLine.get()
		block = self.currentBlock.get()
		
		if line not in self.blockData or block not in self.blockData[line]:
			return
		
		data = self.blockData[line].get(block, {})
		
		if line in self.infoLabels:
			labels = self.infoLabels[line]
			
			labels['block'].config(text=str(block))
			
			slope = data.get('slope', 0.0)
			labels['slope'].config(text=f"{slope:+.1f}%")
			
			speed = data.get('speed', 0)
			labels['speed'].config(text=f"{speed:.1f} mph")
			
			switch = data.get('switch')
			if switch:
				labels['switch'].config(text=f"To Block {switch}")
			else:
				labels['switch'].config(text="None")
				
			station = data.get('station', 'Unknown')
			labels['station'].config(text=station)
		
	def _updateTestInfo(self, block, line_name):
		# Updates test mode information labels.
		if line_name not in self.blockData or block not in self.blockData[line_name]:
			return
		
		data = self.blockData[line_name].get(block, {})
		
		labels = self.testInfoLabels
		
		labels['block'].config(text=str(block))
		
		slope = data.get('slope', 0.0)
		labels['slope'].config(text=f"{slope:+.1f}%")
		
		speed = data.get('speed', 0)
		labels['speed'].config(text=f"{speed:.1f} mph")
		
		switch = data.get('switch')
		if switch:
			labels['switch'].config(text=f"To: {switch}")
		else:
			labels['switch'].config(text="None")
			
		station = data.get('station', 'Unknown')
		labels['station'].config(text=station)
		
	def _updateTime(self):
		# Updates the time display on all tabs.
		now = datetime.now()
		timeStr = now.strftime("%#m/%#d/%y %#I:%M %p") if os.name == 'nt' else now.strftime("%-m/%-d/%y %-I:%M %p")
		
		for label in self.timeLabels.values():
			if label:
				label.config(text=timeStr)
			
		self.root.after(1000, self._updateTime)

if __name__ == "__main__":
	root = tk.Tk()
	app = TrackInformationPanel(root)
	root.mainloop()