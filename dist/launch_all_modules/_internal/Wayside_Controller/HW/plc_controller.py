# ==========================================
# plc_controller.py — Simulated PLC Logic
# ==========================================
from datetime import datetime

class PLCController:
    def __init__(self, log_callback):
        """
        log_callback: reference to add_to_message_log(message)
        """
        self.log = log_callback  # fixed assignment
        self.railroad_light = "GREEN"          # Default
        self.block_3_occupied = False
        self.crossing_fault = False
    
    def main(self):
        """Run the PLC logic"""
        self.log("PLC logic running...")
        # Add PLC behavior here

    def set_crossing_fault(self, state: bool):
        """Trigger or clear a railroad crossing fault."""
        self.crossing_fault = state
        if state:
            self.handle_fault_condition()
        else:
            self.restore_normal_operation()

    def handle_fault_condition(self):
        """If a fault occurs, switch light to RED and mark block 3 occupied."""
        self.railroad_light = "RED"
        self.block_3_occupied = True
        self.log("PLC program updated changes: Railroad fault detected. Light set to RED, Block 3 marked occupied.")

    def restore_normal_operation(self):
        """Clear the fault, return light to GREEN and free block 3."""
        self.railroad_light = "GREEN"
        self.block_3_occupied = False
        self.log("PLC program updated changes: Fault cleared. Light set to GREEN, Block 3 unoccupied.")
