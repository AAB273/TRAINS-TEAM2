import tkinter as tk
import time
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import font
from tkinter import ttk


main_color = '#1a1a4d'
off_color = '#4d4d6d'
######################
root = tk.Tk()
root.title("Test Passenger GUI")
root.configure(bg=main_color)
root.geometry("1250x910")
######################################

#Train Selector
selector_frame = tk.Frame(root, bg=main_color, highlightbackground="black", highlightthickness=4, width=200)
selector_frame.pack(side='right', fill='y', padx=3, pady=3)
selector_frame.pack_propagate(False)

selector_frame.columnconfigure(0, weight=1)  # Train column expands
selector_frame.columnconfigure(1, weight=0)  # Separator column doesn't expand
selector_frame.columnconfigure(2, weight=1)  # Status column expands

# Main Title
title_label = tk.Label(selector_frame, text="Train Selector", bg=main_color, fg='white', font=('Arial', 14, 'bold'))
title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='ew')

# Separator under title
title_separator = ttk.Separator(selector_frame, orient='horizontal')
title_separator.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 10))

# Headers
header_train = tk.Label(selector_frame, text="Train #", bg=main_color, fg='white', font=('Arial', 12, 'bold'))
header_status = tk.Label(selector_frame, text="Deployed?", bg=main_color, fg='white', font=('Arial', 12, 'bold'))

header_train.grid(row=2, column=0, padx=10, pady=(5, 5), sticky='ew')
header_status.grid(row=2, column=2, padx=10, pady=(5, 5), sticky='ew')

# Vertical separator between columns
separator = ttk.Separator(selector_frame, orient='vertical')
separator.grid(row=2, column=1, rowspan=32, padx=10, pady=5, sticky='ns')

# First horizontal separator (right under headers)
first_separator = ttk.Separator(selector_frame, orient='horizontal')
first_separator.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 5))

# Create 10 rows for trains
for i in range(14):
    row_num = 4 + (i * 2)  # Rows 4, 6, 8, 10... for content
    
    # Train number label
    train_label = tk.Label(selector_frame, text=f"Train {i+1}", bg=main_color, fg='white', font=('Arial', 10))
    train_label.grid(row=row_num, column=0, padx=10, pady=10, sticky='ew')
    
    # Canvas for status indicator (rectangle that fits the row)
    status_canvas = tk.Canvas(selector_frame, width=60, height=25, bg=main_color, highlightthickness=0)
    status_canvas.grid(row=row_num, column=2, padx=10, pady=10)
    
    # Draw rectangle - change fill color based on deployment status
    is_deployed = i % 2 == 0  # Example: alternating deployed status
    fill_color = 'green' if is_deployed else 'red'
    status_canvas.create_rectangle(2, 2, 58, 23, fill=fill_color, outline='white', width=2)
    
    # Horizontal separator after each row (except the last one)
    if i < 14:
        row_separator = ttk.Separator(selector_frame, orient='horizontal')
        row_separator.grid(row=row_num+1, column=0, columnspan=3, sticky='ew', pady=5)




# Top Container for time and announcement frames
top_container = tk.Frame(root, bg=main_color, highlightbackground="black", highlightthickness=4)
top_container.pack(fill='x')  # Only fill horizontally, not vertically

#BLT Logo
blt_logo_image = Image.open("Train Model/blt logo.png")
converted_blt_logo_image = blt_logo_image.resize((75,75))
converted_blt_logo_image = ImageTk.PhotoImage(converted_blt_logo_image)
blt_logo_frame = tk.Frame(top_container, bg=main_color, height=80,width=80)
blt_logo_frame.pack(fill='x',side='left',pady=3,padx=3)
blt_logo_frame.pack_propagate(False)
tk.Label(
    blt_logo_frame,
    image=converted_blt_logo_image,
    bg=main_color
).pack(padx=1,pady=1)
blt_logo_frame.image = converted_blt_logo_image

# Time Frame (left side of middle container)
time_frame = tk.Frame(top_container, bg=off_color, width=200, height=80, highlightbackground="black", highlightthickness=4)
time_frame.pack(side='left', padx=3, pady=3)
time_frame.pack_propagate(False)
tk.Label(
    time_frame,
    text="Time",
    bg=off_color,
    fg='white',
    font=('Arial',10,'bold')
).pack(padx=5, pady=5)

