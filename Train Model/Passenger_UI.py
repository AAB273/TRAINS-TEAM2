import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font
from tkinter import ttk
from train_data import get_train_manager
import socket
import threading
import json  # For structured data exchange
import time
# Socket server setup
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
                    current_train.calculate_force_speed_acceleration_()
                else:
                    current_train.set_service_brake(0)
                    current_train.calculate_force_speed_acceleration_()
            elif command == 'set_passenger_count':
                current_train.set_passenger_count(value)
            elif command == 'select_train':
                on_train_selected(value)
            elif command == 'set_temperature':
                target_temp = value
                self._animate_temperature_change(target_temp)
            elif command == 'set_station':
                current_train.set_station(value)
            elif command == 'set_time_to_station':
                current_train.set_time_to_station(value)
            # NEW DEPLOYMENT COMMANDS
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
                # Close the server socket to break out of accept() calls
                self.server_socket.close()
            except:
                pass
        print("Socket server stopped")

    def _animate_temperature_change(self, target_temp):
        """Gradually change temperature using Tkinter's after()"""

        if not current_train:  # Add this safety check
            return
    
        current_temp = current_train.cabin_temp
        target_temp = float(target_temp)
        
        if current_temp < target_temp:
            # Increment by 1 degree
            new_temp = current_temp + 1
            current_train.set_cabin_temp(new_temp)
            update_ui_from_train(current_train)
            
            # Schedule next increment
            root.after(1000, lambda: self._animate_temperature_change(target_temp))
        
        elif current_temp > target_temp:
            # Decrement by 1 degree
            new_temp = current_temp - 1
            current_train.set_cabin_temp(new_temp)
            update_ui_from_train(current_train)
            
            # Schedule next decrement
            root.after(1000, lambda: self._animate_temperature_change(target_temp))
        
        
def start_ui_heartbeat():
    """Periodically check and update UI to ensure it stays in sync"""
    def heartbeat():
        if current_train:
            # Just update the UI regardless of changes
            update_ui_from_train(current_train)
        # Schedule next heartbeat
        root.after(2000, heartbeat)  # Check every 2 seconds
    
    heartbeat()





# Create and start the socket server
socket_server = TrainSocketServer()

main_color = '#1a1a4d'
off_color = '#4d4d6d'

# Get the train manager
train_manager = get_train_manager()
current_train = train_manager.get_selected_train()

root = tk.Tk()
root.title("Passenger Train Model GUI")
root.configure(bg=main_color)
root.geometry("1250x910")

# Store label references for updating
ui_labels = {}
ui_indicators = {}
canvas_frame_circle = None  # Will be set when canvas is created

def emergency_brake_activated():
    current_train.set_emergency_brake(True)
    current_train.set_acceleration(-2.73)
    print(f"EMERGENCY BRAKE ACTIVATED!")

def failure_service_brake_var_changed():
    if failure_brake_var.get():
        current_train.set_service_brake(0)
        current_train.set_emergency_brake(1)
        print(f"Service Brake Failure Activated")
    else:
        print(f"Service Brake Deactivated")
        current_train.set_emergency_brake(0)    



def failure_train_engine_var_changed():
    if failure_train_engine_var.get():
        current_train.set_engine_failure(True)
        current_train.set_power_command(0)
        print(f"Train Engine Failure Activated")
    elif failure_train_engine_var.get():
        current_train.set_engine_failure(False)
        print(f"Train Engine Failure Deactivated")

