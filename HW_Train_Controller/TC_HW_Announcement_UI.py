import tkinter as tk
from tkinter import ttk, Scrollbar
from datetime import datetime
import os

class StationAnnouncementPanel:
	# UI panel for train station announcements with all three lines.
	
	"""
	Attributes:
		root: The main tkinter window
		stations: Dictionary mapping line names to station lists
		selectedStation: StringVar holding the currently selected station
		currentLine: StringVar holding the currently selected line
		notebook: ttk Notebook widget for tabs
		emergencyText: Text widget for emergency messages
		timeLabels: Dict of time labels for each tab
	"""
	
	def __init__(self, root, parent=None):
		# Initializes the station announcement panel.
		self.root = root
		self.parent = parent  # Reference to main UI (SpeedDisplay) for socket access
		self.root.title("STATION ANNOUNCEMENT PANEL")
		self.root.geometry("500x700")
		self.root.configure(bg='#2c3e50')
		
		# Station data for Green and Red lines
		self.stations = {
			'Green Line': ['Pioneer', 'Edgebrook', 'LLC Plaza', 'Whited', 'South Bank', 
			               'Central (Underground)', 'Inglewood (Underground)', 
			               'Overbrook (Underground)', 'Glenbury', 'Dormont', 
			               'Mt Lebanon', 'Poplar', 'Castle Shannon'],
			'Red Line': ['Shadyside', 'Herron Ave', 'Swissville', 
			             'Penn Station (Underground)', 'Steel Plaza (Underground)', 
			             'First Ave (Underground)', 'Station Square', 
			             'South Hills Junction']
		}
		
		self.selectedStation = tk.StringVar()
		self.currentLine = tk.StringVar(value='Green Line')
		self.timeLabels = {}
		
		self._createWidgets()
		self._updateTime()
		
	def _createWidgets(self):
		# Creates all UI widgets for the panel.
		style = ttk.Style()
		style.theme_use('default')
		style.configure('TNotebook', background='#2c3e50', borderwidth=0)
		style.configure('TNotebook.Tab', padding=[30, 10], font=('Arial', 11, 'bold'))
		
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill='both', expand=True)
		
		self._createGreenLineTab()
		self._createRedLineTab()
		self._createEmergencyTab()
		
	def _createLineTab(self, line_name, line_color):
		# Creates a station selection tab for a specific line.
		frame = tk.Frame(self.notebook, bg='#d0e8f5')
		self.notebook.add(frame, text=line_name)
		
		# Header section with title and time
		headerFrame = tk.Frame(frame, bg='#34495e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="STATION\nANNOUNCEMENT\nPANEL",
			font=('Arial', 18, 'bold'),
			bg='#34495e',
			fg='white',
			pady=8
		)
		headerLabel.pack(pady=(10, 5))
		
		timeFrame = tk.Frame(headerFrame, bg='#2c3e50', relief='raised', bd=3)
		timeFrame.pack(pady=(5, 10))
		
		timeLabel = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#2c3e50',
			fg='white',
			padx=20,
			pady=8
		)
		timeLabel.pack()
		self.timeLabels[line_name] = timeLabel
		
		# Line title
		title = tk.Label(
			frame,
			text=line_name,
			font=('Arial', 24, 'bold'),
			bg=line_color,
			fg='white',
			relief='raised',
			bd=4,
			padx=40,
			pady=15
		)
		title.pack(pady=30)
		
		# Scrollable station list frame - CENTERED
		stationsFrame = tk.Frame(frame, bg='#d0e8f5')
		stationsFrame.pack(expand=True, fill='both', pady=20, padx=50)  # Increased side padding
		
		# Create container for centered scrollable area
		centerContainer = tk.Frame(stationsFrame, bg='#d0e8f5')
		centerContainer.pack(expand=True)
		
		# Create canvas and scrollbar for scrolling
		canvas = tk.Canvas(centerContainer, bg='#d0e8f5', highlightthickness=0, width=350)
		scrollbar = Scrollbar(centerContainer, orient="vertical", command=canvas.yview, width=20)
		scrollable_frame = tk.Frame(canvas, bg='#d0e8f5')
		
		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)
		
		canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
		canvas.configure(yscrollcommand=scrollbar.set)
		
		# Pack canvas and scrollbar - centered
		canvas.pack(side="left", fill="y", expand=False)
		scrollbar.pack(side="right", fill="y")
		
		# Add station buttons to scrollable frame - centered
		stations = self.stations[line_name]
		
		for station in stations:
			btn = tk.Button(
				scrollable_frame,
				text=station,
				font=('Arial', 14, 'bold'),
				bg='#3498db',
				fg='white',
				activebackground='#2980b9',
				activeforeground='white',
				relief='raised',
				bd=3,
				command=lambda s=station, l=line_name: self._selectStation(s, l),
				height=2,
				width=28  # Fixed width for all buttons
			)
			btn.pack(pady=5)
		
		# Announce button at bottom
		announceFrame = tk.Frame(frame, bg="#4b87e0")
		announceFrame.pack(side='bottom', pady=30)
		
		announceBtn = tk.Button(
			announceFrame,
			text="ANNOUNCE",
			font=('Arial', 18, 'bold'),
			bg='#1e8449',
			fg='white',
			activebackground='#196f3d',
			activeforeground='white',
			relief='raised',
			bd=4,
			command=lambda: self._announceStation(line_name),
			width=18,
			height=2
		)
		announceBtn.pack()
		
		
	def _createGreenLineTab(self):
		# Creates the Green Line station selection tab.
		self._createLineTab('Green Line', '#2d7a2d')
		
	def _createRedLineTab(self):
		# Creates the Red Line station selection tab.
		self._createLineTab('Red Line', '#c0392b')
		
	def _createEmergencyTab(self):
		# Creates the Emergency message tab.
		frame = tk.Frame(self.notebook, bg='#ffe8e8')
		self.notebook.add(frame, text='Emergency')
		
		# Header section with title and time
		headerFrame = tk.Frame(frame, bg='#34495e')
		headerFrame.pack(fill='x')
		
		headerLabel = tk.Label(
			headerFrame,
			text="STATION\nANNOUNCEMENT\nPANEL",
			font=('Arial', 18, 'bold'),
			bg='#34495e',
			fg='white',
			pady=8
		)
		headerLabel.pack(pady=(10, 5))
		
		timeFrame = tk.Frame(headerFrame, bg='#2c3e50', relief='raised', bd=3)
		timeFrame.pack(pady=(5, 10))
		
		timeLabel = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#2c3e50',
			fg='white',
			padx=20,
			pady=8
		)
		timeLabel.pack()
		self.timeLabels['Emergency'] = timeLabel
		
		# Emergency title
		title = tk.Label(
			frame,
			text="Emergency",
			font=('Arial', 24, 'bold'),
			bg='#c0392b',
			fg='white',
			relief='raised',
			bd=4,
			padx=40,
			pady=15
		)
		title.pack(pady=30)
		
		# Emergency message text input
		msgContainer = tk.Frame(frame, bg='#ffe8e8')
		msgContainer.pack(expand=True, padx=30, fill='both')
		
		msgLabel = tk.Label(
			msgContainer,
			text="Emergency Message:",
			font=('Arial', 14, 'bold'),
			bg='#ffe8e8',
			fg='#2c3e50'
		)
		msgLabel.pack(anchor='w', pady=(0, 10))
		
		textFrame = tk.Frame(msgContainer, bg='#2c3e50', relief='raised', bd=3)
		textFrame.pack(fill='both', expand=True)
		
		# Add scrollbar to text widget
		scrollbar = Scrollbar(textFrame)
		scrollbar.pack(side='right', fill='y')
		
		self.emergencyText = tk.Text(
			textFrame,
			height=8,
			font=('Arial', 12),
			bg='white',
			fg='#2c3e50',
			wrap='word',
			relief='flat',
			bd=0,
			yscrollcommand=scrollbar.set
		)
		self.emergencyText.pack(fill='both', expand=True, padx=3, pady=3)
		scrollbar.config(command=self.emergencyText.yview)
		
		# Announce button
		announceFrame = tk.Frame(frame, bg='#ffe8e8')
		announceFrame.pack(side='bottom', pady=30)
		
		emergencyBtn = tk.Button(
			announceFrame,
			text="ANNOUNCE",
			font=('Arial', 18, 'bold'),
			bg='#e74c3c',
			fg='white',
			activebackground='#c0392b',
			activeforeground='white',
			relief='raised',
			bd=4,
			command=self._announceEmergency,
			width=18,
			height=2
		)
		emergencyBtn.pack()
		
	def _selectStation(self, station, line):
		# Selects a station for announcement.
		self.selectedStation.set(station)
		self.currentLine.set(line)
		print(f"Selected: {station} on {line}")
		
	def _announceStation(self, line):
		# Broadcasts station arrival announcement.
		station = self.selectedStation.get()
		if not station or station == "Select a station":
			print(f"Please select a station on {line} first!")
			return
		
		# Check if selected station matches current line
		if self.currentLine.get() != line:
			print(f"Please select a station on {line}!")
			return
		
		stations = self.stations[line]
		try:
			currentIdx = stations.index(station)
			nextStation = stations[currentIdx + 1] if currentIdx < len(stations) - 1 else "the end of the line"
		except ValueError:
			nextStation = "the next station"
		
		doorSide = "both sides"
		
		announcement = (
			f"Train is arriving at {station}. "
			f"Doors will open on {doorSide}. "
			f"Next stop is {nextStation}."
		)
		
		print(f"ANNOUNCEMENT ({line}): {announcement}")
		
		# Send announcement through socket server to Train Model
		if self.parent and hasattr(self.parent, 'server') and self.parent.server:
			if hasattr(self.parent, 'train_model_connected') and self.parent.train_model_connected:
				self.parent.server.send_to_ui("Train Model", {
					'command': 'Announcement',
					'value': announcement,
					'train_id': 1
				})
				print(f"📢 Announcement sent to Train Model: {announcement}")
			else:
				print("⚠️ Not connected to Train Model - announcement not sent")
		else:
			print("⚠️ No socket server available - announcement not sent")
		
	def _announceEmergency(self):
		# Broadcasts emergency message.
		msg = self.emergencyText.get('1.0', 'end-1c').strip()
		if not msg:
			print("Please enter an emergency message first!")
			return
		
		print(f"EMERGENCY BROADCAST: {msg}")
		
		# Send emergency announcement through socket server to Train Model
		if self.parent and hasattr(self.parent, 'server') and self.parent.server:
			if hasattr(self.parent, 'train_model_connected') and self.parent.train_model_connected:
				self.parent.server.send_to_ui("Train Model", {
					'command': 'Announcement',
					'value': f"EMERGENCY: {msg}",
					'train_id': 1
				})
				print(f"📢 Emergency announcement sent to Train Model: {msg}")
			else:
				print("⚠️ Not connected to Train Model - emergency announcement not sent")
		else:
			print("⚠️ No socket server available - emergency announcement not sent")
		
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
	app = StationAnnouncementPanel(root)
	root.mainloop()