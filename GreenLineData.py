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

class BeaconData:
    def __init__(self, beacon_number, distance_to_next=None, forward_station_name=None, backward_station_name=None):
        self.block_number = beacon_number
        self.distance_to_next = distance_to_next
        self.forward_station_name = forward_station_name
        self.backward_station_name = backward_station_name


# Beacon 1: Glenbury (Block 60) to Dormont (Block 68)
# Distance: 50 + 100 + 100 + 100 + 100 + 100 + 100 + 50 = 800m
# Midpoint distance: 400m from each station
# Beacon placed at: Block 64 (midpoint between blocks)
glenburyToDormont = BeaconData(
    beacon_number=64,
    distance_to_next=400.0,
    forward_station_name="Dormont",
    backward_station_name="Glenbury"
)

# Beacon 2: Dormont (Block 68) to MT Lebanon (Block 71)
# Distance: 50 + 100 + 100 + 50 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 70 (midpoint between blocks)
dormountToMTLebanon = BeaconData(
    beacon_number=70,
    distance_to_next=150.0,
    forward_station_name="MT Lebanon",
    backward_station_name="Dormont"
)

# Beacon 3: MT Lebanon (Block 71) to Poplar (Block 79)
# Distance: 50 + 200 + 300 + 300 + 300 + 200 + 100 + 50 = 1500m
# Midpoint distance: 750m from each station
# Beacon placed at: Block 75 (midpoint between blocks)
mtLebanoToPoplar = BeaconData(
    beacon_number=75,
    distance_to_next=750.0,
    forward_station_name="Poplar",
    backward_station_name="MT Lebanon"
)

# Beacon 4: Poplar (Block 79) to Castle Shannon (Block 85)
# Distance: 50 + 75 + 75 + 75 + 75 + 75 + 50 = 475m
# Midpoint distance: 237.5m from each station
# Beacon placed at: Block 82 (midpoint between blocks)
poplarToCastleShannon = BeaconData(
    beacon_number=82,
    distance_to_next=237.5,
    forward_station_name="Castle Shannon",
    backward_station_name="Poplar"
)

# Beacon 5: Castle Shannon (Block 85) to MT Lebanon (Block 71)
# Distance: 50 + 75 + 75 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 50 = 1150m
# Midpoint distance: 575m from each station
# Beacon placed at: Block 78 (midpoint between blocks)
castleShannonToMTLebanon = BeaconData(
    beacon_number=78,
    distance_to_next=575.0,
    forward_station_name="MT Lebanon",
    backward_station_name="Castle Shannon"
)

# Beacon 6: MT Lebanon (Block 71) to Dormont (Block 96)
# Distance: 50 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 80 + 50 = 1180m
# Midpoint distance: 590m from each station
# Beacon placed at: Block 83 (midpoint between blocks)
mtLebanonToDormount2 = BeaconData(
    beacon_number=83,
    distance_to_next=590.0,
    forward_station_name="Dormont",
    backward_station_name="MT Lebanon"
)

# Beacon 7: Dormont (Block 96) to Glenbury (Block 101)
# Distance: 50 + 100 + 100 + 100 + 100 + 50 = 500m
# Midpoint distance: 250m from each station
# Beacon placed at: Block 98 (midpoint between blocks)
dormountToGlenbury = BeaconData(
    beacon_number=98,
    distance_to_next=250.0,
    forward_station_name="Glenbury",
    backward_station_name="Dormont"
)

# Beacon 8: Glenbury (Block 101) to Overbrook (Block 122)
# Distance: 50 + 100 + 100 + 100 + 100 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 = 1300m
# Midpoint distance: 650m from each station
# Beacon placed at: Block 111 (midpoint between blocks)
glenburyToOverbrook = BeaconData(
    beacon_number=111,
    distance_to_next=650.0,
    forward_station_name="Overbrook",
    backward_station_name="Glenbury"
)

# Beacon 9: Overbrook (Block 122) to Inglewood (Block 132)
# Distance: 25 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 25 = 500m
# Midpoint distance: 250m from each station
# Beacon placed at: Block 127 (midpoint between blocks)
overbrookToInglewood = BeaconData(
    beacon_number=127,
    distance_to_next=250.0,
    forward_station_name="Inglewood",
    backward_station_name="Overbrook"
)

# Beacon 10: Inglewood (Block 132) to Central (Block 140)
# Distance: 25 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 25 = 400m
# Midpoint distance: 200m from each station
# Beacon placed at: Block 136 (midpoint between blocks)
inglewoodToCentral = BeaconData(
    beacon_number=136,
    distance_to_next=200.0,
    forward_station_name="Central",
    backward_station_name="Inglewood"
)