def failure_signal_pickup_var_changed():
    if failure_signal_pickup_var.get():
        print(f"Signal Pickup Failure Activated")
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
    
    # Update crew count
    ui_labels['crew_count'].config(text=f"Crew Count: {train.crew_count}")

    # Update speed limit
    imperial_speed_limit = train.speed_limit * 0.621371
    ui_labels['Speed Limit'].config(text=f"Speed Limit: {imperial_speed_limit:.1f} MPH")

    # Update Grade
    ui_labels['Grade'].config(text=f"Grade: {train.grade}%")

    # Update Elevation
    ui_labels['Elevation'].config(text=f"Elevation: {train.elevation}ft")
    # Update cabin temp (canvas text item)
    if canvas_frame_circle and 'cabin_temp' in ui_labels:
        canvas_frame_circle.itemconfig(ui_labels['cabin_temp'], text=f"{train.cabin_temp:.0f}°F")
    
    # Update dimensions
    imperial_height = train.height * 3.28084
    imperial_length = train.length * 3.28084
    imperial_width = train.width * 3.28084
    ui_labels['height'].config(text=f"Height: {imperial_height:.1f}ft")
    ui_labels['length'].config(text=f"Length: {imperial_length:.1f}ft")
    ui_labels['width'].config(text=f"Width: {imperial_width:.1f}ft")

    #Update Announcement
    ui_labels['announcement'].config(text=f"Arriving to Station {train.station} in {train.time_to_station}mins")
    
    #Update Time
    local_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    #ui_labels['time'].conifg(text=f"{formatted_time}")

    # Update power command
    ui_labels['power_command'].config(text=f"{train.power_command:.0f} Watts")
    
    # Update door indicators (green=closed, red=open)
    right_door_color = 'green' if train.right_door_open else 'red'
    ui_indicators['cabin_right_led'].itemconfig(ui_indicators['cabin_right_oval'], fill=right_door_color)
    
    left_door_color = 'green' if train.left_door_open else 'red'
    ui_indicators['cabin_left_led'].itemconfig(ui_indicators['cabin_left_oval'], fill=left_door_color)
    
    # Update light indicators (green=on, red=off)
    headlight_color = 'green' if train.headlights_on else 'red'
    ui_indicators['headlights_led'].itemconfig(ui_indicators['headlights_oval'], fill=headlight_color)
    
    interior_color = 'green' if train.interior_lights_on else 'red'
    ui_indicators['interior_led'].itemconfig(ui_indicators['interior_oval'], fill=interior_color)

def on_train_selected(train_id):
    """Handle train selection from selector"""
    global current_train
    train = train_manager.select_train(train_id)
    if train and train.deployed:  # Only select if train is deployed
        current_train = train
        update_ui_from_train(train)
        
        # Update visual selection in train selector
        for btn_id, button in train_buttons.items():
            if btn_id == train_id:
                button.config(bg='#3a3a7d', relief='sunken')
            else:
                button.config(bg=main_color, relief='flat')
    else:
        print(f"Train {train_id} is not deployed or doesn't exist")

