from datetime import datetime

def run_plc_cycle(data, log_callback):
    """
    PLC with CTC override logic (no sectioning, bidirectional CTC authority)
    """
    # Track previous state
    if not hasattr(run_plc_cycle, 'last_occupancy_state'):
        run_plc_cycle.last_occupancy_state = {}
    
    # Get occupancy
    current_occupancy = {}
    occupied_blocks = []
    
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info.get("number", "0")
        is_occupied = block_info.get("occupied", False)
        
        try:
            block_num_int = int(block_num)
            current_occupancy[block_num_int] = is_occupied
            if is_occupied:
                occupied_blocks.append(block_num_int)
        except ValueError:
            pass
    
    occupied_blocks.sort()
    
    # Check occupancy change
    occupancy_changed = (current_occupancy != run_plc_cycle.last_occupancy_state)
    run_plc_cycle.last_occupancy_state = current_occupancy.copy()
    
    current_line = data.current_line
    #print(f"\nPLC CYCLE for {current_line} line")
    #print(f"Occupied blocks: {occupied_blocks}")
    
    # ==============================================
    # Find blocks where CTC suggests authority 3
    # ==============================================
    ctc_override_blocks = []
    if current_line in data.suggested_authority:
        for block_num, suggested_auth in data.suggested_authority[current_line].items():
            try:
                if int(suggested_auth) == 3:
                    ctc_override_blocks.append(int(block_num))
            except ValueError:
                pass
    
    ctc_override_blocks.sort()
    #if ctc_override_blocks:
        #print(f"CTC override blocks (suggested auth=3): {ctc_override_blocks}")
    
    # Initialize commanded speed dict if needed
    if current_line not in data.commanded_speed:
        data.commanded_speed[current_line] = {}
    
    # Initialize commanded authority dict if needed
    if current_line not in data.commanded_authority:
        data.commanded_authority[current_line] = {}
    
    # ==============================================
    # Clear user-set authorities when train passes over them
    # ==============================================
    apply_commanded_authority_overrides(data, log_callback)
    
    # Create a list to track blocks with user overrides
    user_override_blocks = []
    
    # Process each block
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info["number"]
        
        try:
            block_num_int = int(block_num)
        except ValueError:
            continue
        
        # Default values
        default_authority = 3
        default_speed = 25
        final_authority = default_authority

        # ==============================================
        # Check for user-set commanded authority override FIRST
        # ==============================================
        user_override_auth = None
        if hasattr(data, 'user_commanded_authority'):
            if current_line in data.user_commanded_authority:
                if block_num in data.user_commanded_authority[current_line]:
                    user_override_auth = data.user_commanded_authority[current_line][block_num]
        
        # ==============================================
        # Apply user authority override (takes ABSOLUTE precedence)
        # ==============================================
        if user_override_auth is not None:
            try:
                user_auth_int = int(user_override_auth)
                final_authority = user_auth_int
                
                # Update data with user authority
                data.update_block_in_track_data(block_num, "authority", final_authority)
                data.commanded_authority[current_line][block_num] = str(final_authority)
                
                # Track this as a user override block
                user_override_blocks.append(block_num)
                
                # Continue to next block - SKIP all PLC calculations
                continue
            except ValueError:
                pass  # If invalid, fall through to PLC calculations
            
        # ==============================================
        # ONLY RUN PLC LOGIC IF NO USER OVERRIDE
        # ==============================================
        
        # Check if block itself is occupied
        is_block_occupied = block_num_int in occupied_blocks
        
        if not is_block_occupied and occupied_blocks:
            # Find nearest occupied block in BOTH directions
            nearest_ahead = None
            nearest_behind = None
            min_ahead_distance = float('inf')
            min_behind_distance = float('inf')
            
            for occupied in occupied_blocks:
                if occupied > block_num_int:  # Blocks AHEAD
                    distance = occupied - block_num_int
                    if distance < min_ahead_distance:
                        min_ahead_distance = distance
                        nearest_ahead = occupied
                elif occupied < block_num_int:  # Blocks BEHIND
                    distance = block_num_int - occupied
                    if distance < min_behind_distance:
                        min_behind_distance = distance
                        nearest_behind = occupied
            
            # Use the closest occupied block in EITHER direction
            if nearest_ahead is not None or nearest_behind is not None:
                if min_ahead_distance <= min_behind_distance:
                    # Closest occupied is ahead
                    if min_ahead_distance == 1:
                        final_authority = 0
                    elif min_ahead_distance == 2:
                        final_authority = 1
                    elif min_ahead_distance == 3:
                        final_authority = 2
                else:
                    # Closest occupied is behind (BIDIRECTIONAL)
                    if min_behind_distance == 1:
                        final_authority = 0
                    elif min_behind_distance == 2:
                        final_authority = 1
                    elif min_behind_distance == 3:
                        final_authority = 2
        
        # ==============================================
        # Apply CTC override logic with bidirectional pattern
        # ==============================================
        if ctc_override_blocks:
            final_authority, updated_ctc_override_blocks = apply_bidirectional_ctc_override_logic(
                data, current_line, block_num_int, final_authority, 
                occupied_blocks, ctc_override_blocks
            )
            # Update the list for consistency
            ctc_override_blocks = updated_ctc_override_blocks
        
        # Update data
        data.update_block_in_track_data(block_num, "authority", final_authority)
        
        # Store commanded values for later speed override processing
        data.commanded_authority[current_line][block_num] = str(final_authority)
        
    # ==============================================
    # Apply CTC and Commanded Speed Overrides
    # ==============================================
    # Apply CTC speed overrides first
    apply_ctc_speed_overrides(data, log_callback)
    
    # Apply commanded speed overrides second (user-set speeds)
    apply_commanded_speed_overrides(data, log_callback)
    
    # Now set default speed for any blocks that don't have a speed yet
    # INCLUDING blocks with user authority overrides
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info["number"]
        block_num_str = str(block_num)
        
        # If this block doesn't have a commanded speed yet, set default
        if block_num_str not in data.commanded_speed[current_line]:
            data.commanded_speed[current_line][block_num_str] = "25"
            data.update_block_in_track_data(block_num, "speed", 25)
            
    # ==============================================
    # Send updated commanded values to track model for occupied blocks
    # ==============================================
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info["number"]
        block_num_str = str(block_num)
        
        # Check if block is occupied
        if block_info.get("occupied", False):
            # Get current commanded values
            cmd_speed = data.commanded_speed[current_line].get(block_num_str, "25")
            cmd_auth = data.commanded_authority[current_line].get(block_num_str, "3")
            
            # Send to track model
            if hasattr(data, 'app') and data.app:
                try:
                    data.app.send_commanded_to_track_model(
                        current_line, block_num_str, cmd_speed, cmd_auth
                    )
                except Exception as e:
                    print(f"  Error sending block {block_num} to track model: {e}")
    
    # Trigger UI update
    for callback in data.on_data_update:
            callback()
        
    # Log occupancy changes
    if occupancy_changed and occupied_blocks:
        if log_callback:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            occupied_str = ", ".join(str(b) for b in sorted(occupied_blocks))
            log_callback(f"{current_time} PLC: Occupied blocks: {occupied_str}")
    
    #print("PLC cycle complete\n")

