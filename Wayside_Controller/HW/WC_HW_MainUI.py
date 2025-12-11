import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageTk
from plc_controller import PLCController
import os, sys
from time import strftime
from threading import Timer
import json
# import green_line
# import red_line


#############################################
# MAKE EVERYTHING GO IN MESSAGE LOG ON UI #
#############################################

# from Clock import clock
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from clock import Clock
from TrainSocketServer import TrainSocketServer
########################################################################################################################


# Backend Data Structures (same as before)
# Traffic light blocks:
        # Green Line: {1, 62, 76, 100, 150}
        # Red Line: {1, 10, 15, 28, 32, 39, 43, 53, 66, 67, 71, 72, 76}

commanded_speed = []
commanded_authority = []
switch_positions = []
light_states = []
block_occupancy = []

blocks = []
track_direction = []
railway_crossing = []
# heaters_work = []

switch_locations = []
light_location = []
railway_location = []
station_location = []

# environmental_temp: float
# failure_modes = []
# track_circuit_fail: bool
# railway_crossing_fail: bool
# power_fail: bool

# ticket_sales = []
# passengers_boarding = []
# passengers_disembarking = []
# train_occupancy = []
# active_trains = []
######
##############


def update_suggested_speed_display(speed, authority=None):
    """Update the suggested speed and authority display in the right panel"""
    try:
        if hasattr(right_panel, 'update_suggested_speed'):
            right_panel.update_suggested_speed(speed)
        if authority is not None and hasattr(right_panel, 'update_suggested_authority'):
            right_panel.update_suggested_authority(authority)
        if authority is not None:
            # Fallback: try to find and update the label directly
            formatted_speed = f"{speed:.2f} mph"
            add_to_message_log(f"CTC Speed received (UI update pending): {formatted_speed}, Authority={authority} blocks")
        else: 
            add_to_message_log(f"CTC Speed recieved: {formatted_speed} mph")
    except Exception as e:
        add_to_message_log(f"ERROR updating speed display: {e}")


# installing update_callback function
def update_callback(message):
    """Socket server callback function"""
    print(f"Socket message recieved: {message}")
    add_to_message_log(f"Socket: {message}")


# Example of Process Function:
def _process_message(self, data, connection=None, server_instance=None):
    """Process incoming messages from Test UI"""
    try:
        print(f"\n{'='*60}")
        print(f"TRACK HW MAIN UI: Received message from CTC")
        print(f"Data type: {type(data)}")
        print(f"Data: {data}")

        # Try to parse
        try:

            print(f"\n{'='*60}")
            print(f"TRACK HW MAIN UI: Received message from CTC")
            print(f"Data type: {type(data)}")
            print(f"Data: {data}")

        # 1. Handle connection test FIRST
            if isinstance(data, str) and data.strip() == "CTC":
                print("CTC connection test received - sending ACK")
                add_to_message_log("CTC connection test received")
                if connection:
                    try:
                        connection.sendall(b"CTC_ACK")
                        print("Sent CTC_ACK response")
                    except Exception as e:
                        print(f"Error sending ACK: {e}")
                return  # IMPORTANT: Stop processing here for connection tests

            import json
            message_data = json.loads(data)
            print(f"Parsed: {message_data}")
        
        # Call your handler
            if hasattr(test_data, 'handle_ctc_message'):
                test_data.handle_ctc_message(message_data)
        except:
            print(f"Could not parse: {data}")
    
        print(f"{'='*60}")
        print(f"{'='*60}\n")
        
        
        # 2. Parse message
        message_data = None
        if isinstance(data, str):
            try:
                # Parse as JSON (your data IS valid JSON from CTC)
                message_data = json.loads(data)
                print(f"Parsed JSON data: {message_data}")
                print(f"Raw data: {data}")
                print(f"Parsed message_data: {message_data}")
                print(f"Type of message_data: {type(message_data)}")
            except json.JSONDecodeError:
                # If not JSON, check if it's a Python dict string
                try:
                    import ast
                    if data.startswith('{') and data.endswith('}'):
                        message_data = ast.literal_eval(data)
                        print(f"Parsed as Python dict: {message_data}")
                    else:
                        # Simple string commands
                        message_data = {'message': data}
                except:
                    message_data = {'message': data}
        elif isinstance(data, dict):
            message_data = data
            print(f"Data is already a dictionary: {data}")
        else:
            print(f"Unknown data type: {type(data)}")
            return
      
        # 3. Process command
        command = message_data.get('command', '')
        value = message_data.get('value', '')
        
        print(f"Processing command: {command}, value: {value}")

        #########################################################################################
                # After parsing speed and authority values:
        print(f"Processing suggested update: {track} Block {block} -> Speed:{speed}, Auth:{authority}")

        # CALL YOUR EXISTING FUNCTIONS
        if hasattr(right_panel, 'update_suggested_speed'):
            right_panel.update_suggested_speed(speed)
            print(f"Called update_suggested_speed({speed})")

        if hasattr(right_panel, 'update_suggested_authority'):
            right_panel.update_suggested_authority(authority)
            print(f"Called update_suggested_authority({authority})")

        # Also select the block
        if hasattr(right_panel, 'block_combo') and block:
            right_panel.block_combo.set(str(block))
            print(f"Selected block {block} in dropdown")

        add_to_message_log(f"CTC Suggested: Block {block} - Speed: {speed:.3f} mph, Authority: {authority} blocks")
        
        ############################################################################
        
        if command == 'update_speed_auth':
            # CALL THE EXISTING HANDLER IN UITestData
            # Extract block from the value dictionary
            block = value.get('block', '')
            track = value.get('track', '')
            speed_str = value.get('speed', '0')
            authority_str = value.get('authority', '0')
            value_type = value.get('value_type', 'suggested')
            print(f"DEBUG: Calling test_data._handle_speed_auth_update with: {value}")
            
            # Check if test_data has the method
            if hasattr(test_data, '_handle_speed_auth_update'):
                test_data._handle_speed_auth_update(value)
            elif hasattr(test_data, 'handle_ctc_message'):
                test_data.handle_ctc_message(message_data)
            else:
                # Fallback: Update right panel directly
                print(f"No handler found, updating right panel directly")
                if isinstance(value, dict):
                    track = value.get('track', '')
                    speed_str = value.get('speed', '0')
                    authority_str = value.get('authority', '0')
                    
                    try:
                        speed = round(float(speed_str),2)
                        if hasattr(right_panel, 'update_suggested_speed'):
                            right_panel.update_suggested_speed(speed)
                    except:
                        speed = 0.0
                        pass
                    
                    try:
                        authority = int(authority_str)
                        if hasattr(right_panel, 'update_suggested_authority'):
                            right_panel.update_suggested_authority(authority)
                    except:
                        authority = 0
                        pass
                    
                    add_to_message_log(f"CTC Update: Speed={speed_str}, Authority={authority_str}")
        # =====================================================================
        # HANDLE CTC MESSAGES
        # =====================================================================        
        elif command == 'ctc_suggestion':
            # Handle speed suggestion
            print(f"\n[{timestamp}] CTC Suggestion Received")
            add_to_message_log(f"CTC Update: Speed={speed_str}, Authority={authority_str}")
            handle_ctc_suggested_speed(value)

        elif command == 'set_block_occupancy':
            pass  # Add handling if needed
        elif command == 'MAINT':
                # Handle maintenance request from CTC
                print("CTC Maintenance Request Received")
                add_to_message_log("CTC: Maintenance Request Received")
                
                # Update maintenance LED
                maint_led.config(bg="orange", text="MAINT REQ")
                add_to_message_log("Maintenance Request LED activated")
            
        elif command == 'set_switch_position':
            # Legacy switch command - redirect to SW command
            print(f"Legacy set_switch_position command: {value}")
            add_to_message_log(f"Switch position update: {value}")
        elif command == "SW":
            # Handle switch command from CTC - FOR TRACK HW
            print(f"CTC SWITCH COMMAND received: {value}")
        # =====================================================================
        # HANDLE TRACK MODEL INCOMING MESSAGES
        # =====================================================================
        
        elif command == 'update_occupancy' or command == 'occupancy':
            block = value.get('block', '')
            track = value.get('track', test_data.current_line)
            occupied = value.get('occupied', False)
            
            print(f"Track Model Occupancy Update: Block {block} on {track} -> {occupied}")
            add_to_message_log(f"Track Model: Block {block} Occupancy = {occupied}")
            
            # Update block data
            occupied_str = "Yes" if occupied else "No"
            for idx, row in enumerate(test_data.block_data):
                if str(row[2]) == str(block) and row[1] == track:
                    test_data.block_data[idx][0] = occupied_str
                    break
            
            # Send occupancy to CTC
            if hasattr(test_data, 'send_occupancy'):
                test_data.send_occupancy(track, block, occupied_str)
        
        elif command == 'update_light' or command == 'light_state':
            block = value.get('block', '')
            track = value.get('track', test_data.current_line)
            color = value.get('color', 'Green')
            
            print(f"Track Model Light Update: Block {block} on {track} -> {color}")
            add_to_message_log(f"Track Model: Light {block} = {color}")
            
            # Update track_data
            light_name = f"Light {block}"
            if light_name in test_data.track_data.get("lights", {}):
                test_data.track_data["lights"][light_name]["signal"] = color
            
            # Send light state to CTC
            if hasattr(test_data, 'send_light_state'):
                test_data.send_light_state(track, block, color)
        
        elif command == 'update_crossing' or command == 'crossing_state':
            block = value.get('block', '')
            track = value.get('track', test_data.current_line)
            bar = value.get('bar', 'Open')
            lights = value.get('lights', 'Off')
            
            print(f"Track Model Crossing Update: Block {block} on {track} -> Bar:{bar}")
            add_to_message_log(f"Track Model: Crossing {block} Bar={bar}")
            
            # Update track_data
            crossing_name = f"Railway Crossing: {block}"
            if crossing_name in test_data.track_data.get("crossings", {}):
                test_data.track_data["crossings"][crossing_name]["bar"] = bar
                test_data.track_data["crossings"][crossing_name]["lights"] = lights
            
            # Send railway state to CTC
            if hasattr(test_data, 'send_railway_state'):
                test_data.send_railway_state(track, block, bar)

            if isinstance(value, list) and len(value) >= 2:
                location = str(value[0])
                line = value[1]
                
                # Log the switch command
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"{timestamp} CTC REQUEST: Toggle Switch {location} on {line} track"
                message_logger.log(log_message, "WARNING")
                # Also use the old function for compatibility
                add_to_message_log(f"CTC Switch Command: Block {location} on {line} Line")
                
                # Update the left panel switch display if it matches current line
                if line.lower() == test_data.current_line.lower():
                    print(f"Updating switch for current line: {line}")
                    
                    # Find and update the appropriate switch in left panel
                    if hasattr(left_panel, 'switch_selector'):
                        # Try to find a switch that includes this block
                        found_switch = None
                        for switch_name in test_data.track_data.get("switches", {}):
                            # Check if location is part of the switch name
                            if location in switch_name:
                                found_switch = switch_name
                                break
                            # Check if location matches numbers in switch name
                            import re
                            numbers = re.findall(r'\d+', switch_name)
                            if location in numbers:
                                found_switch = switch_name
                                break
                        
                        if found_switch:
                            print(f"Found matching switch: {found_switch}")
                            
                            # Update the switch selector
                            left_panel.switch_selector.set(found_switch)
                            left_panel.update_switch_display()
                            
                            # Toggle the switch direction
                            current_direction = test_data.track_data["switches"][found_switch]["direction"]
                            
                            # Determine new direction (toggle between two positions)
                            # This depends on your switch logic - here's an example:
                            if "Blocks" in current_direction:
                                # Extract block numbers
                                import re
                                blocks = re.findall(r'\d+', current_direction)
                                if len(blocks) >= 2:
                                    # Toggle the direction (swap blocks or change pattern)
                                    # Example: If current is "Blocks 12-13", change to "Blocks 12-1"
                                    # You'll need to customize this based on your actual switch logic
                                    if "12-13" in current_direction:
                                        new_direction = "Blocks 12-1"
                                    elif "28-29" in current_direction:
                                        new_direction = "Blocks 28-150"  # Example toggle
                                    else:
                                        # Default toggle - swap the two numbers
                                        new_direction = f"Blocks {blocks[1]}-{blocks[0]}"
                                    
                                    # Update the direction
                                    test_data.track_data["switches"][found_switch]["direction"] = new_direction
                                    left_panel.switch_direction.set(new_direction)
                                    
                                    # Log the change
                                    message_logger.log(f"Switch {found_switch}: Direction changed to {new_direction} by CTC")
                            
                            add_to_message_log(f"CTC Switch Command: Updated {found_switch} for Block {location}")
                        else:
                            print(f"No matching switch found for block {location}")
                            add_to_message_log(f"CTC Switch Command: No switch found for Block {location}")
                    else:
                        print("Left panel switch_selector not found")
                else:
                    print(f"Ignoring switch command for different line: {line} (we're on {test_data.current_line})")
                
                # Send acknowledgment back to CTC
                if hasattr(test_data, 'server1'):
                    ack_message = {
                        "command": 'SW_ACK',
                        "value": {
                            "location" : location,
                            "line": line,
                            "status": 'processed',
                            "timestamp": timestamp
                        }
                    }
                    test_data.server1.send_to_ui('CTC', ack_message)
                    print(f"Sent SW_ACK to CTC for switch {location}")  
            
        else:
            print(f"Unknown command: {command} with value: {value}")
            
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
    # Store as simple attributes
    right_panel.update_suggested_speed = speed
    right_panel.update_suggested_authority = authority

    # Update display
    right_panel.update_suggested_display()

def handle_ctc_suggested_speed(speed_data):
    """
    Handle CTC suggested speed messages and convert to float with 3 decimal places        """
    try:
        suggested_speed = None
    
        # Handle different input formats
        if isinstance(speed_data, (int, float)):
                suggested_speed = float(speed_data)
        elif isinstance(speed_data, str):
                # Look for float value in string
            if "float:" in speed_data:
                # Use your existing code
                import re
                float_match = re.search(r'float:\s*([0-9]*\.?[0-9]+)', speed_data)
                if float_match:
                    speed_str = float_match.group(1)
                    suggested_speed = float(speed_str)
            else:
                # Try direct conversion if it's just a number string
                try:
                    suggested_speed = float(speed_data)
                except:
                    pass
            
        elif isinstance(speed_data, dict):
            # Use your existing dictionary handling
            if 'Suggested_speed' in speed_data:
                speed_value = speed_data['Suggested_speed']
                if isinstance(speed_value, str) and "float:" in speed_value:
                    speed_str = speed_value.split("float:")[1].strip()
                    suggested_speed = float(speed_str)
                else:
                    suggested_speed = float(speed_value)
            elif 'value' in speed_data:
                suggested_speed = float(speed_data['value'])
            elif 'speed' in speed_data:
                suggested_speed = float(speed_data['speed'])

            # Try different possible keys
            for key in ['Suggested_speed', 'value', 'speed']:
                if key in speed_data:
                    val = speed_data[key]
                    if isinstance(val, str) and "float:" in val:
                        suggested_speed = float(val.split("float:")[1].strip())
                    else:
                        suggested_speed = float(val)
                    break
    
        # Format to 3 decimal places if conversion was successful
        if suggested_speed is not None:
            speed_mps = suggested_speed
            speed = speed_mps * 2.23694
            # Log with conversion info
            add_to_message_log(f"CTC Suggested Speed Received: {formatted_speed:.2f} mph ({speed_mps:.2f} m/s)")
            formatted_speed = round(suggested_speed, 3)
            add_to_message_log(f"CTC Suggested Speed Received: {formatted_speed:.2f} mph")
            # Message log
            message_logger.log(add_to_message_log, "INFO")
            
            # Update display
            update_suggested_speed_display(formatted_speed)
            update_suggested_speed_display(formatted_speed)
            return formatted_speed
        else:
            add_to_message_log("ERROR: Could not extract speed from CTC message")
        
    except Exception as e:
        add_to_message_log(f"ERROR: Processing CTC speed message - {e}")

    return None
    

