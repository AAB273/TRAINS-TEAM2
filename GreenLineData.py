from BeaconData import BeaconData

class GreenLine:
    def __init__(self):
        self.blocks = [
            {"block_number": 1, "section": "A", "block_length_m": 100, "block_grade_percent": 0.5, "speed_limit": 45, "infrastructure": "STATION; PIONEER", "station_side": "Left", "elevation_m": 0.5, "cumulative_elevation_m": 8.0},
            {"block_number": 2, "section": "A", "block_length_m": 100, "block_grade_percent": 1, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 1, "cumulative_elevation_m": 9.0},
            {"block_number": 3, "section": "A", "block_length_m": 100, "block_grade_percent": 1.5, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 1.5, "cumulative_elevation_m": 10.5},
            {"block_number": 4, "section": "B", "block_length_m": 100, "block_grade_percent": 2, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 2, "cumulative_elevation_m": 12.5},
            {"block_number": 5, "section": "B", "block_length_m": 100, "block_grade_percent": 1.5, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 1.5, "cumulative_elevation_m": 14.0},
            {"block_number": 6, "section": "B", "block_length_m": 100, "block_grade_percent": 1, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 1, "cumulative_elevation_m": 15.0},
            {"block_number": 7, "section": "C", "block_length_m": 100, "block_grade_percent": 0.5, "speed_limit": 45, "infrastructure": "STATION; EDGEBROOK", "station_side": "Left", "elevation_m": 0.5, "cumulative_elevation_m": 15.5},
            {"block_number": 8, "section": "C", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 15.5},
            {"block_number": 9, "section": "C", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 45, "infrastructure": "SWITCH (12-13; 1-13)", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 15.5},
            {"block_number": 10, "section": "C", "block_length_m": 100, "block_grade_percent": 4.5, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 4.5, "cumulative_elevation_m": 20.0},
            {"block_number": 11, "section": "D", "block_length_m": 100, "block_grade_percent": 4.5, "speed_limit": 45, "infrastructure": "", "station_side": "", "elevation_m": 4.5, "cumulative_elevation_m": 24.5},
            {"block_number": 12, "section": "D", "block_length_m": 150, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 13, "section": "D", "block_length_m": 150, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "STATION", "station_side": "Left/Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 14, "section": "D", "block_length_m": 150, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 15, "section": "E", "block_length_m": 150, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "RAILWAY CROSSING", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 16, "section": "E", "block_length_m": 150, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "STATION; WAITES", "station_side": "Left/Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 17, "section": "F", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 18, "section": "F", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 19, "section": "F", "block_length_m": 150, "block_grade_percent": 0, "speed_limit": 60, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 20, "section": "F", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 21, "section": "F", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 22, "section": "F", "block_length_m": 200, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 23, "section": "F", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "SWITCH (28-29; 150-28)", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 24, "section": "G", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 25, "section": "G", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "STATION; SOUTH BANK", "station_side": "Left", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 26, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 27, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 28, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 29, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 30, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 31, "section": "H", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "STATION; CENTRAL; UNDERGROUND", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 32, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 33, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 34, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 35, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 36, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 37, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 38, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 39, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 40, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 41, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 42, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 43, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 44, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 45, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "STATION; DOWNTOWN; RIGHT", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 46, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 47, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 48, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 49, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 50, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 51, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 52, "section": "I", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 53, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "UNDERGROUND; STATION", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 54, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "SWITCH TO YARD (52 yards)", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 55, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 56, "section": "J", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 57, "section": "J", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 58, "section": "K", "block_length_m": 200, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "SWITCH (FROM YARD) (Yard 63)", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 59, "section": "K", "block_length_m": 200, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 60, "section": "K", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "STATION; GLENBURY", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 61, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 62, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 63, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 64, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 65, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 66, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 67, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 68, "section": "L", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "STATION; DORMONT", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 69, "section": "M", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 70, "section": "M", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "SWITCH (26-27; 27-101)", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 71, "section": "M", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 40, "infrastructure": "STATION; MT LEBANON", "station_side": "Left/Right", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 72, "section": "N", "block_length_m": 200, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 73, "section": "N", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 74, "section": "N", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 75, "section": "N", "block_length_m": 300, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 76, "section": "N", "block_length_m": 200, "block_grade_percent": 0, "speed_limit": 70, "infrastructure": "SWITCH (85-86; 100-85)", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 77, "section": "O", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 78, "section": "O", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 79, "section": "O", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "STATION; POPLAR", "station_side": "Left", "elevation_m": 0, "cumulative_elevation_m": 24.5},
            {"block_number": 80, "section": "P", "block_length_m": 75, "block_grade_percent": -0.5, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": -0.375, "cumulative_elevation_m": 10.8},
            {"block_number": 81, "section": "P", "block_length_m": 75, "block_grade_percent": -0.5, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": -0.375, "cumulative_elevation_m": 10.8},
            {"block_number": 82, "section": "P", "block_length_m": 75, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 83, "section": "P", "block_length_m": 75, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 84, "section": "P", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0.375, "cumulative_elevation_m": 10.8},
            {"block_number": 85, "section": "P", "block_length_m": 75, "block_grade_percent": 0.5, "speed_limit": 25, "infrastructure": "STATION; CASTLE SHANNON", "station_side": "Left", "elevation_m": 0.375, "cumulative_elevation_m": 10.8},
            {"block_number": 86, "section": "Q", "block_length_m": 75, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 87, "section": "Q", "block_length_m": 75, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 88, "section": "Q", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 89, "section": "R", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 90, "section": "R", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 91, "section": "R", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 92, "section": "R", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 25, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 93, "section": "S", "block_length_m": 80, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 94, "section": "S", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 95, "section": "S", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 96, "section": "S", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "STATION; DORMONT", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 97, "section": "T", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 98, "section": "T", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 99, "section": "T", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "RAILWAY CROSSING", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 100, "section": "T", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 101, "section": "U", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "STATION; GLENBURY", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 102, "section": "U", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 103, "section": "U", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 104, "section": "U", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 105, "section": "U", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 30, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 106, "section": "V", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 107, "section": "V", "block_length_m": 100, "block_grade_percent": 0, "speed_limit": 28, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 108, "section": "V", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 15, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 109, "section": "V", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 15, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 110, "section": "V", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 15, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 111, "section": "V", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 15, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 112, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 113, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 114, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 115, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 116, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 117, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 118, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 119, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 120, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 121, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 122, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "STATION; OVERBROOK; UNDERGROUND", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 123, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 124, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 125, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 126, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 127, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 128, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 129, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 130, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 131, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 132, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "Left", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 133, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 134, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 135, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 136, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 137, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 138, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 139, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 140, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "STATION; CENTRAL; UNDERGROUND", "station_side": "Right", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 141, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 142, "section": "W", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 143, "section": "X", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 144, "section": "X", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 145, "section": "X", "block_length_m": 50, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
            {"block_number": 146, "section": "X", "block_length_m": 164, "block_grade_percent": 0, "speed_limit": 20, "infrastructure": "UNDERGROUND", "station_side": "", "elevation_m": 0, "cumulative_elevation_m": 10.8},
        ]
    YardToGlenbury1 = BeaconData(64, 2000, "Glenbury")
    Glenbury1ToDormont1 = BeaconData(102, 800, "Dormont")
    Dormont1ToMtLebanon = BeaconData(97, 700, "Mt Lebanon")
    MtLebanonToPoplar = BeaconData(72, 600, "Poplar")
    PoplarToCastleShannon = BeaconData(80, 500, "Castle Shannon")
    def get_value(self, block_number, key):
        """
        Get a value from a specific block.
        
        Args:
            block_number (int): The block number (1-146)
            key (str): The field name to retrieve. Options:
                - 'section'
                - 'block_length_m'
                - 'block_grade_percent'
                - 'speed_limit'
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