def refresh_train_selector():
    """Completely rebuild the train selector UI"""
    global train_buttons
    
    print("Refreshing train selector...")
    
    # Clear existing widgets from selector frame (except title)
    for widget in selector_frame.winfo_children():
        if widget not in [title_label]:  # Only keep the title
            widget.destroy()
    
    # Rebuild headers
    header_train = tk.Label(selector_frame, text="Train #", bg=main_color, fg='white', font=('Arial', 12, 'bold'))
    header_status = tk.Label(selector_frame, text="Line", bg=main_color, fg='white', font=('Arial', 12, 'bold'))
    
    header_train.grid(row=2, column=0, padx=10, pady=(5, 5), sticky='ew')
    header_status.grid(row=2, column=2, padx=10, pady=(5, 5), sticky='ew')
    
    separator = ttk.Separator(selector_frame, orient='vertical')
    separator.grid(row=2, column=1, rowspan=32, padx=10, pady=5, sticky='ns')
    
    first_separator = ttk.Separator(selector_frame, orient='horizontal')
    first_separator.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 5))
    
    # Rebuild the train selector
    train_buttons = {}
    
    # Get all trains and filter only deployed ones
    deployed_trains = []
    for train_id in range(1, 15):
        train = train_manager.get_train(train_id)
        if train and train.deployed:
            deployed_trains.append(train_id)
            print(f"Train {train_id} is deployed: {train.deployed}")
    
    print(f"Found {len(deployed_trains)} deployed trains: {deployed_trains}")
    
    # Recreate UI elements only for deployed trains
    for i, train_id in enumerate(deployed_trains):
        row_num = 4 + (i * 2)
        
        # Make train label clickable
        train_btn = tk.Button(
            selector_frame,
            text=f"Train {train_id}",
            bg=main_color,
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2',
            command=lambda tid=train_id: on_train_selected(tid)
        )
        train_btn.grid(row=row_num, column=0, padx=10, pady=10, sticky='ew')
        train_buttons[train_id] = train_btn
        
        # Status indicator
        status_canvas = tk.Canvas(selector_frame, width=60, height=25, bg=main_color, highlightthickness=2)
        status_canvas.grid(row=row_num, column=2, padx=10, pady=10)
        
        line_color = 'gray'

        train = train_manager.get_train(train_id)
        if train.line == 'blue':
            line_color = 'blue'
        elif train.line == 'red':
            line_color = 'red'
        elif train.line == 'green':
            line_color = 'green'
        status_canvas.create_rectangle(2, 2, 58, 23, fill=line_color, outline='white', width=2)
        
        # Add separator between items (except after the last one)
        if i < len(deployed_trains) - 1:
            row_separator = ttk.Separator(selector_frame, orient='horizontal')
            row_separator.grid(row=row_num+1, column=0, columnspan=3, sticky='ew', pady=5)
    
    # Update the header to show count of deployed trains
    title_label.config(text=f"Train Selector ({len(deployed_trains)} Deployed)")
    
    # Highlight current selection if it's still deployed
    if current_train and hasattr(current_train, 'train_id') and current_train.train_id in deployed_trains:
        if current_train.train_id in train_buttons:
            train_buttons[current_train.train_id].config(bg='#3a3a7d', relief='sunken')
    elif deployed_trains:
        # Select first deployed train if current selection is no longer deployed
        first_train_id = deployed_trains[0]
        if first_train_id in train_buttons:
            train_buttons[first_train_id].config(bg='#3a3a7d', relief='sunken')
            on_train_selected(first_train_id)


            
#Train Selector
selector_frame = tk.Frame(root, bg=main_color, highlightbackground="black", highlightthickness=4, width=200)
selector_frame.pack(side='right', fill='y', padx=3, pady=3)
selector_frame.pack_propagate(False)

selector_frame.columnconfigure(0, weight=1)
selector_frame.columnconfigure(1, weight=0)
selector_frame.columnconfigure(2, weight=1)

title_label = tk.Label(selector_frame, text="Train Selector", bg=main_color, fg='white', font=('Arial', 14, 'bold'))
title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='ew')

# Use the refresh function to build the initial selector
refresh_train_selector()



train_buttons = {}

# Get all trains and filter only deployed ones
deployed_trains = []
for train_id in range(1, 15):
    train = train_manager.get_train(train_id)
    if train.deployed:
        deployed_trains.append(train_id)

# Create UI elements only for deployed trains
for i, train_id in enumerate(deployed_trains):
    row_num = 4 + (i * 2)
    
    # Make train label clickable
    train_btn = tk.Button(
        selector_frame,
        text=f"Train {train_id}",
        bg=main_color,
        fg='white',
        font=('Arial', 10),
        relief='flat',
        cursor='hand2',
        command=lambda tid=train_id: on_train_selected(tid)
    )
    train_btn.grid(row=row_num, column=0, padx=10, pady=10, sticky='ew')
    train_buttons[train_id] = train_btn
    
   
    
    # Add separator between items (except after the last one)
    if i < len(deployed_trains) - 1:
        row_separator = ttk.Separator(selector_frame, orient='horizontal')
        row_separator.grid(row=row_num+1, column=0, columnspan=3, sticky='ew', pady=5)