##############################################################################################################################
###############################################################################################################################
#############################################################################################################################
# Enhanced Mock data class for both panels
class UITestData:
    def __init__(self):
        # # Define your block to section mapping
        # Callbacks
        self.on_line_change = []
        self.on_block_change = []
        self.block_sections = {}
        # Current line
        self.current_line = "Green"

        # Maintenance mode
        self.maintenance_mode = False
        
        # Initialize block_data with sample data FIRST
        self.block_data = []
        self.filtered_block_data = []
        # Initialize track data
        self.track_data = {
        "crossings": {},
        "switches": {},
        "lights": {}
        }
        self.filtered_track_data = self.track_data.copy()

         # Initialize socket server
        # self.initialize_socket_server()
    # Define your block to section mapping FIRST
        self.green_sections = {
        "1": "A", "2": "A", "3": "A", "4": "B", "5": "B", "6": "B",
        "7": "C", "8": "C", "9": "C", "10": "C", "11": "C", "12": "C",
        "13": "D", "14": "D", "15": "D", "16": "D",
        "17": "E", "18": "E", "19": "E", "20": "E",
        "21": "F", "22": "F", "23": "F", "24": "F", "25": "F", "26": "F", "27": "F", "28": "F",
        "29": "G", "30": "G", "31": "G", "32": "G",
        "33": "H", "34": "H", "35": "H",
        "36": "I", "37": "I", "38": "I", "39": "I", "40": "I", "41": "I", "42": "I", "43": "I",
        "44": "I", "45": "I", "46": "I", "47": "I", "48": "I", "49": "I", "50": "I", "51": "I",
        "52": "I", "53": "I", "54": "I", "55": "I", "56": "I", "57": "I",
        "58": "J", "59": "J", "60": "J", "61": "J", "62": "J",
        "63": "K", "64": "K", "65": "K", "66": "K", "67": "K", "68": "K",
        "69": "L", "70": "L", "71": "L", "72": "L", "73": "L",
        "150": "Z"
        }

        self.red_sections = {
        "74": "M", "75": "M", "76": "M",
        "77": "N", "78": "N", "79": "N", "80": "N", "81": "N", "82": "N", "83": "N", "84": "N", "85": "N",
        "86": "O", "87": "O", "88": "O",
        "89": "P", "90": "P", "91": "P", "92": "P", "93": "P", "94": "P", "95": "P", "96": "P", "97": "P",
        "98": "Q", "99": "Q", "100": "Q",
        "101": "R",
        "102": "S", "103": "S", "104": "S",
        "105": "T", "106": "T", "107": "T", "108": "T", "109": "T",
        "110": "U", "111": "U", "112": "U", "113": "U", "114": "U", "115": "U", "116": "U",
        "117": "V", "118": "V", "119": "V", "120": "V", "121": "V",
        "122": "W", "123": "W", "124": "W", "125": "W", "126": "W", "127": "W", "128": "W", 
        "129": "W", "130": "W", "131": "W", "132": "W", "133": "W", "134": "W", "135": "W",
        "136": "W", "137": "W", "138": "W", "139": "W", "140": "W", "141": "W", "142": "W", "143": "W",
        "144": "X", "145": "X", "146": "X",
        "147": "Y", "148": "Y", "149": "Y",
        # Yard to F sections
        "1": "Yard", "2": "Yard", "3": "Yard",
        "4": "A", "5": "A", "6": "A",
        "7": "B", "8": "B", "9": "B",
        "10": "C", "11": "C", "12": "C",
        "13": "D", "14": "D", "15": "D",
        "16": "E", "17": "E", "18": "E", "19": "E", "20": "E",
        "21": "F", "22": "F", "23": "F"
        }
    
    # LOAD DATA - Force load initial data
        self.load_initial_data()

    def load_initial_data(self):
        """Load initial data for the current line"""
        print(f"\n=== Loading initial data for {self.current_line} Line ===")
    
    # Try to load from file
        filename = "green_line.txt" if self.current_line == "Green" else "red_line.txt"
        
        # call load data 
        # self.load_line_data(filename)
    
    # Check if file exists
        import os
        if os.path.exists(filename):
            print(f"Found file: {filename}")
            loaded_data = self.load_complete_track_data(filename)
            if loaded_data:
                self.block_data = loaded_data
                print(f"Successfully loaded {len(self.block_data)} rows from {filename}")
            else:
                print(f"Failed to load from {filename}, using emergency data")
                self.block_data = self.create_emergency_data(filename)
        else:
            print(f"File {filename} not found, using emergency data")
            self.block_data = self.create_emergency_data(filename)
    
    # Initialize filtered data
        self.filtered_block_data = self.block_data.copy()
        print(f"Total rows in block_data: {len(self.block_data)}")
        if self.block_data:
            print(f"Sample row: {self.block_data[0]}")
        
    # SOCKET SERVER
        self.server1 = TrainSocketServer(port=12344, ui_id="Track HW")
        self.server1.set_allowed_connections(["WC_HW_TestUI", "CTC", "Track Model"])
        self.server1.start_server(_process_message)
    
    # Connect to other UIs
        self.server1.connect_to_ui('localhost', 12346, "WC_HW_TestUI")
        self.server1.connect_to_ui('localhost', 12341, "CTC")
        self.server1.connect_to_ui('localhost', 12344, "Track Model")
    
    # Call this after a short delay
        if hasattr(self, 'root'):
            self.root.after(2000, self.verify_server_running)    
        
        # In UITestData.__init__ after server starts:
        print(f"\n[TRACK HW DEBUG] Server started on port 12344")
        print(f"[TRACK HW DEBUG] Waiting for connections...")

