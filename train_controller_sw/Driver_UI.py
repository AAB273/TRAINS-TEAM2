import json          
from pathlib import Path 

def load_socket_config():
    """Load socket configuration from config.json"""
    config_path = Path("config.json")
    config = {}  #  Initialize config first
    
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
import pygame
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

# GREEN LINE underground blocks
greenLineUndergroundBlocks = {36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 
                      53, 54, 55, 56, 57, 122, 123, 124, 125, 126, 127, 128, 129, 130, 
                      131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 142, 143}

# RED LINE underground blocks
redLineUndergroundBlocks = {24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
                            67, 68, 69, 70, 71, 72, 73, 74, 75, 76}

# Special case: INGLEWOOD at block 132 uses left door instead of right
STATION_DOOR_EXCEPTIONS = {
    132: 'left'  # INGLEWOOD at block 132 uses left door
}

# Position Tracking Module - Based on TC_HW Working Implementation
# This should replace the PositionTracker class in Driver_UI.py

class PositionTracker:
    """Track train position along the route - TC_HW style implementation"""
    def __init__(self, track_info, station_door_sides, selected_line):
        self.track_info = track_info
        self.station_door_sides = station_door_sides
        self.selected_line = selected_line
        
        # Set underground blocks based on selected line
        if selected_line == 'GREEN':
            self.underground_blocks = greenLineUndergroundBlocks
        else:  # RED
            self.underground_blocks = redLineUndergroundBlocks
        
        self.current_segment_index = 0
        self.distance_traveled_in_segment = 0.0
        self.distance_to_next_station = 0.0
        self.last_update_time = None
        self.current_block = 63 if selected_line == 'GREEN' else 8
        self.is_at_station = False
        self.station_dwell_start_time = None
        
        # Track underground state
        self.is_underground = self.current_block in self.underground_blocks
        self.last_underground_state = self.is_underground
        
        # Constants - MATCHING TC_HW
        self.DECELERATION_DISTANCE = 200.0  # meters
        self.STATION_STOP_THRESHOLD = 5.0   # meters
        self.STATION_DWELL_TIME = 30.0      # seconds
        self.TIME_SCALE = 10.0  # 10x faster simulation
        
        # Door safety
        self.doors_open_at_station = False
        self.doors_locked = False
        
        # Initialize distance to next station
        if len(self.track_info['segments']) > 0:
            self.distance_to_next_station = self.track_info['segments'][0]['distance']
        
    def update(self, current_speed_ms, ui_callback=None):
        """
        Update position based on velocity and time - TC_HW STYLE
        
        Key differences from old implementation:
        1. Simple station detection (no complex arrival logic)
        2. Early return when at station
        3. Direct brake control integration
        """
        current_time = time.time()
        
        # Initialize timing on first call
        if self.last_update_time is None:
            self.last_update_time = current_time
            return
        
        # Calculate time elapsed since last update
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Apply time acceleration
        dt = dt * self.TIME_SCALE
        
        # Check and update underground status
        self._update_underground_status(ui_callback)
        
        # Door safety: Lock doors when train is moving
        if current_speed_ms > 1.0 and not self.doors_locked:
            self.doors_locked = True
            if ui_callback and hasattr(ui_callback, 'lock_doors'):
                ui_callback.lock_doors()
        
        # ===== AT STATION LOGIC (TC_HW STYLE) =====
        if self.is_at_station:
            # Check if dwell time is complete
            if self.station_dwell_start_time is not None:
                dwell_elapsed = current_time - self.station_dwell_start_time
                
                # Display remaining dwell time
                if not hasattr(self, '_last_dwell_print'):
                    self._last_dwell_print = 0
                self._last_dwell_print += 1
                
                if self._last_dwell_print % 10 == 0:
                    remaining = max(0, self.STATION_DWELL_TIME - dwell_elapsed)
                    if ui_callback and hasattr(ui_callback, 'add_to_status_log'):
                        ui_callback.add_to_status_log(f"Station dwell: {int(remaining)}s remaining")
                    self._last_dwell_print = 0
                
                if dwell_elapsed >= self.STATION_DWELL_TIME:
                    station_name = self.get_current_station_name()
                    print(f"[POSITION] Dwell complete at {station_name}, departing")
                    
                    # CRITICAL: RELEASE SERVICE BRAKE BEFORE DEPARTURE (TC_HW style)
                    if ui_callback:
                        ui_callback.service_brake_active = False
                        ui_callback.send_service_brake(False)
                        print(f" Service brake RELEASED for departure from {station_name}")
                    
                    # CLOSE DOORS before departure
                    if ui_callback:
                        if hasattr(ui_callback, 'send_left_door_signal'):
                            ui_callback.send_left_door_signal(False)
                            if hasattr(ui_callback, 'left_door_btn') and ui_callback.left_door_btn.is_on:
                                ui_callback.left_door_btn.toggle()
                        if hasattr(ui_callback, 'send_right_door_signal'):
                            ui_callback.send_right_door_signal(False)
                            if hasattr(ui_callback, 'right_door_btn') and ui_callback.right_door_btn.is_on:
                                ui_callback.right_door_btn.toggle()
                        if hasattr(ui_callback, 'add_to_status_log'):
                            ui_callback.add_to_status_log("Doors closing - preparing to depart")
                    
                    # Move to next segment
                    self.current_segment_index += 1
                    if self.current_segment_index >= len(self.track_info['segments']):
                        self.current_segment_index = 1  # Loop back to main route
                    
                    # Reset for next segment
                    self.distance_traveled_in_segment = 0.0
                    self.distance_to_next_station = self.track_info['segments'][self.current_segment_index]['distance']
                    self.is_at_station = False
                    self.station_dwell_start_time = None
                    self.doors_open_at_station = False
                    self.doors_locked = False
                    
                    if ui_callback and hasattr(ui_callback, 'add_to_status_log'):
                        next_station = self.get_next_station_name()
                        ui_callback.add_to_status_log(f"Departing for {next_station}")
                        print(f"[POSITION] Next destination: {next_station}")
                        
                        # Send announcement to Train Model for passengers
                        if hasattr(ui_callback, 'server') and ui_callback.server:
                            try:
                                ui_callback.server.send_to_ui("Train Model", {
                                    'command': 'Announcement',
                                    'value': f"Departing for {next_station}",
                                    'train_id': 2
                                })
                                print(f"[ANNOUNCEMENT] Sent to Train Model: Departing for {next_station}")
                            except Exception as e:
                                print(f"[ANNOUNCEMENT] Error sending to Train Model: {e}")
            
            return  # CRITICAL: Early return while at station
        
        # ===== MOVING - UPDATE POSITION =====
        # Calculate displacement: distance = velocity × time
        displacement = current_speed_ms * dt
        
        # Update position tracking
        self.distance_traveled_in_segment += displacement
        self.distance_to_next_station = self.track_info['segments'][self.current_segment_index]['distance'] - self.distance_traveled_in_segment
        
        # ===== CHECK FOR STATION ARRIVAL (SIMPLE) =====
        if self.distance_to_next_station <= self.STATION_STOP_THRESHOLD:
            self.is_at_station = True
            self.station_dwell_start_time = current_time
            self.distance_to_next_station = 0.0
            current_station = self.track_info['segments'][self.current_segment_index]['to_station']
            
            print(f"[POSITION] *** ARRIVED AT {current_station} ***")
            
            if ui_callback and hasattr(ui_callback, 'add_to_status_log'):
                ui_callback.add_to_status_log(f"*** ARRIVED AT {current_station} ***")
                
                # Send announcement to Train Model for passengers
                if hasattr(ui_callback, 'server') and ui_callback.server:
                    try:
                        ui_callback.server.send_to_ui("Train Model", {
                            'command': 'Announcement',
                            'value': f"Arrived at {current_station}",
                            'train_id': 2
                        })
                        print(f"[ANNOUNCEMENT] Sent to Train Model: Arrived at {current_station}")
                    except Exception as e:
                        print(f"[ANNOUNCEMENT] Error sending to Train Model: {e}")
            
            # Open appropriate doors at station
            self._open_station_doors(ui_callback)
        
        # Update current block
        self._update_current_block()
    
    def _update_underground_status(self, ui_callback):
        """Update underground status and control lights"""
        new_underground = self.current_block in self.underground_blocks
        
        if new_underground != self.last_underground_state:
            self.is_underground = new_underground
            
            if ui_callback:
                if new_underground:
                    # Turn lights ON
                    if hasattr(ui_callback, 'send_headlights'):
                        ui_callback.send_headlights(True)
                    if hasattr(ui_callback, 'send_cabin_lights'):
                        ui_callback.send_cabin_lights(True)
                    
                    # Update UI buttons to show lights are ON
                    if hasattr(ui_callback, 'headlights_btn') and not ui_callback.headlights_btn.is_on:
                        ui_callback.headlights_btn.toggle()
                    if hasattr(ui_callback, 'cabin_lights_btn') and not ui_callback.cabin_lights_btn.is_on:
                        ui_callback.cabin_lights_btn.toggle()
                    
                    if hasattr(ui_callback, 'add_to_status_log'):
                        ui_callback.add_to_status_log(f"Entering underground tunnel (Block {self.current_block}) - Lights ON")
                else:
                    # Turn lights OFF
                    if hasattr(ui_callback, 'send_headlights'):
                        ui_callback.send_headlights(False)
                    if hasattr(ui_callback, 'send_cabin_lights'):
                        ui_callback.send_cabin_lights(False)
                    
                    # Update UI buttons to show lights are OFF
                    if hasattr(ui_callback, 'headlights_btn') and ui_callback.headlights_btn.is_on:
                        ui_callback.headlights_btn.toggle()
                    if hasattr(ui_callback, 'cabin_lights_btn') and ui_callback.cabin_lights_btn.is_on:
                        ui_callback.cabin_lights_btn.toggle()
                    
                    if hasattr(ui_callback, 'add_to_status_log'):
                        ui_callback.add_to_status_log(f"Exiting tunnel (Block {self.current_block}) - Lights OFF")
            
            self.last_underground_state = new_underground
    
    def _open_station_doors(self, ui_callback):
        """Open appropriate doors at station"""
        if not ui_callback:
            return
        
        station_name = self.get_current_station_name()
        
        # Check for block-specific exceptions first
        door_side = STATION_DOOR_EXCEPTIONS.get(self.current_block)
        if not door_side:
            door_side = self.station_door_sides.get(station_name, 'both')
        
        self.doors_open_at_station = True
        
        if hasattr(ui_callback, 'add_to_status_log'):
            ui_callback.add_to_status_log(f"[DOOR] Station {station_name}: {door_side} door(s)")
        
        # Open appropriate doors
        if door_side == 'left' or door_side == 'both':
            if hasattr(ui_callback, 'send_left_door_signal'):
                ui_callback.send_left_door_signal(True)
            if hasattr(ui_callback, 'left_door_btn'):
                if not ui_callback.left_door_btn.is_on:
                    ui_callback.left_door_btn.toggle()
        
        if door_side == 'right' or door_side == 'both':
            if hasattr(ui_callback, 'send_right_door_signal'):
                ui_callback.send_right_door_signal(True)
            if hasattr(ui_callback, 'right_door_btn'):
                if not ui_callback.right_door_btn.is_on:
                    ui_callback.right_door_btn.toggle()
    
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
            
            # Simple linear interpolation
            if to_block > from_block:
                blocks_span = to_block - from_block
                self.current_block = from_block + int(progress * blocks_span)
            else:
                self.current_block = from_block
    
    def get_distance_to_next_station(self):
        """Get distance remaining to next station in meters"""
        return self.distance_to_next_station
    
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
        return self.distance_to_next_station <= self.DECELERATION_DISTANCE and not self.is_at_station
    
    def get_current_speed_limit(self):
        """Get speed limit for current segment in MPH"""
        if self.current_segment_index < len(self.track_info['segments']):
            return self.track_info['segments'][self.current_segment_index]['speed_limit']
        return 43.50  # Default



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
        self.screen_width = self.root.winfo_screenwidth()-50
        self.screen_height = self.root.winfo_screenheight()-50
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        #make resizable
        self.root.resizable(True, True)

        # Select line at startup
        
        
        # Initialize position tracker based on selected line
        if self.selected_line == 'GREEN':
            self.position_tracker = PositionTracker(greenLineTrackInformation, greenLineStationDoorSides, selected_line)
            self.current_block = 63
        else:  # RED
            self.position_tracker = PositionTracker(redLineTrackInformation, redLineStationDoorSides, selected_line)
            self.current_block = 8

        # Socket server setup
        #added socket server 
        module_config = load_socket_config()
        train_model_config = module_config.get("Train SW", {"port": 12346})
        self.server = TrainSocketServer(port=train_model_config["port"], ui_id="Train SW")
        
        self.server.set_allowed_connections(["Train Model", "Track Model", "Train HW", "CTC"])
        self.server.start_server(self._process_message)
        self.server.connect_to_ui('localhost', 12345, "Train Model")
        self.server.connect_to_ui('localhost', 12344, "Track Model")
        self.server.connect_to_ui('localhost', 12347, "Train HW")
        self.server.connect_to_ui('localhost', 12341, "CTC")
        
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
        
        self.authority_value = tk.Label(blocks_frame, text="0 Blocks", 
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
        
        # Clock frame with ClockDisplay widget
        self.clock_frame = tk.Label(self.root, bg="lightblue")
        self.clock_frame.place(relx=0.2, rely=0.01)  # Top-left to avoid overlap
        self.clock = ClockDisplay(self.clock_frame)
        self.clock.pack(padx=5, pady=5)

        #engineer control panel
        engineer_btn = tk.Button(self.root, text="Engineer Panel", 
                                font=("Arial", 12, "bold"),
                                bg="orange", fg="black", relief=tk.RAISED, bd=2,
                                command=self.toggle_engineer_ui)
        engineer_btn.place(relx=0.72, rely=0.015, relwidth=0.1, relheight=0.045)

        # In the __init__ method of Main_Window class, add these flags:
        self.has_received_commanded_speed = False
        self.has_received_authority = False
        self.initial_service_brake_applied = True  # Track initial service brake

         # State variables
        self.current_speed = 0  # Will be in mph (converted from m/s for display)
        self.current_speed_ms = 0  # Store original m/s value for calculations
        self.commanded_speed_ms = 0  # Store commanded speed in m/s for calculations
        self.commanded_speed_mph = 0
        self.display_commanded_speed_mph = 0  # Raw commanded speed (before authority adjustment)
        self.set_speed = 45
        self.set_temp = 70
        self.is_auto_mode = True
        self.service_brake_active = True
        self.root.after(2000, lambda: self.send_service_brake(True))  # Send after 2 seconds

        self.emergency_brake_active = False
        self.door_safety_lock = False
        self.emergency_brake_auto_triggered = False
        self.commanded_authority = 0


        self.has_control_authority = False  # ←  Don't send power until we have authority
        
        # PID Control Parameters
        self.kp = 10.0  # Default proportional gain (will be updated from Engineer UI)
        self.ki = 2.0   # Default integral gain (will be updated from Engineer UI)
        self.max_power_kw = 120.0  # Maximum power in kW
        self.integral_error = 0.0  # For PI calculation (in m/s)
        self.prev_error = 0.0  # Previous error for trapezoidal integration (TC_HW style)
        self.sample_time = 0.1  # 100ms update rate
        self.last_power_sent = None  # Track last power to avoid duplicates

        # Track previous commanded speed for speed reduction detection
        self.previous_commanded_speed_ms = 0.0
        
        # Time multiplier for simulation speed (1x or 10x)
        self.time_multiplier = 1  # Default to normal speed
        
        # Brake for speed reduction after authority/commanded speed changes
        self._brake_for_speed_reduction = False
        self._target_speed_after_brake = None
        
        # Brake time tracking for speed reduction
        self.speed_reduction_brake_time = 0.0
        self.last_brake_check_time = time.time()

        #create engineer UI
        self.engineer_ui = EngineerUI(self, callback=self._onPIDParametersApplied)
        
        self.update_displays()
        # Test Panel
        #self.test_panel = TestPanel(self.root, self)

        #safety critical design:
        #self.safety_monitor = SafetyMonitor(self)

    def lock_doors(self):
        """Lock doors when train is moving"""
        if not self.door_safety_lock:
            self.door_safety_lock = True
            
            # Force close any open doors
            if hasattr(self, 'left_door_btn') and self.left_door_btn.is_on:
                self.left_door_btn.toggle()
                self.send_left_door_signal(False)
            
            if hasattr(self, 'right_door_btn') and self.right_door_btn.is_on:
                self.right_door_btn.toggle()
                self.send_right_door_signal(False)
            
            # Disable door buttons
            if hasattr(self, 'left_door_btn'):
                self.left_door_btn.config(state="disabled")
            if hasattr(self, 'right_door_btn'):
                self.right_door_btn.config(state="disabled")
            
            self.add_to_status_log("Doors locked - train in motion")

    def unlock_doors(self):
        """Unlock doors when train is stopped at station"""
        if self.door_safety_lock and self.current_speed_ms < 0.1:  # Use m/s
            self.door_safety_lock = False
            
            # Enable door buttons
            if hasattr(self, 'left_door_btn'):
                self.left_door_btn.config(state="normal")
            if hasattr(self, 'right_door_btn'):
                self.right_door_btn.config(state="normal")
            
            self.add_to_status_log("Doors unlocked - train stopped at station")

    def _process_message(self, message, source_ui_id):
        """Process incoming messages and update train state"""
        try:
            command = message.get('command')
            value = message.get('value')
            
            # ========== COMMANDED SPEED ==========
            if command == 'Commanded Speed':
                self.has_received_commanded_speed = True
                # Track previous commanded speed for reduction detection
                self.previous_commanded_speed_ms = self.commanded_speed_ms
                
                # Input: mph from train model
                speed_mph = float(value)
                
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"[COMMANDED SPEED] RECEIVED from Train Model: {speed_mph:.1f} mph")
                
                # Store RAW commanded speed (before authority adjustment)
                self.display_commanded_speed_mph = speed_mph
                
                # Apply authority-based limiting to internal commanded speed (TC_HW style)
                if self.commanded_authority == 0:
                    self.commanded_speed_mph = 0.0
                    print(f"[COMMANDED SPEED] Authority=0 → Adjusted to: 0.0 mph")
                elif self.commanded_authority == 1:
                    self.commanded_speed_mph = speed_mph * 0.5  # 50%
                    print(f"[COMMANDED SPEED] Authority=1 (50%) → Adjusted to: {self.commanded_speed_mph:.1f} mph")
                elif self.commanded_authority == 2:
                    self.commanded_speed_mph = speed_mph * 0.75  # 75%
                    print(f"[COMMANDED SPEED] Authority=2 (75%) → Adjusted to: {self.commanded_speed_mph:.1f} mph")
                elif self.commanded_authority == 3:
                    self.commanded_speed_mph = speed_mph  # 100%
                    print(f"[COMMANDED SPEED] Authority=3 (100%) → Adjusted to: {self.commanded_speed_mph:.1f} mph")
                else:
                    self.commanded_speed_mph = speed_mph  # Default 100%
                    print(f"[COMMANDED SPEED] Authority={self.commanded_authority} → Adjusted to: {self.commanded_speed_mph:.1f} mph")
                
                self.commanded_speed_ms = self.commanded_speed_mph * MPH_TO_METERS_PER_SEC
                print(f"[COMMANDED SPEED] Converted to m/s: {self.commanded_speed_ms:.2f} m/s")
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                self.set_commanded_speed(round(self.commanded_speed_mph, 1))
                
                # DO NOT reset integral error - let PI controller handle the change smoothly
                
                self.add_to_status_log(f"Commanded: {self.commanded_speed_mph:.1f} mph (raw: {speed_mph:.1f})")
    
                # Release initial service brake once we have both speed and authority
                self._check_initial_conditions()
            
            # ========== COMMANDED AUTHORITY ==========
            elif command == 'Commanded Authority':
                self.has_received_authority = True
                prev_authority = self.commanded_authority
                blocks = int(value)
                self.commanded_authority = blocks
                
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"[AUTHORITY] RECEIVED from Train Model: {blocks} blocks (was {prev_authority})")
                
                # CRITICAL: Recalculate commanded speed based on NEW authority (TC_HW style)
                if hasattr(self, 'display_commanded_speed_mph'):
                    raw_speed = self.display_commanded_speed_mph
                    old_commanded = self.commanded_speed_mph
                    print(f"[AUTHORITY] Raw commanded speed: {raw_speed:.1f} mph")
                    print(f"[AUTHORITY] OLD authority-adjusted speed: {old_commanded:.1f} mph")
                    
                    if self.commanded_authority == 0:
                        # Authority 0: Emergency stop
                        if not self.position_tracker.is_at_station:
                            self.commanded_speed_mph = 0.0
                            print(f"[AUTHORITY] Authority=0 (NOT at station) → Speed set to: 0.0 mph")
                            self.service_brake_active = True
                            self.send_service_brake(True)
                            print(f"AUTHORITY 0 - SERVICE BRAKE ENGAGED")
                        else:
                            print(f"[AUTHORITY] Authority=0 (at station) → Ignoring, station logic handles stop")
                            self.commanded_speed_mph = 0.0
                    elif self.commanded_authority == 1:
                        self.commanded_speed_mph = self.display_commanded_speed_mph * 0.5
                        print(f"[AUTHORITY] Authority=1 (50%) → Speed set to: {self.commanded_speed_mph:.1f} mph")
                    elif self.commanded_authority == 2:
                        self.commanded_speed_mph = self.display_commanded_speed_mph * 0.75
                        print(f"[AUTHORITY] Authority=2 (75%) → Speed set to: {self.commanded_speed_mph:.1f} mph")
                    elif self.commanded_authority == 3:
                        self.commanded_speed_mph = self.display_commanded_speed_mph
                        print(f"[AUTHORITY] Authority=3 (100%) → Speed set to: {self.commanded_speed_mph:.1f} mph")
                    else:
                        self.commanded_speed_mph = self.display_commanded_speed_mph
                        print(f"[AUTHORITY] Authority={self.commanded_authority} → Speed set to: {self.commanded_speed_mph:.1f} mph")
                    
                    self.commanded_speed_ms = self.commanded_speed_mph * MPH_TO_METERS_PER_SEC
                    print(f"[AUTHORITY] NEW authority-adjusted m/s: {self.commanded_speed_ms:.2f} m/s")
                    print(f"[AUTHORITY] Current speed: {self.current_speed_ms:.2f} m/s ({self.current_speed_ms*2.237:.1f} mph)")
                    
                    # CRITICAL NEW LOGIC: If new speed < current speed, APPLY BRAKE
                    speed_reduction_mph = old_commanded - self.commanded_speed_mph
                    if speed_reduction_mph > 2.0:  # Significant decrease (>2 mph)
                        print(f"SPEED DECREASE DETECTED: {old_commanded:.1f} → {self.commanded_speed_mph:.1f} mph (Δ={speed_reduction_mph:.1f} mph)")
                        
                        # Only apply brake if we're currently going faster than new target
                        if self.current_speed_ms > self.commanded_speed_ms + 1.0:  # >1 m/s faster
                            print(f"APPLYING SERVICE BRAKE to decelerate from {self.current_speed_ms*2.237:.1f} mph to {self.commanded_speed_mph:.1f} mph")
                            self.service_brake_active = True
                            self.send_service_brake(True)
                            
                            # Set flag to release brake when target reached
                            self._brake_for_speed_reduction = True
                            self._target_speed_after_brake = self.commanded_speed_ms
                        else:
                            print(f" Already near target speed, no brake needed")
                    
                    print(f"[AUTHORITY] Error will be: {self.commanded_speed_ms - self.current_speed_ms:.2f} m/s")
                    
                    self.set_commanded_speed(round(self.commanded_speed_mph, 1))
                    
                    # Release service brake if transitioning from authority 0 to non-zero
                    if prev_authority == 0 and self.commanded_authority > 0 and self.service_brake_active and not self.position_tracker.is_at_station:
                        print(f"AUTHORITY {self.commanded_authority} - Releasing emergency stop brake")
                        self.service_brake_active = False
                        self.send_service_brake(False)
                
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # DO NOT reset integral error - let PI controller handle the change smoothly
                
                self.set_authority(blocks)
                self.add_to_status_log(f"Authority: {blocks} blocks")
                
                # Release initial service brake once we have both speed and authority
                self._check_initial_conditions()
            
            # ========== PASSENGER EMERGENCY SIGNAL ==========
            elif command == "Passenger Emergency Signal":
                is_active = bool(value)
                self.set_emergency_signal(is_active)
                if is_active and not self.emergency_brake_active:
                    self.emergency_brake_activate()  # Use correct method name
                    self.add_to_status_log(" Passenger emergency: E-brake activated!")
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
            
            # ========== TIME (CLOCK DISPLAY) ==========
            # Receives time string from CTC/Track Model and displays it
            # This updates the ClockDisplay widget via set_time() method
            elif command == 'TIME':
                time_str = str(value)
                
                # Update ClockDisplay widget
                if hasattr(self, 'clock') and self.clock:
                    self.clock.set_time(time_str)
                    
                # Update station window clock if it exists
                if hasattr(self, 'station_window') and hasattr(self.station_window, 'clock_display'):
                    self.station_window.clock_display.config(text=time_str)
                
                # Note: We don't log every time update to avoid console spam
            
            # ========== MULT (TIME MULTIPLIER) ==========
            # Receives speed multiplier from CTC (1x or 10x)
            # This controls how fast the simulation runs
            # Updates: position_tracker.TIME_SCALE and clock.speed_multiplier
            elif command == "MULT":
                try:
                    multiplier = int(value)
                    
                    # Validate multiplier is 1 or 10
                    if multiplier not in [1, 10]:
                        print(f"[MULT] Invalid value: {multiplier} (must be 1 or 10)")
                        self.add_to_status_log(f"Invalid MULT value: {multiplier}")
                    else:
                        # Call set_speed_mult to update position tracker and clock
                        self.set_speed_mult(multiplier)
                        print(f"[MULT] Received and processed: {multiplier}x speed")
                        
                except ValueError as e:
                    print(f"[MULT] ValueError: {value} is not a valid integer - {e}")
                    self.add_to_status_log(f"Invalid MULT format: {value}")
                except Exception as e:
                    print(f"[MULT] Error processing MULT command: {e}")
                    self.add_to_status_log(f"Error processing MULT: {str(e)}")
            
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
    
    def _release_speed_reduction_brake(self):
        """Release service brake after speed reduction"""
        if self.service_brake_active and not self.position_tracker.is_at_station:
            self.service_brake_active = False
            self.send_service_brake(False)
            self.add_to_status_log(f" Service brake released after speed adjustment")
    
    def calculate_power_command(self):
        """
        Calculate power using PI controller - TC_HW STYLE
        
        Key differences from old implementation:
        1. Updates position FIRST (synchronized)
        2. Checks service brake and returns 0 power if active
        3. Simple station deceleration logic
        4. Auto-engages/releases service brake at stations
        """
        # Don't output power until we have control authority
        # UNLESS we're already moving (recovery from stuck state)
        if not self.has_control_authority:
            # If we have speed and authority but lost control authority flag, restore it
            if self.has_received_commanded_speed and self.has_received_authority:
                self.has_control_authority = True
                print("[RECOVERY] Restoring control authority")
            else:
                return 0.0
        
        # CRITICAL: Update position tracking FIRST
        self.position_tracker.update(self.current_speed_ms, self)
        
        # Conversion constants
        MPH_TO_MS = 0.44704  # 1 mph = 0.44704 m/s
        MS_TO_MPH = 2.23694  # 1 m/s = 2.23694 mph
        
        # Get commanded speed based on mode
        if self.is_auto_mode:
            commanded_speed_mph = self.commanded_speed_mph  # Already authority-adjusted
            commanded_speed_ms = commanded_speed_mph * MPH_TO_MS
        else:
            # Manual mode
            commanded_speed_mph = float(self.set_speed)
            commanded_speed_ms = commanded_speed_mph * MPH_TO_MS
        
        # Apply speed limit
        speed_limit_mph = self.position_tracker.get_current_speed_limit()
        speed_limit_ms = speed_limit_mph * MPH_TO_MS
        commanded_speed_ms = min(commanded_speed_ms, speed_limit_ms)
        
        # ===== STATION HANDLING (TC_HW STYLE) =====
        if self.is_auto_mode:
            if self.position_tracker.is_at_station:
                # Force stop at station
                commanded_speed_ms = 0.0
                
                # Ensure service brake is active
                if not self.service_brake_active:
                    self.service_brake_active = True
                    self.send_service_brake(True)
                    station_name = self.position_tracker.get_current_station_name()
                    self.add_to_status_log(f"At station {station_name} - Service brake holding")
                    print(f"[POWER] Service brake ENGAGED at {station_name}")
                
                # Unlock doors when stopped
                self.unlock_doors()
                
                # DO NOT return early - continue to power calculation
                # Brake check in update_displays will send 0 power
                
            elif self.position_tracker.should_decelerate_for_station():
                # Calculate deceleration profile for smooth stop
                dist_to_station = self.position_tracker.get_distance_to_next_station()
                
                # Target deceleration: v² = v₀² + 2a·d
                # v = sqrt(2 * decel * distance)
                DECEL_RATE = 1.0  # m/s² - comfortable deceleration
                
                if dist_to_station > 0:
                    target_speed = (2 * DECEL_RATE * dist_to_station) ** 0.5
                    # Limit to current commanded speed (don't accelerate)
                    commanded_speed_ms = min(commanded_speed_ms, target_speed)
                    
                    # Apply service brake when very close (within 20m)
                    if dist_to_station < 20.0:
                        if not self.service_brake_active:
                            self.service_brake_active = True
                            self.send_service_brake(True)
                            self.add_to_status_log("Approaching station - Service brake applied")
                else:
                    commanded_speed_ms = 0.0
        
        # ===== PI CONTROLLER CALCULATION (TC_HW TRAPEZOIDAL STYLE) =====
        current_speed_ms = self.current_speed_ms
        velocity_error = commanded_speed_ms - current_speed_ms
        
        # CRITICAL: Check if we're braking for speed reduction and have reached target
        if hasattr(self, '_brake_for_speed_reduction') and self._brake_for_speed_reduction:
            if hasattr(self, '_target_speed_after_brake'):
                # Check if we've slowed down to near the target (within 1 m/s = 2.2 mph)
                if current_speed_ms <= self._target_speed_after_brake + 1.0:
                    print(f"✓ TARGET SPEED REACHED: {current_speed_ms*2.237:.1f} mph ≤ {self._target_speed_after_brake*2.237:.1f} mph")
                    print(f"RELEASING SERVICE BRAKE - PI controller taking over")
                    self.service_brake_active = False
                    self.send_service_brake(False)
                    self._brake_for_speed_reduction = False
                    self._target_speed_after_brake = None
        
        # Get PI gains
        kp = self.kp
        ki = self.ki
        max_power = self.max_power_kw
        
        # Debug output every 20 calls
        if not hasattr(self, '_power_debug_counter'):
            self._power_debug_counter = 0
        self._power_debug_counter += 1
        
        # Calculate P term
        p_term = kp * velocity_error
        power_without_integral = p_term
        
        # TRAPEZOIDAL INTEGRATION with ANTI-WINDUP (TC_HW style)
        # Only integrate if P^cmd < P^max
        if power_without_integral < max_power:
            # u_k = u_{k-1} + (T/2)(e_k + e_{k-1})
            self.integral_error += (self.sample_time / 2.0) * (velocity_error + self.prev_error)
        # else: at power limit - don't integrate (anti-windup)
        
        # Store current error for next iteration
        self.prev_error = velocity_error
        
        # Calculate I term
        i_term = ki * self.integral_error
        
        # Total power: P^cmd = Kp * e_k + Ki * u_k
        power_kw = p_term + i_term
        power_kw = max(0.0, min(max_power, power_kw))
        
        # Debug output
        if self._power_debug_counter % 5 == 0:  # Every 0.5 seconds
            print(f"[POWER CALC] Cmd={commanded_speed_ms:.2f}m/s ({commanded_speed_ms*2.237:.1f}mph), "
                  f"Curr={current_speed_ms:.2f}m/s ({current_speed_ms*2.237:.1f}mph), "
                  f"Err={velocity_error:.2f}m/s, P={p_term:.1f}kW, I={i_term:.1f}kW, "
                  f"→ TOTAL={power_kw:.1f}kW")
        
        # Update previous commanded speed for tracking
        self.previous_commanded_speed_ms = commanded_speed_ms
        
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
    
    def set_speed_mult(self, multiplier):
        """
        Set the speed multiplier for the entire system
        Updates position tracker and clock display
        
        Args:
            multiplier (int): Speed multiplier (1 or 10)
        """
        if multiplier not in [1, 10]:
            print(f"[SPEED MULT] Invalid multiplier: {multiplier} (must be 1 or 10)")
            return
        
        print(f"[SPEED MULT] Setting speed multiplier to {multiplier}x")
        
        # Update time multiplier
        self.time_multiplier = multiplier
        
        # Update position tracker TIME_SCALE
        if hasattr(self, 'position_tracker') and self.position_tracker:
            self.position_tracker.TIME_SCALE = float(multiplier)
            print(f"[SPEED MULT] Position tracker TIME_SCALE updated to {multiplier}")
        
        # Update ClockDisplay - try each possible interface once
        if hasattr(self, 'clock') and self.clock:
            clock_updated = False
            try:
                # Try method 1: set_speed_multiplier()
                if hasattr(self.clock, 'set_speed_multiplier'):
                    self.clock.set_speed_multiplier(multiplier)
                    print(f"[SPEED MULT] Clock updated via set_speed_multiplier()")
                    clock_updated = True
                # Try method 2: set_mult()
                elif hasattr(self.clock, 'set_mult'):
                    self.clock.set_mult(multiplier)
                    print(f"[SPEED MULT] Clock updated via set_mult()")
                    clock_updated = True
                # Try method 3: speed_multiplier attribute
                elif hasattr(self.clock, 'speed_multiplier'):
                    self.clock.speed_multiplier = multiplier
                    print(f"[SPEED MULT] Clock updated via speed_multiplier attribute")
                    clock_updated = True
                # Try method 4: mult attribute
                elif hasattr(self.clock, 'mult'):
                    self.clock.mult = multiplier
                    print(f"[SPEED MULT] Clock updated via mult attribute")
                    clock_updated = True
                
                if not clock_updated:
                    print(f"[SPEED MULT] Warning: ClockDisplay has no recognized speed multiplier interface")
                    print(f"[SPEED MULT] Available ClockDisplay methods: {[m for m in dir(self.clock) if not m.startswith('_')]}")
                    
            except AttributeError as e:
                print(f"[SPEED MULT] AttributeError updating clock: {e}")
            except Exception as e:
                print(f"[SPEED MULT] Unexpected error updating clock: {e}")
        
        print(f"[SPEED MULT] System speed multiplier successfully set to {multiplier}x")
        self.add_to_status_log(f"Speed multiplier: {multiplier}x")

    def handle_failure_mode(self, failure_type, is_active):
        """Handle failure mode activation/deactivation"""
        if is_active:
            # Failure detected - turn on appropriate light and auto-activate emergency brake
            self.add_to_status_log(f"CRITICAL: {failure_type} detected!")
            
            # Turn on the failure light
            if failure_type == "Brake Failure":
                self.activate_brake_failure_light()
            elif failure_type == "Signal Pickup Failure":
                self.activate_signal_failure_light()
            elif failure_type == "Train Engine Failure":
                self.activate_engine_failure_light()
            
            if not self.emergency_brake_active:
                self.emergency_brake_activate()
                self.emergency_brake_auto_triggered = True
                self.add_to_status_log("Emergency brake auto-activated due to failure!")
                print(f"EMERGENCY BRAKE AUTO-ACTIVATED: {failure_type}")
        else:
            # Failure cleared - turn off appropriate light
            self.add_to_status_log(f"✓ {failure_type} cleared")
            
            # Turn off the failure light
            if failure_type == "Brake Failure":
                self.deactivate_brake_failure_light()
            elif failure_type == "Signal Pickup Failure":
                self.deactivate_signal_failure_light()
            elif failure_type == "Train Engine Failure":
                self.deactivate_engine_failure_light()
            
            # Update release button state (may enable it now)
            self.update_ebrake_release_state()
    
    def activate_brake_failure_light(self):
        """Turn on brake failure indicator (yellow)"""
        self.brake_failure.activate()
        print("[FAILURE LIGHT] Brake failure - YELLOW light ON")
    
    def deactivate_brake_failure_light(self):
        """Turn off brake failure indicator"""
        self.brake_failure.deactivate()
        print("[FAILURE LIGHT] Brake failure cleared - light OFF")
    
    def activate_signal_failure_light(self):
        """Turn on signal pickup failure indicator (orange)"""
        self.signal_failure.activate()
        print("[FAILURE LIGHT] Signal pickup failure - ORANGE light ON")
    
    def deactivate_signal_failure_light(self):
        """Turn off signal pickup failure indicator"""
        self.signal_failure.deactivate()
        print("[FAILURE LIGHT] Signal pickup failure cleared - light OFF")
    
    def activate_engine_failure_light(self):
        """Turn on train engine failure indicator (red)"""
        self.engine_failure.activate()
        print("[FAILURE LIGHT] Train engine failure - RED light ON")
    
    def deactivate_engine_failure_light(self):
        """Turn off train engine failure indicator"""
        self.engine_failure.deactivate()
        print("[FAILURE LIGHT] Train engine failure cleared - light OFF")
    
    def update_displays(self):
        """
        Update all displays - TC_HW STYLE
        
        CRITICAL: Always calculate power, check brakes when SENDING
        Position tracking happens INSIDE calculate_power_command()
        """
        
        # ALWAYS calculate power (even when brake is on)
        try:
            power_kw = self.calculate_power_command()
            power_watts = power_kw * 1000
            
            # BRAKE CHECK WHEN SENDING (TC_HW style)
            if self.service_brake_active or self.emergency_brake_active:
                # Brake active - send zero power
                if self.last_power_sent != 0:
                    self.send_setpoint_power(0.0)
                    self.last_power_sent = 0
                    print(f"Brake active - power command set to ZERO")
            else:
                # No brake - ALWAYS send power (don't throttle by 100W)
                # This ensures authority/speed changes update immediately
                self.send_setpoint_power(power_kw)
                self.last_power_sent = power_watts
        except Exception as e:
            print(f"Error in power calculation: {e}")
        
        # Update E-brake release button state
        self.update_ebrake_release_state()
        
        # Update door safety based on speed
        if self.current_speed_ms > 1.0 and not self.door_safety_lock:
            self.lock_doors()
        elif self.current_speed_ms < 0.1 and self.door_safety_lock and self.position_tracker.is_at_station:
            self.unlock_doors()
        
        # Schedule next update
        self.root.after(100, self.update_displays)
    
    def apply_brake_effect(self):
        """Apply brake effects to current speed"""
        # Note: Brake deceleration is handled by Train Model
        # Service brake: 1.2 m/s²
        # Emergency brake: 2.73 m/s²
        # DO NOT reset integral error here - let PI controller handle it
        pass
    
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
        # Don't update commanded speed yet - wait for confirmation
        self.add_to_status_log(f"Set speed: {self.set_speed} mph (press Confirm to apply)")
    
    def decrease_set_speed(self):
        if self.is_auto_mode:
            self.mode_select.set_mode("manual")
        self.set_speed = max(0, self.set_speed - 5)
        self.set_speed_value.config(text=str(self.set_speed))
        # Don't update commanded speed yet - wait for confirmation
        self.add_to_status_log(f"Set speed: {self.set_speed} mph (press Confirm to apply)")
    
    def confirm_speed(self):
        """Callback when speed is confirmed in manual mode"""
        if not self.is_auto_mode:
            # Update both commanded speed variables for manual mode
            self.commanded_speed_mph = float(self.set_speed)
            self.commanded_speed_ms = self.commanded_speed_mph * MPH_TO_METERS_PER_SEC
            self.commanded_speed_value.config(text=str(self.set_speed))
            
            # DO NOT reset integral - let PI controller smoothly transition
            self.add_to_status_log(f"Manual speed confirmed: {self.set_speed} mph")
            print(f"[MANUAL SPEED] Confirmed: {self.set_speed} mph → {self.commanded_speed_ms:.2f} m/s")

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
        """Handle service brake button press/release - NO integral reset"""
        print(f"[DEBUG] Service brake action called: pressed={pressed}")
        
        if pressed:
            self.service_brake_active = True
            self.send_service_brake(True)
            # DO NOT reset integral - let PI controller continue tracking
            self.add_to_status_log(f" Service brake applied")
            print(f"SERVICE BRAKE: ACTIVE")
        else:
            self.service_brake_active = False
            self.send_service_brake(False)
            # DO NOT reset integral - let PI controller continue tracking
            self.add_to_status_log(" Service brake released")
            print("SERVICE BRAKE: RELEASED")
    
    
    def emergency_brake_activate(self, pressed=None):
        """Activate emergency brake (single press, no release)"""
        if not self.emergency_brake_active:
            self.emergency_brake_active = True
            self.emergency_brake_auto_triggered = False  # Reset auto-trigger flag
            
            # Activate emergency light
            self.emergency_light.activate()
            
            # Send emergency brake signal
            self.send_emergency_brake_signal(True)
            
            # Reset integral error when emergency brake is applied
            self.integral_error = 0.0
            
            # Force service brake off (emergency brake overrides)
            self.service_brake_active = False
            self.send_service_brake(False)
            
            self.add_to_status_log("EMERGENCY BRAKE ACTIVATED!")
            print("EMERGENCY BRAKE ACTIVATED!")
            
            # Darken the button to show it's active
            self.emergency_brake.canvas.itemconfig(self.emergency_brake.button, fill="red4")
            
            # Update release button state
            self.update_ebrake_release_state()

    def emergency_brake_release(self):
        """Release emergency brake - only works when speed is zero"""
        # DEBUG: Print current state
        print(f"[DEBUG E-BRAKE] current_speed_ms={self.current_speed_ms}, current_speed={self.current_speed}")
        
        # Use m/s for comparison (more precise)
        if self.current_speed_ms > 0.1:  # Using m/s directly
            self.add_to_status_log(f"Cannot release E-brake: Train moving at {self.current_speed_ms:.2f} m/s")
            print(f"E-brake release DENIED - train moving at {self.current_speed_ms:.2f} m/s")
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
        
        # Also release service brake if it was active
        if self.service_brake_active:
            self.service_brake_active = False
            self.send_service_brake(False)
        
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
        
        # Use m/s for speed check
        at_zero_speed = self.current_speed_ms <= 0.1
        
        print(f"[E-BRAKE CHECK] speed_ms={self.current_speed_ms}, zero={at_zero_speed}, no_failures={no_failures}")
        
        if no_failures and at_zero_speed:
            # Safe to allow release
            self.ebrake_release_btn.config(state="normal", bg="green")
            self.add_to_status_log(f"✓ E-brake ready to release (speed: {self.current_speed_ms:.2f} m/s)")
        else:
            # Not safe yet
            self.ebrake_release_btn.config(state="disabled", bg="darkgray")
            
        # Log current state for debugging
        print(f"[E-BRAKE DEBUG] Active: {self.emergency_brake_active}, Failures: {not no_failures}, Speed: {self.current_speed_ms}m/s")
    
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
        if self.current_speed_ms > 0.1:  # Use m/s for consistency
            self.add_to_status_log("Left door: REQUEST DENIED - Train moving")
            return
            
        status = "OPEN" if state else "CLOSED"
        self.send_left_door_signal(state)  # Send to train model
        self.add_to_status_log(f"Left door: {status}")
        print(f"Left door: {status}")
        
        # Update button visual state
        self.left_door_btn.update_indicator(state)

    def toggle_right_door(self, state):
        if self.current_speed_ms > 0.1:  # Use m/s for consistency
            self.add_to_status_log("Right door: REQUEST DENIED - Train moving")
            return
            
        status = "OPEN" if state else "CLOSED"
        self.add_to_status_log(f"Right door: {status}")
        self.send_right_door_signal(state)  # Send to train model
        print(f"Right door: {status}")
        
        # Update button visual state
        self.right_door_btn.update_indicator(state)
    
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
        self.current_speed = speed  # mph for display
        self.current_speed_ms = speed * MPH_TO_METERS_PER_SEC  # Store m/s for calculations
        
        self.speedometer.update_speed(speed)
        self.current_speed_display.config(text=f"Current Speed: {int(speed)} mph")
        
        # Update E-brake release button whenever speed changes
        self.update_ebrake_release_state()
    
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
    
    
    def _check_initial_conditions(self):
        """
        Check if we have received initial commanded speed and authority.
        Once both are received, release the initial service brake.
        """
        if (self.has_received_commanded_speed and 
            self.has_received_authority and 
            not self.has_control_authority):  # Only release once
            
            # Mark that we now have control
            self.has_control_authority = True
            
            # Release service brake if still in initial state
            if self.service_brake_active and self.initial_service_brake_applied:
                self.service_brake_active = False
                self.send_service_brake(False)
                self.initial_service_brake_applied = False
                self.add_to_status_log("Initial conditions met - service brake released, ready to move")
                print("[INIT] Service brake released - train ready to move")

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
        Output: power in Watts (Train Model expects Watts)
        """
        try:
            power_watts = float(power_kw * 1000)
            
            # CRITICAL DEBUG: Log EVERY power send
            print(f"[SEND POWER] Sending {power_kw:.2f} kW ({power_watts:.0f} W) to Train Model")
            
            self.server.send_to_ui("Train Model", {
                'command': "Power Command",
                'value': power_watts,
                'train_id' : 2
            })
        except Exception as e:
            print(f"ERROR sending power: {e}")
            self.add_to_status_log("Failed to send power command")


    def send_emergency_brake_signal(self, is_active):
        """
        Send emergency brake signal to Train Model
        Input: boolean
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Emergency Brake",
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
            self.add_to_status_log("Failed to send service brake")

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

    # Make sure window is visible before grabbing
    dialog.update_idletasks()  # Force window to render
    dialog.grab_set()   # Make modal - AFTER window is rendered
    dialog.focus_set()

    # Wait for dialog result
    root.wait_window(dialog)

    # --- Now show main window with selection ---
    root.deiconify()  
    app = Main_Window(root, selected_line=selection["line"])

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()