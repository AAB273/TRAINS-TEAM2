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
        
        # Make fullscreen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.configure(bg="navy")

        # Socket server setup
        self.server = TrainSocketServer(port=6, ui_id="Train SW")
        self.server.set_allowed_connections(["Train Model", "Track Model"])
        self.server.start_server(self._process_message)
        self.server.connect_to_ui('localhost', 12346, "Train Model", "Track Model")
        
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
        self.brake_percentage_display = tk.Label(speedometer_frame, text="Service Brake: 0%", 
                                                font=("Arial", 12, "bold"), bg="white", fg="red")
        self.brake_percentage_display.pack(pady=2)
        
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
            self.train_horn = tk.Button(main_container, text="Train Horn\n🎺", 
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
        
        # Brake Percentage Control
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
        
        # Emergency Brake
        self.emergency_brake = Brake_button(main_container, radius=70, color="darkred", 
                                            hover_color="red", active_color="red4",
                                            text="Emergency\nBrake", 
                                            command=self.emergency_brake_action, canvas_bg="white")
        self.emergency_brake.place(relx=.69, rely=.52)
        
        # Emergency Light
        self.emergency_light = EmergencyLight(main_container, size=100)
        self.emergency_light.place(relx=.7, rely=.41)
        
        tk.Label(main_container, text="Emergency Signal", font=("Arial", 14, "bold"),
                bg="lightgray", fg="darkred").place(relx=.68, rely=.38)
        
        # Control Buttons Grid
        self.button_grid_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.button_grid_frame.place(relx=0.75, rely=0.68, relwidth=0.22, relheight=0.28)
        
        try:
            self.bulb_logo = tk.PhotoImage(file="bulb.png").subsample(9, 9)
            self.cabin_lights_btn = ToggleButton(self.button_grid_frame, image=self.bulb_logo,
                                                callback=self.toggle_cabin_lights)
            self.cabin_lights_btn.image = self.bulb_logo
        except:
            self.cabin_lights_btn = ToggleButton(self.button_grid_frame, text="💡", 
                                                font=("Arial", 24), callback=self.toggle_cabin_lights)
        self.cabin_lights_btn.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        
        try:
            self.headlight_logo = tk.PhotoImage(file="headlight.png").subsample(5, 5)
            self.headlights_btn = ToggleButton(self.button_grid_frame, image=self.headlight_logo,
                                              callback=self.toggle_headlights)
            self.headlights_btn.image = self.headlight_logo
        except:
            self.headlights_btn = ToggleButton(self.button_grid_frame, text="🔦", 
                                              font=("Arial", 24), callback=self.toggle_headlights)
        self.headlights_btn.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        
        try:
            self.left_door_logo = tk.PhotoImage(file="leftdoor.png").subsample(10, 10)
            self.left_door_btn = ToggleButton(self.button_grid_frame, image=self.left_door_logo,
                                             callback=self.toggle_left_door)
            self.left_door_btn.image = self.left_door_logo
        except:
            self.left_door_btn = ToggleButton(self.button_grid_frame, text="◄|", 
                                             font=("Arial", 24), callback=self.toggle_left_door)
        self.left_door_btn.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        
        try:
            self.right_door_logo = tk.PhotoImage(file="right.png").subsample(10, 10)
            self.right_door_btn = ToggleButton(self.button_grid_frame, image=self.right_door_logo,
                                              callback=self.toggle_right_door)
            self.right_door_btn.image = self.right_door_logo
        except:
            self.right_door_btn = ToggleButton(self.button_grid_frame, text="|►", 
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
        logo_frame.place(relx=0.01, rely=0.01, relwidth=0.12, relheight=0.24)
        
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

        # State variables
        self.current_speed = 0
        self.set_speed = 45
        self.set_temp = 68
        self.is_auto_mode = True
        self.service_brake_percentage = 50  # Default to 50%
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.door_safety_lock = True
        
        self.update_displays()
        # Test Panel
        #self.test_panel = TestPanel(self.root, self)

        #safety critical design:
        self.safety_monitor = SafetyMonitor(self)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _process_message(self, message, source_ui_id):
        """Process incoming messages and update train state"""
        try:
            print(f"Received message from {source_ui_id}: {message}")

            command = message.get('command')
            value = message.get('value')
            
            if command == 'Commanded Authority':
                #set authority command
            if command == 'Commanded Speed': 
                #set commanded
            if command == "Passenger Emergency Signal":
                #set signal light
            if command == "Actual Velocity":
                #set speedometer
            if command == "Cabin Temperature": 
                #set cabin temp
            if command == "Failure Modes": 
                #set failure lights
            if command == "Beacon Data": 
                #update beacon information
            if command == "Preloaded Track Information":
                #update track information
            if command == "Light States": 
                #display lights states
        except Exception as e:
            print(f"Error processing message: {e}")

    
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
    
    def update_displays(self):
        """Update all displays periodically"""
        # Update brake effect on speed
        self.apply_brake_effect()
        
        # Update door safety
        self.update_door_safety()

        #check failure modes:
        self.check_failure_modes()

        #safety critical implementation
        #self.safety_monitor.check_vital_conditions()

        # Schedule next update
        self.root.after(100, self.update_displays)

    
    def apply_brake_effect(self):
        """Apply brake effects to current speed"""
        if self.emergency_brake_active:
            # Emergency brake: immediate full deceleration
            if self.current_speed > 0:
                self.current_speed = max(0, self.current_speed - 20)  # Rapid deceleration
                self.set_current_speed(self.current_speed)
                self.se
        elif self.service_brake_active:
            # Service brake: gradual deceleration based on percentage
            deceleration_rate = self.service_brake_percentage * 0.1  # Scale factor
            if self.current_speed > 0:
                self.current_speed = max(0, self.current_speed - deceleration_rate)
                self.set_current_speed(self.current_speed)
    
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
        if not self.is_auto_mode:
            self.commanded_speed_value.config(text=str(self.set_speed))
            self.add_to_status_log(f"Commanded speed confirmed: {self.set_speed} mph")
            print(f"Commanded speed set to: {self.set_speed}")
    
    def increase_temp(self):
        self.set_temp = min(85, self.set_temp + 1)
        self.set_temp_value.config(text=f"{self.set_temp}°F")
        self.add_to_status_log(f"Temperature set point increased to: {self.set_temp}°F")
        print(f"Set temperature: {self.set_temp}°F")
    
    def decrease_temp(self):
        self.set_temp = max(60, self.set_temp - 1)
        self.set_temp_value.config(text=f"{self.set_temp}°F")
        self.add_to_status_log(f"Temperature set point decreased to: {self.set_temp}°F")
        print(f"Set temperature: {self.set_temp}°F")
    
    def toggle_ac(self, state):
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"AC Power: {status}")
        print(f"AC Power: {status}")
    
    def press_horn(self):
        self.add_to_status_log("Train horn activated")
        print("Train horn pressed!")
    
    def service_brake_action(self, pressed):
        if pressed:
            self.service_brake_active = True
            self.add_to_status_log(f"Service brake activated at {self.service_brake_percentage}%")
            print(f"Service brake: PRESSED at {self.service_brake_percentage}%")
        else:
            self.service_brake_active = False
            self.add_to_status_log("Service brake released")
            print("Service brake: RELEASED")
    
    def emergency_brake_action(self, pressed):
        if pressed:
            self.emergency_brake_active = True
            self.emergency_light.activate()
            self.add_to_status_log(" EMERGENCY BRAKE ACTIVATED!")
            print("EMERGENCY BRAKE ACTIVATED!")
        else:
            self.emergency_brake_active = False
            self.emergency_light.deactivate()
            self.add_to_status_log("Emergency brake deactivated")
            print("Emergency brake deactivated")
    
    def toggle_cabin_lights(self, state):
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"Cabin lights: {status}")
        print(f"Cabin lights: {status}")
    
    def toggle_headlights(self, state):
        status = "ON" if state else "OFF"
        self.add_to_status_log(f"Headlights: {status}")
        print(f"Headlights: {status}")
    
    def toggle_left_door(self, state):
        if self.current_speed > 0:
            self.add_to_status_log("Left door: REQUEST DENIED - Train moving")
            return
            
        status = "OPEN" if state else "CLOSED"
        self.add_to_status_log(f"Left door: {status}")
        print(f"Left door: {status}")
    
    def toggle_right_door(self, state):
        if self.current_speed > 0:
            self.add_to_status_log("Right door: REQUEST DENIED - Train moving")
            return
            
        status = "OPEN" if state else "CLOSED"
        self.add_to_status_log(f"Right door: {status}")
        print(f"Right door: {status}")
    
    def open_station_window(self):
        self.station_window.show_window()
    
    def expand_station_window(self):
        self.station_window.show_window()
    
    def on_station_announce(self, line, station):
        self.add_to_status_log(f"Station announcement: {station} on {line}")
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
            self.add_to_status_log("⚠️ FAILURE DETECTED: Activating emergency brake.")
            self.emergency_brake_action(True)
        elif not failure_detected and self.emergency_brake_active:
            # Automatically release when all failures are cleared
            self.add_to_status_log("✅ All failures cleared: Releasing emergency brake.")
            self.emergency_brake_action(False)


    def open_track_info(self):
        """Opens the Track Information Panel"""
        if not hasattr(self, "track_info_window") or not tk.Toplevel.winfo_exists(self.track_info_window):
            self.track_info_window = tk.Toplevel(self.root)
            self.track_info_window.title("Track Information Panel")
            self.track_info_panel = TrackInformationPanel(self.track_info_window)
        else:
            self.track_info_window.lift()

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
    root.mainloop()