# track_config.py
import os
import re

class TrackConfig:
    def __init__(self):
        # Load ALL track configurations from TXT files
        self.tracks = {}
        self.load_all_tracks()
        
    def get_data_file_path(self, filename):
        """Get the correct path to data files - works in both development and Git environments"""
        # Get the directory where this Python file (track_config.py) is located
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try multiple possible locations
        possible_locations = [
            os.path.join(current_file_dir, filename),  # Same directory as track_config.py
            os.path.join(current_file_dir, 'data', filename),  # data subdirectory
            os.path.join(current_file_dir, '..', 'data', filename),  # Parent's data directory
            os.path.join(current_file_dir, '..', '..', 'data', filename),  # Wayside_Controller/SW/data
            os.path.join(os.getcwd(), 'data', filename),  # data subdirectory of working dir
            os.path.join(os.getcwd(), 'Wayside_Controller', 'SW', 'data', filename),  # Your specific structure
            os.path.join(os.getcwd(), filename),  # Directly in working directory
        ]
        
        for path in possible_locations:
            normalized_path = os.path.normpath(path)
            if os.path.exists(normalized_path):
                print(f"✅ TrackConfig found data file: {normalized_path}")
                return normalized_path
        
        print(f"❌ TrackConfig: Data file not found: {filename}")
        print(f"   Searched in: {possible_locations}")
        return None
        
    def load_all_tracks(self):
        """Load all track configurations from TXT files in data folder"""
        track_files = {
            "Green": "green_line.txt",
            "Red": "red_line.txt", 
            "Blue": "blue_line.txt"
        }
        
        for track_name, filename in track_files.items():
            file_path = self.get_data_file_path(filename)
            
            if file_path and os.path.exists(file_path):
                self.tracks[track_name] = self.load_track_from_txt(file_path)
            else:
                print(f"⚠️ TrackConfig: Could not find data file for {track_name} line")
                # Create empty track data as fallback
                self.tracks[track_name] = {
                    "suggested_speed": "0 mph",
                    "suggested_authority": "0 blocks", 
                    "commanded_speed": "0 mph",
                    "commanded_authority": "0 blocks",
                    "switches": {},
                    "lights": {},
                    "railway": {},
                    "blocks": []
                }
    
    def load_track_from_txt(self, file_path):
        """Load track configuration from TXT file - COMPLETELY DYNAMIC"""
        track_data = {
            "suggested_speed": "31 mph",  # Default fallback
            "suggested_authority": "10 blocks",  # Default fallback
            "commanded_speed": "31 mph",  # Default fallback
            "commanded_authority": "10 blocks",  # Default fallback
            "switches": {},
            "lights": {},
            "railway": {},
            "blocks": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # Skip header line if present
                for row_line in lines[1:]:
                    # split into at most 3 parts in case infrastructure contains additional commas
                    parts = row_line.strip().split(',', 2)
                    if len(parts) >= 2:
                        line_name = parts[0].strip()
                        block = parts[1].strip()
                        infrastructure = parts[2].strip() if len(parts) == 3 else ""
                        infra_upper = infrastructure.upper()
                        
                        # Add block to blocks list (store as string)
                        if block and block not in track_data["blocks"]:
                            track_data["blocks"].append(block)
                        
                        # Parse infrastructure dynamically
                        if 'SWITCH' in infra_upper:
                            # extract a list of switch options for this block
                            options = self.extract_switch_directions(infrastructure)
                            # Save as list of strings
                            track_data["switches"][block] = options
                        
                        # Note: file doesn't use the literal word "Light" in your example,
                        # but in case it does in other files, we support it.
                        if 'LIGHT' in infra_upper:
                            # store available colors (UI expects a list)
                            track_data["lights"][block] = ["Red", "Yellow", "Green"]
                        
                        if 'RAILWAY CROSSING' in infra_upper or 'RAILWAY' in infra_upper:
                            track_data["railway"][block] = ["Off", "On"]
                            
            print(f"✅ Loaded track data from: {file_path}")
            print(f"   Blocks: {len(track_data['blocks'])}")
            print(f"   Switches: {len(track_data['switches'])}")
            print(f"   Lights: {len(track_data['lights'])}")
            print(f"   Crossings: {len(track_data['railway'])}")
                            
        except FileNotFoundError:
            print(f"Warning: {file_path} not found. Track will be empty.")
            # Return empty track data instead of hardcoded defaults
            return {
                "suggested_speed": "0 mph",
                "suggested_authority": "0 blocks", 
                "commanded_speed": "0 mph",
                "commanded_authority": "0 blocks",
                "switches": {},
                "lights": {},
                "railway": {},
                "blocks": []
            }
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {
                "suggested_speed": "0 mph",
                "suggested_authority": "0 blocks", 
                "commanded_speed": "0 mph",
                "commanded_authority": "0 blocks",
                "switches": {},
                "lights": {},
                "railway": {},
                "blocks": []
            }
        
        return track_data

    def extract_switch_directions(self, infrastructure_text):
        """
        Extract switch direction(s) from an infrastructure description.
        Returns a list of option strings (ex: ["12-13", "1-13", "Normal"]).
        Heuristics:
          - If parentheses content exists, split by ';' or ',' inside them.
          - Otherwise, extract hyphenated pairs or tokens like 'TO YARD' / 'FROM YARD'.
        """
        if not infrastructure_text:
            return ["Normal"]
        
        infra = infrastructure_text.strip()
        # try to find parentheses content first
        paren_match = re.search(r'\((.*?)\)', infra)
        options = []
        if paren_match:
            inside = paren_match.group(1)
            # split on semicolon or comma separators
            raw_options = re.split(r'[;,]', inside)
            for opt in raw_options:
                opt_clean = opt.strip()
                if opt_clean:
                    # normalize whitespace and remove extraneous parentheses
                    options.append(opt_clean)
        
        # if none found in parentheses, try to find hyphenated pairs or yard keywords
        if not options:
            # capture patterns like 12-13, 150-28, 57-yard, Yard-63, etc.
            # also include 'TO YARD' or 'FROM YARD' tokens if present
            infra_upper = infra.upper()
            if 'TO YARD' in infra_upper:
                options.append("TO YARD")
            if 'FROM YARD' in infra_upper:
                options.append("FROM YARD")
            
            # regex to find hyphenated tokens with numbers and/or words (e.g. 12-13, 57-yard)
            found_pairs = re.findall(r'\b[\w]+\s*-\s*[\w]+\b', infra)
            for p in found_pairs:
                # normalize whitespace around hyphen
                p_norm = p.replace(' ', '')
                options.append(p_norm)
        
        # Final clean: remove duplicates while preserving order, strip whitespace
        seen = set()
        cleaned = []
        for o in options:
            o_s = o.strip()
            if o_s and o_s not in seen:
                seen.add(o_s)
                cleaned.append(o_s)
        
        # if nothing discovered, fallback to Normal
        if not cleaned:
            cleaned = ["Normal"]
        
        return cleaned

    def set_track_data(self, track_name, track_data):
        """Set track data programmatically"""
        self.tracks[track_name] = track_data
    
    def load_track_from_file(self, track_name, file_path):
        """Load track configuration from external file"""
        try:
            self.tracks[track_name] = self.load_track_from_txt(file_path)
            print(f"Loaded {track_name} track data from {file_path}")
        except Exception as e:
            print(f"Error loading track data: {e}")
    
    def get_switch_options(self, track_name, block_number):
        """Get switch options for a specific track and block"""
        switches = self.tracks.get(track_name, {}).get("switches", {})
        # block_number will usually be a string from the Combobox; use as-is
        options = switches.get(str(block_number), [])
        return options
    
    def get_light_options(self, track_name, block_number):
        """Get light color options for a specific track and block"""
        lights = self.tracks.get(track_name, {}).get("lights", {})
        return lights.get(str(block_number), ["Red", "Yellow", "Green"])
    
    def get_railway_options(self, track_name, block_number):
        """Get railway crossing options for a specific track and block"""
        railway = self.tracks.get(track_name, {}).get("railway", {})
        return railway.get(str(block_number), ["Off", "On"])
    
    def get_track_switches(self, track_name):
        return self.tracks.get(track_name, {}).get("switches", {})
    
    def get_track_lights(self, track_name):
        return self.tracks.get(track_name, {}).get("lights", {})
    
    def get_track_railway(self, track_name):
        return self.tracks.get(track_name, {}).get("railway", {})
    
    def get_available_blocks(self, track_name):
        """Get all available blocks for a track"""
        return self.tracks.get(track_name, {}).get("blocks", [])
    
    def get_blocks_with_switches(self, track_name):
        """Get only blocks that have switches"""
        switches = self.tracks.get(track_name, {}).get("switches", {})
        return list(switches.keys())
    
    def get_blocks_with_lights(self, track_name):
        """Get only blocks that have lights"""
        lights = self.tracks.get(track_name, {}).get("lights", {})
        return list(lights.keys())
    
    def get_blocks_with_crossings(self, track_name):
        """Get only blocks that have railway crossings"""
        railway = self.tracks.get(track_name, {}).get("railway", {})
        return list(railway.keys())
    
    def get_track_names(self):
        """Get all available track names"""
        return list(self.tracks.keys())