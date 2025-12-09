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
    
    # ==============================================
    # FIX: Run Section N logic BEFORE processing blocks
    # ==============================================
    section_n_dynamic_auth = {}  # Store dynamic authorities for Section N blocks
    
    # Apply Section N dynamic logic if section N has occupied block
    if section_N_occupied:
        #print("\n[DEBUG] Running Section N dynamic authority logic...")
        section_n_dynamic_auth = apply_section_n_authority_logic(data, log_callback)
        #print(f"[DEBUG] Section N dynamic authorities calculated: {section_n_dynamic_auth}")
    
    # ==============================================
    # FIX: Run switch control ONCE, before processing blocks
    # ==============================================
    #print("[DEBUG] Running switch control...")
    control_switches_automatically(data, log_callback)
    
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
            #print(f"[DEBUG] Block {block_num} is occupied: auth=0")
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
                    #print(f"[DEBUG] Block {block_num}: 1 block ahead of occupied {nearest_ahead}: auth=0")
                elif min_distance == 2:
                    final_authority = 1
                    #print(f"[DEBUG] Block {block_num}: 2 blocks ahead of occupied {nearest_ahead}: auth=1")
                elif min_distance == 3:
                    final_authority = 2
                    #print(f"[DEBUG] Block {block_num}: 3 blocks ahead of occupied {nearest_ahead}: auth=2")
                # else: stays at 3 (default)
        
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
        
        # ==============================================
        # FIX: Apply Section N authorities AFTER CTC logic
        # ==============================================
        if section_N_occupied:
            # Check if this block has a dynamic authority from Section N
            if block_num in section_n_dynamic_auth:
                dynamic_auth = section_n_dynamic_auth[block_num]
                #print(f"[DEBUG] Block {block_num}: Applying Section N dynamic auth {dynamic_auth} (was {final_authority})")
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
                    print(f"  Section N Fixed: Block {block_num} auth = min({old_auth}, {section_N_fixed_auth}) = {final_authority}")
        
        # ==============================================
        # DEBUG: Show final authority
        # ==============================================
        #if final_authority != default_authority:
            #print(f"[DEBUG] Block {block_num}: Final authority = {final_authority}")
        
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
    print(f"[DEBUG] Triggering UI update with {len(data.on_data_update)} callbacks")
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
    
    print(f"[DEBUG] Switch control: Train in section N = {train_in_section_N}")
    
    # Switch 85 - Check if manually set
    switch_85_name = "Switch 85"
    switch_85_id = "85"
    
    if switch_85_name in data.filtered_switch_positions:
        # Check if this switch was manually set in maintenance mode
        if hasattr(data, 'manual_switches') and switch_85_id in data.manual_switches:
            print(f"[DEBUG] Switch 85: Skipping - manually set by user")
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
                print(f"[DEBUG] Switch 85: {current_pos} -> {desired_pos}")
                # UPDATE BOTH DIRECTION AND CONDITION
                data.update_track_data("switch_positions", switch_85_name, "direction", desired_pos)
                data.update_track_data("switch_positions", switch_85_name, "condition", condition_text)
            else:
                print(f"[DEBUG] Switch 85: Already at {desired_pos}")
    
    # Switch 76 - Check if manually set
    switch_76_name = "Switch 76"
    switch_76_id = "76"
    
    if switch_76_name in data.filtered_switch_positions:
        # Check if this switch was manually set in maintenance mode
        if hasattr(data, 'manual_switches') and switch_76_id in data.manual_switches:
            print(f"[DEBUG] Switch 76: Skipping - manually set by user")
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
                print(f"[DEBUG] Switch 76: {current_pos} -> {desired_pos}")
                # UPDATE BOTH DIRECTION AND CONDITION
                data.update_track_data("switch_positions", switch_76_name, "direction", desired_pos)
                data.update_track_data("switch_positions", switch_76_name, "condition", condition_text)
            else:
                print(f"[DEBUG] Switch 76: Already at {desired_pos}")
    
    print("[DEBUG] Switch control complete")
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
        print("[DEBUG] No Section N blocks found")
        return {}
    
    # Find occupied blocks within section N
    occupied_n_blocks = []
    for block_num in blocks_in_section_N:
        block_key = f"Block {block_num}"
        if block_key in data.filtered_blocks:
            if data.filtered_blocks[block_key].get("occupied", False):
                occupied_n_blocks.append(block_num)
    
    if not occupied_n_blocks:
        print("[DEBUG] No occupied blocks in Section N")
        return {}
    
    print(f"[DEBUG] Section N blocks: {blocks_in_section_N}")
    print(f"[DEBUG] Occupied blocks in Section N: {occupied_n_blocks}")
    
    # Track all authority modifications
    authority_updates = {}
    
    # Process each occupied block in section N
    for occupied_block in occupied_n_blocks:
        print(f"[DEBUG] Processing occupied block {occupied_block} in Section N")
        
        # Get track position for the occupied block
        occupied_block_key = f"Block {occupied_block}"
        if occupied_block_key not in data.filtered_blocks:
            print(f"[DEBUG] Could not find block {occupied_block} in filtered blocks")
            continue
            
        occupied_pos = data.filtered_blocks[occupied_block_key].get("track_position", 0)
        print(f"[DEBUG]   Block {occupied_block} track position: {occupied_pos}")
        
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
            print(f"[DEBUG] Could not find block {occupied_block} in position-sorted list")
            continue
        
        print(f"[DEBUG]   Blocks sorted by position: {blocks_with_positions}")
        print(f"[DEBUG]   Occupied block index: {occupied_idx}")
        
        # 1. Check blocks BEHIND occupied block (lower track positions)
        print(f"[DEBUG]   Checking blocks BEHIND block {occupied_block}...")
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
                if i <= 1:  # Occupied block or 1 block behind
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
                        print(f"[DEBUG]     Block {block_behind} (pos {behind_pos}, {i} behind): auth={auth_value}")
                    else:
                        # Keep the most restrictive (lowest) authority
                        old_auth = authority_updates[block_behind_str]
                        authority_updates[block_behind_str] = min(authority_updates[block_behind_str], auth_value)
                        if old_auth != authority_updates[block_behind_str]:
                            print(f"[DEBUG]     Block {block_behind}: Updated from {old_auth} to {auth_value}")
        
        # 2. Check blocks AHEAD of occupied block (higher track positions)
        print(f"[DEBUG]   Checking blocks AHEAD of block {occupied_block}...")
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
    
    print(f"[DEBUG] Section N authority updates calculated: {authority_updates}")
    return authority_updates