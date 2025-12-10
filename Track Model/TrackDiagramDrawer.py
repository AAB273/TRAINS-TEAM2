import tkinter as tk
from typing import Dict, Any
from PIL import Image, ImageTk
import os

class TrackDiagramDrawer:
    """
    Handles drawing, updating, and clearing of the track diagram and its icons.
    Designed for use within the Track Model UI.
    Now includes Green Line station icon support.
    """

    # Green Line Station Coordinates (same order as provided - lowest to highest block)
    GREEN_LINE_STATION_COORDINATES = {
        "Station 1": (362, 40),
        "Station 2": (460, 24),
        "Station 3": (299, 30),
        "Station 4": (257, 77),
        "Station 5": (261, 154),
        "Station 6": (304, 225),
        "Station 7": (376, 224),
        "Station 8": (443, 223),
        "Station 9": (520, 316),
        "Station 10": (492, 470),
        "Station 11": (357, 470),
        "Station 12": (233, 474),
        "Station 13": (253, 407),
    }

    def __init__(self, ui_reference: Any, track_data: Any):
        """
        Initialize the TrackDiagramDrawer.

        Args:
            ui_reference (Any): Reference to the main UI (TrackModelUI instance)
            track_data (Any): Reference to TrackDataManager or equivalent data source.
        """
        self.ui_reference = ui_reference
        self.track_data = track_data
        self.icon_refs = {}  # Store canvas item references for later updates
        
        # Station-related attributes
        self.station_image = None
        self.station_photo = None
        self.station_items = []  # Store references to station icons on canvas
        
        # Try to load station icon from the uploads directory
        self._load_station_icon()

    def _load_station_icon(self, size=(24, 24)):
        """
        Load the station icon from the expected location.
        
        Args:
            size (tuple): Desired size for the icon (width, height). Default: 24x24 pixels (60% of original).
        """
        # Try multiple possible paths
        possible_paths = [
            "/mnt/user-data/uploads/Station.png",
            "Station.png",
            os.path.join(os.path.dirname(__file__), "Station.png"),
            os.path.join(os.path.dirname(__file__), "assets", "Station.png")
        ]
        
        for icon_path in possible_paths:
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    self.station_photo = ImageTk.PhotoImage(img)
                    self.station_image = img
                    print(f"[TrackDiagramDrawer] Station icon loaded from: {icon_path}")
                    return
                except Exception as e:
                    print(f"[TrackDiagramDrawer] Error loading station icon from {icon_path}: {e}")
        
        print("[TrackDiagramDrawer] Warning: Station icon not found. Stations will not be displayed.")

    def _is_green_line_selected(self):
        """
        Check if Green Line is currently selected in the UI.
        
        Returns:
            bool: True if Green Line is selected, False otherwise
        """
        if hasattr(self.ui_reference, 'selected_line'):
            current_line = self.ui_reference.selected_line.get()
            return "Green" in current_line
        return True  # Default to Green Line if no selection variable exists

    def draw_green_line_stations(self):
        """
        Draw all Green Line station icons at their specified coordinates.
        Only draws if Green Line is selected and station icon is loaded.
        """
        # Check if Green Line is selected
        if not self._is_green_line_selected():
            return
        
        # Check if station icon is loaded
        if not self.station_photo:
            return
        
        # Get canvas from UI reference
        if not hasattr(self.ui_reference, 'track_canvas'):
            print("[TrackDiagramDrawer] Warning: track_canvas not found in UI reference")
            return
        
        canvas = self.ui_reference.track_canvas
        
        # Clear previous station items
        self.clear_stations()
        
        # Draw each station
        for station_name, (x, y) in self.GREEN_LINE_STATION_COORDINATES.items():
            try:
                # Draw the station icon
                item_id = canvas.create_image(x, y, image=self.station_photo, anchor="center")
                self.station_items.append(item_id)
                
                # Draw station label below the icon
                label_id = canvas.create_text(
                    x, y + 22, 
                    text=station_name, 
                    font=("Arial", 8, "bold"),
                    fill="darkgreen"
                )
                self.station_items.append(label_id)
                
            except Exception as e:
                print(f"[TrackDiagramDrawer] Error drawing station {station_name}: {e}")

    def clear_stations(self):
        """
        Remove all station icons from the canvas.
        """
        if hasattr(self.ui_reference, 'track_canvas'):
            canvas = self.ui_reference.track_canvas
            for item_id in self.station_items:
                try:
                    canvas.delete(item_id)
                except:
                    pass
        self.station_items.clear()

    # -------------------------------------------------------------------------
    # CORE DRAWING FUNCTIONS
    # -------------------------------------------------------------------------
    def draw_track_diagram(self):
        """
        Draws the static base layout of the track diagram.
        Includes track lines, block positions, and placeholders for icons.
        """
        if not hasattr(self.ui_reference, 'track_canvas'):
            return
            
        canvas = self.ui_reference.track_canvas
        canvas.delete("all")
        self.icon_refs.clear()
        self.station_items.clear()

        y = 100
        block_length = 60
        num_blocks = len(self.track_data.blocks)

        for i in range(num_blocks):
            x_start = 50 + i * block_length
            x_end = x_start + block_length

            # Draw track line
            canvas.create_line(x_start, y, x_end, y, width=4, fill="black")

            # Draw block label
            block_label = f"Block {i+1}"
            canvas.create_text((x_start + x_end) / 2, y - 15, text=block_label, font=("Arial", 10))

            # Store positions for icon placement
            self.icon_refs[i + 1] = {"x": (x_start + x_end) / 2, "y": y}

        # Draw all icons after layout
        self.draw_track_icons()
        
        # Draw Green Line stations if applicable
        self.draw_green_line_stations()

    def draw_track_icons(self):
        """
        Draws all dynamic icons (switches, crossings, traffic lights, etc.) based on block states.
        This method can be implemented based on your needs.
        """
        # Placeholder for future icon drawing
        pass

    # -------------------------------------------------------------------------
    # SPECIFIC DRAWING HELPERS
    # -------------------------------------------------------------------------
    def draw_traffic_light(self, block_num: int, state: str, light_size: int = 16):
        """
        Draws a traffic light icon representing block signal state.

        Args:
            block_num (int): The block number where the light appears.
            state (str): State of the light ('green', 'red', etc.).
            light_size (int): Diameter of the traffic light circle.
        """
        if not hasattr(self.ui_reference, 'track_canvas'):
            return
            
        canvas = self.ui_reference.track_canvas
        pos = self.icon_refs.get(block_num)
        if not pos:
            return

        x, y = pos["x"], pos["y"] - 40
        color = "green" if state.lower() == "green" else "red"
        canvas.create_oval(
            x - light_size / 2, y - light_size / 2,
            x + light_size / 2, y + light_size / 2,
            fill=color, outline="black"
        )

    def draw_signal(self, block_num: int, state: str):
        """
        Draws a small rectangular signal indicator above each block.

        Args:
            block_num (int): The block number.
            state (str): Signal state (e.g., 'GO', 'STOP').
        """
        if not hasattr(self.ui_reference, 'track_canvas'):
            return
            
        canvas = self.ui_reference.track_canvas
        pos = self.icon_refs.get(block_num)
        if not pos:
            return

        x, y = pos["x"], pos["y"] - 55
        color = "green" if state.upper() == "GO" else "red"
        canvas.create_rectangle(x - 8, y - 4, x + 8, y + 4, fill=color, outline="black")

    # -------------------------------------------------------------------------
    # CLEARING AND RESET
    # -------------------------------------------------------------------------
    def clear_all_track_icons(self):
        """
        Removes all dynamic icons from the canvas while leaving the base track lines intact.
        """
        if hasattr(self.ui_reference, 'track_canvas'):
            canvas = self.ui_reference.track_canvas
            canvas.delete("all")
        self.icon_refs.clear()
        self.station_items.clear()