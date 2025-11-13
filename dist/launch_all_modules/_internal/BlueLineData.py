class BlueLine:
    def __init__(self):
        self.blocks = [
            {
                "block_number": 1,
                "section": "A",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 2,
                "section": "A",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 3,
                "section": "A",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "RAILWAY CROSSING",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 4,
                "section": "A",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 5,
                "section": "A",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Switch (5 to 6) or (5 to 11)",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 6,
                "section": "B",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Switch (5 to 6); Light",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 7,
                "section": "B",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 8,
                "section": "B",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 9,
                "section": "B",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Transponder",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 10,
                "section": "B",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Station B",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 11,
                "section": "C",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Switch (5 to 11); Light",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 12,
                "section": "C",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 13,
                "section": "C",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 14,
                "section": "C",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Transponder",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            },
            {
                "block_number": 15,
                "section": "C",
                "block_length_m": 50,
                "block_grade_percent": 0,
                "speed_limit_kmh": 50,
                "infrastructure": "Station C",
                "elevation_m": 0.00,
                "cumulative_elevation_m": 0.00
            }
        ]

    def get_value(self, block_number, key):
        """
        Get a value from a specific block.
        
        Args:
            block_number (int): The block number (1-15)
            key (str): The field name to retrieve. Options:
                - 'section'
                - 'block_length_m'
                - 'block_grade_percent'
                - 'speed_limit_kmh'
                - 'infrastructure'
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
    blue_line = BlueLine()
    
    # Get specific values
    print(f"Block 3 Speed Limit: {blue_line.get_value(3, 'speed_limit_kmh')} km/h")
    print(f"Block 3 Infrastructure: {blue_line.get_value(3, 'infrastructure')}")
    print(f"Block 10 Section: {blue_line.get_value(10, 'section')}")
    
    # Get entire block
    print(f"\nBlock 15 Info: {blue_line.get_block(15)}")