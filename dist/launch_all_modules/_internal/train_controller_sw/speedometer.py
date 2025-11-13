import tkinter as tk
from tkinter import ttk
import math
import time


class Speedometer(tk.Canvas):
    def __init__(self, parent, max_speed=80, **kwargs):
        super().__init__(parent, bg="white", highlightthickness=2, 
                        highlightbackground="navy", **kwargs)
        self.max_speed = max_speed
        self.current_speed = 0
        
        # Will be set dynamically based on canvas size
        self.center_x = 0
        self.center_y = 0
        self.radius = 0
        
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event=None):
        # Clear canvas
        self.delete("all")
        
        # Get canvas dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Calculate center and radius based on available space
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = min(width, height) * 0.4
        
        # Draw speedometer
        margin = 20
        self.create_oval(margin, margin, width-margin, height-margin, 
                        outline="navy", width=4)
        self.create_oval(margin+20, margin+20, width-margin-20, height-margin-20, 
                        outline="lightblue", width=2, fill="lightblue")
        
        # Draw tick marks and numbers
        for i in range(0, self.max_speed + 1, 10):
            angle = 225 - (i / self.max_speed * 270)
            angle_rad = math.radians(angle)
            
            x1 = self.center_x + (self.radius - 20) * math.cos(angle_rad)
            y1 = self.center_y - (self.radius - 20) * math.sin(angle_rad)
            x2 = self.center_x + (self.radius - 5) * math.cos(angle_rad)
            y2 = self.center_y - (self.radius - 5) * math.sin(angle_rad)
            
            self.create_line(x1, y1, x2, y2, width=3, fill="navy")
            
            x_text = self.center_x + (self.radius - 40) * math.cos(angle_rad)
            y_text = self.center_y - (self.radius - 40) * math.sin(angle_rad)
            self.create_text(x_text, y_text, text=str(i), 
                           font=("Arial", int(self.radius/8), "bold"), fill="navy")
        
        # Draw label
        self.create_text(self.center_x, self.center_y + self.radius * 0.5, 
                        text="mph", font=("Arial", int(self.radius/7), "bold"), 
                        fill="gray")
        
        # Redraw needle at current speed
        self.draw_needle(self.current_speed)
    
    def draw_needle(self, speed):
        # Remove old needle
        self.delete("needle")
        
        if self.radius == 0:
            return
        
        speed = max(0, min(speed, self.max_speed))
        angle = 225 - (speed / self.max_speed * 270)
        angle_rad = math.radians(angle)
        
        needle_length = self.radius - 35
        x = self.center_x + needle_length * math.cos(angle_rad)
        y = self.center_y - needle_length * math.sin(angle_rad)
        
        self.create_line(self.center_x, self.center_y, x, y, 
                        width=5, fill="navy", arrow=tk.LAST, 
                        arrowshape=(12, 15, 6), tags="needle")
        
        self.create_oval(self.center_x-10, self.center_y-10, 
                        self.center_x+10, self.center_y+10, 
                        fill="navy", outline="navy", tags="needle")
    
    def update_speed(self, speed):
        self.current_speed = speed
        self.draw_needle(speed)