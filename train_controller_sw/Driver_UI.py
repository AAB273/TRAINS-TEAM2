import tkinter as tk
from tkinter import ttk
import math
import time
from ClockDisplay import ClockDisplay
from CircleButton import Circle_button
from Emlight import EmergencyLight
from speedometer import Speedometer
from SA_display import StationAnnouncementDisplay
from SA_window import StationAnnouncementWindow
from Test_UI import TestPanel
from TC_SW_TrackInfo import TrackInformationPanel


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
        
        main_container = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=5)
        main_container.place(relx=0.02, rely=0.08, relwidth=0.96, relheight=0.9)
        
        title_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=2)
        title_frame.place(relx=0.4, rely=0.01, relwidth=0.2, relheight=0.05)
        tk.Label(title_frame, text="Monitor Display", font=("Arial", 18, "bold"), 
                bg="white").pack(pady=5)
        
        #tab to open track info
                # === Track Info Button (top bar) ===
        track_btn = tk.Button(self.root, text="Track Info", font=("Arial", 12, "bold"),
                              bg="lightblue", fg="black", relief=tk.RAISED, bd=2,
                              command=self.open_track_info)
        track_btn.place(relx=0.63, rely=0.015, relwidth=0.08, relheight=0.045)

        
        # Driver Mode Frame - centered at top
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
        
        # Commanded Speed Frame - below speedometer (better formatting, no cutoff)
        self.commanded_speed_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.commanded_speed_frame.place(relx=0.32, rely=0.69, relwidth=0.36, relheight=0.27)
        
        # Use grid with proper column configuration for centering
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
        
        # AC Frame - left side (better formatting and filling)
        self.ac_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.ac_frame.place(relx=0.02, rely=0.25, relwidth=0.18, relheight=0.35)
        
        # Configure grid to center and fill
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
        
        # Authority Frame - bottom left
        self.authority_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.authority_frame.place(relx=0.02, rely=0.65, relwidth=0.22, relheight=0.25)
        
        tk.Label(self.authority_frame, text="Commanded\nAuthority:", 
                font=("Arial", 14, "bold"), bg="lightblue").pack(pady=10)
        
        blocks_frame = tk.Frame(self.authority_frame, bg="lightgrey", relief=tk.SUNKEN, bd=2)
        blocks_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.authority_value = tk.Label(blocks_frame, text="3 Blocks", 
                                       font=("Arial", 20, "bold"), bg="lightgrey")
        self.authority_value.pack(expand=True)
        
        # Train Horn Button - left middle
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

        
        # Service Brake - left lower middle (raised higher)
        self.service_brake = Circle_button(main_container, radius=80, color="orange", 
                                          hover_color="darkorange", active_color="orange4",
                                          text="Service\nBrake", command=self.service_brake_action,
                                          hold_mode=True, canvas_bg="white")
        self.service_brake.place(relx=0.215, rely=0.46)
        
        # Emergency Brake - right lower middle (raised higher)
        self.emergency_brake = Circle_button(main_container, radius=80, color="darkred", 
                                            hover_color="red", active_color="red4",
                                            text="Emergency\nBrake", 
                                            command=self.emergency_brake_action, canvas_bg="white")
        self.emergency_brake.place(relx=0.70, rely=0.46)
        
        # Emergency Light - right of emergency brake
        emergency_container = tk.Frame(main_container, bg="white")
        emergency_container.place(relx=0.8, rely=0.47, relwidth=0.15, relheight=0.25)
        
        self.emergency_light = EmergencyLight(emergency_container, size=120)
        self.emergency_light.pack(pady=(5, 2))
        
        tk.Label(emergency_container, text="Emergency Signal", font=("Arial", 11, "bold"),
                bg="white", fg="darkred").pack(pady=2)
        
        # Control Buttons Grid - bottom right
        self.button_grid_frame = tk.Frame(main_container, bg="grey", relief=tk.RAISED, bd=2)
        self.button_grid_frame.place(relx=0.75, rely=0.68, relwidth=0.22, relheight=0.28)
        
        # Try to load images, fallback to text
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
        
        # BLT Logo - top left (bigger container to show full logo)
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

        #adding the failure modes: 
                # === Failure Indicators Row (between BLT logo and clock) ===
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
        self.brake_failure = FailureIndicator(lights_frame, size=40, color="gray", glow_color="red")
        self.brake_failure.grid(row=0, column=2, padx=5)
        tk.Label(lights_frame, text="BF", font=("Arial", 9, "bold"), bg="white", fg="black").grid(row=1, column=2)

        
        # Station Announcement Display - embedded in main window
        self.station_display = StationAnnouncementDisplay(main_container, 
                                                         callback=self.on_station_announce,
                                                         expand_callback=self.expand_station_window)
        self.station_display.place(relx=0.70, rely=0.02, relwidth=0.28, relheight=0.35)
        
        self.station_window = StationAnnouncementWindow(self.root, 
                                                       callback=self.on_station_announce)
        
        #clock frame
        self.clock_frame = tk.Label(self.root, bg="lightblue")
        self.clock_frame.place(relx=.3, rely=0.15)
        self.clock = ClockDisplay(self.clock_frame)
        self.clock.pack(padx=5, pady=5)

        self.current_speed = 0
        self.set_speed = 45
        self.set_temp = 68
        self.is_auto_mode = True
        
        self.update_displays()
        # --- TEST PANEL LAUNCH ---
        self.test_panel = TestPanel(self.root, self)

    
    def update_displays(self):
        pass
    
    def on_mode_change(self, mode):
        self.is_auto_mode = (mode == "auto")
        print(f"Mode changed to: {mode}")
    
    def increase_set_speed(self):
        if self.is_auto_mode:
            self.mode_select.set_mode("manual")
        self.set_speed = min(80, self.set_speed + 5)
        self.set_speed_value.config(text=str(self.set_speed))
    
    def decrease_set_speed(self):
        if self.is_auto_mode:
            self.mode_select.set_mode("manual")
        self.set_speed = max(0, self.set_speed - 5)
        self.set_speed_value.config(text=str(self.set_speed))
    
    def confirm_speed(self):
        if not self.is_auto_mode:
            self.commanded_speed_value.config(text=str(self.set_speed))
            print(f"Commanded speed set to: {self.set_speed}")
    
    def increase_temp(self):
        self.set_temp = min(85, self.set_temp + 1)
        self.set_temp_value.config(text=f"{self.set_temp}F")
        print(f"Set temperature: {self.set_temp}F")
    
    def decrease_temp(self):
        self.set_temp = max(60, self.set_temp - 1)
        self.set_temp_value.config(text=f"{self.set_temp}F")
        print(f"Set temperature: {self.set_temp}F")
    
    def toggle_ac(self):
        print("AC toggled")
    
    def toggle_ac(self, state):
        print(f"AC Power: {'ON' if state else 'OFF'}")
    
    def press_horn(self):
        print("Train horn pressed!")
    
    def service_brake_action(self, pressed):
        print(f"Service brake: {'PRESSED' if pressed else 'RELEASED'}")
    
    def emergency_brake_action(self, pressed):
        if pressed:
            print("EMERGENCY BRAKE ACTIVATED!")
            # Emergency light is controlled by external signal, not by brake
    
    def toggle_cabin_lights(self, state):
        print(f"Cabin lights: {'ON' if state else 'OFF'}")
    
    def toggle_headlights(self, state):
        print(f"Headlights: {'ON' if state else 'OFF'}")
    
    def toggle_left_door(self, state):
        print(f"Left door: {'OPEN' if state else 'CLOSED'}")
    
    def toggle_right_door(self, state):
        print(f"Right door: {'OPEN' if state else 'CLOSED'}")
    
    def open_station_window(self):
        self.station_window.show_window()
    
    def expand_station_window(self):
        self.station_window.show_window()
    
    def on_station_announce(self, line, station):
        print(f"Announcing: {station} on {line}")
    
    def set_current_speed(self, speed):
        self.current_speed = speed
        self.speedometer.update_speed(speed)
        self.current_speed_display.config(text=f"Current Speed: {int(speed)} mph")
    
    def set_commanded_speed(self, speed):
        if self.is_auto_mode:
            self.commanded_speed_value.config(text=str(speed))
    
    def set_authority(self, blocks):
        self.authority_value.config(text=f"{blocks} Blocks")
    
    def set_cabin_temp(self, temp):
        self.current_temp.config(text=f"{temp}°F")
    
    def set_emergency_signal(self, active):
        """Method to control emergency light from external module"""
        self.emergency_light.set_state(active)
    
    def open_track_info(self):
        """Opens the Track Information Panel"""
        if not hasattr(self, "track_info_window") or not tk.Toplevel.winfo_exists(self.track_info_window):
            self.track_info_window = tk.Toplevel(self.root)
            self.track_info_window.title("Track Information Panel")
            self.track_info_panel = TrackInformationPanel(self.track_info_window)
        else:
            self.track_info_window.lift()
