import json          # ← ADD
from pathlib import Path  # ← ADD

def load_socket_config():
    """Load socket configuration from config.json"""
    config_path = Path("config.json")
    config = {}  # ✅ Initialize config first
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading config.json: {e}")
        except Exception as e:
            print(f"Error loading config: {e}")
    else:
        print("Warning: config.json not found, using default configuration")
    
    return config.get("modules", {})

METERS_PER_SEC_TO_MPH = 2.23694  # 1 m/s = 2.23694 mph
MPH_TO_METERS_PER_SEC = 0.44704  # 1 mph = 0.44704 m/s
KW_TO_WATTS = 1000  # 1 kW = 1000 W
WATTS_TO_KW = 0.001  # 1 W = 0.001 kW

import tkinter as tk
from tkinter import ttk
import math
import time

from ClockDisplay import ClockDisplay
from BrakeButton import Brake_button
from Emlight import EmergencyLight
from speedometer import Speedometer
from SA_display import StationAnnouncementDisplay
from SA_window import StationAnnouncementWindow
from Test_UI import TestPanel
from SafetyMonitor import SafetyMonitor
from TC_SW_TrackInfo import TrackInformationPanel
from Engineer_UI import EngineerUI
from FailureIndicator import FailureIndicator
from ToggleButton import ToggleButton
from ModeToggle import Mode_Toggle
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer

# GREEN LINE PRELOADED TRACK INFORMATION
greenLineTrackInformation = {
    'segments': [
        # YARD to GLENBURY (initialization)
        {
            'from_station': 'YARD',
            'to_station': 'GLENBURY',
            'distance': 300.0,
            'from_block': 63,
            'to_block': 65,
            'station_block_half_length': 100.0,
            'speed_limit': 43.50
        },
        # Main loop segments
        {
            'from_station': 'GLENBURY',
            'to_station': 'DORMONT',
            'distance': 850.0,
            'from_block': 65,
            'to_block': 73,
            'station_block_half_length': 50.0,
            'speed_limit': 24.85
        },
        {
            'from_station': 'DORMONT',
            'to_station': 'MT LEBANON',
            'distance': 550.0,
            'from_block': 73,
            'to_block': 77,
            'station_block_half_length': 150.0,
            'speed_limit': 43.50
        },
        {
            'from_station': 'MT LEBANON',
            'to_station': 'POPLAR',
            'distance': 2936.6,
            'from_block': 77,
            'to_block': 88,
            'station_block_half_length': 50.0,
            'speed_limit': 15.53
        },
        {
            'from_station': 'POPLAR',
            'to_station': 'CASTLE SHANNON',
            'distance': 662.5,
            'from_block': 88,
            'to_block': 96,
            'station_block_half_length': 37.5,
            'speed_limit': 15.53
        },
        {
            'from_station': 'CASTLE SHANNON',
            'to_station': 'DORMONT',
            'distance': 740.0,
            'from_block': 96,
            'to_block': 105,
            'station_block_half_length': 50.0,
            'speed_limit': 24.85
        },
    ]
}

# RED LINE PRELOADED TRACK INFORMATION
redLineTrackInformation = {
    'segments': [
        # YARD to SHADYSIDE (initialization)
        {
            'from_station': 'YARD',
            'to_station': 'SHADYSIDE',
            'distance': 75.0,
            'from_block': 8,
            'to_block': 7,
            'station_block_half_length': 37.5,
            'speed_limit': 24.85
        },
        {
            'from_station': 'SHADYSIDE',
            'to_station': 'HERRON AVE',
            'distance': 362.5,
            'from_block': 7,
            'to_block': 16,
            'station_block_half_length': 25.0,
            'speed_limit': 24.85
        },
        {
            'from_station': 'HERRON AVE',
            'to_station': 'SWISSVILLE',
            'distance': 1300.0,
            'from_block': 16,
            'to_block': 21,
            'station_block_half_length': 50.0,
            'speed_limit': 34.17
        },
        {
            'from_station': 'SWISSVILLE',
            'to_station': 'PENN STATION',
            'distance': 325.0,
            'from_block': 21,
            'to_block': 25,
            'station_block_half_length': 25.0,
            'speed_limit': 43.50
        },
        {
            'from_station': 'PENN STATION',
            'to_station': 'STEEL PLAZA',
            'distance': 520.0,
            'from_block': 25,
            'to_block': 35,
            'station_block_half_length': 25.0,
            'speed_limit': 43.50
        },
    ]
}

# Station door side mapping
greenLineStationDoorSides = {
    'PIONEER': 'left',
    'EDGEBROOK': 'left',
    'LLC PLAZA': 'both',
    'WHITED': 'both',
    'SOUTH BANK': 'left',
    'CENTRAL': 'right',
    'INGLEWOOD': 'right',
    'OVERBROOK': 'right',
    'GLENBURY': 'right',
    'DORMONT': 'right',
    'MT LEBANON': 'both',
    'POPLAR': 'left',
    'CASTLE SHANNON': 'left'
}

redLineStationDoorSides = {
    'SHADYSIDE': 'both',
    'HERRON AVE': 'both',
    'SWISSVILLE': 'both',
    'PENN STATION': 'both',
    'STEEL PLAZA': 'both',
    'FIRST AVE': 'both',
    'STATION SQUARE': 'both',
    'SOUTH HILLS JUNCTION': 'both'
}