# Add to _process_message:
        # print(f"[TRACK HW] Connection from: {12341}")

    def load_complete_track_data(self, filename):
        """Load all green line blocks, merging sections where available"""
        # complete_data = []
        data = []
        # sections = {}
        try:
            print(f"\n{'='*60}")
            print(f"LOADING FILE: {filename}")
            print(f"{'='*60}")

            import os
            # Debug statments:
            # print(f"Loading track data from: {filename}")
            # print(f"File exists: {os.path.exists(filename)}")
            # print(f"block_sections defined: {hasattr(self, 'block_sections')}")

             # Read the entire file first to see content
            # with open(filename, 'r') as file:
            #     raw_content = file.read()
                # print(f"Raw content length: {len(raw_content)} chars")
                # print(f"Raw content (first 500 chars):\n{raw_content[:500]}")
                # print(f"Raw content ends with: {repr(raw_content[-50:])}")

        # Simple file read
            with open(filename, 'r') as file:
                lines = file.readlines()
                print(f"\nNumber of lines: {len(lines)}")

            green_sections = self.green_sections # use class attributes
            red_sections = self.red_sections # use class attribute

            # Combine sections for lookup
            all_sections = {**green_sections, **red_sections}

            # print(f"SUCCESS: Read {len(lines)} lines from {filename}")
            start_line = 0
            if len(lines) > 0 and ("Line,Block" in lines[0] or "Line, Block, Section" in lines[0]):
                print(f"Skipping header: {lines[0].strip()}")
                start_line = 1  # Skip header line

            line_count = 0
            for i in range(start_line, len(lines)):
                line = lines[i].strip()
                if not line:  # Skip empty lines
                    continue
                
                line_count += 1
                # Parse: "Green,1,Light" or "Red,1,Yard"
                parts = line.split(',')
                parts = [p.strip() for p in parts]
                
                # Show first few lines for debugging
                if line_count <= 3:
                    print(f"Raw line {line_count}: {parts}")
                
                # We need at least 2 parts (Line, Block)
                if len(parts) >= 2:
                # Try different parsing strategies based on content
                    # if parts[0] in ["Green", "Red", "Blue"]:
                    # Format: Line, Block, Infrastructure
                        line_name = parts[0]
                        block_num = parts[1]
                    
                    # Try to get section (might be in parts[2] or parts[3])
                        # Get section from mapping based on line
                        if line_name == "Green":
                            section = green_sections.get(block_num, "Unknown")
                        else:  # Red line
                            section = red_sections.get(block_num, "Unknown")
                
                # Default occupancy to "No"
                        occupied = "No"
                
                # Create 4-column row: [Occupancy, Line, Block, Section]
                        row = [occupied, line_name, block_num, section]
                        data.append(row)
                
                # Debug first few conversions
                        if line_count <= 3:
                            print(f"  -> Converted to: {row}")
        
            print(f"\nSuccessfully converted {len(data)} rows")
            # Print section statistics
            sections = set(self.block_sections.values())
            print(f"Found sections in {filename}: {sorted(sections)}")

            if data:
                print("\nFirst 3 converted rows:")
                for i, row in enumerate(data[:5]):
                    print(f"  Row{i+1}: {row}")
                # return data
                print("\nLast 5 converted rows:")
            
            for i, row in enumerate(data[-5:]):
                print(f"  {len(data)-4+i}: {row}")

            # Show statistics
            green_rows = [r for r in data if r[1] == "Green"]
            red_rows = [r for r in data if r[1] == "Red"]
            print(f"\nStatistics:")
            print(f"  Green line rows: {len(green_rows)}")
            print(f"  Red line rows: {len(red_rows)}")
        
            return data
        
        except Exception as e:
            print(f"ERROR in load_complete_track_data: {e}")
        import traceback
        traceback.print_exc()
        
    def create_emergency_data(self, filename):
        """Create emergency data when file loading fails"""
        print(f"Creating emergency data for {filename}")
    
        emergency_data = []
    
        if "green" in filename.lower():
            # Green Line: Sections A-J and Z
            sections = {
            "1": "A", "2": "A", "3": "A", "4": "B", "5": "B", "6": "B",
            "7": "C", "8": "C", "9": "C", "10": "C", "11": "C", "12": "C",
            "13": "D", "14": "D", "15": "D", "16": "D",
            "17": "E", "18": "E", "19": "E", "20": "E",
            "21": "F", "22": "F", "23": "F", "24": "F", "25": "F", "26": "F", "27": "F", "28": "F",
            "29": "G", "30": "G", "31": "G", "32": "G",
            "33": "H", "34": "H", "35": "H",
            "36": "I", "37": "I", "38": "I", "39": "I", "40": "I", "41": "I", "42": "I", "43": "I",
            "44": "I", "45": "I", "46": "I", "47": "I", "48": "I", "49": "I", "50": "I", "51": "I",
            "52": "I", "53": "I", "54": "I", "55": "I", "56": "I", "57": "I",
            "58": "J", "59": "J", "60": "J", "61": "J", "62": "J",
            "63": "K", "64": "K", "65": "K", "66": "K", "67": "K", "68": "K",
            "69": "L", "70": "L", "71": "L", "72": "L", "73": "L",
            # Add Z section for Green line 
            "150": "Z"
        }
        
            for block_num, section in sections.items():
                occupied = "Yes" if int(block_num) % 5 == 0 else "No"
                emergency_data.append([occupied, "Green", block_num, section])
    
        else:  # Red line
            # Red Line: Sections J-N and Yard to F
            sections = {
            # J-N sections
            "74": "M", "75": "M", "76": "M",
            "77": "N", "78": "N", "79": "N", "80": "N", "81": "N", "82": "N", "83": "N", "84": "N", "85": "N",
            "86": "O", "87": "O", "88": "O",
            "89": "P", "90": "P", "91": "P", "92": "P", "93": "P", "94": "P", "95": "P", "96": "P", "97": "P",
            "98": "Q", "99": "Q", "100": "Q",
            "101": "R",
            "102": "S", "103": "S", "104": "S",
            "105": "T", "106": "T", "107": "T", "108": "T", "109": "T",
            "110": "U", "111": "U", "112": "U", "113": "U", "114": "U", "115": "U", "116": "U",
            "117": "V", "118": "V", "119": "V", "120": "V", "121": "V",
            "122": "W", "123": "W", "124": "W", "125": "W", "126": "W", "127": "W", "128": "W", 
            "129": "W", "130": "W", "131": "W", "132": "W", "133": "W", "134": "W", "135": "W",
            "136": "W", "137": "W", "138": "W", "139": "W", "140": "W", "141": "W", "142": "W", "143": "W",
            "144": "X", "145": "X", "146": "X",
            "147": "Y", "148": "Y", "149": "Y",
            # Yard to F sections
            "1": "Yard", "2": "Yard", "3": "Yard",
            "4": "A", "5": "A", "6": "A",
            "7": "B", "8": "B", "9": "B",
            "10": "C", "11": "C", "12": "C",
            "13": "D", "14": "D", "15": "D",
            "16": "E", "17": "E", "18": "E", "19": "E", "20": "E",
            "21": "F", "22": "F", "23": "F"
            }
        
            for block_num, section in sections.items():
                occupied = "Yes" if int(block_num) % 4 == 0 else "No"
                emergency_data.append([occupied, "Red", block_num, section])
        print(f"Created {len(emergency_data)} emergency rows")
        return emergency_data

    def verify_server_running(self):
        """Verify the socket server is actually running"""
        if hasattr(self, 'server1') and self.server1:
            print(f"=== SERVER VERIFICATION ===")
            print(f"Server running: {self.server1.running}")
            print(f"Server port: 12345")
            print(f"UI ID: {self.server1.ui_id}")
            print(f"Allowed connections: {self.server1.allowed_connections}")
        
        # Test if server socket is bound
        if hasattr(self.server1, 'server_socket'):
            print(f"Server socket: {self.server1.server_socket}")
            if self.server1.server_socket:
                print(f"Socket bound: {self.server1.server_socket.fileno() != -1}")
        print(f"=== END VERIFICATION ===")

    def create_clock_display(self, parent_frame):
        """Create a clock display in the UI"""
        clock_frame = tk.Frame(parent_frame, bg='#1a1a4d')
        clock_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Clock label
        self.clock_label = tk.Label(clock_frame, text="", 
                                   font=("Arial", 12, "bold"), 
                                   bg='#1a1a4d', fg='white')
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        
        # Start updating the clock display
        self.update_clock_display()
    
    def update_clock_display(self):
        """Update the clock display every second"""
        try:
            current_time = global_clock.getTime()
            self.clock_label.config(text=f"Time: {current_time}")
        except Exception as e:
            print(f"Clock error: {e}")
            self.clock_label.config(text="Time: --:--")
        
        # Update every second
        self.clock_label.after(1000, self.update_clock_display)

    def on_closing(self):
        print("Closing application...")
        try:
            global_clock.endTimer()
        except:
            # print(f"Error stopping clock: {e}")
            pass

        # Properly stop the socket server with comprehensive cleanup
        if hasattr(self, 'server1') and self.server1:
            try:
                # 1. First, notify connected clients
                if hasattr(self.server1, 'connections'):
                    disconnect_msg = {
                        "command": 'server_shutdown',
                        "message": 'Main UI is closing',
                        "timestamp": self.clock.getTime()
                    }
                    for ui_id, connection in list(self.server1.connections.items()):
                        try:
                            self.server1.send_to_ui(ui_id, disconnect_msg)
                        except:
                            pass
                
                # 2. Stop accepting new connections
                self.server1.running = False
                
                # 3. Close all active connections
                if hasattr(self.server1, 'connections'):
                    for ui_id, connection in list(self.server1.connections.items()):
                        try:
                            if hasattr(connection, 'close'):
                                connection.close()
                        except Exception as e:
                            print(f"Error closing connection to {ui_id}: {e}")
                    self.server1.connections.clear()
                
                # 4. Close the server socket
                if hasattr(self.server1, 'server_socket') and self.server1.server_socket:
                    try:
                        self.server1.server_socket.close()
                        print("Server socket closed")
                    except Exception as e:
                        print(f"Error closing server socket: {e}")
                
                # 5. Stop any running threads
                if hasattr(self.server1, 'listen_thread') and self.server1.listen_thread:
                    try:
                        self.server1.listen_thread.join(timeout=2.0)
                    except Exception as e:
                        print(f"Error joining listen thread: {e}")
                
                print("Socket server shutdown complete")
                
            except Exception as e:
                print(f"Error during socket server shutdown: {e}")
        
        # 6. Finally, destroy the root window
        if hasattr(self, 'root') and self.root:
            try:
                self.root.destroy()
                print("Root window destroyed")
            except Exception as e:
                print(f"Error destroying root window: {e}")
        
        print("Application closed successfully")

    def get_block_table_data(self):
        return self.filtered_block_data

    def update_block_data(self, row_index, col_index, new_value):
        if 0 <= row_index < len(self.block_data):
            self.block_data[row_index][col_index] = new_value
            print(f"Updated block data: row {row_index} = {self.block_data[row_index]}")
            # Trigger callbacks
            for callback in self.on_block_change:
                callback(row_index, col_index, new_value)

    def filter_block_data(self, search_term):
        if not search_term or search_term.strip() == "":
            self.filtered_block_data = self.block_data.copy()
        else:
            search_term = search_term.lower()
            self.filtered_block_data = [
                row for row in self.block_data
                if any(search_term in str(cell).lower() for cell in row)
            ]
   
    def is_changeable(self, component_type):
        """Check if a component type can be edited in current mode"""
        if not self.maintenance_mode:
            return False
        return self.maintenance_changes.get(component_type, False)

    def handle_ctc_message(self, message_data):
        """Unified handler for all CTC messages"""
        try:
            command = message_data.get('command')
            value = message_data.get('value')
            
            if command == 'update_speed_auth':
                # Handle speed+authority updates from CTC schedule screen
                self._handle_speed_auth_update(value)
                
            elif command == 'ctc_suggestion':
                # Handle old format speed-only messages
                self._handle_old_ctc_suggestion(value)
                
            elif command == 'set_block_occupancy':
                # Handle block occupancy
                self._handle_block_occupancy(value)
                
            # Add other commands as needed
                
        except Exception as e:
            add_to_message_log(f"ERROR handling CTC message: {e}")
    
    def _handle_speed_auth_update(self, data):
        """Handle speed and authority updates from CTC"""
        try:
            # # Log receipt of message
            # from datetime import datetime
            # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Handle different input formats from CTC
            if isinstance(data, dict):
            # Format 1: Direct dictionary with speed/authority
                if 'speed' in data and 'authority' in data:
                    speed_str = data.get('speed', '0').strip()
                    authority_str = data.get('authority', '0').strip()
                    block = data.get('block', '').strip()
                    track = data.get('track', '').strip()

                    # Only process if for current line
                    if track.lower() != self.current_line.lower():
                        return
                # Convert values
                try:
                    speed = round(float(speed_str), 3)
                except:
                    speed = 0.0
            
                try:
                    authority = int(authority_str)
                except:
                    authority = 0
            
            # Update display
                if hasattr(right_panel, 'update_suggested_speed'):
                    right_panel.update_suggested_speed(speed)
                if hasattr(right_panel, 'update_suggested_authority'):
                    right_panel.update_suggested_authority(authority)
            
            # Log update (below currently)
                # add_to_message_log(f"CTC Update: Speed={speed:.2f} mph, Authority={authority} blocks")

            ####################################################################################################################
            # 12/8 -- UPDATING WITH CTC SUGGESTED SPEED AND AUTHORITY 
                #  After parsing the message and getting the values:
            if track.lower() == test_data.current_line.lower():
                # Convert values
                speed = round(float(speed_str), 3)
                authority = int(authority_str)
                
            print(f"Updating display for block {block}: Speed={speed}, Auth={authority}")
            
            # DIRECT UPDATE - This is the key fix:
            if hasattr(right_panel, 'suggested_speed_label'):
                right_panel.suggested_speed_label.config(text=f"{speed:.3f} mph")
                print(f"Updated speed label to: {speed:.3f} mph")
            
            if hasattr(right_panel, 'suggested_auth_label'):
                right_panel.suggested_auth_label.config(text=f"{authority} blocks")
                print(f"Updated authority label to: {authority} blocks")
            
            # Also update the block selector to show block 63
            if hasattr(right_panel, 'block_combo') and block:
                right_panel.block_combo.set(block)

            add_to_message_log(f"CTC: Block {block} - Speed: {speed:.3f} mph, Authority: {authority} blocks")
            # Add to message log in the format you want
            message_logger.log(f"CTC SUGGESTION: Block {block} on {track} - Authority: {authority} blocks, Speed: {speed:.1f} mph", "INFO")
        except Exception as e:
            print(f"Error handling speed/auth update: {e}")
            add_to_message_log(f"ERROR processing CTC update: {e}")


    def handle_ctc_switch(self, switch_data):
        """Handle switch command from CTC"""
        try:
            if isinstance(switch_data, list) and len(switch_data) >= 2:
                location = str(switch_data[0])
                line = switch_data[1]
                
                print(f"CTC Switch Command: Block {location} on {line} Line")
                add_to_message_log(f"CTC Switch Command: Block {location} on {line} Line")
                
                # Update switch display if it matches current line
                if line.lower() == self.current_line.lower() and hasattr(left_panel, 'switch_selector'):
                    # Find the switch that includes this block
                    for switch_name in self.track_data.get("switches", {}):
                        if location in switch_name:
                            left_panel.switch_selector.set(switch_name)
                            left_panel.update_switch_display()
                            
                            # Optionally change direction
                            # This would depend on your switch logic
                            add_to_message_log(f"Updated switch display for {switch_name}")
                            break
                
        except Exception as e:
            print(f"Error handling CTC switch command: {e}")
            add_to_message_log(f"ERROR: Failed to process CTC switch command: {e}")
    
    # =====================================================================
    # SEND FUNCTIONS FOR TRACK MODEL AND CTC INTEGRATION
    # =====================================================================
    
    def send_to_track_model(self, message):
        """Send message to Track Model"""
        if hasattr(self, 'server1') and self.server1:
            return self.server1.send_to_ui("Track Model", message)
        else:
            print("ERROR: No server connection to Track Model")
            return False
    
    def send_to_CTC(self, message):
        """Send message to CTC"""
        if hasattr(self, 'server1') and self.server1:
            return self.server1.send_to_ui("CTC", message)
        else:
            print("ERROR: No server connection to CTC")
            return False

    def send_commanded_to_track_model(self, track, block, speed, authority):
        """Send commanded speed and authority to Track Model"""
        track_model_message = {
            "command": "Speed and Authority",
            "block_number": block,
            "commanded_speed": speed,
            "commanded_authority": authority,
        }
        print(f"Sending commanded to Track Model: {track_model_message}")
        add_to_message_log(f"Sending Speed/Authority to Track Model: Block {block}")
        return self.send_to_track_model(track_model_message)

    def send_light_state(self, track, block, color):
        """Send Light State to CTC and Track Model"""
        # Convert color to CTC format
        if color == 'Red':
            color_ctc = "00"
        elif color == 'Yellow':
            color_ctc = "01"
        elif color == 'Green':
            color_ctc = "10"
        else:  # Super Green
            color_ctc = "11"

        message = {
            "command": "LS",
            "value": [block, color_ctc, track]
        }
        
        print(f"Sending light state to CTC: {message}")
        add_to_message_log(f"Light State: Block {block} -> {color} sent to CTC")
        self.send_to_CTC(message)

        # Send ALL light states to Track Model
        self.send_all_lights_to_track_model(track)

    def send_all_lights_to_track_model(self, track):
        """Send ALL light states for a track to Track Model"""
        light_list = []
        
        # Get light locations based on track
        if track == "Green":
            light_blocks = [1, 13, 19, 28, 57]
        else:  # Red
            light_blocks = [9, 11, 15]
        
        # Build light state array
        for block_num in sorted(light_blocks):
            light_name = f"Light {block_num}"
            if light_name in self.track_data.get("lights", {}):
                signal = self.track_data["lights"][light_name].get("signal", "Green")
            else:
                signal = "Green"
            
            # Convert signal to ['0','1'] format
            if signal == 'Red':
                color_set = ['0', '0']
            elif signal == 'Yellow':
                color_set = ['0', '1']
            elif signal == 'Green':
                color_set = ['1', '0']
            else:  # Super Green
                color_set = ['1', '1']
            light_list.append(color_set)
        
        track_model_message = {
            "command": "light_states",
            "value": light_list
        }
        
        print(f"Sending all lights to Track Model: {track_model_message}")
        add_to_message_log(f"Light states sent to Track Model")
        self.send_to_track_model(track_model_message)

    def send_switch_to_track_model(self, track, block, position):
        """Send switch states to Track Model"""
        switch_list = []
        
        # Add track identifier (0 for Green, 1 for Red)
        track_id = 0 if track == "Green" else 1
        switch_list.append(track_id)
        
        # Get all switches for the current track
        switches = []
        for switch_name, switch_data in self.track_data.get("switches", {}).items():
            if switch_data.get("line", track) == track:
                import re
                numbers = re.findall(r'\d+', switch_name)
                if numbers:
                    switch_block_num = int(numbers[0])
                    pos = switch_data.get("numeric_position", 0)
                    switches.append((switch_block_num, pos))
        
        switches.sort(key=lambda x: x[0])
        
        for block_num, pos in switches:
            switch_list.append(pos)
        
        switch_message = {
            "command": "switch_states",
            "value": switch_list
        }
        
        print(f"Sending switches to Track Model: {switch_message}")
        add_to_message_log(f"Switch states sent to Track Model")
        return self.send_to_track_model(switch_message)

    def send_occupancy(self, track, block, occupied):
        """Send Occupancy to CTC"""
        if occupied == 'Yes':
            message = {
                "command": "TL",
                "value": [block, track]
            }
            print(f"Sending occupancy to CTC: {message}")
            add_to_message_log(f"Occupancy: Block {block} occupied - sent to CTC")
            self.send_to_CTC(message)

    def send_railway_state(self, track, block, bar):
        """Send Railway Crossing State to CTC and Track Model"""
        if bar == 'Closed':
            booly = "1"
        else:
            booly = "0"
            
        message = {
            "command": "RC",
            "value": [block, booly, track]
        }
        
        print(f"Sending railway crossing state to CTC: {message}")
        add_to_message_log(f"Railway Crossing: Block {block} Bar {bar} sent to CTC")
        self.send_to_CTC(message)
        self.send_rc_to_track_model(track)
    
    def send_rc_to_track_model(self, track):
        """Send all railway crossing states to Track Model"""
        rc_list = []
        
        if track == "Green":
            crossing_blocks = [19]
        else:
            crossing_blocks = [19]
        
        for block_num in sorted(crossing_blocks):
            crossing_name = f"Railway Crossing: {block_num}"
            if crossing_name in self.track_data.get("crossings", {}):
                bar_state = self.track_data["crossings"][crossing_name].get("bar", "Open")
            else:
                bar_state = "Open"
            
            state = 1 if bar_state == "Closed" else 0
            rc_list.append(state)
        
        rc_message = {
            "command": "rc_states",
            "value": rc_list
        }
        
        print(f"Sending railway crossings to Track Model: {rc_message}")
        add_to_message_log(f"Railway crossing states sent to Track Model")
        return self.send_to_track_model(rc_message)


    def handle_ctc_maintenance(self, maint_data=None):
        """Handle maintenance mode request from CTC"""
        try:
            print("CTC maintenance request received")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update maintenance mode
            self.maintenance_mode = True
            
            # Log the maintenance request
            log_message = f"{current_time} CTC: Maintenance Request Received"
            add_to_message_log(log_message)
            
            # Update UI elements
            if hasattr(maint_led, 'config'):
                maint_led.config(bg="orange", text="MAINT REQ")
                add_to_message_log("Maintenance Request LED activated")

            # Send acknowledgment back to CTC
            if hasattr(self, 'server1'):
                ack_message = {
                    "command": "MAINT_ACK",
                    "value": {
                        "status": 'accepted',
                        "timestamp": current_time,
                        "message": 'Maintenance mode activated'
                    }
                }
            self.server1.send_to_ui('CTC', ack_message)
            
            # Optionally switch to maintenance mode in the UI
            if hasattr(view_var_maint, 'set'):
                view_var_maint.set(True)
                toggle_maintenance_mode()
                
            # Update left panel if it exists
            if hasattr(left_panel, 'update_mode_ui'):
                left_panel.update_mode_ui()
                
            # Update right panel if it exists
            if hasattr(right_panel, 'update_mode_ui'):
                right_panel.update_mode_ui()
                
            # Send acknowledgment back to CTC
            if hasattr(self, 'server1'):
                ack_message = {
                    'command': 'MAINT_ACK',
                    'value': {
                        'status': 'accepted',
                        'timestamp': current_time,
                        'message': 'Maintenance mode activated'
                    }
                }
                self.server1.send_to_ui('CTC', ack_message)
          ####################################################################################################################
        except Exception as e:
            error_msg = f"Error processing CTC maintenance command: {e}"
            print(f"✗ {error_msg}")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_to_message_log(f"{current_time} ERROR: Failed to process CTC maintenance request")


        #             value_type = data.get('value_type', 'suggested').strip()
                
                
        #     # Format 2: CTC schedule format (from your CTC files)
        #         elif 'command' in data and 'value' in data:
        #             command = data['command']
                
        #         # Check if this is a speed/authority command
        #             if command in ['speed_auth', 'update_speed_auth', 'ctc_suggestion']:
        #                 value = data['value']
                    
        #             # Parse the value which might be a string or dict
        #                 if isinstance(value, dict):
        #                     speed_str = value.get('speed', '0')
        #                     authority_str = value.get('authority', '0')
        #                     block = value.get('block', '')
        #                     track = value.get('track', '')
        #                     value_type = value.get('value_type', 'suggested')
        #                 elif isinstance(value, str):
        #                 # Parse string format like "45.5,10" (speed,authority)
        #                     parts = value.split(',')
        #                     if len(parts) >= 2:
        #                         speed_str = parts[0].strip()
        #                         authority_str = parts[1].strip()
        #                         block = value.get('block', '') if isinstance(value, dict) else ''
        #                         track = value.get('track', '') if isinstance(value, dict) else ''
        #                         value_type = 'suggested'
        #                     else:
        #                     # Try to extract just speed
        #                         speed_str = value.strip()
        #                         authority_str = '0'
        #                         block = ''
        #                         track = ''
        #                         value_type = 'suggested'
        #                 else:
        #                     return  # Unknown format
        #             else:
        #                 return  # Not a speed/authority command
        #         else:
        #             return  # Unknown format
                
        #     elif isinstance(data, str):
        #     # Format 3: Simple string format
        #         if ',' in data:
        #         # Format: "speed,authority" or "speed,authority,block,track"
        #             parts = data.split(',')
        #             if len(parts) >= 2:
        #                 speed_str = parts[0].strip()
        #                 authority_str = parts[1].strip()
        #                 block = parts[2].strip() if len(parts) > 2 else ''
        #                 track = parts[3].strip() if len(parts) > 3 else ''
        #                 value_type = 'suggested'
        #             else:
        #                 return
        #         else:
        #         # Format: Just speed value
        #             speed_str = data.strip()
        #             authority_str = '0'
        #             block = ''
        #             track = ''
        #             value_type = 'suggested'
        #     else:
        #         return  # Unknown data type
        
        # # Only process if it's for the current line (if track specified)
        #     if track and track.lower() != self.current_line.lower():
        #         print(f"Ignoring update for different line: {track} (we're on {self.current_line})")
        #         return
        
        # # Convert speed to float with 3 decimal places
        #     try:
        #         speed = float(speed_str)
        #         formatted_speed = round(speed, 3)
        #     except ValueError:
        #         print(f"Invalid speed value: {speed_str}")
        #         formatted_speed = 0.0
        
        # # Convert authority to int
        #     try:
        #         authority = int(authority_str)
        #     except ValueError:
        #         print(f"Invalid authority value: {authority_str}")
        #         authority = 0
        
        #     print(f"CTC Update - Block {block if block else 'unspecified'}, Speed: {formatted_speed:.2f} mph, Authority: {authority} blocks, Type: {value_type}")
        
        # # Update the display based on value type
        #     if value_type == 'suggested':
        #     # Update suggested values in right panel
        #         if hasattr(right_panel, 'update_suggested_speed'):
        #             right_panel.update_suggested_speed(formatted_speed)
        #         if hasattr(right_panel, 'update_suggested_authority'):
        #             right_panel.update_suggested_authority(authority)
            
        #     # Log the update
        #         if block:
        #             add_to_message_log(f"CTC Suggested Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks for Block {block}")
        #         else:
        #             add_to_message_log(f"CTC Suggested Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks")
        
        #     elif value_type == 'commanded':
        #         # Update commanded values
        #         if hasattr(right_panel, 'auth_entry'):
        #             right_panel.auth_entry.delete(0, tk.END)
        #             right_panel.auth_entry.insert(0, f"{authority} blocks")
            
        #         if hasattr(right_panel, 'speed_entry'):
        #             right_panel.speed_entry.delete(0, tk.END)
        #             right_panel.speed_entry.insert(0, f"{formatted_speed:.2f} mph")
            
        #     # Log the update
        #         if block:
        #             add_to_message_log(f"CTC Commanded Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks for Block {block}")
        #         else:
        #             add_to_message_log(f"CTC Commanded Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks")
        
        #     else:
        #     # Default to suggested if type not specified
        #         if hasattr(right_panel, 'update_suggested_speed'):
        #             right_panel.update_suggested_speed(formatted_speed)
        #         if hasattr(right_panel, 'update_suggested_authority'):
        #             right_panel.update_suggested_authority(authority)
            
        #         add_to_message_log(f"CTC Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks")
            
        # except Exception as e:
        #     print(f"Error handling speed/auth update: {e}")
        #     add_to_message_log(f"ERROR processing CTC update: {e}", "ERROR")

    # def _handle_speed_auth_update(self, data):
    #     """Handle speed and authority updates from CTC"""
    #     try:
    #         if isinstance(data, dict):
    #             track = data.get('track', '').strip()
    #             block = data.get('block', '').strip()
    #             speed_str = data.get('speed', '0').strip()
    #             authority_str = data.get('authority', '0').strip()
    #             value_type = data.get('value_type', '').strip()
            
    #             # Only process if it's for the current line
    #             if track.lower() != self.current_line.lower():
    #                 print(f"Ignoring update for different line: {track} (we're on {self.current_line})")
    #                 return
            
    #             # Convert speed to float
    #             try:
    #                 speed = float(speed_str)
    #                 formatted_speed = round(speed, 3)
    #             except ValueError:
    #                 print(f"Invalid speed value: {speed_str}")
    #                 formatted_speed = 0.0
            
    #             # Convert authority to int
    #             try:
    #                 authority = int(authority_str)
    #             except ValueError:
    #                 print(f"Invalid authority value: {authority_str}")
    #                 authority = 0
            
    #             print(f"CTC Update: Block {block}, Speed: {formatted_speed}, Authority: {authority}, Type: {value_type}")
            
    #             # Update the display
    #             if value_type == 'suggested':
    #                 # Update suggested values in right panel
    #                 if hasattr(right_panel, 'update_suggested_speed'):
    #                     right_panel.update_suggested_speed(formatted_speed)
    #                 if hasattr(right_panel, 'update_suggested_authority'):
    #                     right_panel.update_suggested_authority(authority)
                
    #                 # Also log the update
    #                 add_to_message_log(f"CTC Suggested Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks for Block {block}")
            
    #             elif value_type == 'commanded':
    #                 # Update commanded values
    #                 if hasattr(right_panel, 'auth_entry'):
    #                     right_panel.auth_entry.delete(0, tk.END)
    #                     right_panel.auth_entry.insert(0, f"{authority} blocks")
                
    #                 if hasattr(right_panel, 'speed_entry'):
    #                     right_panel.speed_entry.delete(0, tk.END)
    #                     right_panel.speed_entry.insert(0, f"{formatted_speed:.2f} mph")
                
    #                 add_to_message_log(f"CTC Commanded Values: Speed={formatted_speed:.2f} mph, Authority={authority} blocks for Block {block}")
            
    #     except Exception as e:
    #         print(f"Error handling speed/auth update: {e}")
    #         add_to_message_log(f"ERROR processing CTC update: {e}", "ERROR")

# Create mock data instance
test_data = UITestData()
# Temporary safety check - ensure filtered_track_data exists
if not hasattr(test_data, 'filtered_track_data'):
    print("Warning: filtered_track_data not found, creating it now...")
    test_data.filtered_track_data = test_data.track_data.copy() if hasattr(test_data, 'track_data') else {"switches": {}, "lights": {}, "crossings": {}}
