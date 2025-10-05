import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import font
from tkinter import ttk
from train_data import get_train_manager

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

def update_ui_from_train(train):
    """Update all UI elements when train data changes"""
    # Update speed
    ui_labels['speed'].config(text=f"{train.speed:.1f} MPH")
    
    # Update acceleration
    ui_labels['acceleration'].config(text=f"{train.acceleration:.1f} MPH²")
    
    # Update passenger count
    ui_labels['passenger_count'].config(text=f"Passenger Count: {train.passenger_count}")
    
    # Update crew count
    ui_labels['crew_count'].config(text=f"Crew Count: {train.crew_count}")
    
    # Update cabin temp (canvas text item)
    if canvas_frame_circle and 'cabin_temp' in ui_labels:
        canvas_frame_circle.itemconfig(ui_labels['cabin_temp'], text=f"{train.cabin_temp:.0f}°F")
    
    # Update dimensions
    ui_labels['height'].config(text=f"Height: {train.height:.1f}ft")
    ui_labels['length'].config(text=f"Length: {train.length:.1f}ft")
    ui_labels['width'].config(text=f"Width: {train.width:.1f}ft")
    
    # Update power command
    ui_labels['power_command'].config(text=f"{train.power_command:.0f} Watts")
    
    # Update door indicators (green=closed, red=open)
    right_door_color = 'red' if train.right_door_open else 'green'
    ui_indicators['cabin_right_led'].itemconfig(ui_indicators['cabin_right_oval'], fill=right_door_color)
    
    left_door_color = 'red' if train.left_door_open else 'green'
    ui_indicators['cabin_left_led'].itemconfig(ui_indicators['cabin_left_oval'], fill=left_door_color)
    
    # Update light indicators (yellow=on, gray=off)
    headlight_color = 'yellow' if train.headlights_on else 'gray'
    ui_indicators['headlights_led'].itemconfig(ui_indicators['headlights_oval'], fill=headlight_color)
    
    interior_color = 'yellow' if train.interior_lights_on else 'gray'
    ui_indicators['interior_led'].itemconfig(ui_indicators['interior_oval'], fill=interior_color)

def on_train_selected(train_id):
    """Handle train selection from selector"""
    global current_train
    train = train_manager.select_train(train_id)
    if train:
        current_train = train
        update_ui_from_train(train)
        
        # Update visual selection in train selector
        for i in range(14):
            if i+1 == train_id:
                train_buttons[i+1].config(bg='#3a3a7d', relief='sunken')
            else:
                train_buttons[i+1].config(bg=main_color, relief='flat')

# Register observer to update UI when train data changes
current_train.add_observer(update_ui_from_train)

#Train Selector
selector_frame = tk.Frame(root, bg=main_color, highlightbackground="black", highlightthickness=4, width=200)
selector_frame.pack(side='right', fill='y', padx=3, pady=3)
selector_frame.pack_propagate(False)

selector_frame.columnconfigure(0, weight=1)
selector_frame.columnconfigure(1, weight=0)
selector_frame.columnconfigure(2, weight=1)

title_label = tk.Label(selector_frame, text="Train Selector", bg=main_color, fg='white', font=('Arial', 14, 'bold'))
title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='ew')

title_separator = ttk.Separator(selector_frame, orient='horizontal')
title_separator.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 10))

header_train = tk.Label(selector_frame, text="Train #", bg=main_color, fg='white', font=('Arial', 12, 'bold'))
header_status = tk.Label(selector_frame, text="Deployed?", bg=main_color, fg='white', font=('Arial', 12, 'bold'))

header_train.grid(row=2, column=0, padx=10, pady=(5, 5), sticky='ew')
header_status.grid(row=2, column=2, padx=10, pady=(5, 5), sticky='ew')

separator = ttk.Separator(selector_frame, orient='vertical')
separator.grid(row=2, column=1, rowspan=32, padx=10, pady=5, sticky='ns')

first_separator = ttk.Separator(selector_frame, orient='horizontal')
first_separator.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 5))

train_buttons = {}

for i in range(14):
    row_num = 4 + (i * 2)
    train_id = i + 1
    
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
    status_canvas = tk.Canvas(selector_frame, width=60, height=25, bg=main_color, highlightthickness=0)
    status_canvas.grid(row=row_num, column=2, padx=10, pady=10)
    
    train = train_manager.get_train(train_id)
    fill_color = 'green' if train.deployed else 'red'
    status_canvas.create_rectangle(2, 2, 58, 23, fill=fill_color, outline='white', width=2)
    
    if i < 14:
        row_separator = ttk.Separator(selector_frame, orient='horizontal')
        row_separator.grid(row=row_num+1, column=0, columnspan=3, sticky='ew', pady=5)

# Highlight initial selection
train_buttons[1].config(bg='#3a3a7d', relief='sunken')

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
tk.Label(time_frame, text="Time", bg=off_color, fg='white', font=('Arial',10,'bold')).pack(padx=5, pady=5)

