import tkinter as tk
from typing import Dict, Any

class TrackDiagramDrawer:
    """
    Handles drawing, updating, and clearing of the track diagram and its icons.
    Designed for use within the Track Model UI.
    """

    def __init__(self, canvas: tk.Canvas, track_data: Any):
        """
        Initialize the TrackDiagramDrawer.

        Args:
            canvas (tk.Canvas): The Tkinter Canvas used for drawing.
            track_data (Any): Reference to TrackDataManager or equivalent data source.
        """
        self.canvas = canvas
        self.track_data = track_data
        self.icon_refs = {}  # Store canvas item references for later updates

    # -------------------------------------------------------------------------
    # CORE DRAWING FUNCTIONS
    # -------------------------------------------------------------------------
    def draw_track_diagram(self):
        """
        Draws the static base layout of the track diagram.
        Includes track lines, block positions, and placeholders for icons.
        """
        self.canvas.delete("all")
        self.icon_refs.clear()

        y = 100
        block_length = 60
        num_blocks = len(self.track_data.blocks)

        for i in range(num_blocks):
            x_start = 50 + i * block_length
            x_end = x_start + block_length

            # Draw track line
            self.canvas.create_line(x_start, y, x_end, y, width=4, fill="black")

            # Draw block label
            block_label = f"Block {i+1}"
            self.canvas.create_text((x_start + x_end) / 2, y - 15, text=block_label, font=("Arial", 10))

            # Store positions for icon placement
            self.icon_refs[i + 1] = {"x": (x_start + x_end) / 2, "y": y}

        # Draw all icons after layout
        self.draw_track_icons()

    def draw_track_icons(self):
        """
        Draws all dynamic icons (switches, crossings, traffic lights, etc.) based on block states.
        """
        for b in self.track_data.blocks:
            pos = self.icon_refs.get(b.block_number, None)
            if not pos:
                continue

            x, y = pos["x"], pos["y"]

            # Draw switch
            if hasattr(b, "switch") and b.switch is not None:
                color = "blue" if b.switch else "gray"
                self.canvas.create_oval(x - 6, y - 25, x + 6, y - 13, fill=color, outline="black")

            # Draw crossing
            if hasattr(b, "crossing") and b.crossing:
                color = "orange" if b.crossing else "gray"
                self.canvas.create_rectangle(x - 6, y + 13, x + 6, y + 25, fill=color, outline="black")

            # Draw signals and lights
            if hasattr(b, "signal"):
                self.draw_signal(b.block_number, b.signal)
            if hasattr(b, "traffic_light"):
                self.draw_traffic_light(b.block_number, b.traffic_light)

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
        pos = self.icon_refs.get(block_num)
        if not pos:
            return

        x, y = pos["x"], pos["y"] - 40
        color = "green" if state.lower() == "green" else "red"
        self.canvas.create_oval(
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
        pos = self.icon_refs.get(block_num)
        if not pos:
            return

        x, y = pos["x"], pos["y"] - 55
        color = "green" if state.upper() == "GO" else "red"
        self.canvas.create_rectangle(x - 8, y - 4, x + 8, y + 4, fill=color, outline="black")

    # -------------------------------------------------------------------------
    # CLEARING AND RESET
    # -------------------------------------------------------------------------
    def clear_all_track_icons(self):
        """
        Removes all dynamic icons from the canvas while leaving the base track lines intact.
        """
        # We’ll just clear everything and redraw static track if needed
        self.canvas.delete("all")
        self.icon_refs.clear()
