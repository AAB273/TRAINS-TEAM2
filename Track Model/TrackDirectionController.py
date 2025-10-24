#

class TrackDirectionController:
    """
    Handles bidirectional track direction management for groups of blocks.
    Integrates with TrackDataManager to track, toggle, and update direction states.
    """

    def __init__(self, data_manager):
        """
        Initialize the TrackDirectionController.

        Args:
            data_manager: Reference to the TrackDataManager instance managing track data.
        """
        self.data_manager = data_manager

        # Initialize with existing bidirectional directions from TrackDataManager
        if not hasattr(self.data_manager, "bidirectional_directions"):
            self.data_manager.bidirectional_directions = {
                "Blocks 1-5": 0,
                "Blocks 6-10": 0,
                "Blocks 11-15": 0
            }

    # -------------------------------------------------------------------------
    # CORE DIRECTION FUNCTIONS
    # -------------------------------------------------------------------------
    def toggle_direction(self, section_name: str):
        """
        Toggles the direction for a given track section between left (0) and right (1).

        Args:
            section_name (str): The name of the section (e.g., "Blocks 1-5").
        """
        if section_name not in self.data_manager.bidirectional_directions:
            print(f"⚠️ Invalid section name: {section_name}")
            return

        current_dir = self.data_manager.bidirectional_directions[section_name]
        new_dir = 1 - current_dir  # Toggle between 0 and 1
        self.data_manager.bidirectional_directions[section_name] = new_dir

        print(f"🔄 {section_name} direction changed: {'Right' if new_dir else 'Left'}")

    def set_direction(self, section_name: str, direction: int):
        """
        Sets a specific direction for a given section.

        Args:
            section_name (str): Section name key.
            direction (int): 0 = Left, 1 = Right.
        """
        if section_name not in self.data_manager.bidirectional_directions:
            print(f"⚠️ Invalid section name: {section_name}")
            return

        if direction not in (0, 1):
            print(f"⚠️ Invalid direction value: {direction}")
            return

        self.data_manager.bidirectional_directions[section_name] = direction
        print(f"✅ {section_name} set to: {'Right' if direction else 'Left'}")

    def get_direction(self, section_name: str) -> int:
        """
        Returns the current direction (0 or 1) of a given section.

        Args:
            section_name (str): Section name key.

        Returns:
            int: 0 = Left, 1 = Right
        """
        return self.data_manager.bidirectional_directions.get(section_name, 0)

    def get_all_directions(self) -> dict:
        """
        Returns a dictionary of all section directions.

        Returns:
            dict: Mapping of section names to their current directions.
        """
        return self.data_manager.bidirectional_directions
    
    def force_bidirectional_table_visible(self):
        """Force the bidirectional table to be visible - debugging method"""
        if hasattr(self, 'bidir_tree'):
            # Make sure the treeview is mapped (visible)
            self.bidir_tree.update()
            
            # Force a geometry update
            self.bidir_tree.pack_info()
            
            # Print treeview geometry information
            print("=== BIDIRECTIONAL TABLE VISIBILITY DEBUG ===")
            print(f"Treeview exists: {self.bidir_tree is not None}")
            print(f"Treeview mapped: {self.bidir_tree.winfo_ismapped()}")
            print(f"Treeview width: {self.bidir_tree.winfo_width()}")
            print(f"Treeview height: {self.bidir_tree.winfo_height()}")
            print(f"Treeview x: {self.bidir_tree.winfo_x()}")
            print(f"Treeview y: {self.bidir_tree.winfo_y()}")
            print(f"Parent visible: {self.bidir_tree.winfo_parent()}")
            
            # Try to force focus and selection to make it visible
            children = self.bidir_tree.get_children()
            if children:
                self.bidir_tree.focus(children[0])
                self.bidir_tree.selection_set(children[0])
            
            print("=============================================")

    def update_bidirectional_table(self):
        """Update the bidirectional block table with current directions from shared data"""
        if hasattr(self, 'bidir_tree'):
            # Clear existing rows
            for item in self.bidir_tree.get_children():
                self.bidir_tree.delete(item)
            
            # Populate with current directions from shared manager
            if hasattr(self.data_manager, 'bidirectional_directions'):
                print(f"🔄 Updating Main UI table with: {self.data_manager.bidirectional_directions}")
                
                for group, direction in self.data_manager.bidirectional_directions.items():
                    direction_text = "← Left" if direction == 0 else "Right →"
                    self.bidir_tree.insert("", "end", values=(group, direction_text))
                    print(f"   ➕ Added row: {group} = {direction_text}")
                
                # Force the treeview to update visually
                self.bidir_tree.update_idletasks()
                print("✅ Main UI bidirectional table VISUALLY updated")

    def toggle_bidirectional_direction(self, group_name):
        """Toggle the direction for a block group using shared data"""
        if hasattr(self.data_manager, 'bidirectional_directions') and group_name in self.data_manager.bidirectional_directions:
            current_direction = self.data_manager.bidirectional_directions[group_name]
            new_direction = 1 if current_direction == 0 else 0
            
            print(f"🔄 Toggling {group_name} from {current_direction} to {new_direction}")
            
            # Update the shared data manager
            self.data_manager.bidirectional_directions[group_name] = new_direction
            
            # Force immediate refresh of the table
            self.update_bidirectional_table()
            
            # Also force refresh the Test UI if it exists
            if hasattr(self, 'tester_reference') and hasattr(self.tester_reference, 'refresh_bidirectional_controls'):
                self.tester_reference.refresh_bidirectional_controls()
                print("🔄 Test UI refresh triggered")
            
            print(f"✅ {group_name} direction changed to: {'Right →' if new_direction == 1 else '← Left'}")

    # -------------------------------------------------------------------------
    # OPTIONAL: UI HOOKS
    # -------------------------------------------------------------------------
    def update_ui_labels(self, ui_labels: dict):
        """
        Updates direction labels or indicators in the UI.

        Args:
            ui_labels (dict): A mapping of section names to Tkinter Label widgets.
        """
        for section, label in ui_labels.items():
            direction = self.get_direction(section)
            label.config(text=f"{section}: {'→ Right' if direction else '← Left'}")

    def reset_all_directions(self):
        """
        Resets all directions to Left (0).
        """
        for section in self.data_manager.bidirectional_directions:
            self.data_manager.bidirectional_directions[section] = 0
        print("🔁 All track directions reset to Left.")

