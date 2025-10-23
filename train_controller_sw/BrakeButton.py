import tkinter as tk
from tkinter import ttk
import math
import time

class Brake_button(tk.Canvas):
    def __init__(self, parent, radius=40, color="orange", hover_color="lightorange",
                 active_color="darkorange", text="", command=None, hold_mode=False, canvas_bg="white", **kwargs):
        # Extract canvas_bg before passing to super
        super().__init__(parent, width=radius*2, height=radius*2, highlightthickness=0, 
                        bg=canvas_bg, **kwargs)
        
        self.radius = radius
        self.color = color
        self.hover_color = hover_color
        self.active_color = active_color
        self.command = command
        self.hold_mode = hold_mode
        self.is_pressed = False
        
        self.circle = self.create_oval(2, 2, radius*2-2, radius*2-2, fill=color, outline="black", width=3)
        self.text_id = self.create_text(radius, radius, text=text, font=("Arial", 12, "bold"), 
                                       fill="white", width=radius*1.5)
        
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def on_hover(self, event):
        if not self.is_pressed:
            self.itemconfig(self.circle, fill=self.hover_color)
    
    def on_leave(self, event):
        if not self.is_pressed:
            self.itemconfig(self.circle, fill=self.color)
    
    def on_press(self, event):
        self.is_pressed = True
        self.itemconfig(self.circle, fill=self.active_color)
        if self.command:
            self.command(True)
    
    def on_release(self, event):
        if self.hold_mode:
            self.is_pressed = False
            self.itemconfig(self.circle, fill=self.color)
            if self.command:
                self.command(False)