def apply_bidirectional_ctc_override_logic(data, current_line, block_num_int, final_authority, occupied_blocks, ctc_override_blocks):
    """
    Apply CTC override authority logic with BIDIRECTIONAL pattern.
    Returns: tuple of (updated_final_authority, updated_ctc_override_blocks)
    """
    if not ctc_override_blocks:
        return final_authority, ctc_override_blocks
    
    # FIRST: Check if train has reached any CTC stopping point
    ctc_overrides_to_clear = []
    
    for ctc_block in ctc_override_blocks:
        # BIDIRECTIONAL: Check both forward and backward directions
        # Forward stopping point: ctc_block + 3
        # Backward stopping point: ctc_block - 3
        forward_stopping = ctc_block + 3
        backward_stopping = ctc_block - 3
        
        # Check if either stopping block is occupied
        forward_stopping_key = f"Block {forward_stopping}"
        backward_stopping_key = f"Block {backward_stopping}"
        
        train_reached_stop = False
        
        # Check forward direction
        if forward_stopping_key in data.filtered_blocks:
            if data.filtered_blocks[forward_stopping_key].get("occupied", False):
                train_reached_stop = True
        
        # Check backward direction
        if backward_stopping_key in data.filtered_blocks:
            if data.filtered_blocks[backward_stopping_key].get("occupied", False):
                train_reached_stop = True
        
        # Also check if train is on the CTC block itself (for immediate stopping)
        ctc_block_key = f"Block {ctc_block}"
        if ctc_block_key in data.filtered_blocks:
            if data.filtered_blocks[ctc_block_key].get("occupied", False):
                train_reached_stop = True
        
        if train_reached_stop:
            # Train has reached destination! Clear this CTC override
            ctc_overrides_to_clear.append(ctc_block)
    
    # Actually delete from suggested_authority
    if ctc_overrides_to_clear and current_line in data.suggested_authority:
        for ctc_block in ctc_overrides_to_clear:
            block_str = str(ctc_block)
            if block_str in data.suggested_authority[current_line]:
                del data.suggested_authority[current_line][block_str]
    
    # Filter active CTC blocks
    if current_line in data.suggested_authority:
        active_ctc_blocks = []
        for ctc_block in ctc_override_blocks:
            if ctc_block in ctc_overrides_to_clear:
                continue
                
            block_str = str(ctc_block)
            if block_str in data.suggested_authority[current_line]:
                suggested_auth = data.suggested_authority[current_line][block_str]
                try:
                    if int(suggested_auth) == 3:
                        active_ctc_blocks.append(ctc_block)
                except ValueError:
                    pass
        
        ctc_override_blocks = active_ctc_blocks
    
    # Apply CTC override logic with BIDIRECTIONAL pattern
    # For each CTC override block, create authority gradient in BOTH directions:
    # CTC block: authority = 3
    # CTC block ±1: authority = 2
    # CTC block ±2: authority = 1
    # CTC block ±3: authority = 0
    # Beyond ±3: no CTC authority restriction
    
    for ctc_block in ctc_override_blocks:
        # Calculate distance in both directions
        forward_distance = block_num_int - ctc_block  # Positive if block is ahead of CTC
        backward_distance = ctc_block - block_num_int  # Positive if block is behind CTC
        
        # Determine which direction is relevant
        # Use the smaller absolute distance
        if abs(forward_distance) <= abs(backward_distance):
            distance = forward_distance
        else:
            distance = -backward_distance  # Negative for backward direction
        
        # Apply authority gradient based on absolute distance
        abs_distance = abs(distance)
        
        if abs_distance == 0:  # CTC block itself
            ctc_auth = 3
            final_authority = min(final_authority, ctc_auth)
        elif abs_distance == 1:  # CTC block ±1
            ctc_auth = 2
            final_authority = min(final_authority, ctc_auth)
        elif abs_distance == 2:  # CTC block ±2
            ctc_auth = 1
            final_authority = min(final_authority, ctc_auth)
        elif abs_distance == 3:  # CTC block ±3
            ctc_auth = 0
            final_authority = min(final_authority, ctc_auth)
        # Beyond ±3: no restriction from this CTC block
    
    return final_authority, ctc_override_blocks

