

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
    def set_heater_state(self, block, is_on: bool, is_working: bool) -> bool:
        """
        Set the heater state for a block with safety validation.

        Args:
            block: The Block object.
            is_on (bool): Whether heater should be ON.
            is_working (bool): Whether heater is functional.

        Returns:
            bool: True if state change succeeded, False otherwise.
        """
        # Prevent turning ON a broken heater
        if not is_working and is_on:
            print(f"⚠️ Cannot turn on heater for block {block.block_number} - heater is broken.")
            return False

        block.track_heater = [1 if is_on else 0, 1 if is_working else 0]
        print(f"🔥 Heater update: Block {block.block_number} → {'ON' if is_on else 'OFF'} | "
              f"{'WORKING' if is_working else 'BROKEN'}")
        return True

    def toggle_heater(self, block_num: int):
        """
        Toggle the heater ON/OFF if it is functional.

        Args:
            block_num (int): Block number.
        """
        block = self.data_manager.blocks[block_num - 1]
        if self.is_heater_working(block):
            new_state = not self.is_heater_on(block)
            self.set_heater_state(block, new_state, True)
            print(f"🔄 Toggled heater for block {block_num}: {'ON' if new_state else 'OFF'}")
        else:
            print(f"❌ Cannot toggle heater for block {block_num} - heater not functional.")

    def break_heater(self, block_num: int):
        """
        Mark heater as broken and ensure it’s OFF.

        Args:
            block_num (int): Block number.
        """
        block = self.data_manager.blocks[block_num - 1]
        was_on = self.is_heater_on(block)
        self.set_heater_state(block, False, False)
        print(f"💥 Heater broken for block {block_num} (was {'ON' if was_on else 'OFF'})")

    def fix_heater(self, block_num: int):
        """
        Repair heater while keeping current ON/OFF state.

        Args:
            block_num (int): Block number.
        """
        block = self.data_manager.blocks[block_num - 1]
        is_on = self.is_heater_on(block)
        self.set_heater_state(block, is_on, True)
        print(f"🧰 Heater repaired for block {block_num} (state preserved: {'ON' if is_on else 'OFF'})")

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
