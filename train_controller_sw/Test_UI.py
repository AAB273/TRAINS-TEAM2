import tkinter as tk
from tkinter import ttk
import math
import time

class TestPanel(tk.Toplevel):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.title("Input Test Panel")
        self.geometry("500x650")
        self.main_window = main_window

        tk.Label(self, text="TEST INTERFACE", font=("Arial", 16, "bold")).pack(pady=10)

        # Temperature Input
        tk.Label(self, text="Set Cabin Temperature (°F):", font=("Arial", 12)).pack(pady=5)
        self.temp_entry = tk.Entry(self)
        self.temp_entry.insert(0, "65")
        self.temp_entry.pack()
        tk.Button(self, text="Send Temp", command=self.set_temp).pack(pady=5)

        # Commanded Authority Input
        tk.Label(self, text="Set Commanded Authority (Blocks):", font=("Arial", 12)).pack(pady=5)
        self.auth_entry = tk.Entry(self)
        self.auth_entry.insert(0, "4")
        self.auth_entry.pack()
        tk.Button(self, text="Send Authority", command=self.set_authority).pack(pady=5)

        # Commanded Speed Input
        tk.Label(self, text="Set Commanded Speed (mph):", font=("Arial", 12)).pack(pady=5)
        self.speed_entry = tk.Entry(self)
        self.speed_entry.insert(0, "55")
        self.speed_entry.pack()
        tk.Button(self, text="Send Speed", command=self.set_speed).pack(pady=5)

        # Speedometer Input
        tk.Label(self, text="Speedometer (Actual Speed mph):", font=("Arial", 12)).pack(pady=5)
        self.actual_speed = tk.Scale(self, from_=0, to=80, orient=tk.HORIZONTAL, command=self.update_speedometer)
        self.actual_speed.pack(fill="x", padx=20)

        # Service Brake Percentage
        tk.Label(self, text="Service Brake Percentage:", font=("Arial", 12)).pack(pady=5)
        self.brake_percentage = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, 
                                       command=self.update_brake_percentage)
        self.brake_percentage.set(0)
        self.brake_percentage.pack(fill="x", padx=20)

        # Emergency Signal
        tk.Label(self, text="Emergency Signal:", font=("Arial", 12)).pack(pady=10)
        tk.Button(self, text="Activate Emergency", bg="red", fg="white", command=self.activate_emergency).pack(pady=3)
        tk.Button(self, text="Deactivate Emergency", bg="grey", fg="white", command=self.deactivate_emergency).pack(pady=3)

        # Failure Mode Controls
        failure_frame = tk.Frame(self)
        failure_frame.pack(pady=10, fill="x", padx=20)
        
        tk.Label(failure_frame, text="Failure Modes:", font=("Arial", 12, "bold")).pack()
        
        failure_controls = tk.Frame(failure_frame)
        failure_controls.pack(pady=5)
        
        # Train Engine Failure
        tk.Button(failure_controls, text="TEF ON", bg="red", fg="white", 
                 command=lambda: self.set_failure("engine", True)).grid(row=0, column=0, padx=5)
        tk.Button(failure_controls, text="TEF OFF", bg="green", fg="white",
                 command=lambda: self.set_failure("engine", False)).grid(row=0, column=1, padx=5)
        
        # Signal Pickup Failure  
        tk.Button(failure_controls, text="SPF ON", bg="orange", fg="white",
                 command=lambda: self.set_failure("signal", True)).grid(row=1, column=0, padx=5, pady=2)
        tk.Button(failure_controls, text="SPF OFF", bg="green", fg="white",
                 command=lambda: self.set_failure("signal", False)).grid(row=1, column=1, padx=5, pady=2)
        
        # Brake Failure
        tk.Button(failure_controls, text="BF ON", bg="red", fg="white",
                 command=lambda: self.set_failure("brake", True)).grid(row=2, column=0, padx=5, pady=2)
        tk.Button(failure_controls, text="BF OFF", bg="green", fg="white",
                 command=lambda: self.set_failure("brake", False)).grid(row=2, column=1, padx=5, pady=2)

        # Output Log
        tk.Label(self, text="Log:", font=("Arial", 12, "bold")).pack(pady=5)
        self.log = tk.Text(self, height=8, width=50, state=tk.DISABLED)
        self.log.pack(pady=5, fill="both", expand=True)

    def log_action(self, text):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def set_temp(self):
        val = self.temp_entry.get()
        self.main_window.set_cabin_temp(val)
        self.main_window.add_to_status_log(f"Temperature set to {val}°F")
        self.log_action(f" Temperature input set to {val}°F")

    def set_authority(self):
        val = self.auth_entry.get()
        self.main_window.set_authority(val)
        self.main_window.add_to_status_log(f"Authority set to {val} blocks")
        self.log_action(f" Commanded authority set to {val} Blocks")

    def set_speed(self):
        val = self.speed_entry.get()
        # Only update commanded speed when in auto mode
        if self.main_window.mode_select.active_mode == "auto":
            self.main_window.set_commanded_speed(val)
            self.main_window.add_to_status_log(f"Commanded speed set to {val} mph (auto mode)")
            self.log_action(f" Commanded speed set to {val} mph (auto mode)")
        else:
            self.log_action(" Ignored commanded speed (not in auto mode)")

    def update_speedometer(self, val):
        val = int(val)
        self.main_window.set_current_speed(val)
        self.log_action(f" Speedometer updated to {val} mph")

    def update_brake_percentage(self, val):
        self.main_window.set_service_brake_percentage(int(val))
        self.log_action(f" Service brake percentage set to {val}%")

    def activate_emergency(self):
        self.main_window.emergency_brake_action(True)
        self.log_action(" Emergency signal activated")

    def deactivate_emergency(self):
        self.main_window.emergency_brake_action(False)
        self.log_action(" Emergency signal cleared")

    def set_failure(self, failure_type, state):
        if failure_type == "engine":
            self.main_window.engine_failure.set_state(state)
            status = "ON" if state else "OFF"
            self.main_window.add_to_status_log(f"Train Engine Failure: {status}")
            self.log_action(f" Train Engine Failure: {status}")
        elif failure_type == "signal":
            self.main_window.signal_failure.set_state(state)
            status = "ON" if state else "OFF"
            self.main_window.add_to_status_log(f"Signal Pickup Failure: {status}")
            self.log_action(f" Signal Pickup Failure: {status}")
        elif failure_type == "brake":
            self.main_window.brake_failure.set_state(state)
            status = "ON" if state else "OFF"
            self.main_window.add_to_status_log(f"Brake Failure: {status}")
            self.log_action(f" Brake Failure: {status}")



if __name__ == "__main__":
    app = TestPanel()
    app.mainloop()