Announcement_frame = tk.Frame(top_container, bg=off_color, width=800, height=80, highlightbackground="black", highlightthickness=4)
Announcement_frame.pack(side='left', padx=3, pady=3)
Announcement_frame.pack_propagate(False)
tk.Label(Announcement_frame, text="Arriving to Dormount in 5 seconds", bg=off_color, fg='white', font=('Arial',10,'bold')).pack(padx=5, pady=5)

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
cabin_right_oval = cabin_right_led.create_oval(2, 2, 148, 48, fill='green', outline='black', width=1)
ui_indicators['cabin_right_led'] = cabin_right_led
ui_indicators['cabin_right_oval'] = cabin_right_oval

thin_line = tk.Frame(cabin_doors_frame, bg='black',height=2)
thin_line.pack(pady=15,fill='x',padx=20)

tk.Label(cabin_doors_frame,text="Left Cabin Door",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
cabin_left_led = tk.Canvas(cabin_doors_frame, width=150, height=50, bg=off_color, highlightthickness=0)
cabin_left_led.pack(pady=5)
cabin_left_oval = cabin_left_led.create_oval(2, 2, 148, 48, fill='green', outline='black', width=1)
ui_indicators['cabin_left_led'] = cabin_left_led
ui_indicators['cabin_left_oval'] = cabin_left_oval

# Lights
lights_frame = tk.Frame(doors_and_lights_frame,bg=off_color)
lights_frame.pack(side='left',padx=5,pady=3,fill='both',expand=True)
lights_frame.pack_propagate(False)

tk.Label(lights_frame,text="Headlights",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
headlights_led = tk.Canvas(lights_frame, width=150, height=50, bg=off_color, highlightthickness=0)
headlights_led.pack(pady=5)
headlights_oval = headlights_led.create_oval(2, 2, 148, 48, fill='green', outline='black', width=1)
ui_indicators['headlights_led'] = headlights_led
ui_indicators['headlights_oval'] = headlights_oval

thin_line = tk.Frame(lights_frame, bg='black',height=2)
thin_line.pack(pady=15,fill='x',padx=20)

tk.Label(lights_frame,text="Interior Cabin Lights",bg=off_color,fg='white',font=('Arial',10,'bold')).pack(pady=10,padx=5)
Interior_led = tk.Canvas(lights_frame, width=150, height=50, bg=off_color, highlightthickness=0)
Interior_led.pack(pady=5)
interior_oval = Interior_led.create_oval(2, 2, 148, 48, fill='green', outline='black', width=1)
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
                                      command=lambda: current_train.set_engine_failure(failure_train_engine_var.get()),
                                      style="Large.TCheckbutton")
train_engine_switch.pack(pady=10,padx=5,fill='x',expand=True)
thin_line = tk.Frame(murphy_frame,bg='black',width=400)
thin_line.pack(pady=2)

failure_signal_pickup_var = tk.BooleanVar(value=False)
signal_pickup_switch = ttk.Checkbutton(murphy_frame, text="Signal Pickup", variable=failure_signal_pickup_var,
                                       command=lambda: current_train.set_signal_pickup_failure(failure_signal_pickup_var.get()),
                                       style="Large.TCheckbutton")
signal_pickup_switch.pack(pady=10,padx=5,fill='x',expand=True)
thin_line = tk.Frame(murphy_frame,bg='black',width=400)
thin_line.pack(pady=2)

failure_brake_var = tk.BooleanVar(value=False)
brake_switch = ttk.Checkbutton(murphy_frame, text="Brake", variable=failure_brake_var,
                               command=lambda: current_train.set_brake_failure(failure_brake_var.get()),
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
tk.Label(live_metrics, text="Live Metrics", bg=off_color, fg='white', width=120, height=1, anchor='n', font=('Arial',20,'bold')).pack(pady=5,padx=5)
thin_line = tk.Frame(live_metrics, bg='black')
thin_line.pack(fill='x')

tk.Label(live_metrics,text="Speed",bg=off_color,fg='white',width=120,height=1,font=('Arial',30,'bold')).pack(pady=20,padx=5)
ui_labels['speed'] = tk.Label(live_metrics,text="0.0 MPH",bg=off_color,fg='white',width=120,height=1,font=('Arial',27,'bold'))
ui_labels['speed'].pack(pady=15,padx=5)
thin_line = tk.Frame(live_metrics, bg='black',width=300)
thin_line.pack()

tk.Label(live_metrics,text="Acceleration",bg=off_color,fg='white',width=120,height=1,font=('Arial',30,'bold')).pack(pady=20,padx=5)
ui_labels['acceleration'] = tk.Label(live_metrics,text="0.0 MPH²",bg=off_color,fg='white',width=120,height=1,font=('Arial',27,'bold'))
ui_labels['acceleration'].pack(pady=20,padx=5)
thin_line = tk.Frame(live_metrics, bg='black',width=300)
thin_line.pack()

ui_labels['passenger_count'] = tk.Label(live_metrics,text="Passenger Count: 0",bg=off_color,fg='white',width=120,height=1,font=('Arial',25,'bold'))
ui_labels['passenger_count'].pack(pady=40,padx=5)
ui_labels['crew_count'] = tk.Label(live_metrics,text="Crew Count: 0",bg=off_color,fg='white',width=120,height=1,font=('Arial',25,'bold'))
ui_labels['crew_count'].pack(pady=40,padx=5)

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
                                   command=lambda: current_train.set_emergency_brake(True),
                                   relief='raised', bd=1, padx=15, pady=3, height=50)
emergency_brake_button.pack(fill='both')

root.mainloop()