def apply_ctc_speed_overrides(data, log_callback):
    """
    Apply CTC speed override logic:
    1. When CTC sends suggested speed, apply it to individual blocks
    2. Cap at maximum speed of 43.5 mph
    3. When block becomes unoccupied, reset to default (25 mph) AND clear suggested speed
    """
    current_line = data.current_line
    
    # Track which suggested speeds to clear
    suggested_speeds_to_clear = []
    
    # Check if CTC has suggested any speeds
    if current_line in data.suggested_speed:
        ctc_suggested_speeds = data.suggested_speed[current_line]
        
        # Process each block with CTC suggested speed
        for block_str, ctc_speed_str in ctc_suggested_speeds.items():
            try:
                block_num_int = int(block_str)
                block_key = f"Block {block_str}"
                
                # Check if user has already set speed for this block
                current_speed = data.commanded_speed[current_line].get(block_str, "25")
                
                # Only apply if current speed is default or different from CTC
                if current_speed == "25":
                    # Convert CTC speed from m/s to mph and cap at 43.5 mph
                    ctc_speed_mph = float(ctc_speed_str) * 2.23694
                    
                    if ctc_speed_mph > 43.5:
                        ctc_speed_mph = 43.5
                    
                    # Set commanded speed for this block
                    data.commanded_speed[current_line][block_str] = str(ctc_speed_mph)
                    data.update_block_in_track_data(block_num_int, "speed", ctc_speed_mph)
                    
                    # Send to Track Model if this block is occupied
                    if block_key in data.filtered_blocks:
                        if data.filtered_blocks[block_key].get("occupied", False):
                            commanded_auth = data.commanded_authority[current_line].get(block_str, "3")
                            if hasattr(data, 'app') and data.app:
                                data.app.send_commanded_to_track_model(
                                    current_line, block_str, 
                                    str(ctc_speed_mph), commanded_auth
                                )
                
                # Check if block should have its CTC speed cleared
                if block_key in data.filtered_blocks:
                    if not data.filtered_blocks[block_key].get("occupied", False):
                        # Block is unoccupied - mark for clearing
                        suggested_speeds_to_clear.append(block_str)
                
            except (ValueError, TypeError) as e:
                print(f"  Error processing CTC speed for block {block_str}: {e}")
    
    # Actually clear the suggested speeds
    if suggested_speeds_to_clear and current_line in data.suggested_speed:
        for block_str in suggested_speeds_to_clear:
            if block_str in data.suggested_speed[current_line]:
                del data.suggested_speed[current_line][block_str]
                # Reset to default speed
                data.commanded_speed[current_line][block_str] = "25"
                try:
                    block_num_int = int(block_str)
                    data.update_block_in_track_data(block_num_int, "speed", 25)
                except ValueError:
                    pass

