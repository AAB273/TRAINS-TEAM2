import tkinter as tk
from tkinter import ttk

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