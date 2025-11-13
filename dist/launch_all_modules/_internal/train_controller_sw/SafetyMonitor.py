import tkinter as tk
from tkinter import ttk

class SafetyMonitor:
    """Independent safety monitor using diverse logic to activate emergency brake"""

    def __init__(self, main_window):
        self.main_window = main_window

    def check_vital_conditions(self):
        """
        A different logic path that ensures train stops in unsafe conditions.
        This acts as a diverse backup to the main control logic.
        """
        # Use different signals than main brake logic:
        speed = self.main_window.current_speed
        door_status = self.main_window.door_status
        failures = (
            self.main_window.engine_failure.active or
            self.main_window.signal_failure.active or
            self.main_window.brake_failure.active
        )

        # Example of diversity:
        # Main system might use failures only,
        # but backup also considers abnormal speed & door state.
        unsafe = (failures or (door_status == "OPEN" and speed > 0))

        if unsafe:
            self.main_window.add_to_status_log(" SafetyMonitor: Unsafe condition detected, forcing E-Brake.")
            self.main_window.emergency_brake_action(True)
        else:
            # Optionally release only if E-brake was triggered by this module
            if self.main_window.emergency_brake_active:
                self.main_window.add_to_status_log(" SafetyMonitor: Conditions safe, maintaining brake state.")