def apply_commanded_speed_overrides(data, log_callback):
    """
    Apply commanded speed override logic:
    1. When user sets commanded speed, apply it to individual blocks
    2. When block becomes unoccupied, reset to default (25 mph)
    """
    current_line = data.current_line
    
    # Track which blocks have user-set commanded speeds
    user_speed_blocks = []
    
    # First pass: identify blocks with user-set speeds
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info["number"]
        block_num_str = str(block_num)
        
        current_speed = data.commanded_speed[current_line].get(block_num_str, "25")
        
        # Check if this looks like a user-set speed (not default and not CTC)
        if current_speed != "25":
            # Check if it's not a CTC speed
            if current_line in data.suggested_speed and block_num_str in data.suggested_speed[current_line]:
                # This is a CTC speed
                continue
            
            # This might be a user-set speed
            try:
                speed_float = float(current_speed)
                # Cap at maximum speed of 43.5 mph
                if speed_float > 43.5:
                    speed_float = 43.5
                    current_speed = "43.5"
                    data.commanded_speed[current_line][block_num_str] = current_speed
                
                user_speed_blocks.append(block_num_str)
            except (ValueError, TypeError):
                continue
    
    # Second pass: check if user-speed blocks should be reset
    blocks_to_reset = []
    
    for block_num_str in user_speed_blocks:
        block_key = f"Block {block_num_str}"
        
        if block_key in data.filtered_blocks:
            # Check if block is occupied
            is_occupied = data.filtered_blocks[block_key].get("occupied", False)
            
            if not is_occupied:
                # Block is unoccupied - reset to default
                blocks_to_reset.append(block_num_str)
    
    # Reset blocks to default speed
    for block_num_str in blocks_to_reset:
        data.commanded_speed[current_line][block_num_str] = "25"
        try:
            block_num_int = int(block_num_str)
            data.update_block_in_track_data(block_num_int, "speed", 25)
        except ValueError:
            pass

