import tkinter as tk
from ui.header import Header
from ui.left_panel import LeftPanel
from ui.center_panel import CenterPanel
from ui.right_panel import RightPanel
from data.models import RailwayData

class RailwayControlSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Wayside Controller")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a4d')
        
        # Initialize data model
        self.data = RailwayData()
        
        # Create UI components
        self.create_ui()
        
    def create_ui(self):
        # Create header
        self.header = Header(self.root, self.data)
        self.header.pack(fill=tk.X, padx=10, pady=5)
        
        # Create main layout container
        main_frame = tk.Frame(self.root, bg='#1a1a4d')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create panels
        self.left_panel = LeftPanel(main_frame, self.data)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.center_panel = CenterPanel(main_frame, self.data)
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.right_panel = RightPanel(main_frame, self.data)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Connect panel updates
        self._connect_panel_updates()
    
    def _connect_panel_updates(self):
        """Connect data change callbacks between panels"""
         # Maintenance mode callbacks
        self.data.on_maintenance_mode_change.append(self.center_panel.update_mode_ui)
        self.data.on_maintenance_mode_change.append(self.right_panel.update_mode_ui)
        self.data.on_maintenance_mode_change.append(self.left_panel.update_mode_ui)

        # Line change callbacks - these update the entire UI
        self.data.on_line_change.append(self.center_panel.on_line_changed)
        self.data.on_line_change.append(self.right_panel.on_line_changed) 
        self.data.on_line_change.append(self.left_panel.on_line_changed)
        self.data.on_line_change.append(self.header.update_tab_appearance)  # Make sure header updates too

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()