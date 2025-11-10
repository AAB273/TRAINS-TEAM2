class RedLine:
    def __init__(self):
        self.blocks = [
            {"block_number": 1, "section": "A", "block_length_m": 50, "block_grade_percent": 0.5, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.25, "cumulative_elevation_m": 0.25},
            {"block_number": 2, "section": "A", "block_length_m": 50, "block_grade_percent": 1, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.50, "cumulative_elevation_m": 0.75},
            {"block_number": 3, "section": "A", "block_length_m": 50, "block_grade_percent": 1.5, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.75, "cumulative_elevation_m": 1.50},
            {"block_number": 4, "section": "B", "block_length_m": 50, "block_grade_percent": 2, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 1.00, "cumulative_elevation_m": 2.50},
            {"block_number": 5, "section": "B", "block_length_m": 50, "block_grade_percent": 1.5, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.75, "cumulative_elevation_m": 3.25},
            {"block_number": 6, "section": "B", "block_length_m": 50, "block_grade_percent": 1, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.50, "cumulative_elevation_m": 3.75},
            {"block_number": 7, "section": "C", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit_kmh": 40, "infrastructure": "STATION: SHADYSIDE", "station_side": "Left/Right", "elevation_m": 0.38, "cumulative_elevation_m": 4.13},
            {"block_number": 8, "section": "C", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": 4.13},
            {"block_number": 9, "section": "C", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 40, "infrastructure": "SWITCH TO/FROM YARD (75-yard)", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": 4.13},
            {"block_number": 10, "section": "D", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": 4.13},
            {"block_number": 11, "section": "D", "block_length_m": 75, "block_grade_percent": -0.5, "speed_limit_kmh": 40, "infrastructure": "RAILWAY CROSSING", "station_side": "", "elevation_m": -0.38, "cumulative_elevation_m": 3.75},
            {"block_number": 12, "section": "D", "block_length_m": 75, "block_grade_percent": -1, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": -0.75, "cumulative_elevation_m": 3.00},
            {"block_number": 13, "section": "E", "block_length_m": 70, "block_grade_percent": -2, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": -1.40, "cumulative_elevation_m": 1.60},
            {"block_number": 14, "section": "E", "block_length_m": 60, "block_grade_percent": -1.25, "speed_limit_kmh": 40, "infrastructure": "", "station_side": "", "elevation_m": -0.75, "cumulative_elevation_m": 0.85},
            {"block_number": 15, "section": "E", "block_length_m": 60, "block_grade_percent": -1, "speed_limit_kmh": 40, "infrastructure": "SWITCH (15-16; 1-16)", "station_side": "", "elevation_m": -0.60, "cumulative_elevation_m": 0.25},
            {"block_number": 16, "section": "F", "block_length_m": 50, "block_grade_percent": -0.5, "speed_limit_kmh": 40, "infrastructure": "STATION: HERRON AVE", "station_side": "Left/Right", "elevation_m": -0.25, "cumulative_elevation_m": 0.00},
            {"block_number": 17, "section": "F", "block_length_m": 200, "block_grade_percent": -0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": -1.00, "cumulative_elevation_m": -1.00},
            {"block_number": 18, "section": "F", "block_length_m": 400, "block_grade_percent": -0.06025, "speed_limit_kmh": 70, "infrastructure": "", "station_side": "", "elevation_m": -0.24, "cumulative_elevation_m": -1.24},
            {"block_number": 19, "section": "F", "block_length_m": 400, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 20, "section": "F", "block_length_m": 200, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 21, "section": "G", "block_length_m": 100, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "STATION; SWISSVILLE", "station_side": "Left/Right", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 22, "section": "G", "block_length_m": 100, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 23, "section": "G", "block_length_m": 100, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 24, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 25, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "STATION; PENN STATION; UNDERGROUND", "station_side": "Left/Right", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 26, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 27, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "SWITCH (27-28; 27-76); UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 28, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 29, "section": "H", "block_length_m": 60, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 30, "section": "H", "block_length_m": 60, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 31, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 32, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "SWITCH (32-33; 33-72); UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 33, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 34, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 35, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "STATION; STEEL PLAZA; UNDERGROUND", "station_side": "Left/Right", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 36, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 37, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 38, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "SWITCH (38-39; 38-71); UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 39, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 40, "section": "H", "block_length_m": 60, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 41, "section": "H", "block_length_m": 60, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 42, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 43, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "SWITCH (43-44; 44-67); UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 44, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 45, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "STATION; FIRST AVE; UNDERGROUND", "station_side": "Left/Right", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 46, "section": "I", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 47, "section": "I", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "RAILWAY CROSSING", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 48, "section": "I", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 70, "infrastructure": "STATION; STATION SQUARE", "station_side": "Left/Right", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 49, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 60, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 50, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 60, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 51, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 52, "section": "J", "block_length_m": 43.2, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "SWITCH (52-53; 52-66)", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 53, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 54, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 55, "section": "K", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.38, "cumulative_elevation_m": -0.87},
            {"block_number": 56, "section": "K", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.38, "cumulative_elevation_m": -0.49},
            {"block_number": 57, "section": "K", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.38, "cumulative_elevation_m": -0.12},
            {"block_number": 58, "section": "L", "block_length_m": 75, "block_grade_percent": 1, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.75, "cumulative_elevation_m": 0.63},
            {"block_number": 59, "section": "L", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.38, "cumulative_elevation_m": 1.01},
            {"block_number": 60, "section": "L", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "STATION; SOUTH HILLS JUNCTION", "station_side": "Left/Right", "elevation_m": 0.00, "cumulative_elevation_m": 1.01},
            {"block_number": 61, "section": "M", "block_length_m": 75, "block_grade_percent": -0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": -0.38, "cumulative_elevation_m": 0.63},
            {"block_number": 62, "section": "M", "block_length_m": 75, "block_grade_percent": -1, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": -0.75, "cumulative_elevation_m": -0.12},
            {"block_number": 63, "section": "M", "block_length_m": 75, "block_grade_percent": -1, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": -0.75, "cumulative_elevation_m": -0.87},
            {"block_number": 64, "section": "N", "block_length_m": 75, "block_grade_percent": -0.5, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": -0.38, "cumulative_elevation_m": -1.24},
            {"block_number": 65, "section": "N", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 66, "section": "N", "block_length_m": 75, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 67, "section": "O", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 68, "section": "P", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 69, "section": "P", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 70, "section": "P", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 71, "section": "Q", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 72, "section": "R", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 73, "section": "S", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 74, "section": "S", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 75, "section": "S", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
            {"block_number": 76, "section": "S", "block_length_m": 50, "block_grade_percent": 0, "speed_limit_kmh": 55, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0.00, "cumulative_elevation_m": -1.24},
        ]

    def get_value(self, block_number, key):
        """
        Get a value from a specific block.
        
        Args:
            block_number (int): The block number (1-76)
            key (str): The field name to retrieve. Options:
                - 'section'
                - 'block_length_m'
                - 'block_grade_percent'
                - 'speed_limit_kmh'
                - 'infrastructure'
                - 'station_side'
                - 'elevation_m'
                - 'cumulative_elevation_m'
        
        Returns:
            The value of the requested field, or None if not found
        """
        for block in self.blocks:
            if block['block_number'] == block_number:
                return block.get(key)
        return None

    def get_block(self, block_number):
        """Get all data for a specific block."""
        for block in self.blocks:
            if block['block_number'] == block_number:
                return block
        return None


# Example usage:
if __name__ == "__main__":
    red_line = RedLine()
    
    # Get specific values
    print(f"Block 7 Infrastructure: {red_line.get_value(7, 'infrastructure')}")
    print(f"Block 7 Station Side: {red_line.get_value(7, 'station_side')}")
    print(f"Block 25 Infrastructure: {red_line.get_value(25, 'infrastructure')}")
    print(f"Block 35 Speed Limit: {red_line.get_value(35, 'speed_limit_kmh')} km/h")
    
    # Get entire block
    print(f"\nBlock 48 Info: {red_line.get_block(48)}")