# Announcement Frame (right side of middle container)
Announcement_frame = tk.Frame(top_container, bg=off_color, width=800, height=80, highlightbackground="black", highlightthickness=4)
Announcement_frame.pack(side='left', padx=3, pady=3)
Announcement_frame.pack_propagate(False)
tk.Label(
    Announcement_frame,
    text="Arriving to Dormount in 5 seconds",
    bg=off_color,
    fg='white',
    font=('Arial',10,'bold')
).pack(padx=5, pady=5)
########################################################
left_frame = tk.Frame(root, bg=main_color)
left_frame.pack(side='left',fill='both')

right_frame = tk.Frame(root, bg=main_color)
right_frame.pack(side='right',fill='both',expand=True)

#Left Test Inputs including Speed, Acceleration, Passenger and Crew Count, Power Command, Train Height & Width & Length
test_inputs_left = tk.Frame(left_frame, bg=off_color, highlightbackground="black", highlightthickness=4)
test_inputs_left.pack(fill='both', expand=True, padx=5, pady=5)

# Configure grid weights for proper expansion
test_inputs_left.columnconfigure(0, weight=1)
test_inputs_left.columnconfigure(1, weight=1)

# Row 0: Speed
tk.Label(test_inputs_left, text="Speed (MPH)", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=0, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=0, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 0
separator1 = ttk.Separator(test_inputs_left, orient='horizontal')
separator1.grid(row=1, column=0, columnspan=2, sticky='ew', pady=10)

# Row 2: Acceleration
tk.Label(test_inputs_left, text="Acceleration (MPH^2)", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=2, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=2, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 2
separator2 = ttk.Separator(test_inputs_left, orient='horizontal')
separator2.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)

# Row 4: Passenger Count
tk.Label(test_inputs_left, text="Passenger Count", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=4, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=4, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 4
separator3 = ttk.Separator(test_inputs_left, orient='horizontal')
separator3.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)

# Row 6: Crew Count
tk.Label(test_inputs_left, text="Crew Count", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=6, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=6, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 6
separator4 = ttk.Separator(test_inputs_left, orient='horizontal')
separator4.grid(row=7, column=0, columnspan=2, sticky='ew', pady=10)

# Row 8: Power Command
tk.Label(test_inputs_left, text="Power Command (kW)", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=8, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=8, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 8
separator5 = ttk.Separator(test_inputs_left, orient='horizontal')
separator5.grid(row=9, column=0, columnspan=2, sticky='ew', pady=10)

# Row 10: Train Height
tk.Label(test_inputs_left, text="Train Height (ft)", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=10, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=10, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 10
separator6 = ttk.Separator(test_inputs_left, orient='horizontal')
separator6.grid(row=11, column=0, columnspan=2, sticky='ew', pady=10)

# Row 12: Train Length
tk.Label(test_inputs_left, text="Train Length (ft)", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=12, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=12, column=1, padx=(35, 10), pady=10, sticky='ew')

# Separator after row 12
separator7 = ttk.Separator(test_inputs_left, orient='horizontal')
separator7.grid(row=13, column=0, columnspan=2, sticky='ew', pady=10)

# Row 14: Train Width
tk.Label(test_inputs_left, text="Train Width (ft)", bg=off_color, fg='white', font=('Arial', 25, 'bold')).grid(row=14, column=0, padx=(10, 35), pady=10, sticky='w')
tk.Entry(test_inputs_left).grid(row=14, column=1, padx=(35, 10), pady=10, sticky='ew')


##################################w
#Emergency Brake
emergency_brake = tk.Frame(left_frame,width=580,height=100, highlightbackground="black",highlightthickness=2,bg=off_color)
emergency_brake.pack(side='top',padx=3,pady=3)
emergency_brake.pack_propagate(False)
emergency_brake_button = tk.Button(
    emergency_brake,
    text="Emergency Brake", 
    bg="red", 
    fg='black', 
    font=('Arial', 10),  
    relief='raised', 
    bd=1, 
    padx=15, 
    pady=3, 
    height=50
)
emergency_brake_button.pack(fill='both')





root.mainloop()