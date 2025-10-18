import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font
from tkinter import ttk
from train_data import get_train_manager
import socket
import threading
import json  # For structured data exchange
import time
#from playsound import playsound
import random

# Socket server setup (unchanged)
class TrainSocketServer:
    def __init__(self, port=12345):
        self.port = port
        self.server_socket = None
        self.running = False
        
    def start_server(self, update_callback):
        """Start the socket server in a separate thread"""
        self.update_callback = update_callback
        self.running = True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(1)
            print(f"Train GUI Server listening on port {self.port}")
            
            # Start accepting connections in background thread
            self.thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.thread.start()
        except Exception as e:
            print(f"Failed to start server: {e}")
            
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"Connection error: {e}")
                    
    def _handle_client(self, client_socket):
        """Handle client messages"""
        while self.running:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                # Parse JSON message
                message = json.loads(data)
                self._process_message(message)
                
            except json.JSONDecodeError:
                print("Invalid JSON received")
            except Exception as e:
                print(f"Client handling error: {e}")
                break
                
        client_socket.close()
        
    def _process_message(self, message):
        """Process incoming messages and update train state"""
        try:
            command = message.get('command')
            value = message.get('value')
            
            if command == 'set_power':
                current_train.set_power_command(value)
                current_train.calculate_force_speed_acceleration_()
            elif command == 'set_right_door':
                if value == 'open':
                    current_train.set_right_door(1)
                elif value == 'close':
                    current_train.set_right_door(0)
            elif command == 'set_left_door':
                if value == 'open':
                    current_train.set_left_door(1)
                elif value == 'close':
                    current_train.set_left_door(0)
            elif command == 'set_headlights':
                if value == 'on':
                    current_train.set_headlights(1)
                else:
                    current_train.set_headlights(0)
            elif command == 'set_interior_lights':
                if value == 'on':
                    current_train.set_interior_lights(1)
                elif value == 'off':
                    current_train.set_interior_lights(0)
            elif command == 'emergency_brake':
                if value == 'on':
                    emergency_brake_activated()
                    current_train.calculate_force_speed_acceleration_()
                else:
                    current_train.set_emergency_brake(0)
                    current_train.calculate_force_speed_acceleration_()
            elif command == 'service_brake':
                if value == 'on':
                    current_train.set_service_brake(1)
                    current_train.set_acceleration(-1.2)
                else:
                    current_train.set_service_brake(0)
                    current_train.calculate_force_speed_acceleration_()
            elif command == 'set_passenger_count':
                current_train.set_passenger_count(value)
                current_train.calculate_force_speed_acceleration_()
            elif command == 'set_speed_limit':
                current_train.set_speed_limit(value)
            elif command == 'set_elevation':
                current_train.set_elevation(value)
            elif command == 'set_grade':
                current_train.set_grade(value)
            elif command == 'select_train':
                on_train_selected(value)
            elif command == 'set_temperature':
                target_temp = value
                self._animate_temperature_change(target_temp)
            elif command == 'set_station':
                current_train.set_station(value)
            elif command == 'set_time_to_station':
                current_train.set_time_to_station(value)
            elif command == 'deploy_train':
                train_id = value
                train = train_manager.get_train(train_id)
                if train:
                    train.deployed = True
                    print(f"Deployed train {train_id}")
                    self._refresh_train_selector()
                    train.calculate_force_speed_acceleration_()
            elif command == 'undeploy_train':
                train_id = value
                train = train_manager.get_train(train_id)
                if train:
                    train.deployed = False
                    print(f"Undeployed train {train_id}")
                    self._refresh_train_selector()
            elif command == 'deploy_all':
                for train_id in range(1, 15):
                    train = train_manager.get_train(train_id)
                    if train:
                        train.deployed = True
                        current_train.calculate_force_speed_acceleration_()
                print("Deployed all trains")
                self._refresh_train_selector()
            elif command == 'undeploy_all':
                for train_id in range(1, 15):
                    train = train_manager.get_train(train_id)
                    if train:
                        train.deployed = False
                print("Undeployed all trains")
                self._refresh_train_selector()
            elif command == 'refresh_trains':
                self._refresh_train_selector()
            
            # Force UI update
            update_ui_from_train(current_train)
            
        except Exception as e:
            print(f"Error processing message: {e}")

    def _refresh_train_selector(self):
        """Refresh the train selector UI to show/hide trains based on deployment status"""
        print("Socket server requesting train selector refresh")
        root.after(0, refresh_train_selector)

    def stop_server(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("Socket server stopped")

    def _animate_temperature_change(self, target_temp):
        """Gradually change temperature using Tkinter's after()"""
        if not current_train:
            return
    
        current_temp = current_train.cabin_temp
        target_temp = float(target_temp)
        
        if current_temp < target_temp:
            new_temp = current_temp + 1
            current_train.set_cabin_temp(new_temp)
            update_ui_from_train(current_train)
            root.after(1000, lambda: self._animate_temperature_change(target_temp))
        elif current_temp > target_temp:
            new_temp = current_temp - 1
            current_train.set_cabin_temp(new_temp)
            update_ui_from_train(current_train)
            root.after(1000, lambda: self._animate_temperature_change(target_temp))
            
        print(f"Real Cabin Temp: {current_train.cabin_temp} Sent!")

def continuous_physics_update():
    """Continuously update train physics for real-time speed changes"""
    if current_train and current_train.deployed:
        current_train.update_physics_continuously()
        update_ui_from_train(current_train)
    root.after(100, continuous_physics_update)

def continuous_state_update():
    """Continuously update train state machine"""
    if current_train and current_train.deployed:
        current_train.update_state()
    root.after(500, continuous_state_update)

# Create and start the socket server
socket_server = TrainSocketServer()

main_color = '#1a1a4d'
off_color = '#4d4d6d'

# Get the train manager
train_manager = get_train_manager()
current_train = train_manager.get_selected_train()

# SCALED DOWN WINDOW SIZE
root = tk.Tk()
root.title("Passenger Train Model GUI")
root.configure(bg=main_color)
root.geometry("900x800")  # Reduced from 1050x970

ui_labels = {}
ui_indicators = {}
canvas_frame_circle = None  

def emergency_brake_activated():
    current_train.set_emergency_brake(True)
    current_train.set_acceleration(-2.73)
    print(f"EMERGENCY BRAKE ACTIVATED!")

def failure_service_brake_var_changed():
    if failure_brake_var.get():
        current_train.set_service_brake(0)
        emergency_brake_activated()
        print(f"Service Brake Failure Activated")
    elif failure_brake_var.get() == 0:
        print(f"Service Brake Deactivated")
        current_train.set_emergency_brake(0)

def failure_train_engine_var_changed():
    if failure_train_engine_var.get():
        current_train.set_engine_failure(True)
        current_train.set_power_command(0)
        current_train.set_acceleration(0)
        print(f"Train Engine Failure Activated")
    elif failure_train_engine_var.get() == 0:
        current_train.set_engine_failure(False)
        print(f"Train Engine Failure Deactivated")

def failure_signal_pickup_var_changed():
    if failure_signal_pickup_var.get():
        print(f"Signal Pickup Failure Activated")
        ui_labels['Speed Limit'].config(text=f"Speed Limit: ??? MPH")
        ui_labels['Grade'].config(text=f"Grade: ???")
        ui_labels['Elevation'].config(text=f"Elevation: ???")
    else:
        print(f"Signal Pickup Failure Deactivated")

def update_ui_from_train(train):
    """Update all UI elements when train data changes"""
    # Update speed
    imperial_speed = train.speed * 2.23964
    ui_labels['speed'].config(text=f"{imperial_speed:.1f} MPH")
    
    # Update acceleration
    imperial_acceleration = train.acceleration * 2.23694
    ui_labels['acceleration'].config(text=f"{imperial_acceleration:.1f} MPH²")
    
    # Update passenger count
    ui_labels['passenger_count'].config(text=f"Passenger Count: {train.passenger_count}")
    ui_labels['disembarking'].config(text=f"Passengers Disembarking: {train.passengers_disembarking}")
    ui_labels['crew_count'].config(text=f"Crew Count: {train.crew_count}")

    # Update speed limit
    imperial_speed_limit = train.speed_limit * 0.621371
    ui_labels['Speed Limit'].config(text=f"Speed Limit: {imperial_speed_limit:.1f} MPH")

    # Update Grade and Elevation
    ui_labels['Grade'].config(text=f"Grade: {train.grade}%")
    ui_labels['Elevation'].config(text=f"Elevation: {train.elevation}ft")
    
    # Update cabin temp
    if canvas_frame_circle and 'cabin_temp' in ui_labels:
        canvas_frame_circle.itemconfig(ui_labels['cabin_temp'], text=f"{train.cabin_temp:.0f}°F")
    
    # Update dimensions
    imperial_height = train.height * 3.28084
    imperial_length = train.length * 3.28084
    imperial_width = train.width * 3.28084
    ui_labels['height'].config(text=f"Height: {imperial_height:.1f}ft")
    ui_labels['length'].config(text=f"Length: {imperial_length:.1f}ft")
    ui_labels['width'].config(text=f"Width: {imperial_width:.1f}ft")

    # Update Announcement and Time
    ui_labels['announcement'].config(text=f"Arriving to Station {train.station} in {train.time_to_station}mins")
    local_time = time.localtime()
    formatted_time = time.strftime("%H:%M:%S\n%p", local_time)
    ui_labels['time'].config(text=f"{formatted_time}")

    # Update power command and commanded values
    ui_labels['power_command'].config(text=f"{train.power_command:.0f} Watts")
    ui_labels['Commanded Authority'].config(text=f"{train.commanded_authority:.0f} ft")
    ui_labels['Commanded Speed'].config(text=f"{train.commanded_speed:.0f} MPH")
    
    # Update door and light indicators
    right_door_color = 'green' if train.right_door_open else 'red'
    ui_indicators['cabin_right_led'].itemconfig(ui_indicators['cabin_right_oval'], fill=right_door_color)
    
    left_door_color = 'green' if train.left_door_open else 'red'
    ui_indicators['cabin_left_led'].itemconfig(ui_indicators['cabin_left_oval'], fill=left_door_color)
    
    headlight_color = 'green' if train.headlights_on else 'red'
    ui_indicators['headlights_led'].itemconfig(ui_indicators['headlights_oval'], fill=headlight_color)
    
    interior_color = 'green' if train.interior_lights_on else 'red'
    ui_indicators['interior_led'].itemconfig(ui_indicators['interior_oval'], fill=interior_color)

def on_train_selected(train_id):
    """Handle train selection from dropdown"""
    global current_train
    train = train_manager.select_train(train_id)
    if train and train.deployed:
        current_train = train
        update_ui_from_train(train)
        train_selector_var.set(f"Train {train_id}")
    else:
        print(f"Train {train_id} is not deployed or doesn't exist")

def refresh_train_selector():
    """Update the dropdown menu with currently deployed trains"""
    print("Refreshing train selector dropdown...")
    
    current_selection = train_selector_var.get()
    train_selector['menu'].delete(0, 'end')
    
    deployed_trains = []
    for train_id in range(1, 15):
        train = train_manager.get_train(train_id)
        if train and train.deployed:
            deployed_trains.append(train_id)
    
    print(f"Found {len(deployed_trains)} deployed trains: {deployed_trains}")
    
    for train_id in deployed_trains:
        train_selector['menu'].add_command(
            label=f"Train {train_id}", 
            command=lambda tid=train_id: on_train_selected(tid)
        )
    
    train_selector_label.config(text=f"Select Train ({len(deployed_trains)} Deployed)")
    
    if current_train and hasattr(current_train, 'train_id') and current_train.train_id in deployed_trains:
        train_selector_var.set(f"Train {current_train.train_id}")
    elif deployed_trains:
        first_train_id = deployed_trains[0]
        train_selector_var.set(f"Train {first_train_id}")
        on_train_selected(first_train_id)
    else:
        train_selector_var.set("No Trains Deployed")

# Train Selector Dropdown Frame - FIXED WIDTH
train_selector_container = tk.Frame(root, bg=main_color, height=30)
train_selector_container.pack(fill='x', padx=8, pady=3)
train_selector_container.pack_propagate(False)

train_selector_label = tk.Label(train_selector_container, text="Select Train", bg=main_color, fg='white', font=('Arial', 10, 'bold'))
train_selector_label.pack(side='left', padx=(8, 3))

# FIXED: Made dropdown wider to fit "No Trains Deployed" text
train_selector_var = tk.StringVar()
train_selector = tk.OptionMenu(train_selector_container, train_selector_var, "Loading...")
train_selector.config(bg=main_color, fg='white', font=('Arial', 9), width=20)  # Increased width from 12 to 20
train_selector.pack(side='left', padx=(0, 8))
train_selector['menu'].config(bg=main_color, fg='white')

# Top Container
top_container = tk.Frame(root, bg=main_color, highlightbackground="black", highlightthickness=3)
top_container.pack(fill='x', padx=8, pady=3)

# BLT Logo - Smaller
blt_logo_image = Image.open("Train Model/blt logo.png")
converted_blt_logo_image = blt_logo_image.resize((60, 60))
converted_blt_logo_image = ImageTk.PhotoImage(converted_blt_logo_image)
blt_logo_frame = tk.Frame(top_container, bg=main_color, height=65, width=65)
blt_logo_frame.pack(fill='x', side='left', pady=2, padx=2)
blt_logo_frame.pack_propagate(False)
tk.Label(blt_logo_frame, image=converted_blt_logo_image, bg=main_color).pack(padx=1, pady=1)
blt_logo_frame.image = converted_blt_logo_image

# Time Frame - Smaller
time_frame = tk.Frame(top_container, bg=off_color, width=150, height=65, highlightbackground="black", highlightthickness=3)
time_frame.pack(side='left', padx=2, pady=2)
time_frame.pack_propagate(False)
ui_labels['time'] = tk.Label(time_frame, text="Time", bg=off_color, fg='white', font=('Arial', 16, 'bold'))
ui_labels['time'].pack(padx=3, pady=3)

# Announcement Frame - Smaller
Announcement_frame = tk.Frame(top_container, bg=off_color, width=600, height=65, highlightbackground="black", highlightthickness=3)
Announcement_frame.pack(side='left', padx=2, pady=2)
Announcement_frame.pack_propagate(False)
ui_labels['announcement'] = tk.Label(Announcement_frame, text="Arriving to Dormount in 5 seconds", bg=off_color, fg='white', font=('Arial', 16, 'bold'))
ui_labels['announcement'].pack(padx=3, pady=3)

# Main frames
left_frame = tk.Frame(root, bg=main_color)
left_frame.pack(side='left', fill='both', padx=8, pady=3)

right_frame = tk.Frame(root, bg=main_color)
right_frame.pack(side='right', fill='both', expand=True, padx=8, pady=3)

# Advertisement Frame - Smaller
ad_image = Image.open("Train Model/wendy's_AD.jpg")
converted_ad_image = ad_image.resize((400, 180))
converted_ad_image = ImageTk.PhotoImage(converted_ad_image)
Advertisement = tk.Frame(right_frame, height=190, highlightbackground="black", highlightthickness=2, bg=off_color)
Advertisement.pack(side='top', padx=2, pady=2, fill='x')
Advertisement.pack_propagate(False)
tk.Label(Advertisement, image=converted_ad_image).pack(padx=1, pady=1)
Advertisement.image = converted_ad_image

# Doors/Lights Frame - Compact
doors_and_lights_frame = tk.Frame(right_frame, height=200, highlightbackground="black", highlightthickness=2, bg=off_color)
doors_and_lights_frame.pack(side='top', padx=2, pady=2, fill='x')
doors_and_lights_frame.pack_propagate(False)

# Cabin Doors - Compact
cabin_doors_frame = tk.Frame(doors_and_lights_frame, bg=off_color)
cabin_doors_frame.pack(side='left', padx=3, pady=2, fill='both', expand=True)

tk.Label(cabin_doors_frame, text="Right Door", bg=off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
cabin_right_led = tk.Canvas(cabin_doors_frame, width=120, height=40, bg=off_color, highlightthickness=0)
cabin_right_led.pack(pady=3)
cabin_right_oval = cabin_right_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
ui_indicators['cabin_right_led'] = cabin_right_led
ui_indicators['cabin_right_oval'] = cabin_right_oval

thin_line = tk.Frame(cabin_doors_frame, bg='black', height=1)
thin_line.pack(pady=8, fill='x', padx=15)

tk.Label(cabin_doors_frame, text="Left Door", bg=off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
cabin_left_led = tk.Canvas(cabin_doors_frame, width=120, height=40, bg=off_color, highlightthickness=0)
cabin_left_led.pack(pady=3)
cabin_left_oval = cabin_left_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
ui_indicators['cabin_left_led'] = cabin_left_led
ui_indicators['cabin_left_oval'] = cabin_left_oval

# Lights - Compact
lights_frame = tk.Frame(doors_and_lights_frame, bg=off_color)
lights_frame.pack(side='left', padx=3, pady=2, fill='both', expand=True)

tk.Label(lights_frame, text="Headlights", bg=off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
headlights_led = tk.Canvas(lights_frame, width=120, height=40, bg=off_color, highlightthickness=0)
headlights_led.pack(pady=3)
headlights_oval = headlights_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
ui_indicators['headlights_led'] = headlights_led
ui_indicators['headlights_oval'] = headlights_oval

thin_line = tk.Frame(lights_frame, bg='black', height=1)
thin_line.pack(pady=8, fill='x', padx=15)

tk.Label(lights_frame, text="Interior Lights", bg=off_color, fg='white', font=('Arial', 9, 'bold')).pack(pady=5)
Interior_led = tk.Canvas(lights_frame, width=120, height=40, bg=off_color, highlightthickness=0)
Interior_led.pack(pady=3)
interior_oval = Interior_led.create_oval(2, 2, 118, 38, fill='red', outline='black', width=1)
ui_indicators['interior_led'] = Interior_led
ui_indicators['interior_oval'] = interior_oval

# Murphy Failure Modes - Compact
murphy_frame = tk.Frame(right_frame, height=200, highlightbackground="black", highlightthickness=2, bg=off_color)
murphy_frame.pack(side='top', padx=2, pady=2, fill='both')
murphy_frame.pack_propagate(False)
tk.Label(murphy_frame, text="Murphy Failure Modes", bg=off_color, fg='white', font=('Arial', 16, 'bold')).pack(pady=3)

# RESTORED: Separator lines in Murphy frame
thin_line = tk.Frame(murphy_frame, bg='black', width=400)
thin_line.pack(pady=2)

failure_train_engine_var = tk.BooleanVar(value=False)
train_engine_switch = ttk.Checkbutton(murphy_frame, text="Train Engine", variable=failure_train_engine_var, 
                                      command=lambda: failure_train_engine_var_changed(),
                                      style="Medium.TCheckbutton")
train_engine_switch.pack(pady=6, padx=3, fill='x', expand=True)

# RESTORED: Separator line
thin_line = tk.Frame(murphy_frame, bg='black', width=400)
thin_line.pack(pady=2)

failure_signal_pickup_var = tk.BooleanVar(value=False)
signal_pickup_switch = ttk.Checkbutton(murphy_frame, text="Signal Pickup", variable=failure_signal_pickup_var,
                                       command=lambda: failure_signal_pickup_var_changed(),
                                       style="Medium.TCheckbutton")
signal_pickup_switch.pack(pady=6, padx=3, fill='x', expand=True)

# RESTORED: Separator line
thin_line = tk.Frame(murphy_frame, bg='black', width=400)
thin_line.pack(pady=2)

failure_brake_var = tk.BooleanVar(value=False)
brake_switch = ttk.Checkbutton(murphy_frame, text="Brake", variable=failure_brake_var,
                               command=lambda: failure_service_brake_var_changed(),
                               style="Medium.TCheckbutton")
brake_switch.pack(pady=6, padx=3, fill='x', expand=True)

# Passenger Disembarking - Compact
pass_disembarking_frame = tk.Frame(right_frame, highlightbackground="black", highlightthickness=2, bg=off_color, height=50)
pass_disembarking_frame.pack(side='top', padx=1, pady=1, fill='both')

disembarking_content = tk.Frame(pass_disembarking_frame, bg=off_color)
disembarking_content.pack(expand=True, fill='both', padx=3, pady=3)

generate_button = tk.Button(disembarking_content, text="Generate", bg=main_color, fg='white', font=('Arial', 9, 'bold'), relief='raised', bd=2, width=6, height=1,
                            command=lambda: [current_train.set_disembarking(random.randint(0,current_train.passenger_count)),
                                             current_train.set_passenger_count(current_train.passenger_count - current_train.passengers_disembarking)])
generate_button.pack(side='left', padx=(0, 8))

ui_labels['disembarking'] = tk.Label(disembarking_content, text="Passengers Disembarking: 0", bg=off_color, fg='white', font=('Arial', 10, 'bold'))
ui_labels['disembarking'].pack(side='left', fill='both', expand=True)

# Style for smaller checkbuttons
style = ttk.Style()
style.theme_use('clam')
style.configure("Medium.TCheckbutton", indicatorsize=16, padding=8, font=('Arial', 12, 'bold'), background=off_color, foreground='white')
style.map("Medium.TCheckbutton", background=[('active', main_color)])

# Train Metrics - Compact
train_metrics_frame = tk.Frame(left_frame, width=480, height=580, bg=main_color, highlightbackground="black", highlightthickness=3)
train_metrics_frame.pack(side='top', padx=2, pady=2)
train_metrics_frame.pack_propagate(False)
tk.Label(train_metrics_frame, text="Train Metrics", bg=off_color, fg='white', highlightbackground='black', highlightthickness=3, 
         font=('Arial', 9, 'bold')).pack(padx=3, pady=3)

# Live Metrics - Compact
live_metrics = tk.Frame(train_metrics_frame, width=320, highlightbackground="black", highlightthickness=2, bg=off_color)
live_metrics.pack(side='right', padx=2, pady=2, fill='y')
live_metrics.pack_propagate(False)
tk.Label(live_metrics, text="Live Metrics", bg=off_color, fg='white', font=('Arial', 16, 'bold')).pack(pady=3)

tk.Label(live_metrics, text="Speed", bg=off_color, fg='white', font=('Arial', 20, 'bold')).pack(pady=6)
ui_labels['speed'] = tk.Label(live_metrics, text="0.0 MPH", bg=off_color, fg='white', font=('Arial', 18, 'bold'))
ui_labels['speed'].pack(pady=3)

# RESTORED: Separator line after speed
thin_line = tk.Frame(live_metrics, bg='black', width=300)
thin_line.pack()

tk.Label(live_metrics, text="Acceleration", bg=off_color, fg='white', font=('Arial', 20, 'bold')).pack(pady=6)
ui_labels['acceleration'] = tk.Label(live_metrics, text="0.0 MPH²", bg=off_color, fg='white', font=('Arial', 18, 'bold'))
ui_labels['acceleration'].pack(pady=3)

# RESTORED: Separator line after acceleration
thin_line = tk.Frame(live_metrics, bg='black', width=300)
thin_line.pack()

ui_labels['passenger_count'] = tk.Label(live_metrics, text="Passenger Count: 0", bg=off_color, fg='white', font=('Arial', 14, 'bold'))
ui_labels['passenger_count'].pack(pady=8)
ui_labels['crew_count'] = tk.Label(live_metrics, text="Crew Count: 0", bg=off_color, fg='white', font=('Arial', 14, 'bold'))
ui_labels['crew_count'].pack(pady=8)

# RESTORED: Separator line after crew count
thin_line = tk.Frame(live_metrics, bg='black', width=300)
thin_line.pack()

ui_labels['Speed Limit'] = tk.Label(live_metrics, text="Speed Limit: 0", bg=off_color, fg='white', font=('Arial', 13, 'bold'))
ui_labels['Speed Limit'].pack(pady=8)

# RESTORED: Separator line after speed limit
thin_line = tk.Frame(live_metrics, bg='black', width=300)
thin_line.pack()

# Bottom metrics - Compact
bottom_live_metrics = tk.Frame(live_metrics, width=320, bg=off_color)
bottom_live_metrics.pack(side='bottom', fill='x', pady=(0, 15))

grade_elevation_row = tk.Frame(bottom_live_metrics, bg=off_color)
grade_elevation_row.pack(fill='x', pady=(0, 25))

ui_labels['Grade'] = tk.Label(grade_elevation_row, text="Grade %: 0", bg=off_color, fg='white', font=('Arial', 12, 'bold'))
ui_labels['Grade'].pack(side='left', padx=(12, 3), expand=True)

ui_labels['Elevation'] = tk.Label(grade_elevation_row, text="Elevation (ft): 0", bg=off_color, fg='white', font=('Arial', 12, 'bold'))
ui_labels['Elevation'].pack(side='right', padx=(3, 12), expand=True)

# RESTORED: Separator line after grade/elevation
thin_line_bottom = tk.Frame(bottom_live_metrics, bg='black', width=300)
thin_line_bottom.pack()

ui_labels['Commanded Authority'] = tk.Label(bottom_live_metrics, text="Commanded Authority (ft): 0", bg=off_color, fg='white', font=('Arial', 11, 'bold'))
ui_labels['Commanded Authority'].pack(pady=8)

ui_labels['Commanded Speed'] = tk.Label(bottom_live_metrics, text="Commanded Speed (MPH): 0", bg=off_color, fg='white', font=('Arial', 11, 'bold'))
ui_labels['Commanded Speed'].pack(pady=3)

# Cabin Temp - Smaller
cabin_temp_frame = tk.Frame(train_metrics_frame, width=120, height=160, highlightbackground="black", highlightthickness=2, bg=off_color)
cabin_temp_frame.pack(side='top', padx=2, pady=2)
cabin_temp_frame.pack_propagate(False)
tk.Label(cabin_temp_frame, text="Cabin Temp", bg=off_color, fg='white', font=('Arial', 9, 'bold')).pack(padx=3, pady=(8, 3))

canvas_frame_circle = tk.Canvas(cabin_temp_frame, width=100, height=140, bg=off_color, highlightbackground=off_color)
canvas_frame_circle.pack(side='top', expand=True)
canvas_frame_circle.create_oval(8, 8, 92, 92, fill=off_color, outline='black', width=2)
ui_labels['cabin_temp'] = canvas_frame_circle.create_text(50, 50, text="75°F", font=('Arial', 20, 'bold'), fill='white')

# Train Dimensions - Smaller
Train_Dimensions_Frame = tk.Frame(train_metrics_frame, width=120, height=220, highlightbackground="black", highlightthickness=2, bg=off_color)
Train_Dimensions_Frame.pack(side='top', padx=2, pady=2)
Train_Dimensions_Frame.pack_propagate(False)
tk.Label(Train_Dimensions_Frame, text="Train Dimensions", bg=off_color, fg='white', font=('Arial', 8, 'bold')).pack(padx=3, pady=3)

ui_labels['height'] = tk.Label(Train_Dimensions_Frame, text="Height: 11.0ft", bg=off_color, fg='white', font=('Arial', 10))
ui_labels['height'].pack(padx=1, pady=15)
ui_labels['length'] = tk.Label(Train_Dimensions_Frame, text="Length: 150.0ft", bg=off_color, fg='white', font=('Arial', 10))
ui_labels['length'].pack(padx=1, pady=15)
ui_labels['width'] = tk.Label(Train_Dimensions_Frame, text="Width: 10.0ft", bg=off_color, fg='white', font=('Arial', 10))
ui_labels['width'].pack(padx=1, pady=15)

# Power Command - Smaller
Train_Power_Command = tk.Frame(train_metrics_frame, width=120, height=180, highlightbackground="black", highlightthickness=2, bg=off_color)
Train_Power_Command.pack(side='top', padx=2, pady=2)
Train_Power_Command.pack_propagate(False)
tk.Label(Train_Power_Command, text="Power Command", bg=off_color, fg='white', font=('Arial', 9, 'bold')).pack(padx=3, pady=3)
ui_labels['power_command'] = tk.Label(Train_Power_Command, text="0 Watts", bg=off_color, fg='white', font=('Arial', 13))
ui_labels['power_command'].pack(padx=1, pady=25)

# Emergency Brake - Smaller
emergency_brake = tk.Frame(left_frame, width=480, height=80, highlightbackground="black", highlightthickness=2, bg=off_color)
emergency_brake.pack(side='top', padx=2, pady=2)
emergency_brake.pack_propagate(False)
emergency_brake_button = tk.Button(emergency_brake, text="EMERGENCY BRAKE", bg="red", fg='white', font=('Arial', 20),
                                   command=emergency_brake_activated,
                                   relief='raised', bd=1, padx=10, pady=2, height=40)
emergency_brake_button.pack(fill='both')

def on_closing():
    """Handle application closing"""
    print("Closing application...")
    socket_server.running = False
    if socket_server.server_socket:
        try:
            socket_server.server_socket.close()
        except:
            pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

#

# Start the socket server
socket_server.start_server(update_ui_from_train)

# Register observer to update UI when train data changes
current_train.add_observer(update_ui_from_train)

# Initialize the train selector dropdown
root.after(100, refresh_train_selector)

root.after(100, continuous_physics_update)
root.after(500, continuous_state_update)

root.mainloop()