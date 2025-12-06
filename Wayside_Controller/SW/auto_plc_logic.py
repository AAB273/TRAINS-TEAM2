from datetime import datetime

def run_plc_cycle(data, log_callback):
    """
    SIMPLE, CORRECT PLC - back to basics
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
        
        # Debug for changed blocks
        if final_authority != 3 or is_block_occupied:
            print(f"  Block {block_num}: occupied={is_block_occupied}, authority={final_authority}")
    
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