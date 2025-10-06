class RailwayData:
    def __init__(self):
        self.maintenance_mode = False
        self.test_mode = False
        self.current_line = "Green"  # Default line
        
        # Callbacks for UI updates
        self.on_line_change = []
        self.on_maintenance_mode_change = []
        self.on_test_mode_change = []
        
        # Initialize data
        self.track_data = {
            "switches": {
                "Switch 28": {"condition": "Normal Operation", "direction": "57-58", "line": "Green"},
                "Switch 15": {"condition": "Normal Operation", "direction": "Normal", "line": "Red"},
            },
            "crossings": {
                "Railway 107": {"condition": "Normal Operation", "lights": "Red", "bar": "Closed", "line": "Green"},
                "Railway 205": {"condition": "Normal Operation", "lights": "Green", "bar": "Open", "line": "Red"},
            },
            "lights": {
                "Light 3": {"condition": "Fault", "signal": "Red", "line": "Green"},
                "Light 7": {"condition": "Normal Operation", "signal": "Green", "line": "Red"},
            }
        }
        
        self.fault_data = [
            ["3/16", "14:22:01", "Green", "107", "Railway Crossing", "Active"],
            ["9/14", "01:11:21", "Red", "67", "Rails", "Resolved"],
            # ... (rest of fault data)
        ]
        
        self.block_data = [
            ["Yes", "Green", "7"],
            ["Yes", "Green", "67"],
            ["No", "Red", "7"],
            ["Yes", "Red", "67"],
            # ... (rest of block data)
        ]
        
        # Keep original data for filtering
        self.fault_data_original = self.fault_data.copy()
        self.block_data_original = self.block_data.copy()

        ######################################
       # Initialize filtered_track_data
        self.filtered_track_data = {}
        self.filter_data_by_line(self.current_line)  # This will populate filtered_track_data

        ################### changed from  # Initialize filtered_track_data - ADD THIS LINE
        ###################self.filtered_track_data = self.track_data.copy()

    def update_fault_data(self, row_index, col_index, new_value):
        """Update fault data and keep original data in sync"""
        if 0 <= row_index < len(self.fault_data):
            self.fault_data[row_index][col_index] = new_value
            # Also update the original data to persist changes
            if 0 <= row_index < len(self.fault_data_original):
                self.fault_data_original[row_index][col_index] = new_value
    
    def update_block_data(self, row_index, col_index, new_value):
        """Update block data and keep original data in sync"""
        if 0 <= row_index < len(self.block_data):
            self.block_data[row_index][col_index] = new_value
            # Also update the original data to persist changes
            if 0 <= row_index < len(self.block_data_original):
                self.block_data_original[row_index][col_index] = new_value
    
    def update_track_data(self, category, item, field, new_value):
        """Update track data (crossings, switches, lights)"""
        if category in self.track_data and item in self.track_data[category]:
            self.track_data[category][item][field] = new_value

    #changes the active track
    def set_current_line(self, line):
        """set the current active track and then filters the data"""
        if line != self.current_line:
            self.current_line = line
            self.filter_data_by_line(line)  # FIXED: Added line parameter
            # Notify all listeners that line changed
            for callback in self.on_line_change:
                callback()
    
    def filter_data_by_line(self, line):  # FIXED: Added line parameter
        """Filter all data to show only the current line"""
        self.current_line = line  # Make sure current_line is updated
        
        # Filter fault data
        self.fault_data = [row for row in self.fault_data_original 
                          if row[2] == line]
        
        # Filter block data  
        self.block_data = [row for row in self.block_data_original 
                          if row[1] == line]
        
        self.filtered_track_data = {
        "switches": {k: v for k, v in self.track_data["switches"].items() 
                    if v.get("line") == line},
        "crossings": {k: v for k, v in self.track_data["crossings"].items() 
                     if v.get("line") == line},
        "lights": {k: v for k, v in self.track_data["lights"].items() 
                  if v.get("line") == line}
        }
       

    def set_maintenance_mode(self, mode):
        self.maintenance_mode = mode
        for callback in self.on_maintenance_mode_change:
            callback()
    
    def set_test_mode(self, mode):
        self.test_mode = mode
        for callback in self.on_test_mode_change:
            callback()
    
    def filter_fault_data(self, search_term):
        if not search_term:
            self.fault_data = [row for row in self.fault_data_original 
                              if row[2] == self.current_line]  # Filter by current line
        else:
            self.fault_data = [row for row in self.fault_data_original 
                              if row[2] == self.current_line and 
                              any(search_term in str(cell).lower() for cell in row)]
        return self.fault_data
    
    def filter_block_data(self, search_term):
        if not search_term:
            self.block_data = [row for row in self.block_data_original 
                              if row[1] == self.current_line]  # Filter by current line
        else:
            self.block_data = [row for row in self.block_data_original 
                              if row[1] == self.current_line and 
                              any(search_term in str(cell).lower() for cell in row)]
        return self.block_data