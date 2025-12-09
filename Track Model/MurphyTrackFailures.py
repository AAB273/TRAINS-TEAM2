"""
MurphyTrackFailures.py

Manages Murphy Failures for track blocks including Track Circuit Failure,
Broken Railroad, and Power Failure.
"""

class MurphyTrackFailures:
    """
    Handles all Murphy failure modes for the track system.
    Integrates with HeaterSystemManager, signals, and crossings.
    """
    
    def __init__(self, data_manager, heater_manager=None, ui_reference=None):
        """
        Initialize the Murphy Track Failures Manager.
        
        Args:
            data_manager: Reference to TrackDataManager
            heater_manager: Reference to HeaterSystemManager (optional)
            ui_reference: Reference to the UI (optional, for updating signals/crossings)
        """
        self.data_manager = data_manager
        self.heater_manager = heater_manager
        self.ui = ui_reference
        
        # Track active failures for each block
        # Format: {block_number: failure_type}
        # failure_type can be: None, "track_circuit", "broken_rail", "power"
        self.active_failures = {}

        # Track which blocks have track elements in failure state
        # Format: {block_number: True/False}
        self.track_element_failures = {}

        # Store original occupancy values for blocks with broken rail failures
        # Format: {block_number: original_occupancy}
        self.broken_rail_original_occupancy = {}
        
        # Initialize all blocks with no failure
        for block in self.data_manager.blocks:
            self.active_failures[block.block_number] = None
            self.track_element_failures[block.block_number] = False
            if not hasattr(block, 'failure_mode'):
                block.failure_mode = None
            if not hasattr(block, 'traversable'):
                block.traversable = True
            if not hasattr(block, 'track_element_failed'):
                block.track_element_failed = False

    # -------------------------------------------------------------------------
    # FAILURE ACTIVATION
    # -------------------------------------------------------------------------
    
    def activate_track_circuit_failure(self, block_num):
        """
        Track Circuit Failure: Block cannot report occupancy, send beacon data, or be heated.
        
        Args:
            block_num (int): Block number to apply failure to
            
        Returns:
            bool: True if successful, False otherwise
        """
        if block_num < 1 or block_num > len(self.data_manager.blocks):
            print(f"❌ Invalid block number: {block_num}")
            return False
        
        block = self.data_manager.blocks[block_num - 1]
        
        # Clear any existing failure first
        self._clear_failure_internal(block_num)
        
        # Set failure mode
        self.active_failures[block_num] = "track_circuit"
        block.failure_mode = "track_circuit"
        
        # Disable beacon data (set all beacon bits to 0)
        if hasattr(block, 'beacon'):
            block.beacon = [0] * len(block.beacon)
        

        # Clear occupancy - track circuit cannot detect trains
        block.occupancy = 0
        # Break the heater (turns it off and marks as broken)
        if self.heater_manager:
            self.heater_manager.break_heater(block_num)
        
        print(f"⚠️ TRACK CIRCUIT FAILURE activated on Block {block_num}")
        print(f"   - Beacon data disabled")
        print(f"   - Heater broken and turned off")
        print(f"   - Occupancy reporting disabled (block shows as unoccupied)")
        self._print_active_failures()
        return True
    
    def activate_broken_rail_failure(self, block_num):
        """
        Broken Railroad Failure: Track cannot be driven over.
        
        Args:
            block_num (int): Block number to apply failure to
            
        Returns:
            bool: True if successful, False otherwise
        """
        if block_num < 1 or block_num > len(self.data_manager.blocks):
            print(f"❌ Invalid block number: {block_num}")
            return False
        
        block = self.data_manager.blocks[block_num - 1]
        
        # Clear any existing failure first
        self._clear_failure_internal(block_num)
        
        # Set failure mode
        self.active_failures[block_num] = "broken_rail"
        block.failure_mode = "broken_rail"
        
        # Store original occupancy and mark block as occupied
        # This prevents trains from entering the broken section
        original_occupancy = getattr(block, 'occupancy', 0)
        self.broken_rail_original_occupancy[block_num] = original_occupancy
        block.occupancy = 1  # Mark as occupied to prevent train entry

        # Mark block as non-traversable (this should be checked by train controller)
        block.traversable = False
        
        print(f"⚠️ BROKEN RAIL FAILURE activated on Block {block_num}")
        print(f"   - Block marked as non-traversable")
        print(f"   - Trains cannot drive over this block")
        print(f"   - Block set to occupied (occupancy = 1)")
        return True
    
    def activate_power_failure(self, block_num):
        """
        Power Failure: Block cannot report occupancy, send beacon data, be heated,
        and any track elements (Signal, Crossing) are turned off.
        
        Args:
            block_num (int): Block number to apply failure to
            
        Returns:
            bool: True if successful, False otherwise
        """
        if block_num < 1 or block_num > len(self.data_manager.blocks):
            print(f"❌ Invalid block number: {block_num}")
            return False
        
        block = self.data_manager.blocks[block_num - 1]
        
        # Clear any existing failure first
        self._clear_failure_internal(block_num)
        
        # Set failure mode
        self.active_failures[block_num] = "power"
        block.failure_mode = "power"
        

        # Clear occupancy - track circuit cannot detect trains
        block.occupancy = 0
        # Disable beacon data
        if hasattr(block, 'beacon'):
            block.beacon = [0] * len(block.beacon)
        
        # Break the heater
        if self.heater_manager:
            self.heater_manager.break_heater(block_num)
        
        # Turn off traffic lights (signals)
        if hasattr(block, 'traffic_light_state'):
            block.traffic_light_state = 0  # Off state
        
        # Deactivate crossing
        if hasattr(block, 'crossing'):
            block.crossing = False  # Inactive

        # Check if this block has track elements (signals or crossings)
        # and mark them as failed for UI display
        has_track_element = (hasattr(block, 'traffic_light_state') or 
                             hasattr(block, 'crossing') or 
                             hasattr(block, 'crossing_state'))
        if has_track_element:
            self.track_element_failures[block_num] = True
            block.track_element_failed = True
        
        print(f"⚠️ POWER FAILURE activated on Block {block_num}")
        print(f"   - Beacon data disabled")
        print(f"   - Occupancy reporting disabled (block shows as unoccupied)")
        print(f"   - Heater broken and turned off")
        print(f"   - Traffic lights turned off")
        print(f"   - Railroad crossing deactivated")
        return True

    # -------------------------------------------------------------------------
    # FAILURE DEACTIVATION (REPAIR)
    # -------------------------------------------------------------------------
    
    def clear_failure(self, block_num):
        """
        Clear any active failure on a block (repair the block).
        
        Args:
            block_num (int): Block number to repair
            
        Returns:
            bool: True if successful, False otherwise
        """
        if block_num < 1 or block_num > len(self.data_manager.blocks):
            print(f"❌ Invalid block number: {block_num}")
            return False
        
        return self._clear_failure_internal(block_num)
    
    def _clear_failure_internal(self, block_num):
        """Internal method to clear failure without validation."""
        block = self.data_manager.blocks[block_num - 1]
        failure_type = self.active_failures.get(block_num)
        
        if failure_type is None:
            # No active failure, but still return success
            return True
        
        # Clear the failure
        self.active_failures[block_num] = None
        block.failure_mode = None
        
        # Restore block functionality based on failure type
        if failure_type in ["track_circuit", "power"]:
            # Fix the heater (doesn't turn it on, just makes it working)
            if self.heater_manager:
                self.heater_manager.fix_heater(block_num)
            
            # Beacon data will need to be re-sent (handled by system)
            # Don't reset beacon here as it may have valid data
        
        if failure_type == "broken_rail":
            # Restore traversability
            block.traversable = True
            # Restore original occupancy
            original_occupancy = self.broken_rail_original_occupancy.get(block_num, 0)
            block.occupancy = original_occupancy
            if block_num in self.broken_rail_original_occupancy:
                del self.broken_rail_original_occupancy[block_num]
        
        if failure_type == "power":
            # Signals and crossings will be restored by normal system operation
            # Don't force them on, let the system control them normally
            # Clear track element failure status
            self.track_element_failures[block_num] = False
            block.track_element_failed = False
        
        print(f"✅ Failure cleared on Block {block_num} (was: {failure_type})")
        return True
    
    def clear_all_failures(self):
        """Clear all active failures on all blocks."""
        count = 0
        for block_num in list(self.active_failures.keys()):
            if self.active_failures[block_num] is not None:
                self.clear_failure(block_num)
                count += 1
        
        print(f"✅ Cleared {count} active failure(s)")
        return count

    # -------------------------------------------------------------------------
    # FAILURE STATUS QUERIES
    # -------------------------------------------------------------------------
    
    def get_failure_status(self, block_num):
        """
        Get the failure status of a specific block.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            str or None: Failure type or None if no failure
        """
        return self.active_failures.get(block_num)
    
    def has_failure(self, block_num):
        """
        Check if a block has any active failure.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if block has a failure, False otherwise
        """
        return self.active_failures.get(block_num) is not None
    
    def get_all_failures(self):
        """
        Get all active failures in the system.
        
        Returns:
            dict: {block_number: failure_type} for blocks with active failures
        """
        return {k: v for k, v in self.active_failures.items() if v is not None}
    
    def can_send_beacon(self, block_num):
        """
        Check if a block can send beacon data.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if beacon can be sent, False otherwise
        """
        failure = self.active_failures.get(block_num)
        return failure not in ["track_circuit", "power"]

    def can_report_occupancy(self, block_num):
        """
        Check if a block can report occupancy.
        Track circuit and power failures prevent occupancy detection.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if occupancy can be reported, False otherwise
        """
        failure = self.active_failures.get(block_num)
        return failure not in ["track_circuit", "power"]
    
    def can_heat(self, block_num):
        """
        Check if a block's heater can function.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if heater can function, False otherwise
        """
        failure = self.active_failures.get(block_num)
        return failure not in ["track_circuit", "power"]
    
    def is_traversable(self, block_num):
        """
        Check if a block can be driven over.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if block is traversable, False otherwise
        """
        failure = self.active_failures.get(block_num)
        if failure == "broken_rail":
            return False
        
        # Also check the block's traversable attribute
        block = self.data_manager.blocks[block_num - 1]
        return getattr(block, 'traversable', True)
    
    def has_power(self, block_num):
        """
        Check if a block has power.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if block has power, False otherwise
        """
        failure = self.active_failures.get(block_num)
        return failure != "power"

    # -------------------------------------------------------------------------
    def is_track_element_failed(self, block_num):
        """
        Check if a track element (signal/crossing) is in failure state.
        This happens when a power failure occurs on a block with track elements.
        
        Args:
            block_num (int): Block number to check
            
        Returns:
            bool: True if track element is failed, False otherwise
        """
        return self.track_element_failures.get(block_num, False)

    # UI INTEGRATION
    # -------------------------------------------------------------------------
    
    def get_failure_display_text(self, block_num):
        """
        Get display text for UI showing failure status.
        
        Args:
            block_num (int): Block number
            
        Returns:
            str: Failure status text for display
        """
        failure = self.active_failures.get(block_num)
        
        if failure is None:
            return "✅ OK"
        elif failure == "track_circuit":
            return "⚠️ TRACK CIRCUIT"
        elif failure == "broken_rail":
            return "🚫 BROKEN RAIL"
        elif failure == "power":
            return "⚡ POWER FAILURE"
        else:
            return "❓ UNKNOWN"
    
    def get_failure_color(self, block_num):
        """
        Get color code for failure status.
        
        Args:
            block_num (int): Block number
            
        Returns:
            str: Color name for display
        """
        failure = self.active_failures.get(block_num)
        
        if failure is None:
            return "green"
        elif failure == "track_circuit":
            return "orange"
        elif failure == "broken_rail":
            return "red"
        elif failure == "power":
            return "darkred"
        else:
            return "gray"
    
    def _print_active_failures(self):
        """Helper method to print active failures count."""
        failures = self.get_all_failures()
        if failures:
            print(f"   - Active failures: {len(failures)} block(s)")
        else:
            print(f"   - No other active failures")

    def print_failure_summary(self):
        """Print a summary of all active failures to console."""
        failures = self.get_all_failures()
        
        if not failures:
            print("\n✅ No active failures in the system")
            return
        
        print("\n" + "="*60)
        print("ACTIVE FAILURE SUMMARY")
        print("="*60)
        
        for block_num, failure_type in failures.items():
            display = self.get_failure_display_text(block_num)
            print(f"Block {block_num:2d}: {display}")
            
            # Show specific effects
            if failure_type == "track_circuit":
                print(f"  └─ Effects: No occupancy detection, No beacon, No heating")
            elif failure_type == "broken_rail":
                print(f"  └─ Effects: Not traversable, Block occupied")
            elif failure_type == "power":
                print(f"  └─ Effects: No occupancy detection, No beacon, No heating, Track elements show FAILURE")
        
        print("="*60 + "\n")