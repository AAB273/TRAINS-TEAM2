import tkinter as tk
from tkinter import ttk
import math


class EmergencyLight(tk.Canvas):
    def __init__(self, parent, size=100, color="red", glow_color="darkred", **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, **kwargs)
        self.size = size
        self.color = color
        self.glow_color = glow_color
        self.active = False
        
        self.points = [size/2, 0, 0, size, size, size]
        self.triangle = self.create_polygon(self.points, fill=color, outline="black", width=2)
        self.text = self.create_text(size/2, size*0.65, text="!", 
                                    font=("Arial", int(size/3), "bold"), fill="white")
    
    def activate(self):
        self.itemconfig(self.triangle, fill=self.glow_color)
        self.active = True
    
    def deactivate(self):
        self.itemconfig(self.triangle, fill=self.color)
        self.active = False
    
    def set_state(self, state):
        if state:
            self.activate()
        else:
            self.deactivate()