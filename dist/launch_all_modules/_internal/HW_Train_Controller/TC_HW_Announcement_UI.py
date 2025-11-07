import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

class StationAnnouncementPanel:
	# UI panel for train station announcements.
	
	"""
	Attributes:
		root: The main tkinter window
		stations: Dictionary mapping line names to station lists
		selectedStation: StringVar holding the currently selected station
		notebook: ttk Notebook widget for tabs
		emergencyText: Text widget for emergency messages
		timeLabelBlue: Label showing time on Blue Line tab
		timeLabelEmergency: Label showing time on Emergency tab
	"""
	
	def __init__(self, root):
		# Initializes the station announcement panel.
		self.root = root
		self.root.title("STATION ANNOUNCEMENT PANEL")
		self.root.geometry("400x600")
		self.root.configure(bg='#2c3e50')
		
		self.stations = {
			'Blue Line': ['Station B', 'Station C']
		}
		
		self.selectedStation = tk.StringVar()
		
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
		
		self._createBlueLineTab()
		self._createEmergencyTab()
		
	def _createBlueLineTab(self):
		# Creates the Blue Line station selection tab.
		frame = tk.Frame(self.notebook, bg='#d0e8f5')
		self.notebook.add(frame, text='Blue Line')
		
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
		
		self.timeLabelBlue = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#2c3e50',
			fg='white',
			padx=20,
			pady=8
		)
		self.timeLabelBlue.pack()
		
		# Blue Line title
		title = tk.Label(
			frame,
			text="Blue Line",
			font=('Arial', 24, 'bold'),
			bg='#1a5490',
			fg='white',
			relief='raised',
			bd=4,
			padx=40,
			pady=15
		)
		title.pack(pady=30)
		
		# Station dropdown menu
		stationsFrame = tk.Frame(frame, bg='#d0e8f5')
		stationsFrame.pack(expand=True, pady=20)
		
		self.selectedStation.set("Select a Station")
		
		dropdownFrame = tk.Frame(stationsFrame, bg='#3498db', relief='sunken', bd=2)
		dropdownFrame.pack()
		
		stationDropdown = tk.OptionMenu(
			dropdownFrame,
			self.selectedStation,
			*self.stations['Blue Line'],
			command=lambda s: self._selectStation(s, 'Blue Line')
		)
		stationDropdown.config(
			font=('Arial', 16),
			bg='#3498db',
			fg='white',
			activebackground='#2980b9',
			activeforeground='white',
			width=25,
			height=2,
			relief='flat',
			bd=0,
			highlightthickness=0,
			anchor='w'
		)
		stationDropdown['menu'].config(
			font=('Arial', 14),
			bg='#3498db',
			fg='white'
		)
		stationDropdown.pack(pady=15)
		
		# Announce button
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
			command=lambda: self._announceStation('Blue Line'),
			width=18,
			height=2
		)
		announceBtn.pack()
		
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
		
		self.timeLabelEmergency = tk.Label(
			timeFrame,
			text="",
			font=('Arial', 16, 'bold'),
			bg='#2c3e50',
			fg='white',
			padx=20,
			pady=8
		)
		self.timeLabelEmergency.pack()
		
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
			text="Emergency Msg.",
			font=('Arial', 14, 'bold'),
			bg='#ffe8e8',
			fg='#2c3e50'
		)
		msgLabel.pack(anchor='w', pady=(0, 10))
		
		textFrame = tk.Frame(msgContainer, bg='#2c3e50', relief='raised', bd=3)
		textFrame.pack(fill='both', expand=True)
		
		self.emergencyText = tk.Text(
			textFrame,
			height=8,
			font=('Arial', 12),
			bg='white',
			fg='#2c3e50',
			wrap='word',
			relief='flat',
			bd=0
		)
		self.emergencyText.pack(fill='both', expand=True, padx=3, pady=3)
		
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
		if station == "Select a station":
			return
		self.selectedStation.set(station)
		print(f"Selected: {station} on {line}")
		
	def _announceStation(self, line):
		# Broadcasts station arrival announcement.
		station = self.selectedStation.get()
		if not station or station == "Select a station":
			print("Please select a station first!")
			return
		
		stations = self.stations[line]
		currentIdx = stations.index(station)
		nextStation = stations[currentIdx + 1] if currentIdx < len(stations) - 1 else "the end of the line"
		doorSide = "both sides"
		
		announcement = (
			f"Train is arriving at {station}. "
			f"Doors will open on {doorSide}. "
			f"Next stop is {nextStation}."
		)
		
		print(f"ANNOUNCEMENT: {announcement}")
		
	def _announceEmergency(self):
		# Broadcasts emergency message.
		msg = self.emergencyText.get('1.0', 'end-1c').strip()
		if not msg:
			print("Please enter an emergency message first!")
			return
		
		print(f"EMERGENCY BROADCAST: {msg}")
		
	def _updateTime(self):
		# Updates the time display on all tabs.
		now = datetime.now()
		timeStr = now.strftime("%#m/%#d/%y %#I:%M %p") if os.name == 'nt' else now.strftime("%-m/%-d/%y %-I:%M %p")
		
		if hasattr(self, 'timeLabelBlue'):
			self.timeLabelBlue.config(text=timeStr)
		if hasattr(self, 'timeLabelEmergency'):
			self.timeLabelEmergency.config(text=timeStr)
			
		self.root.after(1000, self._updateTime)

if __name__ == "__main__":
	root = tk.Tk()
	app = StationAnnouncementPanel(root)
	root.mainloop()