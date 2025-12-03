import json    
from pathlib import Path 

def load_socket_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config.get("modules", {})


import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font
from tkinter import ttk
from train_data import get_train_manager
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer
import clock
import time
import string
from playsound import playsound
import random

class TrainModelPassengerGUI:
    def __init__(self):
        self.main_color = '#1a1a4d'
        self.off_color = '#4d4d6d'
        self.current_train = None
        self.train_manager = get_train_manager()
        self.current_train = self.train_manager.get_selected_train()
        
        # Socket server setup
        module_config = load_socket_config()
        train_model_config = module_config.get("Train Model", {"port": 12345})
        self.server = TrainSocketServer(port=train_model_config["port"], ui_id="Train Model")
        self.server.set_allowed_connections(["Train SW", "Train HW", "Track Model", "Test_UI"])
        self.server.start_server(self._process_message)
        
        

        # Connect using ports from config
        train_sw_config = module_config.get("Train SW", {"port": 12346})
        train_hw_config = module_config.get("Train HW", {"port": 12347})
        track_model_config = module_config.get("Track Model", {"port": 12344})

        self.server.connect_to_ui('localhost', train_sw_config["port"], "Train SW")
        self.server.connect_to_ui('localhost', train_hw_config["port"], "Train HW")
        self.server.connect_to_ui('localhost', track_model_config["port"], "Track Model")
        self.server.connect_to_ui('localhost',12349,"Test_UI")
        
        self.ui_labels = {}
        self.ui_indicators = {}
        self.canvas_frame_circle = None

        self.previous_failure_signal_pickup_state = False
        self.failure_activation_in_progress = False
        
        self.setup_gui()
        
    def _socket_refresh_train_selector(self):
        """Refresh the train selector UI to show/hide trains based on deployment status"""
        print("Socket server requesting train selector refresh")
        self.root.after(0, self.refresh_train_selector)

    def _animate_temperature_change(self, target_temp):
        """Gradually change temperature using Tkinter's after()"""
        if not self.current_train:
            return

        current_temp = self.current_train.cabin_temp
        target_temp = float(target_temp)
        
        if current_temp < target_temp:
            new_temp = current_temp + 1
            self.current_train.set_cabin_temp(new_temp)
            self.update_ui_from_train(self.current_train)
            self.root.after(1000, lambda: self._animate_temperature_change(target_temp))
        elif current_temp > target_temp:
            new_temp = current_temp - 1
            self.current_train.set_cabin_temp(new_temp)
            self.update_ui_from_train(self.current_train)
            self.root.after(1000, lambda: self._animate_temperature_change(target_temp))
            
        self.server.send_to_ui("Train Controller",{"Temp",current_temp})
   
    def _process_message(self, message, source_ui_id):

            try:
                print(f"Received message from {source_ui_id}: {message}")

                command = message.get('command')
                value = message.get('value')
              #Test Commands###########################################################  
                if command == 'set_power':
                    self.current_train.last_power_command = self.current_train.power_command
                    self.current_train.set_power_command(value)
                elif command == 'set_right_door':
                    if value == 'open':
                        self.current_train.set_right_door(1)
                    elif value == 'close':
                        self.current_train.set_right_door(0)
                elif command == 'set_left_door':
                    if value == 'open':
                        self.current_train.set_left_door(1)
                    elif value == 'close':
                        self.current_train.set_left_door(0)
                elif command == 'set_headlights':
                    if value == 'on':
                        self.current_train.set_headlights(1)
                    else:
                        self.current_train.set_headlights(0)
                elif command == 'set_interior_lights':
                    if value == 'on':
                        self.current_train.set_interior_lights(1)
                    elif value == 'off':
                        self.current_train.set_interior_lights(0)
                elif command == 'emergency_brake':
                    if value == 'on':
                        self.emergency_brake_activated()
                    else:
                        self.current_train.set_emergency_brake(0)
                elif command == 'set_service_brake':
                    if self.failure_brake_var.get():
                        pass
                    else:    
                        if value == 'on':
                            self.current_train.set_service_brake(True)
                        else:
                            self.current_train.set_service_brake(False)
                elif command == 'set_passenger_count':
                    self.current_train.set_passenger_count(value)
                elif command == 'horn':
                    playsound('Train Model\diesel-horn-02-98042.mp3')
                elif command == 'set_speed_limit':
                    self.current_train.set_speed_limit(value)
                elif command == 'set_elevation':
                    self.current_train.set_elevation(value)
                elif command == 'set_grade':
                    self.current_train.set_grade(value)
                elif command == 'select_train':
                    self.on_train_selected(value)
                elif command == 'set_temperature':
                    target_temp = value
                    self._animate_temperature_change(target_temp)
                elif command == 'set_authority':
                    self.current_train.set_authority(value)
                elif command == 'set_station':
                    self.current_train.set_station(value)
                elif command == 'set_time_to_station':
                    self.current_train.set_time_to_station(value)
                elif command == 'deploy_train':
                    train_id = value
                    train = self.train_manager.get_train(train_id)
                    if train:
                        train.deployed = True
                        print(f"Deployed train {train_id}")
                        self._socket_refresh_train_selector()
                        train.calculate_force_speed_acceleration_()
                elif command == 'undeploy_train':
                    train_id = value
                    train = self.train_manager.get_train(train_id)
                    if train:
                        train.deployed = False
                        print(f"Undeployed train {train_id}")
                        self._socket_refresh_train_selector()
                elif command == 'deploy_all':
                    for train_id in range(1, 15):
                        train = self.train_manager.get_train(train_id)
                        if train:
                            train.deployed = True
                            self.current_train.calculate_force_speed_acceleration_()
                    print("Deployed all trains")
                    self._socket_refresh_train_selector()
                elif command == 'undeploy_all':
                    for train_id in range(1, 15):
                        train = self.train_manager.get_train(train_id)
                        if train:
                            train.deployed = False
                    print("Undeployed all trains")
                    self._socket_refresh_train_selector()
                elif command == 'refresh_trains':
                    self._socket_refresh_train_selector()
                ############################################################ 


                #MAIN COMMANDS ############################################# 
                elif command == 'Cabin Interior Temperature Control':
                    target_temp = value
                    self._animate_temperature_change(target_temp)
                elif command == 'Service Brake':
                    if self.failure_brake_var.get:
                        pass
                    else:
                        self.current_train.set_service_brake(value)
                elif command == 'Emergency Brake':
                    self.current_train.set_emergency_brake(value)
                elif command == 'Left Door Signal':
                    self.current_train.set_left_door(value)
                elif command == 'Right Door Signal':
                    self.current_train.set_right_door(value)
                elif command == 'Headlights':
                    self.current_train.set_headlights(value)
                elif command == 'Cabin Lights':
                    self.current_train.set_interior_lights(value)
                elif command == 'Power Command':
                    self.current_train.set_power_command(value)
                elif command == 'Train Horn':
                    playsound("Train Model/diesel-horn-02-98042.mp3")
                elif command == 'Station Announcement Message':
                    self.current_train.set_station(value)
                elif command == 'Commanded Authority':
                    self.current_train.set_authority(value)
                    self.server.send_to_ui("Train SW",{'command': "Commanded Authority",'value': value})
                    self.server.send_to_ui("Train HW",{'command': "Commanded Authority",'value':value})
                elif command == 'Commanded Speed':
                    self.current_train.set_commanded_speed(value)
                    self.server.send_to_ui("Train SW",{'command':"Commanded Speed",'value':value})
                    self.server.send_to_ui("Train HW",{'command':"Commanded Speed",'value':value})
                    self.current_train.set_service_brake(False)
                elif command == 'Block Occupancy': #Figure out signal pickup
                    self.current_train.set_block(value)
                elif command == 'Passengers Boarding':
                    self.update_boarding(value)
                elif command == 'Beacon':
                    if self.current_train.line == 'Green':
                        print("Implement beacon data, figure out how you are gonna reference it.")
                self.update_ui_from_train(self.current_train)
                
            except Exception as e:
                print(f"Error processing message: {e}")

    def continuous_physics_update(self):
        """Continuously update train physics for real-time speed changes"""
        if self.current_train and self.current_train.deployed:
            old_speed = self.current_train.speed
            self.current_train.calculate_force_speed_acceleration_distance()
            new_speed = self.current_train.speed
            if new_speed != old_speed:    
                self.server.send_to_ui("Train HW",{'command': "Current Speed",'value': self.current_train.speed})
                self.server.send_to_ui("Train SW",{'command': "Current Speed",'value': self.current_train.speed})
                self.server.send_to_ui("Track Model",{'command': 'Current Speed', 'value': self.current_train.speed})
            self.update_ui_from_train(self.current_train)
        self.root.after(100, self.continuous_physics_update)

    def emergency_brake_activated(self):
        self.current_train.set_emergency_brake(True)
        self.current_train.set_acceleration(-2.73)
        self.server.send_to_ui("Train HW",{'command': "Passenger Emergency Signal",'value': True})
        self.server.send_to_ui("Train SW",{'command': "Passenger Emergency Signal",'value': True})
        print(f"EMERGENCY BRAKE ACTIVATED!")

    def failure_service_brake_var_changed(self):
        if self.failure_brake_var.get():
            self.current_train.set_service_brake(0)
            self.server.send_to_ui("Train SW",{'command': "Service Brake Failure",'value': True})
            self.server.send_to_ui("Train HW",{'command': "Service Brake Failure",'value': True})
            print(f"Service Brake Failure Activated")
        elif self.failure_brake_var.get() == 0:
            print(f"Service Brake Deactivated")
            self.server.send_to_ui("Train SW",{'command': "Service Brake Failure",'value': False})
            self.server.send_to_ui("Train HW",{'command': "Service Brake Failure",'value': False})

    def failure_train_engine_var_changed(self):
        if self.failure_train_engine_var.get():
            self.current_train.set_engine_failure(True)
            self.current_train.set_power_command(0)
            self.current_train.set_acceleration(0)
            self.server.send_to_ui("Train SW",{'command': "Train Engine Failure",'value': True})
            self.server.send_to_ui("Train HW",{'command': "Train Engine Failure",'value': True})
            print(f"Train Engine Failure Activated")
        elif self.failure_train_engine_var.get() == 0:
            self.current_train.set_engine_failure(False)
            print(f"Train Engine Failure Deactivated")
            self.server.send_to_ui("Train SW",{"Train Engine Failure",0})
            self.server.send_to_ui("Train HW",{"Train Engine Failure",0})

    def update_failure_signal(self):
        current_state = self.failure_signal_pickup_var.get()
        
        # Only proceed if state actually changed
        if current_state == self.previous_failure_signal_pickup_state:
            return
        
        if current_state and not self.failure_activation_in_progress:
            self.activate_signal_failure()
        else:
            self.deactivate_signal_failure()
        
        self.previous_failure_signal_pickup_state = current_state

    def deactivate_signal_failure(self):
        print(f"Signal Pickup Failure Deactivated")
        self.server.send_to_ui("Train SW", {'command': "Signal Pickup Failure", 'value': False})
        self.server.send_to_ui("Train HW", {'command': "Signal Pickup Failure", 'value': False})

    def activate_signal_failure(self):
        print(f"Signal Pickup Failure Activated")
        self.failure_activation_in_progress = True
        
        # Set the values directly without calling methods that might cause loops
        # Your periodic 100ms update will handle the UI refresh
        self.current_train.speed_limit = 0
        self.current_train.grade = 0
        self.current_train.elevation = 0
        
        self.server.send_to_ui("Train SW", {'command': "Signal Pickup Failure", 'value': True})
        self.server.send_to_ui("Train HW", {'command': "Signal Pickup Failure", 'value': True})
        
        self.failure_activation_in_progress = False
            
    def update_disembarking(self):
        if self.current_train and self.current_train.deployed and self.current_train.passenger_count != 0:
            
            if(self.current_train.speed == 0 and self.current_train.service_brake_active  and 
            (self.current_train.right_door_open or self.current_train.left_door_open)):
                
                passenger_count = self.current_train.passenger_count
                disembarking = random(0,passenger_count)
                
                self.current_train.set_disembarking(disembarking)
                self.current_train.set_passenger_count(passenger_count - disembarking)
                self.server.send_to_ui("Track Model",{"command": 'Passenger Disembarking', 'value': disembarking})
                self.server.send_to_ui('Track Model',{'command' : 'Train Occupancy', 'value': self.current_train.passenger_count})

    def update_boarding(self,boarding):
        MAX_CAPACITY = 222
        if boarding > MAX_CAPACITY:
            self.current_train.passenger_count = MAX_CAPACITY + self.current_train.passenger_count
        else:
            self.current_train.passenger_count = self.current_train.passenger_count + boarding

    def update_ui_from_train(self, train):
        """Update all UI elements when train data changes"""
        # Update speed
        imperial_speed = train.speed * 2.23964
        self.ui_labels['speed'].config(text=f"{imperial_speed:.4f} MPH")
        
        # Update acceleration
        imperial_acceleration = train.acceleration * 2.23694
        self.ui_labels['acceleration'].config(text=f"{imperial_acceleration:.4f} MPH²")
        
        # Update passenger count
        self.ui_labels['passenger_count'].config(text=f"Passenger Count: {train.passenger_count}")
        self.ui_labels['disembarking'].config(text=f"Passengers Disembarking: {train.passengers_disembarking}")
        self.ui_labels['crew_count'].config(text=f"Crew Count: {train.crew_count}")


        # SIGNAL PICKUP FAILURE CHECKING ##########################################
        if self.failure_signal_pickup_var.get():
            # Failure active - show ??? values
            self.ui_labels['Commanded Authority'].config(text="Commanded Authority: ??? Blocks")
            self.ui_labels['Commanded Speed'].config(text="Commanded Speed: ??? MPH")
        else:
            self.ui_labels['Commanded Authority'].config(text=f"Commanded Authority: {train.commanded_authority:.0f} Blocks")
            self.ui_labels['Commanded Speed'].config(text=f"Commanded Speed: {train.commanded_speed:.0f} MPH")
    
        # Check for failure state changes
        self.update_failure_signal()

        # Normal operation - show actual values
        imperial_speed_limit = train.speed_limit * 0.621371
        self.ui_labels['Speed Limit'].config(text=f"Speed Limit: {imperial_speed_limit:.1f} MPH")

        # Update Grade and Elevation
        self.ui_labels['Grade'].config(text=f"Grade: {train.grade}%")
        self.ui_labels['Elevation'].config(text=f"Elevation: {train.elevation}ft")
        # Update cabin temp
        if self.canvas_frame_circle and 'cabin_temp' in self.ui_labels:
            self.canvas_frame_circle.itemconfig(self.ui_labels['cabin_temp'], text=f"{train.cabin_temp:.0f}°F")
        
        # Update dimensions
        imperial_height = train.height * 3.28084
        imperial_length = train.length * 3.28084
        imperial_width = train.width * 3.28084
        self.ui_labels['height'].config(text=f"Height: {imperial_height:.1f}ft")
        self.ui_labels['length'].config(text=f"Length: {imperial_length:.1f}ft")
        self.ui_labels['width'].config(text=f"Width: {imperial_width:.1f}ft")

        # Update Announcement and Time
        if self.current_train.emergency_brake_active:
            self.ui_labels['announcement'].config(text=f"EMERGENCY")
        else:
            self.ui_labels['announcement'].config(text=f"Arriving to Station {train.station} in {train.time_to_station}mins")

        # Update power command and commanded values
        self.ui_labels['power_command'].config(text=f"{train.power_command:.0f} Watts")
        
        
        # Update door and light indicators
        right_door_color = 'green' if train.right_door_open else 'red'
        self.ui_indicators['cabin_right_led'].itemconfig(self.ui_indicators['cabin_right_oval'], fill=right_door_color)
        
        left_door_color = 'green' if train.left_door_open else 'red'
        self.ui_indicators['cabin_left_led'].itemconfig(self.ui_indicators['cabin_left_oval'], fill=left_door_color)
        
        headlight_color = 'green' if train.headlights_on else 'red'
        self.ui_indicators['headlights_led'].itemconfig(self.ui_indicators['headlights_oval'], fill=headlight_color)
        
        interior_color = 'green' if train.interior_lights_on else 'red'
        self.ui_indicators['interior_led'].itemconfig(self.ui_indicators['interior_oval'], fill=interior_color)

    def on_train_selected(self, train_id):
        """Handle train selection from dropdown"""
        train = self.train_manager.select_train(train_id)
        if train and train.deployed:
            self.current_train = train
            self.update_ui_from_train(train)
            self.train_selector_var.set(f"Train {train_id}")
        else:
            print(f"Train {train_id} is not deployed or doesn't exist")

    def refresh_train_selector(self):
        """Update the dropdown menu with currently deployed trains"""
        print("Refreshing train selector dropdown...")
        
        current_selection = self.train_selector_var.get()
        self.train_selector['menu'].delete(0, 'end')
        
        deployed_trains = []
        for train_id in range(1, 15):
            train = self.train_manager.get_train(train_id)
            if train and train.deployed:
                deployed_trains.append(train_id)
        
        print(f"Found {len(deployed_trains)} deployed trains: {deployed_trains}")
        
        for train_id in deployed_trains:
            self.train_selector['menu'].add_command(
                label=f"Train {train_id}", 
                command=lambda tid=train_id: self.on_train_selected(tid)
            )
        
        self.train_selector_label.config(text=f"Select Train ({len(deployed_trains)} Deployed)")
        
        if self.current_train and hasattr(self.current_train, 'train_id') and self.current_train.train_id in deployed_trains:
            self.train_selector_var.set(f"Train {self.current_train.train_id}")
        elif deployed_trains:
            first_train_id = deployed_trains[0]
            self.train_selector_var.set(f"Train {first_train_id}")
            self.on_train_selected(first_train_id)
        else:
            self.train_selector_var.set("No Trains Deployed")

    def setup_gui(self):
        """Setup the complete GUI"""
        self.root = tk.Tk()
        self.root.title("Passenger Train Model GUI")
        self.root.configure(bg=self.main_color)
        self.root.geometry("900x800")  

        # Train Selector Dropdown Frame 
        train_selector_container = tk.Frame(self.root, bg=self.main_color, height=30)
        train_selector_container.pack(fill='x', padx=8, pady=3)
        train_selector_container.pack_propagate(False)

        self.train_selector_label = tk.Label(train_selector_container, text="Select Train", bg=self.main_color, fg='white', font=('Arial', 10, 'bold'))
        self.train_selector_label.pack(side='left', padx=(8, 3))

        # Train Selector
        self.train_selector_var = tk.StringVar()
        self.train_selector = tk.OptionMenu(train_selector_container, self.train_selector_var, "Loading...")
        self.train_selector.config(bg=self.main_color, fg='white', font=('Arial', 9), width=20)  
        self.train_selector.pack(side='left', padx=(0, 8))
        self.train_selector['menu'].config(bg=self.main_color, fg='white')

        # Top Container
        top_container = tk.Frame(self.root, bg=self.main_color, highlightbackground="black", highlightthickness=3)
        top_container.pack(fill='x', padx=8, pady=3)

        # BLT Logo 
        blt_logo_image = Image.open("Train Model/blt logo.png")
        converted_blt_logo_image = blt_logo_image.resize((60, 60))
        converted_blt_logo_image = ImageTk.PhotoImage(converted_blt_logo_image)
        blt_logo_frame = tk.Frame(top_container, bg=self.main_color, height=65, width=65)
        blt_logo_frame.pack(fill='x', side='left', pady=2, padx=2)
        blt_logo_frame.pack_propagate(False)
        tk.Label(blt_logo_frame, image=converted_blt_logo_image, bg=self.main_color).pack(padx=1, pady=1)
        blt_logo_frame.image = converted_blt_logo_image

        # Time Frame
        time_frame = tk.Frame(top_container, bg=self.off_color, width=150, height=65, highlightbackground="black", highlightthickness=3)
        time_frame.pack(side='left', padx=2, pady=2)
        time_frame.pack_propagate(False)
        self.ui_labels['time'] = tk.Label(time_frame, text="Time", bg=self.off_color, fg='white', font=('Arial', 16, 'bold'))
        self.ui_labels['time'].pack(padx=3, pady=3)

        # Announcement Frame 
        Announcement_frame = tk.Frame(top_container, bg=self.off_color, width=600, height=65, highlightbackground="black", highlightthickness=3)
        Announcement_frame.pack(side='left', padx=2, pady=2)
        Announcement_frame.pack_propagate(False)
        self.ui_labels['announcement'] = tk.Label(Announcement_frame, text="Arriving to Dormount in 5 seconds", bg=self.off_color, fg='white', font=('Arial', 16, 'bold'))
        self.ui_labels['announcement'].pack(padx=3, pady=3)

        # Main frames
        left_frame = tk.Frame(self.root, bg=self.main_color)
        left_frame.pack(side='left', fill='both', padx=8, pady=3)

        right_frame = tk.Frame(self.root, bg=self.main_color)
        right_frame.pack(side='right', fill='both', expand=True, padx=8, pady=3)

        # Advertisement Frame 
        ad_image = Image.open("Train Model/wendy's_AD.jpg")
        converted_ad_image = ad_image.resize((400, 180))
        converted_ad_image = ImageTk.PhotoImage(converted_ad_image)
        Advertisement = tk.Frame(right_frame, height=190, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        Advertisement.pack(side='top', padx=2, pady=2, fill='x')
        Advertisement.pack_propagate(False)
        tk.Label(Advertisement, image=converted_ad_image).pack(padx=1, pady=1)
        Advertisement.image = converted_ad_image

        # Doors/Lights Frame 
        doors_and_lights_frame = tk.Frame(right_frame, height=200, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        doors_and_lights_frame.pack(side='top', padx=2, pady=2, fill='x')
        doors_and_lights_frame.pack_propagate(False)

        # Cabin Doors 
        cabin_doors_frame = tk.Frame(doors_and_lights_frame, bg=self.off_color)
        cabin_doors_frame.pack(side='left', padx=3, pady=2, fill='both', expand=True)

        tk.Label(cabin_doors_frame, text="Right Door", bg=self.off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
        cabin_right_led = tk.Canvas(cabin_doors_frame, width=120, height=40, bg=self.off_color, highlightthickness=0)
        cabin_right_led.pack(pady=3)
        cabin_right_oval = cabin_right_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
        self.ui_indicators['cabin_right_led'] = cabin_right_led
        self.ui_indicators['cabin_right_oval'] = cabin_right_oval

        thin_line = tk.Frame(cabin_doors_frame, bg='black', height=1)
        thin_line.pack(pady=8, fill='x', padx=15)

        tk.Label(cabin_doors_frame, text="Left Door", bg=self.off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
        cabin_left_led = tk.Canvas(cabin_doors_frame, width=120, height=40, bg=self.off_color, highlightthickness=0)
        cabin_left_led.pack(pady=3)
        cabin_left_oval = cabin_left_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
        self.ui_indicators['cabin_left_led'] = cabin_left_led
        self.ui_indicators['cabin_left_oval'] = cabin_left_oval

        # Lights 
        lights_frame = tk.Frame(doors_and_lights_frame, bg=self.off_color)
        lights_frame.pack(side='left', padx=3, pady=2, fill='both', expand=True)

        tk.Label(lights_frame, text="Headlights", bg=self.off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
        headlights_led = tk.Canvas(lights_frame, width=120, height=40, bg=self.off_color, highlightthickness=0)
        headlights_led.pack(pady=3)
        headlights_oval = headlights_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
        self.ui_indicators['headlights_led'] = headlights_led
        self.ui_indicators['headlights_oval'] = headlights_oval

        thin_line = tk.Frame(lights_frame, bg='black', height=1)
        thin_line.pack(pady=8, fill='x', padx=15)

        tk.Label(lights_frame, text="Interior Lights", bg=self.off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
        Interior_led = tk.Canvas(lights_frame, width=120, height=40, bg=self.off_color, highlightthickness=0)
        Interior_led.pack(pady=3)
        interior_oval = Interior_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
        self.ui_indicators['interior_led'] = Interior_led
        self.ui_indicators['interior_oval'] = interior_oval

        # Murphy Failure Modes 
        murphy_frame = tk.Frame(right_frame, height=200, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        murphy_frame.pack(side='top', padx=2, pady=2, fill='both')
        murphy_frame.pack_propagate(False)
        tk.Label(murphy_frame, text="Murphy Failure Modes", bg=self.off_color, fg='white', font=('Arial', 16, 'bold')).pack(pady=3)

        #Separator lines in Murphy frame
        thin_line = tk.Frame(murphy_frame, bg='black', width=400)
        thin_line.pack(pady=2)

        self.failure_train_engine_var = tk.BooleanVar(value=False)
        train_engine_switch = ttk.Checkbutton(murphy_frame, text="Train Engine", variable=self.failure_train_engine_var, 
                                              command=lambda: self.failure_train_engine_var_changed(),
                                              style="Medium.TCheckbutton")
        train_engine_switch.pack(pady=6, padx=3, fill='x', expand=True)

        #Separator line
        thin_line = tk.Frame(murphy_frame, bg='black', width=400)
        thin_line.pack(pady=2)

        self.failure_signal_pickup_var = tk.BooleanVar(value=False)
        signal_pickup_switch = ttk.Checkbutton(murphy_frame, text="Signal Pickup", variable=self.failure_signal_pickup_var,
                                               style="Medium.TCheckbutton")
        signal_pickup_switch.pack(pady=6, padx=3, fill='x', expand=True)

        #Separator line
        thin_line = tk.Frame(murphy_frame, bg='black', width=400)
        thin_line.pack(pady=2)

        self.failure_brake_var = tk.BooleanVar(value=False)
        brake_switch = ttk.Checkbutton(murphy_frame, text="Brake", variable=self.failure_brake_var,
                                       command=lambda: self.failure_service_brake_var_changed(),
                                       style="Medium.TCheckbutton")
        brake_switch.pack(pady=6, padx=3, fill='x', expand=True)

        # Passenger Disembarking
        pass_disembarking_frame = tk.Frame(right_frame, highlightbackground="black", highlightthickness=2, bg=self.off_color, height=50)
        pass_disembarking_frame.pack(side='top', padx=1, pady=1, fill='both')

        disembarking_content = tk.Frame(pass_disembarking_frame, bg=self.off_color)
        disembarking_content.pack(expand=True, fill='both', padx=3, pady=3)

        self.ui_labels['disembarking'] = tk.Label(disembarking_content, text="Passengers Disembarking: 0", bg=self.off_color, fg='white', font=('Arial', 10, 'bold'))
        self.ui_labels['disembarking'].pack(side='left', fill='both', expand=True)

      
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Medium.TCheckbutton", indicatorsize=16, padding=8, font=('Arial', 12, 'bold'), background=self.off_color, foreground='white')
        style.map("Medium.TCheckbutton", background=[('active', self.main_color)])

        # Train Metrics 
        train_metrics_frame = tk.Frame(left_frame, width=480, height=580, bg=self.main_color, highlightbackground="black", highlightthickness=3)
        train_metrics_frame.pack(side='top', padx=2, pady=2)
        train_metrics_frame.pack_propagate(False)
        tk.Label(train_metrics_frame, text="Train Metrics", bg=self.off_color, fg='white', highlightbackground='black', highlightthickness=3, 
                 font=('Arial', 9, 'bold')).pack(padx=3, pady=3)

        # Live Metrics 
        live_metrics = tk.Frame(train_metrics_frame, width=320, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        live_metrics.pack(side='right', padx=2, pady=2, fill='y')
        live_metrics.pack_propagate(False)
        tk.Label(live_metrics, text="Live Metrics", bg=self.off_color, fg='white', font=('Arial', 16, 'bold')).pack(pady=3)

        tk.Label(live_metrics, text="Speed", bg=self.off_color, fg='white', font=('Arial', 20, 'bold')).pack(pady=6)
        self.ui_labels['speed'] = tk.Label(live_metrics, text="0.0 MPH", bg=self.off_color, fg='white', font=('Arial', 18, 'bold'))
        self.ui_labels['speed'].pack(pady=3)

        #Separator line after speed
        thin_line = tk.Frame(live_metrics, bg='black', width=300)
        thin_line.pack()

        tk.Label(live_metrics, text="Acceleration", bg=self.off_color, fg='white', font=('Arial', 20, 'bold')).pack(pady=6)
        self.ui_labels['acceleration'] = tk.Label(live_metrics, text="0.0 MPH²", bg=self.off_color, fg='white', font=('Arial', 18, 'bold'))
        self.ui_labels['acceleration'].pack(pady=3)

        #Separator line after acceleration
        thin_line = tk.Frame(live_metrics, bg='black', width=300)
        thin_line.pack()

        self.ui_labels['passenger_count'] = tk.Label(live_metrics, text="Passenger Count: 0", bg=self.off_color, fg='white', font=('Arial', 14, 'bold'))
        self.ui_labels['passenger_count'].pack(pady=8)
        self.ui_labels['crew_count'] = tk.Label(live_metrics, text="Crew Count: 0", bg=self.off_color, fg='white', font=('Arial', 14, 'bold'))
        self.ui_labels['crew_count'].pack(pady=8)

        #Separator line after crew count
        thin_line = tk.Frame(live_metrics, bg='black', width=300)
        thin_line.pack()

        self.ui_labels['Speed Limit'] = tk.Label(live_metrics, text="Speed Limit: 0", bg=self.off_color, fg='white', font=('Arial', 13, 'bold'))
        self.ui_labels['Speed Limit'].pack(pady=8)

        #Separator line after speed limit
        thin_line = tk.Frame(live_metrics, bg='black', width=300)
        thin_line.pack()

        # Bottom metrics
        bottom_live_metrics = tk.Frame(live_metrics, width=320, bg=self.off_color)
        bottom_live_metrics.pack(side='bottom', fill='x', pady=(0, 15))

        grade_elevation_row = tk.Frame(bottom_live_metrics, bg=self.off_color)
        grade_elevation_row.pack(fill='x', pady=(0, 25))

        self.ui_labels['Grade'] = tk.Label(grade_elevation_row, text="Grade %: 0", bg=self.off_color, fg='white', font=('Arial', 12, 'bold'))
        self.ui_labels['Grade'].pack(side='left', padx=(12, 3), expand=True)

        self.ui_labels['Elevation'] = tk.Label(grade_elevation_row, text="Elevation (ft): 0", bg=self.off_color, fg='white', font=('Arial', 12, 'bold'))
        self.ui_labels['Elevation'].pack(side='right', padx=(3, 12), expand=True)

        #Separator line after grade/elevation
        thin_line_bottom = tk.Frame(bottom_live_metrics, bg='black', width=300)
        thin_line_bottom.pack()

        self.ui_labels['Commanded Authority'] = tk.Label(bottom_live_metrics, text="Commanded Authority (ft): 0", bg=self.off_color, fg='white', font=('Arial', 11, 'bold'))
        self.ui_labels['Commanded Authority'].pack(pady=8)

        self.ui_labels['Commanded Speed'] = tk.Label(bottom_live_metrics, text="Commanded Speed (MPH): 0", bg=self.off_color, fg='white', font=('Arial', 11, 'bold'))
        self.ui_labels['Commanded Speed'].pack(pady=3)

        # Cabin Temp
        cabin_temp_frame = tk.Frame(train_metrics_frame, width=120, height=160, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        cabin_temp_frame.pack(side='top', padx=2, pady=2)
        cabin_temp_frame.pack_propagate(False)
        tk.Label(cabin_temp_frame, text="Cabin Temp", bg=self.off_color, fg='white', font=('Arial', 9, 'bold')).pack(padx=3, pady=(8, 3))

        self.canvas_frame_circle = tk.Canvas(cabin_temp_frame, width=100, height=140, bg=self.off_color, highlightbackground=self.off_color)
        self.canvas_frame_circle.pack(side='top', expand=True)
        self.canvas_frame_circle.create_oval(8, 8, 92, 92, fill=self.off_color, outline='black', width=2)
        self.ui_labels['cabin_temp'] = self.canvas_frame_circle.create_text(50, 50, text="75°F", font=('Arial', 20, 'bold'), fill='white')

        # Train Dimensions
        Train_Dimensions_Frame = tk.Frame(train_metrics_frame, width=120, height=220, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        Train_Dimensions_Frame.pack(side='top', padx=2, pady=2)
        Train_Dimensions_Frame.pack_propagate(False)
        tk.Label(Train_Dimensions_Frame, text="Train Dimensions", bg=self.off_color, fg='white', font=('Arial', 8, 'bold')).pack(padx=3, pady=3)

        self.ui_labels['height'] = tk.Label(Train_Dimensions_Frame, text="Height: 11.0ft", bg=self.off_color, fg='white', font=('Arial', 10))
        self.ui_labels['height'].pack(padx=1, pady=15)
        self.ui_labels['length'] = tk.Label(Train_Dimensions_Frame, text="Length: 150.0ft", bg=self.off_color, fg='white', font=('Arial', 10))
        self.ui_labels['length'].pack(padx=1, pady=15)
        self.ui_labels['width'] = tk.Label(Train_Dimensions_Frame, text="Width: 10.0ft", bg=self.off_color, fg='white', font=('Arial', 10))
        self.ui_labels['width'].pack(padx=1, pady=15)

        # Power Command 
        Train_Power_Command = tk.Frame(train_metrics_frame, width=120, height=180, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        Train_Power_Command.pack(side='top', padx=2, pady=2)
        Train_Power_Command.pack_propagate(False)
        tk.Label(Train_Power_Command, text="Power Command", bg=self.off_color, fg='white', font=('Arial', 9, 'bold')).pack(padx=3, pady=3)
        self.ui_labels['power_command'] = tk.Label(Train_Power_Command, text="0 Watts", bg=self.off_color, fg='white', font=('Arial', 13))
        self.ui_labels['power_command'].pack(padx=1, pady=25)

        # Emergency Brake 
        emergency_brake = tk.Frame(left_frame, width=480, height=80, highlightbackground="black", highlightthickness=2, bg=self.off_color)
        emergency_brake.pack(side='top', padx=2, pady=2)
        emergency_brake.pack_propagate(False)
        emergency_brake_button = tk.Button(emergency_brake, text="EMERGENCY BRAKE", bg="red", fg='white', font=('Arial', 20),
                                           command=self.emergency_brake_activated,
                                           relief='raised', bd=1, padx=10, pady=2, height=40)
        emergency_brake_button.pack(fill='both')

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def updateTime(self):
    #continuously recall itself every second to update the time variable 
        
        local_time = clock.clock.getTime()
        self.ui_labels['time'].config(text=f"{local_time}")
        self.root.after(100, self.updateTime)

    
    def on_closing(self):
        print("Closing application...")
        self.root.destroy()
        os._exit(0)  # This will definitely terminate the process
    
    def run(self):
        """Start the application"""
        # Register observer to update UI when train data changes
        self.current_train.add_observer(self.update_ui_from_train)

        # Initialize the train selector dropdown
        self.root.after(100, self.refresh_train_selector)

        self.root.after(100, self.continuous_physics_update)

        self.root.after(100, self.updateTime)

        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = TrainModelPassengerGUI()
    app.run()