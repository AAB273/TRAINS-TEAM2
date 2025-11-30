import random

class HeaterSystemManager:
    """
    Handles all track heater management, including power state, functionality,
    validation, and automatic temperature control for each block.
    """

    def __init__(self, data_manager):
        """
        Initialize the Heater System Manager.

        Args:
            data_manager: Reference to TrackDataManager containing all blocks.
                         Can also accept a UI object - will extract manager attribute.
        """
        # Handle if UI object is passed instead of data_manager
        if hasattr(data_manager, 'manager'):
            self.data_manager = data_manager.manager
        else:
            self.data_manager = data_manager
        
        # Temperature settings
        # Target temperature is what heaters try to ACHIEVE (comfort level for stations)
        self.target_temperature = 68.0  # Default target temp in Fahrenheit (what heaters maintain)
        self.temperature_threshold = 3.0  # Turn on heater if X degrees below target
        
        # Environmental temp is the OUTSIDE temperature (cold weather)
        # Blocks start at environmental temp and heaters warm them up to target temp
        
        # Initialize individual block temperatures (start at environmental temp or default)
        self.block_temperatures = {}
        self.initialize_all_temperatures()

    def initialize_all_temperatures(self):
        """Initialize or reinitialize all block temperatures"""
        # Safe initialization - check if blocks exist
        if hasattr(self.data_manager, 'blocks') and self.data_manager.blocks:
            env_temp = self.data_manager.environmental_temp if self.data_manager.environmental_temp else 23.0
            for block in self.data_manager.blocks:
                # Only initialize if not already set, or reinitialize all
                self.block_temperatures[block.block_number] = env_temp
        #     print(f"🌡️ Initialized {len(self.block_temperatures)} block temperatures to {env_temp}°F")
        # else:
        #     print("⚠️ Warning: No blocks found during temperature initialization")

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
            # print(f"⚠️ Cannot turn on heater for block {block.block_number} - heater is not working")
            return False  # Can't turn on a non-working heater
        
        block.track_heater = [1 if is_on else 0, 1 if is_working else 0]
        # print(f"🔧 Block {block.block_number} heater: {'ON' if is_on else 'OFF'}, {'WORKING' if is_working else 'BROKEN'}")
        return True

    def toggle_heater(self, block_num):
        """Toggle heater on/off if it's working"""
        block = self.data_manager.blocks[block_num - 1]
        if self.is_heater_working(block):
            new_state = not self.is_heater_on(block)
            self.set_heater_state(block, new_state, True)
        # else:
        #     print(f"❌ Cannot toggle heater for block {block_num} - heater is not working")

    def break_heater(self, block_num):
        """Break the heater (turns it off if it was on)"""
        block = self.data_manager.blocks[block_num - 1]
        was_on = self.is_heater_on(block)
        self.set_heater_state(block, False, False)  # Turn off and break
        # if was_on:
        #     print(f"🔧 Heater broken and turned off for block {block_num}")

    def fix_heater(self, block_num):
        """Fix the heater (doesn't change on/off state)"""
        block = self.data_manager.blocks[block_num - 1]
        is_on = self.is_heater_on(block)
        self.set_heater_state(block, is_on, True)  # Keep current on/off state, set working

    # -------------------------------------------------------------------------
    # TEMPERATURE CONTROL SYSTEM
    # -------------------------------------------------------------------------
    def set_target_temperature(self, temp):
        """Set the target temperature for the system"""
        self.target_temperature = temp
        # print(f"🌡️ Target temperature set to {temp}°F")

    def set_environmental_temperature(self, temp):
        """Update the environmental temperature in data manager and reinitialize block temps"""
        self.data_manager.environmental_temp = temp
        # Reinitialize all block temperatures to the new environmental temp
        for block_num in self.block_temperatures:
            self.block_temperatures[block_num] = temp
        # print(f"🌡️ Environmental temperature set to {temp}°F - All blocks reset to {temp}°F")
        
        # Immediately trigger heater control based on new temperature
        self.update_all_temperatures()

    def get_block_temperature(self, block_num):
        """Get the current temperature of a specific block"""
        # If block not in dict, initialize it first
        if block_num not in self.block_temperatures:
            env_temp = self.data_manager.environmental_temp if self.data_manager.environmental_temp else 23.0
            self.block_temperatures[block_num] = env_temp
        return self.block_temperatures[block_num]

    def update_block_temperature(self, block):
        """
        Update a single block's temperature based on heater state.
        Called during the temperature control cycle.
        """
        block_num = block.block_number
        
        # Ensure block is in temperature dict
        if block_num not in self.block_temperatures:
            env_temp = self.data_manager.environmental_temp if self.data_manager.environmental_temp else 23.0
            self.block_temperatures[block_num] = env_temp
            
        current_temp = self.block_temperatures[block_num]
        environmental_temp = self.data_manager.environmental_temp if self.data_manager.environmental_temp else 23.0
        
        if self.is_heater_on(block) and self.is_heater_working(block):
            # Heater is on and working - heat up (2-3 degrees per refresh)
            heat_increase = random.uniform(2.0, 3.0)
            new_temp = current_temp + heat_increase
            
            # Don't exceed a reasonable maximum (target + 10 degrees)
            max_temp = self.target_temperature + 10.0
            new_temp = min(new_temp, max_temp)
            
        else:
            # Heater is off or broken - cool down toward environmental temp (1-2 degrees per refresh)
            if current_temp > environmental_temp:
                cool_decrease = random.uniform(1.0, 2.0)
                new_temp = current_temp - cool_decrease
                # Don't go below environmental temp
                new_temp = max(new_temp, environmental_temp)
            else:
                # Already at or below environmental temp
                new_temp = current_temp
        
        self.block_temperatures[block_num] = round(new_temp, 1)
        return new_temp

    def automatic_heater_control(self, block):
        """
        Automatically control heater based on temperature for a single block.
        Returns True if state changed, False otherwise.
        """
        block_num = block.block_number
        
        # Ensure temperature is initialized
        if block_num not in self.block_temperatures:
            env_temp = self.data_manager.environmental_temp if self.data_manager.environmental_temp else 23.0
            self.block_temperatures[block_num] = env_temp
            
        current_temp = self.block_temperatures[block_num]
        
        # Only control if heater is working
        if not self.is_heater_working(block):
            return False
        
        state_changed = False
        
        # Turn on if temperature is below target - threshold
        if current_temp < (self.target_temperature - self.temperature_threshold):
            if not self.is_heater_on(block):
                self.set_heater_state(block, True, True)
                state_changed = True
                # print(f"🔥 AUTO: Block {block_num} heater turned ON (temp: {current_temp:.1f}°F < target: {self.target_temperature}°F)")
        
        # Turn off if temperature reaches or exceeds target
        elif current_temp >= self.target_temperature:
            if self.is_heater_on(block):
                self.set_heater_state(block, False, True)
                state_changed = True
                # print(f"❄️ AUTO: Block {block_num} heater turned OFF (temp: {current_temp:.1f}°F >= target: {self.target_temperature}°F)")
        
        return state_changed

    def update_all_temperatures(self):
        """
        Update temperatures for all blocks and manage heaters automatically.
        Call this method periodically (e.g., every second or on UI refresh).
        """
        for block in self.data_manager.blocks:
            # First, automatically control the heater
            self.automatic_heater_control(block)
            
            # Then, update the temperature based on current heater state
            self.update_block_temperature(block)

    def get_temperature_status(self):
        """
        Get a summary of all block temperatures and heater states.
        
        Returns:
            dict: {block_number: {'temp': float, 'heater_on': bool, 'heater_working': bool}}
        """
        status = {}
        for block in self.data_manager.blocks:
            status[block.block_number] = {
                'temperature': self.block_temperatures[block.block_number],
                'heater_on': self.is_heater_on(block),
                'heater_working': self.is_heater_working(block),
                'target_temp': self.target_temperature
            }
        return status

    # -------------------------------------------------------------------------
    # BULK OPERATIONS
    # -------------------------------------------------------------------------
    def reset_all_heaters(self):
        """Turn off and fix all heaters in all blocks."""
        for block in self.data_manager.blocks:
            block.track_heater = [0, 1]  # OFF but WORKING
        # print("♻️ All heaters reset to OFF and functional.")

    def break_all_heaters(self):
        """Mark all heaters as broken."""
        for block in self.data_manager.blocks:
            block.track_heater = [0, 0]  # OFF and BROKEN
        # print("💣 All heaters marked as broken.")

    def reset_all_temperatures(self):
        """Reset all block temperatures to environmental temperature"""
        env_temp = self.data_manager.environmental_temp or 50.0
        for block_num in self.block_temperatures:
            self.block_temperatures[block_num] = env_temp
        # print(f"🌡️ All block temperatures reset to {env_temp}°F")

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
    # UI HOOKS
    # -------------------------------------------------------------------------
    def update_ui_heater_indicators(self, ui_labels: dict):
        """
        Update UI heater indicators based on each block's heater state and temperature.

        Args:
            ui_labels (dict): Mapping of block numbers to Tkinter Label widgets.
        """
        for block_num, label in ui_labels.items():
            block = self.data_manager.blocks[block_num - 1]
            current_temp = self.block_temperatures[block_num]
            
            state = "ON 🔥" if self.is_heater_on(block) else "OFF ❄️"
            working = "OK ✅" if self.is_heater_working(block) else "BROKEN ⚠️"
            
            label.config(text=f"Block {block_num}: {state} | {working} | {current_temp:.1f}°F")

    def update_ui_temperature_display(self, temp_labels: dict):
        """
        Update UI temperature displays for each block.
        
        Args:
            temp_labels (dict): Mapping of block numbers to Tkinter Label widgets for temperature.
        """
        for block_num, label in temp_labels.items():
            current_temp = self.block_temperatures[block_num]
            target = self.target_temperature
            
            # Color code based on temperature relative to target
            if current_temp >= target:
                color = "green"
            elif current_temp >= target - self.temperature_threshold:
                color = "orange"
            else:
                color = "red"
            
            label.config(
                text=f"{current_temp:.1f}°F (Target: {target:.1f}°F)",
                fg=color
            )