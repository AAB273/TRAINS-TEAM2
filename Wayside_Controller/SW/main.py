import tkinter as tk
from ui.header import Header
from ui.left_panel import LeftPanel
from ui.center_panel import CenterPanel
from ui.right_panel import RightPanel
from data.models import RailwayData
#
class RailwayControlSystem:
    def __init__(self, root, shared_data=None):
        self.root = root
        self.root.title("Wayside Controller")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a4d')
        
        # Use shared data or create new instance
        if shared_data:
            self.data = shared_data
            print("🔗 Main UI using shared data instance")
        else:
            self.data = RailwayData()
            print("🚂 Main UI using standalone data instance")
        
        # Create UI components
        self.create_ui()

        # Set up the logging callback system
        self.setup_logging()

    def setup_logging(self):
        """Set up the direct callback logging system"""
        # Use center_panel's log_callback directly
        if hasattr(self.center_panel, 'log_callback') and self.center_panel.log_callback:
            log_callback = self.center_panel.log_callback
            
            # Connect all panels to the same callback
            if hasattr(self.header, 'set_log_callback'):
                self.header.set_log_callback(log_callback)
            
            if hasattr(self.left_panel, 'set_log_callback'):
                self.left_panel.set_log_callback(log_callback)
            
            if hasattr(self.right_panel, 'set_log_callback'):
                self.right_panel.set_log_callback(log_callback)
            
            # Test the logging system
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_callback(f"{current_time} SYSTEM: Main application initialized successfully")
        else:
            print("❌ Logging system not available")

    def create_ui(self):
        # Create header - pass self as app reference
        self.header = Header(self.root, self.data, app=self)
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

        # Line change callbacks
        self.data.on_line_change.append(self.right_panel.on_line_changed) 
        self.data.on_line_change.append(self.header.update_tab_appearance)

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayControlSystem(root)
    root.mainloop()