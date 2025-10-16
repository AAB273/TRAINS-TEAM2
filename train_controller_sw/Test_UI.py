import tkinter as tk
import random

class NumberDisplay(tk.Frame):
    """Displays a label + dynamic number value (with optional unit)."""
    def __init__(self, parent, label_text="Value:", initial_value=0, unit="", **kwargs):
        super().__init__(parent, **kwargs)
        self.value = initial_value
        self.unit = unit
        tk.Label(self, text=label_text, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.display = tk.Label(self, text=f"{self.value} {self.unit}", font=("Arial", 12))
        self.display.pack(side="left", padx=5)
    def update_value(self, new_value):
        self.value = new_value
        self.display.config(text=f"{self.value} {self.unit}")

class EmergencyLight(tk.Canvas):
    """Triangle warning light that glows red when activated."""
    def __init__(self, parent, size=80, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, **kwargs)
        self.size = size
        self.glow = False
        h = size
        w = size
        self.triangle = self.create_polygon(
            w/2, 5,
            w-5, h-5,
            5, h-5,
            fill="gray", outline="black", width=2
        )
        self.text = self.create_text(w/2, h*0.65, text="!", font=("Arial", int(size/2), "bold"), fill="white")

    def activate(self):
        self.glow = True
        self._pulse_light()

    def deactivate(self):
        self.glow = False
        self.itemconfig(self.triangle, fill="gray")

    def toggle_failure(self, failure_type, state):
        """Send failure signal input to main UI"""
        if failure_type == 'engine':
            self.main_window.set_engine_failure(state)
        elif failure_type == 'signal':
            self.main_window.set_signal_failure(state)
        elif failure_type == 'brake':
            self.main_window.set_brake_failure(state)

        action = "activated" if state else "cleared"
        self.log_action(f"⚠️ {failure_type.title()} failure {action}")


    def _pulse_light(self):
        if not self.glow:
            return
        # Alternate between two shades of red
        current_color = self.itemcget(self.triangle, "fill")
        new_color = "red2" if current_color == "darkred" else "darkred"
        self.itemconfig(self.triangle, fill=new_color)
        self.after(500, self._pulse_light)

class TestPanel(tk.Tk):
    """Standalone input test GUI with auto-test mode."""
    def __init__(self):
        super().__init__()
        self.title("Input Test Panel")
        self.geometry("400x450")
        #self.main_window = main_window

        tk.Label(self, text="TEST INTERFACE", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        # Temperature input
        tk.Label(self, text="Cabin Temperature (°F):", bg="white").pack()
        self.temp_display = NumberDisplay(self, label_text="", initial_value=70, unit="°F", bg="white")
        self.temp_display.pack(pady=5)
        tk.Button(self, text="Random Temp", command=self.random_temp).pack(pady=5)

        # Authority
        tk.Label(self, text="Commanded Authority (blocks):", bg="white").pack()
        self.auth_display = NumberDisplay(self, label_text="", initial_value=4, unit="Blocks", bg="white")
        self.auth_display.pack(pady=5)
        tk.Button(self, text="Random Authority", command=self.random_authority).pack(pady=5)

        # Commanded Speed
        tk.Label(self, text="Commanded Speed (mph):", bg="white").pack()
        self.speed_display = NumberDisplay(self, label_text="", initial_value=55, unit="mph", bg="white")
        self.speed_display.pack(pady=5)
        tk.Button(self, text="Random Speed", command=self.random_speed).pack(pady=5)

        # Speedometer Slider
        tk.Label(self, text="Actual Speed (mph):", bg="white").pack()
        self.speed_scale = tk.Scale(self, from_=0, to=80, orient=tk.HORIZONTAL, command=self.update_speed, bg="white")
        self.speed_scale.pack(fill="x", padx=30, pady=5)

        # Emergency Light
        tk.Label(self, text="Emergency Indicator:", bg="white").pack(pady=10)
        self.emergency_light = EmergencyLight(self)
        self.emergency_light.pack(pady=5)
        tk.Button(self, text="Activate", bg="red", fg="white", command=self.emergency_light.activate).pack(side="left", padx=30, pady=10)
        tk.Button(self, text="Deactivate", bg="grey", fg="white", command=self.emergency_light.deactivate).pack(side="right", padx=30, pady=10)

        # Failure Mode Signals
        tk.Label(self, text="Failure Mode Signals:", font=("Arial", 12, "bold")).pack(pady=8)

        fail_frame = tk.Frame(self)
        fail_frame.pack(pady=5)

        # Train Engine Failure
        tk.Button(fail_frame, text="Engine FAIL", bg="red", fg="white",
                command=lambda: self.toggle_failure('engine', True)).grid(row=0, column=0, padx=5)
        tk.Button(fail_frame, text="Engine CLEAR", bg="grey", fg="white",
                command=lambda: self.toggle_failure('engine', False)).grid(row=1, column=0, padx=5)

        # Signal Pickup Failure
        tk.Button(fail_frame, text="Signal FAIL", bg="orange", fg="white",
                command=lambda: self.toggle_failure('signal', True)).grid(row=0, column=1, padx=5)
        tk.Button(fail_frame, text="Signal CLEAR", bg="grey", fg="white",
                command=lambda: self.toggle_failure('signal', False)).grid(row=1, column=1, padx=5)

        # Brake Failure
        tk.Button(fail_frame, text="Brake FAIL", bg="red", fg="white",
                command=lambda: self.toggle_failure('brake', True)).grid(row=0, column=2, padx=5)
        tk.Button(fail_frame, text="Brake CLEAR", bg="grey", fg="white",
                command=lambda: self.toggle_failure('brake', False)).grid(row=1, column=2, padx=5)


        # Auto test controls
        tk.Label(self, text="Automatic Test Mode:", bg="white").pack(pady=10)
        tk.Button(self, text="Start Auto Test", bg="blue", fg="white", command=self.start_auto_test).pack(pady=3)
        tk.Button(self, text="Stop Auto Test", bg="grey", fg="white", command=self.stop_auto_test).pack(pady=3)

        # Log output
        tk.Label(self, text="Log:", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
        self.log = tk.Text(self, height=6, width=40, state=tk.DISABLED)
        self.log.pack(pady=5)

        # State
        self.auto_testing = False
        self.auto_step = 0

    # Random value setters
    def random_temp(self):
        val = random.randint(60, 75)
        self.temp_display.update_value(val)
        self.log_action(f"🌡️ Temperature set to {val}°F")

    def random_authority(self):
        val = random.randint(1, 5)
        self.auth_display.update_value(val)
        self.log_action(f"📏 Authority set to {val} blocks")

    def random_speed(self):
        val = random.randint(30, 80)
        self.speed_display.update_value(val)
        self.log_action(f"🚆 Commanded speed set to {val} mph")

    def update_speed(self, val):
        self.log_action(f"🧭 Actual speed: {val} mph")

    # Auto test
    def start_auto_test(self):
        self.auto_testing = True
        self.auto_step = 0
        self.log_action("🤖 Starting auto test mode...")
        self.run_auto_step()

    def stop_auto_test(self):
        self.auto_testing = False
        self.log_action("🛑 Auto test mode stopped.")

    def run_auto_step(self):
        if not self.auto_testing:
            return

        step = self.auto_step % 6

        if step == 0:
            self.random_temp()
        elif step == 1:
            self.random_authority()
        elif step == 2:
            self.random_speed()
        elif step == 3:
            speed = random.randint(0, 80)
            self.speed_scale.set(speed)
            self.update_speed(speed)
        elif step == 4:
            self.emergency_light.activate()
            self.log_action("🚨 Emergency activated")
        elif step == 5:
            self.emergency_light.deactivate()
            self.log_action("🟢 Emergency cleared")

        self.auto_step += 1
        self.after(1500, self.run_auto_step)

    def log_action(self, text):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = TestPanel()
    app.mainloop()
