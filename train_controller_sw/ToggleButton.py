import tkinter as tk
from tkinter import ttk

class ToggleButton(tk.Button):
    def __init__(self, parent, text="", callback=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.callback = callback
        self.is_on = False
        self.config(command=self.toggle, bg="lightgrey", activebackground="grey")
    
    def toggle(self):
        self.is_on = not self.is_on
        if self.is_on:
            self.config(bg="lightgreen", activebackground="green")
        else:
            self.config(bg="lightgrey", activebackground="grey")
        
        if self.callback:
            self.callback(self.is_on)