# Beacon 11: Central (Block 140) to Whited (Block 16)
# Distance: 25 + 50*54 + 75 + 25 = 5325m
# Midpoint distance: 2662.5m from each station
# Beacon placed at: Block 78 (midpoint between blocks)
centralToWhited = BeaconData(
    beacon_number=78,
    distance_to_next=2662.5,
    forward_station_name="Whited",
    backward_station_name="Central"
)

# Beacon 12: Whited (Block 16) to LLC (Block 13)
# Distance: 75 + 150 + 75 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 14 (midpoint between blocks)
whitedToLLC = BeaconData(
    beacon_number=14,
    distance_to_next=150.0,
    forward_station_name="LLC",
    backward_station_name="Whited"
)

# Beacon 13: LLC (Block 13) to Edgebrook (Block 7)
# Distance: 75 + 100 + 100 + 100 + 100 + 75 = 550m
# Midpoint distance: 275m from each station
# Beacon placed at: Block 10 (midpoint between blocks)
llcToEdgebrook = BeaconData(
    beacon_number=10,
    distance_to_next=275.0,
    forward_station_name="Edgebrook",
    backward_station_name="LLC"
)

# Beacon 14: Edgebrook (Block 7) to Pioneer (Block 1)
# Distance: 50 + 100 + 100 + 100 + 100 + 50 = 500m
# Midpoint distance: 250m from each station
# Beacon placed at: Block 4 (midpoint between blocks)
edgebrookToPioneer = BeaconData(
    beacon_number=4,
    distance_to_next=250.0,
    forward_station_name="Pioneer",
    backward_station_name="Edgebrook"
)

# Beacon 15: Pioneer (Block 1) to LLC (Block 13)
# Distance: 50 + 100 + 100 + 100 + 100 + 75 + 150 + 75 = 750m
# Midpoint distance: 375m from each station
# Beacon placed at: Block 7 (midpoint between blocks)
pioneerToLLC = BeaconData(
    beacon_number=7,
    distance_to_next=375.0,
    forward_station_name="LLC",
    backward_station_name="Pioneer"
)

# Beacon 16: LLC (Block 13) to Whited (Block 16)
# Distance: 75 + 150 + 75 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 14 (midpoint between blocks)
llcToWhited = BeaconData(
    beacon_number=14,
    distance_to_next=150.0,
    forward_station_name="Whited",
    backward_station_name="LLC"
)

# Beacon 17: Whited (Block 16) to South Bank (Block 25)
# Distance: 75 + 50 + 50 + 50 + 50 + 50 + 50 + 75 = 400m
# Midpoint distance: 200m from each station
# Beacon placed at: Block 20 (midpoint between blocks)
whitedToSouthBank = BeaconData(
    beacon_number=20,
    distance_to_next=200.0,
    forward_station_name="South Bank",
    backward_station_name="Whited"
)

# Beacon 18: South Bank (Block 25) to Central (Block 31)
# Distance: 25 + 50 + 50 + 50 + 50 + 50 + 25 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 28 (midpoint between blocks)
southBankToCentral = BeaconData(
    beacon_number=28,
    distance_to_next=150.0,
    forward_station_name="Central",
    backward_station_name="South Bank"
)

# Create list of all beacons
beacons = [
    glenburyToDormont,
    dormountToMTLebanon,
    mtLebanoToPoplar,
    poplarToCastleShannon,
    castleShannonToMTLebanon,
    mtLebanonToDormount2,
    dormountToGlenbury,
    glenburyToOverbrook,
    overbrookToInglewood,
    inglewoodToCentral,
    centralToWhited,
    whitedToLLC,
    llcToEdgebrook,
    edgebrookToPioneer,
    pioneerToLLC,
    llcToWhited,
    whitedToSouthBank,
    southBankToCentral,
]

# Display beacon data
print("Green Line Beacon Midpoints\n" + "="*120)
print(f"{'Beacon':<10} {'Block':<8} {'Distance to Station (m)':<25} {'Backward Station':<20} {'→':<3} {'Forward Station':<20}")
print("="*120)
for idx, beacon in enumerate(beacons, 1):
    print(f"{idx:<10} {beacon.block_number:<8} {beacon.distance_to_next:<25.1f} {beacon.backward_station_name:<20} {'→':<3} {beacon.forward_station_name:<20}")

print("="*120)
print(f"Total Beacons: {len(beacons)}")