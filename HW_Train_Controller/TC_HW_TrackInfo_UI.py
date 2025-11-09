import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class TrackInformationPanel:
	# UI panel for track information display with all three lines.
	
	"""
	Attributes:
		root: The main tkinter window
		trackMap: PhotoImage of the track layout
		currentBlock: IntVar holding the current block number
		currentLine: StringVar holding the current line
		blockData: Dictionary containing track information for each line and block
		notebook: ttk Notebook widget for tabs
		timeLabels: Dict of time labels for each tab
	"""
	
	def __init__(self, root):
		# Initializes the track information panel.
		self.root = root
		self.root.title("TRACK INFORMATION PANEL")
		self.root.geometry("1200x750")
		self.root.configure(bg='#7cb9e8')
		
		self.currentBlock = tk.IntVar(value=1)
		self.currentLine = tk.StringVar(value='Blue Line')
		self.trackMap = None
		self.timeLabels = {}
		self.infoLabels = {}
		self.testInfoLabels = {}
		
		# Track data for all three lines
		self.blockData = {
			'Blue Line': {
				1: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B or C'},
				2: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B or C'},
				3: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B or C'},
				4: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B or C'},
				5: {'slope': 0.0, 'speed': 31.06, 'switch': 6, 'station': 'Station B or C'},
				6: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B'},
				7: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B'},
				8: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B'},
				9: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B'},
				10: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station B'},
				11: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station C'},
				12: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station C'},
				13: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station C'},
				14: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station C'},
				15: {'slope': 0.0, 'speed': 31.06, 'switch': None, 'station': 'Station C'}
			},
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
	
	def beaconReceiver(self, blockNumber, line='Blue Line'):
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
		style.configure('TNotebook.Tab', padding=[30, 10], font=('Arial', 11, 'bold'))
		
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill='both', expand=True)
		
		self._createTrackInfoTab('Blue Line', '#1a5490')
		self._createTrackInfoTab('Green Line', '#2d7a2d')
		self._createTrackInfoTab('Red Line', '#c0392b')
		
	def _createTrackInfoTab(self, line_name, line_color):
		# Creates the Track Information display tab for a specific line.
		frame = tk.Frame(self.notebook, bg='#7cb9e8')
		self.notebook.add(frame, text=f'{line_name} Info')
		
		headerFrame = tk.Frame(frame, bg='#1e5a8e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text=f"TRACK INFORMATION\n{line_name.upper()}",
			font=('Arial', 24, 'bold'),
			bg='#1e5a8e',
			fg='white',
			pady=15
		)
		headerLabel.pack()
		
		timeFrame = tk.Frame(headerFrame, bg='#15406b', relief='raised', bd=3)
		timeFrame.pack(pady=(0, 10))
		
		timeLabel = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#15406b',
			fg='white',
			padx=20,
			pady=8
		)
		timeLabel.pack()
		self.timeLabels[line_name] = timeLabel
		
		mainFrame = tk.Frame(frame, bg='#7cb9e8')
		mainFrame.pack(fill='both', expand=True, padx=20, pady=20)
		
		# Info Section (no map for now)
		self._createInfoSection(mainFrame, line_name, line_color)
		
		# Test Mode Section
		self._createTestModeSection(mainFrame, line_name, line_color)
		
	def _createInfoSection(self, parent, line_name, line_color):
		# Creates the track information display section.
		infoFrame = tk.Frame(parent, bg='#34495e', relief='raised', bd=4, width=500)
		infoFrame.pack(side='left', fill='both', padx=(0, 10), expand=True)
		
		infoTitle = tk.Label(
			infoFrame,
			text=f"CURRENT TRACK INFO\n{line_name}",
			font=('Arial', 16, 'bold'),
			bg='#34495e',
			fg='white',
			pady=10
		)
		infoTitle.pack()
		
		infoContainer = tk.Frame(infoFrame, bg='#2c3e50')
		infoContainer.pack(fill='both', expand=True, padx=15, pady=15)
		
		# Create info labels for this line
		if line_name not in self.infoLabels:
			self.infoLabels[line_name] = {}
		
		self.infoLabels[line_name]['block'] = self._createInfoLabel(infoContainer, "BLOCK:", "1")
		self.infoLabels[line_name]['slope'] = self._createInfoLabel(infoContainer, "SLOPE:", "0.0%")
		self.infoLabels[line_name]['speed'] = self._createInfoLabel(infoContainer, "SPEED LIMIT:", "40 mph")
		self.infoLabels[line_name]['switch'] = self._createInfoLabel(infoContainer, "SWITCH STATUS:", "None")
		self.infoLabels[line_name]['station'] = self._createInfoLabel(infoContainer, "NEAREST STATION:", "Unknown")
		
	def _createTestModeSection(self, parent, line_name, line_color):
		# Creates test mode with block selector.
		testFrame = tk.Frame(parent, bg='#e8f4f8', relief='raised', bd=4, width=500)
		testFrame.pack(side='right', fill='both', padx=(10, 0), expand=True)
		
		testTitle = tk.Label(
			testFrame,
			text=f"TEST MODE\n{line_name}",
			font=('Arial', 16, 'bold'),
			bg=line_color,
			fg='white',
			relief='raised',
			bd=4,
			padx=40,
			pady=15
		)
		testTitle.pack(pady=20)
		
		controlFrame = tk.Frame(testFrame, bg='#5dade2', relief='raised', bd=4)
		controlFrame.pack(fill='x', padx=40, pady=20)
		
		controlTitle = tk.Label(
			controlFrame,
			text="BLOCK SELECTOR",
			font=('Arial', 16, 'bold'),
			bg='#5dade2',
			fg='white',
			pady=15
		)
		controlTitle.pack()
		
		sliderFrame = tk.Frame(controlFrame, bg='#aed6f1')
		sliderFrame.pack(fill='x', padx=30, pady=20)
		
		# Get block range for this line
		blocks = list(self.blockData[line_name].keys())
		min_block = min(blocks) if blocks else 1
		max_block = max(blocks) if blocks else 15
		
		blockSlider = tk.Scale(
			sliderFrame,
			from_=min_block,
			to=max_block,
			orient='horizontal',
			command=lambda v: self._onBlockChange(v, line_name),
			font=('Arial', 14, 'bold'),
			bg='#3498db',
			fg='white',
			activebackground='#2980b9',
			troughcolor='#1e5a8e',
			relief='raised',
			bd=3,
			length=350,
			width=35,
			sliderlength=50
		)
		blockSlider.pack()
		blockSlider.set(min_block)
		
		infoDisplay = tk.Frame(testFrame, bg='#d6eaf8', relief='raised', bd=4)
		infoDisplay.pack(fill='both', expand=True, padx=40, pady=(20, 40))
		
		infoTitle = tk.Label(
			infoDisplay,
			text="CURRENT BLOCK INFORMATION",
			font=('Arial', 16, 'bold'),
			bg='#d6eaf8',
			fg='#1e5a8e',
			pady=15
		)
		infoTitle.pack()
		
		self._createTestInfoLabels(infoDisplay, line_name)
		
	def _createTestInfoLabels(self, parent, line_name):
		# Creates info labels for test mode display.
		infoContainer = tk.Frame(parent, bg='#d6eaf8')
		infoContainer.pack(fill='both', expand=True, padx=30, pady=(0, 20))
		
		if line_name not in self.testInfoLabels:
			self.testInfoLabels[line_name] = {}
		
		blocks = list(self.blockData[line_name].keys())
		min_block = min(blocks) if blocks else 1
		
		self.testInfoLabels[line_name]['block'] = self._createTestLabel(infoContainer, "BLOCK:", str(min_block))
		self.testInfoLabels[line_name]['slope'] = self._createTestLabel(infoContainer, "SLOPE:", "0.0%")
		self.testInfoLabels[line_name]['speed'] = self._createTestLabel(infoContainer, "SPEED LIMIT:", "40 mph")
		self.testInfoLabels[line_name]['switch'] = self._createTestLabel(infoContainer, "SWITCH STATUS:", "None")
		self.testInfoLabels[line_name]['station'] = self._createTestLabel(infoContainer, "NEAREST STATION:", "Unknown")
		
	def _createTestLabel(self, parent, labelText, valueText):
		# Creates a formatted test info label.
		frame = tk.Frame(parent, bg='#5dade2', relief='raised', bd=3)
		frame.pack(fill='x', pady=6)
		
		title = tk.Label(
			frame,
			text=labelText,
			font=('Arial', 12, 'bold'),
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
			font=('Arial', 18, 'bold'),
			bg='#aed6f1',
			fg='#1e5a8e',
			anchor='w',
			padx=15,
			pady=10
		)
		value.pack(fill='x')
		
		return value
		
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
		
	def _onBlockChange(self, value, line_name):
		# Updates track information when block selection changes in test mode.
		block = int(float(value))
		self._updateTestInfo(block, line_name)
		
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
		
		if line_name in self.testInfoLabels:
			labels = self.testInfoLabels[line_name]
			
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