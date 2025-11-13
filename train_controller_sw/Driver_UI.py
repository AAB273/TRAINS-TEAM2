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
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer


class Mode_Toggle(tk.Frame):
    def __init__(self, parent, callback=None):
        super().__init__(parent, bg="gray")
        
        self.callback = callback
        self.active_mode = None
        
        self.Driver_button1 = tk.Button(self, text="Auto", command=lambda: self.set_mode("auto"), 
                                       font=("Arial", 12, "bold"), width=8)
        self.Driver_button2 = tk.Button(self, text="Manual", command=lambda: self.set_mode("manual"),
                                       font=("Arial", 12, "bold"), width=8)
        
        self.Driver_button1.grid(row=0, column=0, padx=5, pady=5)
        self.Driver_button2.grid(row=0, column=1, padx=5, pady=5)
        
        self.set_mode("auto")
    
    def set_mode(self, mode):
        if mode == self.active_mode:
            return
        
        self.active_mode = mode
        
        if mode == "auto":
            self.Driver_button1.config(bg="lightgreen", activebackground="green")
            self.Driver_button2.config(bg="lightgrey", activebackground="grey")
        else:
            self.Driver_button2.config(bg="lightgreen", activebackground="green")
            self.Driver_button1.config(bg="lightgrey", activebackground="grey")
        
        if self.callback:
            self.callback(mode)