#######################################################################################################################


# Root window setup
root = tk.Tk()
root.title("Wayside Controller Hardware UI")
root.geometry("1400x900")
root.configure(bg="#0b1443")

# ========== HEADER ========== #
header_frame = tk.Frame(root, bg="#0b1443")
header_frame.pack(fill="x", pady=10)

# Load and display the BLT logo
try:
    # Debug: Check current directory and file existence
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # List all files in current directory
    # print("Files in current directory:")
    # for file in os.listdir(current_dir):
    #     print(f"  - {file}")
    
    # Check if file exists
    # logo_path = "/home/siram/TRAINS-TEAM2/blt logo.png"
    logo_path = "blt logo.png"
    print(f"Looking for logo at: {logo_path}")
    print(f"Logo file exists: {os.path.exists(logo_path)}")
    
    # Load the image and resize it appropriately
    logo_image = Image.open(logo_path)
    logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
   
    # Create label with image
    logo = tk.Label(header_frame, image=logo_photo, bg="#0b1443")
    logo.image = logo_photo  # Keep a reference to prevent garbage collection
    logo.pack(side="left", padx=15)
    print("SUCCESS: Logo loaded successfully!")
    
except Exception as e:
    # Fallback to text if image loading fails
    print(f"Error loading logo: {e}")
    logo = tk.Label(header_frame, text="🚉", bg="#0b1443", fg="white", font=("Arial", 20))
    logo.pack(side="left", padx=15)

#creating a frame to contain buttons and status of PLC
plc_upload_btn = tk.Button(header_frame, text="Select PLC File", font=("Arial", 11, "bold"),
    width=16, height=2, command=lambda: select_plc_file())
plc_upload_btn.pack(side="left", padx=20)

run_plc_btn = tk.Button(
    header_frame,
    text="Run PLC",
    font=("Arial", 11, "bold"),
    width=16,
    height=2,
    bg="#008000",
    fg="white",
    command=lambda: run_plc_file()
)
run_plc_btn.pack(side="left", padx=10)

################### Differnt Line choice ##########################
#toggle button for map choice (red vs green)
def toggle_line_map():
    """Switches between red and green line data"""
    global current_line
    global test_data

    if test_data.current_line == "Green":
        test_data.current_line = "Red"
        map_toggle_btn.config(text="Switch to Green Line", bg="#66cc66")
        add_to_message_log("Switched to Red Line data")
        # load_line_data("Red")
        test_data.load_initial_data("red_line.txt") # calling the method on test_data
    else:
        test_data.current_line = "Green"
        map_toggle_btn.config(text="Switch to Red Line", bg="#ff6666")
        add_to_message_log("Switched to Green Line data")
        # load_line_data("Green")
        test_data.load_initial_data("green_line.txt") # calling the method on test_data

    # update test_data
    # test_data.current_line = current_line

    # Load the appropriate track data
    load_line_data(test_data.current_line)
    
    # Trigger line change callbacks to update all panels
    for callback in test_data.on_line_change:
        callback()
    
    # forcing an update on the RightPanel with data
    if hasattr(right_panel, 'on_line_changed'):
        right_panel.on_line_changed()

    add_to_message_log(f"Displaying {test_data.current_line} Line data")

def load_line_data(self, filename):
    # changed this at 1:53 am 12/7
    """Load track data for the specified line"""
    try:
        print(f"DEBUG: Loading file: '{filename}'")
        print(f"DEBUG: Current directory: {os.getcwd()}")
        print(f"DEBUG: Files in directory: {os.listdir('.')}")
        
        # Clear existing data
        self.block_data = []
        self.block_sections = {}
        
        # Load block data
        self.block_data = self.load_complete_track_data(filename)
        self.filtered_block_data = self.block_data.copy()
        
        if filename == "green_line.txt":
            # Update track data for green line
            self.track_data["Green"] = {
                "crossings": {
                    "Railway Crossing: 19": {"condition": "Normal", "lights": "Red", "bar": "Closed"}
                },
                "switches": {
                    "Switch 12-13": {"condition": "Normal", "direction": "Blocks 12-13"},
                    "Switch 28-29": {"condition": "Normal", "direction": "Blocks 28-29"},
                    "Switch 57-Yard": {"condition": "Normal", "direction": "Blocks 57-Yard"},
                    "Switch 62-Yard": {"condition": "Normal", "direction": "Blocks Yard-63"}
                },
                "lights": {
                    "Light 1": {"condition": "Normal", "signal": "Green"},
                    "Light 13": {"condition": "Normal", "signal": "Green"},
                    "Light 28": {"condition": "Normal", "signal": "Yellow"},
                    "Light 57": {"condition": "Normal", "signal": "Red"},
                    "Light 19": {"condition": "Normal", "signal": "Red"}
                }
            }
            # Update block sections for Green Line
            self.block_sections = self.green_sections
            
        else:  # Red line
            # Update track data for Red Line
            self.track_data["Red"] = {
                "crossings": {
                    "Railway Crossing: 19": {"condition": "Normal", "lights": "Red", "bar": "Closed"}
                },
                "switches": {
                    "Switch 12-13": {"condition": "Normal", "direction": "Blocks 12-13 (C-D)"},
                    "Switch 1-13": {"condition": "Normal", "direction": "Blocks 1-13 (D-A)"},
                    "Switch 28-29": {"condition": "Normal", "direction": "Blocks 28-29(F-G)"},
                    "Switch 150-28": {"condition": "Normal", "direction": "Blocks 150-28(F-Z)"}
                },
                "lights": {
                    "Light 9": {"condition": "Normal", "signal": "Green"},
                    "Light 15": {"condition": "Normal", "signal": "Yellow"},
                    "Light 11": {"condition": "Normal", "signal": "Red"}
                }
            }
            # Update block sections for Red Line
            self.block_sections = self.red_sections
        
        self.filtered_track_data = self.track_data.copy()
        print(f"Loaded {len(self.block_data)} rows for {filename} Line")
        add_to_message_log(f"Loaded {filename} Line data")
        
        # Get unique sections for this line
        sections = set()
        for row in self.block_data:
            if (filename == "green_line.txt" and row[1] == "Green") or \
               (filename == "red_line.txt" and row[1] == "Red"):
                if len(row) > 3:
                    sections.add(row[3])
        
        print(f"Sections in {filename} Line: {sorted(sections)}")
        add_to_message_log(f"Loaded {filename} Line: {len(self.block_data)} blocks, {len(sections)} sections")
        
    except Exception as e:
        add_to_message_log(f"ERROR loading {filename} Line data: {e}")
        print(f"Error loading line data: {e}")
        import traceback
        traceback.print_exc()

map_toggle_btn = tk.Button(
    header_frame,
    text="Switch to Red Line",
    font=("Arial", 11, "bold"),
    width=18,
    height=2,
    bg="#ff6666",  # Currently in
    fg="white",
    command=toggle_line_map
)
map_toggle_btn.pack(side="left", padx=10)
###################################################################################################


# creating a center frame for additonal buttons
center_frame = tk.Frame(header_frame, bg="#0b1443")
center_frame.pack(side="left", expand=True)

# Clock - positioned between PLC buttons and LEDs
clock_frame = tk.Frame(header_frame, bg="#0b1443")
clock_frame.pack(side="right", padx=15)

global_clock = Clock()

clock_label = tk.Label(
    header_frame, 
    text=global_clock.getTime(), 
    font=("Arial", 12, "bold"), 
    bg="white",
    width=10) 
    # fg="white")
clock_label.pack(side="right", anchor="ne")


# Fault LED indicator
fault_led = tk.Label(header_frame, text="Fault LED", bg="gray", fg="white", width=10, font=("Arial", 10, "bold"))
fault_led.pack(side="right", padx=30)

# Maintenance Mode LED indicator:
maint_led = tk.Label(header_frame, text="MM OFF", bg="gray", fg="white", width=10, font=("Arial", 10, "bold"))
maint_led.pack(side="right", padx=10)

#PLC Upload LED indicator:
plc_LED = tk.Label(header_frame, text="PLC Ready", bg="gray", fg="black", font=("Arial", 10, "bold"))
plc_LED.pack(side="left", padx=0)

# PLC upload and run buttons
def trigger_plc_fault():
    """Simulate a railroad crossing fault (PLC triggered)."""
    plc_instance.set_crossing_fault(True)
    fault_led.config(bg="red", text="FAULT")  # Turn LED red

def clear_plc_fault():
    """Clear the railroad crossing fault."""
    plc_instance.set_crossing_fault(False)
    fault_led.config(bg="green", text="OK")  # Turn LED green

selected_plc_file = None
plc_instance = None

def update_clock_display():
    """Continuously update the clock display every second"""
    try:
        current_time = global_clock.getTime()
        clock_label.config(text=current_time)
    except Exception as e:
        print(f"Clock error: {e}")
        clock_label.config(text="--:--:--")
# update every 100 ms
    # Update every second (1000ms)
    root.after(1000, update_clock_display)

    # time = clock.clock.getTime()
    # self.clockText.configure(text = time)
    # self.clockTimer = self.root.after(100, self.updateTime)
# Start the clock update loop
update_clock_display()

#######################################################################################
#######################################################################################
# ========== BODY ========== #
body_frame = tk.Frame(root, bg="#0b1443")
body_frame.pack(fill="both", expand=True, padx=15, pady=10)

# Two main pages (stacked)
main_frame = tk.Frame(body_frame, bg="#0b1443")
maintenance_frame = tk.Frame(body_frame, bg="#0b1443")

for frame in (main_frame, maintenance_frame):
    frame.place(relwidth=1, relheight=1)

#######################################################################################
#######################################################################################
# ---------- CENTER AREA (Map + Message Log) ---------- #
center_container = tk.Frame(main_frame, bg="#0b1443")
center_container.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# Map Display
map_frame = tk.Frame(center_container, bg="white", relief="ridge", borderwidth=3, width=750, height=650)
map_frame.pack(fill="none", expand=False)  # Don't expand, use fixed size
map_frame.pack_propagate(False)  # Prevent frame from shrinking to fit contents
##
# Create canvas for displaying the track image
canvas = tk.Canvas(map_frame, bg="white")
canvas.pack(fill="both", expand=True)
###########################################################################################################
##########################################################################################################
# Load and display the Red Green Blue Line track image
# try:
#     track_image = Image.open("./home/siram/TRAINS-TEAM2/Red and Green Line.png")
#     # Resize image to fit the canvas while maintaining aspect ratio
#     track_image = track_image.resize((700, 400), Image.Resampling.LANCZOS)
#     track_photo = ImageTk.PhotoImage(track_image)
   
#     # Display image on canvas
#     canvas.create_image(360, 215, image=track_photo)
#     canvas.image = track_photo  # Keep a reference to prevent garbage collection
   
# except Exception as e:
#     # Fallback if image loading fails
#     print(f"Error loading track image: {e}")
#     canvas.create_text(400, 250, text="TRACK MAP DISPLAY\n(Red and Green Line.png not found)",
#                       fill="black", font=("Arial", 14, "bold"), justify="center")

# Load and display the Green Line track image
try:
    # Debug: Check current directory and file existence
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # List all files in current directory
    # print("Files in current directory:")
    # for file in os.listdir(current_dir):
    #     print(f"  - {file}")
    
    # Check if file exists in TRAINS-TEAM2 folder
    image_path = "Red and Green Line.png"
    print(f"Looking for image at: {image_path}")
    print(f"File exists: {os.path.exists(image_path)}")
    
    track_image = Image.open(image_path)
    # Resize image to fit the canvas while maintaining aspect ratio
    track_image = track_image.resize((700, 600), Image.Resampling.LANCZOS)
    track_photo = ImageTk.PhotoImage(track_image)
   
    # Display image on canvas
    canvas.create_image(375, 300, image=track_photo)
    canvas.image = track_photo  # Keep a reference to prevent garbage collection
    print("SUCCESS: Image loaded successfully!")
   
except Exception as e:
    # Fallback if image loading fails
    print(f"Error loading track image: {e}")
    canvas.create_text(400, 250, text="TRACK MAP DISPLAY\n(Red and Green Line.png not found)",
                      fill="black", font=("Arial", 14, "bold"), justify="center")
#######################################################################################################
#######################################################################################################

# Add the MessageLogger class definition right after your imports
class MessageLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget
       
    def log(self, message, level="INFO"):
        """Add timestamped message with color coding"""
        self.text_widget.config(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = self.get_color_for_level(level)
        self.text_widget.insert("end", f"{timestamp} [{level}] {message}\n")
        self.text_widget.tag_config(level, foreground=color)
        self.text_widget.see("end")
        self.text_widget.config(state="disabled")
   
    def get_color_for_level(self, level):
        colors = {"INFO": "white", "WARNING": "yellow", "ERROR": "red", "DEBUG": "cyan"}
        return colors.get(level, "white")
   
    def clear(self):
        self.text_widget.config(state="normal")
        self.text_widget.delete(1.0, "end")
        self.text_widget.config(state="disabled")

# Message Log (now underneath the map)
message_frame = tk.Frame(center_container, bg="#0b1443", height=150)
message_frame.pack(fill="x", pady=(10, 0))

tk.Label(message_frame, text="Messages", bg="#0b1443", fg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=5)

# Create a frame for the text widget with scrollbar
log_container = tk.Frame(message_frame, bg="#0b1443")
log_container.pack(fill="x", pady=5)

log_text = tk.Text(log_container, height=6, bg="#111b52", fg="white", font=("Courier", 10))
scrollbar = tk.Scrollbar(log_container, orient="vertical", command=log_text.yview)
log_text.configure(yscrollcommand=scrollbar.set)

log_text.pack(side="left", fill="x", expand=True)
scrollbar.pack(side="right", fill="y")

# Create MessageLogger instance
message_logger = MessageLogger(log_text)

# Keep this function for backward compatibility with existing code
def add_to_message_log(message):
    """Wrapper for backward compatibility"""
    message_logger.log(message, "INFO")

# plc = PLCController(add_to_message_log)
# plc_instance = PLCController(add_to_message_log)
# plc_instance.main()  # Runs PLC logic
#
# Initialize with some messages
add_to_message_log("INFO: UI initialized.")
add_to_message_log("INFO: Map display loaded.")
add_to_message_log("INFO: Control panels ready.")
###########################################################################################
############################      PLC MANAGER  ############################################

# Add PLCManager class definition after MessageLogger
class PLCManager:
    def __init__(self, message_logger):
        self.message_logger = message_logger
        self.plc_instance = None
        self.current_file = None
       
    def load_plc_file(self, file_path):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("plc_module", file_path)
            plc_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plc_module)
           
            self.plc_instance = plc_module.PLCController(self.message_logger.log)
            self.current_file = file_path
            self.message_logger.log(f"PLC file loaded: {file_path}")
            return True
        except Exception as e:
            self.message_logger.log(f"PLC load error: {e}")
            return False
   
    def run_plc(self):
        if not self.plc_instance:
            self.message_logger.log("No PLC file loaded")
            messagebox.showwarning("No PLC File", "Please upload a PLC file first!")
            return False
       
        try:
            self.plc_instance.main()
            self.message_logger.log(f"PLC file executed: {self.current_file.split('/')[-1]}")
            return True
        except Exception as e:
            self.message_logger.log(f"PLC runtime error: {e}")
            return False
   
    def get_status(self):
        return {
            "loaded": self.plc_instance is not None,
            "file": self.current_file
        }
   
#creating mock data instance
test_data = UITestData()  

# Creating MessageLogger
message_logger = MessageLogger(log_text)

# Create PLCManager instance (after message_logger is created)
plc_manager = PLCManager(message_logger)

# Update the button functions:
def select_plc_file():
    """Open a file dialog to select a PLC file"""
    file_path = filedialog.askopenfilename(
        title ="Select PLC File",
        filetypes=[("Python Files", "*.py")]
    )
    if file_path:
        if plc_manager.load_plc_file(file_path):
            # Update LED or other UI elements if needed
            plc_LED.config(bg="white", text="PLC LOADED")

def run_plc_file():
    """Run the PLC logic using the selected file."""
    if plc_manager.run_plc():
        plc_LED.config(bg="green", text="PLC RUNNING")
    else:
        plc_LED.config(bg="red", text="FAULT")

# Keep global plc_instance for backward compatibility
plc_instance = None  # This will be set by PLCManager internally

# Update buttons
plc_upload_btn.config(command=select_plc_file)
run_plc_btn.config(command=run_plc_file)

#########################################################################################
#########################################################################################

# Screen toggle checkboxes
toggle_frame = tk.Frame(header_frame, bg="#0b1443")
toggle_frame.pack(side="right", padx=30)

view_var_main = tk.BooleanVar(value=True)
view_var_maint = tk.BooleanVar(value=False)

def update_screen_view():
    if view_var_main.get():
        main_frame.tkraise()
        # When switching to main screen, update maintenance mode based on maint_check
        test_data.maintenance_mode = view_var_maint.get()
        if hasattr(right_panel, 'update_mode_ui'):
            right_panel.update_mode_ui()
    elif view_var_maint.get():
        maintenance_frame.tkraise()

main_check = tk.Checkbutton(toggle_frame, text="Main Screen", variable=view_var_main,
                            command=lambda: [view_var_maint.set(False), update_screen_view()],
                            bg="#0b1443", fg="white", selectcolor="#333", font=("Arial", 10))
main_check.grid(row=0, column=0, padx=10)

