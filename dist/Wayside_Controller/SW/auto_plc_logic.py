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
    track = data.filtered_track_data

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
            data.update_track_data("crossings", name, "lights", new_light)
            changed = True
            changes_made = True
        if crossing.get("bar") != new_bar:
            data.update_track_data("crossings", name, "bar", new_bar)
            changed = True
            changes_made = True
        if crossing.get("condition") != cond_str:
            data.update_track_data("crossings", name, "condition", cond_str)
            changed = True
            changes_made = True
        
        # Only log when state changes
        if changed:
            status = "Train Approaching" if train_nearby else "Clear"
            safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Crossing {name} - {status} ({cond_str})")

    # --- 2. Get current switch positions ---
    switch_positions = {}
    for switch_name, switch in switches.items():
        switch_positions[switch_name] = switch.get("direction", "")

    # --- 3. Handle track lights (signals) - only log changes ---
    for name, light in lights.items():
        linked_block_name = light.get("linked_block")
        if not linked_block_name:
            # Try to extract block number from light name
            import re
            match = re.search(r'\d+', name)
            if match:
                linked_block_name = f"Block {match.group()}"
        
        block_info = blocks.get(linked_block_name, {})

        new_color = "Red" if block_info.get("occupied", False) else "Green"
        cond_str = f"Signal: {new_color}"

        # Only update and log if changed
        changed = False
        if light.get("signal") != new_color:
            data.update_track_data("lights", name, "signal", new_color)
            changed = True
            changes_made = True
        if light.get("condition") != cond_str:
            data.update_track_data("lights", name, "condition", cond_str)
            changed = True
            changes_made = True
        
        if changed:
            safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Light {name} set to {new_color}")

    # --- 4. Define track topology with completely separate branches ---
    def get_next_blocks(current_block, switch_positions):
        """Get the next blocks based on current block and switch positions"""
        block_num = current_block.replace("Block ", "")
        
        # Main line blocks
        if block_num == "1": return ["Block 2"]
        elif block_num == "2": return ["Block 3"]
        elif block_num == "3": return ["Block 4"]
        elif block_num == "4": return ["Block 5"]
        elif block_num == "5":
            # Block 5 is a switch - check which way it's set
            switch_5_direction = switch_positions.get("Switch 5", "5-6")
            if "11" in switch_5_direction:
                return ["Block 11"]  # Switch set to 11 path
            else:
                return ["Block 6"]   # Switch set to 6 path (default)
        elif block_num == "6": return ["Block 7"]
        elif block_num == "7": return ["Block 8"]
        elif block_num == "8": return ["Block 9"]
        elif block_num == "9": return ["Block 10"]
        elif block_num == "10": return []  # End of branch 6-10
        elif block_num == "11": return ["Block 12"]
        elif block_num == "12": return ["Block 13"]
        elif block_num == "13": return ["Block 14"]
        elif block_num == "14": return ["Block 15"]
        elif block_num == "15": return ["Block 16"]
        else:
            return []

    # --- 5. Calculate authority using BFS to find distance to nearest occupied block ---
    def find_distance_to_occupied(start_block, blocks, switch_positions, visited=None):
        if visited is None:
            visited = set()
        
        if start_block in visited:
            return float('inf')
        
        visited.add(start_block)
        
        current_block_data = blocks.get(start_block, {})
        
        # If this block is occupied, distance is 0
        if current_block_data.get("occupied", False):
            return 0
        
        # If this block is faulted, treat as occupied
        if current_block_data.get("faulted", False):
            return 0
        
        # Check next blocks based on track topology and switch positions
        next_blocks = get_next_blocks(start_block, switch_positions)
        min_distance = float('inf')
        
        for next_block in next_blocks:
            if next_block in blocks:
                distance = 1 + find_distance_to_occupied(next_block, blocks, switch_positions, visited.copy())
                min_distance = min(min_distance, distance)
        
        return min_distance

    # --- 6. Update authority and speed for each block ---
    for block_name, block in blocks.items():
        current_faulted = block.get("faulted", False)
        current_occupied = block.get("occupied", False)
        
        # Calculate distance to nearest occupied block along the active path
        distance = find_distance_to_occupied(block_name, blocks, switch_positions)
        
        # Authority calculation:
        if current_faulted:
            new_authority = 0
        elif current_occupied:
            new_authority = 15  # Occupied block gets full authority
        elif distance == float('inf'):
            new_authority = 15  # No occupied blocks ahead
        else:
            # Authority = distance to nearest occupied block - 1
            # So block right before occupied gets 0
            new_authority = max(0, distance - 1)
        
        # Speed calculation: 31 mph if authority > 0 and not faulted, else 0
        new_speed = 31 if new_authority > 0 and not current_faulted else 0

        # Track changes for logging (only log actual changes)
        old_authority = block.get("authority", -1)
        old_speed = block.get("speed", -1)
        
        authority_changed = (old_authority != new_authority)
        speed_changed = (old_speed != new_speed)
        
        if authority_changed:
            block["authority"] = new_authority
            changes_made = True
            
        if speed_changed:
            block["speed"] = new_speed
            changes_made = True
        
        # Only add to authority_changes if something actually changed
        if authority_changed or speed_changed:
            authority_changes[block_name] = (new_authority, new_speed, current_occupied)

        # Sync block occupancy and faulted status
        block_num = str(block.get("number", block_name.replace("Block ", "")))
        for idx, row in enumerate(data.block_data):
            if row[1] == current_line and str(row[2]) == str(block_num):
                # Update occupancy
                block_occupied_in_data = (row[0] == "Yes")
                if block.get("occupied") != block_occupied_in_data:
                    block["occupied"] = block_occupied_in_data
                    safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Block {block_num} occupancy changed to {row[0]}")
                    changes_made = True
                
                # Update faulted status
                if len(row) > 3:
                    block_faulted_in_data = (row[3] == "Yes")
                    if block.get("faulted") != block_faulted_in_data:
                        block["faulted"] = block_faulted_in_data
                        safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Block {block_num} fault status changed to {row[3]}")
                        changes_made = True
                break

    # --- 7. Log authority changes only once per block per cycle ---
    for block_name, (authority, speed, occupied) in authority_changes.items():
        block_num = block_name.replace("Block ", "")
        status = "OCCUPIED" if occupied else "CLEAR"
        safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} PLC: Block {block_num} ({status}) - Authority: {authority}, Speed: {speed} mph")

    # --- 8. Update commanded_values for right panel ---
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

    # Notify callbacks if changes were made
    if changes_made and hasattr(data, 'on_data_update'):
        for callback in data.on_data_update:
            try:
                callback()
            except Exception as e:
                safe_log(f"{datetime.now():%Y-%m-%d %H:%M:%S} WARNING: Callback error: {e}")