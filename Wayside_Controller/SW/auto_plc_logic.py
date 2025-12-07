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
    print(f"\nPLC CYCLE for {current_line} line")
    print(f"Occupied blocks: {occupied_blocks}")
    print(f"Section N occupied: {section_N_occupied}")
    
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
    if ctc_override_blocks:
        print(f"CTC override blocks (suggested auth=3): {ctc_override_blocks}")
    
    # Process each block
    for block_key, block_info in data.filtered_blocks.items():
        block_num = block_info["number"]
        
        try:
            block_num_int = int(block_num)
        except ValueError:
            continue
        
        # Default values
        default_authority = 3
        default_speed = 32
        final_authority = default_authority
        final_speed = default_speed
        
        # Check if block itself is occupied
        is_block_occupied = block_num_int in occupied_blocks
        
        if is_block_occupied:
            # Occupied block: authority 0
            final_authority = 0
        elif occupied_blocks:
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
                # else: stays at 3 (default)
        
        control_switches_automatically(data, log_callback)
        
        # ==============================================
        # NEW: Apply CTC override logic
        # ==============================================
        if ctc_override_blocks:
            # Check if this block is within range of any CTC override block
            for ctc_block in ctc_override_blocks:
                # CTC block is at position X
                # We want: X+1 = 2, X+2 = 1, X+3 = 0, X+4+ = 3
                distance_to_ctc = block_num_int - ctc_block
                
                if distance_to_ctc == 1:  # Block X+1
                    ctc_auth = 2
                    final_authority = min(final_authority, ctc_auth)  # Use most restrictive
                    print(f"  CTC Override: Block {block_num} (X+1) auth = min({final_authority}, {ctc_auth})")
                elif distance_to_ctc == 2:  # Block X+2
                    ctc_auth = 1
                    final_authority = min(final_authority, ctc_auth)
                    print(f"  CTC Override: Block {block_num} (X+2) auth = min({final_authority}, {ctc_auth})")
                elif distance_to_ctc == 3:  # Block X+3
                    ctc_auth = 0
                    final_authority = min(final_authority, ctc_auth)
                    print(f"  CTC Override: Block {block_num} (X+3) auth = min({final_authority}, {ctc_auth})")
                # Block X+4 and beyond: no override (stays at current auth)
        
        # Apply Section N rules if section N has occupied block
        if section_N_occupied and block_num in ['74', '75', '76', '98', '99', '100']:
            # Get Section N authority for this block
            section_N_auth = None
            if block_num in ['74', '98']:
                section_N_auth = 2
            elif block_num in ['75', '99']:
                section_N_auth = 1
            elif block_num in ['76', '100']:
                section_N_auth = 0
            
            if section_N_auth is not None:
                # Use the smaller (more restrictive) authority
                old_auth = final_authority
                final_authority = min(final_authority, section_N_auth)
                print(f"  Section N: Block {block_num} auth = min({old_auth}, {section_N_auth}) = {final_authority}")
        
        # Update data
        data.update_block_in_track_data(block_num, "authority", final_authority)
        data.update_block_in_track_data(block_num, "speed", final_speed)
        
        # Update commanded values
        if current_line not in data.commanded_authority:
            data.commanded_authority[current_line] = {}
        if current_line not in data.commanded_speed:
            data.commanded_speed[current_line] = {}
        
        data.commanded_authority[current_line][block_num] = str(final_authority)
        data.commanded_speed[current_line][block_num] = str(final_speed)
        
    # Apply filter
    data.apply_plc_filter()
    
    # Trigger UI update
    for callback in data.on_data_update:
        try:
            callback()
        except Exception as e:
            print(f"PLC callback error: {e}")
    
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
    
    print(f"\n=== SWITCH CONTROL ===")
    print(f"Train in section N: {train_in_section_N}")
    
    # Switch 85
    switch_85_name = "Switch 85"
    if switch_85_name in data.filtered_switch_positions:
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
            print(f"Switch 85: {current_pos} -> {desired_pos}")
            # UPDATE BOTH DIRECTION AND CONDITION
            data.update_track_data("switch_positions", switch_85_name, "direction", desired_pos)
            data.update_track_data("switch_positions", switch_85_name, "condition", condition_text)
        else:
            print(f"Switch 85: Already at {desired_pos}")
    
    # Switch 76 (Add this logic!)
    switch_76_name = "Switch 76"  # or "Switch 77" - check your actual name
    if switch_76_name in data.filtered_switch_positions:
        switch_76 = data.filtered_switch_positions[switch_76_name]
        current_pos = switch_76.get("direction", "76-77")
        
        if train_in_section_N:
            desired_pos = "77-101"
            condition_text = f"N -> R"
        else:
            desired_pos = "76-77"
            condition_text = f"M -> N"
        
        if current_pos != desired_pos:
            print(f"Switch 76: {current_pos} -> {desired_pos}")
            # UPDATE BOTH DIRECTION AND CONDITION
            data.update_track_data("switch_positions", switch_76_name, "direction", desired_pos)
            data.update_track_data("switch_positions", switch_76_name, "condition", condition_text)
        else:
            print(f"Switch 76: Already at {desired_pos}")
    
    print(f"=== SWITCH CONTROL COMPLETE ===\n")