def toggle_maintenance_mode():
    """Toggle maintenance mode when Maintenance checkbox is clicked"""
    test_data.maintenance_mode = view_var_maint.get()

    # Update the maintenance LED color/text
    if test_data.maintenance_mode:
        maint_led.config(bg="orange", text="MM ON")
        add_to_message_log("Maintenance Mode Activated")
    else:
        maint_led.config(bg="gray", text="MM OFF")

    # Send acknowledgment to CTC if this was triggered by CTC request
    if hasattr(test_data, 'server1'):
            ack_message = {
                'command': 'MAINT_ACK',
                'value': {
                    'status': 'active',
                    'mode': 'manual',
                    'message': 'Maintenance mode manually activated'
                }
            }
            test_data.server1.send_to_ui('CTC', ack_message)
    else:
        maint_led.config(bg="gray", text="MM OFF")
        add_to_message_log("Maintenance Mode Deactivated")


    # Update the right panel UI
    if hasattr(right_panel, 'update_mode_ui'):
        right_panel.update_mode_ui()
    
    # Update the left panel UI
    if hasattr(left_panel, 'update_mode_ui'):
        left_panel.update_mode_ui()

    # Keep the main screen visible regardless of maintenance mode
    if view_var_main.get():
        main_frame.tkraise()


maint_check = tk.Checkbutton(toggle_frame, text="Maintenance", variable=view_var_maint,
                             command=lambda: [view_var_main.set(True), toggle_maintenance_mode(), update_screen_view()],
                             bg="#0b1443", fg="white", selectcolor="#333", font=("Arial", 10))
maint_check.grid(row=0, column=1, padx=10)


