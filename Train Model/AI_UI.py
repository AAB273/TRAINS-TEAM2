import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime

class TrainControlInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Train Control System")
        self.root.configure(bg='#1a1a4d')
        self.root.geometry("1000x650")
        
        # Murphy failure states
        self.murphy_states = {
            "Train Engine": True,
            "Signal Pickup": True, 
            "Brake": True
        }
        
        # Murphy LED canvases for updating colors
        self.murphy_leds = {}
        
        # Current selected train
        self.selected_train = 1
        
        # Train data for different trains
        self.train_data = {
            1: {"speed": 20, "acceleration": 2, "passengers": 45, "crew": 2, "temp": 70, "power": 34},
            2: {"speed": 35, "acceleration": 1.5, "passengers": 62, "crew": 3, "temp": 72, "power": 42},
            3: {"speed": 15, "acceleration": 3, "passengers": 28, "crew": 2, "temp": 68, "power": 28},
            4: {"speed": 42, "acceleration": 0.8, "passengers": 71, "crew": 3, "temp": 74, "power": 55},
            5: {"speed": 28, "acceleration": 2.2, "passengers": 39, "crew": 2, "temp": 69, "power": 38},
            6: {"speed": 0, "acceleration": 0, "passengers": 0, "crew": 1, "temp": 65, "power": 5},
            7: {"speed": 12, "acceleration": 1.8, "passengers": 18, "crew": 2, "temp": 71, "power": 22},
            8: {"speed": 38, "acceleration": 1.2, "passengers": 58, "crew": 3, "temp": 73, "power": 48},
            9: {"speed": 25, "acceleration": 2.5, "passengers": 33, "crew": 2, "temp": 67, "power": 32},
            10: {"speed": 0, "acceleration": 0, "passengers": 0, "crew": 1, "temp": 64, "power": 8},
            11: {"speed": 31, "acceleration": 1.6, "passengers": 47, "crew": 2, "temp": 70, "power": 41}
        }
        
        # Create main container
        self.create_interface()
        
        # Start time updates
        self.update_time()
        
    def create_interface(self):
        # Top tabs
        self.create_tabs()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#1a1a4d')
        main_frame.pack(fill='both', expand=True, padx=5, pady=2)
        
        # Status bar with time and arrival info
        self.create_status_bar(main_frame)
        
        # Content sections - more compact layout
        content_frame = tk.Frame(main_frame, bg='#1a1a4d')
        content_frame.pack(fill='both', expand=True, pady=5)
        
        # Left side - Train Metrics and Emergency
        left_frame = tk.Frame(content_frame, bg='#1a1a4d', width=280)
        left_frame.pack(side='left', fill='y', padx=(0, 3))
        left_frame.pack_propagate(False)
        
        self.create_train_metrics(left_frame)
        self.create_emergency_brake(left_frame)
        
        # Middle - Door Controls and Murphy Failures
        middle_frame = tk.Frame(content_frame, bg='#1a1a4d', width=280)
        middle_frame.pack(side='left', fill='y', padx=3)
        middle_frame.pack_propagate(False)
        
        self.create_door_controls(middle_frame)
        self.create_murphy_failures(middle_frame)
        
        # Right side - Train Selector
        right_frame = tk.Frame(content_frame, bg='#1a1a4d', width=150)
        right_frame.pack(side='right', fill='y', padx=(3, 0))
        right_frame.pack_propagate(False)
        
        self.create_train_selector(right_frame)
    
    def create_tabs(self):
        tab_frame = tk.Frame(self.root, bg='#1a1a4d')
        tab_frame.pack(fill='x', padx=5, pady=2)
        
        # Passenger View tab (active)
        passenger_tab = tk.Button(tab_frame, text="Passenger View", 
                                 bg='#87ceeb', fg='black', font=('Arial', 10),
                                 relief='raised', bd=1, padx=15, pady=3)
        passenger_tab.pack(side='left')
        
        # Test View tab (inactive)
        test_tab = tk.Button(tab_frame, text="Test View", 
                            bg='white', fg='black', font=('Arial', 10),
                            relief='raised', bd=1, padx=15, pady=3)
        test_tab.pack(side='left')
    
    def create_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg='#1a1a4d')
        status_frame.pack(fill='x', pady=(0, 5))
        
        # Time and logo section
        time_frame = tk.Frame(status_frame, bg='#2d2d5d', relief='solid', bd=1, height=50)
        time_frame.pack(side='left', padx=(0, 5))
        time_frame.pack_propagate(False)
        
        # Mock logo (circular frame)
        logo_canvas = tk.Canvas(time_frame, bg='orange', width=40, height=40, highlightthickness=0)
        logo_canvas.pack(side='left', padx=5, pady=5)
        logo_canvas.create_oval(2, 2, 38, 38, fill='orange', outline='black', width=2)
        
        # Time display
        self.time_label = tk.Label(time_frame, text="12:45pm", font=('Arial', 18, 'bold'),
                                  bg='#2d2d5d', fg='white')
        self.time_label.pack(side='left', padx=5)
        
        # Arrival info
        arrival_frame = tk.Frame(status_frame, bg='#2d2d5d', relief='solid', bd=1, height=50)
        arrival_frame.pack(fill='x', expand=True)
        arrival_frame.pack_propagate(False)
        
        arrival_label = tk.Label(arrival_frame, text="ARRIVING AT DORMONT IN 5mins",
                               font=('Arial', 14, 'bold'), bg='#2d2d5d', fg='white')
        arrival_label.pack(expand=True)
    
    def create_train_metrics(self, parent):
        metrics_frame = tk.LabelFrame(parent, text="Train Metrics", font=('Arial', 10, 'bold'),
                                    bg='#2d2d5d', fg='white', bd=1, relief='solid')
        metrics_frame.pack(fill='x', pady=(0, 3))
        
        # Live Metrics header
        live_header = tk.Label(metrics_frame, text="Live Metrics", font=('Arial', 10, 'bold'),
                              bg='#4d4d6d', fg='white', relief='solid', bd=1)
        live_header.pack(fill='x', padx=3, pady=(3, 2))
        
        # Content area - side by side layout
        content_frame = tk.Frame(metrics_frame, bg='#2d2d5d')
        content_frame.pack(fill='x', padx=3, pady=3)
        
        # Left side - Cabin temp and dimensions
        left_side = tk.Frame(content_frame, bg='#2d2d5d', width=120)
        left_side.pack(side='left', fill='y')
        left_side.pack_propagate(False)
        
        # Cabin Temperature
        temp_frame = tk.Frame(left_side, bg='#4d4d6d', relief='solid', bd=1)
        temp_frame.pack(fill='x', pady=(0, 2))
        
        tk.Label(temp_frame, text="Cabin Temp", font=('Arial', 8, 'bold'),
                bg='#4d4d6d', fg='white').pack(pady=2)
        
        self.temp_circle = tk.Canvas(temp_frame, width=50, height=50, bg='#4d4d6d', highlightthickness=0)
        self.temp_circle.pack(pady=2)
        
        # Train Dimensions
        dim_frame = tk.Frame(left_side, bg='#4d4d6d', relief='solid', bd=1)
        dim_frame.pack(fill='x', pady=(0, 2))
        
        tk.Label(dim_frame, text="Train Dimensions", font=('Arial', 8, 'bold'),
                bg='#4d4d6d', fg='white').pack(pady=(2, 1))
        
        tk.Label(dim_frame, text="Height: 11.2ft", font=('Arial', 7),
                bg='#4d4d6d', fg='white').pack()
        tk.Label(dim_frame, text="Length: 150.642ft", font=('Arial', 7),
                bg='#4d4d6d', fg='white').pack()
        tk.Label(dim_frame, text="Width: 8.7ft", font=('Arial', 7),
                bg='#4d4d6d', fg='white').pack(pady=(0, 2))
        
        # Power Command
        power_frame = tk.Frame(left_side, bg='#4d4d6d', relief='solid', bd=1)
        power_frame.pack(fill='x')
        
        tk.Label(power_frame, text="Power Command", font=('Arial', 8, 'bold'),
                bg='#4d4d6d', fg='white').pack(pady=(2, 1))
        self.power_label = tk.Label(power_frame, font=('Arial', 10, 'bold'),
                bg='#4d4d6d', fg='white')
        self.power_label.pack(pady=(0, 2))
        
        # Right side - Speed, Acceleration, Counts
        right_side = tk.Frame(content_frame, bg='#2d2d5d')
        right_side.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Speed
        tk.Label(right_side, text="Speed", font=('Arial', 12, 'bold'),
                bg='#2d2d5d', fg='white').pack()
        self.speed_label = tk.Label(right_side, font=('Arial', 20, 'bold'),
                bg='#2d2d5d', fg='white')
        self.speed_label.pack(pady=(0, 5))
        
        # Separator line
        tk.Frame(right_side, height=1, bg='#6d6d8d').pack(fill='x', pady=2)
        
        # Acceleration
        tk.Label(right_side, text="Acceleration", font=('Arial', 12, 'bold'),
                bg='#2d2d5d', fg='white').pack()
        self.accel_label = tk.Label(right_side, font=('Arial', 20, 'bold'),
                bg='#2d2d5d', fg='white')
        self.accel_label.pack(pady=(0, 5))
        
        # Separator line
        tk.Frame(right_side, height=1, bg='#6d6d8d').pack(fill='x', pady=2)
        
        # Passenger Count
        self.passenger_label = tk.Label(right_side, font=('Arial', 9),
                bg='#2d2d5d', fg='white')
        self.passenger_label.pack(pady=1)
        
        # Crew Count
        self.crew_label = tk.Label(right_side, font=('Arial', 9),
                bg='#2d2d5d', fg='white')
        self.crew_label.pack()
        
        # Update display with initial train data
        self.update_train_display()
    
    def create_emergency_brake(self, parent):
        emergency_frame = tk.Frame(parent, bg='#cc0000', relief='solid', bd=2, height=60)
        emergency_frame.pack(fill='x', pady=(3, 0))
        emergency_frame.pack_propagate(False)
        
        emergency_btn = tk.Button(emergency_frame, text="EMERGENCY BRAKE", 
                                font=('Arial', 14, 'bold'), bg='#cc0000', fg='white',
                                relief='flat', bd=0, command=self.emergency_brake_clicked)
        emergency_btn.pack(expand=True, fill='both')
    
    def create_door_controls(self, parent):
        # Right Cabin Door
        right_door_frame = tk.LabelFrame(parent, text="Right Cabin Door", 
                                       font=('Arial', 10, 'bold'),
                                       bg='#2d2d5d', fg='white', bd=1, relief='solid')
        right_door_frame.pack(fill='x', pady=(0, 3))
        
        right_led = tk.Canvas(right_door_frame, width=80, height=25, bg='#2d2d5d', highlightthickness=0)
        right_led.pack(pady=5)
        right_led.create_oval(5, 5, 75, 20, fill='green', outline='black', width=1)
        right_led.create_text(40, 12, text="LED", fill='white', font=('Arial', 8, 'bold'))
        
        # Left Cabin Door
        left_door_frame = tk.LabelFrame(parent, text="Left Cabin Door", 
                                      font=('Arial', 10, 'bold'),
                                      bg='#2d2d5d', fg='white', bd=1, relief='solid')
        left_door_frame.pack(fill='x', pady=(0, 3))
        
        left_led = tk.Canvas(left_door_frame, width=80, height=25, bg='#2d2d5d', highlightthickness=0)
        left_led.pack(pady=5)
        left_led.create_oval(5, 5, 75, 20, fill='red', outline='black', width=1)
        left_led.create_text(40, 12, text="LED", fill='white', font=('Arial', 8, 'bold'))
        
        # Interior Lights
        lights_frame = tk.LabelFrame(parent, text="Interior Lights", 
                                   font=('Arial', 10, 'bold'),
                                   bg='#2d2d5d', fg='white', bd=1, relief='solid')
        lights_frame.pack(fill='x', pady=(0, 3))
        
        lights_led = tk.Canvas(lights_frame, width=80, height=25, bg='#2d2d5d', highlightthickness=0)
        lights_led.pack(pady=5)
        lights_led.create_oval(5, 5, 75, 20, fill='green', outline='black', width=1)
        lights_led.create_text(40, 12, text="LED", fill='white', font=('Arial', 8, 'bold'))
        
        # Headlights
        headlights_frame = tk.LabelFrame(parent, text="Headlights", 
                                       font=('Arial', 10, 'bold'),
                                       bg='#2d2d5d', fg='white', bd=1, relief='solid')
        headlights_frame.pack(fill='x', pady=(0, 3))
        
        headlights_led = tk.Canvas(headlights_frame, width=80, height=25, bg='#2d2d5d', highlightthickness=0)
        headlights_led.pack(pady=5)
        headlights_led.create_oval(5, 5, 75, 20, fill='green', outline='black', width=1)
        headlights_led.create_text(40, 12, text="LED", fill='white', font=('Arial', 8, 'bold'))
    
    def create_murphy_failures(self, parent):
        murphy_frame = tk.LabelFrame(parent, text="Murphy Failure Modes", 
                                   font=('Arial', 10, 'bold'),
                                   bg='#2d2d5d', fg='white', bd=1, relief='solid')
        murphy_frame.pack(fill='x')
        
        failures = ["Train Engine", "Signal Pickup", "Brake"]
        
        for name in failures:
            failure_frame = tk.Frame(murphy_frame, bg='#2d2d5d')
            failure_frame.pack(fill='x', padx=5, pady=3)
            
            # Name label
            tk.Label(failure_frame, text=name, font=('Arial', 9),
                    bg='#2d2d5d', fg='white', width=12, anchor='w').pack(side='left')
            
            # Toggle switch (clickable)
            switch_frame = tk.Frame(failure_frame, bg='#2d2d5d')
            switch_frame.pack(side='left', padx=(10, 5))
            
            switch_canvas = tk.Canvas(switch_frame, width=30, height=15, bg='#2d2d5d', highlightthickness=0)
            switch_canvas.pack()
            
            # Bind click event to toggle switch
            switch_canvas.bind("<Button-1>", lambda e, n=name, c=switch_canvas: self.toggle_murphy_switch(n, c))
            
            self.draw_switch(switch_canvas, self.murphy_states[name])
            
            # LED indicator
            led_canvas = tk.Canvas(failure_frame, width=40, height=15, bg='#2d2d5d', highlightthickness=0)
            led_canvas.pack(side='right')
            
            # Store LED canvas reference for updates
            self.murphy_leds[name] = led_canvas
            
            # Draw initial LED state
            self.update_murphy_led(name)
    
    def update_murphy_led(self, name):
        """Update the LED color based on switch state"""
        canvas = self.murphy_leds[name]
        canvas.delete("all")
        
        # Green if switch is ON (failure mode active), Red if OFF
        color = 'green' if self.murphy_states[name] else 'red'
        canvas.create_oval(5, 3, 35, 12, fill=color, outline='black', width=1)
        canvas.create_text(20, 7, text="LED", fill='white', font=('Arial', 6, 'bold'))
    
    def draw_switch(self, canvas, state):
        canvas.delete("all")
        if state:  # On position
            canvas.create_rectangle(1, 1, 29, 14, fill='green', outline='black', width=1)
            canvas.create_oval(16, 2, 27, 13, fill='white', outline='black', width=1)
        else:  # Off position
            canvas.create_rectangle(1, 1, 29, 14, fill='gray', outline='black', width=1)
            canvas.create_oval(3, 2, 14, 13, fill='white', outline='black', width=1)
    
    def toggle_murphy_switch(self, name, canvas):
        self.murphy_states[name] = not self.murphy_states[name]
        self.draw_switch(canvas, self.murphy_states[name])
        self.update_murphy_led(name)  # Update LED color
        print(f"{name} switch: {'ON' if self.murphy_states[name] else 'OFF'}")
    
    def create_train_selector(self, parent):
        selector_frame = tk.LabelFrame(parent, text="Train Selector", 
                                     font=('Arial', 10, 'bold'),
                                     bg='#4d4d6d', fg='white', bd=1, relief='solid')
        selector_frame.pack(fill='both', expand=True)
        
        # Header row
        header_frame = tk.Frame(selector_frame, bg='#4d4d6d')
        header_frame.pack(fill='x', padx=3, pady=2)
        
        tk.Label(header_frame, text="Train #", font=('Arial', 9, 'bold'),
                bg='#4d4d6d', fg='white', width=6).pack(side='left')
        tk.Label(header_frame, text="Deployed?", font=('Arial', 9, 'bold'),
                bg='#4d4d6d', fg='white').pack(side='left')
        
        # Train rows
        train_colors = ['green'] * 5 + ['red'] * 6  # Trains 1-5 green, 6-11 red
        self.train_buttons = {}  # Store train button references
        
        for i in range(11):
            train_frame = tk.Frame(selector_frame, bg='#4d4d6d')
            train_frame.pack(fill='x', padx=3, pady=1)
            
            # Train number - make it clickable
            train_btn = tk.Button(train_frame, text=f"Train {i+1}", font=('Arial', 8),
                    bg='#4d4d6d', fg='white', width=6, relief='flat', bd=0,
                    command=lambda train_num=i+1: self.select_train(train_num))
            train_btn.pack(side='left')
            self.train_buttons[i+1] = train_btn
            
            # Status bar
            status_canvas = tk.Canvas(train_frame, width=80, height=12, bg='#4d4d6d', highlightthickness=0)
            status_canvas.pack(side='left', fill='x', expand=True)
            
            color = train_colors[i]
            status_canvas.create_rectangle(1, 1, 79, 11, fill=color, outline='black', width=1)
            
            # Add blue sections for variety
            if i < 5:  # Green trains get blue bottom sections
                status_canvas.create_rectangle(1, 7, 79, 11, fill='blue', outline='black', width=1)
            else:  # Red trains get blue top sections
                status_canvas.create_rectangle(1, 1, 79, 5, fill='blue', outline='black', width=1)
        
        # Highlight initially selected train
        self.update_train_selection_display()
    
    def select_train(self, train_num):
        """Select a different train and update the display"""
        self.selected_train = train_num
        self.update_train_display()
        self.update_train_selection_display()
        print(f"Selected Train {train_num}")
    
    def update_train_display(self):
        """Update the main display with current train's data"""
        data = self.train_data[self.selected_train]
        
        # Update temperature display
        self.temp_circle.delete("all")
        self.temp_circle.create_oval(5, 5, 45, 45, fill='#6d6d8d', outline='white', width=2)
        self.temp_circle.create_text(25, 25, text=f"{data['temp']}°F", fill='white', font=('Arial', 8, 'bold'))
        
        # Update power
        self.power_label.config(text=f"{data['power']} Watts")
        
        # Update speed
        self.speed_label.config(text=f"{data['speed']} MPH")
        
        # Update acceleration
        self.accel_label.config(text=f"{data['acceleration']} MPH²")
        
        # Update passenger and crew counts
        self.passenger_label.config(text=f"Passenger Count: {data['passengers']}")
        self.crew_label.config(text=f"Crew Count: {data['crew']}")
    
    def update_train_selection_display(self):
        """Update the visual indication of which train is selected"""
        for train_num, button in self.train_buttons.items():
            if train_num == self.selected_train:
                button.config(bg='#6d6d8d', fg='yellow')  # Highlight selected train
            else:
                button.config(bg='#4d4d6d', fg='white')  # Normal appearance
    
    def update_time(self):
        current_time = datetime.now().strftime("%I:%M%p").lower()
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Update every second
    
    def emergency_brake_clicked(self):
        print("EMERGENCY BRAKE ACTIVATED!")
        # Add emergency brake functionality here

def main():
    root = tk.Tk()
    app = TrainControlInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()