def apply_commanded_authority_overrides(data, log_callback):
    """
    Apply user-set commanded authority overrides:
    1. When user sets commanded authority, it overrides PLC calculations
    2. The override persists until train passes over the block
    3. When block becomes occupied then unoccupied, clear the override
    """
    current_line = data.current_line
    
    # Initialize user_commanded_authority if it doesn't exist
    if not hasattr(data, 'user_commanded_authority'):
        data.user_commanded_authority = {}
    
    if current_line not in data.user_commanded_authority:
        data.user_commanded_authority[current_line] = {}
    
    # Initialize block_override_occupancy_tracker if it doesn't exist
    if not hasattr(data, 'block_override_occupancy_tracker'):
        data.block_override_occupancy_tracker = {}
    
    if current_line not in data.block_override_occupancy_tracker:
        data.block_override_occupancy_tracker[current_line] = {}
    
    # Get current occupancy
    occupied_blocks = []
    for block_key, block_info in data.filtered_blocks.items():
        if block_info.get("occupied", False):
            try:
                block_num = block_info.get("number", "0")
                block_num_int = int(block_num)
                occupied_blocks.append(block_num_int)
            except ValueError:
                pass
    
    # Track occupancy changes and clear overrides when train passes
    blocks_to_clear = []
    
    for block_num_str in list(data.user_commanded_authority[current_line].keys()):
        try:
            block_num_int = int(block_num_str)
            block_key = f"Block {block_num_str}"
            
            # Get current occupancy state
            is_occupied = block_num_int in occupied_blocks
            
            # Initialize tracking if not exists
            if block_num_str not in data.block_override_occupancy_tracker[current_line]:
                data.block_override_occupancy_tracker[current_line][block_num_str] = {
                    'was_occupied': is_occupied,
                    'has_been_occupied': is_occupied
                }
            else:
                tracker = data.block_override_occupancy_tracker[current_line][block_num_str]
                previous_occupied = tracker['was_occupied']
                
                # Update tracker
                tracker['was_occupied'] = is_occupied
                if is_occupied:
                    tracker['has_been_occupied'] = True
                
                # Clear override if: block was occupied and is now unoccupied
                if previous_occupied and not is_occupied:
                    blocks_to_clear.append(block_num_str)
                    
                    # Send default authority to track model
                    default_speed = data.commanded_speed[current_line].get(block_num_str, "25")
                    if hasattr(data, 'app') and data.app:
                        data.app.send_commanded_to_track_model(
                            current_line, block_num_str, default_speed, "3"
                        )
        
        except (ValueError, TypeError) as e:
            print(f"  Error processing authority override for block {block_num_str}: {e}")
    
    # Clear the overrides
    for block_num_str in blocks_to_clear:
        if block_num_str in data.user_commanded_authority[current_line]:
            del data.user_commanded_authority[current_line][block_num_str]
        
        if block_num_str in data.block_override_occupancy_tracker[current_line]:
            del data.block_override_occupancy_tracker[current_line][block_num_str]

def set_commanded_authority_override(data, track, block, authority):
    """
    Set a user-commanded authority override for a specific block.
    This will persist until the train passes over the block.
    """
    # Initialize data structures if needed
    if not hasattr(data, 'user_commanded_authority'):
        data.user_commanded_authority = {}
    
    if track not in data.user_commanded_authority:
        data.user_commanded_authority[track] = {}
    
    if not hasattr(data, 'block_override_occupancy_tracker'):
        data.block_override_occupancy_tracker = {}
    
    if track not in data.block_override_occupancy_tracker:
        data.block_override_occupancy_tracker[track] = {}
    
    # Validate authority value
    try:
        auth_int = int(authority)
        if auth_int < 0 or auth_int > 3:
            print(f"Error: Authority must be between 0 and 3, got {authority}")
            return False
    except ValueError:
        print(f"Error: Invalid authority value '{authority}' - must be integer")
        return False
    
    # Set the override
    data.user_commanded_authority[track][block] = authority
    
    # Initialize occupancy tracker for this block
    data.block_override_occupancy_tracker[track][block] = {
        'was_occupied': False,
        'has_been_occupied': False
    }
    
    # Immediately update the UI if possible
    if hasattr(data, 'command_authority_override_callback'):
        try:
            data.command_authority_override_callback(track, block, authority)
        except Exception as e:
            print(f"Warning: Could not update UI callback: {e}")
    
    return True