#######################################################################################
#######################################################################################
# ---------- LEFT PANEL ---------- #
class LeftPanel(tk.Frame):
    def __init__(self, parent, data):
        self.parent = parent
        super().__init__(parent, bg='#1a1a4d', width=250)
        self.pack_propagate(False)
        self.data = data
        self.create_widgets()
        self.ensure_data_initialized()
        # Connect line change callback:
        self.data.on_line_change.append(self.on_line_changed)
   
    def create_widgets(self):
        #Tabs are now controlled by header
       
        # Railway Crossing Detail
        self.create_crossing_section()
       
        # Switch Details
        self.create_switch_section()
       
        # Light Detail
        self.create_light_section()

        # Initialize with current line data
        self.update_crossing_options()

        #maintenance call button for CTC request
        self.maintenance_request_section()

    def create_crossing_section(self):
        crossing_frame = tk.LabelFrame(self, text="Railway Crossing Detail",
                                      bg='#cccccc', font=('Arial', 9, 'bold'))
        crossing_frame.pack(fill=tk.X, pady=5)
       
        tk.Label(crossing_frame, text="Select Crossing:", bg='#cccccc').pack(pady=2)
        self.crossing_selector = ttk.Combobox(crossing_frame, width=18, state='readonly')
        self.crossing_selector.pack(pady=2)
        self.crossing_selector.bind('<<ComboboxSelected>>', self.update_crossing_display)
       
        tk.Label(crossing_frame, text="Condition:", bg='#cccccc').pack()
        self.crossing_condition = tk.Entry(crossing_frame, width=20, state='readonly')
        self.crossing_condition.pack()
       
        tk.Label(crossing_frame, text="Lights:", bg='#cccccc').pack()
        self.crossing_lights = ttk.Combobox(crossing_frame, width=18,
                                           values=["On", "Off"], state='readonly')
        self.crossing_lights.pack()
        self.crossing_lights.bind('<<ComboboxSelected>>', self.update_crossing_lights)
       
        tk.Label(crossing_frame, text="Bar:", bg='#cccccc').pack()
        self.crossing_bar = ttk.Combobox(crossing_frame, width=18, values=["Closed", "Open"], state='readonly')
        self.crossing_bar.pack()
        self.crossing_bar.bind('<<ComboboxSelected>>', self.update_crossing_bar)
        # sendCrossing = tk.Button(crossing_frame, text="Send", width=5, command=self.update_crossing_lights)
        # sendCrossing.pack(side=tk.BOTTOM)

    def update_crossing_options(self):
        """Update crossing dropdown based on current line"""
        # Get crossings for current line
        if self.data.current_line == "Green":
            crossings = ["Railway Crossing: 19"]
        else:  # Red line
            crossings = ["Railway Crossing: 19"]  # Same for Red line
    
        self.crossing_selector['values'] = crossings
        if crossings:
            self.crossing_selector.set(crossings[0])
            self.update_crossing_display()

        # """Update combobox options based on current line"""
        # crossings = list(self.data.filtered_track_data.get("crossings", {}).keys())
        # self.crossing_selector['values'] = crossings
        # if crossings:
        #     self.crossing_selector.set(crossings[0])
        #     self.update_crossing_display()
   
    def create_switch_section(self):
        switch_frame = tk.LabelFrame(self, text="Switch Details",
                                    bg='#cccccc', font=('Arial', 9, 'bold'))
        switch_frame.pack(fill=tk.X, pady=5)
       
        tk.Label(switch_frame, text="Select Switch:", bg='#cccccc').pack(pady=2)
        self.switch_selector = ttk.Combobox(switch_frame, width=18, state='readonly')
        self.switch_selector.pack(pady=2)
        self.switch_selector.bind('<<ComboboxSelected>>', self.update_switch_display)
       
        tk.Label(switch_frame, text="Condition:", bg='#cccccc').pack()
        self.switch_condition = tk.Entry(switch_frame, width=20, state='readonly')
        self.switch_condition.pack()
       
        tk.Label(switch_frame, text="Direction:", bg='#cccccc').pack()
        self.switch_direction = ttk.Combobox(switch_frame, width=18,
                                            values=["Blocks 5-11", "Blocks 5-15"])
                                            # state='readonly') # this makes the dropdown BLANK - FIX THIS
        self.switch_direction.pack()
        self.switch_direction.bind('<<ComboboxSelected>>', self.update_switch_direction)

        # sendSwitch = tk.Button(switch_frame, text="Send", width=5, command=self.update_switch_direction)
        # sendSwitch.pack(side=tk.BOTTOM)

        # Initialize with current line data
        self.update_switch_options()

    def ensure_data_initialized(self):
        """Ensure all required data structures exist"""
        if not hasattr(self.data, 'filtered_track_data'):
            self.data.filtered_track_data = {
                "crossings": {},
                "switches": {},
                "lights": {},
                "occupancy": {}
            }
        if not hasattr(self.data, 'track_data'):
            self.data.track_data = self.data.filtered_track_data.copy()

    def update_switch_options(self):
        """Update combobox options based on current line"""
        if self.data.current_line == "Green":
        # Green Line switches
            switches = [
            "Switch 12-13",
            "Switch 28-29", 
            "Switch 57-Yard",
            "Switch 62-Yard"
        ]
        else:  # Red line
        # Red Line switches
            switches = [
            "Switch 12-13",
            "Switch 1-13",
            "Switch 28-29",
            "Switch 150-28"
            ]
        self.switch_selector['values'] = switches
        if switches:
            self.switch_selector.set(switches[0])
            self.update_switch_display()
   
    def create_light_section(self):
        light_frame = tk.LabelFrame(self, text="Light Detail",
                                   bg='#cccccc', font=('Arial', 9, 'bold'))
        light_frame.pack(fill=tk.X, pady=5)
       
        tk.Label(light_frame, text="Select Light:", bg='#cccccc').pack(pady=2)
        self.light_selector = ttk.Combobox(light_frame, width=18, state='readonly')
        self.light_selector.pack(pady=2)
        self.light_selector.bind('<<ComboboxSelected>>', self.update_light_display)
       
        tk.Label(light_frame, text="Condition:", bg='#cccccc').pack()
        self.light_condition = tk.Entry(light_frame, width=20, state='readonly')
        self.light_condition.pack()
       
        tk.Label(light_frame, text="Signal:", bg='#cccccc').pack()
        self.light_signal = ttk.Combobox(light_frame, width=18,
                                        values=["Red", "Yellow", "Green", "Super Green" ],
                                        state='readonly')
        self.light_signal.pack()
        self.light_signal.bind('<<ComboboxSelected>>', self.update_light_signal)

        # sendLights = tk.Button(light_frame, text="Send", width=5, command=self.update_light_signal)
        # sendLights.pack(side=tk.BOTTOM)
        # Initialize with current line data
        self.update_light_options()

    def maintenance_request_section(self):
        """Create maintenance call button section"""
        maint_frame = tk.LabelFrame(self, text="Maintenance Actions",
                                   bg='#cccccc', font=('Arial', 9, 'bold'))
        maint_frame.pack(fill=tk.X, pady=5)
       
        # Maintenance Call Button
        self.maint_call_btn = tk.Button(
            maint_frame,
            text="Request Maintenance",
            font=("Arial", 9, "bold"),
            width=18,
            height=2,
            bg="#FFA500",  # Orange color
            fg="white",
            command=self.send_maintenance_request
        )
        self.maint_call_btn.pack(pady=5, padx=5)

    def send_maintenance_request(self):
        """Send maintenance request to CTC and other UIs"""
        try:
            print("Sending maintenance request...")
            # Create a confirmation popup first
            confirm_popup = tk.Toplevel(self)
            confirm_popup.title("Confirm Maintenance Request")
            confirm_popup.geometry("400x250")
            confirm_popup.configure(bg="#1a1a4d")
            
            # Center the popup
            confirm_popup.transient(self)
            confirm_popup.grab_set()
            
            # Popup message content - QUESTION
            message_frame = tk.Frame(confirm_popup, bg='#1a1a4d')
            message_frame.pack(expand=True, fill='both', padx=20, pady=20)

        
        # Title
            title_label = tk.Label(
                message_frame,
                text="Maintenance Request Status",
                bg='#1a1a4d',
                fg='white',
                font=('Arial', 14, 'bold')
            )
            title_label.pack(pady=10)
        
        # Message
            message_label = tk.Label(
                message_frame,
                text="Do you want to send a maintenance request\nto the CTC and other systems?",
                bg='#1a1a4d',
                fg='white',
                font=('Arial', 12),
                justify='center'
            )
            message_label.pack(pady=10)
        
        # Additional info
            info_label = tk.Label(
                message_frame,
                text=f"Line: {test_data.current_line}\nTime: {datetime.now().strftime('%H:%M:%S')}",
                bg='#1a1a4d',
                fg='#cccccc',
                font=('Arial', 10),
                justify='center'
            )
            info_label.pack(pady=10)

            # Button frame
            button_frame = tk.Frame(message_frame, bg='#1a1a4d')
            button_frame.pack(pady=15)
            
            # YES button - sends the request
            yes_button = tk.Button(
                button_frame,
                text="YES",
                command=lambda: self.confirm_and_send_request(confirm_popup),
                bg='#FFA500',
                fg='white',
                font=('Arial', 8, 'bold'),
                width=8,
                height=3
            )
            yes_button.pack(side=tk.LEFT, padx=10)
            
            # NO button - cancels
            no_button = tk.Button(
                button_frame,
                text="NO",
                command=confirm_popup.destroy,
                bg='#666666',
                fg='white',
                font=('Arial', 8, 'bold'),
                width=8,
                height=3
            )
            no_button.pack(side=tk.LEFT, padx=10)
            
            # Close the popup when clicking the X
            confirm_popup.protocol("WM_DELETE_WINDOW", confirm_popup.destroy)
            # # Update button state
            # self.maint_call_btn.config(
            #     text="Request Sent",
            #     bg="#666666",
            #     state="disabled"
            # )

        except Exception as e:
            print(f"Error creating confirmation popup: {e}")
            add_to_message_log(f"ERROR: Failed to create confirmation popup: {e}")
    def confirm_and_send_request(self, confirm_popup):
        """Actually send the maintenance request after confirmation"""
        try:
            # Close the confirmation popup
            confirm_popup.destroy()
            
            # Log the request
            add_to_message_log("Sending maintenance request to CTC")
            
            # Update button state TEMPORARILY (will be reset when popup closes)
            self.maint_call_btn.config(
                state="disabled"
            )
            
            # Create maintenance request message
            maint_message = {
                'command': 'MAINT',
                'value': {
                    'source': 'Track_HW',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'line': test_data.current_line,
                    'priority': 'normal',
                    'message': 'Maintenance assistance requested'
                }
            }
            
            # Send to CTC
            if hasattr(test_data, 'server1'):
                test_data.server1.send_to_ui('CTC', maint_message)
                add_to_message_log(f"Maintenance request sent to CTC for {test_data.current_line} Line")
            
            # Also send to Test UI
            test_data.server1.send_to_ui('WC_HW_TestUI', maint_message)
            
            # Update maintenance LED in header
            maint_led.config(bg="orange", text="MAINT REQ")

            # Show success popup
            self.show_success_popup()

            # Schedule button reset after 10 seconds (if button is still disabled)
            if hasattr(self, 'maint_call_btn') and self.maint_call_btn['state'] == 'disabled':
                self.after(10000, lambda: self.maint_call_btn.config(state="normal") if hasattr(self, 'maint_call_btn') else None)
            
        except Exception as e:
            print(f"Error sending maintenance request: {e}")
            add_to_message_log(f"ERROR: Failed to send maintenance request: {e}")
            self.maint_call_btn.config(state="normal")
            # Re-enable the button on error
            if hasattr(self, 'maint_call_btn'):
                self.maint_call_btn.config(state="normal")
    
    def show_success_popup(self):
        """Show success popup after sending request"""
        success_popup = tk.Toplevel(self)
        success_popup.title("Request Sent")
        success_popup.geometry("350x180")
        success_popup.configure(bg="#1a1a4d")
        
        # Center the popup
        success_popup.transient(self)
        
        # Message frame
        message_frame = tk.Frame(success_popup, bg='#1a1a4d')
        message_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Success message
        success_label = tk.Label(
            message_frame,
            text="✓ Maintenance Request Sent",
            bg='#1a1a4d',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        success_label.pack(pady=10)
        
        # Details
        details_label = tk.Label(
            message_frame,
            text=f"Sent to CTC for {test_data.current_line} Line",
            bg='#1a1a4d',
            fg='#cccccc',
            font=('Arial', 10)
        )
        details_label.pack(pady=5)
        
        # OK button
        ok_button = tk.Button(
            message_frame,
            text="OK",
            command=lambda: self.close_success_popup(success_popup),
            bg='#FFA500',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=10,
            height=1
        )
        ok_button.pack(pady=15)
        
        # Close the popup when clicking the X
        success_popup.protocol("WM_DELETE_WINDOW", lambda: self.close_success_popup(success_popup))
    
    def close_success_popup(self, popup):
        """Close success popup and reset button"""
        popup.destroy()
        # Reset button to normal state
        if hasattr(self, 'maint_call_btn'):
            self.maint_call_btn.config(state="normal")
        add_to_message_log("Success popup closed, button reset")

    def update_light_options(self):
        """Update combobox options based on current line"""
        if self.data.current_line == "Green":
        # Green Line lights
            lights = [
            "Light 1",
            "Light 13",
            "Light 28", 
            "Light 57",
            "Light 19"
            ]
        else:  # Red line
        # Red Line lights
            lights = [
            "Light 9",
            "Light 15",
            "Light 11"
            ]
        self.light_selector['values'] = lights
        if lights:
            self.light_selector.set(lights[0])
            self.update_light_display()
           
    def on_line_changed(self):
        """Update all left panel components when line changes"""
        print(f"Left panel: Line changed to {self.data.current_line}")  # Debug
        self.update_crossing_options()
        self.update_switch_options()
        self.update_light_options()
        # Force update display for first item in each category
        if self.crossing_selector['values']:
            self.crossing_selector.set(self.crossing_selector['values'][0])
            self.update_crossing_display()
    
        if self.switch_selector['values']:
            self.switch_selector.set(self.switch_selector['values'][0])
            self.update_switch_display()
    
        if self.light_selector['values']:
            self.light_selector.set(self.light_selector['values'][0])
            self.update_light_display()
   
    def update_crossing_display(self, event=None):
        selected = self.crossing_selector.get()
        crossings = self.data.filtered_track_data.get("crossings", {})
        if selected in crossings:
            data = crossings[selected]
            self.crossing_condition.config(state='normal')
            self.crossing_condition.delete(0, tk.END)
            self.crossing_condition.insert(0, data["condition"])
            self.crossing_condition.config(state='readonly')
            self.crossing_lights.set(data["lights"])
            self.crossing_bar.set(data["bar"])
   
    def update_crossing_lights(self, event=None):
        selected = self.crossing_selector.get()
        if selected in self.data.track_data["crossings"]:
            old_value = self.data.track_data["crossings"][selected]["lights"]
            new_value = self.crossing_lights.get()
            self.data.track_data["crossings"][selected]["lights"] = self.crossing_lights.get()
            message_logger.log(f"Crossing {selected}: Lights changed from {old_value} to {new_value}")

    def update_switch_display(self, event=None):
        selected = self.switch_selector.get()
        switches = self.data.filtered_track_data.get("switches", {})
        if selected in switches:
            data = switches[selected]
            self.switch_condition.config(state='normal')
            self.switch_condition.delete(0, tk.END)
            self.switch_condition.insert(0, data["condition"])
            self.switch_condition.config(state='readonly')
            self.switch_direction.set(data["direction"])
   
    def update_switch_direction(self, event=None):
        """Update switch direction and log the change"""
        selected = self.switch_selector.get()
        if selected in self.data.track_data["switches"]:
            old_value = self.data.track_data["switches"][selected]["direction"]
            new_value = self.switch_direction.get()
            self.data.track_data["switches"][selected]["direction"] = new_value
            message_logger.log(f"Switch {selected}: Direction changed from {old_value} to {new_value}")

            # Create log message in the specific format
            # Extract block numbers from the switch name or direction
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
            # Parse the direction to get block numbers
            switch_mapping = {
            "Switch 12-13": ("12", "1"),      # 12 to 1
            "Switch 28-29": ("28", "29"),     # 28 to 29
            "Switch 57-Yard": ("57", "0"),    # 0 to 57 (Yard is represented as 0)
            "Switch 62-Yard": ("62", "0"),    # Alternative yard switch
            "Switch 1-13": ("1", "13"),       # Red line switch
            "Switch 150-28": ("150", "28"),   # Another red line switch
            "Switch 76-77": ("76", "77"),     # 76 to 77
            "Switch 85-100": ("85", "100")    # 85 to 100
        }
        
        # Get the appropriate block number based on switch name
        ctc_block = ""
        if selected in switch_mapping:
            # Use the first block in the mapping for CTC log
            ctc_block = switch_mapping[selected][0]
        else:
            # Try to extract block number from switch name
            import re
            numbers = re.findall(r'\d+', selected)
            if numbers:
                ctc_block = numbers[0]  # Use first number found
        
        # Create CTC format log message
        if ctc_block:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{timestamp} CTC REQUEST: Toggle Switch {ctc_block} on {self.data.current_line} track"
            message_logger.log(log_message, "INFO")
        
        # Also log the detailed change
        message_logger.log(f"Switch {selected}: Direction changed from {old_value} to {new_value}")
        # # Send switch state to Track Model
        # if ctc_block and hasattr(self.data, 'send_switch_to_track_model'):
        #     numeric_pos = 0 if "Yard" in new_value or "-1" in new_value else 1
        #     self.data.track_data["switches"][selected]["numeric_position"] = numeric_pos
        #     self.data.send_switch_to_track_model(self.data.current_line, ctc_block, new_value)
        #     add_to_message_log(f"Switch {ctc_block}: Direction {new_value} sent to Track Model")
        
   
    def update_light_display(self, event=None):
        selected = self.light_selector.get()
        lights = self.data.filtered_track_data.get("lights", {})
        if selected in lights:
            data = lights[selected]
            self.light_condition.config(state='normal')
            self.light_condition.delete(0, tk.END)
            self.light_condition.insert(0, data["condition"])
            self.light_condition.config(state='readonly')
            self.light_signal.set(data["signal"])
   
    def update_light_signal(self, event=None):
        selected = self.light_selector.get()
        if selected in self.data.track_data["lights"]:
            old_value = self.data.track_data["lights"][selected]["signal"]
            new_value = self.light_signal.get()
            self.data.track_data["lights"][selected]["signal"] = new_value
            message_logger.log(f"Light {selected}: Signal changed from {old_value} to {new_value}")
            
            # Extract block number from light name (e.g., "Light 13" -> "13")
            import re
            block_match = re.search(r'\d+', selected)
            if block_match:
                block = block_match.group()
                # Send light state to CTC and Track Model
                if hasattr(self.data, 'send_light_state'):
                    self.data.send_light_state(self.data.current_line, block, new_value)
                    add_to_message_log(f"Light {block}: {new_value} sent to CTC and Track Model")


    def handle_maintenance_request(self):
        """Handle maintenance request - enable editable fields"""
        print("LeftPanel: Handling maintenance request")
        
        # Enable switch controls for maintenance
        self.switch_direction.config(state='readonly')
        
        # Visual feedback for maintenance mode
        self.switch_direction.config(background='#ffffcc')
        
        # Add maintenance-specific styling
        for widget in [self.switch_selector, self.light_selector, self.crossing_selector]:
            widget.config(background='#fff0cc')
        
        add_to_message_log("LeftPanel: Maintenance controls enabled")


    def update_mode_ui(self):
        # Refresh UI based on maintenance mode
        # pass
        """Update UI elements based on maintenance mode"""
        # enable/diable comoboxes based on mainteneance mode and specific edits
        switch_changes = self.data.is_changeable("switches")
        light_changes = self.data.is_changeable("lights")
        crossing_changes = self.data.is_changeable("crossing")

        # update switch controls
        if switch_changes:
            self.switch_direction.config(state='readonly')
            add_to_message_log("switch controls enabled for maintenance")
        else:
            self.switch_direction.config(state='disabled')


        # Enable/disable comboboxes based on maintenance mode
        if self.data.maintenance_mode:
        # Maintenance mode ON
            self.switch_direction.config(state='readonly')
            self.switch_direction.config(background='#ffffcc')
        
        # Visual feedback for maintenance mode
            for widget in [self.switch_selector, self.light_selector, self.crossing_selector]:
                widget.config(background='#fff0cc')
        
            add_to_message_log("Maintenance Mode: Switch controls enabled")
        else:
            # Maintenance mode OFF
            self.switch_direction.config(state='disabled')
            self.switch_direction.config(background='white')
        
            # Reset backgrounds
            for widget in [self.switch_selector, self.light_selector, self.crossing_selector]:
                widget.config(background='white')
        
        
        #update light controls
        self.light_signal.config(state='disabled')

        # Update crossing controls (always disabled in this design)
        self.crossing_lights.config(state='disabled')
        self.crossing_bar.config(state='disabled')

        # Visual feedback - change background colors to show editable state
        self.update_visual_feedback()

    def update_visual_feedback(self):
        """Change background colors to indicate editable fields"""
        switch_editable = self.data.is_changeable("switches")
       
        if switch_editable:
            # Make editable fields stand out
            self.switch_direction.config(background='#ffffcc')  # Light yellow for editable
        else:
            self.switch_direction.config(background='white')    # Normal white for read-only
           
        # Keep non-editable fields with normal background
        self.light_signal.config(background='#f0f0f0')          # Grayed out
        self.crossing_lights.config(background='#f0f0f0')
        self.crossing_bar.config(background='#f0f0f0')
   
    def update_switch_direction(self, event=None):
        """Only allow switch direction changes if editable"""
        if not self.data.is_changeable("switches"):
            add_to_message_log("WARNING: Switch changes not allowed in current mode")
            return
           
        selected = self.switch_selector.get()
        if selected in self.data.track_data["switches"]:
            old_value = self.data.track_data["switches"][selected]["direction"]
            new_value = self.switch_direction.get()
            self.data.track_data["switches"][selected]["direction"] = new_value
            add_to_message_log(f"Switch {selected}: Direction changed from {old_value} to {new_value}")
            
            # Send switch state to Track Model
            if hasattr(self.data, 'send_switch_to_track_model'):
                # Extract block number from switch name (e.g., "Switch 12-13" -> "12")
                import re
                numbers = re.findall(r'\d+', selected)
                block = numbers[0] if numbers else ""
                
                # Determine numeric position based on direction
                numeric_pos = 0 if "Yard" in new_value or "-1" in new_value else 1
                self.data.track_data["switches"][selected]["numeric_position"] = numeric_pos
                self.data.send_switch_to_track_model(self.data.current_line, block, new_value)
                add_to_message_log(f"Switch {block}: Direction {new_value} sent to Track Model")
   
    def update_crossing_lights(self, event=None):
        selected = self.crossing_selector.get()
        if selected in self.data.track_data["crossings"]:
            old_value = self.data.track_data["crossings"][selected]["lights"]
            new_value = self.crossing_lights.get()
            self.data.track_data["crossings"][selected]["lights"] = self.crossing_lights.get()
            message_logger.log(f"Crossing {selected}: Lights changed from {old_value} to {new_value}")
            
            # Extract block number and send to CTC/Track Model
            import re
            block_match = re.search(r'\d+', selected)
            if block_match:
                block = block_match.group()
                bar_state = self.data.track_data["crossings"][selected].get("bar", "Open")
                if hasattr(self.data, 'send_railway_state'):
                    self.data.send_railway_state(self.data.current_line, block, bar_state)
                    add_to_message_log(f"Railway Crossing {block}: sent to CTC and Track Model")

    def update_crossing_bar(self, event=None):
        """Handle crossing bar state changes"""
        selected = self.crossing_selector.get()
        if selected in self.data.track_data["crossings"]:
            old_value = self.data.track_data["crossings"][selected].get("bar", "Open")
            new_value = self.crossing_bar.get()
            self.data.track_data["crossings"][selected]["bar"] = new_value
            message_logger.log(f"Crossing {selected}: Bar changed from {old_value} to {new_value}")
            
            import re
            block_match = re.search(r'\d+', selected)
            if block_match:
                block = block_match.group()
                if hasattr(self.data, 'send_railway_state'):
                    self.data.send_railway_state(self.data.current_line, block, new_value)
                    add_to_message_log(f"Railway Crossing {block}: Bar {new_value} sent")
   
    def update_light_signal(self, event=None):
        """Prevent light signal changes"""
        if self.data.maintenance_mode:
            add_to_message_log("WARNING: Light signal changes not permitted in maintenance mode")
            # Revert to original value
            self.update_light_display()

test_data = UITestData()
# Create the left panel with mock data
left_panel = LeftPanel(main_frame, test_data)
left_panel.pack(side="left", fill="y", padx=5, pady=5)

#######################################################################################
#######################################################################################

# ---------- RIGHT PANEL ---------- #
class RightPanel(tk.Frame):
    # Check how you're creating the RightPanel
# Ensure test_data contains the full block_data with all columns
    print(f"DEBUG: Block data length: {len(test_data.block_data)}")
    print(f"DEBUG: First row: {test_data.block_data[0] if test_data.block_data else 'Empty'}")
    print(f"DEBUG: Row structure: {[len(row) for row in test_data.block_data[:5]] if test_data.block_data else 'No data'}")

    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d', width=250)
        self.pack_propagate(False)
        self.data = data

        # Connect line change callback
        self.data.on_line_change.append(self.on_line_changed)
        self.data.on_block_change.append(self.on_block_data_changed)

        # Initialize attributes first
        self.block_num_label = None
        self.line_label = None
        self.section_label = None
        self.occupied_label = None
        self.block_combo = None

        # Initialize data structures
        self.initialize_data()
    
        # Create all UI components
        self.create_widgets()

        # self.set_default_commanded_values()
    
        # Initialize with current data
        self.update_block_options()

        # Set initial yard to station commands
        self.set_yard_to_station_commands()

        
    def initialize_data(self):
        """Initialize data structures"""
        # Store information about currently selected block
        self.current_block_info = {}

        # Dictionaries for commanded values by line and block
        self.commanded_authority = {"Blue": {}, "Green": {}, "Red": {}}
        self.commanded_speed = {"Blue": {}, "Green": {}, "Red": {}}
        
        # Dictionaries for suggested values by line and block
        self.suggested_authority = {"Blue": {}, "Green": {}, "Red": {}}
        self.suggested_speed = {"Blue": {}, "Green": {}, "Red": {}}


        # Clear any search filters and show all data
        if hasattr(self.data, 'filtered_block_data'):
            self.data.filtered_block_data = self.data.block_data.copy()        
        
        
    def on_block_data_changed(self, row_index, col_index, new_value):
        """Update UI when block data changes"""
        # Update current block display if the changed block is selected
        selected_block = self.block_combo.get()
        if selected_block:
            block_num = self.data.block_data[row_index][2]
            if str(block_num) == str(selected_block):
                self.update_current_block_info()
        
        # Update the table in maintenance mode
        if self.data.maintenance_mode:
            self.create_block_table()
        
        add_to_message_log(f"[Main UI] Block {self.data.block_data[row_index][2]} updated to {new_value}")
   
    def create_widgets(self):
        """Create all UI components"""
        # Block selector
        block_frame = tk.Frame(self, bg='#cccccc')
        block_frame.pack(fill=tk.X, pady=5)
        tk.Label(block_frame, text="Block", bg='#cccccc').pack(side=tk.LEFT, padx=5)
       
        # Update block combo based on current line
        self.block_combo = ttk.Combobox(block_frame, width=15, state='readonly')
        self.block_combo.pack(side=tk.LEFT, padx=5)
        self.block_combo.bind('<<ComboboxSelected>>', self.on_block_selected)
        
        # Current block section
        self.create_current_block_section()
        
        # Suggested section
        self.create_suggested_section()
       
        # Commanded section (YOUR ORIGINAL DESIGN)
        self.create_commanded_section()
       
        # Search and block table
        self.create_block_table_section()

    def update_block_options(self):
        """Update block selector based on current line"""
        print(f"DEBUG: Updating block options for {self.data.current_line} line")

        # get blocks for current line
        blocks = []
        if hasattr(self.data, 'block_data') and self.data.block_data:
            for row in self.data.block_data:
                if row[1] == self.data.current_line:
                    blocks.append(str(row[2]))

        ## Remove duplicates and sort
        blocks = sorted(list(set(blocks)), key=lambda x: int(x) if x.isdigit() else x)
        
        print(f"DEBUG: Found {len(blocks)} blocks: {blocks}")
        if blocks:
            print(f"DEBUG: First 5 blocks: {blocks[:5]}")
            print(f"DEBUG: Last 5 blocks: {blocks[-5:]}")
        
        if self.block_combo:
            self.block_combo['values'] = blocks
            if blocks:
                self.block_combo.set(blocks[0])
                # Only update current block info if labels exist
                if hasattr(self, 'line_label') and self.line_label:
                    self.update_current_block_info()
                else:
                    self.block_combo.set("")
            # Preserve selection if possible
            # current_selection = self.block_combo.get()
            # if current_selection in blocks:
            #     self.block_combo.set(current_selection)
            # else:
            #     self.block_combo.set(blocks[0])
            # self.update_current_block_info()

    def on_block_selected(self, event):
        """When a block is selected from dropdown"""
        self.update_current_block_info()
        self.update_suggested_display()
        self.update_commanded_display()

    def create_current_block_section(self):
        """Display current selected block information"""
        current_block_frame = tk.LabelFrame(self, text="Current Block:", 
                                               bg='#cccccc', font=('Arial', 10, 'bold'))
        current_block_frame.pack(fill=tk.X, pady=5)
        
        # # Occupied status display
        # tk.Label(current_block_frame, text="Occupancy:", bg='#cccccc',
        #         width=8).grid(row=1, column=2, padx=2, pady=2, sticky='w')
        # self.occupied_label = tk.Label(current_block_frame, text="", bg='white',
        #                               width=8, relief=tk.SUNKEN)
        # self.occupied_label.grid(row=1, column=1, padx=2, pady=2, sticky='w')

        # # Line
        # tk.Label(current_block_frame, text="Line:", bg='#cccccc', width=10).grid(row=0, column=2, padx=2, pady=2, sticky='w')
        # self.line_label = tk.Label(current_block_frame, text="N/A", bg='white', width=8, relief=tk.SUNKEN)  # THIS WAS MISSING
        # self.line_label.grid(row=0, column=3, padx=2, pady=2, sticky='w')

        # Block number display
        tk.Label(current_block_frame, text="Block #:", bg='#cccccc', 
                width=8).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.block_num_label = tk.Label(current_block_frame, text="n/a", bg='white', 
                                       width=8, relief=tk.SUNKEN)
        self.block_num_label.grid(row=0, column=1, padx=3, pady=2, sticky='w')
        
        # Section
        tk.Label(current_block_frame, text="Section:", bg='#cccccc', width=10).grid(row=1, column=0, padx=2, pady=2, sticky='w')
        self.section_label = tk.Label(current_block_frame, text="N/A", bg='white', width=8, relief=tk.SUNKEN)
        self.section_label.grid(row=1, column=1, padx=4, pady=2, sticky='w')

    def update_current_block_info(self):
        """Update current block display from data"""
        selected_block = self.block_combo.get()
        print(f"DEBUG: Updating current block info for block: {selected_block}")  # Debug

        if selected_block:
            # Find block data
            # for current line
            found = False
            for row in self.data.block_data:
                if row[1] == self.data.current_line and str(row[2]) == str(selected_block):
                    print(f"DEBUG: Found matching row: {row}")  # Debug
                    
                    # Update labels (only 4 columns now)
                    self.block_num_label.config(text=row[2])
                    
                    # # Line with color
                    # line_color = '#66cc66' if row[1] == "Green" else '#ff6666'
                    # self.line_label.config(text=row[1], bg=line_color)
                
                # Section (now in column 3 instead of 4)
                    self.section_label.config(text=row[3] if len(row) > 3 else "")

                    # Color coding for occupancy
                    occupied_text = row[0] if len(row) > 0 else "No"
                    occupied_color = '#ffcccc' if occupied_text == "Yes" else '#ccffcc'
                    self.occupied_label.config(text=occupied_text, bg=occupied_color)

                    found = True
                    break #exits the loop once finding matching new row
            if not found:
                print(f"DEBUG: No matching row found for block {selected_block}")
                    # Set default values
                self.block_num_label.config(text="N/A")
                self.line_label.config(text="N/A", bg='white')
                self.section_label.config(text="N/A")
                self.occupied_label(text="N/A", bg='white')
        else:
                print("DEBUG: No block selected")
                # Set default values
                self.block_num_label.config(text="N/A")
                self.line_label.config(text="N/A", bg='white')
                self.section_label.config(text="N/A")
                self.occupied_label(text="N/A", bg='white')

    def create_suggested_section(self):
        """Display suggested authority and speed"""
        suggested_frame = tk.LabelFrame(self, text="Suggested:",
                                       bg='#cccccc', font=('Arial', 10, 'bold'))
        suggested_frame.pack(fill=tk.X, pady=5)
        
        # Authority display
        auth_frame = tk.Frame(suggested_frame, bg='#cccccc')
        auth_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(auth_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)

        self.suggested_auth_label = tk.Label(auth_frame, text="0 blocks", bg='white',
                                           relief=tk.SUNKEN, width=12, anchor='w')
        self.suggested_auth_label.pack(side=tk.LEFT, padx=2)
        
        # Speed display
        speed_frame = tk.Frame(suggested_frame, bg='#cccccc')
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(speed_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)

        self.suggested_speed_label = tk.Label(speed_frame, text="0 mph", bg='white',
                                            relief=tk.SUNKEN, width=12, anchor='w')
        self.suggested_speed_label.pack(side=tk.LEFT, padx=2)
   
    def update_suggested_display(self):
        """Update suggested values display"""
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line:
            # Check local storage first
            local_auth = self.suggested_authority.get(current_line, {}).get(selected_block)
            local_speed = self.suggested_speed.get(current_line, {}).get(selected_block)
            
            if local_auth is not None:
                self.suggested_auth_label.config(text=f"{local_auth} blocks")
                self.suggested_speed_label.config(text=f"{local_speed} mph")
            else:
                # No values found - show defaults
                self.suggested_auth_label.config(text="0 blocks")
                self.suggested_speed_label.config(text="0 mph")
        else:
            # No block selected
            self.suggested_auth_label.config(text="N/A")
            self.suggested_speed_label.config(text="N/A")
   
    def create_commanded_section(self):
        """Create commanded values input section - YOUR ORIGINAL DESIGN"""
        commanded_frame = tk.LabelFrame(self, text="Commanded:",
                                   bg='#cccccc', font=('Arial', 10, 'bold'))
        commanded_frame.pack(fill=tk.X, pady=5)
   
        # Authority section - YOUR ORIGINAL DESIGN
        auth_frame = tk.Frame(commanded_frame, bg='#cccccc')
        auth_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(auth_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)
   
        self.auth_entry = tk.Entry(auth_frame, width=10)
        self.auth_entry.insert(0, "2 blocks")  # Default value
        self.auth_entry.pack(side=tk.LEFT, padx=2)
   
        # auth_button = tk.Button(auth_frame, text="Send", width=5, command=self.update_authority)
        # auth_button.pack(side=tk.LEFT)

        # Single "Send All" button for both speed and authority
        send_all_button = tk.Button(auth_frame, text="Send All", width=8, 
                               command=self.send_all_commanded_values)
        send_all_button.pack(side=tk.LEFT, padx=5)

        # Speed section - YOUR ORIGINAL DESIGN
        speed_frame = tk.Frame(commanded_frame, bg='#cccccc')
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(speed_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)
   
        self.speed_entry = tk.Entry(speed_frame, width=10)
        self.speed_entry.insert(0, "38 mph")  # Default value
        self.speed_entry.pack(side=tk.LEFT, padx=2)
   
        # speed_button = tk.Button(speed_frame, text="Send", width=5, command=self.update_speed)
        # speed_button.pack(side=tk.LEFT)

    def send_all_commanded_values(self):
        """Send both speed and authority to Track Model"""
    # Update local storage
        self.update_authority()
        self.update_speed()
    
    # Send combined to Track Model
        # self.send_combined_to_track_model()

    # Change it to this (add the send_commanded_to_track_model call):
    def update_authority(self):
        """Update commanded authority and send to Track Model"""
        new_authority = self.auth_entry.get()
        block = self.block_combo.get()
        current_line = self.data.current_line
    
    # Extract just the number from "X blocks"
        try:
            authority_value = int(new_authority.split()[0])
        except:
            authority_value = 0

        if block and current_line:
            # Store in local storage
            self.commanded_authority[current_line][block] = new_authority
        # Store in shared data if available
            if hasattr(self.data, 'commanded_authority'):
                self.data.commanded_authority[current_line][block] = new_authority
        
        # Send to Track Model immediately (like main_SW.txt does)
            speed = self.speed_entry.get()
            self.send_commanded_to_track_model(current_line, block, speed, new_authority)
    
        add_to_message_log(f"Commanded Authority updated to: {new_authority}")
        self.update_commanded_display()

    def update_speed(self):
        """Update commanded speed and send to Track Model"""
        new_speed = self.speed_entry.get()
        block = self.block_combo.get()
        current_line = self.data.current_line
    
    # Extract just the number from "X mph"
        try:
            speed_value = float(new_speed.split()[0])
        except:
            speed_value = 0.0

        if block and current_line:
        # Store in local storage
            self.commanded_speed[current_line][block] = new_speed
        # Store in shared data if available
        if hasattr(self.data, 'commanded_speed'):
            self.data.commanded_speed[current_line][block] = new_speed
        
        # Send to Track Model immediately (like main_SW.txt does)
        authority = self.auth_entry.get()
        self.send_commanded_to_track_model(current_line, block, new_speed, authority)
    
        add_to_message_log(f"Commanded Speed updated to: {new_speed}")
        self.update_commanded_display()

    # Replace that entire function with this:
    def send_commanded_to_track_model(self, track, block, speed, authority):
        """Send commanded speed and authority to Track Model"""
        try:
            if not block or block == "":
                add_to_message_log("ERROR: No block selected")
                return
        
        # Parse speed value
            try:
                if "mph" in str(speed):
                    speed_value = float(str(speed).replace("mph", "").strip())
                else:
                    speed_value = float(speed)
            except:
                speed_value = 0.0
                add_to_message_log("WARNING: Invalid speed, using 0.0")
        
        # Parse authority value
            try:
                if "blocks" in str(authority):
                    auth_value = int(str(authority).replace("blocks", "").strip())
                else:
                    auth_value = int(authority)
            except:
                auth_value = 0
                add_to_message_log("WARNING: Invalid authority, using 0")
        
        # Create the exact message format Track Model expects
            message = {
            "command": "Speed and Authority",
            "block_number": int(block),
            "commanded_speed": float(speed_value),
            "commanded_authority": int(auth_value),
            "track": track
            }
        
        # Send to Track Model
            if hasattr(self.data, 'server1') and self.data.server1:
                self.data.server1.send_to_ui('Track Model', message)
                add_to_message_log(f"COMMANDED: Block {block} - Speed: {speed_value:.1f} mph, Authority: {auth_value} blocks")
            else:
                add_to_message_log("ERROR: No server connection to Track Model")
        
        except Exception as e:
            add_to_message_log(f"ERROR sending to Track Model: {e}")

    def update_commanded_display(self):
        """Update commanded values display"""
        # Check if widgets are ready
        if not hasattr(self, 'block_combo') or not self.block_combo:
            print("DEBUG: Widgets not ready yet, skipping commanded display update")
            return
        selected_block = self.block_combo.get()
        current_line = self.data.current_line
        
        if selected_block and current_line:
            # Check shared data from RailwayData if available
            if hasattr(self.data, 'commanded_authority'):
                data_auth = self.data.commanded_authority.get(current_line, {}).get(selected_block)
                data_speed = self.data.commanded_speed.get(current_line, {}).get(selected_block)
                
                if data_auth is not None or data_speed is not None:
                    # Update entry fields with values from shared data
                    if data_auth is not None and self.auth_entry.get() != data_auth:
                        self.auth_entry.delete(0, tk.END)
                        self.auth_entry.insert(0, data_auth)
                    if data_speed is not None and self.speed_entry.get() != data_speed:
                        self.speed_entry.delete(0, tk.END)
                        self.speed_entry.insert(0, data_speed)
                    
                    # Update local storage
                    if data_auth is not None:
                        self.commanded_authority[current_line][selected_block] = data_auth
                    if data_speed is not None:
                        self.commanded_speed[current_line][selected_block] = data_speed
                    return
            
            # Fallback to local storage - update entry fields
            local_auth = self.commanded_authority.get(current_line, {}).get(selected_block)
            local_speed = self.commanded_speed.get(current_line, {}).get(selected_block)
            
            if local_auth is not None and self.auth_entry.get() != local_auth:
                self.auth_entry.delete(0, tk.END)
                self.auth_entry.insert(0, local_auth)
            
            if local_speed is not None and self.speed_entry.get() != local_speed:
                self.speed_entry.delete(0, tk.END)
                self.speed_entry.insert(0, local_speed)

    def update_suggested_speed(self, speed_value):
        """Update suggested speed from external source"""
        # selected_block = self.block_combo.get()
        # current_line = self.data.current_line
            # Get the block from the CTC message (not from combo box)
        # We need to pass the block number as a parameter
        print(f"DEBUG: update_suggested_speed called with {speed_value}")
    
    # Store the value for future use
    # For now, just update the display directly
        if speed_value is not None:
            self.suggested_speed_label.config(text=f"{speed_value:.3f} mph")
            add_to_message_log(f"Suggested Speed updated: {speed_value:.3f} mph")
        # if selected_block and current_line and speed_value is not None:
        #     self.suggested_speed[current_line][selected_block] = speed_value
        #     self.suggested_speed_label.config(text=f"{speed_value:.3f} mph")
        #     add_to_message_log(f"Suggested Speed updated to: {speed_value:.3f} mph")

    def update_suggested_authority(self, authority_value):
        """Update suggested authority from external source"""
        print(f"DEBUG: update_suggested_authority called with {authority_value}")
    
        # For now, just update the display directly
        if authority_value is not None:
            self.suggested_auth_label.config(text=f"{authority_value} blocks")
            add_to_message_log(f"Suggested Authority updated: {authority_value} blocks")
        # """Update suggested authority from external source"""
        # selected_block = self.block_combo.get()
        # current_line = self.data.current_line
        
        # if selected_block and current_line and authority_value is not None:
        #     self.suggested_authority[current_line][selected_block] = authority_value
        #     self.suggested_auth_label.config(text=f"{authority_value} blocks")
        #     add_to_message_log(f"Suggested Authority updated to: {authority_value} blocks")

    def create_block_table_section(self):
        """Create block status table section with horizontal scroll"""
        # Search frame
        search_frame = tk.Frame(self, bg='#1a1a4d')
        search_frame.pack(fill=tk.X, pady=5)
        self.block_search_var = tk.StringVar()
        self.block_search_var.trace('w', self.filter_block_table)
        block_search = tk.Entry(search_frame, textvariable=self.block_search_var, width=20)
        block_search.pack(side=tk.LEFT, padx=5)
        tk.Label(search_frame, text="Search", bg='#1a1a4d', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
   
        # Table container - FIXED HEIGHT to match other sections
        table_container = tk.Frame(self, bg='#1a1a4d', height=300)
        table_container.pack(fill=tk.BOTH, expand=True, pady=5)
        table_container.pack_propagate(False)  # Prevent container from shrinking
   
        # Create a frame for canvas and scrollbars
        canvas_frame = tk.Frame(table_container, bg='#1a1a4d')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Horizontal scrollbar (top)
        x_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Vertical scrollbar (right)
        y_scrollbar = tk.Scrollbar(canvas_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        # Canvas for scrolling with BOTH scrollbars
        self.table_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0,
                                     xscrollcommand=x_scrollbar.set,
                                     yscrollcommand=y_scrollbar.set)
        self.table_canvas.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbars
        x_scrollbar.config(command=self.table_canvas.xview)
        y_scrollbar.config(command=self.table_canvas.yview)
        
        # Frame inside canvas for table content
        self.block_table_frame = tk.Frame(self.table_canvas, bg='white')
        self.canvas_window = self.table_canvas.create_window((0, 0), window=self.block_table_frame, anchor="nw")
        
        # Update scroll region after table is created
        def update_scrollregion(event=None):
            # Update the scrollregion to encompass the table frame
            self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
            # Update canvas window width to match canvas width
            self.table_canvas.itemconfig(self.canvas_window, width=self.table_canvas.winfo_width())

        # Configure canvas to expand with container
        def configure_canvas(event):
            # Update canvas window width when canvas is resized
            self.table_canvas.itemconfig(self.canvas_window, width=event.width)
            # Update scroll region
            self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
            update_scrollregion()
        
        self.table_canvas.bind("<Configure>", configure_canvas)
        
        # Mousewheel scrolling for vertical only
        def _on_mousewheel(event):
            self.table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_shift_mousewheel(event):
            self.table_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        self.table_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.table_canvas.bind("<MouseWheel>", _on_shift_mousewheel) # horizontal movement

        self.block_table_frame.bind("<MouseWheel>", _on_mousewheel)
        self.block_table_frame.bind("<MouseWheel>", _on_shift_mousewheel)

        # Initial table creation
        self.create_block_table()
        # Force initial scroll region update
        self.block_table_frame.update_idletasks()
        update_scrollregion()

    def create_block_table(self):
        """Create block status table with compact layout"""
        # Clear existing widgets
        for widget in self.block_table_frame.winfo_children():
            widget.destroy()
        
        print(f"\n=== DEBUG: Creating block table ===")
        print(f"Current line: {self.data.current_line}")
        print(f"Has block_data: {hasattr(self.data, 'block_data')}")
        print(f"Length of block_data: {len(self.data.block_data) if hasattr(self.data, 'block_data') else 'N/A'}")

        # Get data for current line
        display_data = []
        if hasattr(self.data, 'filtered_block_data') and len(self.data.filtered_block_data) > 0:
            print(f"Using filtered_block_data: {len(self.data.filtered_block_data)} rows")
            display_data = [row for row in self.data.filtered_block_data 
                      if row[1] == self.data.current_line]
        else:
            print(f"Using block_data: {len(self.data.block_data) if hasattr(self.data, 'block_data') else 0} rows")
            display_data = [row for row in self.data.block_data 
                      if row[1] == self.data.current_line]
        
        if not display_data:
        # Show message if no data
            tk.Label(self.block_table_frame, text="No block data available", 
                bg='white', fg='red').pack(pady=20)
            return
        print(f"DEBUG: First 5 rows to display: {display_data[:5]}")

        # Headers - 5 columns with COMPACT widths to fit
        headers_frame = tk.Frame(self.block_table_frame, bg='#cccccc')
        headers_frame.pack(fill=tk.X)
        
        # Define column widths for 4 columns (slightly wider since we removed one column)
        col_widths = {'occupied': 8, 'line': 6, 'block': 6, 'section': 10}
        
        # Occupied header
        tk.Label(headers_frame, text="Occupied", bg='#cccccc',
            font=('Arial', 9, 'bold'), width=col_widths['occupied']).pack(side=tk.LEFT, padx=2)
        tk.Label(headers_frame, text="Line", bg='#cccccc',
            font=('Arial', 9, 'bold'), width=col_widths['line']).pack(side=tk.LEFT, padx=2)
        tk.Label(headers_frame, text="Block", bg='#cccccc',
            font=('Arial', 9, 'bold'), width=col_widths['block']).pack(side=tk.LEFT, padx=2)
        tk.Label(headers_frame, text="Section", bg='#cccccc',
            font=('Arial', 9, 'bold'), width=col_widths['section']).pack(side=tk.LEFT, padx=2)
        
        # Data rows
        # self.block_combos = []
        # Data rows
        for row_index, row in enumerate(display_data):
            row_frame = tk.Frame(self.block_table_frame, bg='white')
            row_frame.pack(fill='x', pady=1)

        # Ensure row has exactly 4 elements
        while len(row) < 4:
            row.append("")
        if len(row) > 4:
            row = row[:4]  # Truncate to 4 columns
        
        if self.data.maintenance_mode:
            # MAINTENANCE MODE - Editable occupancy
            occ_combo = ttk.Combobox(row_frame, values=["Yes", "No"], 
                                  width=col_widths['occupied']-2)
            occ_combo.set(row[0] if row[0] in ["Yes", "No"] else "No")
            occ_combo.pack(side=tk.LEFT, padx=2)
            
            # Bind change event
            occ_combo.bind('<<ComboboxSelected>>',
                lambda event, idx=row_index, combo=occ_combo, r=row:
                self.on_block_data_change(r[2], combo.get()))
            
            # Line (read-only with color)
            bg_color = '#66cc66' if row[1] == "Green" else '#ff6666'
            tk.Label(row_frame, text=row[1], bg=bg_color, width=col_widths['line'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)
            
            # Block # (read-only)
            tk.Label(row_frame, text=str(row[2]), bg='white', width=col_widths['block'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)
            
            # Section Letter (read-only)
            tk.Label(row_frame, text=row[3], bg='white', width=col_widths['section'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)
        else:
            # NORMAL MODE - all read-only
            # Occupied with color coding
            occupied_color = '#ffcccc' if row[0] == "Yes" else '#ccffcc'
            tk.Label(row_frame, text=row[0], bg=occupied_color, width=col_widths['occupied'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)
            
            # Line with color
            bg_color = '#66cc66' if row[1] == "Green" else '#ff6666'
            tk.Label(row_frame, text=row[1], bg=bg_color, width=col_widths['line'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)
            
            # Block #
            tk.Label(row_frame, text=str(row[2]), bg='white', width=col_widths['block'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)
            
            # Section Letter
            tk.Label(row_frame, text=row[3], bg='white', width=col_widths['section'],
                   borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=2)

    def on_block_data_change(self, block_num, new_value):
        """Handle block data changes in maintenance mode"""
        # Find and update the block in data
        old_value = None
        found_index = -1
        for i, row in enumerate(self.data.block_data):
            if str(row[2]) == str(block_num):
                old_value = row[0]
                self.data.block_data[i][0] = new_value  # Update occupancy
                found_index = i
                break

            if found_index >= 0:
            # Update filtered data if it exists
                if hasattr(self.data, 'filtered_block_data'):
                    for j, f_row in enumerate(self.data.filtered_block_data):
                        if str(f_row[2]) == str(block_num):
                            self.data.filtered_block_data[j][0] = new_value
                    break

                if old_value is not None:
                    add_to_message_log(f"Block {block_num} occupancy changed from {old_value} to {new_value}")
                else:
                    add_to_message_log(f"Block {block_num} occupancy set to {new_value}")
            else:
                add_to_message_log(f"WARNING: Block {block_num} not found in data")
    
                # Update filtered data if it exists
            if hasattr(self.data, 'filtered_block_data'):
                for j, f_row in enumerate(self.data.filtered_block_data):
                    if str(f_row[2]) == str(block_num):
                        self.data.filtered_block_data[j][0] = new_value
                        break
            
            add_to_message_log(f"Block {block_num} occupancy changed from {old_value} to {new_value}")
            break
    
        # Update current block display if this block is selected
        if self.block_combo.get() == str(block_num):
            self.update_current_block_info()
       
    def filter_block_table(self, *args):
        """Filter block table based on search term"""
        search_term = self.block_search_var.get().lower()
        self.data.filtered_block_data(search_term)
        self.create_block_table()
   
    def update_mode_ui(self):
        """Refresh UI when maintenance mode changes"""
        self.create_block_table()
        self.update_current_block_info()
   
    def on_line_changed(self):
        """Refresh right panel when line changes"""
        self.update_block_options()
        self.create_block_table()
        self.update_current_block_info()
        self.update_suggested_display()
        self.update_commanded_display()
        
    def set_yard_to_station_commands(self):
        """Set hardcoded commanded values for yard to station"""
        current_line = "Green"
        
        # Outbound: Yard (63) to Station (96)
        blocks_outbound = list(range(63, 97))
        authority = len(blocks_outbound) - 1
        
        for block_num in blocks_outbound:
            self.commanded_authority[current_line][str(block_num)] = f"{authority} blocks"
            self.commanded_speed[current_line][str(block_num)] = "31 mph" if authority > 0 else "0 mph"
            authority -= 1
        
        # Return: Station (96) back to Yard (57)
        blocks_return = list(range(96, 56, -1))
        authority = len(blocks_return) - 1
        
        for block_num in blocks_return:
            self.commanded_authority[current_line][str(block_num)] = f"{authority} blocks"
            self.commanded_speed[current_line][str(block_num)] = "31 mph" if authority > 0 else "0 mph"
            authority -= 1
        
        # Final destinations
        self.commanded_authority[current_line]["96"] = "0 blocks"
        self.commanded_speed[current_line]["96"] = "0 mph"
        self.commanded_authority[current_line]["57"] = "0 blocks"
        self.commanded_speed[current_line]["57"] = "0 mph"
        
        # Update display if on Green line
        if self.data.current_line == "Green":
            self.update_commanded_display()





# # ---------- RIGHT PANEL ---------- #
# class RightPanel(tk.Frame):
#     def __init__(self, parent, data):
#         super().__init__(parent, bg='#1a1a4d', width=250)
#         self.pack_propagate(False)
#         self.data = data
        
#         #attributes for suggested speed/authority
#         self.suggested_speed_label = None
#         self.suggested_authority_label = None
#         # self.create_suggested_section()

#         # Connect line change callback
#         self.data.on_line_change.append(self.on_line_changed)
#         self.data.on_block_change.append(self.on_block_data_changed)

#          # Clear any search filters and show all data
#         if hasattr(self.data, 'filtered_block_data'):
#             self.data.filtered_block_data = self.data.block_data.copy()
#         self.create_widgets()
#     def on_block_data_changed(self, row_index, col_index, new_value):
#         # Update only the affected row in the table if maintenance mode
#         if self.data.maintenance_mode:
#             self.create_block_table()  # Simple approach: rebuild table
#         add_to_message_log(f"[Main UI] Block {self.data.block_data[row_index][2]} updated to {new_value}")
   
#     def create_widgets(self):
#         # Block selector
#         block_frame = tk.Frame(self, bg='#cccccc')
#         block_frame.pack(fill=tk.X, pady=5)
#         tk.Label(block_frame, text="Block", bg='#cccccc').pack(side=tk.LEFT, padx=5)
       
#         # Update block combo based on current line
#         self.block_combo = ttk.Combobox(block_frame, width=15, state='readonly')
#         self.block_combo.pack(side=tk.LEFT, padx=5)
#         self.update_block_options()

#         # Suggested section
#         self.create_suggested_section()
       
#         # Commanded section
#         self.create_commanded_section()
       
#         # Search and block table
#         self.create_block_table_section()

#     def update_block_options(self):
#         """Update block selector based on current line"""
#         blocks = [row[2] for row in self.data.block_data]
#         self.block_combo['values'] = blocks
#         if blocks:
#             self.block_combo.set(blocks[0])
   
#     def on_line_changed(self):
#         """Refresh right panel when line changes"""
#         print(f"Right panel: Line changed to {self.data.current_line}")
#         self.update_block_options()
#         self.create_block_table()
   
#     def create_suggested_section(self):
#         suggested_frame = tk.LabelFrame(self, text="Suggested:",
#                                        bg='#cccccc', font=('Arial', 10, 'bold'))
#         suggested_frame.pack(fill=tk.X, pady=5)
#        # Authority:
#         tk.Label(suggested_frame, text="Authority:", bg='#cccccc').pack(anchor='w', padx=5)
#         tk.Label(suggested_frame, text="0 blocks", bg='white',
#                 relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=2)
#         #Speed:
#         tk.Label(suggested_frame, text="Speed:", bg='#cccccc').pack(anchor='w', padx=5)
#         tk.Label(suggested_frame, text="0.000 mph", bg='white',
#                 relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=2)
   
#     def create_commanded_section(self):
#         commanded_frame = tk.LabelFrame(self, text="Commanded:",
#                                    bg='#cccccc', font=('Arial', 10, 'bold'))
#         commanded_frame.pack(fill=tk.X, pady=5)
   
#     # Authority section
#         auth_frame = tk.Frame(commanded_frame, bg='#cccccc')
#         auth_frame.pack(fill=tk.X, padx=5, pady=2)
#         tk.Label(auth_frame, text="Authority:", bg='#cccccc').pack(side=tk.LEFT)
   
#         self.auth_entry = tk.Entry(auth_frame, width=10)
#         self.auth_entry.insert(0, "2 blocks")  # Default value
#         self.auth_entry.pack(side=tk.LEFT, padx=2)
   
#         auth_button = tk.Button(auth_frame, text="Send", width=5, command=self.update_authority)
#         auth_button.pack(side=tk.LEFT)
   
#     # Speed section
#         speed_frame = tk.Frame(commanded_frame, bg='#cccccc')
#         speed_frame.pack(fill=tk.X, padx=5, pady=2)
#         tk.Label(speed_frame, text="Speed:", bg='#cccccc').pack(side=tk.LEFT)
   
#         self.speed_entry = tk.Entry(speed_frame, width=10)
#         self.speed_entry.insert(0, "38 mph")  # Default value
#         self.speed_entry.pack(side=tk.LEFT, padx=2)
   
#         speed_button = tk.Button(speed_frame, text="Send", width=5, command=self.update_speed)
#         speed_button.pack(side=tk.LEFT)

#     def update_authority(self):
#         """Update commanded authority and log the change"""
#         new_authority = self.auth_entry.get()
#         add_to_message_log(f"Commanded Authority updated to: {new_authority}")
#         # Here you would also update the backend data structure
#         # commanded_authority.append(new_authority)

#     def update_speed(self):
#         """Update commanded speed and log the change"""
#         new_speed = self.speed_entry.get()
#         add_to_message_log(f"Commanded Speed updated to: {new_speed}")
#     # Here you would also update the backend data structure
#     # commanded_speed.append(new_speed)
#     #######################################################################################################################
#     ######################################################################################################################
#     def update_suggested_speed(self, speed_value):
#     # """Update the suggested speed display with formatted value"""
#         try:
#             if speed_value is not None:
#                 formatted_speed = f"{speed_value:.3f} mph"
#                 self.suggested_speed_label.config(text=formatted_speed)
#                 add_to_message_log(f"Suggested Speed updated to: {formatted_speed}")
#             else:
#                 add_to_message_log(f"ERROR: Invalid speed value received", "ERROR")
#         except Exception as e:
#             add_to_message_log(f"ERROR updating speed display: {e}", "ERROR")

#     def update_suggested_authority(self, authority_value):
#         """Update the suggested authority display"""
#         try:
#             if authority_value is not None:
#                 formatted_authority = f"{authority_value} blocks"
#                 self.suggested_authority_label.config(text=formatted_authority)
#                 add_to_message_log(f"Suggested Authority updated to: {formatted_authority}")
#             # else:
#             #     add_to_message_log("ERROR: Invalid authority value received", "ERROR")
#         except Exception as e:
#             add_to_message_log(f"ERROR updating authority display: {e}", "ERROR")
#    ############################################################################################################################
#    ##############################################################################################################################
#     def create_block_table_section(self):
#     # Search
#         search_frame = tk.Frame(self, bg='#1a1a4d')
#         search_frame.pack(fill=tk.X, pady=5)
#         self.block_search_var = tk.StringVar()
#         self.block_search_var.trace('w', self.filter_block_table)
#         block_search = tk.Entry(search_frame, textvariable=self.block_search_var, width=20)
#         block_search.pack(side=tk.LEFT, padx=5)
#         tk.Label(search_frame, text="Search", bg='#1a1a4d', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
   
#     # Create scrollable table with fixed height
#         table_container = tk.Frame(self, bg='white', relief=tk.SUNKEN, borderwidth=2, height=300)
#         table_container.pack(fill=tk.BOTH, expand=True, pady=5)
#         table_container.pack_propagate(False)  # Prevent container from shrinking
   
#     # Canvas and scrollbar
#         canvas = tk.Canvas(table_container, bg='white', highlightthickness=0, width=350)
#         scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
#         self.block_table_frame = tk.Frame(canvas, bg='white')
    
#     # # Create a frame for canvas and scrollbar
#         # scroll_frame = tk.Frame(table_container, bg='white')
#         # scroll_frame.pack(fill=tk.BOTH, expand=True)
   
   
#     # Configure scrolling
#         self.block_table_frame.bind(
#             "<Configure>",
#             lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
#         )
   
#         canvas.create_window((0, 0), window=self.block_table_frame, anchor="nw")
#         canvas.configure(yscrollcommand=scrollbar.set)
   
#     # Pack canvas and scrollbar
#     # def configure_canvas(event):
#     #     canvas.itemconfig(canvas_window, width=event.width)
#     #     canvas.bind("<Configure>", configure_canvas)
#         canvas.pack(side="left", fill="both", expand=True)
#         scrollbar.pack(side="right", fill="y")
   
#     # Add mousewheel scrolling
#     def _on_mousewheel(self, event):
#         canvas.yview_scroll(int(-1*(event.delta/120)), "units")

#         # Force the table to be created immediately with ALL data
#         self.block_search_var.set("")  # Clear any search text
#         self.data.filter_block_data("")  # Show all data
#         return "break" # Prevent default scrolling
    
#         canvas.bind("<MouseWheel>", _on_mousewheel)
#         self.block_table_frame.bind("<MouseWheel>", _on_mousewheel)
#         table_container.bind("<MouseWheel>", _on_mousewheel)
#         # self.block_search_var.set("")  # Clear any search text
#         self.data.filter_block_data("")  # Show all data
#         self.create_block_table()

#     def create_block_table(self):
#         print(f"DEBUG: Creating block table in frame: {self.block_table_frame}")
#         # print(f"DEBUG: Frame width: {self.block_table_frame.winfo_width()}, height: {self.block_table_frame.winfo_height()}")

#     # Clear existing widgets
#         for widget in self.block_table_frame.winfo_children():
#             widget.destroy()
#      # Get the filtered data
#         block_data = self.data.get_block_table_data()

#         # print(f"DEBUG: Block data received: {len(block_data)} rows")
#         # if block_data:
#             # print(f"DEBUG: First row: {block_data[0]}")
#             # print(f"DEBUG: Row structure: {[len(row) for row in block_data]}")

#     # Headers - 4 columns
#         headers_frame = tk.Frame(self.block_table_frame, bg='#cccccc')
#         headers_frame.pack(fill=tk.X)
   
#     # define consistent widths for all columns
#         col_widths = {
#             'occupied': 8,
#             'line': 4,
#             'block': 5,
#             'section': 6,
#             'infrastructure': 14
#         }

#         tk.Label(headers_frame, text="Occupied", bg='#cccccc',
#             font=('Arial', 8, 'bold'), width=col_widths['occupied']).pack(side=tk.LEFT, padx=1)
#         tk.Label(headers_frame, text="Line", bg='#cccccc',
#             font=('Arial', 8, 'bold'), width=col_widths['line']).pack(side=tk.LEFT, padx=1)
#         tk.Label(headers_frame, text="Block", bg='#cccccc',
#             font=('Arial', 8, 'bold'), width=col_widths['block']).pack(side=tk.LEFT, padx=1)
#         tk.Label(headers_frame, text="Section", bg='#cccccc',
#             font=('Arial', 8, 'bold'), width=col_widths['section']).pack(side=tk.LEFT, padx=1)
#         tk.Label(headers_frame, text="Infrastructure", bg='#cccccc',
#             font=('Arial', 8, 'bold'), width=col_widths['infrastructure']).pack(side=tk.LEFT, padx=1)
#     # Data rows
#         self.block_combos = []  # Store references to comboboxes

#         # Use filtered data for display
#         display_data = self.data.filtered_block_data if hasattr(self.data, 'filtered_block_data') else self.data.block_data

#         for row_index, row in enumerate(display_data):
#             # print(f"DEBUG: Processing row {row_index}: {row}")
#             row_frame = tk.Frame(self.block_table_frame, bg='white')
#             row_frame.pack(fill='x', pady=1)
#             try:
#                 while len(row) < 5:
#                     row.append("")  # Add empty strings for missing columns

#                 if self.data.maintenance_mode:
#             # Editable in maintenance mode - OCCUPIED COMBO
#                     occ_combo = ttk.Combobox(row_frame, values=["Yes", "No"], width=col_widths['occupied']-2)
#                     occ_combo.set(row[0])
#                     occ_combo.pack(side=tk.LEFT, padx=1)

#             # Bind the change event to update data model
#                     occ_combo.bind('<<ComboboxSelected>>',
#                         lambda event, idx=row_index, combo=occ_combo:
#                         self.on_block_data_change(idx, 0, combo.get()))
           
#             # LINE - READ ONLY (track color should not change)
#                     bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
#                     tk.Label(row_frame, text=row[1], bg=bg_color, width=col_widths['line'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
           
#             # Block number (read-only)
#                     tk.Label(row_frame, text=row[2], bg='white', width=col_widths['block'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
            
#             # Section letter (read-only)
#                     tk.Label(row_frame, text=row[3], bg='white', width=col_widths['section'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
             
#             #  Infrastructure (read-only) 
#                     tk.Label(row_frame, text=str(row[4]), bg='white', width=col_widths['infrastructure'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
#             # Store combos for potential access
#                     self.block_combos.append(occ_combo)
           
#                 else:
#             # print(f"DEBUG: Creating normal mode labels for block {row[2]}")
#                     tk.Label(row_frame, text=row[0], bg='white', width=col_widths['occupied'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
            
#                     bg_color = '#66cc66' if row[1] == "Green" else '#ff6666' if row[1] == "Red" else '#6666ff'
#                     tk.Label(row_frame, text=row[1], bg=bg_color, width=col_widths['line'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
            
#                     tk.Label(row_frame, text=row[2], bg='white', width=col_widths['block'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
            
#                     tk.Label(row_frame, text=row[3], bg='white', width=col_widths['section'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)

#                     tk.Label(row_frame, text=str(row[4]), bg='white', width=col_widths['infrastructure'],
#                     borderwidth=1, relief=tk.GROOVE).pack(side=tk.LEFT, padx=1)
#             except Exception as e:
#                 print(f"Error creating row {row_index}: {e} - Row data: {row}")
    
#         # if i < 3:  # Debug first 3 rows
#         #     print(f"DEBUG: Created row {i}: {row}")
    
#         # print(f"DEBUG: Finished creating {len(block_data)} rows")
#     # Force update
#         self.block_table_frame.update()            
#     # print("DEBUG: Finished creating block table")

#     def on_block_data_change(self, row_index, col_index, new_value):
#         """Callback when any block data is changed in maintenance mode"""
#         print(f"Block data changed: row {row_index}, col {col_index}, value '{new_value}'")
#         self.data.update_block_data(row_index, col_index, new_value)
       
#     def filter_block_table(self, *args):
#         search_term = self.block_search_var.get().lower()
#         self.data.filter_block_data(search_term)
#         self.create_block_table()
   
#     def update_mode_ui(self):
#         """Refresh block table when mode changes"""
#         self.create_block_table()
#############################################################################################################
################################################################################################################
    
#############################################################################################################
################################################################################################################
# Create the right panel with mock data
right_panel = RightPanel(main_frame, test_data)
right_panel.pack(side="right", fill="y", padx=5, pady=5)

# ---------- MAINTENANCE SCREEN (simple placeholder) ---------- #
maint_label = tk.Label(maintenance_frame, text="Maintenance Mode Active", bg="#0b1443", fg="white", font=("Arial", 24))
maint_label.place(relx=0.3, rely=0.4)

# Raise main screen by default
main_frame.tkraise()

root.mainloop()