"""
Engineer_UI.py
Engineer control panel with DUAL MODE:
- Live display of PID parameters from TC_HW (real-time monitoring)
- Manual adjustment capability (optional override)
"""

import tkinter as tk
from tkinter import ttk
import datetime

class EngineerUI:
    def __init__(self, parent_window, callback=None):
        """
        Engineer UI with live display and manual control
        
        Args:
            parent_window: The main window (Main_Window instance)
            callback: Callback function when values change
        """
        self.parent = parent_window
        self.callback = callback
        self.update_count = 0
        
        # Create separate window
        self.window = tk.Toplevel(parent_window.root)
        self.window.title("Engineer Control Panel")
        self.window.geometry("900x750")
        self.window.configure(bg="lightgray")
        
        # Prevent closing with X button - hide instead
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container
        main_frame = tk.Frame(self.window, bg="white", relief=tk.RAISED, bd=3)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="PID Control Parameters", 
                              font=("Arial", 18, "bold"), bg="navy", fg="white",
                              relief=tk.RAISED, bd=2)
        title_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Mode info
        info_label = tk.Label(main_frame, 
                             text="⚡ Receives live updates from TC_HW | Manual override available",
                             font=("Arial", 10, "italic"), bg="white", fg="blue")
        info_label.pack(pady=(5, 10))
        
        # ===== LIVE DISPLAY SECTION =====
        live_frame = tk.LabelFrame(main_frame, text="🔴 LIVE - Current Active Parameters", 
                                font=("Arial", 14, "bold"), bg="lightgreen", 
                                relief=tk.GROOVE, bd=3)
        live_frame.pack(fill=tk.X, padx=10, pady=10)
        
        live_info = tk.Label(live_frame, 
                          text="These values are actively controlling the train",
                          font=("Arial", 10, "italic"), bg="lightgreen", fg="darkgreen")
        live_info.pack(pady=(10, 15))
        
        # Kp Live Display
        kp_live_frame = tk.Frame(live_frame, bg="lightgreen")
        kp_live_frame.pack(fill=tk.X, pady=10, padx=20)
        
        tk.Label(kp_live_frame, text="Kp:", 
                font=("Arial", 14, "bold"), bg="lightgreen", fg="darkblue",
                width=15, anchor="w").pack(side=tk.LEFT, padx=10)
        
        self.kp_live_display = tk.Label(kp_live_frame, text="10.0", 
                                   font=("Arial", 42, "bold"), bg="black", 
                                   fg="lime", width=8, relief=tk.SUNKEN, bd=3)
        self.kp_live_display.pack(side=tk.LEFT, padx=10)
        
        # Ki Live Display
        ki_live_frame = tk.Frame(live_frame, bg="lightgreen")
        ki_live_frame.pack(fill=tk.X, pady=10, padx=20)
        
        tk.Label(ki_live_frame, text="Ki:", 
                font=("Arial", 14, "bold"), bg="lightgreen", fg="darkblue",
                width=15, anchor="w").pack(side=tk.LEFT, padx=10)
        
        self.ki_live_display = tk.Label(ki_live_frame, text="2.0", 
                                   font=("Arial", 42, "bold"), bg="black", 
                                   fg="lime", width=8, relief=tk.SUNKEN, bd=3)
        self.ki_live_display.pack(side=tk.LEFT, padx=10)
        
        # Last Update Info
        self.last_update_label = tk.Label(live_frame, 
                                          text="Waiting for TC_HW updates...",
                                          font=("Arial", 10, "italic"), 
                                          bg="lightgreen", fg="gray")
        self.last_update_label.pack(pady=10)
        
        # ===== MANUAL CONTROL SECTION =====
        manual_frame = tk.LabelFrame(main_frame, text="🔧 Manual Override Control", 
                                font=("Arial", 14, "bold"), bg="lightblue", 
                                relief=tk.GROOVE, bd=3)
        manual_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        manual_info = tk.Label(manual_frame, 
                              text="⚠️ Manual changes will override TC_HW values",
                              font=("Arial", 9, "italic"), bg="lightblue", fg="red")
        manual_info.pack(pady=(5, 10))
        
        # Kp Manual Control
        kp_manual_frame = tk.LabelFrame(manual_frame, text="Kp (Proportional Gain)", 
                                font=("Arial", 11, "bold"), bg="lightblue", 
                                relief=tk.GROOVE, bd=2)
        kp_manual_frame.pack(fill=tk.X, padx=15, pady=8)
        
        kp_info = tk.Label(kp_manual_frame, text="Range: 0.0 - 20.0", 
                          font=("Arial", 9), bg="lightblue", fg="darkblue")
        kp_info.pack(pady=(5, 0))
        
        kp_control_frame = tk.Frame(kp_manual_frame, bg="lightblue")
        kp_control_frame.pack(pady=10)
        
        self.kp_var = tk.DoubleVar(value=10.0)
        self.kp_slider = tk.Scale(kp_control_frame, from_=0, to=20, resolution=0.1,
                                  orient=tk.HORIZONTAL, length=200,
                                  variable=self.kp_var, command=self.on_kp_change,
                                  bg="lightblue", font=("Arial", 10),
                                  showvalue=False)
        self.kp_slider.pack(side=tk.LEFT, padx=10)
        
        self.kp_manual_display = tk.Label(kp_control_frame, text="10.0", 
                                   font=("Arial", 16, "bold"), bg="black", 
                                   fg="yellow", width=6, relief=tk.SUNKEN, bd=2)
        self.kp_manual_display.pack(side=tk.LEFT, padx=10)
        
        # Ki Manual Control
        ki_manual_frame = tk.LabelFrame(manual_frame, text="Ki (Integral Gain)", 
                                font=("Arial", 11, "bold"), bg="lightblue",
                                relief=tk.GROOVE, bd=2)
        ki_manual_frame.pack(fill=tk.X, padx=15, pady=8)
        
        ki_info = tk.Label(ki_manual_frame, text="Range: 0.0 - 5.0", 
                          font=("Arial", 9), bg="lightblue", fg="darkblue")
        ki_info.pack(pady=(5, 0))
        
        ki_control_frame = tk.Frame(ki_manual_frame, bg="lightblue")
        ki_control_frame.pack(pady=10)
        
        self.ki_var = tk.DoubleVar(value=2.0)
        self.ki_slider = tk.Scale(ki_control_frame, from_=0, to=5, resolution=0.1,
                                  orient=tk.HORIZONTAL, length=200,
                                  variable=self.ki_var, command=self.on_ki_change,
                                  bg="lightblue", font=("Arial", 10),
                                  showvalue=False)
        self.ki_slider.pack(side=tk.LEFT, padx=10)
        
        self.ki_manual_display = tk.Label(ki_control_frame, text="2.0", 
                                   font=("Arial", 16, "bold"), bg="black", 
                                   fg="yellow", width=6, relief=tk.SUNKEN, bd=2)
        self.ki_manual_display.pack(side=tk.LEFT, padx=10)
        
        # Apply button
        apply_btn = tk.Button(manual_frame, text="APPLY MANUAL OVERRIDE", 
                             font=("Arial", 12, "bold"), bg="darkgreen", 
                             fg="white", command=self.apply_parameters,
                             relief=tk.RAISED, bd=3, padx=20, pady=8)
        apply_btn.pack(pady=15)
        
        # ===== STATISTICS SECTION =====
        stats_frame = tk.LabelFrame(main_frame, text="Statistics", 
                                font=("Arial", 11, "bold"), bg="lightgray", 
                                relief=tk.GROOVE, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_grid = tk.Frame(stats_frame, bg="lightgray")
        stats_grid.pack(pady=8)
        
        tk.Label(stats_grid, text="TC_HW Updates:", 
                font=("Arial", 10, "bold"), bg="lightgray").grid(row=0, column=0, sticky="w", padx=15, pady=3)
        self.update_count_label = tk.Label(stats_grid, text="0", 
                                          font=("Arial", 10), bg="lightgray", fg="darkgreen")
        self.update_count_label.grid(row=0, column=1, sticky="w", pady=3)
        
        tk.Label(stats_grid, text="Connection:", 
                font=("Arial", 10, "bold"), bg="lightgray").grid(row=1, column=0, sticky="w", padx=15, pady=3)
        self.connection_status_label = tk.Label(stats_grid, text="⚪ Waiting", 
                                               font=("Arial", 10), bg="lightgray", fg="orange")
        self.connection_status_label.grid(row=1, column=1, sticky="w", pady=3)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready", 
                                     font=("Arial", 10, "bold"), bg="white", fg="blue")
        self.status_label.pack(pady=5)
        
        # Start waiting animation
        self._start_waiting_animation()
        
    def receive_pid_parameters(self, kp, ki):
        """
        Receive and display PID parameters from TC_HW
        Updates both live display and applies to controller immediately
        """
        # Update LIVE displays
        self.kp_live_display.config(text=f"{kp:.1f}")
        self.ki_live_display.config(text=f"{ki:.1f}")
        
        # Update manual sliders to match (so they stay in sync)
        self.kp_var.set(kp)
        self.ki_var.set(ki)
        self.kp_manual_display.config(text=f"{kp:.1f}")
        self.ki_manual_display.config(text=f"{ki:.1f}")
        
        # Apply immediately to parent controller
        if hasattr(self.parent, 'set_pid_parameters'):
            self.parent.set_pid_parameters(kp, ki)
        
        # Call callback
        if self.callback:
            self.callback(kp, ki)
        
        # Update statistics
        self.update_count += 1
        self.update_count_label.config(text=str(self.update_count))
        self.connection_status_label.config(text="🟢 Connected", fg="darkgreen")
        
        # Update timestamp
        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M:%S %p")
        self.last_update_label.config(
            text=f"Last update: {timestamp} - Kp={kp:.1f}, Ki={ki:.1f}",
            fg="darkgreen"
        )
        
        # Update status
        self.status_label.config(
            text=f"✅ LIVE from TC_HW: Kp={kp:.1f}, Ki={ki:.1f}",
            fg="darkgreen"
        )
        
        # Flash to show update
        self._flash_live_displays()
        
        # Log to main window
        if hasattr(self.parent, 'add_to_status_log'):
            self.parent.add_to_status_log(f"PID LIVE: Kp={kp:.1f}, Ki={ki:.1f}")
        
        print(f"[ENGINEER UI] Received from TC_HW: Kp={kp:.1f}, Ki={ki:.1f}")
    
    def on_kp_change(self, value):
        """Update Kp manual display when slider changes"""
        kp_value = float(value)
        self.kp_manual_display.config(text=f"{kp_value:.1f}")
        
    def on_ki_change(self, value):
        """Update Ki manual display when slider changes"""
        ki_value = float(value)
        self.ki_manual_display.config(text=f"{ki_value:.1f}")
    
    def apply_parameters(self):
        """Apply manual override - takes precedence over TC_HW values"""
        kp = self.kp_var.get()
        ki = self.ki_var.get()
        
        # Update LIVE displays to show manual override
        self.kp_live_display.config(text=f"{kp:.1f}")
        self.ki_live_display.config(text=f"{ki:.1f}")
        
        # Update parent window
        if hasattr(self.parent, 'set_pid_parameters'):
            self.parent.set_pid_parameters(kp, ki)
        
        # Call callback
        if self.callback:
            self.callback(kp, ki)
        
        # Update status
        self.status_label.config(
            text=f"⚠️ MANUAL OVERRIDE: Kp={kp:.1f}, Ki={ki:.1f}", 
            fg="orange"
        )
        
        self.last_update_label.config(
            text=f"Manual override applied: Kp={kp:.1f}, Ki={ki:.1f}",
            fg="orange"
        )
        
        # Log to main window
        if hasattr(self.parent, 'add_to_status_log'):
            self.parent.add_to_status_log(f"PID MANUAL: Kp={kp:.1f}, Ki={ki:.1f}")
        
        print(f"[ENGINEER UI] Manual override: Kp={kp:.1f}, Ki={ki:.1f}")
    
    def _flash_live_displays(self):
        """Flash live displays to indicate TC_HW update"""
        self.kp_live_display.config(bg="yellow", fg="black")
        self.ki_live_display.config(bg="yellow", fg="black")
        
        self.window.after(150, lambda: self.kp_live_display.config(bg="black", fg="lime"))
        self.window.after(150, lambda: self.ki_live_display.config(bg="black", fg="lime"))
    
    def _start_waiting_animation(self):
        """Animate while waiting for first TC_HW update"""
        if self.update_count == 0:
            current_color = self.connection_status_label.cget("fg")
            new_color = "orange" if current_color == "gray" else "gray"
            self.connection_status_label.config(fg=new_color)
            self.window.after(500, self._start_waiting_animation)
    
    def get_kp(self):
        """Get current Kp value from live display"""
        try:
            return float(self.kp_live_display.cget("text"))
        except:
            return 10.0
    
    def get_ki(self):
        """Get current Ki value from live display"""
        try:
            return float(self.ki_live_display.cget("text"))
        except:
            return 2.0
    
    def on_closing(self):
        """Handle window close - hide instead of destroy"""
        self.window.withdraw()
        
    def show(self):
        """Show the engineer UI window"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """Hide the engineer UI window"""
        self.window.withdraw()