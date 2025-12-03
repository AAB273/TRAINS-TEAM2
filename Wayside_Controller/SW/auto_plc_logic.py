# Store previous values to detect changes
_previous_occupancy = {}
_previous_ctc_auth = {}
_previous_ctc_speed = {}

def run_plc_cycle(data, log_callback):
    """
    PLC program that updates commanded authority and speed directly in data model
    Unoccupied blocks keep their CTC destination values for when trains enter them
    """
    global _previous_occupancy, _previous_ctc_auth, _previous_ctc_speed
    
    current_line = data.current_line
    
    # Check if anything changed since last cycle
    occupancy_changed = has_occupancy_changed(data, current_line)
    ctc_changed = has_ctc_changed(data, current_line)
    
    # Only run calculations if something actually changed
    if not occupancy_changed and not ctc_changed:
        return  # Skip this cycle, no changes detected
    
    # Initialize commanded dictionaries if they don't exist
    if current_line not in data.commanded_authority:
        data.commanded_authority[current_line] = {}
    if current_line not in data.commanded_speed:
        data.commanded_speed[current_line] = {}
    
    # Process ALL blocks
    for block_name, block_info in data.filtered_track_data["blocks"].items():
        block_num = block_info["number"]
        
        # Get CTC destination values for this block (default to 0 if not set)
        ctc_dest_auth = data.commanded_authority.get(current_line, {}).get(block_num, 0)
        ctc_speed = data.suggested_speed.get(current_line, {}).get(block_num, 30)
        
        if block_info.get("occupied", False):
            # Calculate actual authority for OCCUPIED blocks considering safety
            actual_auth = calculate_authority(data, current_line, block_num, ctc_dest_auth)
            
            # Update commanded values for OCCUPIED blocks
            data.commanded_authority[current_line][block_num] = actual_auth
            data.commanded_speed[current_line][block_num] = ctc_speed
            
            # Also update track data for consistency
            data.update_block_in_track_data(block_num, "authority", actual_auth)
            data.update_block_in_track_data(block_num, "speed", ctc_speed)
            
        else:
            # UNOCCUPIED blocks keep their CTC destination values
            # This way when a train enters, it knows where to go
            data.commanded_authority[current_line][block_num] = ctc_dest_auth
            data.commanded_speed[current_line][block_num] = ctc_speed
            
            # Also update track data
            data.update_block_in_track_data(block_num, "authority", ctc_dest_auth)
            data.update_block_in_track_data(block_num, "speed", ctc_speed)
    
    # Update previous values for next cycle
    update_previous_values(data, current_line)
    
    # Trigger UI update callbacks
    for callback in data.on_data_update:
        try:
            callback()
        except Exception as e:
            print(f"PLC callback error: {e}")

def has_occupancy_changed(data, line):
    """Check if any block occupancy changed since last cycle"""
    global _previous_occupancy
    
    for block_name, block_info in data.filtered_track_data["blocks"].items():
        block_num = block_info["number"]
        key = f"{line}_{block_num}"
        current_occupied = block_info.get("occupied", False)
        previous_occupied = _previous_occupancy.get(key, None)
        
        if previous_occupied is None or current_occupied != previous_occupied:
            return True
    
    return False

def has_ctc_changed(data, line):
    """Check if any CTC values changed since last cycle"""
    global _previous_ctc_auth, _previous_ctc_speed
    
    # Check commanded authority changes
    for block_num, auth in data.commanded_authority.get(line, {}).items():
        if _previous_ctc_auth.get(f"{line}_{block_num}") != auth:
            return True
    
    # Check suggested speed changes (from CTC)
    for block_num, speed in data.suggested_speed.get(line, {}).items():
        if _previous_ctc_speed.get(f"{line}_{block_num}") != speed:
            return True
    
    return False

def update_previous_values(data, line):
    """Store current values for next cycle comparison"""
    global _previous_occupancy, _previous_ctc_auth, _previous_ctc_speed
    
    # Store occupancy
    for block_name, block_info in data.filtered_track_data["blocks"].items():
        block_num = block_info["number"]
        key = f"{line}_{block_num}"
        _previous_occupancy[key] = block_info.get("occupied", False)
    
    # Store commanded authority
    for block_num, auth in data.commanded_authority.get(line, {}).items():
        _previous_ctc_auth[f"{line}_{block_num}"] = auth
    
    # Store suggested speed (from CTC)
    for block_num, speed in data.suggested_speed.get(line, {}).items():
        _previous_ctc_speed[f"{line}_{block_num}"] = speed

def calculate_authority(data, line, current_block, ctc_destination_auth):
    """Calculate authority for OCCUPIED blocks considering safety and destination"""
    current_block_num = int(current_block)
    
    # 1. Moving block safety (5 blocks ahead max)
    safety_auth = 5
    for blocks_ahead in range(1, 6):
        check_block = current_block_num + blocks_ahead
        check_block_str = str(check_block)
        block_key = f"Block {check_block_str}"
        
        if (block_key in data.filtered_track_data["blocks"] and 
            data.filtered_track_data["blocks"][block_key].get("occupied", False)):
            safety_auth = blocks_ahead - 1
            break
    
    # 2. CTC destination authority
    destination_auth = ctc_destination_auth
    
    # 3. Use the more restrictive authority
    actual_auth = min(safety_auth, destination_auth)
    
    return max(0, actual_auth)