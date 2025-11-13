from datetime import datetime

def run_plc_cycle(data, log):
    """
    PLC logic for Wayside Controller
    ------------------------------------------------
    - Closes crossings if trains are detected nearby
    - Sets lights to red/green depending on track occupancy
    - Updates authority and block occupancy for right panel
    - Dynamic authority calculation based on block positions and switch states
    """

    def safe_log(msg):
        if log and callable(log):
            log(msg)

    current_line = data.current_line
    
    # Create track data structure from separate attributes
    track = {
        "crossings": data.filtered_railway_crossings,
        "switches": data.filtered_switch_positions,
        "lights": data.filtered_light_states,
        "blocks": data.filtered_blocks
    }

    crossings = track.get("crossings", {})
    switches = track.get("switches", {})
    lights = track.get("lights", {})
    blocks = track.get("blocks", {})

    # Track if any changes were made this cycle
    changes_made = False
    authority_changes = {}  # Track authority changes for logging

    # --- 1. Handle crossings (specific logic for Railway 3) ---
    for name, crossing in crossings.items():
        # SPECIAL LOGIC: Railway 3 crossing activates when blocks 2 or 3 are occupied
        if "Railway 3" in name or "3" in name:
            block_2 = blocks.get("Block 2", {})
            block_3 = blocks.get("Block 3", {})
            train_nearby = block_2.get("occupied", False) or block_3.get("occupied", False)
        else:
            # General logic for other crossings
            crossing_pos = crossing.get("position", 0)
            nearby_blocks = [
                b for b in blocks.values()
                if abs(b.get("position", 0) - crossing_pos) <= 2
            ]
            train_nearby = any(b.get("occupied", False) for b in nearby_blocks)

        new_light = "Red" if train_nearby else "Green"
        new_bar = "Closed" if train_nearby else "Open"
        cond_str = f"Lights {new_light}, Bar {new_bar}"

        # Only update and log if something actually changed
        changed = False
        if crossing.get("lights") != new_light:
            data.update_track_data("railway_crossings", name, "lights", new_light)
            changed = True
            changes_made = True
        if crossing.get("bar") != new_bar:
            data.update_track_data("railway_crossings", name, "bar", new_bar)
            changed = True
            changes_made = True
        if crossing.get("condition") != cond_str:
            data.update_track_data("railway_crossings", name, "condition", cond_str)
            changed = True
            changes_made = True
        
        # Only log when state changes
        if changed:
            status = "Train Approaching" if train_nearby else "Clear"
            safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Crossing {name} - {status} ({cond_str})")

    # --- 2. Get current switch positions and build connection map ---
    switch_positions = {}
    connection_map = {}  # Maps block numbers to their possible next blocks
    
    # Build connection map from switches
    for switch_name, switch in switches.items():
        switch_positions[switch_name] = switch.get("direction", "")
        
        # Extract switch number from name (e.g., "Switch 85" -> "85")
        switch_num = switch_name.replace("Switch ", "").strip()
        
        # Get all connection options for this switch
        options = switch.get("options", [])
        
        # Parse each option to build connections
        for option in options:
            # Handle formats like "85-86", "100-85", "yard-57", etc.
            parts = option.split('-')
            if len(parts) == 2:
                block1 = '0' if 'yard' in parts[0].lower() else parts[0]
                block2 = '0' if 'yard' in parts[1].lower() else parts[1]
                
                # Add connection from block1 to block2
                if block1 not in connection_map:
                    connection_map[block1] = []
                if block2 not in connection_map[block1]:
                    connection_map[block1].append(block2)
                
                # Add connection from block2 to block1  
                if block2 not in connection_map:
                    connection_map[block2] = []
                if block1 not in connection_map[block2]:
                    connection_map[block2].append(block1)

    # --- 3. Handle track lights (signals) - FIXED: turn red when block is occupied ---
    for name, light in lights.items():
        # Extract block number from light name (e.g., "Light 1" -> "1")
        import re
        match = re.search(r'\d+', name)
        if match:
            block_num = match.group()
            linked_block_name = f"Block {block_num}"
        else:
            linked_block_name = light.get("linked_block", "")
        
        block_info = blocks.get(linked_block_name, {})

        # FIX: Light should be RED when block is occupied, GREEN when clear
        new_color = "Red" if block_info.get("occupied", False) else "Green"
        cond_str = f"Signal: {new_color}"

        # Only update and log if changed
        changed = False
        if light.get("signal") != new_color:
            data.update_track_data("light_states", name, "signal", new_color)
            changed = True
            changes_made = True
        if light.get("condition") != cond_str:
            data.update_track_data("light_states", name, "condition", cond_str)
            changed = True
            changes_made = True
        
        if changed:
            safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Light {name} set to {new_color} (Block {block_num} occupied: {block_info.get('occupied', False)})")

    # --- 4. Simple dynamic topology function ---
    def get_next_blocks(current_block, switch_positions):
        """Get the next blocks based on connection map"""
        current_num = current_block.replace("Block ", "").strip()
        
        # Check if we have connections for this block
        if current_num in connection_map:
            next_nums = connection_map[current_num]
            return [f"Block {next_num}" for next_num in next_nums]
        
        # Fallback: simple sequential logic for testing
        try:
            current_int = int(current_num)
            next_num = current_int + 1
            if f"Block {next_num}" in blocks:
                return [f"Block {next_num}"]
        except ValueError:
            pass
            
        return []

    # --- 5. NEW: Calculate authority based on suggested authority from connected blocks ---
    def calculate_authority_from_suggested(block_name, blocks, switch_positions):
        """Calculate authority based on suggested authority from next blocks"""
        current_num = block_name.replace("Block ", "").strip()
        current_block = blocks.get(block_name, {})
        
        # If block is occupied or faulted, authority is 0
        if current_block.get("occupied", False) or current_block.get("faulted", False):
            return 0
        
        # Get next blocks
        next_blocks = get_next_blocks(block_name, switch_positions)
        
        # Find the minimum suggested authority from next blocks
        min_next_authority = float('inf')
        
        for next_block_name in next_blocks:
            next_block = blocks.get(next_block_name, {})
            # Get suggested authority from the next block
            suggested_auth = data.suggested_authority.get(current_line, {}).get(
                next_block_name.replace("Block ", ""), 0)
            
            # Convert to int if it's a string
            if isinstance(suggested_auth, str):
                try:
                    suggested_auth = int(suggested_auth)
                except ValueError:
                    suggested_auth = 0
            
            min_next_authority = min(min_next_authority, suggested_auth)
        
        # If no next blocks found, use default authority
        if min_next_authority == float('inf'):
            return 15  # Default authority when no path constraints
        
        # Authority is one less than the minimum suggested authority of next blocks
        return max(0, min_next_authority - 1)

    # --- 6. Update authority and speed for each block ---
    for block_name, block in blocks.items():
        current_faulted = block.get("faulted", False)
        current_occupied = block.get("occupied", False)
        
        # NEW: Calculate authority based on suggested authority from connected blocks
        new_authority = calculate_authority_from_suggested(block_name, blocks, switch_positions)
        
        # Speed calculation: 31 mph if authority > 0 and not faulted, else 0
        new_speed = 31 if new_authority > 0 and not current_faulted else 0

        # Track changes for logging (only log actual changes)
        old_authority = block.get("authority", -1)
        old_speed = block.get("speed", -1)
        
        authority_changed = (old_authority != new_authority)
        speed_changed = (old_speed != new_speed)
        
        if authority_changed:
            data.update_block_in_track_data(block.get("number"), "authority", new_authority)
            changes_made = True
            
        if speed_changed:
            data.update_block_in_track_data(block.get("number"), "speed", new_speed)
            changes_made = True
        
        # Only add to authority_changes if something actually changed
        if authority_changed or speed_changed:
            authority_changes[block_name] = (new_authority, new_speed, current_occupied)

        # Sync block occupancy and faulted status (with error handling)
        block_num = str(block.get("number", block_name.replace("Block ", "")))
        try:
            for idx, row in enumerate(data.block_data):
                if row[1] == current_line and str(row[2]) == str(block_num):
                    # Update occupancy
                    block_occupied_in_data = (row[0] == "Yes")
                    if block.get("occupied") != block_occupied_in_data:
                        block["occupied"] = block_occupied_in_data
                        changes_made = True
                    
                    # Update faulted status
                    if len(row) > 3:
                        block_faulted_in_data = (row[3] == "Yes")
                        if block.get("faulted") != block_faulted_in_data:
                            block["faulted"] = block_faulted_in_data
                            changes_made = True
                    break
        except Exception as e:
            safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} WARNING: Error syncing block {block_num}: {e}")

    # --- 7. Log authority changes only once per block per cycle ---
    for block_name, (authority, speed, occupied) in authority_changes.items():
        block_num = block_name.replace("Block ", "")
        status = "OCCUPIED" if occupied else "CLEAR"
        safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Block {block_num} ({status}) - Authority: {authority}, Speed: {speed} mph")

    # --- 8. Update commanded_values for right panel (with error handling) ---
    try:
        # Check if commanded_values exists, if not, skip this section
        if not hasattr(data, 'commanded_values'):
            return  # Skip if commanded_values doesn't exist
        
        if current_line not in data.commanded_values:
            data.commanded_values[current_line] = {}
        
        for block_name, block in blocks.items():
            block_num = str(block.get("number", block_name.replace("Block ", "")))
            authority = block.get("authority", 0)
            speed = block.get("speed", 0)
            
            data.commanded_values[current_line][block_num] = {
                "authority": str(authority),
                "speed": str(speed)
            }
    except Exception as e:
        safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} WARNING: Error updating commanded_values: {e}")

    # Notify callbacks if changes were made (with error handling)
    if changes_made and hasattr(data, 'on_data_update'):
        for callback in data.on_data_update:
            try:
                callback()
            except Exception as e:
                safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} WARNING: Callback error: {e}")