# Update the header to show count of deployed trains
title_label.config(text=f"Train Selector ({len(deployed_trains)} Deployed)",font=('Arial',12))

# Highlight initial selection if there are deployed trains
if deployed_trains:
    first_train_id = deployed_trains[0]
    train_buttons[first_train_id].config(bg='#3a3a7d', relief='sunken')
    # Optionally select the first deployed train automatically
    on_train_selected(first_train_id)



# Top Container
top_container = tk.Frame(root, bg=main_color, highlightbackground="black", highlightthickness=4)
top_container.pack(fill='x')

#BLT Logo
blt_logo_image = Image.open("Train Model/blt logo.png")
converted_blt_logo_image = blt_logo_image.resize((75,75))
converted_blt_logo_image = ImageTk.PhotoImage(converted_blt_logo_image)
blt_logo_frame = tk.Frame(top_container, bg=main_color, height=80,width=80)
blt_logo_frame.pack(fill='x',side='left',pady=3,padx=3)
blt_logo_frame.pack_propagate(False)
tk.Label(blt_logo_frame, image=converted_blt_logo_image, bg=main_color).pack(padx=1,pady=1)
blt_logo_frame.image = converted_blt_logo_image

time_frame = tk.Frame(top_container, bg=off_color, width=200, height=80, highlightbackground="black", highlightthickness=4)
time_frame.pack(side='left', padx=3, pady=3)
time_frame.pack_propagate(False)
ui_labels['time'] = tk.Label(time_frame, text="Time", bg=off_color, fg='white', font=('Arial',10,'bold')).pack(padx=5, pady=5)

Announcement_frame = tk.Frame(top_container, bg=off_color, width=800, height=80, highlightbackground="black", highlightthickness=4)
Announcement_frame.pack(side='left', padx=3, pady=3)
Announcement_frame.pack_propagate(False)
ui_labels['announcement'] = tk.Label(Announcement_frame, text="Arriving to Dormount in 5 seconds", bg=off_color, fg='white', font=('Arial',20,'bold'))
ui_labels['announcement'].pack(padx=5, pady=5)

left_frame = tk.Frame(root, bg=main_color)
left_frame.pack(side='left',fill='both')

right_frame = tk.Frame(root, bg=main_color)
right_frame.pack(side='right',fill='both',expand=True)

# Advertisement Frame
ad_image = Image.open("Train Model/wendy's_AD.jpg")
converted_ad_image = ImageTk.PhotoImage(ad_image)
Advertisement = tk.Frame(right_frame,height=230,highlightbackground="black",highlightthickness=2,bg=off_color)
Advertisement.pack(side='top',padx=2,pady=2,fill='x')
Advertisement.pack_propagate(False)
tk.Label(Advertisement, image=converted_ad_image).pack(padx=1,pady=1)
Advertisement.image = converted_ad_image

# Doors/Lights Frame
doors_and_lights_frame = tk.Frame(right_frame,height=300,highlightbackground="black",highlightthickness=2,bg=off_color)
doors_and_lights_frame.pack(side='top',padx=3,pady=3,fill='x')
doors_and_lights_frame.pack_propagate(False)

# Cabin Doors
cabin_doors_frame = tk.Frame(doors_and_lights_frame,bg=off_color)
cabin_doors_frame.pack(side='left',padx=5,pady=3,fill='both',expand=True)
cabin_doors_frame.pack_propagate(False)

