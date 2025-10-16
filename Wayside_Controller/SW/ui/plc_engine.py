import threading
import time
import os
from datetime import datetime
import importlib.util

class PLCProgram:
    def __init__(self, data, log_callback=None):
        """
        PLCProgram runs a user-uploaded PLC Python file in a safe background thread.
        data: the shared data object for the system
        log_callback: function to send log messages to the UI
        """
        self.data = data
        self.log_callback = log_callback
        self.running = False
        self.thread = None
        self.plc_file = None  # Path to the PLC Python file
        self.cycle_interval = 2.0  # Run PLC cycle every 2 seconds (adjustable)

    def start(self):
        """Start the PLC program in a background thread."""
        if not self.plc_file:
            if self.log_callback:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_callback(f"{current_time} WARNING: No PLC file uploaded. Cannot start PLC.")
            return

        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_loop, daemon=True)
            self.thread.start()
            if self.log_callback:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_callback(f"{current_time} SYSTEM: PLC Program started.")

    def stop(self):
        """Stop the PLC program safely."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=2.0)  # Wait up to 2 seconds for clean shutdown
            if self.log_callback:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_callback(f"{current_time} SYSTEM: PLC Program stopped.")

    def run_loop(self):
        """Main PLC scan loop with configurable cycle time."""
        while self.running:
            try:
                if not self.running:
                    break
                
                # Execute one PLC cycle
                self.perform_logic()
                
                # Sleep in small increments for responsive shutdown
                sleep_chunks = int(self.cycle_interval * 10)  # 100ms chunks
                for _ in range(sleep_chunks):
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                if self.log_callback:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_callback(f"{current_time} ERROR: PLC thread error: {e}")
                # Continue running even after errors
                time.sleep(1.0)

    def perform_logic(self):
        """Load and execute the PLC cycle from the uploaded file."""
        try:
            if not self.plc_file or not os.path.exists(self.plc_file):
                if self.log_callback:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_callback(f"{current_time} ERROR: PLC file not found or missing.")
                return

            # Dynamically load the PLC Python module
            spec = importlib.util.spec_from_file_location("plc_module", self.plc_file)
            plc_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plc_module)

            # Run the PLC cycle function
            if hasattr(plc_module, "run_plc_cycle") and callable(plc_module.run_plc_cycle):
                plc_module.run_plc_cycle(self.data, self.log_callback)
            else:
                if self.log_callback:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_callback(f"{current_time} ERROR: PLC file missing run_plc_cycle(data, log)")
                    
        except Exception as e:
            if self.log_callback:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_callback(f"{current_time} WARNING: PLC runtime error: {e}")