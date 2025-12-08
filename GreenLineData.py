class GreenLine:
    def __init__(self):
        self.blocks = [
            {"blockNumber": 1, "section": "A", "blockLengthM": 100, "blockGradePercent": 0.5, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 0.5, "cumulativeElevationM": 0.5},
            {"blockNumber": 2, "section": "A", "blockLengthM": 100, "blockGradePercent": 1.0, "speedLimit": 45, "infrastructure": "STATION; PIONEER", "stationSide": "Left", "elevationM": 1.0, "cumulativeElevationM": 1.5},
            {"blockNumber": 3, "section": "A", "blockLengthM": 100, "blockGradePercent": 1.5, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 1.5, "cumulativeElevationM": 3.0},
            {"blockNumber": 4, "section": "B", "blockLengthM": 100, "blockGradePercent": 2.0, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 2.0, "cumulativeElevationM": 5.0},
            {"blockNumber": 5, "section": "B", "blockLengthM": 100, "blockGradePercent": 3.0, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 3.0, "cumulativeElevationM": 8.0},
            {"blockNumber": 6, "section": "B", "blockLengthM": 100, "blockGradePercent": 4.0, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 4.0, "cumulativeElevationM": 12.0},
            {"blockNumber": 7, "section": "C", "blockLengthM": 100, "blockGradePercent": 5.0, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 5.0, "cumulativeElevationM": 17.0},
            {"blockNumber": 8, "section": "C", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 17.0},
            {"blockNumber": 9, "section": "C", "blockLengthM": 100, "blockGradePercent": -5.0, "speedLimit": 45, "infrastructure": "STATION; EDGEBROOK", "stationSide": "Left", "elevationM": -5.0, "cumulativeElevationM": 12.0},
            {"blockNumber": 10, "section": "C", "blockLengthM": 100, "blockGradePercent": -4.5, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": -4.5, "cumulativeElevationM": 7.5},
            {"blockNumber": 11, "section": "C", "blockLengthM": 100, "blockGradePercent": -4.0, "speedLimit": 45, "infrastructure": "", "stationSide": "", "elevationM": -4.0, "cumulativeElevationM": 3.5},
            {"blockNumber": 12, "section": "C", "blockLengthM": 100, "blockGradePercent": -3.0, "speedLimit": 45, "infrastructure": "SWITCH (12-13; 1-13)", "stationSide": "", "elevationM": -3.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 13, "section": "D", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 14, "section": "D", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 15, "section": "D", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 16, "section": "D", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "STATION; LLC", "stationSide": "Left/Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 17, "section": "E", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 60, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 18, "section": "E", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 60, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 19, "section": "E", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 60, "infrastructure": "RAILWAY CROSSING", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 20, "section": "E", "blockLengthM": 150, "blockGradePercent": 0.0, "speedLimit": 60, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 21, "section": "F", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 22, "section": "F", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "STATION; WHITED", "stationSide": "Left/Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 23, "section": "F", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 24, "section": "F", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 25, "section": "F", "blockLengthM": 200, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 26, "section": "F", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 27, "section": "F", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 28, "section": "F", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "SWITCH (28-29; 150-28)", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 29, "section": "G", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 30, "section": "G", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 31, "section": "G", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "STATION; SOUTH BANK", "stationSide": "Left", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 32, "section": "G", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 33, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 34, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 35, "section": "H", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 36, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 37, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 38, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 39, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "STATION; CENTRAL; UNDERGROUND", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 40, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 41, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 42, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 43, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 44, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 45, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 46, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 47, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 48, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "STATION; INGLEWOOD; UNDERGROUND", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 49, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 50, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 51, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 52, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 53, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 54, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 55, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 56, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 57, "section": "I", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "STATION; OVERBROOK; UNDERGROUND", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 58, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "SWITCH TO YARD (57-yard)", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 59, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 60, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 61, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 62, "section": "J", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "SWITCH FROM YARD (Yard-63)", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 63, "section": "K", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 64, "section": "K", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 65, "section": "K", "blockLengthM": 200, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "STATION; GLENBURY", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 66, "section": "K", "blockLengthM": 200, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 67, "section": "K", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 68, "section": "K", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 69, "section": "L", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 70, "section": "L", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 71, "section": "L", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 72, "section": "L", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 73, "section": "L", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "STATION; DORMONT", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 74, "section": "M", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 75, "section": "M", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 76, "section": "M", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 40, "infrastructure": "SWITCH (76-77;77-101)", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 77, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "STATION; MT LEBANON", "stationSide": "Left/Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 78, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 79, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 80, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 81, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 82, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 83, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 84, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 85, "section": "N", "blockLengthM": 300, "blockGradePercent": 0.0, "speedLimit": 70, "infrastructure": "SWITCH (85-86; 100-85)", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 86, "section": "O", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 87, "section": "O", "blockLengthM": 86.6, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 88, "section": "O", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "STATION; POPLAR", "stationSide": "Left", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 89, "section": "P", "blockLengthM": 75, "blockGradePercent": -0.5, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": -0.375, "cumulativeElevationM": 0.125},
            {"blockNumber": 90, "section": "P", "blockLengthM": 75, "blockGradePercent": -1.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": -0.75, "cumulativeElevationM": -0.625},
            {"blockNumber": 91, "section": "P", "blockLengthM": 75, "blockGradePercent": -2.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": -1.5, "cumulativeElevationM": -2.125},
            {"blockNumber": 92, "section": "P", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": -2.125},
            {"blockNumber": 93, "section": "P", "blockLengthM": 75, "blockGradePercent": 2.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 1.5, "cumulativeElevationM": -0.625},
            {"blockNumber": 94, "section": "P", "blockLengthM": 75, "blockGradePercent": 1.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.75, "cumulativeElevationM": 0.125},
            {"blockNumber": 95, "section": "P", "blockLengthM": 75, "blockGradePercent": 0.5, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.375, "cumulativeElevationM": 0.5},
            {"blockNumber": 96, "section": "P", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "STATION; CASTLE SHANNON", "stationSide": "Left", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 97, "section": "P", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 98, "section": "Q", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 99, "section": "Q", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 100, "section": "Q", "blockLengthM": 75, "blockGradePercent": 0.0, "speedLimit": 25, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 101, "section": "R", "blockLengthM": 35, "blockGradePercent": 0.0, "speedLimit": 26, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 102, "section": "S", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 103, "section": "S", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 104, "section": "S", "blockLengthM": 80, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 105, "section": "T", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 106, "section": "T", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 107, "section": "T", "blockLengthM": 90, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 108, "section": "T", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "RAILWAY CROSSING", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 109, "section": "T", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 28, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 110, "section": "U", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 111, "section": "U", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 112, "section": "U", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 113, "section": "U", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 114, "section": "U", "blockLengthM": 162, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 115, "section": "U", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 116, "section": "U", "blockLengthM": 100, "blockGradePercent": 0.0, "speedLimit": 30, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 117, "section": "V", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 15, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 118, "section": "V", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 15, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 119, "section": "V", "blockLengthM": 40, "blockGradePercent": 0.0, "speedLimit": 15, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 120, "section": "V", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 15, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 121, "section": "V", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 15, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 122, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 123, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 124, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 125, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 126, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 127, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 128, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 129, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 130, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 131, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 132, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "Left", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 133, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 134, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 135, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 136, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 137, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 138, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 139, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 140, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 141, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "Right", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 142, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 143, "section": "W", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "UNDERGROUND", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 144, "section": "X", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 145, "section": "X", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 146, "section": "X", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 147, "section": "Y", "blockLengthM": 50, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 148, "section": "Y", "blockLengthM": 184, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 149, "section": "Y", "blockLengthM": 40, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5},
            {"blockNumber": 150, "section": "Z", "blockLengthM": 35, "blockGradePercent": 0.0, "speedLimit": 20, "infrastructure": "", "stationSide": "", "elevationM": 0.0, "cumulativeElevationM": 0.5}
        ]
        self.preloadedDistances = {
                    'segments': [
                        {
                            'fromStation': 'GLENBURY',
                            'toStation': 'DORMONT',
                            'distance': 1000.0 + 50.0,  # meters + half of block 73 (100m block)
                            'fromBlock': 65,
                            'toBlock': 73,
                            'stationBlockHalfLength': 50.0
                        },
                        {
                            'fromStation': 'DORMONT',
                            'toStation': 'MT LEBANON',
                            'distance': 400.0 + 150.0,  # meters + half of block 77 (300m block)
                            'fromBlock': 73,
                            'toBlock': 77,
                            'stationBlockHalfLength': 150.0
                        },
                        {
                            'fromStation': 'MT LEBANON',
                            'toStation': 'POPLAR',
                            'distance': 2886.6 + 50.0,  # meters + half of block 88 (100m block)
                            'fromBlock': 77,
                            'toBlock': 88,
                            'stationBlockHalfLength': 50.0
                        },
                        {
                            'fromStation': 'POPLAR',
                            'toStation': 'CASTLE SHANNON',
                            'distance': 625.0 + 37.5,  # meters + half of block 96 (75m block)
                            'fromBlock': 88,
                            'toBlock': 96,
                            'stationBlockHalfLength': 37.5
                        },
                        {
                            'fromStation': 'CASTLE SHANNON',
                            'toStation': 'DORMONT',
                            'distance': 690.0 + 50.0,  # meters + half of block 105 (100m block)
                            'fromBlock': 96,
                            'toBlock': 105,
                            'stationBlockHalfLength': 50.0
                        },
                        {
                            'fromStation': 'DORMONT',
                            'toStation': 'GLENBURY',
                            'distance': 890.0 + 81.0,  # meters + half of block 114 (162m block)
                            'fromBlock': 105,
                            'toBlock': 114,
                            'stationBlockHalfLength': 81.0
                        },
                        {
                            'fromStation': 'GLENBURY',
                            'toStation': 'OVERBROOK',
                            'distance': 652.0 + 25.0,  # meters + half of block 123 (50m block)
                            'fromBlock': 114,
                            'toBlock': 123,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'OVERBROOK',
                            'toStation': 'INGLEWOOD',
                            'distance': 450.0 + 25.0,  # meters + half of block 132 (50m block)
                            'fromBlock': 123,
                            'toBlock': 132,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'INGLEWOOD',
                            'toStation': 'CENTRAL',
                            'distance': 450.0 + 25.0,  # meters + half of block 141 (50m block)
                            'fromBlock': 132,
                            'toBlock': 141,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'CENTRAL',
                            'toStation': 'WHITED',
                            'distance': 1609.0 + 150.0,  # meters + half of block 22 (300m block)
                            'fromBlock': 141,
                            'toBlock': 22,
                            'stationBlockHalfLength': 150.0
                        },
                        {
                            'fromStation': 'WHITED',
                            'toStation': 'LLC PLAZA',
                            'distance': 1200.0 + 75.0,  # meters + half of block 16 (150m block)
                            'fromBlock': 22,
                            'toBlock': 16,
                            'stationBlockHalfLength': 75.0
                        },
                        {
                            'fromStation': 'LLC PLAZA',
                            'toStation': 'EDGEBROOK',
                            'distance': 900.0 + 50.0,  # meters + half of block 9 (100m block)
                            'fromBlock': 16,
                            'toBlock': 9,
                            'stationBlockHalfLength': 50.0
                        },
                        {
                            'fromStation': 'EDGEBROOK',
                            'toStation': 'PIONEER',
                            'distance': 700.0 + 50.0,  # meters + half of block 2 (100m block)
                            'fromBlock': 9,
                            'toBlock': 2,
                            'stationBlockHalfLength': 50.0
                        },
                        {
                            'fromStation': 'PIONEER',
                            'toStation': 'LLC PLAZA',
                            'distance': 650.0 + 75.0,  # meters + half of block 16 (150m block)
                            'fromBlock': 2,
                            'toBlock': 16,
                            'stationBlockHalfLength': 75.0
                        },
                        {
                            'fromStation': 'LLC PLAZA',
                            'toStation': 'WHITED',
                            'distance': 1050.0 + 150.0,  # meters + half of block 22 (300m block)
                            'fromBlock': 16,
                            'toBlock': 22,
                            'stationBlockHalfLength': 150.0
                        },
                        {
                            'fromStation': 'WHITED',
                            'toStation': 'SOUTH BANK',
                            'distance': 1400.0 + 25.0,  # meters + half of block 31 (50m block)
                            'fromBlock': 22,
                            'toBlock': 31,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'SOUTH BANK',
                            'toStation': 'CENTRAL',
                            'distance': 400.0 + 25.0,  # meters + half of block 39 (50m block)
                            'fromBlock': 31,
                            'toBlock': 39,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'CENTRAL',
                            'toStation': 'INGLEWOOD',
                            'distance': 450.0 + 25.0,  # meters + half of block 48 (50m block)
                            'fromBlock': 39,
                            'toBlock': 48,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'INGLEWOOD',
                            'toStation': 'OVERBROOK',
                            'distance': 450.0 + 25.0,  # meters + half of block 57 (50m block)
                            'fromBlock': 48,
                            'toBlock': 57,
                            'stationBlockHalfLength': 25.0
                        },
                        {
                            'fromStation': 'OVERBROOK',
                            'toStation': 'GLENBURY',
                            'distance': 500.0 + 100.0,  # meters + half of block 65 (200m block)
                            'fromBlock': 57,
                            'toBlock': 65,
                            'stationBlockHalfLength': 100.0
                        }
                    ]
                }
    
    def getDistance(self, blockNumber):
        """
        Get a distance to next station from a specific block
        
        :param blockNumber: The block Number (1-146)
        """
        for distances in self.preloadedDistances['segments']:
            if distances['fromBlock'] == blockNumber:
                return distances
        return None
    
    def getValue(self, blockNumber, key):
        """
        Get a value from a specific block.
        
        Args:
            blockNumber (int): The block number (1-146)
            key (str): The field name to retrieve. Options:
                - 'section'
                - 'blockLengthM'
                - 'blockGradePercent'
                - 'speedLimit'
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

class BeaconData:
    def __init__(self, beaconNumber, distanceToNext=None, forwardStationName=None, backwardStationName=None):
        self.blockNumber = beaconNumber
        self.distanceToNext = distanceToNext
        self.forwardStationName = forwardStationName
        self.backwardStationName = backwardStationName


# Beacon 1: Glenbury (Block 60) to Dormont (Block 68)
# Distance: 50 + 100 + 100 + 100 + 100 + 100 + 100 + 50 = 800m
# Midpoint distance: 400m from each station
# Beacon placed at: Block 64 (midpoint between blocks)
glenburyToDormont = BeaconData(
    beaconNumber=64,
    distanceToNext=400.0,
    forwardStationName="Dormont",
    backwardStationName="Glenbury"
)

# Beacon 2: Dormont (Block 68) to MT Lebanon (Block 71)
# Distance: 50 + 100 + 100 + 50 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 70 (midpoint between blocks)
dormountToMTLebanon = BeaconData(
    beaconNumber=70,
    distanceToNext=150.0,
    forwardStationName="MT Lebanon",
    backwardStationName="Dormont"
)

# Beacon 3: MT Lebanon (Block 71) to Poplar (Block 79)
# Distance: 50 + 200 + 300 + 300 + 300 + 200 + 100 + 50 = 1500m
# Midpoint distance: 750m from each station
# Beacon placed at: Block 75 (midpoint between blocks)
mtLebanoToPoplar = BeaconData(
    beaconNumber=75,
    distanceToNext=750.0,
    forwardStationName="Poplar",
    backwardStationName="MT Lebanon"
)

# Beacon 4: Poplar (Block 79) to Castle Shannon (Block 85)
# Distance: 50 + 75 + 75 + 75 + 75 + 75 + 50 = 475m
# Midpoint distance: 237.5m from each station
# Beacon placed at: Block 82 (midpoint between blocks)
poplarToCastleShannon = BeaconData(
    beaconNumber=82,
    distanceToNext=237.5,
    forwardStationName="Castle Shannon",
    backwardStationName="Poplar"
)

# Beacon 5: Castle Shannon (Block 85) to MT Lebanon (Block 71)
# Distance: 50 + 75 + 75 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 50 = 1150m
# Midpoint distance: 575m from each station
# Beacon placed at: Block 78 (midpoint between blocks)
castleShannonToMTLebanon = BeaconData(
    beaconNumber=78,
    distanceToNext=575.0,
    forwardStationName="MT Lebanon",
    backwardStationName="Castle Shannon"
)

# Beacon 6: MT Lebanon (Block 71) to Dormont (Block 96)
# Distance: 50 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 80 + 50 = 1180m
# Midpoint distance: 590m from each station
# Beacon placed at: Block 83 (midpoint between blocks)
mtLebanonToDormount2 = BeaconData(
    beaconNumber=83,
    distanceToNext=590.0,
    forwardStationName="Dormont",
    backwardStationName="MT Lebanon"
)

# Beacon 7: Dormont (Block 96) to Glenbury (Block 101)
# Distance: 50 + 100 + 100 + 100 + 100 + 50 = 500m
# Midpoint distance: 250m from each station
# Beacon placed at: Block 98 (midpoint between blocks)
dormountToGlenbury = BeaconData(
    beaconNumber=98,
    distanceToNext=250.0,
    forwardStationName="Glenbury",
    backwardStationName="Dormont"
)

# Beacon 8: Glenbury (Block 101) to Overbrook (Block 122)
# Distance: 50 + 100 + 100 + 100 + 100 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 = 1300m
# Midpoint distance: 650m from each station
# Beacon placed at: Block 111 (midpoint between blocks)
glenburyToOverbrook = BeaconData(
    beaconNumber=111,
    distanceToNext=650.0,
    forwardStationName="Overbrook",
    backwardStationName="Glenbury"
)

# Beacon 9: Overbrook (Block 122) to Inglewood (Block 132)
# Distance: 25 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 25 = 500m
# Midpoint distance: 250m from each station
# Beacon placed at: Block 127 (midpoint between blocks)
overbrookToInglewood = BeaconData(
    beaconNumber=127,
    distanceToNext=250.0,
    forwardStationName="Inglewood",
    backwardStationName="Overbrook"
)

# Beacon 10: Inglewood (Block 132) to Central (Block 140)
# Distance: 25 + 50 + 50 + 50 + 50 + 50 + 50 + 50 + 25 = 400m
# Midpoint distance: 200m from each station
# Beacon placed at: Block 136 (midpoint between blocks)
inglewoodToCentral = BeaconData(
    beaconNumber=136,
    distanceToNext=200.0,
    forwardStationName="Central",
    backwardStationName="Inglewood"
)

# Beacon 11: Central (Block 140) to Whited (Block 16)
# Distance: 25 + 50*54 + 75 + 25 = 5325m
# Midpoint distance: 2662.5m from each station
# Beacon placed at: Block 78 (midpoint between blocks)
centralToWhited = BeaconData(
    beaconNumber=78,
    distanceToNext=2662.5,
    forwardStationName="Whited",
    backwardStationName="Central"
)

# Beacon 12: Whited (Block 16) to LLC (Block 13)
# Distance: 75 + 150 + 75 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 14 (midpoint between blocks)
whitedToLLC = BeaconData(
    beaconNumber=14,
    distanceToNext=150.0,
    forwardStationName="LLC",
    backwardStationName="Whited"
)

# Beacon 13: LLC (Block 13) to Edgebrook (Block 7)
# Distance: 75 + 100 + 100 + 100 + 100 + 75 = 550m
# Midpoint distance: 275m from each station
# Beacon placed at: Block 10 (midpoint between blocks)
llcToEdgebrook = BeaconData(
    beaconNumber=10,
    distanceToNext=275.0,
    forwardStationName="Edgebrook",
    backwardStationName="LLC"
)

# Beacon 14: Edgebrook (Block 7) to Pioneer (Block 1)
# Distance: 50 + 100 + 100 + 100 + 100 + 50 = 500m
# Midpoint distance: 250m from each station
# Beacon placed at: Block 4 (midpoint between blocks)
edgebrookToPioneer = BeaconData(
    beaconNumber=4,
    distanceToNext=250.0,
    forwardStationName="Pioneer",
    backwardStationName="Edgebrook"
)

# Beacon 15: Pioneer (Block 1) to LLC (Block 13)
# Distance: 50 + 100 + 100 + 100 + 100 + 75 + 150 + 75 = 750m
# Midpoint distance: 375m from each station
# Beacon placed at: Block 7 (midpoint between blocks)
pioneerToLLC = BeaconData(
    beaconNumber=7,
    distanceToNext=375.0,
    forwardStationName="LLC",
    backwardStationName="Pioneer"
)

# Beacon 16: LLC (Block 13) to Whited (Block 16)
# Distance: 75 + 150 + 75 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 14 (midpoint between blocks)
llcToWhited = BeaconData(
    beaconNumber=14,
    distanceToNext=150.0,
    forwardStationName="Whited",
    backwardStationName="LLC"
)

# Beacon 17: Whited (Block 16) to South Bank (Block 25)
# Distance: 75 + 50 + 50 + 50 + 50 + 50 + 50 + 75 = 400m
# Midpoint distance: 200m from each station
# Beacon placed at: Block 20 (midpoint between blocks)
whitedToSouthBank = BeaconData(
    beaconNumber=20,
    distanceToNext=200.0,
    forwardStationName="South Bank",
    backwardStationName="Whited"
)

# Beacon 18: South Bank (Block 25) to Central (Block 31)
# Distance: 25 + 50 + 50 + 50 + 50 + 50 + 25 = 300m
# Midpoint distance: 150m from each station
# Beacon placed at: Block 28 (midpoint between blocks)
southBankToCentral = BeaconData(
    beaconNumber=28,
    distanceToNext=150.0,
    forwardStationName="Central",
    backwardStationName="South Bank"
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