'''------------------------------------------------------------------------------------------------------------------------------'''
#side window for test ui
'''class TestPanel(tk.Toplevel):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.title("Input Test Panel")
        self.geometry("400x450")
        self.main_window = main_window

        tk.Label(self, text="TEST INTERFACE", font=("Arial", 16, "bold")).pack(pady=10)

        # Temperature Input
        tk.Label(self, text="Set Cabin Temperature (°F):", font=("Arial", 12)).pack(pady=5)
        self.temp_entry = tk.Entry(self)
        self.temp_entry.insert(0, "65")
        self.temp_entry.pack()
        tk.Button(self, text="Send Temp", command=self.set_temp).pack(pady=5)

        # Commanded Authority Input
        tk.Label(self, text="Set Commanded Authority (Blocks):", font=("Arial", 12)).pack(pady=5)
        self.auth_entry = tk.Entry(self)
        self.auth_entry.insert(0, "4")
        self.auth_entry.pack()
        tk.Button(self, text="Send Authority", command=self.set_authority).pack(pady=5)

        # Commanded Speed Input
        tk.Label(self, text="Set Commanded Speed (mph):", font=("Arial", 12)).pack(pady=5)
        self.speed_entry = tk.Entry(self)
        self.speed_entry.insert(0, "55")
        self.speed_entry.pack()
        tk.Button(self, text="Send Speed", command=self.set_speed).pack(pady=5)

        # Speedometer Input
        tk.Label(self, text="Speedometer (Actual Speed mph):", font=("Arial", 12)).pack(pady=5)
        self.actual_speed = tk.Scale(self, from_=0, to=80, orient=tk.HORIZONTAL, command=self.update_speedometer)
        self.actual_speed.pack(fill="x", padx=20)

        # Emergency Signal
        tk.Label(self, text="Emergency Signal:", font=("Arial", 12)).pack(pady=10)
        tk.Button(self, text="Activate Emergency", bg="red", fg="white", command=self.activate_emergency).pack(pady=3)
        tk.Button(self, text="Deactivate Emergency", bg="grey", fg="white", command=self.deactivate_emergency).pack(pady=3)

        # Output Log
        tk.Label(self, text="Log:", font=("Arial", 12, "bold")).pack(pady=5)
        self.log = tk.Text(self, height=6, width=40, state=tk.DISABLED)
        self.log.pack(pady=5)

    def log_action(self, text):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def set_temp(self):
        val = self.temp_entry.get()
        self.main_window.current_temp.config(text=f"{val}°F")
        self.log_action(f"✅ Temperature input set to {val}°F")

    def set_authority(self):
        val = self.auth_entry.get()
        self.main_window.authority_value.config(text=f"{val} Blocks")
        self.log_action(f"✅ Commanded authority set to {val} Blocks")

    def set_speed(self):
        val = self.speed_entry.get()
        # Only update commanded speed when in auto mode
        if self.main_window.mode_select.active_mode == "auto":
            self.main_window.commanded_speed_value.config(text=val)
            self.log_action(f"✅ Commanded speed set to {val} mph (auto mode)")
        else:
            self.log_action("⚠️ Ignored commanded speed (not in auto mode)")

    def update_speedometer(self, val):
        val = int(val)
        self.main_window.speedometer.update_speed(val)
        self.main_window.current_speed_display.config(text=f"Current Speed: {val} mph")
        self.log_action(f"✅ Speedometer updated to {val} mph")

    def activate_emergency(self):
        self.main_window.emergency_light.activate()
        self.log_action("🚨 Emergency signal activated")

    def deactivate_emergency(self):
        self.main_window.emergency_light.deactivate()
        self.log_action("🟢 Emergency signal cleared")
'''

'''---------------------------------------------------------------------------------------------------------------------------------'''
if __name__ == "__main__":
    root = tk.Tk()
    app = Main_Window(root)

    '''
    def test_speed_update():
        import random
        speed = random.randint(0, 80)
        app.set_current_speed(speed)
        root.after(2000, test_speed_update)'''
    
    #test_speed_update()
    
    root.mainloop()