class ToggleButton(tk.Button):
    def __init__(self, parent, text="", callback=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.callback = callback
        self.is_on = False
        self.config(command=self.toggle, bg="lightgrey", activebackground="grey")
    
    def toggle(self):
        self.is_on = not self.is_on
        if self.is_on:
            self.config(bg="lightgreen", activebackground="green")
        else:
            self.config(bg="lightgrey", activebackground="grey")
        
        if self.callback:
            self.callback(self.is_on)


class FailureIndicator(tk.Canvas):
    def __init__(self, parent, size=60, color="yellow", glow_color="orange", **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, **kwargs)
        self.size = size
        self.color = color
        self.glow_color = glow_color
        self.active = False
        self.circle = self.create_oval(5, 5, size-5, size-5, fill=color, outline="black", width=2)
        self.text = self.create_text(size/2, size/2, text="!", font=("Arial", int(size/2.5), "bold"), fill="black")

    def activate(self):
        self.itemconfig(self.circle, fill=self.glow_color)
        self.active = True

    def deactivate(self):
        self.itemconfig(self.circle, fill=self.color)
        self.active = False

    def set_state(self, state):
        if state:
            self.activate()
        else:
            self.deactivate()

class Main_Window:
    def __init__(self, root):
        self.root = root
        self.root.title("Train Controller - Monitor Display")
        #add zoomed command to make screen fit 
        #self.root.attributes('-zoomed', True)  # On macOS/Linux
        self.root.configure(bg="navy")
        self.root.attributes('-zoomed', True)  # On macOS/Linux
        #self.root.state('zoomed') for windows

        # Make fullscreen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        #make resizable
        self.root.resizable(True, True)

        # Socket server setup
        #added socket server 
        module_config = load_socket_config()
        train_model_config = module_config.get("Train SW", {"port": 12346})
        self.server = TrainSocketServer(port=train_model_config["port"], ui_id="Train SW")
        
        self.server.set_allowed_connections(["Train Model", "Track Model"])
        self.server.start_server(self._process_message)
        self.server.connect_to_ui('localhost', 12345, "Train Model")
        self.server.connect_to_ui('localhost', 12344, "Track Model")
        
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
        
        # Service Brake Percentage Display
        #self.brake_percentage_display = tk.Label(speedometer_frame, text="Service Brake: 0%", 
                                                #font=("Arial", 12, "bold"), bg="white", fg="red")
        #self.brake_percentage_display.pack(pady=2)
        
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
        
        self.current_temp = tk.Label(self.ac_frame, text="70°F", font=("Arial", 28, "bold"), 
                                    bg="grey", fg="white")
        self.current_temp.grid(row=1, column=0, pady=10)
        
        tk.Label(self.ac_frame, text="Set Temperature:", font=("Arial", 12, "bold"), 
                bg="lightblue").grid(row=2, column=0, pady=10, sticky="ew", padx=5)
        
        temp_control = tk.Frame(self.ac_frame, bg="grey")
        temp_control.grid(row=3, column=0, pady=10)
        
        tk.Button(temp_control, text="▲", command=self.increase_temp, width=3, height=1,
                 font=("Arial", 16, "bold"), bg="lightblue").grid(row=0, column=0, padx=8)
        
        self.set_temp_value = tk.Label(temp_control, text="68°F", font=("Arial", 22, "bold"), 
                                      bg="black", fg="white", width=6, relief=tk.SUNKEN, bd=2)
        self.set_temp_value.grid(row=0, column=1, padx=8)
        
        tk.Button(temp_control, text="▼", command=self.decrease_temp, width=3, height=1,
                 font=("Arial", 16, "bold"), bg="lightblue").grid(row=0, column=2, padx=8)
        
        self.power_btn = ToggleButton(self.ac_frame, text="Set", 
                                     font=("Arial", 14, "bold"), 
                                     callback=self.toggle_ac, width=10, pady=5)
        self.power_btn.grid(row=4, column=0, pady=15)
        
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
            self.train_horn_icon = tk.PhotoImage(file="trainhorn.png")
            self.train_horn_icon = self.train_horn_icon.subsample(5, 5)
            self.train_horn = tk.Button(main_container, image=self.train_horn_icon, 
                                       bg="burlywood1", activebackground="burlywood3",
                                       command=self.press_horn, relief=tk.RAISED, bd=3)
        except:
            self.train_horn = tk.Button(main_container, text="Train Horn\n", 
                                       font=("Arial", 14, "bold"), bg="burlywood1", 
                                       activebackground="burlywood3",
                                       command=self.press_horn, relief=tk.RAISED, bd=3)
        self.train_horn.place(relx=0.21, rely=0.30, relwidth=0.1, relheight=0.12)
        tk.Label(main_container, text="Train Horn", font=("Arial", 11, "bold"), 
         bg="white").place(relx=0.22, rely=0.27)
        
        # Service Brake Button
        self.service_brake = Brake_button(main_container, radius=70, color="orange", 
                                          hover_color="darkorange", active_color="orange4",
                                          text="Service\nBrake", command=self.service_brake_action,
                                          hold_mode=True, canvas_bg="white")
        self.service_brake.place(relx=.23, rely=.52)
        
        '''# Brake Percentage Control
        brake_percent_frame = tk.Frame(main_container, bg="white")
        brake_percent_frame.place(relx=.23, rely=.48)
        
        tk.Label(brake_percent_frame, text="Brake %:", font=("Arial", 10, "bold"), 
                bg="white").pack(side=tk.LEFT, padx=(0, 5))
        
        self.brake_percent_var = tk.StringVar(value="50%")
        brake_percent_menu = ttk.Combobox(brake_percent_frame, 
                                        textvariable=self.brake_percent_var,
                                        values=["25%", "50%", "75%", "100%"],
                                        state="readonly", width=6,
                                        font=("Arial", 10))
        brake_percent_menu.pack(side=tk.LEFT)
        brake_percent_menu.bind("<<ComboboxSelected>>", self.on_brake_percent_change)
        '''

        # Emergency Brake
        self.emergency_brake = Brake_button(main_container, radius=70, color="darkred", 
                                            hover_color="red", active_color="red4",
                                            text="Emergency\nBrake", 
                                            command=self.emergency_brake_action, canvas_bg="white")
        self.emergency_brake.place(relx=.69, rely=.52)
        
        # Emergency Light
        self.emergency_light = EmergencyLight(main_container, size=75)
        self.emergency_light.place(relx=.7, rely=.41)
        
        tk.Label(main_container, text="Emergency Signal", font=("Arial", 14, "bold"),
                bg="darkgray", fg="darkred").place(relx=.68, rely=.38)
        
        # Control Buttons Grid
        self.button_grid_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.button_grid_frame.place(relx=0.75, rely=0.68, relwidth=0.22, relheight=0.28)
        
        try:
            self.bulb_logo = tk.PhotoImage(file="bulb.png").subsample(9, 9)
            self.cabin_lights_btn = ToggleButton(self.button_grid_frame, image=self.bulb_logo,
                                                callback=self.toggle_cabin_lights)
            self.cabin_lights_btn.image = self.bulb_logo
        except:
            self.cabin_lights_btn = ToggleButton(self.button_grid_frame, text="", 
                                                font=("Arial", 24), callback=self.toggle_cabin_lights)
        self.cabin_lights_btn.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        
        try:
            self.headlight_logo = tk.PhotoImage(file="headlight.png").subsample(5, 5)
            self.headlights_btn = ToggleButton(self.button_grid_frame, image=self.headlight_logo,
                                              callback=self.toggle_headlights)
            self.headlights_btn.image = self.headlight_logo
        except:
            self.headlights_btn = ToggleButton(self.button_grid_frame, text="", 
                                              font=("Arial", 24), callback=self.toggle_headlights)
        self.headlights_btn.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        
        try:
            self.left_door_logo = tk.PhotoImage(file="leftdoor.png").subsample(10, 10)
            self.left_door_btn = ToggleButton(self.button_grid_frame, image=self.left_door_logo,
                                             callback=self.toggle_left_door)
            self.left_door_btn.image = self.left_door_logo
        except:
            self.left_door_btn = ToggleButton(self.button_grid_frame, text="", 
                                             font=("Arial", 24), callback=self.toggle_left_door)
        self.left_door_btn.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        
        try:
            self.right_door_logo = tk.PhotoImage(file="right.png").subsample(10, 10)
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
            self.bltlogo = tk.PhotoImage(file="bltlogo.png").subsample(4, 4)
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
        self.set_temp = 68
        self.is_auto_mode = True
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.door_safety_lock = True
        self.emergency_brake_auto_triggered = False
        
        # PID Control Parameters
        self.kp = 10.0  # Default proportional gain (will be updated from Engineer UI)
        self.ki = 2.0   # Default integral gain (will be updated from Engineer UI)
        self.max_power_kw = 120.0  # Maximum power in kW
        self.integral_error = 0.0  # For PI calculation (in m/s)
        self.sample_time = 0.1  # 100ms update rate
        self.last_power_sent = None  # Track last power to avoid duplicates

        #create engineer UI
        self.engineer_ui = EngineerUI(self, callback=self.on_pid_change)
        
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
            elif command == "Actual Velocity":
                # Input: m/s from Train Model
                self.current_speed_ms = float(value)  # Store original m/s
                velocity_mph = self.current_speed_ms * METERS_PER_SEC_TO_MPH
                self.set_current_speed(velocity_mph)
                # Don't log every update - handled in power calculation
            
            # ========== CABIN TEMPERATURE ==========
            elif command == "Cabin Temperature":
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
            
            # ========== ADDITIONAL COMMANDS ==========
            elif command == "Beacon Data":
                self.add_to_status_log(f"Beacon: {value}")
            
            elif command == "Preloaded Track Information":
                self.add_to_status_log("Track info updated")
            
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

    def on_pid_change(self, kp, ki):
        """Callback when PID parameters change"""
        self.add_to_status_log(f"Engineer: Kp={kp:.1f}, Ki={ki:.2f}")

    def on_pid_change(self, kp, ki):
        """Callback when PID parameters change"""
        self.add_to_status_log(f"Engineer adjusted PID: Kp={kp:.1f}, Ki={ki:.1f}")
    
    def toggle_engineer_ui(self):
        """Show/hide engineer UI"""
        if self.engineer_ui.window.state() == 'normal':
            self.engineer_ui.hide()
        else:
            self.engineer_ui.show()
    
    def calculate_power_command(self):
        """
        Calculate power command using PI controller.
        
        Uses Kp and Ki from Engineer UI.
        All internal calculations done in METRIC (m/s).
        
        Returns:
            Power in kW (kilowatts)
        """
        # Get PI gains from Engineer UI
        kp = self.engineer_ui.get_kp() if hasattr(self, 'engineer_ui') else self.kp
        ki = self.engineer_ui.get_ki() if hasattr(self, 'engineer_ui') else self.ki
        
        # Determine commanded speed based on mode
        if self.is_auto_mode:
            # In automatic mode, use commanded speed from Track Model (already in m/s)
            commanded_speed_ms = self.commanded_speed_ms
        else:
            # In manual mode, use set speed (convert from mph to m/s)
            commanded_speed_mph = float(self.set_speed_value.cget("text"))
            commanded_speed_ms = commanded_speed_mph * MPH_TO_METERS_PER_SEC
        
        # Get current actual speed (in m/s for calculation)
        current_speed_ms = self.current_speed_ms
        
        # Calculate velocity error in METRIC (m/s)
        velocity_error = commanded_speed_ms - current_speed_ms
        
        # Update integral error with anti-windup (in m/s)
        self.integral_error += velocity_error * self.sample_time
        
        # Anti-windup: limit integral term
        max_integral = self.max_power_kw / (ki if ki > 0 else 1.0)
        self.integral_error = max(-max_integral, min(max_integral, self.integral_error))
        
        # Calculate PI control output
        # Power = Kp * error + Ki * integral_error
        p_term = kp * velocity_error
        i_term = ki * self.integral_error
        power_kw = p_term + i_term
        
        # Limit power to max and ensure non-negative
        power_kw = max(0.0, min(self.max_power_kw, power_kw))
        
        # Log periodically (every 1 second instead of every update)
        current_time = time.time()
        if not hasattr(self, '_last_power_log_time') or (current_time - self._last_power_log_time) >= 1.0:
            velocity_error_mph = velocity_error * METERS_PER_SEC_TO_MPH
            self.add_to_status_log(
                f"PI: Power={power_kw:.1f}kW, Error={velocity_error_mph:.1f}mph, "
                f"P={p_term:.1f}, I={i_term:.1f}"
            )
            self._last_power_log_time = current_time
        
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
            self.add_to_status_log(f" CRITICAL: {failure_type} detected!")
            
            if not self.emergency_brake_active:
                self.emergency_brake_active = True
                self.emergency_brake_auto_triggered = True
                self.emergency_light.activate()
                self.add_to_status_log(" Emergency brake auto-activated due to failure!")
                print(f"EMERGENCY BRAKE AUTO-ACTIVATED: {failure_type}")
        else:
            # Failure cleared
            self.add_to_status_log(f"✓ {failure_type} cleared")
            
            # Check if ALL failures are now cleared
            if self.emergency_brake_auto_triggered:
                all_cleared = not (
                    self.engine_failure.active or
                    self.signal_failure.active or
                    self.brake_failure.active
                )
                
                if all_cleared:
                    self.add_to_status_log("✓ All failures cleared - Safe to release emergency brake")
                    # Optional: Auto-release if ALL failures are cleared
                    # self.emergency_brake_active = False
                    # self.emergency_brake_auto_triggered = False
                    # self.emergency_light.deactivate()
    
    def update_displays(self):
        """Update all displays periodically"""
        # Update brake effect on speed
        self.apply_brake_effect()
        
        # Update door safety
        self.update_door_safety()
        
        # Calculate and send power command
        # Only send power when NOT in emergency brake and NOT in service brake
        if not self.emergency_brake_active and not self.service_brake_active:
            try:
                # Calculate power using PI controller
                power_kw = self.calculate_power_command()
                
                # Convert kW to Watts for Train Model
                power_watts = power_kw * KW_TO_WATTS
                
                # Only send if power changed significantly (more than 100W / 0.1kW)
                # This reduces message flooding
                if self.last_power_sent is None or abs(power_watts - self.last_power_sent) > 100:
                    self.send_setpoint_power(power_kw)
                    self.last_power_sent = power_watts
            
            except Exception as e:
                print(f"Error in power calculation: {e}")
        else:
            # Braking active - send zero power
            if self.last_power_sent != 0:
                self.send_setpoint_power(0.0)
                self.last_power_sent = 0
        
        # Schedule next update (100ms = 0.1s sample time)
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
        self.send_drivetrain_mode(self.is_auto_mode)  # Send to train model
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
        """Increase temperature setpoint"""
        self.set_temp = min(85, self.set_temp + 1)
        self.set_temp_value.config(text=f"{self.set_temp}°F")
        self.add_to_status_log(f"Temperature set point increased to: {self.set_temp}°F")
        # Only send if AC is currently on
        if self.power_btn.is_on:
            self.send_cabin_temperature_control(self.set_temp)
        print(f"Set temperature: {self.set_temp}°F")
    
    def decrease_temp(self):
        """Decrease temperature setpoint"""
        self.set_temp = max(60, self.set_temp - 1)
        self.set_temp_value.config(text=f"{self.set_temp}°F")
        self.add_to_status_log(f"Temperature set point decreased to: {self.set_temp}°F")
        # Only send if AC is currently on
        if self.power_btn.is_on:
            self.send_cabin_temperature_control(self.set_temp)
        print(f"Set temperature: {self.set_temp}°F")
    
    def toggle_ac(self, state):
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"AC Power: {status}")
        self.send_air_conditioning(state)  # Send to train model
    # Also send temperature setpoint when AC is turned on
        if state:
            self.send_cabin_temperature_control(self.set_temp)
        print(f"AC Power: {status}")
    
    def press_horn(self):
        self.add_to_status_log("Train horn activated")
        self.send_train_horn(True)  # Horn on
        print("Train horn pressed!")

        self.root.after(2000, lambda: self.send_train_horn(False))
    
    def service_brake_action(self, pressed):
        if pressed:
            self.service_brake_active = True
            deceleration = 1.2  # m/s² (positive value for deceleration)
            self.send_service_brake(deceleration)
            self.add_to_status_log(f"Service brake applied")
            print(f"Service brake applied")
        else:
            self.service_brake_active = False
            self.send_service_brake(0)  # Release brake
            self.add_to_status_log("Service brake released")
            print("Service brake: RELEASED")
    
    def emergency_brake_action(self, pressed):
        """Handle emergency brake button press"""
        if pressed:
            self.emergency_brake_active = True
            self.emergency_light.activate()
            self.send_emergency_brake_signal(True)  # Send to train model
            self.add_to_status_log(" EMERGENCY BRAKE ACTIVATED!")
            print("EMERGENCY BRAKE ACTIVATED!")
        else:
            # Check if it's safe to release (no active failures)
            failure_detected = (
                self.engine_failure.active or
                self.signal_failure.active or
                self.brake_failure.active
            )
            
            if failure_detected:
                self.add_to_status_log(" Cannot release e-brake: Active system failure!")
                print("E-brake release DENIED - failure active")
                # Don't change brake state - keep it active
                return
            
            # Safe to release
            self.emergency_brake_active = False
            self.emergency_brake_auto_triggered = False
            self.emergency_light.deactivate()
            self.send_emergency_brake_signal(False)  # Send to train model
            self.add_to_status_log(" Emergency brake released")
            print("Emergency brake deactivated")
    
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
                'command': "Setpoint Power",
                'value': float(power_kw)
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
                'value': bool(is_active)
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
                'value': bool(is_on)
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
                'value': bool(is_on)
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
                'value': bool(is_open)
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
                'value': bool(is_open)
            })
            print(f"Sent right door signal: {is_open}")
        except Exception as e:
            print(f"Error sending right door signal: {e}")


    def send_air_conditioning(self, is_on):
        """
        Send air conditioning on/off to Train Model
        Input: boolean
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Air Conditioning",
                'value': bool(is_on)
            })
            print(f"Sent AC: {is_on}")
        except Exception as e:
            print(f"Error sending AC signal: {e}")


    def send_cabin_temperature_control(self, temp_fahrenheit):
        """
        Send cabin temperature setpoint to Train Model
        Input: temperature in Fahrenheit
        Output: temperature in Fahrenheit (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Cabin Interior Temperature Control",
                'value': float(temp_fahrenheit)
            })
            print(f"Sent temperature setpoint: {temp_fahrenheit}°F")
        except Exception as e:
            print(f"Error sending temperature setpoint: {e}")


    def send_drivetrain_mode(self, is_auto):
        """
        Send drivetrain mode to Train Model
        Input: boolean (True = auto, False = manual)
        Output: boolean (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Drivetrain Mode",
                'value': bool(is_auto)
            })
            print(f"Sent drivetrain mode: {'auto' if is_auto else 'manual'}")
        except Exception as e:
            print(f"Error sending drivetrain mode: {e}")


    def send_service_brake(self, deceleration_ms2):
        """
        Send service brake to Train Model
        Input: deceleration in m/s²
        Output: deceleration in m/s² (no conversion needed)
        
        Note: When service brake is active, send the deceleration rate.
        When released, send 0.
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Service Brake",
                'value': float(deceleration_ms2)
            })
            print(f"Sent service brake: {deceleration_ms2} m/s²")
        except Exception as e:
            print(f"Error sending service brake: {e}")


    def send_station_announcement(self, message):
        """
        Send station announcement message to Train Model
        Input: string message
        Output: string (no conversion needed)
        """
        try:
            self.server.send_to_ui("Train Model", {
                'command': "Station Announcement Message",
                'value': str(message)
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
                'value': bool(is_active)
            })
            print(f"Sent train horn: {is_active}")
        except Exception as e:
            print(f"Error sending train horn: {e}")

    def on_closing(self):
        """Handle application closing"""
        print("Closing application...")
        self.server.running = False
        if self.server.server_socket:
            try:
                self.server.server_socket.close()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Main_Window(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()