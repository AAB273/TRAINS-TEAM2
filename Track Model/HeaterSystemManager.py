

class HeaterSystemManager:
    """
    Handles all track heater management, including power state, functionality,
    and validation for each block in the track model system.
    """

    def __init__(self, data_manager):
        """
        Initialize the Heater System Manager.

        Args:
            data_manager: Reference to TrackDataManager containing all blocks.
        """
        self.data_manager = data_manager

    # -------------------------------------------------------------------------
    # HEATER STATE CHECKS
    # -------------------------------------------------------------------------
    def is_heater_on(self, block):
        """Check if the heater is ON (first bit of track_heater)."""
        if hasattr(block, 'track_heater') and isinstance(block.track_heater, list):
            return block.track_heater[0] == 1
        return False

    def is_heater_working(self, block):
        """Check if the heater is FUNCTIONAL (second bit of track_heater)."""
        if hasattr(block, 'track_heater') and isinstance(block.track_heater, list):
            return block.track_heater[1] == 1
        return False

    # -------------------------------------------------------------------------
    # HEATER STATE CONTROL
    # -------------------------------------------------------------------------
    def set_heater_state(self, block, is_on, is_working):
        """Set heater state with validation"""
        if not is_working and is_on:
            print(f"⚠️ Cannot turn on heater for block {block.block_number} - heater is not working")
            return False  # Can't turn on a non-working heater
        
        block.track_heater = [1 if is_on else 0, 1 if is_working else 0]
        print(f"🔧 Block {block.block_number} heater: {'ON' if is_on else 'OFF'}, {'WORKING' if is_working else 'BROKEN'}")
        return True

    def toggle_heater(self, block_num):
        """Toggle heater on/off if it's working"""
        block = self.data_manager.blocks[block_num - 1]
        if self.is_heater_working(block):
            new_state = not self.is_heater_on(block)
            self.set_heater_state(block, new_state, True)
        else:
            print(f"❌ Cannot toggle heater for block {block_num} - heater is not working")

    def break_heater(self, block_num):
        """Break the heater (turns it off if it was on)"""
        block = self.data_manager.blocks[block_num - 1]
        was_on = self.is_heater_on(block)
        self.set_heater_state(block, False, False)  # Turn off and break
        if was_on:
            print(f"🔧 Heater broken and turned off for block {block_num}")

    def fix_heater(self, block_num):
        """Fix the heater (doesn't change on/off state)"""
        block = self.data_manager.blocks[block_num - 1]
        is_on = self.is_heater_on(block)
        self.set_heater_state(block, is_on, True)  # Keep current on/off state, set working

    # -------------------------------------------------------------------------
    # BULK OPERATIONS
    # -------------------------------------------------------------------------
    def reset_all_heaters(self):
        """Turn off and fix all heaters in all blocks."""
        for block in self.data_manager.blocks:
            block.track_heater = [0, 1]  # OFF but WORKING
        print("♻️ All heaters reset to OFF and functional.")

    def break_all_heaters(self):
        """Mark all heaters as broken."""
        for block in self.data_manager.blocks:
            block.track_heater = [0, 0]  # OFF and BROKEN
        print("💣 All heaters marked as broken.")

    def get_heater_status_summary(self) -> dict:
        """
        Return a dictionary summary of heater states.

        Returns:
            dict: {block_number: {'on': bool, 'working': bool}}
        """
        summary = {}
        for block in self.data_manager.blocks:
            summary[block.block_number] = {
                "on": self.is_heater_on(block),
                "working": self.is_heater_working(block)
            }
        return summary

    # -------------------------------------------------------------------------
    # OPTIONAL: UI HOOKS
    # -------------------------------------------------------------------------
    def update_ui_heater_indicators(self, ui_labels: dict):
        """
        Update UI heater indicators based on each block’s heater state.

        Args:
            ui_labels (dict): Mapping of block numbers to Tkinter Label widgets.
        """
        for block_num, label in ui_labels.items():
            block = self.data_manager.blocks[block_num - 1]
            state = "ON 🔥" if self.is_heater_on(block) else "OFF ❄️"
            working = "OK ✅" if self.is_heater_working(block) else "BROKEN ⚠️"
            label.config(text=f"Block {block_num}: {state} | {working}")
