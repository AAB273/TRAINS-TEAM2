"""
EngineerUI.py
Engineer control panel for adjusting PID parameters
"""

import tkinter as tk
from tkinter import ttk

class EngineerUI:
    def __init__(self, parent_window, callback=None):
        """
        Engineer UI for setting PID control parameters
        
        Args:
            parent_window: The main window (Main_Window instance)
            callback: Optional callback function when values change
        """
        self.parent = parent_window
        self.callback = callback
        
        # Create separate window
        self.window = tk.Toplevel(parent_window.root)
        self.window.title("Engineer Control Panel")
        self.window.geometry("400x350")
        self.window.configure(bg="lightgray")
        
        # Prevent closing with X button - hide instead
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container
        main_frame = tk.Frame(self.window, bg="white", relief=tk.RAISED, bd=3)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="PID Control Parameters", 
                              font=("Arial", 16, "bold"), bg="navy", fg="white",
                              relief=tk.RAISED, bd=2)
        title_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Warning label
        warning_label = tk.Label(main_frame, 
                                text="⚠️ Adjust with caution - affects train control",
                                font=("Arial", 9, "italic"), bg="white", fg="red")
        warning_label.pack(pady=(5, 10))
        
        # Kp Section
        kp_frame = tk.LabelFrame(main_frame, text="Proportional Gain (Kp)", 
                                font=("Arial", 12, "bold"), bg="lightblue", 
                                relief=tk.GROOVE, bd=2)
        kp_frame.pack(fill=tk.X, padx=10, pady=10)
        
        kp_info = tk.Label(kp_frame, text="Range: 0.0 - 20.0", 
                          font=("Arial", 9), bg="lightblue", fg="darkblue")
        kp_info.pack(pady=(5, 0))
        
        kp_control_frame = tk.Frame(kp_frame, bg="lightblue")
        kp_control_frame.pack(pady=10)
        
        # Kp slider
        self.kp_var = tk.DoubleVar(value=10.0)  # Default Kp = 10
        self.kp_slider = tk.Scale(kp_control_frame, from_=0, to=20, resolution=0.1,
                                  orient=tk.HORIZONTAL, length=220,
                                  variable=self.kp_var, command=self.on_kp_change,
                                  bg="lightblue", font=("Arial", 10),
                                  showvalue=False)
        self.kp_slider.pack(side=tk.LEFT, padx=10)
        
        # Kp value display
        self.kp_display = tk.Label(kp_control_frame, text="10.0", 
                                   font=("Arial", 18, "bold"), bg="black", 
                                   fg="lime", width=6, relief=tk.SUNKEN, bd=2)
        self.kp_display.pack(side=tk.LEFT, padx=10)
        
        # Ki Section
        ki_frame = tk.LabelFrame(main_frame, text="Integral Gain (Ki)", 
                                font=("Arial", 12, "bold"), bg="lightblue",
                                relief=tk.GROOVE, bd=2)
        ki_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ki_info = tk.Label(ki_frame, text="Range: 0.0 - 5.0", 
                          font=("Arial", 9), bg="lightblue", fg="darkblue")
        ki_info.pack(pady=(5, 0))
        
        ki_control_frame = tk.Frame(ki_frame, bg="lightblue")
        ki_control_frame.pack(pady=10)
        
        # Ki slider
        self.ki_var = tk.DoubleVar(value=2.0)  # Default Ki = 2
        self.ki_slider = tk.Scale(ki_control_frame, from_=0, to=5, resolution=0.1,
                                  orient=tk.HORIZONTAL, length=220,
                                  variable=self.ki_var, command=self.on_ki_change,
                                  bg="lightblue", font=("Arial", 10),
                                  showvalue=False)
        self.ki_slider.pack(side=tk.LEFT, padx=10)
        
        # Ki value display
        self.ki_display = tk.Label(ki_control_frame, text="2.0", 
                                   font=("Arial", 18, "bold"), bg="black", 
                                   fg="lime", width=6, relief=tk.SUNKEN, bd=2)
        self.ki_display.pack(side=tk.LEFT, padx=10)
        
        # Apply button
        apply_btn = tk.Button(main_frame, text="APPLY PARAMETERS", 
                             font=("Arial", 12, "bold"), bg="darkgreen", 
                             fg="white", command=self.apply_parameters,
                             relief=tk.RAISED, bd=3, padx=20, pady=8)
        apply_btn.pack(pady=15)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready to apply parameters", 
                                     font=("Arial", 10), bg="white", fg="blue")
        self.status_label.pack(pady=5)
        
    def on_kp_change(self, value):
        """Update Kp display when slider changes"""
        kp_value = float(value)
        self.kp_display.config(text=f"{kp_value:.1f}")
        
    def on_ki_change(self, value):
        """Update Ki display when slider changes"""
        ki_value = float(value)
        self.ki_display.config(text=f"{ki_value:.1f}")
    
    def apply_parameters(self):
        """Apply the current Kp and Ki values"""
        kp = self.kp_var.get()
        ki = self.ki_var.get()
        
        # Update parent window
        if hasattr(self.parent, 'set_pid_parameters'):
            self.parent.set_pid_parameters(kp, ki)
        
        # Call callback if provided
        if self.callback:
            self.callback(kp, ki)
        
        # Update status
        self.status_label.config(text=f"✓ Applied: Kp={kp:.1f}, Ki={ki:.1f}", 
                                fg="green")
        
        # Reset status after 3 seconds
        self.window.after(3000, lambda: self.status_label.config(
            text="Ready to apply parameters", fg="blue"))
        
        # Log to main window
        if hasattr(self.parent, 'add_to_status_log'):
            self.parent.add_to_status_log(f"PID parameters updated: Kp={kp:.1f}, Ki={ki:.1f}")
        
        print(f"PID Parameters Applied - Kp: {kp:.1f}, Ki: {ki:.1f}")
    
    def get_kp(self):
        """Get current Kp value"""
        return self.kp_var.get()
    
    def get_ki(self):
        """Get current Ki value"""
        return self.ki_var.get()
    
    def on_closing(self):
        """Handle window close - just hide instead of destroy"""
        self.window.withdraw()  # Hide window instead of closing
        
    def show(self):
        """Show the engineer UI window"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """Hide the engineer UI window"""
        self.window.withdraw()