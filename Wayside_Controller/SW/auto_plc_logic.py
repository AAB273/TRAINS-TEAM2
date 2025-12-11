from datetime import datetime

def run_plc_cycle(data, log_callback):
    """
    PLC with CTC override logic
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
    
    # Enable filter if needed
    plc_sections = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    
    if not data.plc_filter_active:
        data.enable_plc_filter(plc_sections)
        if log_callback:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_callback(f"{current_time} PLC: K-Y section filtering enabled")
    
    # Check if section N has occupied blocks
    blocks_in_section_N = data.get_blocks_in_section(data.current_line, 'N')
    section_N_occupied = False
    for block_num in blocks_in_section_N:
        block_key = f"Block {block_num}"
        if block_key in data.filtered_blocks:
            if data.filtered_blocks[block_key].get("occupied", False):
                section_N_occupied = True
                break
    
    current_line = data.current_line
    #print(f"\nPLC CYCLE for {current_line} line")
    #print(f"Occupied blocks: {occupied_blocks}")
    #print(f"Section N occupied: {section_N_occupied}")
    
    # ==============================================
    # NEW: Find blocks where CTC suggests authority 3
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
    
    # ==============================================
    # FIX: Run Section N logic BEFORE processing blocks
    # ==============================================
    section_n_dynamic_auth = {}  # Store dynamic authorities for Section N blocks
    
    # Apply Section N dynamic logic if section N has occupied block
    if section_N_occupied:
        section_n_dynamic_auth = apply_section_n_authority_logic(data, log_callback)
    
    # ==============================================
    # FIX: Run switch control ONCE, before processing blocks
    # ==============================================
    control_switches_automatically(data, log_callback)
    control_lights_automatically(data, log_callback)
    control_railway_crossings(data, log_callback)

    
    # Initialize commanded speed dict if needed
    if current_line not in data.commanded_speed:
        data.commanded_speed[current_line] = {}
    
    # Initialize commanded authority dict if needed
    if current_line not in data.commanded_authority:
        data.commanded_authority[current_line] = {}
    
    # ==============================================
    # NEW: Clear user-set authorities when train passes over them
    # This should be BEFORE processing blocks so we know which overrides are active
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
        # MODIFIED: Check for user-set commanded authority override FIRST
        # ==============================================
        user_override_auth = None
        if hasattr(data, 'user_commanded_authority'):
            if current_line in data.user_commanded_authority:
                if block_num in data.user_commanded_authority[current_line]:
                    user_override_auth = data.user_commanded_authority[current_line][block_num]
                    print(f"  User Authority Override: Block {block_num} -> {user_override_auth}")
        
        # ==============================================
        # MODIFIED: Apply user authority override (takes ABSOLUTE precedence)
        # ==============================================
        if user_override_auth is not None:
            try:
                user_auth_int = int(user_override_auth)
                final_authority = user_auth_int
                print(f"  User Authority APPLIED: Block {block_num} = {final_authority}")
                
                # Update data with user authority
                data.update_block_in_track_data(block_num, "authority", final_authority)
                data.commanded_authority[current_line][block_num] = str(final_authority)
                
                # Track this as a user override block
                user_override_blocks.append(block_num)
                
                # Continue to next block - SKIP all PLC calculations
                continue  # Skip the rest of the PLC calculations for this block
            except ValueError:
                pass  # If invalid, fall through to PLC calculations
            
        # ==============================================
        # ONLY RUN PLC LOGIC IF NO USER OVERRIDE
        # ==============================================
        
        # Check if block itself is occupied
        is_block_occupied = block_num_int in occupied_blocks
        
        if not is_block_occupied and occupied_blocks:
            # Find nearest occupied block AHEAD
            nearest_ahead = None
            min_distance = float('inf')
            
            for occupied in occupied_blocks:
                if occupied > block_num_int:  # Only blocks AHEAD
                    distance = occupied - block_num_int
                    if distance < min_distance:
                        min_distance = distance
                        nearest_ahead = occupied
            
            if nearest_ahead is not None:
                # Authority based on distance to nearest occupied block ahead
                if min_distance == 1:
                    final_authority = 0
                elif min_distance == 2:
                    final_authority = 1
                elif min_distance == 3:
                    final_authority = 2
        
        # ==============================================
        # NEW: Apply CTC override logic using extracted function
        # ==============================================
        if ctc_override_blocks:
            final_authority, updated_ctc_override_blocks = apply_ctc_override_logic(
                data, current_line, block_num_int, final_authority, 
                occupied_blocks, ctc_override_blocks
            )
            # Update the list for consistency
            ctc_override_blocks = updated_ctc_override_blocks
        
        # ==============================================
        # FIX: Apply Section N authorities AFTER CTC logic
        # ==============================================
        if section_N_occupied:
            # Check if this block has a dynamic authority from Section N
            if block_num in section_n_dynamic_auth:
                dynamic_auth = section_n_dynamic_auth[block_num]
                final_authority = min(final_authority, dynamic_auth)  # Use most restrictive
            
            # Apply the fixed authority rules for specific blocks (74-76, 98-100)
            if block_num in ['74', '75', '76', '98', '99', '100']:
                # Get Section N fixed authority for this block
                section_N_fixed_auth = None
                if block_num in ['74', '98']:
                    section_N_fixed_auth = 2
                elif block_num in ['75', '99']:
                    section_N_fixed_auth = 1
                elif block_num in ['76', '100']:
                    section_N_fixed_auth = 0
                
                if section_N_fixed_auth is not None:
                    # Use the smaller (more restrictive) authority
                    old_auth = final_authority
                    final_authority = min(final_authority, section_N_fixed_auth)
                    #print(f"  Section N Fixed: Block {block_num} auth = min({old_auth}, {section_N_fixed_auth}) = {final_authority}")
        
        # ==============================================
        # IMPORTANT: Set default speed here before speed overrides
        # ==============================================
        final_speed = default_speed
        
        # Update data
        data.update_block_in_track_data(block_num, "authority", final_authority)
        
        # Store commanded values for later speed override processing
        data.commanded_authority[current_line][block_num] = str(final_authority)
        
    # ==============================================
    # FIX: Apply CTC and Commanded Speed Overrides AFTER all blocks processed
    # ==============================================
    #print("\n[SPEED OVERRIDES]")
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
    # Now send updated commanded values to track model for occupied blocks
    # INCLUDING blocks with user authority overrides
    # ==============================================
    #print("\n[SENDING TO TRACK MODEL]")
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info["number"]
        block_num_str = str(block_num)
        
        # Check if block is occupied
        if block_info.get("occupied", False):
            # Get current commanded values
            # For user override blocks, use the user authority
            # For others, use the PLC-calculated authority
            cmd_speed = data.commanded_speed[current_line].get(block_num_str, "25")
            cmd_auth = data.commanded_authority[current_line].get(block_num_str, "3")
            
            # Send to track model
            if hasattr(data, 'app') and data.app:
                try:
                    data.app.send_commanded_to_track_model(
                        current_line, block_num_str, cmd_speed, cmd_auth
                    )
                    print(f"  Block {block_num}: Speed={cmd_speed} mph, Authority={cmd_auth}")
                except Exception as e:
                    print(f"  Error sending block {block_num} to track model: {e}")
    
    # Apply filter
    data.apply_plc_filter()
    
    # Trigger UI update
    for callback in data.on_data_update:
            callback()
        
    # Log occupancy changes
    if occupancy_changed and occupied_blocks:
        if log_callback:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            occupied_str = ", ".join(str(b) for b in sorted(occupied_blocks))
            log_callback(f"{current_time} PLC: Occupied blocks: {occupied_str}")
    
    print("PLC cycle complete\n")


def control_switches_automatically(data, log_callback):
    """
    Switch control - ALWAYS set switches based on current state
    """
    current_line = data.current_line
    
    # Check if train in section N
    blocks_in_section_N = data.get_blocks_in_section(current_line, 'N')
    train_in_section_N = False
    
    for block_num in blocks_in_section_N:
        block_key = f"Block {block_num}"
        if block_key in data.filtered_blocks:
            if data.filtered_blocks[block_key].get("occupied", False):
                train_in_section_N = True
                break
        
    # Switch 85 - Check if manually set
    switch_85_name = "Switch 85"
    switch_85_id = "85"
    
    if switch_85_name in data.filtered_switch_positions:
        # FIX: UNCOMMENT THIS AND ADD maintenance_mode CHECK
        if data.maintenance_mode and hasattr(data, 'manual_switches') and switch_85_id in data.manual_switches:
            # Don't control this switch - return early
            return train_in_section_N
        else:
            switch_85 = data.filtered_switch_positions[switch_85_name]
            current_pos = switch_85.get("direction", "85-86")
            
            if train_in_section_N:
                desired_pos = "85-86"
                condition_text = f"N -> O"
            else:
                desired_pos = "100-85"
                condition_text = f"Q -> N"
            
            # Only update if position actually needs to change
            if current_pos != desired_pos:
                #print(f"[DEBUG] Switch 85: {current_pos} -> {desired_pos}")
                # UPDATE BOTH DIRECTION AND CONDITION
                data.update_track_data("switch_positions", switch_85_name, "direction", desired_pos)
                data.update_track_data("switch_positions", switch_85_name, "condition", condition_text)
            #else:
                #print(f"[DEBUG] Switch 85: Already at {desired_pos}")
    
    # Switch 76 - Check if manually set
    switch_76_name = "Switch 76"
    switch_76_id = "76"
    
    if switch_76_name in data.filtered_switch_positions:
        # FIX: UNCOMMENT THIS AND ADD maintenance_mode CHECK
        if data.maintenance_mode and hasattr(data, 'manual_switches') and switch_76_id in data.manual_switches:
            #print(f"[DEBUG] Switch 76: Skipping - manually set by user")
            # Don't control this switch - return early
            return train_in_section_N
        else:
            switch_76 = data.filtered_switch_positions[switch_76_name]
            current_pos = switch_76.get("direction", "76-77")
            
            if train_in_section_N:
                desired_pos = "77-101"
                condition_text = f"N -> R"
            else:
                desired_pos = "76-77"
                condition_text = f"M -> N"
            
            if current_pos != desired_pos:
                #print(f"[DEBUG] Switch 76: {current_pos} -> {desired_pos}")
                # UPDATE BOTH DIRECTION AND CONDITION
                data.update_track_data("switch_positions", switch_76_name, "direction", desired_pos)
                data.update_track_data("switch_positions", switch_76_name, "condition", condition_text)
            #else:
                #print(f"[DEBUG] Switch 76: Already at {desired_pos}")
    
    #print("[DEBUG] Switch control complete")
    return train_in_section_N


def apply_section_n_authority_logic(data, log_callback):
    """
    Apply authority logic for Section N when it has occupied blocks.
    For each occupied block in section N, set authorities for blocks 
    both behind and ahead within the same section.
    
    Returns: dict of {block_num: authority} for Section N blocks
    """
    current_line = data.current_line
    blocks_in_section_N = data.get_blocks_in_section(current_line, 'N')
    
    if not blocks_in_section_N:
        #print("[DEBUG] No Section N blocks found")
        return {}
    
    # Find occupied blocks within section N
    occupied_n_blocks = []
    for block_num in blocks_in_section_N:
        block_key = f"Block {block_num}"
        if block_key in data.filtered_blocks:
            if data.filtered_blocks[block_key].get("occupied", False):
                occupied_n_blocks.append(block_num)
    
    if not occupied_n_blocks:
        #print("[DEBUG] No occupied blocks in Section N")
        return {}
    
    #print(f"[DEBUG] Section N blocks: {blocks_in_section_N}")
    #print(f"[DEBUG] Occupied blocks in Section N: {occupied_n_blocks}")
    
    # Track all authority modifications
    authority_updates = {}
    
    # Process each occupied block in section N
    for occupied_block in occupied_n_blocks:
        #print(f"[DEBUG] Processing occupied block {occupied_block} in Section N")
        
        # Get track position for the occupied block
        occupied_block_key = f"Block {occupied_block}"
        if occupied_block_key not in data.filtered_blocks:
            #print(f"[DEBUG] Could not find block {occupied_block} in filtered blocks")
            continue
            
        occupied_pos = data.filtered_blocks[occupied_block_key].get("track_position", 0)
        #print(f"[DEBUG]   Block {occupied_block} track position: {occupied_pos}")
        
        # Create a list of blocks with their positions for this section
        blocks_with_positions = []
        for block_num in blocks_in_section_N:
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                pos = data.filtered_blocks[block_key].get("track_position", 0)
                blocks_with_positions.append((block_num, pos))
        
        # Sort blocks by track position (ascending - lower position is behind)
        blocks_with_positions.sort(key=lambda x: x[1])
        
        # Find index of occupied block in sorted-by-position list
        occupied_idx = -1
        for i, (block_num, pos) in enumerate(blocks_with_positions):
            if str(block_num) == str(occupied_block):
                occupied_idx = i
                break
        
        if occupied_idx == -1:
            #print(f"[DEBUG] Could not find block {occupied_block} in position-sorted list")
            continue
        
        #print(f"[DEBUG]   Blocks sorted by position: {blocks_with_positions}")
        #print(f"[DEBUG]   Occupied block index: {occupied_idx}")
        
        # 1. Check blocks BEHIND occupied block (lower track positions)
        #print(f"[DEBUG]   Checking blocks BEHIND block {occupied_block}...")
        for i in range(0, 5):  # Check up to 4 blocks behind (including occupied block)
            behind_idx = occupied_idx - i
            if behind_idx >= 0:
                block_behind, behind_pos = blocks_with_positions[behind_idx]
                block_behind_str = str(block_behind)
                
                # Authority based on distance behind
                # Occupied block (i=0): auth = 0
                # 1 block behind (i=1): auth = 0
                # 2 blocks behind (i=2): auth = 1
                # 3 blocks behind (i=3): auth = 2
                # 4+ blocks behind (i=4): auth = 3
                if i == 1:  # Occupied block or 1 block behind
                    auth_value = 0
                elif i == 2:  # 2 blocks behind
                    auth_value = 1
                elif i == 3:  # 3 blocks behind
                    auth_value = 2
                else:  # 4+ blocks behind
                    auth_value = 3
                
                # Only update if within section N blocks
                if block_behind_str in [str(b) for b in blocks_in_section_N]:
                    if block_behind_str not in authority_updates:
                        authority_updates[block_behind_str] = auth_value
                        #print(f"[DEBUG]     Block {block_behind} (pos {behind_pos}, {i} behind): auth={auth_value}")
                    else:
                        # Keep the most restrictive (lowest) authority
                        old_auth = authority_updates[block_behind_str]
                        authority_updates[block_behind_str] = min(authority_updates[block_behind_str], auth_value)
                        #if old_auth != authority_updates[block_behind_str]:
                            #print(f"[DEBUG]     Block {block_behind}: Updated from {old_auth} to {auth_value}")
        
        # 2. Check blocks AHEAD of occupied block (higher track positions)
        #print(f"[DEBUG]   Checking blocks AHEAD of block {occupied_block}...")
        for i in range(1, 5):  # Check up to 4 blocks ahead
            ahead_idx = occupied_idx + i
            if ahead_idx < len(blocks_with_positions):
                block_ahead, ahead_pos = blocks_with_positions[ahead_idx]
                block_ahead_str = str(block_ahead)
                
                # Authority based on distance ahead
                # 1 block ahead (i=1): auth = 0
                # 2 blocks ahead (i=2): auth = 1
                # 3 blocks ahead (i=3): auth = 2
                # 4+ blocks ahead (i=4): auth = 3
                if i == 1:  # 1 block ahead
                    auth_value = 0
                elif i == 2:  # 2 blocks ahead
                    auth_value = 1
                elif i == 3:  # 3 blocks ahead
                    auth_value = 2
                else:  # 4+ blocks ahead
                    auth_value = 3
                
                # Only update if within section N blocks
                if block_ahead_str in [str(b) for b in blocks_in_section_N]:
                    if block_ahead_str not in authority_updates:
                        authority_updates[block_ahead_str] = auth_value
                        print(f"[DEBUG]     Block {block_ahead} (pos {ahead_pos}, {i} ahead): auth={auth_value}")
                    else:
                        # Keep the most restrictive (lowest) authority
                        old_auth = authority_updates[block_ahead_str]
                        authority_updates[block_ahead_str] = min(authority_updates[block_ahead_str], auth_value)
                        if old_auth != authority_updates[block_ahead_str]:
                            print(f"[DEBUG]     Block {block_ahead}: Updated from {old_auth} to {auth_value}")
    
    #print(f"[DEBUG] Section N authority updates calculated: {authority_updates}")
    return authority_updates

def apply_ctc_speed_overrides(data, log_callback):
    """
    Apply CTC speed override logic for PLC sections K-Y only:
    1. When CTC sends suggested speed, set that SECTION to CTC speed (max 43.5 mph)
    2. When section becomes unoccupied, reset to default (25 mph) AND clear suggested speed
    """
    current_line = data.current_line
    
    # PLC sections we control
    plc_sections = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    
    # Track which suggested speeds to clear
    suggested_speeds_to_clear = []
    
    # Check if CTC has suggested any speeds
    if current_line in data.suggested_speed:
        ctc_suggested_speeds = data.suggested_speed[current_line]
        
        # Process each block with CTC suggested speed
        for block_str, ctc_speed_str in ctc_suggested_speeds.items():
            try:
                block_num = int(block_str)
                
                # Get the section for this block
                block_section = data.get_section_for_block(current_line, block_str)
                
                # Only process if section is in PLC sections K-Y
                if block_section and block_section in plc_sections:
                    
                    # Convert CTC speed from m/s to mph (if needed) and cap at 43.5 mph
                    ctc_speed_mph = float(ctc_speed_str) * 2.23694  # Convert m/s to mph
                    
                    # Cap at maximum speed of 43.5 mph
                    if ctc_speed_mph > 43.5:
                        ctc_speed_mph = 43.5
                        print(f"  CTC Speed Capped: Section {block_section} speed capped to 43.5 mph")
                    
                    print(f"  CTC Speed Override: Block {block_num} in Section {block_section} -> {ctc_speed_mph:.1f} mph")
                    
                    # Find all blocks in this section
                    blocks_in_section = data.get_blocks_in_section(current_line, block_section)
                    
                    # Apply CTC speed to ALL blocks in this section
                    for section_block in blocks_in_section:
                        section_block_str = str(section_block)
                        
                        # Only set speed if not already set by user or previous CTC command
                        # Check if current speed is default (32) or needs updating
                        current_speed = data.commanded_speed[current_line].get(section_block_str, "25")
                        if current_speed == "25" or current_speed != str(ctc_speed_mph):
                            # Set commanded speed for this block
                            data.commanded_speed[current_line][section_block_str] = str(ctc_speed_mph)
                            data.update_block_in_track_data(section_block, "speed", ctc_speed_mph)
                            print(f"    -> Block {section_block}: Speed set to {ctc_speed_mph:.1f} mph")
                        
                        # Send to Track Model if this block is occupied
                        block_key = f"Block {section_block}"
                        if block_key in data.filtered_blocks:
                            if data.filtered_blocks[block_key].get("occupied", False):
                                # Send commanded values to Track Model
                                commanded_auth = data.commanded_authority[current_line].get(section_block_str, "3")
                                if hasattr(data, 'app') and data.app:
                                    data.app.send_commanded_to_track_model(
                                        current_line, section_block_str, 
                                        str(ctc_speed_mph), commanded_auth
                                    )
                                    print(f"    -> Sent to Track Model (occupied)")
                
            except (ValueError, TypeError) as e:
                print(f"  Error processing CTC speed for block {block_str}: {e}")
    
    # Reset sections to default speed when conditions are met
    # ONLY for PLC sections K-Y
    for section in plc_sections:
        blocks_in_section = data.get_blocks_in_section(current_line, section)
        
        # Skip if no blocks in this section
        if not blocks_in_section:
            continue
        
        # Check if section should be reset to default speed
        should_reset = False
        
        # Condition 1: Check if entire section is unoccupied
        section_occupied = False
        for block_num in blocks_in_section:
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    section_occupied = True
                    break
        
        if not section_occupied:
            should_reset = True
            #print(f"  Speed Reset: Section {section} is unoccupied -> reset to default")
            
            # Mark any suggested speeds in this section for clearing
            if current_line in data.suggested_speed:
                for block_str in list(data.suggested_speed[current_line].keys()):
                    try:
                        block_section = data.get_section_for_block(current_line, block_str)
                        if block_section == section:
                            suggested_speeds_to_clear.append(block_str)
                            #print(f"    -> Will clear suggested speed for block {block_str}")
                    except:
                        pass
        
        # Reset section to default speed if conditions are met
        if should_reset:
            default_speed = "25"  # Default speed in mph
            
            for block_num in blocks_in_section:
                block_str = str(block_num)
                
                # Update commanded speed
                data.commanded_speed[current_line][block_str] = default_speed
                data.update_block_in_track_data(block_num, "speed", 25)
                
                # Send to Track Model if block is occupied
                block_key = f"Block {block_num}"
                if block_key in data.filtered_blocks:
                    if data.filtered_blocks[block_key].get("occupied", False):
                        commanded_auth = data.commanded_authority[current_line].get(block_str, "3")
                        if hasattr(data, 'app') and data.app:
                            data.app.send_commanded_to_track_model(
                                current_line, block_str, default_speed, commanded_auth
                            )
    
    # Actually clear the suggested speeds
    if suggested_speeds_to_clear and current_line in data.suggested_speed:
        for block_str in suggested_speeds_to_clear:
            if block_str in data.suggested_speed[current_line]:
                del data.suggested_speed[current_line][block_str]
                print(f"  CTC Speed CLEARED: Removed suggested speed for block {block_str}")

def apply_ctc_override_logic(data, current_line, block_num_int, final_authority, occupied_blocks, ctc_override_blocks):
    """
    Apply CTC override authority logic.
    Returns: tuple of (updated_final_authority, updated_ctc_override_blocks)
    """
    if not ctc_override_blocks:
        return final_authority, ctc_override_blocks
    
    # FIRST: Check if train has reached any CTC stopping point
    ctc_overrides_to_clear = []
    
    for ctc_block in ctc_override_blocks:
        # Determine stopping point based on block number
        if ctc_block == 80:
            # SPECIAL CASE: Backward movement for block 80
            stopping_block = ctc_block - 3  # 80-3 = 77
            #print(f"  CTC Block 80: Using BACKWARD pattern (stopping at {stopping_block})")
        else:
            # NORMAL: Forward movement for all other blocks
            stopping_block = ctc_block + 3  # X+3
            #print(f"  CTC Block {ctc_block}: Using FORWARD pattern (stopping at {stopping_block})")
        
        # Check if stopping block is occupied
        stopping_key = f"Block {stopping_block}"
        if stopping_key in data.filtered_blocks:
            if data.filtered_blocks[stopping_key].get("occupied", False):
                # Train has reached destination! Clear this CTC override
                ctc_overrides_to_clear.append(ctc_block)
                #print(f"  CTC AUTO-CLEAR: Block {ctc_block} (train at stopping block {stopping_block})")
    
    # Actually delete from suggested_authority
    if ctc_overrides_to_clear and current_line in data.suggested_authority:
        for ctc_block in ctc_overrides_to_clear:
            block_str = str(ctc_block)
            if block_str in data.suggested_authority[current_line]:
                del data.suggested_authority[current_line][block_str]
                #print(f"  CTC OVERRIDE DELETED: Removed block {ctc_block}")
    
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
    
    # Apply CTC override logic with correct direction
    for ctc_block in ctc_override_blocks:
        if ctc_block == 80:
            # BACKWARD pattern for block 80: 80=3, 79=2, 78=1, 77=0
            distance = ctc_block - block_num_int  # Positive if block is behind CTC
            
            if distance == 0:  # Block 80 itself
                ctc_auth = 3
                final_authority = min(final_authority, ctc_auth)
            elif distance == 1:  # Block 79 (80-1)
                ctc_auth = 2
                final_authority = min(final_authority, ctc_auth)
            elif distance == 2:  # Block 78 (80-2)
                ctc_auth = 1
                final_authority = min(final_authority, ctc_auth)
            elif distance == 3:  # Block 77 (80-3)
                ctc_auth = 0
                final_authority = min(final_authority, ctc_auth)
        else:
            # FORWARD pattern for all others: X=3, X+1=2, X+2=1, X+3=0
            distance = block_num_int - ctc_block  # Positive if block is ahead of CTC
            
            if distance == 0:  # CTC block itself
                ctc_auth = 3
                final_authority = min(final_authority, ctc_auth)
            elif distance == 1:  # Block X+1
                ctc_auth = 2
                final_authority = min(final_authority, ctc_auth)
            elif distance == 2:  # Block X+2
                ctc_auth = 1
                final_authority = min(final_authority, ctc_auth)
            elif distance == 3:  # Block X+3
                ctc_auth = 0
                final_authority = min(final_authority, ctc_auth)
    
    return final_authority, ctc_override_blocks


def apply_ctc_speed_overrides(data, log_callback):
    """
    Apply CTC speed override logic for PLC sections K-Y only:
    1. When CTC sends suggested speed, set that SECTION to CTC speed (max 43.5 mph)
    2. UNLESS user has already set a commanded speed for that section
    3. When section becomes unoccupied, reset to default (25 mph) AND clear suggested speed
    """
    current_line = data.current_line
    
    # PLC sections we control
    plc_sections = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    
    # Track which suggested speeds to clear
    suggested_speeds_to_clear = []
    
    # Check if CTC has suggested any speeds
    if current_line in data.suggested_speed:
        ctc_suggested_speeds = data.suggested_speed[current_line]
        
        # Process each block with CTC suggested speed
        for block_str, ctc_speed_str in ctc_suggested_speeds.items():
            try:
                block_num = int(block_str)
                block_section = data.get_section_for_block(current_line, block_str)
                
                if block_section and block_section in plc_sections:
                    # Check if user has already set speed for this section
                    blocks_in_section = data.get_blocks_in_section(current_line, block_section)
                    user_has_set_speed = False
                    
                    for section_block in blocks_in_section:
                        section_block_str = str(section_block)
                        current_speed = data.commanded_speed[current_line].get(section_block_str, "25")
                        
                        # Check if this looks like a user-set speed (not default)
                        # AND not from CTC (check suggested_speed dict)
                        if current_speed != "25":
                            # Check if this speed is from CTC (including capping)
                            is_ctc_speed = False
                            if current_line in data.suggested_speed:
                                try:
                                    current_speed_mph = float(current_speed)
                                    # Check if any CTC suggested speed, when converted and capped, matches current speed
                                    for ctc_block, ctc_speed_ms in data.suggested_speed[current_line].items():
                                        try:
                                            ctc_speed_mph = float(ctc_speed_ms) * 2.23694
                                            # Apply capping
                                            if ctc_speed_mph > 43.5:
                                                ctc_speed_mph = 43.5
                                            
                                            # Compare with tolerance
                                            if abs(current_speed_mph - ctc_speed_mph) < 0.1:
                                                is_ctc_speed = True
                                                break
                                        except:
                                            pass
                                except:
                                    pass
                            
                            # If not from CTC, assume user set it
                            if not is_ctc_speed:
                                user_has_set_speed = True
                                break
                    
                    if user_has_set_speed:
                        continue  # Skip CTC override for this section
                    
                    # ============ APPLY CTC SPEED ============
                    # Convert CTC speed from m/s to mph (if needed) and cap at 43.5 mph
                    ctc_speed_mph = float(ctc_speed_str) * 2.23694  # Convert m/s to mph
                    
                    # Cap at maximum speed of 43.5 mph
                    if ctc_speed_mph > 43.5:
                        ctc_speed_mph = 43.5
                    
                    
                    # Apply CTC speed to ALL blocks in this section
                    for section_block in blocks_in_section:
                        section_block_str = str(section_block)
                        
                        # Only set speed if not already set by user
                        current_speed = data.commanded_speed[current_line].get(section_block_str, "25")
                        if current_speed == "25":  # Only override default speed
                            # Set commanded speed for this block
                            data.commanded_speed[current_line][section_block_str] = str(ctc_speed_mph)
                            data.update_block_in_track_data(section_block, "speed", ctc_speed_mph)
                        
                        # Send to Track Model if this block is occupied
                        block_key = f"Block {section_block}"
                        if block_key in data.filtered_blocks:
                            if data.filtered_blocks[block_key].get("occupied", False):
                                # Send commanded values to Track Model
                                commanded_auth = data.commanded_authority[current_line].get(section_block_str, "3")
                                if hasattr(data, 'app') and data.app:
                                    data.app.send_commanded_to_track_model(
                                        current_line, section_block_str, 
                                        str(ctc_speed_mph), commanded_auth
                                    )
                    # ============ END APPLY CTC SPEED ============
                
            except (ValueError, TypeError) as e:
                #print(f"  Error processing CTC speed for block {block_str}: {e}")
                print(f" ")


    # Reset sections to default speed when conditions are met
    # ONLY for PLC sections K-Y
    for section in plc_sections:
        blocks_in_section = data.get_blocks_in_section(current_line, section)
        
        # Skip if no blocks in this section
        if not blocks_in_section:
            continue
        
        # Check if section should be reset to default speed
        should_reset = False
        
        # Condition 1: Check if entire section is unoccupied
        section_occupied = False
        for block_num in blocks_in_section:
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    section_occupied = True
                    break
        
        if not section_occupied:
            should_reset = True
            #print(f"  Speed Reset: Section {section} is unoccupied -> reset to default")
            
            # Mark any suggested speeds in this section for clearing
            if current_line in data.suggested_speed:
                for block_str in list(data.suggested_speed[current_line].keys()):
                    try:
                        block_section = data.get_section_for_block(current_line, block_str)
                        if block_section == section:
                            suggested_speeds_to_clear.append(block_str)
                            #print(f"    -> Will clear suggested speed for block {block_str}")
                    except:
                        pass
        
        # Reset section to default speed if conditions are met
        if should_reset:
            default_speed = "25"  # Default speed in mph
            
            for block_num in blocks_in_section:
                block_str = str(block_num)
                
                # Update commanded speed
                data.commanded_speed[current_line][block_str] = default_speed
                
                # Send to Track Model if block is occupied
                block_key = f"Block {block_num}"
                if block_key in data.filtered_blocks:
                    if data.filtered_blocks[block_key].get("occupied", False):
                        commanded_auth = data.commanded_authority[current_line].get(block_str, "3")
                        if hasattr(data, 'app') and data.app:
                            data.app.send_commanded_to_track_model(
                                current_line, block_str, default_speed, commanded_auth
                            )
                            #print(f"    -> Block {block_num}: Reset to default speed {default_speed} mph")
    
    # Actually clear the suggested speeds
    if suggested_speeds_to_clear and current_line in data.suggested_speed:
        for block_str in suggested_speeds_to_clear:
            if block_str in data.suggested_speed[current_line]:
                del data.suggested_speed[current_line][block_str]
                #print(f"  CTC Speed CLEARED: Removed suggested speed for block {block_str}")

def apply_commanded_speed_overrides(data, log_callback):
    """
    Apply commanded speed override logic for PLC sections K-Y only:
    1. When user sets commanded speed, set that SECTION to commanded speed (max 43.5 mph)
    2. When section becomes unoccupied, reset to default (25 mph) AND clear commanded speed override
    3. DO NOT reset if CTC has set a speed for that section
    """
    current_line = data.current_line
    
    # PLC sections we control
    plc_sections = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    
    # Track which commanded speeds to clear (we'll track by section)
    commanded_speeds_to_clear = set()
    
    # First, check for sections that should have their commanded speeds cleared
    for section in plc_sections:
        blocks_in_section = data.get_blocks_in_section(current_line, section)
        
        # Skip if no blocks in this section
        if not blocks_in_section:
            continue
        
        # Check if CTC has set a speed for any block in this section
        ctc_has_speed_for_section = False
        if current_line in data.suggested_speed:
            for block_str in data.suggested_speed[current_line]:
                try:
                    block_section = data.get_section_for_block(current_line, block_str)
                    if block_section == section:
                        ctc_has_speed_for_section = True
                        break
                except:
                    pass
        
        # If CTC has set speed for this section, skip resetting
        if ctc_has_speed_for_section:
            #print(f"  Commanded Speed: Section {section} has CTC speed - skipping reset")
            continue
        
        # Check if section should be reset to default speed
        should_reset = False
        
        # Condition 1: Check if entire section is unoccupied
        section_occupied = False
        for block_num in blocks_in_section:
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    section_occupied = True
                    break
        
        if not section_occupied:
            should_reset = True
            #print(f"  Commanded Speed Reset: Section {section} is unoccupied -> reset to default")
            commanded_speeds_to_clear.add(section)
        
        # REMOVE THIS CONDITION: Don't reset based on authority 0 if CTC has speed
        # Condition 2: Check if any block in section has authority 0 AND is occupied
        # This means train has reached stopping point - BUT CTC might want different speed
        # if not should_reset:  # Only check if section is occupied
        #     for block_num in blocks_in_section:
        #         block_str = str(block_num)
        #         block_key = f"Block {block_num}"
        #         
        #         # Check both: authority = 0 AND block is occupied
        #         block_auth = data.commanded_authority[current_line].get(block_str, "3")
        #         is_occupied = False
        #         
        #         if block_key in data.filtered_blocks:
        #             is_occupied = data.filtered_blocks[block_key].get("occupied", False)
        #         
        #         if block_auth == "0" and is_occupied:
        #             should_reset = True
        #             print(f"  Commanded Speed Reset: Block {block_num} in Section {section} has authority 0 AND is occupied -> reset to default")
        #             commanded_speeds_to_clear.add(section)
        #             break
    
    # Now apply commanded speed logic
    # We need to track which blocks have user-set commanded speeds
    # (Different from CTC suggested speeds)
    
    # Reset sections that need clearing
    for section in commanded_speeds_to_clear:
        blocks_in_section = data.get_blocks_in_section(current_line, section)
        
        for block_num in blocks_in_section:
            block_str = str(block_num)
            
            # Set default speed
            default_speed = "25"
            data.commanded_speed[current_line][block_str] = default_speed
            data.update_block_in_track_data(block_num, "speed", 25)
            
            # Send to Track Model if block is occupied
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    commanded_auth = data.commanded_authority[current_line].get(block_str, "3")
                    if hasattr(data, 'app') and data.app:
                        data.app.send_commanded_to_track_model(
                            current_line, block_str, default_speed, commanded_auth
                        )
                        #print(f"    -> Block {block_num}: Reset to default speed {default_speed} mph")
    
    # For sections NOT being cleared, we need to ensure commanded speeds are applied correctly
    # This is tricky because we don't track which speeds were user-set vs PLC-calculated
    
    # One approach: Check if any block in a section has a commanded speed different from default
    # and apply it to the whole section (similar to CTC logic)
    
    for section in plc_sections:
        if section in commanded_speeds_to_clear:
            continue  # Already handled above
            
        blocks_in_section = data.get_blocks_in_section(current_line, section)
        
        # Find any user-set commanded speed in this section
        user_set_speed = None
        for block_num in blocks_in_section:
            block_str = str(block_num)
            cmd_speed = data.commanded_speed[current_line].get(block_str)
            
            # Check if this speed looks like it was user-set (not default and not CTC)
            if cmd_speed and cmd_speed != "25":
                # Check if it's not a CTC speed (CTC sends m/s, user sends mph)
                # User speeds in mph could be any value, but CTC speeds are from suggested_speed
                if current_line in data.suggested_speed and block_str in data.suggested_speed[current_line]:
                    # This is a CTC speed, not user commanded
                    continue
                
                # This might be a user-set speed
                try:
                    speed_float = float(cmd_speed)
                    # Cap at maximum speed of 43.5 mph
                    if speed_float > 43.5:
                        speed_float = 43.5
                        cmd_speed = "43.5"
                        #print(f"  Commanded Speed Capped: Section {section} speed capped to 43.5 mph")
                    
                    user_set_speed = cmd_speed
                    #print(f"  Commanded Speed Override: Found user-set speed {cmd_speed} mph in Section {section}")
                    break
                except (ValueError, TypeError):
                    continue
        
        # Apply user-set speed to entire section if found
        if user_set_speed:
            for block_num in blocks_in_section:
                block_str = str(block_num)
                
                # Set commanded speed for this block
                data.commanded_speed[current_line][block_str] = user_set_speed
                data.update_block_in_track_data(block_num, "speed", float(user_set_speed))
                
                # Send to Track Model if this block is occupied
                block_key = f"Block {block_num}"
                if block_key in data.filtered_blocks:
                    if data.filtered_blocks[block_key].get("occupied", False):
                        # Send commanded values to Track Model
                        commanded_auth = data.commanded_authority[current_line].get(block_str, "3")
                        if hasattr(data, 'app') and data.app:
                            data.app.send_commanded_to_track_model(
                                current_line, block_str, 
                                user_set_speed, commanded_auth
                            )
                            #print(f"    -> Block {block_num}: Applied commanded speed {user_set_speed} mph")

def control_lights_automatically(data, log_callback):
    """
    Control lights based on occupancy logic:
    - Light 75: Controls approach to Section N from blocks 86-100
    - Light 100: Controls approach to Section N from blocks 69-76
    """
    current_line = data.current_line
    
    # Get blocks in Section N
    blocks_in_section_N = data.get_blocks_in_section(current_line, 'N')
    
    # ==============================================
    # Check if Section N is occupied
    # ==============================================
    section_N_occupied = False
    for block_num in blocks_in_section_N:
        block_key = f"Block {block_num}"
        if block_key in data.filtered_blocks:
            if data.filtered_blocks[block_key].get("occupied", False):
                section_N_occupied = True
                break
    
    #print(f"[DEBUG] Section N occupied: {section_N_occupied}")
    
    # ==============================================
    # LIGHT 75 LOGIC
    # ==============================================
    light_75_name = "Light 75"
    
    if light_75_name in data.filtered_light_states:
        # Check blocks 86-100 for occupancy
        blocks_86_to_100_occupied = False
        for block_num in range(86, 101):  # 86 to 100 inclusive
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    blocks_86_to_100_occupied = True
                    #print(f"[DEBUG] Light 75: Block {block_num} is occupied (86-100 range)")
                    break
        
        #print(f"[DEBUG] Light 75: Blocks 86-100 occupied: {blocks_86_to_100_occupied}")
        
        # Determine Light 75 state
        if section_N_occupied:
            # RED: Section N is occupied
            light_state = "Red"
            condition_text = "Section N occupied"
        elif blocks_86_to_100_occupied:
            # YELLOW: Blocks 86-100 are occupied (but N is not)
            light_state = "Yellow"
            condition_text = "Blocks 86-100 occupied"
        else:
            # GREEN: Nothing occupied in 86-100 and N is not occupied
            light_state = "Green"
            condition_text = "Clear path to Section N"
        
        #print(f"[DEBUG] Light 75: Setting to {light_state} - {condition_text}")
        
        # Update light state
        data.update_track_data("light_states", light_75_name, "signal", light_state)
        data.update_track_data("light_states", light_75_name, "condition", condition_text)
    
    # ==============================================
    # LIGHT 100 LOGIC
    # ==============================================
    light_100_name = "Light 100"
    
    if light_100_name in data.filtered_light_states:
        # Check blocks 69-76 for occupancy
        blocks_69_to_76_occupied = False
        for block_num in range(69, 77):  # 69 to 76 inclusive
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    blocks_69_to_76_occupied = True
                    #print(f"[DEBUG] Light 100: Block {block_num} is occupied (69-76 range)")
                    break
        
        #print(f"[DEBUG] Light 100: Blocks 69-76 occupied: {blocks_69_to_76_occupied}")
        
        # Check blocks 101-116 for occupancy (for SUPER GREEN)
        blocks_101_to_116_occupied = False
        for block_num in range(101, 117):  # 101 to 116 inclusive
            block_key = f"Block {block_num}"
            if block_key in data.filtered_blocks:
                if data.filtered_blocks[block_key].get("occupied", False):
                    blocks_101_to_116_occupied = True
                    #print(f"[DEBUG] Light 100: Block {block_num} is occupied (101-116 range)")
                    break
        
        #print(f"[DEBUG] Light 100: Blocks 101-116 occupied: {blocks_101_to_116_occupied}")
        
        # Determine Light 100 state
        if section_N_occupied:
            # RED: Section N is occupied
            light_state = "Red"
            condition_text = "Section N occupied"
        elif blocks_69_to_76_occupied:
            # YELLOW: Blocks 69-76 are occupied (but N is not)
            light_state = "Yellow"
            condition_text = "Blocks 69-76 occupied"
        elif not blocks_101_to_116_occupied:
            # SUPER GREEN: Nothing in 69-76, N, AND 101-116
            light_state = "Super Green"
            condition_text = "Clear path through Section N and beyond"
        else:
            # GREEN: Nothing in 69-76 and N, but something in 101-116
            light_state = "Green"
            condition_text = "Clear path to Section N"
        
        #print(f"[DEBUG] Light 100: Setting to {light_state} - {condition_text}")
        
        # Update light state
        data.update_track_data("light_states", light_100_name, "signal", light_state)
        data.update_track_data("light_states", light_100_name, "condition", condition_text)
    
    #print("[DEBUG] Light control complete")

def control_railway_crossings(data, log_callback):
    """
    Control Railway Crossing 108
    Activate when train is on block 108 OR block 107
    """
    current_line = data.current_line
    crossing_name = "Railway 108"  # CHANGED from "Railway Crossing 108"
    
    #print(f"[DEBUG] Controlling {crossing_name}")
    
    # CRITICAL: Create crossing if it doesn't exist
    if crossing_name not in data.railway_crossings:
        #print(f"[DEBUG] Creating Railway 108 dynamically")
        
        # Add to main data
        data.railway_crossings[crossing_name] = {
            "lights": "Off",
            "bar": "Open",
            "condition": "Not initialized",
            "line": current_line,
            "section": data.get_section_for_block(current_line, "108")  # ADD SECTION
        }
        
        # Also add to filtered data
        data.filtered_railway_crossings[crossing_name] = {
            "lights": "Off",
            "bar": "Open",
            "condition": "Not initialized",
            "line": current_line,
            "section": data.get_section_for_block(current_line, "108")  # ADD SECTION
        }
        #print(f"[DEBUG] Railway 108 created - will appear in UI")
    
    # Initialize variables
    crossing_occupied = False
    previous_occupied = False
    
    # Check block 108
    if "Block 108" in data.filtered_blocks:
        crossing_occupied = data.filtered_blocks["Block 108"].get("occupied", False)
    
    # Check block 107  
    if "Block 107" in data.filtered_blocks:
        previous_occupied = data.filtered_blocks["Block 107"].get("occupied", False)
    
    # Activate if train on 108 OR 107
    should_activate = crossing_occupied or previous_occupied
    
    if should_activate:
        lights_state = "On"
        bar_state = "Closed"
        if crossing_occupied:
            condition_text = f"Lights: {lights_state}, Bar: {bar_state}"  # CHANGED
        else:
            condition_text = f"Lights: {lights_state}, Bar: {bar_state}"  # CHANGED
    else:
        lights_state = "Off"
        bar_state = "Open"
        condition_text = f"Lights: {lights_state}, Bar: {bar_state}"  # CHANGED

    # Update using the standard method
    data.update_track_data("railway_crossings", crossing_name, "lights", lights_state)
    data.update_track_data("railway_crossings", crossing_name, "bar", bar_state)
    data.update_track_data("railway_crossings", crossing_name, "condition", condition_text)

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
                # This means train has passed over the block
                if previous_occupied and not is_occupied:
                    blocks_to_clear.append(block_num_str)
                    print(f"  Authority Override CLEARED: Block {block_num_str} - train has passed")
                    
                    # Also send default authority to track model if block is in PLC section
                    # Get the section for this block
                    section = data.get_section_for_block(current_line, block_num_str)
                    plc_sections = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
                    
                    if section in plc_sections and is_occupied:
                        # Send default authority (3) to track model
                        default_speed = data.commanded_speed[current_line].get(block_num_str, "25")
                        if hasattr(data, 'app') and data.app:
                            data.app.send_commanded_to_track_model(
                                current_line, block_num_str, default_speed, "3"
                            )
                            print(f"    -> Sent default authority 3 to Track Model")
        
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
    
    Call this function when user sets authority from the UI.
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
    
    print(f"User authority override set: {track} Block {block} = {authority}")
    
    # Immediately update the UI if possible
    if hasattr(data, 'command_authority_override_callback'):
        try:
            data.command_authority_override_callback(track, block, authority)
        except Exception as e:
            print(f"Warning: Could not update UI callback: {e}")
    
    return True