class PositionTracker:
    """Track train position along the route"""
    
    def __init__(self, track_info, station_door_sides):
        self.track_info = track_info
        self.station_door_sides = station_door_sides
        self.current_segment_index = 0
        self.distance_traveled_in_segment = 0.0
        self.last_update_time = None
        self.current_block = 63  # Default to Green Line yard
        self.is_at_station = False
        self.station_dwell_start_time = None
        
        # Constants
        self.DECELERATION_DISTANCE = 200.0  # meters
        self.STATION_STOP_THRESHOLD = 5.0   # meters
        self.STATION_DWELL_TIME = 3.0       # seconds
        
    def update(self, current_speed_ms):
        """Update position based on velocity and time"""
        current_time = time.time()
        
        if self.last_update_time is None:
            self.last_update_time = current_time
            return
        
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # If at station, handle dwell time
        if self.is_at_station:
            if self.station_dwell_start_time is not None:
                elapsed = current_time - self.station_dwell_start_time
                if elapsed >= self.STATION_DWELL_TIME:
                    # Move to next segment
                    self.current_segment_index += 1
                    if self.current_segment_index >= len(self.track_info['segments']):
                        self.current_segment_index = 1  # Loop back to main route
                    
                    self.distance_traveled_in_segment = 0.0
                    self.is_at_station = False
                    self.station_dwell_start_time = None
                    print(f"Departing for {self.get_next_station_name()}")
            return
        
        # Calculate displacement
        displacement = current_speed_ms * dt
        self.distance_traveled_in_segment += displacement
        
        # Check if arrived at station
        distance_remaining = self.get_distance_to_next_station()
        if distance_remaining <= self.STATION_STOP_THRESHOLD:
            self.is_at_station = True
            self.station_dwell_start_time = current_time
            self.distance_traveled_in_segment = self.track_info['segments'][self.current_segment_index]['distance']
            print(f"Arrived at {self.get_current_station_name()}")
        
        # Update current block
        self._update_current_block()
    
    def _update_current_block(self):
        """Update current block based on position"""
        if self.current_segment_index >= len(self.track_info['segments']):
            return
        
        segment = self.track_info['segments'][self.current_segment_index]
        from_block = segment['from_block']
        to_block = segment['to_block']
        total_distance = segment['distance']
        
        if total_distance > 0:
            progress = min(1.0, self.distance_traveled_in_segment / total_distance)
            
            # Simple linear interpolation between blocks
            if to_block > from_block:
                blocks_span = to_block - from_block
                self.current_block = from_block + int(progress * blocks_span)
            else:
                # Handle wrapping case
                self.current_block = from_block
    
    def get_distance_to_next_station(self):
        """Get distance remaining to next station in meters"""
        if self.current_segment_index >= len(self.track_info['segments']):
            return 0.0
        
        total_distance = self.track_info['segments'][self.current_segment_index]['distance']
        return total_distance - self.distance_traveled_in_segment
    
    def get_next_station_name(self):
        """Get name of next station"""
        if self.current_segment_index < len(self.track_info['segments']):
            return self.track_info['segments'][self.current_segment_index]['to_station']
        return "YARD"
    
    def get_current_station_name(self):
        """Get name of current station"""
        if self.current_segment_index < len(self.track_info['segments']):
            return self.track_info['segments'][self.current_segment_index]['to_station']
        return "YARD"
    
    def should_decelerate_for_station(self):
        """Check if train should start decelerating for station"""
        distance = self.get_distance_to_next_station()
        return distance <= self.DECELERATION_DISTANCE and not self.is_at_station
    
    def get_current_speed_limit(self):
        """Get speed limit for current segment in MPH"""
        if self.current_segment_index < len(self.track_info['segments']):
            return self.track_info['segments'][self.current_segment_index]['speed_limit']
        return 43.50  # Default
    
    def get_door_side(self):
        """Get which doors should open at current station"""
        station = self.get_current_station_name()
        return self.station_door_sides.get(station, 'both')