tk.Label(cabin_doors_frame,text="Right Cabin Door",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
cabin_right_led = tk.Canvas(cabin_doors_frame, width=150, height=50, bg=off_color, highlightthickness=0)
cabin_right_led.pack(pady=5)
cabin_right_oval = cabin_right_led.create_oval(2, 2, 148, 48, fill='red', outline='black', width=1)
ui_indicators['cabin_right_led'] = cabin_right_led
ui_indicators['cabin_right_oval'] = cabin_right_oval

thin_line = tk.Frame(cabin_doors_frame, bg='black',height=2)
thin_line.pack(pady=15,fill='x',padx=20)

tk.Label(cabin_doors_frame,text="Left Cabin Door",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
cabin_left_led = tk.Canvas(cabin_doors_frame, width=150, height=50, bg=off_color, highlightthickness=0)
cabin_left_led.pack(pady=5)
cabin_left_oval = cabin_left_led.create_oval(2, 2, 148, 48, fill='red', outline='black', width=1)
ui_indicators['cabin_left_led'] = cabin_left_led
ui_indicators['cabin_left_oval'] = cabin_left_oval

# Lights
lights_frame = tk.Frame(doors_and_lights_frame,bg=off_color)
lights_frame.pack(side='left',padx=5,pady=3,fill='both',expand=True)
lights_frame.pack_propagate(False)

tk.Label(lights_frame,text="Headlights",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
headlights_led = tk.Canvas(lights_frame, width=150, height=50, bg=off_color, highlightthickness=0)
headlights_led.pack(pady=5)
headlights_oval = headlights_led.create_oval(2, 2, 148, 48, fill='red', outline='black', width=1)
ui_indicators['headlights_led'] = headlights_led
ui_indicators['headlights_oval'] = headlights_oval

thin_line = tk.Frame(lights_frame, bg='black',height=2)
thin_line.pack(pady=15,fill='x',padx=20)

tk.Label(lights_frame,text="Interior Cabin Lights",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
Interior_led = tk.Canvas(lights_frame, width=150, height=50, bg=off_color, highlightthickness=0)
Interior_led.pack(pady=5)
interior_oval = Interior_led.create_oval(2, 2, 148, 48, fill='red', outline='black', width=1)
ui_indicators['interior_led'] = Interior_led
ui_indicators['interior_oval'] = interior_oval

# Murphy Failure Modes
murphy_frame = tk.Frame(right_frame,height=250,highlightbackground="black",highlightthickness=2,bg=off_color)
murphy_frame.pack(side='top',padx=3,pady=3,fill='both')
murphy_frame.pack_propagate(False)
tk.Label(murphy_frame, text="Murphy Failure Modes", bg=off_color, fg='white', width=120, height=1, anchor='n', font=('Arial',20,'bold')).pack(pady=5,padx=5)
thin_line = tk.Frame(murphy_frame, bg='black',width=400)
thin_line.pack(pady=2)

failure_train_engine_var = tk.BooleanVar(value=False)
train_engine_switch = ttk.Checkbutton(murphy_frame, text="Train Engine", variable=failure_train_engine_var, 
                                      command=lambda: failure_train_engine_var_changed(),
                                      style="Large.TCheckbutton")
train_engine_switch.pack(pady=10,padx=5,fill='x',expand=True)
thin_line = tk.Frame(murphy_frame,bg='black',width=400)
thin_line.pack(pady=2)

failure_signal_pickup_var = tk.BooleanVar(value=False)
signal_pickup_switch = ttk.Checkbutton(murphy_frame, text="Signal Pickup", variable=failure_signal_pickup_var,
                                       command=lambda: failure_signal_pickup_var_changed(),
                                       style="Large.TCheckbutton")
signal_pickup_switch.pack(pady=10,padx=5,fill='x',expand=True)
thin_line = tk.Frame(murphy_frame,bg='black',width=400)
thin_line.pack(pady=2)

failure_brake_var = tk.BooleanVar(value=False)
brake_switch = ttk.Checkbutton(murphy_frame, text="Brake", variable=failure_brake_var,
                               command=lambda: failure_service_brake_var_changed(),
                               style="Large.TCheckbutton")
brake_switch.pack(pady=3,padx=5,fill='x',expand=True)

style = ttk.Style()
style.theme_use('clam')
style.configure("Large.TCheckbutton",indicatorsize=20, padding=10,font=('Arial',15,'bold'),background=off_color,foreground='white')
style.map("Large.TCheckbutton",background=[('active', main_color)])

# Train Metrics
train_metrics_frame = tk.Frame(left_frame, width=580, height=700, bg=main_color,highlightbackground="black", highlightthickness=4)
train_metrics_frame.pack(side='top',padx=3, pady=3)
train_metrics_frame.pack_propagate(False)
tk.Label(train_metrics_frame, text="Train Metrics", bg=off_color, fg='white', highlightbackground='black', highlightthickness=4, 
         width=40, height=1, anchor='n', font=('Arial',10,'bold')).pack(padx=5, pady=5)

# Live Metrics
live_metrics = tk.Frame(train_metrics_frame, width=400, highlightbackground="black", highlightthickness=2,bg=off_color)
live_metrics.pack(side='right',padx=3,pady=3,fill='y')
live_metrics.pack_propagate(False)
tk.Label(live_metrics, text="Live Metrics", bg=off_color, fg='white', width=120, height=1, anchor='n', font=('Arial',18,'bold')).pack(pady=5,padx=5)
thin_line = tk.Frame(live_metrics, bg='black')
thin_line.pack(fill='x')

tk.Label(live_metrics,text="Speed",bg=off_color,fg='white',width=120,height=1,font=('Arial',24,'bold')).pack(pady=15,padx=5)
ui_labels['speed'] = tk.Label(live_metrics,text="0.0 MPH",bg=off_color,fg='white',width=120,height=1,font=('Arial',21,'bold'))
ui_labels['speed'].pack(pady=10,padx=5)
thin_line = tk.Frame(live_metrics, bg='black',width=300)
thin_line.pack()

tk.Label(live_metrics,text="Acceleration",bg=off_color,fg='white',width=120,height=1,font=('Arial',24,'bold')).pack(pady=15,padx=5)
ui_labels['acceleration'] = tk.Label(live_metrics,text="0.0 MPH²",bg=off_color,fg='white',width=120,height=1,font=('Arial',21,'bold'))
ui_labels['acceleration'].pack(pady=10,padx=5)
thin_line = tk.Frame(live_metrics, bg='black',width=300)
thin_line.pack()

ui_labels['passenger_count'] = tk.Label(live_metrics,text="Passenger Count: 0",bg=off_color,fg='white',width=120,height=1,font=('Arial',20,'bold'))
ui_labels['passenger_count'].pack(pady=20,padx=5)
ui_labels['crew_count'] = tk.Label(live_metrics,text="Crew Count: 0",bg=off_color,fg='white',width=120,height=1,font=('Arial',20,'bold'))
ui_labels['crew_count'].pack(pady=20,padx=5)

thin_line = tk.Frame(live_metrics, bg='black',width=300)
thin_line.pack()

ui_labels['Speed Limit'] = tk.Label(live_metrics,text="Speed Limit: 0",bg=off_color,fg='white',width=120,height=1,font=('Arial',15,'bold'))
ui_labels['Speed Limit'].pack(pady=20,padx=5)

thin_line = tk.Frame(live_metrics, bg='black',width=300)
thin_line.pack()

bottom_live_metrics = tk.Frame(live_metrics, width=400, bg=off_color)
bottom_live_metrics.pack(side='bottom',fill='x',pady=(0,45))
ui_labels['Grade'] = tk.Label(bottom_live_metrics,text="Grade %: 0",bg=off_color,fg='white',height=1,font=('Arial',15,'bold'))
ui_labels['Grade'].pack(pady=(5,5),padx=(15,5),side='left')
ui_labels['Elevation']  = tk.Label(bottom_live_metrics,text="Elevation: 0",bg=off_color,fg='white',height=1,font=('Arial',15,'bold'))
ui_labels['Elevation'].pack(pady=(5,5),padx=15,side='right')

# Cabin Temp
cabin_temp_frame = tk.Frame(train_metrics_frame, width=140,height=200,highlightbackground="black", highlightthickness=2,bg=off_color)
cabin_temp_frame.pack(side='top',padx=3,pady=3)
cabin_temp_frame.pack_propagate(False)
tk.Label(cabin_temp_frame, text="Cabin Temp", bg=off_color, fg='white', width=120, height=1, font=('Arial',10,'bold')).pack(padx=5, pady=(10, 5), side='top')

canvas_frame_circle = tk.Canvas(cabin_temp_frame, width=120, height=180, bg=off_color, highlightbackground=off_color)
canvas_frame_circle.pack(side='top', expand=True)
canvas_frame_circle.create_oval(10, 10, 110, 110, fill=off_color, outline='black', width=2)
ui_labels['cabin_temp'] = canvas_frame_circle.create_text(60, 60, text="75°F", font=('Arial', 25, 'bold'), fill='white')

# Train Dimensions
Train_Dimensions_Frame = tk.Frame(train_metrics_frame, width=140,height=260,highlightbackground="black", highlightthickness=2,bg=off_color)
Train_Dimensions_Frame.pack(side='top',padx=3,pady=3)
Train_Dimensions_Frame.pack_propagate(False)
tk.Label(Train_Dimensions_Frame, text="Train Dimensions", bg=off_color, fg='white', width=120, height=1, anchor='n', font=('Arial',9,'bold')).pack(padx=5, pady=5)

ui_labels['height'] = tk.Label(Train_Dimensions_Frame, text="Height: 11.0ft", bg=off_color, fg='white', font=('Arial',12))
ui_labels['height'].pack(padx=1,pady=20)
ui_labels['length'] = tk.Label(Train_Dimensions_Frame, text="Length: 150.0ft", bg=off_color, fg='white', font=('Arial',12))
ui_labels['length'].pack(padx=1,pady=20)
ui_labels['width'] = tk.Label(Train_Dimensions_Frame, text="Width: 10.0ft", bg=off_color, fg='white', font=('Arial',12))
ui_labels['width'].pack(padx=1,pady=20)

# Power Command
Train_Power_Command = tk.Frame(train_metrics_frame, width=140,height=225,highlightbackground="black", highlightthickness=2,bg=off_color)
Train_Power_Command.pack(side='top',padx=3,pady=3)
Train_Power_Command.pack_propagate(False)
tk.Label(Train_Power_Command, text="Power Command", bg=off_color, fg='white', width=120, height=1, anchor='n', font=('Arial',10,'bold')).pack(padx=5, pady=5)
ui_labels['power_command'] = tk.Label(Train_Power_Command, text="0 Watts", bg=off_color, fg='white', font=('Arial',15))
ui_labels['power_command'].pack(padx=1,pady=35)

# Emergency Brake
emergency_brake = tk.Frame(left_frame,width=580,height=100, highlightbackground="black",highlightthickness=2,bg=off_color)
emergency_brake.pack(side='top',padx=3,pady=3)
emergency_brake.pack_propagate(False)
emergency_brake_button = tk.Button(emergency_brake, text="EMERGENCY BRAKE", bg="red", fg='white', font=('Arial', 30),
                                   command=emergency_brake_activated,
                                   relief='raised', bd=1, padx=15, pady=3, height=50)
emergency_brake_button.pack(fill='both')

def on_closing():
    """Handle application closing"""
    print("Closing application...")
    socket_server.running = False
    
    # Force close the server socket
    if socket_server.server_socket:
        try:
            socket_server.server_socket.close()
        except:
            pass
    
    # Destroy the root window
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the socket server
socket_server.start_server(update_ui_from_train)

# Register observer to update UI when train data changes
current_train.add_observer(update_ui_from_train)

root.after(100, start_ui_heartbeat)

root.mainloop()