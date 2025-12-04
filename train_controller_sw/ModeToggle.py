import tkinter as tk
from tkinter import ttk

class Mode_Toggle(tk.Frame):
    def __init__(self, parent, callback=None):
        super().__init__(parent, bg="gray")
        
        self.callback = callback
        self.active_mode = None
        
        self.Driver_button1 = tk.Button(self, text="Auto", command=lambda: self.set_mode("auto"), 
                                       font=("Arial", 12, "bold"), width=8)
        self.Driver_button2 = tk.Button(self, text="Manual", command=lambda: self.set_mode("manual"),
                                       font=("Arial", 12, "bold"), width=8)
        
        self.Driver_button1.grid(row=0, column=0, padx=5, pady=5)
        self.Driver_button2.grid(row=0, column=1, padx=5, pady=5)
        
        self.set_mode("auto")
    
    def set_mode(self, mode):
        if mode == self.active_mode:
            return
        
        self.active_mode = mode
        
        if mode == "auto":
            self.Driver_button1.config(bg="lightgreen", activebackground="green")
            self.Driver_button2.config(bg="lightgrey", activebackground="grey")
        else:
            self.Driver_button2.config(bg="lightgreen", activebackground="green")
            self.Driver_button1.config(bg="lightgrey", activebackground="grey")
        
        if self.callback:
            self.callback(mode)