class Main_Window:
    def __init__(self, root, selected_line):
        self.root = root
        self.selected_line = selected_line
        self.root.title("Train Controller - Monitor Display")
        #add zoomed command to make screen fit 
        #self.root.attributes('-zoomed', True)  # On macOS/Linux
        self.root.configure(bg="navy")
        #self.root.attributes('-zoomed', True)  # On macOS/Linux
        #self.root.attributes('-zoomed', True)  # On macOS/Linux
        #self.root.state('zoomed') for windows

        # Make fullscreen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        #make resizable
        self.root.resizable(True, True)

        # Select line at startup
        
        
        # Initialize position tracker based on selected line
        if self.selected_line == 'GREEN':
            self.position_tracker = PositionTracker(greenLineTrackInformation, greenLineStationDoorSides)
            self.current_block = 63
        else:  # RED
            self.position_tracker = PositionTracker(redLineTrackInformation, redLineStationDoorSides)
            self.current_block = 8

        # Socket server setup
        #added socket server 
        module_config = load_socket_config()
        train_model_config = module_config.get("Train SW", {"port": 12346})
        self.server = TrainSocketServer(port=train_model_config["port"], ui_id="Train SW")
        
        self.server.set_allowed_connections(["Train Model", "Track Model", "Train HW"])
        self.server.start_server(self._process_message)
        self.server.connect_to_ui('localhost', 12345, "Train Model")
        self.server.connect_to_ui('localhost', 12344, "Track Model")
        self.server.connect_to_ui('localhost', 12347, "Train HW")
        
        main_container = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=5)
        main_container.place(relx=0.02, rely=0.08, relwidth=0.96, relheight=0.9)
        
        title_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=2)
        title_frame.place(relx=0.4, rely=0.01, relwidth=0.2, relheight=0.05)
        tk.Label(title_frame, text="Monitor Display", font=("Arial", 18, "bold"), 
                bg="white").pack(pady=5)
        
        # Track Info Button
        
        track_btn = tk.Button(self.root, text="Track Info", font=("Arial", 12, "bold"),
                              bg="lightblue", fg="black", relief=tk.RAISED, bd=2,
                              command=self.open_track_info)
        track_btn.place(relx=0.63, rely=0.015, relwidth=0.08, relheight=0.045)

        # Status Log Frame (Simple version for now)
        self.status_log_frame = tk.Frame(main_container, bg="black", relief=tk.SUNKEN, bd=2)
        self.status_log_frame.place(relx=.8, rely=.374, relwidth=0.18, relheight=0.3)
        
        tk.Label(self.status_log_frame, text="STATUS LOG", font=("Arial", 12, "bold"), 
                bg="black", fg="white").pack(pady=2)
        
        self.status_log = tk.Text(self.status_log_frame, height=6, width=50, 
                                 font=("Courier", 9), bg="black", fg="lime", 
                                 state=tk.DISABLED, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(self.status_log_frame, command=self.status_log.yview)
        self.status_log.config(yscrollcommand=scrollbar.set)
        self.status_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Driver Mode Frame
        self.driver_mode_frame = tk.Frame(main_container, bg="gray", relief=tk.RAISED, bd=2)
        self.driver_mode_frame.place(relx=0.38, rely=0.02, relwidth=0.24, relheight=0.14)
        
        tk.Label(self.driver_mode_frame, text="Driver Mode", font=("Arial", 14, "bold"), 
                bg="lightgrey", relief=tk.RAISED, padx=10).pack(pady=8)
        
        self.mode_select = Mode_Toggle(self.driver_mode_frame, callback=self.on_mode_change)
        self.mode_select.pack(pady=8)
        
        # Speedometer container - center
        speedometer_frame = tk.Frame(main_container, bg="white")
        speedometer_frame.place(relx=0.32, rely=0.18, relwidth=0.36, relheight=0.48)
        
        self.speedometer = Speedometer(speedometer_frame, max_speed=80)
        self.speedometer.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Current speed display below speedometer
        self.current_speed_display = tk.Label(speedometer_frame, text="Current Speed: 0 mph", 
                                             font=("Arial", 14, "bold"), bg="white", fg="navy")
        self.current_speed_display.pack(pady=5)
        
        # Commanded Speed Frame
        self.commanded_speed_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.commanded_speed_frame.place(relx=0.32, rely=0.69, relwidth=0.36, relheight=0.27)
        
        self.commanded_speed_frame.columnconfigure(0, weight=1)
        
        tk.Label(self.commanded_speed_frame, text="Commanded Speed:", 
                font=("Arial", 14, "bold"), bg="lightgrey", relief=tk.RAISED, 
                padx=15, pady=5).grid(row=0, column=0, pady=(8, 3), sticky="ew", padx=20)
        
        self.commanded_speed_value = tk.Label(self.commanded_speed_frame, text="40", 
                                             font=("Arial", 30, "bold"), bg="grey", fg="white")
        self.commanded_speed_value.grid(row=1, column=0, pady=3)
        
        tk.Label(self.commanded_speed_frame, text="Set Commanded:", 
                font=("Arial", 11, "bold"), bg="grey", fg="white").grid(row=2, column=0, pady=3)
        
        control_frame = tk.Frame(self.commanded_speed_frame, bg="grey")
        control_frame.grid(row=3, column=0, pady=5)
        
        up_btn = tk.Button(control_frame, text="▲", font=("Arial", 18, "bold"), 
                          command=self.increase_set_speed, width=3, height=1, bg="lightblue")
        up_btn.grid(row=0, column=0, padx=8)
        
        self.set_speed_value = tk.Label(control_frame, text="45", font=("Arial", 22, "bold"), 
                                       bg="black", fg="white", width=5, height=1, relief=tk.SUNKEN, bd=2)
        self.set_speed_value.grid(row=0, column=1, padx=8)
        
        tk.Label(control_frame, text="mph", font=("Arial", 13, "bold"), bg="grey", 
                fg="white").grid(row=0, column=2, padx=5)
        
        down_btn = tk.Button(control_frame, text="▼", font=("Arial", 18, "bold"), 
                            command=self.decrease_set_speed, width=3, height=1, bg="lightblue")
        down_btn.grid(row=0, column=3, padx=8)
        
        confirm_btn = tk.Button(self.commanded_speed_frame, text="CONFIRM", 
                               font=("Arial", 13, "bold"), bg="darkgreen", fg="white", 
                               command=self.confirm_speed, padx=25, pady=5)
        confirm_btn.grid(row=4, column=0, pady=8)
        
        # AC Frame
        self.ac_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.ac_frame.place(relx=0.02, rely=0.25, relwidth=0.18, relheight=0.35)

        self.ac_frame.columnconfigure(0, weight=1)

        tk.Label(self.ac_frame, text="Current Cabin Temperature:", 
                font=("Arial", 12, "bold"), bg="lightblue", wraplength=150).grid(row=0, column=0, 
                                                                                pady=10, padx=5, sticky="ew")

        self.current_temp = tk.Label(self.ac_frame, text="72°F", font=("Arial", 28, "bold"), 
                                    bg="grey", fg="white")
        self.current_temp.grid(row=1, column=0, pady=10)

        tk.Label(self.ac_frame, text="Set Temperature:", font=("Arial", 12, "bold"), 
                bg="lightblue").grid(row=2, column=0, pady=10, sticky="ew", padx=5)

        temp_control = tk.Frame(self.ac_frame, bg="grey")
        temp_control.grid(row=3, column=0, pady=10)

        # Store temp buttons as instance variables so we can disable them
        self.temp_up_btn = tk.Button(temp_control, text="▲", command=self.increase_temp, width=3, height=1,
                font=("Arial", 16, "bold"), bg="lightblue", state="disabled")  # Start disabled
        self.temp_up_btn.grid(row=0, column=0, padx=8)

        self.set_temp_value = tk.Label(temp_control, text="68°F", font=("Arial", 22, "bold"), 
                                    bg="black", fg="white", width=6, relief=tk.SUNKEN, bd=2)
        self.set_temp_value.grid(row=0, column=1, padx=8)

        self.temp_down_btn = tk.Button(temp_control, text="▼", command=self.decrease_temp, width=3, height=1,
                font=("Arial", 16, "bold"), bg="lightblue", state="disabled")  # Start disabled
        self.temp_down_btn.grid(row=0, column=2, padx=8)

        # AC control buttons frame
        ac_buttons_frame = tk.Frame(self.ac_frame, bg="grey")
        ac_buttons_frame.grid(row=4, column=0, pady=15)

        self.power_btn = ToggleButton(ac_buttons_frame, text="Power", 
                                    font=("Arial", 14, "bold"), 
                                    callback=self.toggle_ac, width=8, pady=5)
        self.power_btn.grid(row=0, column=0, padx=5)

        self.temp_confirm_btn = tk.Button(ac_buttons_frame, text="Confirm",
                                        font=("Arial", 14, "bold"),
                                        bg="darkgreen", fg="white",
                                        command=self.confirm_temperature,
                                        width=8, pady=5,
                                        state="disabled")  # Start disabled
        self.temp_confirm_btn.grid(row=0, column=1, padx=5)
        
        # Authority Frame
        self.authority_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.authority_frame.place(relx=0.02, rely=0.70, relwidth=0.22, relheight=0.25)
        
        tk.Label(self.authority_frame, text="Commanded\nAuthority:", 
                font=("Arial", 14, "bold"), bg="lightblue").pack(pady=10)
        
        blocks_frame = tk.Frame(self.authority_frame, bg="lightgrey", relief=tk.SUNKEN, bd=2)
        blocks_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.authority_value = tk.Label(blocks_frame, text="3 Blocks", 
                                       font=("Arial", 20, "bold"), bg="lightgrey")
        self.authority_value.pack(expand=True)
        
        # Train Horn Button
        try:
            self.train_horn_icon = tk.PhotoImage(file="train_controller_sw/trainhorn.png")
            self.train_horn_icon = self.train_horn_icon.subsample(8, 8)
            self.train_horn = tk.Button(main_container, image=self.train_horn_icon, 
                                       bg="burlywood1", activebackground="burlywood3",
                                       command=self.press_horn, relief=tk.RAISED, bd=3)
        except:
            self.train_horn = tk.Button(main_container, text="Train Horn\n", 
                                       font=("Arial", 14, "bold"), bg="burlywood1", 
                                       activebackground="burlywood3",
                                       command=self.press_horn, relief=tk.RAISED, bd=3)
        self.train_horn.place(relx=0.63, rely=0.06, relwidth=0.06, relheight=0.08)
        tk.Label(main_container, text="Train Horn", font=("Arial", 11, "bold"), 
         bg="white").place(relx=0.64, rely=0.03)
        
        # Service Brake Button
        self.service_brake = Brake_button(main_container, radius=70, color="orange", 
                                          hover_color="darkorange", active_color="orange4",
                                          text="Service\nBrake", command=self.service_brake_action,
                                          hold_mode=True, canvas_bg="white")
        self.service_brake.place(relx=.23, rely=.52)

        # Emergency Brake
        self.emergency_brake = Brake_button(main_container, radius=70, color="darkred", 
                                            hover_color="red", active_color="red4",
                                            text="Emergency\nBrake", 
                                            command=self.emergency_brake_activate, 
                                            canvas_bg="white",
                                            hold_mode=False)  # Single press activation
        self.emergency_brake.place(relx=.69, rely=.50)

        # Emergency Brake Release Switch (separate control)
        self.ebrake_release_frame = tk.Frame(main_container, bg="white")
        self.ebrake_release_frame.place(relx=.60, rely=.63)

        self.ebrake_release_btn = tk.Button(self.ebrake_release_frame, 
                                            text="Release\nE-Brake",
                                            font=("Arial", 10, "bold"), 
                                            bg="navy", fg="white",
                                            command=self.emergency_brake_release,
                                            width=10, height=2,
                                            state="disabled",  # Start disabled
                                            relief=tk.RAISED, bd=3)
        self.ebrake_release_btn.pack()
        
        # Emergency Light
        self.emergency_light = EmergencyLight(main_container, size=75)
        self.emergency_light.place(relx=.7, rely=.41)
        
        tk.Label(main_container, text="Emergency Signal", font=("Arial", 14, "bold"),
                bg="darkgray", fg="darkred").place(relx=.68, rely=.38)
        
        # Control Buttons Grid
        self.button_grid_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.button_grid_frame.place(relx=0.75, rely=0.68, relwidth=0.22, relheight=0.28)
        
        try:
            self.bulb_logo = tk.PhotoImage(file="train_controller_sw/bulb.png").subsample(9, 9)
            self.cabin_lights_btn = ToggleButton(self.button_grid_frame, image=self.bulb_logo,
                                                callback=self.toggle_cabin_lights)
            self.cabin_lights_btn.image = self.bulb_logo
        except:
            self.cabin_lights_btn = ToggleButton(self.button_grid_frame, text="", 
                                                font=("Arial", 24), callback=self.toggle_cabin_lights)
        self.cabin_lights_btn.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        
        try:
            self.headlight_logo = tk.PhotoImage(file="train_controller_sw/headlight.png").subsample(5, 5)
            self.headlights_btn = ToggleButton(self.button_grid_frame, image=self.headlight_logo,
                                              callback=self.toggle_headlights)
            self.headlights_btn.image = self.headlight_logo
        except:
            self.headlights_btn = ToggleButton(self.button_grid_frame, text="", 
                                              font=("Arial", 24), callback=self.toggle_headlights)
        self.headlights_btn.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        
        try:
            self.left_door_logo = tk.PhotoImage(file="train_controller_sw/leftdoor.png").subsample(10, 10)
            self.left_door_btn = ToggleButton(self.button_grid_frame, image=self.left_door_logo,
                                             callback=self.toggle_left_door)
            self.left_door_btn.image = self.left_door_logo
        except:
            self.left_door_btn = ToggleButton(self.button_grid_frame, text="", 
                                             font=("Arial", 24), callback=self.toggle_left_door)
        self.left_door_btn.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        
        try:
            self.right_door_logo = tk.PhotoImage(file="train_controller_sw/leftdoor.png").subsample(10, 10)
            self.right_door_btn = ToggleButton(self.button_grid_frame, image=self.right_door_logo,
                                              callback=self.toggle_right_door)
            self.right_door_btn.image = self.right_door_logo
        except:
            self.right_door_btn = ToggleButton(self.button_grid_frame, text="", 
                                              font=("Arial", 24), callback=self.toggle_right_door)
        self.right_door_btn.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        tk.Label(self.button_grid_frame, text="Left Door", font=("Arial", 10, "bold"), 
                        bg="grey", fg="white").grid(row=2, column=0, pady=(0,5))
        tk.Label(self.button_grid_frame, text="Right Door", font=("Arial", 10, "bold"), 
                        bg="grey", fg="white").grid(row=2, column=1, pady=(0,5))
        self.button_grid_frame.rowconfigure(2, weight=0)

        
        self.button_grid_frame.columnconfigure(0, weight=1)
        self.button_grid_frame.columnconfigure(1, weight=1)
        self.button_grid_frame.rowconfigure(0, weight=1)
        self.button_grid_frame.rowconfigure(1, weight=1)
        
        # BLT Logo
        logo_frame = tk.Frame(main_container, bg="white", relief=tk.RAISED, bd=1)
        logo_frame.place(relx=0.01, rely=0.01, relwidth=0.12, relheight=0.22)
        
        try:
            self.bltlogo = tk.PhotoImage(file="train_controller_sw/bltlogo.png").subsample(4, 4)
            self.bltLabel = tk.Label(logo_frame, image=self.bltlogo, bg="white", borderwidth=0)
            self.bltLabel.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
        except:
            self.bltLabel = tk.Label(logo_frame, text="BLT\nLOGO", font=("Arial", 14, "bold"), 
                                    bg="lightblue")
            self.bltLabel.pack(expand=True, fill=tk.BOTH)

        # Failure Indicators
        failure_frame = tk.Frame(main_container, bg="white")
        failure_frame.place(relx=0.16, rely=0.06, relwidth=0.13, relheight=0.12)

        tk.Label(failure_frame, text="System Failures", font=("Arial", 11, "bold"), 
                 bg="white", fg="black").pack(anchor="n", pady=(0, 3))

        lights_frame = tk.Frame(failure_frame, bg="white")
        lights_frame.pack(pady=2)

        # Train Engine Failure
        self.engine_failure = FailureIndicator(lights_frame, size=40, color="gray", glow_color="red")
        self.engine_failure.grid(row=0, column=0, padx=5)
        tk.Label(lights_frame, text="TEF", font=("Arial", 9, "bold"), bg="white", fg="black").grid(row=1, column=0)

        # Signal Pickup Failure
        self.signal_failure = FailureIndicator(lights_frame, size=40, color="gray", glow_color="orange")
        self.signal_failure.grid(row=0, column=1, padx=5)
        tk.Label(lights_frame, text="SPF", font=("Arial", 9, "bold"), bg="white", fg="black").grid(row=1, column=1)

        # Brake Failure
        self.brake_failure = FailureIndicator(lights_frame, size=40, color="gray", glow_color="yellow")
        self.brake_failure.grid(row=0, column=2, padx=5)
        tk.Label(lights_frame, text="BF", font=("Arial", 9, "bold"), bg="white", fg="black").grid(row=1, column=2)

        
        # Station Announcement Display
        self.station_display = StationAnnouncementDisplay(main_container, 
                                                         callback=self.on_station_announce,
                                                         expand_callback=self.expand_station_window)
        self.station_display.place(relx=0.70, rely=0.02, relwidth=0.28, relheight=0.35)
        
        self.station_window = StationAnnouncementWindow(self.root, 
                                                       callback=self.on_station_announce)
        
        # Clock frame
        self.clock_frame = tk.Label(self.root, bg="lightblue")
        self.clock_frame.place(relx=.3, rely=0.15)
        self.clock = ClockDisplay(self.clock_frame)
        self.clock.pack(padx=5, pady=5)

        #engineer control panel
        engineer_btn = tk.Button(self.root, text="Engineer Panel", 
                                font=("Arial", 12, "bold"),
                                bg="orange", fg="black", relief=tk.RAISED, bd=2,
                                command=self.toggle_engineer_ui)
        engineer_btn.place(relx=0.72, rely=0.015, relwidth=0.1, relheight=0.045)

         # State variables
        self.current_speed = 0  # Will be in mph (converted from m/s for display)
        self.current_speed_ms = 0  # Store original m/s value for calculations
        self.commanded_speed_ms = 0  # Store commanded speed in m/s for calculations
        self.set_speed = 45
        self.set_temp = 70
        self.is_auto_mode = True
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.door_safety_lock = True
        self.emergency_brake_auto_triggered = False
        self.commanded_authority = 0


        self.has_control_authority = False  # ←  Don't send power until we have authority
        
        # PID Control Parameters
        self.kp = 10.0  # Default proportional gain (will be updated from Engineer UI)
        self.ki = 2.0   # Default integral gain (will be updated from Engineer UI)
        self.max_power_kw = 120.0  # Maximum power in kW
        self.integral_error = 0.0  # For PI calculation (in m/s)
        self.sample_time = 0.1  # 100ms update rate
        self.last_power_sent = None  # Track last power to avoid duplicates

        #create engineer UI
        self.engineer_ui = EngineerUI(self, callback=self._onPIDParametersApplied)
        
        self.update_displays()
        # Test Panel
        #self.test_panel = TestPanel(self.root, self)

        #safety critical design:
        #self.safety_monitor = SafetyMonitor(self)

    def _process_message(self, message, source_ui_id):
        """Process incoming messages and update train state"""
        try:
            command = message.get('command')
            value = message.get('value')
            
            # ========== COMMANDED SPEED ==========
            if command == 'Commanded Speed':
                # Input: m/s from Train Model
                self.commanded_speed_ms = float(value)  # Store original m/s
                speed_mph = self.commanded_speed_ms * METERS_PER_SEC_TO_MPH
                self.set_commanded_speed(round(speed_mph, 1))
                self.add_to_status_log(f"Commanded: {speed_mph:.1f} mph ({self.commanded_speed_ms:.2f} m/s)")
            
            # ========== COMMANDED AUTHORITY ==========
            elif command == 'Commanded Authority':
                blocks = int(value)
                self.set_authority(blocks)
                self.add_to_status_log(f"Authority: {blocks} blocks")
            
            # ========== PASSENGER EMERGENCY SIGNAL ==========
            elif command == "Passenger Emergency Signal":
                is_active = bool(value)
                self.set_emergency_signal(is_active)
                if is_active and not self.emergency_brake_active:
                    self.emergency_brake_action(True)
                    self.add_to_status_log("🚨 Passenger emergency: E-brake activated!")
                elif not is_active:
                    self.add_to_status_log("Passenger emergency signal cleared")
            
            # ========== ACTUAL VELOCITY ==========
            elif command == "Current Speed":
                # Input: m/s from Train Model
                self.current_speed_ms = float(value)  # Store original m/s
                velocity_mph = self.current_speed_ms * METERS_PER_SEC_TO_MPH
                self.set_current_speed(velocity_mph)
                # Don't log every update - handled in power calculation
            
            # ========== CABIN TEMPERATURE ==========
            elif command == "Temp":
                temp_f = float(value)
                self.set_cabin_temp(round(temp_f, 1))
                if not hasattr(self, '_last_logged_temp') or abs(temp_f - self._last_logged_temp) >= 2:
                    self.add_to_status_log(f"Cabin temp: {temp_f:.1f}°F")
                    self._last_logged_temp = temp_f
            
            # ========== FAILURE MODES ==========
            elif command == "Brake Failure":
                is_failed = bool(value)
                self.handle_failure_mode("Brake Failure", is_failed)
                self.brake_failure.set_state(is_failed)
            
            elif command == "Signal Pickup Failure":
                is_failed = bool(value)
                self.handle_failure_mode("Signal Pickup Failure", is_failed)
                self.signal_failure.set_state(is_failed)
            
            elif command == "Train Engine Failure":
                is_failed = bool(value)
                self.handle_failure_mode("Train Engine Failure", is_failed)
                self.engine_failure.set_state(is_failed)
            
            elif command == 'PID Parameters':
                kp = message.get('kp', 10.0)
                ki = message.get('ki', 2.0)
                print(f"[RECEIVED] PID Parameters from TC_HW: Kp={kp:.1f}, Ki={ki:.1f}")
                if hasattr(self, 'engineer_ui'):
                    self.engineer_ui.receive_pid_parameters(kp, ki)
                    print(f"[APPLIED] PID Parameters sent to Engineer UI")
                else:
                    print(f"[WARNING] Engineer UI not initialized yet")
                return
            
            # ========== ADDITIONAL COMMANDS ==========
            elif command == "Beacon Data":
                self.add_to_status_log(f"Beacon: {value}")
            
            elif command == "Light States":
                self.add_to_status_log(f"Lights: {value}")
            
            else:
                print(f"Unknown command: {command}")
                
        except ValueError as e:
            print(f"Value conversion error for {command}: {e}")
            self.add_to_status_log(f"Invalid data for {command}")
        except Exception as e:
            print(f"Message processing error: {e}")
            self.add_to_status_log(f"Processing error")

    def set_pid_parameters(self, kp, ki):
        """Set PID parameters from engineer UI"""
        self.kp = kp
        self.ki = ki
        self.integral_error = 0.0  # Reset integral when parameters change
        self.add_to_status_log(f"PI params: Kp={kp:.1f}, Ki={ki:.2f}")
        print(f"PI parameters updated - Kp: {kp}, Ki: {ki}")

    def _onPIDParametersApplied(self, kp, ki):
        """Callback when PID parameters are applied in Engineer UI"""
        # Update the local PID controller
        self.kp = kp
        self.ki = ki
        self.add_to_status_log(f"✓ PID Updated: Kp={kp:.1f}, Ki={ki:.1f}")
        print(f"[DRIVER UI] PID parameters updated: Kp={kp:.1f}, Ki={ki:.1f}")

    def on_pid_change(self, kp, ki):
        """Callback when PID parameters change"""
        self.add_to_status_log(f"Engineer adjusted PID: Kp={kp:.1f}, Ki={ki:.1f}")
    
    def toggle_engineer_ui(self):
        """Show/hide engineer UI"""
        if self.engineer_ui.window.state() == 'normal':
            self.engineer_ui.hide()
        else:
            self.engineer_ui.show()


    def _handle_station_doors(self):
        """Open appropriate doors based on station platform"""
        door_side = self.position_tracker.get_door_side()
        
        if door_side == 'left' or door_side == 'both':
            self.send_left_door_signal(True)
            self.add_to_status_log("Left door opening")
        
        if door_side == 'right' or door_side == 'both':
            self.send_right_door_signal(True)
            self.add_to_status_log("Right door opening")
    
    def _close_all_doors(self):
        """Close all doors when departing"""
        self.send_left_door_signal(False)
        self.send_right_door_signal(False)
        self.add_to_status_log("Doors closing")
    
    def calculate_power_command(self):
        """Calculate power with authority-based speed adjustment"""
        # NEW: Update position tracking
        self.position_tracker.update(self.current_speed_ms)
        
        # SAME: Get base commanded speed (keep your existing logic)
        if self.is_auto_mode:
            commanded_speed_ms = self.commanded_speed_ms
        else:
            commanded_speed_mph = float(self.set_speed)
            commanded_speed_ms = commanded_speed_mph * MPH_TO_METERS_PER_SEC
        
        # NEW: Apply authority-based speed reduction
        if self.commanded_authority == 0:
            # No authority - brake to stop
            commanded_speed_ms = 0.0
            if not self.service_brake_active:
                self.service_brake_active = True
                self.send_service_brake(True)
                self.add_to_status_log("Authority 0: Braking to stop")
        elif self.commanded_authority == 1:
            # 50% of commanded speed
            commanded_speed_ms *= 0.5
        elif self.commanded_authority == 2:
            # 75% of commanded speed
            commanded_speed_ms *= 0.75
        elif self.commanded_authority == 3:
            # 100% of commanded speed (no change)
            pass
        else:  # authority >= 4
            # Maximum authority - no restriction
            pass
        
        # NEW: Apply speed limit from current segment
        speed_limit_mph = self.position_tracker.get_current_speed_limit()
        speed_limit_ms = speed_limit_mph * MPH_TO_METERS_PER_SEC
        commanded_speed_ms = min(commanded_speed_ms, speed_limit_ms)
        
        # NEW: Handle station approach
        if self.position_tracker.should_decelerate_for_station():
            dist_to_station = self.position_tracker.get_distance_to_next_station()
            DECEL_RATE = 1.0
            if dist_to_station > 0:
                target_speed = (2 * DECEL_RATE * dist_to_station) ** 0.5
                commanded_speed_ms = min(commanded_speed_ms, target_speed)
        
        # NEW: Handle station stop and door control
        if self.position_tracker.is_at_station:
            commanded_speed_ms = 0.0
            if not self.service_brake_active:
                self.service_brake_active = True
                self.send_service_brake(True)
                self._handle_station_doors()
        elif self.service_brake_active and self.commanded_authority > 0:
            # Release brake when leaving station
            self.service_brake_active = False
            self.send_service_brake(False)
            self._close_all_doors()
        
        # SAME: PI controller calculation (keep your existing PI logic)
        current_speed_ms = self.current_speed_ms
        velocity_error = commanded_speed_ms - current_speed_ms
        
        self.integral_error += velocity_error * self.sample_time
        max_integral = self.max_power_kw / (self.ki if self.ki > 0 else 1.0)
        self.integral_error = max(-max_integral, min(max_integral, self.integral_error))
        
        p_term = self.kp * velocity_error
        i_term = self.ki * self.integral_error
        power_kw = p_term + i_term
        
        power_kw = max(0.0, min(self.max_power_kw, power_kw))
        
        return power_kw

    def on_closing(self):
        """Handle application closing"""
        print("Closing application...")
        
        # Close engineer UI
        if hasattr(self, 'engineer_ui'):
            self.engineer_ui.window.destroy()
        
        # Close server
        self.server.running = False
        if self.server.server_socket:
            try:
                self.server.server_socket.close()
            except:
                pass
        
        self.root.destroy()

    
    def add_to_status_log(self, message):
        """Add timestamped message to status log"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_log.config(state=tk.NORMAL)
        self.status_log.insert(tk.END, f"[{timestamp}] {message}\n")
        # Keep only last 100 lines to prevent memory issues
        lines = self.status_log.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.status_log.delete(1.0, f"{len(lines)-100}.0")
        self.status_log.see(tk.END)
        self.status_log.config(state=tk.DISABLED)

    def handle_failure_mode(self, failure_type, is_active):
        """Handle failure mode activation/deactivation"""
        if is_active:
            # Failure detected - auto-activate emergency brake
            self.add_to_status_log(f"CRITICAL: {failure_type} detected!")
            
            if not self.emergency_brake_active:
                self.emergency_brake_activate()
                self.emergency_brake_auto_triggered = True
                self.add_to_status_log("Emergency brake auto-activated due to failure!")
                print(f"EMERGENCY BRAKE AUTO-ACTIVATED: {failure_type}")
        else:
            # Failure cleared
            self.add_to_status_log(f"✓ {failure_type} cleared")
            
            # Update release button state (may enable it now)
            self.update_ebrake_release_state()
    
    def update_displays(self):
        """Update all displays"""
        # SAME: Keep all your existing display updates
        # Just add these new station info updates if you added those labels
        
        # NEW: Update station information displays (if you added them)
        if hasattr(self, 'next_station_label'):
            next_station = self.position_tracker.get_next_station_name()
            distance = self.position_tracker.get_distance_to_next_station()
            self.next_station_label.config(text=next_station)
            
        if hasattr(self, 'distance_label'):
            distance = self.position_tracker.get_distance_to_next_station()
            self.distance_label.config(text=f"Distance: {int(distance)} m")
        
        # SAME: Keep all your existing speed/brake/power logic
        # Calculate and send power (your existing code)
        if not self.emergency_brake_active and not self.service_brake_active:
            try:
                power_kw = self.calculate_power_command()
                power_watts = power_kw * KW_TO_WATTS
                
                if self.last_power_sent is None or abs(power_watts - self.last_power_sent) > 100:
                    self.send_setpoint_power(power_kw)
                    self.last_power_sent = power_watts
            except Exception as e:
                print(f"Error in power calculation: {e}")
        else:
            if self.last_power_sent != 0:
                self.send_setpoint_power(0.0)
                self.last_power_sent = 0
        
        # SAME: Keep your existing schedule
        self.root.after(100, self.update_displays)

    
    def apply_brake_effect(self):
        """Apply brake effects to current speed"""
        if self.emergency_brake_active:
            # Emergency brake active - ensure integral error resets
            self.integral_error = 0.0
            # Note: actual deceleration handled by Train Model (2.73 m/s²)
            
        elif self.service_brake_active:
            # Service brake active - ensure integral error resets
            self.integral_error = 0.0
            # Note: actual deceleration handled by Train Model (1.2 m/s²)
    
    def update_door_safety(self):
        """Update door safety based on current speed"""
        if self.current_speed > 0 and not self.door_safety_lock:
            # Train is moving but doors aren't locked - force close
            self.door_safety_lock = True
            if self.left_door_btn.is_on:
                self.left_door_btn.toggle()  # Close left door
                self.add_to_status_log("Left door auto-closed: train moving")
            if self.right_door_btn.is_on:
                self.right_door_btn.toggle()  # Close right door
                self.add_to_status_log("Right door auto-closed: train moving")
        
        # Update door button states based on safety lock
        door_state = "normal" if self.current_speed == 0 else "disabled"
        self.left_door_btn.config(state=door_state)
        self.right_door_btn.config(state=door_state)
    
    def on_brake_percent_change(self, event):
        """Handle brake percentage selection from dropdown"""
        percent_str = self.brake_percent_var.get()
        self.service_brake_percentage = int(percent_str.replace('%', ''))
        self.brake_percentage_display.config(text=f"Service Brake: {self.service_brake_percentage}%")
        if self.service_brake_active:
            self.add_to_status_log(f"Service brake percentage changed to {self.service_brake_percentage}%")
    
    def on_mode_change(self, mode):
        self.is_auto_mode = (mode == "auto")
        #self.send_drivetrain_mode(self.is_auto_mode)  # Send to train model
        self.add_to_status_log(f"Driver mode changed to: {mode}")
        print(f"Mode changed to: {mode}")
    
    def increase_set_speed(self):
        if self.is_auto_mode:
            self.mode_select.set_mode("manual")
        self.set_speed = min(80, self.set_speed + 5)
        self.set_speed_value.config(text=str(self.set_speed))
        self.add_to_status_log(f"Set speed increased to: {self.set_speed} mph")
    
    def decrease_set_speed(self):
        if self.is_auto_mode:
            self.mode_select.set_mode("manual")
        self.set_speed = max(0, self.set_speed - 5)
        self.set_speed_value.config(text=str(self.set_speed))
        self.add_to_status_log(f"Set speed decreased to: {self.set_speed} mph")
    
    def confirm_speed(self):
        """Callback when speed is confirmed in manual mode"""
        if not self.is_auto_mode:
            self.commanded_speed_value.config(text=str(self.set_speed))
            # Reset integral error when manually changing speed
            self.integral_error = 0.0
            self.add_to_status_log(f"Manual speed: {self.set_speed} mph")
            print(f"Manual commanded speed: {self.set_speed} mph")

    def increase_temp(self):
        """Increase temperature setpoint - only works when AC is on"""
        if self.power_btn.is_on:  # Only allow if AC is on
            self.set_temp = min(85, self.set_temp + 1)
            self.set_temp_value.config(text=f"{self.set_temp}°F")
            self.add_to_status_log(f"Temperature adjusted to: {self.set_temp}°F (not sent yet)")
            print(f"Set temperature: {self.set_temp}°F")
        else:
            self.add_to_status_log("Cannot adjust temp: AC is OFF")

    def decrease_temp(self):
        """Decrease temperature setpoint - only works when AC is on"""
        if self.power_btn.is_on:  # Only allow if AC is on
            self.set_temp = max(60, self.set_temp - 1)
            self.set_temp_value.config(text=f"{self.set_temp}°F")
            self.add_to_status_log(f"Temperature adjusted to: {self.set_temp}°F (not sent yet)")
            print(f"Set temperature: {self.set_temp}°F")
        else:
            self.add_to_status_log("Cannot adjust temp: AC is OFF")

    def confirm_temperature(self):
        """Send the temperature setpoint when Confirm is pressed"""
        if self.power_btn.is_on:
            self.send_cabin_temperature_control(self.set_temp)
            self.add_to_status_log(f"✓ Temperature setpoint confirmed: {self.set_temp}°F")
            print(f"Temperature setpoint sent: {self.set_temp}°F")
        else:
            self.add_to_status_log("Cannot confirm temp: AC is OFF")

    def toggle_ac(self, state):
        """Toggle AC and enable/disable temperature controls"""
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"AC Power: {status}")
        
        # Enable/disable temperature controls based on AC state
        button_state = "normal" if state else "disabled"
        self.temp_up_btn.config(state=button_state)
        self.temp_down_btn.config(state=button_state)
        self.temp_confirm_btn.config(state=button_state)
        
        if state:
            print(f"AC ON - Use Confirm button to send temperature")
        else:
            print("AC OFF")
    
    def press_horn(self):
        self.add_to_status_log("Train horn activated")
        self.send_train_horn(True)  # Horn on
        print("Train horn pressed!")

        self.root.after(2000, lambda: self.send_train_horn(False))
    
    def service_brake_action(self, pressed):
        """Handle service brake button press/release - BOOLEAN VERSION"""
        print(f"[DEBUG] Service brake action called: pressed={pressed}")
        
        if pressed:
            self.service_brake_active = True
            self.send_service_brake(True)  # Send True (brake ON)
            self.add_to_status_log(f" Service brake applied")
            print(f"SERVICE BRAKE: ACTIVE")
        else:
            self.service_brake_active = False
            self.send_service_brake(False)  # Send False (brake OFF)
            self.add_to_status_log(" Service brake released")
            print("SERVICE BRAKE: RELEASED")
    
    
    def emergency_brake_activate(self, pressed=None):
        """Activate emergency brake (single press, no release)"""
        if not self.emergency_brake_active:
            self.emergency_brake_active = True
            self.emergency_light.activate()
            self.send_emergency_brake_signal(True)
            self.add_to_status_log("EMERGENCY BRAKE ACTIVATED!")
            print("EMERGENCY BRAKE ACTIVATED!")
            
            # Darken the button to show it's active
            self.emergency_brake.canvas.itemconfig(self.emergency_brake.button, fill="red4")
            
            # Check if we can enable release button (only at zero speed)
            self.update_ebrake_release_state()

    def emergency_brake_release(self):
        """Release emergency brake - only works when speed is zero"""
        if self.current_speed > 0.1:
            self.add_to_status_log("Cannot release E-brake: Train still moving!")
            print("E-brake release DENIED - train moving")
            return
        
        # Check for active failures
        failure_detected = (
            self.engine_failure.active or
            self.signal_failure.active or
            self.brake_failure.active
        )
        
        if failure_detected:
            self.add_to_status_log("Cannot release E-brake: Active system failure!")
            print("E-brake release DENIED - failure active")
            return
        
        # Safe to release
        self.emergency_brake_active = False
        self.emergency_brake_auto_triggered = False
        self.emergency_light.deactivate()
        self.send_emergency_brake_signal(False)
        
        # Reset button to default color
        self.emergency_brake.canvas.itemconfig(self.emergency_brake.button, fill="darkred")
        
        # Disable release button
        self.ebrake_release_btn.config(state="disabled", bg="darkgray")
        
        self.add_to_status_log("✓ Emergency brake released")
        print("Emergency brake released manually")

    def update_ebrake_release_state(self):
        """Enable/disable E-brake release button based on conditions"""
        if not self.emergency_brake_active:
            # E-brake not active, keep release button disabled
            self.ebrake_release_btn.config(state="disabled", bg="darkgray")
            return
        
        # E-brake is active - check if we can enable release
        no_failures = not (
            self.engine_failure.active or
            self.signal_failure.active or
            self.brake_failure.active
        )
        
        at_zero_speed = self.current_speed <= 0.1
        
        if no_failures and at_zero_speed:
            # Safe to allow release
            self.ebrake_release_btn.config(state="normal", bg="green")
        else:
            # Not safe yet
            self.ebrake_release_btn.config(state="disabled", bg="darkgray")
    
    def toggle_cabin_lights(self, state):
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"Cabin lights: {status}")
        self.send_cabin_lights(state)  # Send to train model
        print(f"Cabin lights: {status}")
    
    def toggle_headlights(self, state):
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"Headlights: {status}")
        self.send_headlights(state)  # Send to train model
        print(f"Headlights: {status}")
    
    def toggle_left_door(self, state):
        if self.current_speed > 0:
            self.add_to_status_log("Left door: REQUEST DENIED - Train moving")
            return
            
        status = "OPEN" if state else "CLOSED"
        self.send_left_door_signal(state)  # Send to train model
        self.add_to_status_log(f"Left door: {status}")
        print(f"Left door: {status}")
    
    def toggle_right_door(self, state):
        if self.current_speed > 0:
            self.add_to_status_log("Right door: REQUEST DENIED - Train moving")
            return
            
        status = "OPEN" if state else "CLOSED"
        self.add_to_status_log(f"Right door: {status}")
        self.send_right_door_signal(state)  # Send to train model
        print(f"Right door: {status}")
    
    def open_station_window(self):
        self.station_window.show_window()
    
    def expand_station_window(self):
        self.station_window.show_window()
    
    def on_station_announce(self, line, station):
        message = f"{station} on {line}"
        self.add_to_status_log(f"Station announcement: {message}")
        self.send_station_announcement(message)  # Send to train model
        print(f"Announcing: {station} on {line}")
    
    def set_current_speed(self, speed):
        """Set current speed and update displays"""
        self.current_speed = speed
        self.speedometer.update_speed(speed)
        self.current_speed_display.config(text=f"Current Speed: {int(speed)} mph")
    
    def set_commanded_speed(self, speed):
        """Set commanded speed from external input"""
        if self.is_auto_mode:
            self.commanded_speed_value.config(text=str(speed))
    
    def set_authority(self, blocks):
        """Set authority from external input"""
        self.commanded_authority = blocks
        self.authority_value.config(text=f"{blocks} Blocks")
    
    def set_cabin_temp(self, temp):
        """Set cabin temperature from external input"""
        self.current_temp.config(text=f"{temp}°F")
    
    def set_emergency_signal(self, active):
        """Control emergency light from external module"""
        self.emergency_light.set_state(active)
    
    def set_service_brake_percentage(self, percentage):
        """Set service brake percentage from test panel"""
        self.service_brake_percentage = percentage
        self.brake_percentage_display.config(text=f"Service Brake: {percentage}%")
        # Update dropdown to match
        self.brake_percent_var.set(f"{percentage}%")
        if self.service_brake_active:
            self.add_to_status_log(f"Service brake percentage set to {percentage}%")

    def check_failure_modes(self):
        """Activate emergency brake automatically if any failure mode is active"""
        failure_detected = (
            self.engine_failure.active or
            self.signal_failure.active or
            self.brake_failure.active
        )

        if failure_detected and not self.emergency_brake_active:
            # Automatically activate the emergency brake
            self.add_to_status_log(" FAILURE DETECTED: Activating emergency brake.")
            self.emergency_brake_action(True)
        elif not failure_detected and self.emergency_brake_active:
            # Automatically release when all failures are cleared
            self.add_to_status_log(" All failures cleared: Releasing emergency brake.")
            self.emergency_brake_action(False)


    def open_track_info(self):
        """Opens the Track Information Panel"""
        if not hasattr(self, "track_info_window") or not tk.Toplevel.winfo_exists(self.track_info_window):
            self.track_info_window = tk.Toplevel(self.root)
            self.track_info_window.title("Track Information Panel")
            self.track_info_panel = TrackInformationPanel(self.track_info_window)
        else:
            self.track_info_window.lift()

    def send_setpoint_power(self, power_kw):
        """
        Send setpoint power to Train Model
        Input: power in kW
        Output: power in kW (Train Model expects kW)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Power Command",
                'value': float(power_kw *  1000),
                'train_id' : 2
            })
            # Don't print every power command to avoid spam
            # print(f"Sent power: {power_kw:.2f} kW")
        except Exception as e:
            print(f"Error sending power: {e}")
            self.add_to_status_log("⚠️ Failed to send power command")


    def send_emergency_brake_signal(self, is_active):
        """
        Send emergency brake signal to Train Model
        Input: boolean
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Emergency Brake Signal",
                'value': bool(is_active), 
                'train_id' : 2
            })
            print(f"Sent emergency brake signal: {is_active}")
        except Exception as e:
            print(f"Error sending emergency brake signal: {e}")


    def send_headlights(self, is_on):
        """
        Send headlights state to Train Model
        Input: boolean
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Headlights",
                'value': bool(is_on), 
                'train_id' : 2
            })
            print(f"Sent headlights: {is_on}")
        except Exception as e:
            print(f"Error sending headlights: {e}")


    def send_cabin_lights(self, is_on):
        """
        Send cabin lights state to Train Model
        Input: boolean
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Cabin Lights",
                'value': bool(is_on), 
                'train_id' : 2
            })
            print(f"Sent cabin lights: {is_on}")
        except Exception as e:
            print(f"Error sending cabin lights: {e}")


    def send_left_door_signal(self, is_open):
        """
        Send left door signal to Train Model
        Input: boolean (True = open, False = closed)
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Left Door Signal",
                'value': bool(is_open), 
                "train_id": 2
            })
            print(f"Sent left door signal: {is_open}")
        except Exception as e:
            print(f"Error sending left door signal: {e}")


    def send_right_door_signal(self, is_open):
        """
        Send right door signal to Train Model
        Input: boolean (True = open, False = closed)
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Right Door Signal",
                'value': bool(is_open), 
                'train_id' : 2
            })
            print(f"Sent right door signal: {is_open}")
        except Exception as e:
            print(f"Error sending right door signal: {e}")



    def send_cabin_temperature_control(self, temp_fahrenheit):
        """
        Send cabin temperature setpoint to Train Model
        Input: temperature in Fahrenheit
        Output: temperature in Fahrenheit (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Temp",
                'value': float(temp_fahrenheit), 
                'train_id' : 2
            })
            print(f"Sent temperature setpoint: {temp_fahrenheit}°F")
        except Exception as e:
            print(f"Error sending temperature setpoint: {e}")

    '''
    def send_drivetrain_mode(self, is_auto):
        """
        Send drivetrain mode to Train Model
        Input: boolean (True = auto, False = manual)
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Drivetrain Mode",
                'value': bool(is_auto), 
                'train_id' : 2
            })
            print(f"Sent drivetrain mode: {'auto' if is_auto else 'manual'}")
        except Exception as e:
            print(f"Error sending drivetrain mode: {e}")
    '''

    def send_service_brake(self, is_active):
        """
        Send service brake to Train Model
        Input: boolean (True = brake on, False = brake off)
        Output: boolean (no conversion needed)
        
        Note: When service brake is active, send True.
        When released, send False.
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Service Brake",
                'value': bool(is_active), 
                'train_id' : 2
            })
            status = "ACTIVE" if is_active else "RELEASED"
            print(f"[SENT] Service Brake: {status} (value={is_active})")
        except Exception as e:
            print(f"[ERROR] Failed to send service brake: {e}")
            self.add_to_status_log("⚠️ Failed to send service brake")

    def send_station_announcement(self, message):
        """
        Send station announcement message to Train Model
        Input: string message
        Output: string (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Announcement",
                'value': str(message), 
                'train_id' : 2
            })
            print(f"Sent station announcement: {message}")
        except Exception as e:
            print(f"Error sending station announcement: {e}")


    def send_train_horn(self, is_active):
        """
        Send train horn signal to Train Model
        Input: boolean (True = horn on, False = horn off)
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Train Horn",
                'value': bool(is_active), 
                'train_id' : 2
            })
            print(f"Sent train horn: {is_active}")
        except Exception as e:
            print(f"Error sending train horn: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window until line is selected

    # --- Create selection dialog ---
    dialog = tk.Toplevel(root)
    dialog.title("Train Line Selection")
    dialog.geometry("400x250")
    dialog.configure(bg='#1e3c72')
    dialog.grab_set()   # Make modal
    dialog.focus_set()

    tk.Label(dialog, text="SELECT TRAIN LINE SW", font=("Arial", 20, "bold"),
             bg='#1e3c72', fg='white', pady=20).pack()

    selection = {"line": None}

    def choose(line):
        selection["line"] = line
        dialog.destroy()

    frame = tk.Frame(dialog, bg="#1e3c72")
    frame.pack(expand=True)

    tk.Button(frame, text="GREEN LINE", font=("Arial", 16, "bold"),
              bg="#27ae60", fg="white", width=12, height=2,
              command=lambda: choose("GREEN")).pack(side="left", padx=10)

    tk.Button(frame, text="RED LINE", font=("Arial", 16, "bold"),
              bg="#e74c3c", fg="white", width=12, height=2,
              command=lambda: choose("RED")).pack(side="left", padx=10)

    # Wait for dialog result
    root.wait_window(dialog)

    # --- Now show main window with selection ---
    root.deiconify()  
    app = Main_Window(root, selected_line=selection["line"])

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
