class RedLine:
    def __init__(self):
        self.blocks = [
            {"blockNumber": 1, "section": "A", "blockLengthM": 50, "blockGradePercent": 0.5, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.25, "cumulativeElevationM": 0.25},
            {"blockNumber": 2, "section": "A", "blockLengthM": 50, "blockGradePercent": 1.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.50, "cumulativeElevationM": 0.75},
            {"blockNumber": 3, "section": "A", "blockLengthM": 50, "blockGradePercent": 1.5, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.75, "cumulativeElevationM": 1.50},
            {"blockNumber": 4, "section": "B", "blockLengthM": 50, "blockGradePercent": 2.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 1.00, "cumulativeElevationM": 2.50},
            {"blockNumber": 5, "section": "B", "blockLengthM": 50, "blockGradePercent": 1.5, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.75, "cumulativeElevationM": 3.25},
            {"blockNumber": 6, "section": "B", "blockLengthM": 50, "blockGradePercent": 1.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.50, "cumulativeElevationM": 3.75},
            {"blockNumber": 7, "section": "C", "blockLengthM": 75, "blockGradePercent": 0.5, "speedLimitKmh": 40, "infrastructure": "STATION: SHADYSIDE", "stationSide": "Left/Right", "elevationM": 0.375, "cumulativeElevationM": 4.125},
            {"blockNumber": 8, "section": "C", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": 4.125},
            {"blockNumber": 9, "section": "C", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 40, "infrastructure": "SWITCH TO/FROM YARD (75-yard)", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": 4.125},
            {"blockNumber": 10, "section": "D", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": 4.125},
            {"blockNumber": 11, "section": "D", "blockLengthM": 75, "blockGradePercent": -0.5, "speedLimitKmh": 40, "infrastructure": "RAILWAY CROSSING", "stationSide": "", "elevationM": -0.375, "cumulativeElevationM": 3.75},
            {"blockNumber": 12, "section": "D", "blockLengthM": 75, "blockGradePercent": -1.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": -0.75, "cumulativeElevationM": 3.00},
            {"blockNumber": 13, "section": "E", "blockLengthM": 70, "blockGradePercent": -2.0, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": -1.40, "cumulativeElevationM": 1.60},
            {"blockNumber": 14, "section": "E", "blockLengthM": 60, "blockGradePercent": -1.25, "speedLimitKmh": 40, "infrastructure": "", "stationSide": "", "elevationM": -0.75, "cumulativeElevationM": 0.85},
            {"blockNumber": 15, "section": "E", "blockLengthM": 60, "blockGradePercent": -1.0, "speedLimitKmh": 40, "infrastructure": "SWITCH (15-16; 1-16)", "stationSide": "", "elevationM": -0.60, "cumulativeElevationM": 0.25},
            {"blockNumber": 16, "section": "F", "blockLengthM": 50, "blockGradePercent": -0.5, "speedLimitKmh": 40, "infrastructure": "STATION: HERRON AVE", "stationSide": "Left/Right", "elevationM": -0.25, "cumulativeElevationM": 0.00},
            {"blockNumber": 17, "section": "F", "blockLengthM": 200, "blockGradePercent": -0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": -1.00, "cumulativeElevationM": -1.00},
            {"blockNumber": 18, "section": "F", "blockLengthM": 400, "blockGradePercent": -0.06025, "speedLimitKmh": 70, "infrastructure": "", "stationSide": "", "elevationM": -0.241, "cumulativeElevationM": -1.241},
            {"blockNumber": 19, "section": "F", "blockLengthM": 400, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 20, "section": "F", "blockLengthM": 200, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 21, "section": "G", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "STATION; SWISSVILLE", "stationSide": "Left/Right", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 22, "section": "G", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 23, "section": "G", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 24, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 25, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "STATION; PENN STATION; UNDERGROUND", "stationSide": "Left/Right", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 26, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 27, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "SWITCH (27-28; 27-76); UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 28, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 29, "section": "H", "blockLengthM": 60, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 30, "section": "H", "blockLengthM": 60, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 31, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 32, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "SWITCH (32-33; 33-72); UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 33, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 34, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 35, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "STATION; STEEL PLAZA; UNDERGROUND", "stationSide": "Left/Right", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 36, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 37, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 38, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "SWITCH (38-39; 38-71); UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 39, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 40, "section": "H", "blockLengthM": 60, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 41, "section": "H", "blockLengthM": 60, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 42, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 43, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "SWITCH (43-44; 44-67); UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 44, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 45, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "STATION; FIRST AVE; UNDERGROUND", "stationSide": "Left/Right", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 46, "section": "I", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 47, "section": "I", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "RAILWAY CROSSING", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 48, "section": "I", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 70, "infrastructure": "STATION; STATION SQUARE", "stationSide": "Left/Right", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 49, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 60, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 50, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 60, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 51, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 52, "section": "J", "blockLengthM": 43.2, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "SWITCH (52-53; 52-66)", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 53, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 54, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 55, "section": "K", "blockLengthM": 75, "blockGradePercent": 0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.375, "cumulativeElevationM": -0.866},
            {"blockNumber": 56, "section": "K", "blockLengthM": 75, "blockGradePercent": 0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.375, "cumulativeElevationM": -0.491},
            {"blockNumber": 57, "section": "K", "blockLengthM": 75, "blockGradePercent": 0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.375, "cumulativeElevationM": -0.116},
            {"blockNumber": 58, "section": "L", "blockLengthM": 75, "blockGradePercent": 1.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.75, "cumulativeElevationM": 0.634},
            {"blockNumber": 59, "section": "L", "blockLengthM": 75, "blockGradePercent": 0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.375, "cumulativeElevationM": 1.009},
            {"blockNumber": 60, "section": "L", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "STATION; SOUTH HILLS JUNCTION", "stationSide": "Left/Right", "elevationM": 0.00, "cumulativeElevationM": 1.009},
            {"blockNumber": 61, "section": "M", "blockLengthM": 75, "blockGradePercent": -0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": -0.375, "cumulativeElevationM": 0.634},
            {"blockNumber": 62, "section": "M", "blockLengthM": 75, "blockGradePercent": -1.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": -0.75, "cumulativeElevationM": -0.116},
            {"blockNumber": 63, "section": "M", "blockLengthM": 75, "blockGradePercent": -1.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": -0.75, "cumulativeElevationM": -0.866},
            {"blockNumber": 64, "section": "N", "blockLengthM": 75, "blockGradePercent": -0.5, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": -0.375, "cumulativeElevationM": -1.241},
            {"blockNumber": 65, "section": "N", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 66, "section": "N", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 67, "section": "O", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 68, "section": "P", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 69, "section": "P", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 70, "section": "P", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 71, "section": "Q", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 72, "section": "R", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 73, "section": "S", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 74, "section": "S", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 75, "section": "S", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
            {"blockNumber": 76, "section": "T", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimitKmh": 55, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.00, "cumulativeElevationM": -1.241},
        ]

    def getValue(self, blockNumber, key):
        """
        Get a value from a specific block.
        
        Args:
            blockNumber (int): The block number (1-76)
            key (str): The field name to retrieve. Options:
                - 'section'
                - 'blockLengthM'
                - 'blockGradePercent'
                - 'speedLimitKmh'
                - 'infrastructure'
                - 'stationSide'
                - 'elevationM'
                - 'cumulativeElevationM'
        
        Returns:
            The value of the requested field, or None if not found
        """
        for block in self.blocks:
            if block['blockNumber'] == blockNumber:
                return block.get(key)
        return None

    def getBlock(self, blockNumber):
        """Get all data for a specific block."""
        for block in self.blocks:
            if block['blockNumber'] == blockNumber:
                return block
        return None


# Example usage:
if __name__ == "__main__":
    red_line = RedLine()