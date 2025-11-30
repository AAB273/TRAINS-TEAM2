import json    
from pathlib import Path 

def load_socket_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config.get("modules", {})

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import UI_Variables
import tkinter.simpledialog as simpledialog
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from Test_UI import TrackModelTestUI  # Test/debug UI
from FileUploadManager import FileUploadManager
from TrackDiagramDrawer import TrackDiagramDrawer
from HeaterSystemManager import HeaterSystemManager
from BeaconManager import BeaconManager
from TrainSocketServer import TrainSocketServer
from MurphyTrackFailures import MurphyTrackFailures


class TrackModelUI(tk.Tk):
    def __init__(self, manager: UI_Variables.TrackDataManager):
        super().__init__()
        self.title("Track Model UI")
        self.geometry("1300x850")
        self.configure(bg="navy")

        # CRITICAL: Set data_manager FIRST before anything else
        self.data_manager = manager

        # Socket server setup
        module_config = load_socket_config()
        config = module_config.get("Track Model", {"port": 4})
        self.server = TrainSocketServer(
            port=config["port"],
            ui_id="Track Model"
        )
        self.server.set_allowed_connections(["Track SW","Track HW", "Train Model", "CTC", "Train HW","Train SW"])
        self.server.start_server(self._process_message)
        self.server.connect_to_ui('localhost', 12341, "CTC")
        self.server.connect_to_ui('localhost', 12346, "Train SW")
        self.server.connect_to_ui('localhost', 12347, "Train HW")
        self.server.connect_to_ui('localhost', 12345, "Train Model")
        self.server.connect_to_ui('localhost', 12342,  'Track SW')
        self.server.connect_to_ui('localhost', 12343,'Track HW')

        self.switch_blocks = set()
        self.switch_states = {}  # Dictionary to track switch states {block_num: direction}
        # Switch routing configuration for train path determination
        self.switch_routing = {
            12: {"normal": 13, "reverse": 13},    # Switch housed at 12: (12-13; 1-13)
            28: {"normal": 29, "reverse": 150},   # Switch housed at 28: (28-29; 150-28)
            58: {"normal": 58, "reverse": 151},   # Switch housed at 58: controls 57→58 or 57→yard
            62: {"normal": 63, "reverse": 63},    # Switch housed at 62: from main line or yard to 63
            76: {"normal": 78, "reverse": 101},   # Switch housed at 76: controls junction at 77 (76-77-78 or 76-77-101)
            85: {"normal": 86, "reverse": 100}    # Switch housed at 85: (85-86; 100-85)
        }
        self.crossing_blocks = set()
        self.light_states = {12, 29, 76, 86}
        self.station_blocks = set()

        self.block_positions_occupancy = {
            1: (125, 240), 
            2: (190, 240), 
            3: (250, 240), 
            4: (330, 240), 
            5: (410, 240),  
            6: (480, 110), 
            7: (540, 90), 
            8: (600, 70),  
            9: (660, 110),  
            10: (720, 105),  
            11: (480, 300), 
            12: (550, 330), 
            13: (640, 360), 
            14: (720, 400),  
            15: (820, 340),  
        }
        self.terminals = []

        self.test_block_occupancy(4, 1)

        # Initialize sorting state variables
        self.track_data_sort_column = None
        self.track_data_sort_reverse = False
        self.track_system_sort_column = None
        self.track_system_sort_reverse = False

        # Initialize random FIRST
        import random
        self.random = random

        # --- Auto-load Green Line data from Excel file FIRST ---
        import os
        track_file = os.path.join(os.path.dirname(__file__), "Track Data.xlsx")
        if os.path.exists(track_file):
            loaded = self.data_manager.load_excel_data(track_file)
            if loaded:
                print("[UI] Green Line Track Data successfully loaded on launch.")
            else:
                print("[UI] Failed to load Green Line Track Data.")
        else:
            print("[UI] Track Data.xlsx not found in directory.")

        # Initialize managers - AFTER data is loaded
        self.file_manager = FileUploadManager(self.data_manager, ui_reference=self)
        self.heater_manager = HeaterSystemManager(self.data_manager)
        self.diagram_drawer = TrackDiagramDrawer(self, self.data_manager)

        # Initialize BeaconManager for station beacons
        self.beacon_manager = BeaconManager()
        print('[UI] BeaconManager initialized with station beacons')


        # --- Auto-load Green Line track data from Excel on startup ---
        if not self.file_manager.auto_load_green_line():
            print("[UI] ⚠️ Green Line data could not be loaded automatically.")

        # --- POPULATE INFRASTRUCTURE SETS AFTER LOADING ---
        self._populate_infrastructure_sets()

        # Initialize traffic light states and occupancy for all blocks
        for b in self.data_manager.blocks:
            if not hasattr(b, "traffic_light_state"):
                b.traffic_light_state = 0
            if not hasattr(b, "occupancy"):
                b.occupancy = 0

        # Set initial environmental temperature
        if self.data_manager.environmental_temp is None:
            self.data_manager.environmental_temp = 70.0
            print("[Heater] Initial environmental temperature set to 70.0°F")
        
        # Initialize all block temperatures to environmental temp
        self.heater_manager.initialize_all_temperatures()

        # NOW initialize ticket sales AFTER blocks are loaded
        self._initialize_station_ticket_sales()

        self.update_station_boarding_data()

        # Start monitoring station occupancy AFTER everything is ready
        self.after(1000, self.monitor_station_occupancy)

        style = ttk.Style(self)
        style.configure("Large.TCheckbutton", font=("Arial", 11), padding=5)

        self.murphy_failures = MurphyTrackFailures(
            data_manager=self.data_manager,
            heater_manager=self.heater_manager,
            ui_reference=self
        )

        # Layout frames
        top_frame = tk.Frame(self, bg="navy")
        top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        left_frame = tk.Frame(top_frame, bg="navy")
        left_frame.pack(side="left", fill="y", padx=10)

        center_frame = tk.Frame(top_frame, bg="navy")
        center_frame.pack(side="left", fill="both", expand=True, padx=10)

        bottom_frame = tk.Frame(self, bg="navy")
        bottom_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=20)

        # Initialize filter variables
        self.filter_vars = {}

        # Build UI
        self.create_left_panel(left_frame)
        self.create_center_panel(center_frame)
        self.create_bottom_table(center_frame)

        # Start temperature loop
        self.after(100, self.start_temperature_update_loop)
        
        # Initialize train tracking data for actual speed and movement
        self.train_actual_speeds = {}  # Dictionary to store actual speeds by train ID
        self.train_positions_in_block = {}  # Track distance traveled in current block (meters)
        self.last_movement_update = {}  # Track last update time for each train
        self.train_directions = {}  # Track train direction: 'forward' or 'backward'
        
        # Start train movement update loop (runs every 100ms for smooth movement)
        self.after(100, self.update_train_movements)
        
        # Refresh UI periodically
        self.after(1000, self.refresh_ui)

    # ---------------- Helper ----------------
    def make_card(self, parent, title=None):
        card = tk.Frame(parent, bg="white", bd=2, relief="ridge")
        if title:
            tk.Label(card, text=title, font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
        return card
    
    def on_failure_changed(self):
        """Triggered when any failure mode checkbox is toggled."""
        import tkinter.simpledialog as simpledialog
        import tkinter.messagebox as messagebox

        # Determine which failure was triggered
        failures = {
            "Track Circuit": self.failure_train_circuit_var,
            "Broken Railroads": self.failure_rail_var,
            "Power": self.failure_power_var,
        }

        for failure_name, var in failures.items():
            if var.get():  # Box was checked
                block = simpledialog.askstring(
                    "Select Block",
                    f"Enter the block number to apply '{failure_name}' failure:"
                )

                if block:
                    # Here you could apply the failure to the backend (TrackDataManager, etc.)
                    print(f"Applying {failure_name} failure to Block {block}")
                    # Example if you have data_manager:
                    # self.data_manager.set_failure(block, failure_name)

                else:
                    messagebox.showinfo("Cancelled", f"No block selected for {failure_name}.")
                    var.set(False)  # Uncheck if cancelled

            else:
                # Failure unchecked (cleared)
                print(f"{failure_name} states updated")
                # Example: self.data_manager.clear_failure(failure_name)

    # ---------------- Left Panel ----------------
    def create_left_panel(self, parent):
        # Logo
        try:
            img = Image.open("blt logo.png").resize((120, 120))
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self.logo_img, bg="navy").pack(pady=10)
        except:
            tk.Label(parent, text="Logo not found", bg="navy", fg="white").pack(pady=10)

        # Line Selection
        line_card = self.make_card(parent, "Line Selection")
        
        # Create variable to track selected line
        self.selected_line = tk.StringVar(value="Green Line")
        
        # Radio buttons for line selection
        tk.Radiobutton(
            line_card,
            text="Red Line",
            variable=self.selected_line,
            value="Red Line",
            command=self.switch_line_data,
            bg="white",
            font=("Arial", 10)
        ).pack(anchor="w", padx=10, pady=5)
        
        tk.Radiobutton(
            line_card,
            text="Green Line",
            variable=self.selected_line,
            value="Green Line",
            command=self.switch_line_data,
            bg="white",
            font=("Arial", 10)
        ).pack(anchor="w", padx=10, pady=5)
        
        line_card.pack(fill="x", pady=10)

        # Environment Temp
        temp_card = self.make_card(parent, "Environment")

        def set_environment_temp():
            """Set the environmental (outside/ambient) temperature."""
            new_temp = simpledialog.askfloat("Set Temperature", "Enter new environmental temperature (°F):")
            if new_temp is not None:
                self.data_manager.environmental_temp = new_temp
                self.temp_label.config(text=f"Temperature: {new_temp}°F")
                self.heater_manager.set_environmental_temperature(new_temp)

        tk.Button(temp_card, text="Set Environmental Temp", command=set_environment_temp).pack(padx=10, pady=10)
        self.temp_label = tk.Label(
            temp_card,
            text=f"Temperature: {getattr(self.data_manager, 'environmental_temp', '--')}°F",
            bg="white"
        )
        self.temp_label.pack(padx=10, pady=5)
        temp_card.pack(fill="x", pady=10)

        # Train Details
        train_card = self.make_card(parent, "Train Details")
        self.train_combo = ttk.Combobox(train_card, values=self.data_manager.active_trains)
        self.train_combo.bind("<<ComboboxSelected>>", self.update_train_info)
        self.train_combo.pack(padx=10, pady=5)

        self.train_info = tk.Label(
            train_card,
            text="Occupancy: --\nCommanded Speed: --\nCommanded Authority: --",
            bg="white",
            justify="left"
        )
        self.train_info.pack(padx=10, pady=5)
        train_card.pack(fill="x", pady=10)

        # Murphy Failure Modes
        fail_card = self.make_card(parent, "Murphy Failure Modes")
        self.failure_train_circuit_var = tk.BooleanVar(value=False)
        self.failure_rail_var = tk.BooleanVar(value=False)
        self.failure_power_var = tk.BooleanVar(value=False)

        # Track Circuit Failure Checkbox
        track_circuit_check = tk.Checkbutton(
            fail_card,
            text="Track Circuit Failure",
            variable=self.failure_train_circuit_var,
            command=lambda: self.prompt_and_activate_track_circuit(),
            bg="lightblue",
            font=("Arial", 10)
        )
        track_circuit_check.pack(pady=5)

        # Broken Rail Failure Checkbox
        broken_rail_check = tk.Checkbutton(
            fail_card,
            text="Broken Rail Failure",
            variable=self.failure_rail_var,
            command=lambda: self.prompt_and_activate_broken_rail(),
            bg="lightblue",
            font=("Arial", 10)
        )
        broken_rail_check.pack(pady=5)

        # Power Failure Checkbox
        power_check = tk.Checkbutton(
            fail_card,
            text="Power Failure",
            variable=self.failure_power_var,
            command=lambda: self.prompt_and_activate_power(),
            bg="lightblue",
            font=("Arial", 10)
        )
        power_check.pack(pady=5)
        fail_card.pack(fill="x", pady=10)

        # ============================================================
        # PLC Upload Section (moved from right side)
        # ============================================================
        plc_card = self.make_card(parent, "PLC Upload")
        
        tk.Label(
            plc_card,
            text="Upload Track Data file\n(.png, .csv, .txt, .xlsx)",
            font=("Arial", 9),
            bg='white',
            fg='gray',
            justify="center"
        ).pack(pady=5)

        ttk.Button(
            plc_card,
            text="Choose File",
            command=self.file_manager.upload_track_file,
            width=18
        ).pack(pady=5, padx=10)

        self.file_status_label = tk.Label(
            plc_card,
            text="No file selected",
            font=("Arial", 9),
            bg='white',
            fg='gray'
        )
        self.file_status_label.pack(pady=3)

        self.history_label = tk.Label(
            plc_card,
            text="Last upload: Never",
            font=("Arial", 8),
            bg='white',
            fg='darkgray'
        )
        self.history_label.pack(pady=3)
        
        plc_card.pack(fill="x", pady=10)


    def switch_line_data(self):
        """Switch between Red Line and Green Line data"""
        selected = self.selected_line.get()
        print(f"[UI] Switching to {selected}")
        
        # Get the sheet name and image file based on selection
        if selected == "Red Line":
            sheet_name = "Red Line"
            image_file = "RedLineOcc.png"
        else:  # Green Line
            sheet_name = "Green Line"
            image_file = "GreenLineOcc.png"
        
        # Load data from the selected sheet using file_manager
        try:
            # Use the file_manager's auto_load_green_line method with the sheet_name parameter
            loaded = self.file_manager.auto_load_green_line(sheet_name=sheet_name)
            
            if loaded:
                print(f"[UI] ✅ {selected} data successfully loaded.")
                
                # Update the track diagram image
                try:
                    # Store the current image file for future resizes
                    self.current_image_file = image_file
                    
                    # Update the background image
                    self.update_background_image()
                except Exception as e:
                    print(f"⚠️ Could not load {image_file}: {e}")
                
                # Repopulate infrastructure sets for the new line
                self._populate_infrastructure_sets()
                
                # Reinitialize bidirectional directions for the new line
                self._initialize_bidirectional_directions()
                
                # Rebuild the bidirectional controls UI
                if hasattr(self, 'bidir_frame') and hasattr(self, 'bidir_controls'):
                    # Clear existing controls (keep the title label)
                    for widget in self.bidir_frame.winfo_children():
                        # Only destroy Frame widgets (control rows), not the title Label
                        if isinstance(widget, tk.Frame):
                            widget.destroy()
                    
                    # Clear the controls dictionary
                    self.bidir_controls.clear()
                    
                    # Recreate controls for the new line
                    for group_name in self.data_manager.bidirectional_directions.keys():
                        self.create_bidirectional_control(self.bidir_frame, group_name)
                    
                    print(f"[UI] ✅ Rebuilt bidirectional controls for {selected}")
                
                # Refresh the tables to show the new data
                self.refresh_track_data_table()
                self.refresh_track_system_table()
                
                # Update station boarding data
                self.update_station_boarding_data()
                
                # Reinitialize station ticket sales
                self._initialize_station_ticket_sales()
                
                print(f"[UI] ✅ Successfully switched to {selected}")
                
            else:
                print(f"[UI] ❌ Failed to load {selected} data.")
                
        except Exception as e:
            print(f"[UI] ❌ Error switching to {selected}: {e}")
            import traceback
            traceback.print_exc()




    def refresh_track_data_table(self):
        """Refresh the Track and Station Data table."""
        if not hasattr(self, 'tree'):
            return
            
        # Clear existing rows
        self.tree.delete(*self.tree.get_children())
        
        
        # Repopulate ALL blocks (removed infrastructure filter to match populate_track_view)
        for b in self.data_manager.blocks:
            self.tree.insert(
                "",
                "end",
                values=(
                    b.block_number,
                    f"{b.grade}%",
                    f"{b.elevation} m",
                    f"{b.length} m",
                    f"{b.speed_limit} km/h",
                ),
            )
        
        # print("[UI] Track Data table refreshed")
    
    def refresh_track_system_table(self):
        """Refresh the Track Elements table."""
        self.update_track_system_table()
        # print("[UI] Track System table refreshed")


    # ============================================================
    # Add these methods to handle block occupancy
    # ============================================================

    def update_train_info(self, event):
        idx = self.train_combo.current()
        train_name = self.train_combo.get()
        
        occ = self.data_manager.train_occupancy[idx]
        spd = self.data_manager.commanded_speed[idx]
        auth = self.data_manager.commanded_authority[idx]
        
        # DEBUG: Show what we're reading
        print(f"[DEBUG] update_train_info called for {train_name} at index {idx}:")
        print(f"  Occupancy: {occ}")
        print(f"  Commanded Speed: {spd}")
        print(f"  Commanded Authority: {auth}")
        print(f"  Array sizes: active_trains={len(self.data_manager.active_trains)}, "
              f"commanded_speed={len(self.data_manager.commanded_speed)}, "
              f"commanded_authority={len(self.data_manager.commanded_authority)}")
        
        self.train_info.config(
            text=f"Occupancy: {occ} People\nCommanded Speed: {spd} m/s\nCommanded Authority: {auth} blocks"
        )
        
        
    # ---------------- Center Panel ----------------
    def create_center_panel(self, parent):
        # Create card for center panel with fixed height
        card = self.make_card(parent)
        card.pack(fill="both", expand=True)
        card.config(height=500)  # fixed height to prevent shrinking
        card.pack_propagate(False)

        # NO NOTEBOOK/TABS - Just use the card directly as diagram frame
        self.diagram_frame = card
        
        # Build track diagram (using the existing method that uses self.diagram_frame)
        self.build_track_diagram()

        # ADD PLC PANEL - place it in the top-right corner
        plc_panel1 = self.create_PLCupload_panel(card)
        plc_panel1.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # COMMENTED OUT - Tab 2: Block/Station Occupancy
        # frame2 = tk.Frame(notebook, bg="white")
        # notebook.add(frame2, text="Block and Station Occupancy")

        # # --- Add Red and Green Line image to tab 2 ---
        # try:
        #     bg_img2 = Image.open("Red and Green Line.png").resize((550, 450), Image.LANCZOS)
        #     self.block_view_bg = ImageTk.PhotoImage(bg_img2)
        #     self.block_canvas = tk.Canvas(frame2, bg="white", height=450, width=550, highlightthickness=0)
        #     self.block_canvas.pack(fill="x", padx=10, pady=10)
        #     self.block_canvas.create_image(0, 0, image=self.block_view_bg, anchor="nw")
        #     self.block_canvas.config(scrollregion=self.block_canvas.bbox("all"))
        #     
        #     # Initialize train items for the center panel occupancy tab
        #     self.train_items_center = []
        #     
        # except Exception as e:
        #     print("⚠️ Could not load Red and Green Line.png for Block/Station tab:", e)
        #     self.block_canvas = tk.Canvas(frame2, bg="white", height=450, width=550)
        #     self.block_canvas.pack(fill="x", padx=10, pady=10)
        #     self.train_items_center = []

        # # ADD PLC PANEL TO TAB 2 - place it in the top-right corner
        # plc_panel2 = self.create_PLCupload_panel(frame2)
        # plc_panel2.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)


    def create_track_system_table(self, parent):
        """Creates a side panel showing Switches, Signals, and Heaters in a live table."""
        card = self.make_card(parent, "Track Signals, Switches, Crossings, and Heaters")
        card.pack(side="right", fill="y", padx=10, pady=10)

        # Create and style the Treeview
        self.track_sys_tree = ttk.Treeview(
            card,
            columns=("Block", "Switches", "Lights", "Railroad Crossings", "Heaters"),
            show="headings",
            height=15
        )
        self.track_sys_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Define column headings
        for col in ("Block", "Switches", "Lights", "Railroad Crossings", "Heaters"):
            self.track_sys_tree.heading(col, text=col)
            self.track_sys_tree.column(col, anchor="center", width=110)

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(card, orient="vertical", command=self.track_sys_tree.yview)
        self.track_sys_tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # Populate for the first time
        self.update_track_system_table()

    def sort_track_data_table(self, column):
        """Sort Track and Station Data table by the clicked column."""
        # Toggle sort direction if same column clicked again
        if self.track_data_sort_column == column:
            self.track_data_sort_reverse = not self.track_data_sort_reverse
        else:
            self.track_data_sort_column = column
            self.track_data_sort_reverse = False
        
        # Get all current rows
        rows = [(self.tree.item(child)["values"], child) for child in self.tree.get_children()]
        
        # Determine column index
        col_index = self.columns_track.index(column)
        
        # Custom sort function
        def sort_key(item):
            val = item[0][col_index]
            # Remove units and convert to numbers for numeric columns
            if column == "Block":
                return int(val)
            elif column in ("Grade", "Elevation", "Length", "Speed Limit"):
                # Extract numeric value (remove % or m or km/h)
                num_str = ''.join(c for c in str(val).split()[0] if c.isdigit() or c == '.' or c == '-')
                return float(num_str) if num_str else 0
            else:
                return str(val)
        
        # Sort rows
        rows.sort(key=sort_key, reverse=self.track_data_sort_reverse)
        
        # Rearrange items in the tree
        for index, (values, child) in enumerate(rows):
            self.tree.move(child, '', index)
        
        # Update column heading to show sort direction
        for col in self.columns_track:
            if col == column:
                arrow = " ↓" if self.track_data_sort_reverse else " ↑"
                self.tree.heading(col, text=f"{col}{arrow}")
            else:
                self.tree.heading(col, text=col)


    def sort_track_system_table(self, column):
        """Sort Track Elements table by the clicked column."""
        # Toggle sort direction if same column clicked again
        if self.track_system_sort_column == column:
            self.track_system_sort_reverse = not self.track_system_sort_reverse
        else:
            self.track_system_sort_column = column
            self.track_system_sort_reverse = False
        
        # Refresh table with new sort order
        self.update_track_system_table()
        
        # Update column heading to show sort direction
        columns = ("Block", "Switches", "Lights", "Crossings", "Heaters")
        for col in columns:
            if col == column:
                arrow = " ↓" if self.track_system_sort_reverse else " ↑"
                self.track_sys_tree.heading(col, text=f"{col}{arrow}")
            else:
                self.track_sys_tree.heading(col, text=col)


    def apply_track_system_sort(self, rows, column, reverse):
        """Apply sorting to track system table rows."""
        # Map column name to index
        columns = ("Block", "Switches", "Lights", "Crossings", "Heaters")
        col_index = columns.index(column)
        
        # Custom sort key function
        def sort_key(row):
            val = row[col_index]
            
            if column == "Block":
                return int(val)
            
            elif column == "Switches":
                # Sort: Left < Right < N/A
                if val == "N/A":
                    return 2
                elif val == "Left":
                    return 0
                else:  # Right
                    return 1
            
            elif column == "Lights":
                # Sort by the signal state: N/A < Red < Yellow < Green < Super Green
                if val == "N/A":
                    return -1
                elif "Red" in val:  # Handles "Red" and "Red (NO POWER)"
                    return 0
                elif val == "Yellow":
                    return 1
                elif val == "Green":
                    return 2
                elif val == "Super Green":
                    return 3
                else:
                    return 0  # Unknown defaults to Red
            
            elif column == "Crossings":
                # Sort: N/A < Inactive < Active
                if val == "N/A":
                    return 0
                elif val == "Inactive":
                    return 1
                else:  # Active
                    return 2
            
            elif column == "Heaters":
                # Sort by status first (Off < On), then by working state (Broken < Working)
                # N/A comes first
                if val == "N/A":
                    return (0, 0)
                parts = val.split("/")
                status = 0 if parts[0] == "Off" else 1
                working = 0 if parts[1] == "Broken" else 1
                return (status, working)
            
            return str(val)
        
        # Sort and return
        return sorted(rows, key=sort_key, reverse=reverse)
    
    def populate_track_view(self):
        """Populate the table with track block data, preserving scroll position."""
        # Check if we need to create the table or if we're switching from station view
        needs_recreation = False
        
        if not hasattr(self, 'tree'):
            needs_recreation = True
        elif not hasattr(self, '_current_view') or self._current_view != 'track':
            # Switching from station view to track view - need to recreate
            needs_recreation = True
        
        if needs_recreation:
            # Clear existing track tab content
            for widget in self.track_tab.winfo_children():
                widget.destroy()
            
            # Create fresh table frame
            self.table_frame = tk.Frame(self.track_tab, bg="white")
            self.table_frame.pack(fill="both", expand=True)
            
            # Create the tree with track columns
            self.tree = ttk.Treeview(self.table_frame, columns=self.columns_track, show="headings")
            self.tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            for col in self.columns_track:
                self.tree.heading(col, text=col, command=lambda c=col: self.sort_track_data_table(c))
                self.tree.column(col, anchor="center", width=110)
            
            # Mark that we're now in track view
            self._current_view = 'track'
        else:
            # Table already exists for track view - just clear rows
            for item in self.tree.get_children():
                self.tree.delete(item)
        
        # Populate ALL blocks (removed infrastructure filter)
        for b in self.data_manager.blocks:
            self.tree.insert(
                "",
                "end",
                values=(
                    b.block_number,
                    f"{b.grade}%",
                    f"{b.elevation} m",
                    f"{b.length} m",
                    f"{b.speed_limit} km/h",
                ),
            )


    def populate_station_view(self):
        """Populate the table with station data, preserving scroll position."""
        # Check if we need to create the table or if we're switching from track view
        needs_recreation = False
        
        if not hasattr(self, 'tree'):
            needs_recreation = True
        elif not hasattr(self, '_current_view') or self._current_view != 'station':
            # Switching from track view to station view - need to recreate
            needs_recreation = True
        
        if needs_recreation:
            # Clear existing station tab content
            for widget in self.station_tab.winfo_children():
                widget.destroy()
            
            # Create fresh table frame in station tab
            station_table_frame = tk.Frame(self.station_tab, bg="white")
            station_table_frame.pack(fill="both", expand=True)
            
            # Create the tree with station columns
            self.tree = ttk.Treeview(station_table_frame, columns=self.columns_station, show="headings")
            self.tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            for col in self.columns_station:
                self.tree.heading(col, text=col, command=lambda c=col: self.sort_track_data_table(c))
                self.tree.column(col, anchor="center", width=110)
            
            # Mark that we're now in station view
            self._current_view = 'station'
        else:
            # Table already exists for station view - just clear rows
            for item in self.tree.get_children():
                self.tree.delete(item)
        
        # Consolidate station data by station name
        # Group blocks by station name
        station_dict = {}
        for block_num, station_name in self.data_manager.station_location:
            if station_name not in station_dict:
                station_dict[station_name] = []
            station_dict[station_name].append(block_num)
        
        # Populate consolidated station data
        for station_name, block_numbers in sorted(station_dict.items()):
            # Format block numbers as "block1, block2" if multiple
            if len(block_numbers) == 1:
                block_display = str(block_numbers[0])
            else:
                block_display = ", ".join(str(b) for b in sorted(block_numbers))
            
            # Sum up tickets, boarding, and disembarking across all blocks for this station
            total_tickets = 0
            total_boarding = 0
            total_disembarking = 0
            
            for block_num in block_numbers:
                idx = block_num - 1
                total_tickets += int(self.data_manager.ticket_sales[idx])
                total_boarding += int(self.data_manager.passengers_boarding[idx])
                total_disembarking += int(self.data_manager.passengers_disembarking[idx])
            
            self.tree.insert(
                "",
                "end",
                values=(
                    block_display,
                    station_name,
                    f"{total_tickets} Tickets",
                    f"{total_boarding} Boarding",
                    f"{total_disembarking} Leaving",
                ),
            )


    def on_view_tab_change(self, event):
        """Handle switching between Track View and Station View tabs."""
        tab = self.view_tabs.tab(self.view_tabs.select(), "text")
        self.view_mode.set("track" if tab == "Track View" else "station")
        
        # Update the bottom table based on selected view
        if self.view_mode.get() == "station":
            self.populate_station_view()
        else:
            self.populate_track_view()

    # ---------------- Bottom Table ----------------
    def create_bottom_table(self, parent):
        """Creates the bottom section with Track and Station Data on the left 
        and Track Elements on the right."""
        container = tk.Frame(parent, bg="navy")
        container.pack(fill="both", expand=True)

        self.columns_station = ("Block", "Station Name", "Tickets Sold", "Boarding", "Disembarking")

        # --- Left side: Track and Station Data table ---
        left_card = self.make_card(container, "Track and Station Data")
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

        left_card.config(width=550)  # Set fixed width
        left_card.pack_propagate(False)  # Prevent resizing based on content

        # Add tabs INSIDE the Track and Station Data card
        self.view_mode = tk.StringVar(value="track")
        self.view_tabs = ttk.Notebook(left_card)
        
        # Track view tab
        self.track_tab = tk.Frame(self.view_tabs, bg="white")
        self.view_tabs.add(self.track_tab, text="Track View")
        
        # Station view tab
        self.station_tab = tk.Frame(self.view_tabs, bg="white")
        self.view_tabs.add(self.station_tab, text="Station View")
        
        self.view_tabs.pack(fill="both", expand=True, padx=5, pady=5)
        self.view_tabs.bind("<<NotebookTabChanged>>", self.on_view_tab_change)

        # Create table frame inside the track tab
        self.table_frame = tk.Frame(self.track_tab, bg="white")
        self.table_frame.pack(fill="both", expand=True)

        # Define columns (you can add Infrastructure column if desired)
        self.columns_track = ("Block", "Grade", "Elevation", "Length", "Speed Limit")
        self.tree = ttk.Treeview(self.table_frame, columns=self.columns_track, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in self.columns_track:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_track_data_table(c))
            self.tree.column(col, anchor="center", width=110)

        # --- Filter and populate only infrastructure blocks ---
        infra_map = getattr(self.data_manager, "infrastructure_data", {})
        allowed_keywords = ["STATION", "SWITCH", "RAILWAY CROSSING", "CROSSING"]

        # Clear any existing rows (in case of reload)
        self.tree.delete(*self.tree.get_children())

        for b in self.data_manager.blocks:
            infra = str(infra_map.get(b.block_number, "")).upper()
            if any(keyword in infra for keyword in allowed_keywords):
                heater_display = (
                    f"{'On' if self.heater_manager.is_heater_on(b) else 'Off'}/"
                    f"{'Working' if self.heater_manager.is_heater_working(b) else 'Broken'}"
                )

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        b.block_number,
                        f"{b.grade}%",
                        f"{b.elevation} m",
                        f"{b.length} m",
                        f"{b.speed_limit} km/h",
                        heater_display,
                    ),
                )

        # --- Right side: Track Elements table ---
        right_card = self.make_card(container, "Track Elements")
        right_card.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.track_sys_tree = ttk.Treeview(
            right_card,
            columns=("Block", "Switches", "Lights", "Crossings", "Heaters"),
            show="headings",
            height=15
        )
        self.track_sys_tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in ("Block", "Switches", "Lights", "Crossings", "Heaters"):
            self.track_sys_tree.heading(col, text=col, command=lambda c=col: self.sort_track_system_table(c))
            self.track_sys_tree.column(col, anchor="center", width=110)

        vsb = ttk.Scrollbar(right_card, orient="vertical", command=self.track_sys_tree.yview)
        self.track_sys_tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # Populate initial Track System table
        self.update_track_system_table()

    def show_station_view(self):
        """Display station data with Red and Green Line image and dynamic train positions."""
        
        # --- Configure columns for station view ---
        self.tree.config(columns=self.columns_station)
        for col in self.columns_station:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110)
        
        # --- Clear existing rows ---
        self.tree.delete(*self.tree.get_children())
        
        # --- Populate station data ---
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            self.tree.insert(
                "",
                "end",
                values=(
                    block_num,
                    station_name,
                    f"{int(self.data_manager.ticket_sales[idx])} Tickets",
                    f"{int(self.data_manager.passengers_boarding[idx])} Boarding",
                    f"{int(self.data_manager.passengers_disembarking[idx])} Leaving",
                ),
            )

        # --- Only create the canvas and visualization once ---
        if not hasattr(self, "block_canvas"):
            # Create visualization components (your existing code here)
            self.block_frame = tk.Frame(self.station_tab, bg="white")
            self.block_frame.pack(fill="both", expand=True)

            try:
                image_file = "GreenLineOcc.png" if hasattr(self, "selected_line") and self.selected_line.get() == "Green Line" else ("RedLineOcc.png" if hasattr(self, "selected_line") and self.selected_line.get() == "Red Line" else "GreenLineOcc.png")
                blue_line_img = Image.open(image_file).resize((550, 450), Image.LANCZOS)
                self.block_bg_img = ImageTk.PhotoImage(blue_line_img)
                self.block_canvas = tk.Canvas(self.block_frame, bg="white", height=450, width=550, highlightthickness=0)
                self.block_canvas.pack(fill="x", padx=10, pady=10)
                self.block_canvas.create_image(0, 0, image=self.block_bg_img, anchor="nw")
                self.block_canvas.config(scrollregion=self.block_canvas.bbox("all"))
            except Exception as e:
                print("⚠️ Could not load Red and Green Line.png for occupancy view:", e)
                self.block_canvas = tk.Canvas(self.block_frame, bg="white", height=450, width=550)
                self.block_canvas.pack(fill="x", padx=10, pady=10)

            # Load Train Image
            if not hasattr(self, "train_icon"):
                try:
                    train_img = Image.open("Train_Right.png").resize((40, 40), Image.LANCZOS)
                    self.train_icon = ImageTk.PhotoImage(train_img)
                except Exception as e:
                    print("⚠️ Could not load Train_Right.png:", e)
                    self.train_icon = None

            # Define block positions
            self.block_positions_occupancy = {
                1: (335, 240), 
                2: (400, 270), 
                3: (480, 110), 
                4: (335, 240), 
                5: (400, 270),  
                6: (480, 110), 
                7: (480, 320), 
                8: (480, 110),  
                9: (480, 320),  
                10: (300, 400),  
                11: (480, 320), 
                12: (300, 400), 
                13: (300, 400), 
                14: (300, 400),  
                15: (600, 400),  
            }

            # Initialize train items
            self.train_items_block_canvas = []

        # --- Draw trains on occupancy canvas ---
        self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_block_canvas)

    def draw_trains(self, canvas, items_list):
        """Draw trains on the given canvas using block occupancy data."""
        if not self.train_icon:
            print("❌ No train icon available")
            return
        if canvas is None:
            print("❌ No canvas available")
            return
        if items_list is None:
            print("❌ No items_list available")
            return

        # Remove previous train images
        for item in items_list:
            canvas.delete(item)
        items_list.clear()

        # print("🔍 === Checking Block Occupancy ===")
        occupied_blocks = []
        
        # Check all blocks for occupancy
        for i, block in enumerate(self.data_manager.blocks):
            block_num = i + 1
            occupancy_value = getattr(block, 'occupancy', 0)
            if occupancy_value != 0:
                occupied_blocks.append(block_num)
                # print(f"   Block {block_num}: OCCUPIED (value: {occupancy_value})")
        
        # print(f"   Found {len(occupied_blocks)} occupied blocks: {occupied_blocks}")
        
        trains_drawn = 0
        # Draw trains for occupied blocks
        for block_num in occupied_blocks:
            coords = self.block_positions_occupancy.get(block_num)
            if coords:
                x, y = coords
                item = canvas.create_image(x, y, image=self.train_icon, anchor="center")
                items_list.append(item)
                trains_drawn += 1
                # print(f"   🚂 Drawing train at block {block_num}, coordinates: {coords}")
            else:
                print(f"   ❌ Block {block_num} occupied but no coordinates available")

        # print(f"🎯 Total trains drawn: {trains_drawn}")
        # print("=====================================")

    # ---------------- Create canvas, load images, initial draw (replace your build_track_diagram) ----------------
    def build_track_diagram(self):
        # Container for the diagram and PLC upload
        diagram_container = tk.Frame(self.diagram_frame, bg="white")
        diagram_container.pack(fill="both", expand=True)

        # Canvas inside left side of container - remove fixed height to allow expansion
        self.track_canvas = tk.Canvas(diagram_container, bg="white")
        self.track_canvas.pack(side="left", fill="both", expand=True)

        # Load train icon once
        self.train_icon = None
        try:
            img = Image.open("Train_Right.png").resize((40, 40), Image.LANCZOS)
            self.train_icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[WARN] Could not load Train_Right.png: {e}")


        # Background image
        try:
            image_file = "GreenLineOcc.png" if hasattr(self, "selected_line") and self.selected_line.get() == "Green Line" else ("RedLineOcc.png" if hasattr(self, "selected_line") and self.selected_line.get() == "Red Line" else "GreenLineOcc.png")
            
            # Store the current image file for resize events
            self.current_image_file = image_file
            
            # Delay initial load to allow PLC panel to render first (so we can measure it)
            self.after(100, self.update_background_image)
            
            # Bind resize event to update image size
            self.track_canvas.bind("<Configure>", lambda e: self.on_canvas_resize(e))
            
            # Bind click event to place red dots and print coordinates
            self.track_canvas.bind("<Button-1>", self.on_canvas_click)
            
            # Bind right-click to clear all red dots
            self.track_canvas.bind("<Button-3>", self.clear_red_dots)
            
            # Store red dot items for potential clearing later
            self.red_dots = []
            self.red_dot_positions = []
            
            # Define block marker positions for Green Line (blocks 1-150)
            self.block_marker_positions = {
                1: (478, 21),
                2: (486, 29),
                3: (491, 40),
                4: (502, 58),
                5: (513, 66),
                6: (531, 70),
                # Blocks 7-16: adjusting by +115 instead of +265 (shifted 150 left)
                7: (438 + 115, 67),   # 553
                8: (458 + 115, 57),   # 573
                9: (462 + 115, 36),   # 577
                10: (434 + 115, 24),  # 549
                11: (403 + 115, 17),  # 518
                12: (376 + 115, 15),  # 491
                13: (327 + 115, 14),  # 442
                14: (318 + 115, 13),  # 433
                15: (309 + 115, 15),  # 424
                16: (302 + 115, 14),  # 417
                # Blocks 17-28: same +115 compensation
                17: (271 + 115, 17),  # 386
                18: (259 + 115, 22),  # 374
                19: (249 + 115, 32),  # 364
                20: (243 + 115, 45),  # 358
                21: (244 + 115, 70),  # 359
                22: (244 + 115, 76),  # 359
                23: (243 + 115, 82),  # 358
                24: (243 + 115, 91),  # 358
                25: (244 + 115, 99),  # 359
                26: (242 + 115, 106), # 357
                27: (243 + 115, 112), # 358
                28: (244 + 115, 117), # 359
                # Blocks 29-57: +5 compensation (moved 10 left from +15)
                29: (360 + 5, 138),  # 365
                30: (359 + 5, 144),  # 364
                31: (359 + 5, 151),  # 364
                32: (360 + 5, 158),  # 365
                33: (361 + 5, 179),  # 366
                34: (365 + 5, 191),  # 370
                35: (374 + 5, 202),  # 379
                36: (398 + 5, 210),  # 403
                37: (404 + 5, 210),  # 409
                38: (410 + 5, 210),  # 415
                39: (415 + 5, 210),  # 420
                40: (421 + 5, 211),  # 426
                41: (427 + 5, 210),  # 432
                42: (433 + 5, 211),  # 438
                43: (439 + 5, 211),  # 444
                44: (447 + 5, 210),  # 452
                45: (454 + 5, 211),  # 459
                46: (460 + 5, 211),  # 465
                47: (467 + 5, 210),  # 472
                48: (473 + 5, 211),  # 478
                49: (477 + 5, 210),  # 482
                50: (485 + 5, 211),  # 490
                51: (496 + 5, 211),  # 501
                52: (502 + 5, 211),  # 507
                53: (509 + 5, 209),  # 514
                54: (516 + 5, 212),  # 521
                55: (528 + 5, 212),  # 533
                56: (540 + 5, 209),  # 545
                57: (551 + 5, 209),  # 556
                # Blocks 58-62: Updated coordinates
                58: (602, 213),
                59: (614, 217),
                60: (625, 228),
                61: (636, 241),
                62: (644, 257),
                # Blocks 63-76: +122 compensation (moved 3 left from +125)
                63: (531 + 122, 280),  # 653
                64: (531 + 122, 296),  # 653
                65: (530 + 122, 314),  # 652
                66: (530 + 122, 334),  # 652
                67: (530 + 122, 352),  # 652
                68: (530 + 122, 372),  # 652
                69: (531 + 122, 412),  # 653
                70: (525 + 122, 430),  # 647
                71: (518 + 122, 451),  # 640
                72: (506 + 122, 466),  # 628
                73: (491 + 122, 478),  # 613
                74: (456 + 122, 484),  # 578
                75: (425 + 122, 484),  # 547
                76: (400 + 122, 482),  # 522
                # Blocks 77-104: +1 compensation (moved 2 right from -1) - PERFECT!
                77: (477 + 1, 481),  # 478
                78: (464 + 1, 482),  # 465
                79: (454 + 1, 484),  # 455
                80: (446 + 1, 483),  # 447
                81: (438 + 1, 483),  # 439
                82: (430 + 1, 482),  # 431
                83: (424 + 1, 481),  # 425
                84: (415 + 1, 484),  # 416
                85: (408 + 1, 483),  # 409
                86: (379 + 1, 483),  # 380
                87: (368 + 1, 482),  # 369
                88: (358 + 1, 483),  # 359
                89: (337 + 1, 482),  # 338
                90: (328 + 1, 471),  # 329
                91: (320 + 1, 453),  # 321
                92: (322 + 1, 433),  # 323
                93: (325 + 1, 419),  # 326
                94: (330 + 1, 409),  # 331
                95: (346 + 1, 404),  # 347
                96: (358 + 1, 416),  # 359
                97: (362 + 1, 432),  # 363
                98: (367 + 1, 451),  # 368
                99: (367 + 1, 463),  # 368
                100: (375 + 1, 471), # 376
                101: (496 + 1, 468), # 497
                102: (518 + 1, 450), # 519
                103: (530 + 1, 452), # 531
                104: (543 + 1, 453), # 544
                # Blocks 105-150: +118 compensation (moved 2 right from +116) - PERFECT!
                105: (452 + 118, 452), # 570
                106: (472 + 118, 444), # 590
                107: (488 + 118, 431), # 606
                108: (499 + 118, 415), # 617
                109: (505 + 118, 397), # 623
                110: (506 + 118, 367), # 624
                111: (504 + 118, 358), # 622
                112: (505 + 118, 351), # 623
                113: (505 + 118, 342), # 623
                114: (506 + 118, 334), # 624
                115: (507 + 118, 327), # 625
                116: (506 + 118, 317), # 624
                117: (505 + 118, 291), # 623
                118: (499 + 118, 274), # 617
                119: (486 + 118, 254), # 604
                120: (469 + 118, 245), # 587
                121: (450 + 118, 238), # 568
                122: (427 + 118, 238), # 545
                123: (422 + 118, 237), # 540
                124: (416 + 118, 236), # 534
                125: (409 + 118, 237), # 527
                126: (403 + 118, 236), # 521
                127: (397 + 118, 236), # 515
                128: (390 + 118, 235), # 508
                129: (385 + 118, 235), # 503
                130: (377 + 118, 235), # 495
                131: (370 + 118, 235), # 488
                132: (361 + 118, 235), # 479
                133: (356 + 118, 237), # 474
                134: (347 + 118, 237), # 465
                135: (340 + 118, 236), # 458
                136: (334 + 118, 235), # 452
                137: (327 + 118, 237), # 445
                138: (318 + 118, 237), # 436
                139: (313 + 118, 237), # 431
                140: (302 + 118, 237), # 420
                141: (294 + 118, 237), # 412
                142: (280 + 118, 237), # 398
                143: (272 + 118, 236), # 390
                144: (249 + 118, 236), # 367
                145: (232 + 118, 230), # 350
                146: (221 + 118, 219), # 339
                147: (219 + 118, 197), # 337
                148: (219 + 118, 188), # 337
                149: (219 + 118, 177), # 337
                150: (227 + 118, 152), # 345
            }
            
            # Define block marker positions for Red Line (blocks 1-76 for now)
            self.block_marker_positions_red = {
                1: (556, 125),
                2: (566, 122),
                3: (575, 119),
                4: (581, 95),
                5: (587, 87),
                6: (599, 81),
                7: (628, 80),
                8: (643, 86),
                9: (659, 94),
                10: (652, 126),
                11: (638, 129),
                12: (621, 132),
                13: (582, 132),
                14: (565, 133),
                15: (549, 133),
                16: (531, 132),
                17: (523, 131),
                18: (518, 132),
                19: (513, 133),
                20: (510, 133),
                21: (487, 135),
                22: (478, 139),
                23: (469, 145),
                24: (467, 172),
                25: (468, 179),
                26: (468, 187),
                27: (468, 193),
                28: (466, 199),
                29: (467, 205),
                30: (467, 212),
                31: (466, 219),
                32: (466, 229),
                33: (466, 233),
                34: (466, 240),
                35: (468, 246),
                36: (466, 250),
                37: (466, 256),
                38: (467, 265),
                39: (467, 270),
                40: (467, 276),
                41: (467, 283),
                42: (467, 288),
                43: (469, 299),
                44: (467, 306),
                45: (467, 315),
                46: (467, 348),
                47: (455, 366),
                48: (435, 380),
                49: (404, 383),
                50: (396, 383),
                51: (389, 383),
                52: (381, 383),
                53: (370, 383),
                54: (364, 383),
                55: (330, 379),
                56: (313, 362),
                57: (301, 340),
                58: (303, 310),
                59: (310, 297),
                60: (320, 284),
                61: (345, 292),
                62: (351, 318),
                63: (355, 341),
                64: (359, 367),
                65: (366, 373),
                66: (373, 374),
                67: (455, 318),
                68: (441, 301),
                69: (440, 296),
                70: (443, 288),
                71: (455, 274),
                72: (454, 225),
                73: (442, 211),
                74: (440, 206),
                75: (441, 200),
                76: (454, 186),
            }
            
            # Manual offset correction (adjust if markers are still misaligned)
            # Negative values move markers left/up, positive values move right/down
            self.marker_offset_correction_x = -265  # Move 265 pixels to the left
            self.marker_offset_correction_y = 0     # No vertical adjustment needed
            
            # Store block marker items (dots or train icons)
            self.block_markers = {}
            
            # Draw initial block markers after image loads
            self.after(200, self.draw_block_markers)
        except Exception as e:
            print("⚠️ Could not load background Red and Green Line.png:", e)

        # Load icon images once and store persistently to prevent garbage collection
        def load_icon(path, size=(32, 32)):
            key = (path, size)
            if key not in self.icon_images:
                img = Image.open(path).resize(size, Image.LANCZOS)
                self.icon_images[key] = ImageTk.PhotoImage(img)
            return self.icon_images[key]

        self.icon_images = {}
        self.icons = {
            "crossing_on": load_icon("Crossing_On.png", (64, 64)),
            "crossing_off": load_icon("Crossing_Off.png", (64, 64)),
            "lever_left": load_icon("Lever_Left.png", (32,32)),
            "lever_right": load_icon("Lever_Right.png", (32, 32)),
        }

        # Load train icon once
        self.train_icon = None
        try:
            img = Image.open("Train_Right.png").resize((40, 40), Image.LANCZOS)
            self.train_icon = ImageTk.PhotoImage(img)
            print("✅ Train icon loaded successfully")
        except Exception as e:
            print(f"❌ Could not load Train_Right.png: {e}")

        # where we will keep canvas item ids for icons (so we can update/delete them)
        self.icon_item_ids = {"crossing": {}, "switch": {}}

        # Define block -> (x, y) coordinates (adjust to your diagram)
        self.block_positions = {
            4: (333, 240),   # Crossing (example coordinates)
            5: (410, 270),   # Switch
            6: (480, 108),   # Traffic Light
            11: (480, 315),   # Traffic Light
        }

        # Draw initial icons
        # self.diagram_drawer.draw_track_icons()

        def load_resized_image(path, size=(32, 32)):
            """Helper to load and resize an image once."""
            key = (path, size)
            if key not in self.icon_images:
                try:
                    img = Image.open(path).resize(size, Image.LANCZOS)
                    self.icon_images[key] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"⚠️ Failed to load {path}: {e}")
                    return None
            return self.icon_images.get(key)

    def _populate_infrastructure_sets(self):
        """Populate switch_blocks, crossing_blocks, and station_blocks from loaded Excel data"""
        # Clear existing sets
        self.switch_blocks.clear()
        self.crossing_blocks.clear()
        self.station_blocks.clear()
        
        # Get infrastructure data from data manager
        infra_map = getattr(self.data_manager, "infrastructure_data", {})
        
        print("[UI] Populating infrastructure sets from Excel data...")
        
        for block_num, infrastructure in infra_map.items():
            infrastructure_upper = str(infrastructure).upper()
            
            # Check for switches
            if "SWITCH" in infrastructure_upper:
                self.switch_blocks.add(block_num)
                print(f"  🔀 Found switch at block {block_num}")
                
                # Initialize switch direction for this block
                if 1 <= block_num <= len(self.data_manager.blocks):
                    block = self.data_manager.blocks[block_num - 1]
                    if not hasattr(block, 'switch_direction'):
                        block.switch_direction = 'normal'  # Default direction
                    # Also initialize in switch_states dictionary
                    self.switch_states[block_num] = getattr(block, 'switch_direction', 'normal')
            
            # Check for crossings
            if "CROSSING" in infrastructure_upper:
                self.crossing_blocks.add(block_num)
                print(f"  🚧 Found crossing at block {block_num}")
            
            # Check for stations
            if "STATION" in infrastructure_upper:
                self.station_blocks.add(block_num)
                print(f"  🚉 Found station at block {block_num}")
        
        print(f"[UI] Infrastructure summary:")
        print(f"  Switches: {sorted(self.switch_blocks)}")
        print(f"  Crossings: {sorted(self.crossing_blocks)}")
        print(f"  Stations: {sorted(self.station_blocks)}")
        print(f"  Signals (hardcoded): {sorted(self.light_states)}")

    def start_temperature_update_loop(self):
        """Start periodic temperature updates (every 1 second)"""
        try:
            if hasattr(self, 'heater_manager'):
                # Update all temperatures and heater states
                self.heater_manager.update_all_temperatures()
                
                # The refresh_ui method will handle updating the display
                # No need to call it separately here since it's already on a timer
                
        except Exception as e:
            print(f"⚠️ Temperature update error: {e}")
        
        # Schedule next update in 1000ms (1 second)
        self.after(1000, self.start_temperature_update_loop)

    def _initialize_bidirectional_directions(self):
        """Initialize bidirectional block directions based on the current line (Green or Red)."""
        # Determine which line is currently selected
        current_line = self.selected_line.get() if hasattr(self, 'selected_line') else "Green Line"
        
        if current_line == "Red Line":
            # Red Line bidirectional blocks
            self.data_manager.bidirectional_directions = {
                "Blocks 1-15": 0,
                "Blocks 16-27": 0,
                "Blocks 28-32": 0,
                "Blocks 33-38": 0,
                "Blocks 39-43": 0,
                "Blocks 44-52": 0,
                "Blocks 53-66": 0,
                "Blocks 67-71": 0,
                "Blocks 72-76": 0
            }
            print("[UI] Initialized bidirectional directions for Red Line")
        else:
            # Green Line bidirectional blocks (default)
            self.data_manager.bidirectional_directions = {
                "Blocks 13-28": 0,
                "Blocks 77-85": 0  # N section - bidirectional blocks
            }
            print("[UI] Initialized bidirectional directions for Green Line")

    def _initialize_station_ticket_sales(self):
        """Initialize random ticket sales and boarding/disembarking for all stations."""
        print("🎫 === INITIALIZING STATION DATA ===")
        
        # Ensure arrays are the correct length
        num_blocks = len(self.data_manager.blocks)
        self.data_manager.ticket_sales = [0] * num_blocks
        self.data_manager.passengers_boarding = [0] * num_blocks
        self.data_manager.passengers_disembarking = [0] * num_blocks
        
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            if 0 <= idx < num_blocks:
                # Generate random ticket sales between 0-70
                ticket_count = self.random.randint(0, 70)
                self.data_manager.ticket_sales[idx] = ticket_count
                
                # Generate random boarding count (0 to ticket_sales)
                boarding_count = self.random.randint(0, ticket_count)
                self.data_manager.passengers_boarding[idx] = boarding_count
                
                print(f"   Station {station_name} (Block {block_num}): {ticket_count} tickets, {boarding_count} boarding")
        
        print("   === STATION DATA INITIALIZATION COMPLETE ===\n")
        
        # Send initial ticket sales to CTC
        for block_num, _ in self.data_manager.station_location:
            self.send_station_data_to_ctc(block_num)


    def update_station_ticket_sales(self):
        """Update ticket sales for all stations - called during refresh"""
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            if 0 <= idx < len(self.data_manager.ticket_sales):
                current_tickets = self.data_manager.ticket_sales[idx]
                
                # Only increase if below max
                if current_tickets < 50:
                    # Generate random increase between 0 and 7
                    new_tickets = self.random.randint(0, 7)
                    
                    # Add new tickets but don't exceed max of 50
                    self.data_manager.ticket_sales[idx] = min(current_tickets + new_tickets, 50)
                    
                    if new_tickets > 0:
                        print(f"🎫 {station_name} (Block {block_num}): {current_tickets} → {self.data_manager.ticket_sales[idx]} (+{new_tickets})")

    def update_station_boarding_data(self):
        """Update boarding data for all stations - called during refresh"""
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            if 0 <= idx < len(self.data_manager.ticket_sales):
                current_tickets = self.data_manager.ticket_sales[idx]
                current_boarding = self.data_manager.passengers_boarding[idx]
                
                # If no train is at the station, generate random boarding data
                block = self.data_manager.blocks[idx]
                if getattr(block, 'occupancy', 0) == 0:
                    # Generate new boarding count based on current tickets
                    if current_tickets > 0:
                        new_boarding = self.random.randint(0, min(50, current_tickets))  # Max 50 boarding at once
                        self.data_manager.passengers_boarding[idx] = new_boarding
                    else:
                        self.data_manager.passengers_boarding[idx] = 0

    def create_block_occupancy_panel(self, parent):
        """Create Block Occupancy display panel for center area."""
        occupancy_frame = tk.Frame(parent, bg="white", highlightbackground="#d0d0d0", highlightthickness=1)
        occupancy_frame.pack(fill="x", padx=5, pady=(0, 8))
        
        tk.Label(
            occupancy_frame,
            text="Occupied Blocks",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="black"
        ).pack(pady=(5, 3))
        
        # Create a frame for the list of occupied blocks
        list_frame = tk.Frame(occupancy_frame, bg="white")
        list_frame.pack(fill="x", pady=5, padx=10)
        
        # Create a label to display occupied blocks (will be updated dynamically)
        self.occupied_blocks_label = tk.Label(
            list_frame,
            text="No blocks currently occupied",
            bg="white",
            font=("Arial", 9),
            fg="gray",
            wraplength=200,
            justify="left"
        )
        self.occupied_blocks_label.pack(pady=5)
        
        # Update the occupied blocks display
        self.update_occupied_blocks_display()
        
        return occupancy_frame
    
    def update_occupied_blocks_display(self):
        """Update the display of occupied blocks."""
        print(f"[DEBUG] update_occupied_blocks_display called")
        
        if not hasattr(self, 'occupied_blocks_label'):
            print("[DEBUG] occupied_blocks_label doesn't exist yet")
            return
            
        if not hasattr(self, 'data_manager') or not hasattr(self.data_manager, 'blocks'):
            print("[DEBUG] data_manager or blocks not available")
            return
        
        print(f"[DEBUG] Checking {len(self.data_manager.blocks)} blocks for occupancy")
        occupied = []
        
        # Check all blocks for occupancy
        for i, block in enumerate(self.data_manager.blocks):
            # Initialize occupancy attribute if it doesn't exist
            if not hasattr(block, 'occupancy'):
                block.occupancy = 0
            
            # Special check for block 63
            if i == 62:  # Block 63 is at index 62
                print(f"[DEBUG] Block 63 occupancy value: {block.occupancy}")
            
            if block.occupancy != 0:
                occupied.append(f"Block {i+1}: Train {block.occupancy}")
                print(f"[DEBUG] Found occupied block {i+1} with train {block.occupancy}")
        
        print(f"[DEBUG] Total occupied blocks found: {len(occupied)}")
        print(f"[DEBUG] Occupied list: {occupied}")
        
        if occupied:
            display_text = "\n".join(occupied)
            self.occupied_blocks_label.config(
                text=display_text,
                fg="black"
            )
            print(f"[DEBUG] Updated occupied blocks display with {len(occupied)} blocks")
            print(f"[DEBUG] Display text: {display_text}")
        else:
            self.occupied_blocks_label.config(
                text="No blocks currently occupied",
                fg="gray"
            )
            # print("[DEBUG] Set display to 'No blocks currently occupied'")
        
        # Force UI update
        try:
            self.occupied_blocks_label.update()
            # print("[DEBUG] Forced label update")
        except Exception as e:
            # print(f"[DEBUG] Could not force update: {e}")
            print("")

    def update_switch_display(self):
        """Update the display of switch states in the UI."""
        print(f"[DEBUG] update_switch_display called")
        
        # Update switch status labels if they exist
        if hasattr(self, 'switch_status_labels'):
            for block_num, label in self.switch_status_labels.items():
                if block_num in self.switch_states:
                    direction = self.switch_states[block_num]
                    label.config(text=f"Switch {block_num}: {direction}")
                    print(f"[DEBUG] Updated switch display for block {block_num}: {direction}")
        
        # Update switch blocks in the data manager
        for block_num in self.switch_blocks:
            if 1 <= block_num <= len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_num - 1]
                if hasattr(block, 'switch_direction'):
                    print(f"[DEBUG] Block {block_num} switch direction: {block.switch_direction}")
        
        # Refresh the track data and system tables to show updated switch states
        try:
            self.refresh_track_data_table()
            self.refresh_track_system_table()
            print("[DEBUG] Refreshed tables after switch update")
        except Exception as e:
            print(f"[DEBUG] Could not refresh tables: {e}")


    def create_PLCupload_panel(self, parent):
        """Creates block occupancy, bidirectional controls and terminal panel (PLC upload moved to left panel)."""
        outer_frame = tk.Frame(parent, bg="white")

        # --- BLOCK OCCUPANCY CONTROL (ADDED ABOVE BIDIRECTIONAL) ---
        self.create_block_occupancy_panel(outer_frame)

        # --- BIDIRECTIONAL BLOCK CONTROLS ---
        self.bidir_frame = tk.Frame(outer_frame, bg="white", highlightbackground="#d0d0d0", highlightthickness=1)
        self.bidir_frame.pack(fill="x", padx=5, pady=(0, 8))

        tk.Label(
            self.bidir_frame,
            text="Bidirectional Block Directions",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="black"
        ).pack(pady=(5, 3))

        # Create control widgets for each bidirectional group
        self.bidir_controls = {}
        
        # Use the shared data from TrackDataManager - ensure it exists
        if not hasattr(self.data_manager, 'bidirectional_directions'):
            # Initialize with default data based on current line
            self._initialize_bidirectional_directions()
        
        # Create controls for each group
        for group_name in self.data_manager.bidirectional_directions.keys():
            self.create_bidirectional_control(self.bidir_frame, group_name)

        # --- TERMINAL / EVENT LOG SECTION ---
        terminal_frame = tk.Frame(
            outer_frame,
            bg="white",
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        terminal_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Header row with title on left and Send Outputs button on right
        header_frame = tk.Frame(terminal_frame, bg="white")
        header_frame.pack(fill="x", padx=5, pady=(3, 0))

        tk.Label(
            header_frame,
            text="Event Log / Terminal",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="black"
        ).pack(side="left", anchor="w")

        send_button = ttk.Button(
            header_frame,
            text="Check Outputs",
            command=self.send_outputs
        )
        send_button.pack(side="right", anchor="e", padx=(0, 3))

        # Inner frame holds text box and scrollbar
        term_inner = tk.Frame(terminal_frame, bg="white")
        term_inner.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        terminal = tk.Text(
            term_inner,
            height=8,
            width=30,
            bg="#f5f5f5",
            fg="black",
            font=("Consolas", 9),
            state="disabled",
            wrap="word"
        )
        terminal.pack(side="left", fill="both", expand=True)

        self.terminals.append(terminal)

        scrollbar = ttk.Scrollbar(term_inner, command=terminal.yview)
        scrollbar.pack(side="right", fill="y")
        terminal.config(yscrollcommand=scrollbar.set)

        return outer_frame
    
    
    def create_bidirectional_control(self, parent, group_name):
        """Create a control row with label, status, and toggle button for a bidirectional group"""
        control_frame = tk.Frame(parent, bg="white")
        control_frame.pack(fill="x", pady=3, padx=5)
        
        # Group label
        lbl_group = tk.Label(control_frame, text=f"{group_name}:", width=15, anchor="w", bg="white")
        lbl_group.pack(side="left", padx=(0, 10))
        
        # Direction status
        status_var = tk.StringVar()
        status_lbl = tk.Label(control_frame, textvariable=status_var, width=12, anchor="center", 
                            bg="white", relief="sunken", bd=1)
        status_lbl.pack(side="left", padx=(0, 10))
        
        # Store the status variable for updates
        self.bidir_controls[group_name] = status_var
        
        # Set initial status
        self.update_bidirectional_status(group_name)

    def update_bidirectional_status(self, group_name):
        """Update the status display for a bidirectional group based on switches and signals"""
        if (hasattr(self.data_manager, 'bidirectional_directions') and 
            group_name in self.data_manager.bidirectional_directions and
            group_name in self.bidir_controls):
            
            # Automatically determine direction based on switches and signals
            direction = self.determine_bidirectional_direction(group_name)
            self.data_manager.bidirectional_directions[group_name] = direction
            
            status_text = "← Left" if direction == 0 else "Right →"
            self.bidir_controls[group_name].set(status_text)
    
    def determine_bidirectional_direction(self, group_name):
        """
        Automatically determine the direction for bidirectional blocks based on:
        - Switch positions (if applicable)
        - Traffic light states (green signals indicate allowed direction)
        
        Returns: 0 for left/backwards, 1 for right/forwards
        """
        if not hasattr(self.data_manager, 'blocks') or not self.data_manager.blocks:
            return 0  # Default to left if no data
        
        # Special handling for N section (blocks 77-85)
        if group_name == "Blocks 77-85":
            # Check switch state at block 85
            if len(self.data_manager.blocks) > 84:
                block_85 = self.data_manager.blocks[84]  # Block 85 at index 84
                if hasattr(block_85, 'switch_state'):
                    # When switch is False (Left/Diverging for 100→85→84 route)
                    # Set blocks to face right for backward travel
                    if not block_85.switch_state:
                        return 1  # Right direction for backward travel
                    else:
                        return 0  # Left direction for normal forward travel
        
        # Parse the block range from group name (e.g., "Blocks 1-5" -> [1,2,3,4,5])
        import re
        match = re.match(r"Blocks?\s+(\d+)-(\d+)", group_name)
        if not match:
            return 0  # Default to left if can't parse
        
        start_block = int(match.group(1))
        end_block = int(match.group(2))
        
        # Check switches and signals in the block range
        forward_signals = 0
        backward_signals = 0
        switch_votes_forward = 0
        switch_votes_backward = 0
        
        for block_num in range(start_block, end_block + 1):
            if block_num <= len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_num - 1]
                
                # Check traffic light state
                # State 0 (Red) = no direction allowed
                # State 1 (Yellow) = caution, typically forward
                # State 2 (Green) = clear, forward direction
                # State 3 (Super Green) = high speed forward
                if hasattr(block, 'traffic_light_state'):
                    state = block.traffic_light_state
                    if state in [1, 2, 3]:  # Yellow, Green, or Super Green
                        forward_signals += 1
                    # Note: We could add logic for backward signals if needed
                
                # Check switch positions if this block has a switch
                if hasattr(block, 'switch_state') and block.switch_state is not None:
                    # True/1 = Right/Forward, False/0 = Left/Backward
                    if block.switch_state:
                        switch_votes_forward += 1
                    else:
                        switch_votes_backward += 1
        
        # Determine direction based on signals and switches
        # Priority: Traffic signals > Switch positions
        if forward_signals > backward_signals:
            return 1  # Forward/Right
        elif backward_signals > forward_signals:
            return 0  # Backward/Left
        elif switch_votes_forward > switch_votes_backward:
            return 1  # Forward/Right based on switches
        elif switch_votes_backward > switch_votes_forward:
            return 0  # Backward/Left based on switches
        else:
            # If no clear direction, maintain current or default to left
            return self.data_manager.bidirectional_directions.get(group_name, 0)

    def toggle_bidirectional_direction(self, group_name):
        """Main UI toggle - now just a placeholder since Test UI controls"""
        print(f"ℹ️ Main UI toggle for {group_name} - Test UI is the controller")

    def save_bidirectional_direction(self, group_name):
        """Main UI save - now just a placeholder"""
        print(f"ℹ️ Main UI save for {group_name} - Test UI controls changes")

    def refresh_bidirectional_controls(self):
        """Refresh all bidirectional controls based on current switches and signals"""
        # print("🔄 Refreshing bidirectional controls based on switches and signals")
        if hasattr(self.data_manager, 'bidirectional_directions'):
            for group_name in self.data_manager.bidirectional_directions.keys():
                self.update_bidirectional_status(group_name)
    
    def update_train_movements(self):
        """Update train positions based on actual speed and block lengths."""
        import time
        current_time = time.time()
        
        # Process each active train
        for train_idx, train_id in enumerate(self.data_manager.active_trains):
            if train_idx >= len(self.data_manager.train_locations):
                continue
                
            current_block_num = self.data_manager.train_locations[train_idx]
            if current_block_num == 0:  # Train not on track
                continue
            
            # Get actual speed for this train (m/s)
            actual_speed = self.train_actual_speeds.get(train_id, 0)
            if actual_speed <= 0:
                continue  # Train not moving
            
            # Initialize tracking for this train if needed
            if train_id not in self.train_positions_in_block:
                self.train_positions_in_block[train_id] = 0
                self.last_movement_update[train_id] = current_time
                print(f"[MOVEMENT] Initialized tracking for {train_id} at block {current_block_num}")
            
            # Calculate time elapsed since last update (seconds)
            time_delta = current_time - self.last_movement_update[train_id]
            self.last_movement_update[train_id] = current_time
            
            # Calculate distance traveled (meters)
            distance_traveled = actual_speed * time_delta
            self.train_positions_in_block[train_id] += distance_traveled
            
            # Get block length (meters)
            block_length = self.get_block_length(current_block_num)
            
            # Check if train has traveled the full block length
            if self.train_positions_in_block[train_id] >= block_length:
                # Move to next block
                next_block = self.get_next_block(current_block_num, train_idx)
                
                if next_block and next_block <= len(self.data_manager.blocks):
                    # Clear current block occupancy
                    if current_block_num <= len(self.data_manager.blocks):
                        current_block = self.data_manager.blocks[current_block_num - 1]
                        current_block.occupancy = 0
                        print(f"[MOVEMENT] {train_id} leaving block {current_block_num}")
                    
                    # Set new block occupancy
                    new_block = self.data_manager.blocks[next_block - 1]
                    train_num = int(train_id.split('_')[1]) if '_' in train_id else int(train_id.replace('Train', '').strip())
                    new_block.occupancy = train_num
                    
                    # Update train location
                    self.data_manager.train_locations[train_idx] = next_block
                    
                    # Reset position in new block (account for overflow)
                    overflow = self.train_positions_in_block[train_id] - block_length
                    self.train_positions_in_block[train_id] = overflow
                    
                    print(f"[MOVEMENT] {train_id} entered block {next_block} (speed: {actual_speed:.1f} m/s)")
                    
                    # Send occupancy updates to other modules
                    self.send_block_occupancy_update(current_block_num, 0)
                    self.send_block_occupancy_update(next_block, train_num)
                    
                    # Update the display
                    self.update_occupied_blocks_display()
                else:
                    print(f"[MOVEMENT] {train_id} reached end of authority at block {current_block_num}")
            
        # Schedule next update
        self.after(100, self.update_train_movements)  # Update every 100ms
    
    def get_block_length(self, block_num):
        """Get the length of a block in meters."""
        if block_num <= 0 or block_num > len(self.data_manager.blocks):
            return 50.0  # Default block length
        
        block = self.data_manager.blocks[block_num - 1]
        # Try to get actual block length from block data
        if hasattr(block, 'length'):
            return float(block.length)
        elif hasattr(block, 'block_length'):
            return float(block.block_length)
        else:
            return 50.0  # Default 50 meters if no length data
    
    def get_next_block(self, current_block, train_idx):
        """
        Determine the next block for train movement.
        Rules:
        1. Always go in ascending order (1→2→3→...→150) EXCEPT:
        2. Bidirectional sections allow descending:
           - Block 100 → 85 (entering N section backwards)
           - Block 150 → 28 (loop return)
        3. Switches route based on their state
        """
        # Check commanded authority
        if train_idx < len(self.data_manager.commanded_authority):
            authority = self.data_manager.commanded_authority[train_idx]
            
            # Calculate how many blocks the train has traveled from its starting point
            # For now, use a simple counter (can be enhanced with actual tracking)
            if not hasattr(self, 'train_blocks_traveled'):
                self.train_blocks_traveled = {}
            
            train_id = self.data_manager.active_trains[train_idx]
            if train_id not in self.train_blocks_traveled:
                self.train_blocks_traveled[train_id] = 0
            
            # Check if we've reached authority limit
            if self.train_blocks_traveled[train_id] >= authority:
                print(f"[AUTHORITY] {train_id} has reached authority limit ({authority} blocks)")
                return None  # Stop at authority limit
            
            # Increment blocks traveled
            self.train_blocks_traveled[train_id] += 1
        
        # ============================================================
        # SPECIAL ROUTING RULES - BIDIRECTIONAL AND SWITCHES
        # ============================================================
        
        
        # RULE 1: End of line loop return - Block 150 goes to 28 (per Excel)
        if current_block == 150:
            print(f"[ROUTING] Block 150 M-bM-^FM-^R 28 (Loop return per switch at block 28)")
            return 28  # Always go to 28 from 150
        
        # RULE 1b: Switch at block 28 controls routing from 28
        # Excel shows: SWITCH (28-29; 150-28)
        # Route 1: 28 M-bM-^FM-^R 29 (normal forward)
        # Route 2: 150 M-bM-^FM-^R 28 (loop return, handled above)
        elif current_block == 28:
            if len(self.data_manager.blocks) > 27:
                block_28 = self.data_manager.blocks[27]  # Block 28 at index 27
                if hasattr(block_28, 'switch_state'):
                    if block_28.switch_state:  # True = Normal = To block 29
                        return 29  # Continue forward
                    else:  # False = Reverse = Loop back to 150
                        print(f"[ROUTING] Block 28 M-bM-^FM-^R 150 (Loop back via switch 28)")
                        return 150  # Loop back
            return 29  # Default forward to 29

        # RULE 2: Switch at block 12 (12-13; 1-13)
        # Excel: SWITCH (12-13; 1-13)
        # Normal: 12 → 13 (continue from block 12)
        # Reverse: allows entry from block 1 → 13
        elif current_block == 1:
            # Block 1 can only go to 2 normally, unless there's a switch routing
            # For now, block 1 goes to 2
            return 2
        
        elif current_block == 12:
            if len(self.data_manager.blocks) > 11:
                block_12 = self.data_manager.blocks[11]  # Block 12 at index 11
                if hasattr(block_12, 'switch_state'):
                    if block_12.switch_state:  # True = Normal = 12 → 13
                        return 13  # Normal progression
                    else:  # False = Reverse = allows 1 → 13 (but we're at 12, so still go to 13)
                        return 13  # Still go to 13
            return 13  # Default
        
        # RULE 4: Switch housed at block 58 (Yard access from block 57)
        # Excel: SWITCH TO YARD (57-yard) - switch housed at block 58
        # Position 1: 57 → 58 (continue on main line)
        # Position 2: 57 → yard (block 151)
        elif current_block == 57:
            if len(self.data_manager.blocks) > 57:
                block_58 = self.data_manager.blocks[57]  # Switch housed at block 58 (index 57)
                if hasattr(block_58, 'switch_state'):
                    if block_58.switch_state:  # True = Normal = Continue on main line
                        return 58  # Continue to 58
                    else:  # False = Reverse = Go to yard
                        print(f"[ROUTING] Block 57 → Yard (151) via switch at 58")
                        return 151  # Go to yard (block 151)
            return 58  # Default: continue on main line
        
        # RULE 5: Switch at block 62 (From yard)
        # Excel: SWITCH FROM YARD (Yard-63) - allows entry from yard or from block 62
        # Normal: 62 → 63 (from main line)
        # Reverse: Yard (151) → 63 (from yard)
        elif current_block == 62:
            return 63  # Always go to 63 from block 62
        
        elif current_block == 151:  # Yard
            # From yard, check switch at block 62
            if len(self.data_manager.blocks) > 61:
                block_62 = self.data_manager.blocks[61]  # Block 62 at index 61
                if hasattr(block_62, 'switch_state'):
                    if not block_62.switch_state:  # False = Reverse = Allow yard → 63
                        print(f"[ROUTING] Yard (151) → 63 via switch 62")
                        return 63  # Return from yard to main line
            # Default: stay in yard or error
            return 151  # Stay in yard if switch not set correctly
        
        # RULE 6: Block 76 always goes to 77
        # Switch is housed at block 76 but controls what happens at the junction
        elif current_block == 76:
            return 77  # Always go to 77 first
        
        # RULE 7: Switch at block 77 controlled by switch housed at block 76
        # Excel: SWITCH (76-77; 77-101) - switch housed at block 76
        # Position 1 (76-77): Train continues 76 → 77 → 78 (through N section)
        # Position 2 (77-101): Train goes 76 → 77 → 101 (bypassing N section)
        elif current_block == 77:
            if len(self.data_manager.blocks) > 75:
                block_76 = self.data_manager.blocks[75]  # Switch housed at block 76 (index 75)
                if hasattr(block_76, 'switch_state'):
                    if block_76.switch_state:  # True = Normal = 76-77 path (continue to 78)
                        return 78  # Enter N section
                    else:  # False = Reverse = 77-101 path (bypass N section)
                        print(f"[ROUTING] Block 77 → 101 (Bypassing N section via switch at 76)")
                        return 101  # Skip N section entirely
            return 78  # Default to N section
        
        # RULE 8: Normal progression through N section (78-84)
        elif 78 <= current_block < 85:
            return current_block + 1  # Normal ascending: 78→79→80→81→82→83→84→85
        
        # RULE 8: Switch at block 85-86
        elif current_block == 85:
            if len(self.data_manager.blocks) > 84:
                block_85 = self.data_manager.blocks[84]  # Block 85 at index 84
                if hasattr(block_85, 'switch_state'):
                    if block_85.switch_state:  # True = To block 86
                        return 86  # Normal forward progression
                    else:  # False = Would be for backward entry from 100
                        # But when AT block 85, we always go forward
                        return 86
            return 86  # Default forward to 86
        
        # RULE 9: Normal progression from 86-99
        elif 86 <= current_block <= 99:
            return current_block + 1  # Continue ascending
        
        # RULE 10: Block 100 → 85 (BIDIRECTIONAL backward entry to N section)
        elif current_block == 100:
            # Check if switch at 85 is set for backward entry
            if len(self.data_manager.blocks) > 84:
                block_85 = self.data_manager.blocks[84]  # Block 85 at index 84
                if hasattr(block_85, 'switch_state'):
                    if not block_85.switch_state:  # False = Allow 100→85 backward route
                        print(f"[ROUTING] Block 100 → 85 (BIDIRECTIONAL: Backward entry to N section)")
                        # Mark this train as going backward through N section
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            self.train_directions[train_id] = 'backward_n_section'
                        return 85  # DESCENDING: 100 → 85
                    else:
                        return 101  # Normal ascending to 101
            # Default: continue ascending
            return 101
        
        # RULE 10b: Handle backward traversal through N section (85→84→83→...→77)
        elif current_block in [85, 84, 83, 82, 81, 80, 79, 78, 77]:
            # Check if this train is traversing N section backward
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'backward_n_section':
                    next_block = self.get_next_block_backward_n_section(current_block)
                    if next_block == 101:
                        # Exiting backward traversal, reset to forward
                        self.train_directions[train_id] = 'forward'
                        print(f"[ROUTING] Exiting N section backward traversal at block 77 → 101")
                    elif next_block:
                        print(f"[ROUTING] N section backward: Block {current_block} → {next_block}")
                    return next_block
            
            # Otherwise, use normal rules (which handles forward traversal)
            if current_block == 85:
                # Already handled in RULE 8
                if len(self.data_manager.blocks) > 84:
                    block_85 = self.data_manager.blocks[84]
                    if hasattr(block_85, 'switch_state'):
                        if block_85.switch_state:
                            return 86  # Normal forward
                        else:
                            return 86  # Still go forward when at 85
                return 86
            elif 77 <= current_block < 85:
                return current_block + 1  # Normal forward through N section
        
        # RULE 11: Continue normal progression 101-149
        elif 101 <= current_block <= 149:
            return current_block + 1  # Normal ascending
        
        # ============================================================
        # DEFAULT: NORMAL ASCENDING PROGRESSION
        # ============================================================
        else:
            # Standard ascending order for any other block
            next_block = current_block + 1
            
            # Safety check
            if next_block > 150:
                return 150  # Stay at 150
            
            return next_block
    
    def get_next_block_backward_n_section(self, current_block):
        """
        Handle backward progression through N section (85→84→83→...→77→101).
        This is only used when a train enters from block 100 to block 85.
        """
        if current_block == 85:
            return 84
        elif current_block == 84:
            return 83
        elif current_block == 83:
            return 82
        elif current_block == 82:
            return 81
        elif current_block == 81:
            return 80
        elif current_block == 80:
            return 79
        elif current_block == 79:
            return 78
        elif current_block == 78:
            return 77
        elif current_block == 77:
            # Exit N section backward traversal, continue to 101
            return 101
        else:
            # Should not reach here in backward N section traversal
            return None
    
    def send_block_occupancy_update(self, block_num, occupancy):
        """Send block occupancy update to other modules."""
        try:
            update = {block_num: occupancy}
            
            # Send to Train Model (keep existing format for Train Model)
            self.server.send_to_ui("Train Model", {
                "command": "block_occupancy",
                "value": update
            })
            
            # Send to Track SW (Wayside Controller) in the exact format required
            # Flat structure with track, block, occupied fields
            self.server.send_to_ui("Track SW", {
                'track': 'Green',
                'block': str(block_num),  # Convert to string
                'occupied': str(occupancy)  # Send occupancy value as string (e.g., "0" or "1")
            })
            
            print(f"📤 Sent to Track SW: Block {block_num} {'occupied' if occupancy != 0 else 'unoccupied'}")
            
            # Also send old format for backward compatibility with Track HW
            self.server.send_to_ui("Track HW", {
                "command": "block_occupancy",
                "value": update
            })
            
            # If a train is entering this block, send block info to Train Model
            if occupancy != 0:
                # Find the train
                train_id = f"Train_{occupancy}"
                if block_num <= len(self.data_manager.blocks):
                    block = self.data_manager.blocks[block_num - 1]
                    block_length = self.get_block_length(block_num)
                    
                    # Send block characteristics to Train Model
                    self.server.send_to_ui("Train Model", {
                        "command": "block_info",
                        "train_id": train_id,
                        "block_number": block_num,
                        "block_length": block_length,
                        "speed_limit": getattr(block, 'speed_limit', 70),
                        "grade": getattr(block, 'grade', 0)
                    })
                    

                    # Check for beacon data using BeaconManager
                    if occupancy != 0 and hasattr(self, 'beacon_manager'):
                        if self.beacon_manager.is_station_block(block_num):
                            train_id = f"Train_{occupancy}"
                            beacon_message = self.beacon_manager.format_beacon_message(block_num, train_id)
                            if beacon_message:
                                # Send beacon data to Train Model
                                self.server.send_to_ui("Train Model", beacon_message)
                                print(f"📡 BEACON ACTIVATED at Block {block_num} for {train_id}")
                                print(f"   Next station: {beacon_message['beacon_info']['next_station_name']}")
                                print(f"   Distance: {beacon_message['beacon_info']['distance_to_next_station']}m")
                                # Send to Train SW for train controller
                                self.server.send_to_ui("Train SW", beacon_message)
                                print(f"📡 Beacon data sent to Train SW")
                                # Report to CTC
                                self.server.send_to_ui("CTC", {
                                    "command": "beacon_activated",
                                    "block": block_num,
                                    "train_id": train_id,
                                    "station_info": beacon_message['beacon_info']
                                })
                                print(f"📡 Beacon activation reported to CTC")
            print(f"📤 Sent occupancy update: Block {block_num} = {occupancy}")
            
        except Exception as e:
            print(f"⚠️ Error sending occupancy update: {e}")
    
    def is_beacon_active(self, block):
        """Check if a beacon is active for a given block."""
        # For now, beacons are always active at stations
        if hasattr(block, 'block_number'):
            return block.block_number in self.station_blocks
        return False
    
    def log_switch_change(self, block_num, from_block, to_block, state, direction):
        """Log switch state changes with descriptive information"""
        # Get the actual route info
        route_info = self.get_switch_destination(block_num, state)
        if isinstance(route_info, tuple) and len(route_info) == 2:
            route_from, route_to = route_info
            if route_from == "Yard":
                direction_text = f"Yard to {route_to}"
            elif route_to == "Yard":
                direction_text = f"{route_from} to Yard"
            else:
                direction_text = f"{route_from} to {route_to}"
        else:
            direction_text = f"To {route_info}"
        
        path_description = f"from Block {from_block} to Block {to_block}"
        
        # Add more context if this is a known switch
        if block_num in self.switch_blocks:
            if abs(to_block - from_block) == 1:
                path_type = "main line"
            elif abs(to_block - from_block) > 10:
                path_type = "branch/crossover"
            else:
                path_type = "alternate route"
            
            print(f"🔀 Switch at Block {block_num}: {direction_text} ({path_type})")
            print(f"   Route: {path_description}")
        else:
            print(f"✅ Updated switch at Block {block_num}: {direction_text}")
            print(f"   Route: {path_description}")
        
        # Special handling for switch at block 85
        # When switch routes from 100→85 (state=False), set N section (77-85) to face right
        if block_num == 85 or (from_block == 85 and to_block in [84, 86]):
            if hasattr(self.data_manager, 'bidirectional_directions'):
                if not state:  # Switch set to Left/Diverging (100→85→84 route)
                    # Set blocks 77-85 to face right (1) for backward travel
                    self.data_manager.bidirectional_directions["Blocks 77-85"] = 1
                    print(f"   📍 N Section (Blocks 77-85) set to Right → for backward travel")
                    # Update the display
                    if "Blocks 77-85" in self.bidir_controls:
                        self.bidir_controls["Blocks 77-85"].set("Right →")
                else:  # Switch set to Right/Straight (normal forward route)
                    # Set blocks 77-85 to face left (0) for normal forward travel
                    self.data_manager.bidirectional_directions["Blocks 77-85"] = 0
                    print(f"   📍 N Section (Blocks 77-85) set to ← Left for forward travel")
                    # Update the display
                    if "Blocks 77-85" in self.bidir_controls:
                        self.bidir_controls["Blocks 77-85"].set("← Left")
        
        # Log to terminal if available
        for terminal in self.terminals:
            terminal.config(state="normal")
            terminal.insert("end", f"Switch {block_num}: {direction} ({from_block}→{to_block})\n")
            terminal.see("end")
            terminal.config(state="disabled")
    
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
    
    def on_bidir_table_click(self, event):
        """Handle clicks on the bidirectional table to toggle directions"""
        item = self.bidir_tree.identify_row(event.y)
        if item:
            column = self.bidir_tree.identify_column(event.x)
            # Only respond to clicks anywhere in the row (not just direction column)
            # This makes it easier to toggle
            values = self.bidir_tree.item(item, "values")
            if values and len(values) > 0:
                group_name = values[0]
                print(f"🖱️ Clicked on {group_name} in column {column}")
                self.toggle_bidirectional_direction(group_name)

    def debug_bidirectional_table(self):
        """Debug method to check the current state of the bidirectional table"""
        if hasattr(self, 'bidir_tree'):
            print("=== BIDIRECTIONAL TABLE DEBUG ===")
            print(f"Treeview exists: {self.bidir_tree is not None}")
            print(f"Number of rows: {len(self.bidir_tree.get_children())}")
            
            for item in self.bidir_tree.get_children():
                values = self.bidir_tree.item(item, "values")
                print(f"  Row: {values}")
            
            print(f"Data manager state: {getattr(self.data_manager, 'bidirectional_directions', 'NO DATA')}")
            print("=================================")


    def send_outputs(self):
        """Only refresh terminals when Send Outputs button is clicked"""
        print("🔄 Manual terminal refresh triggered by Send Outputs button")
        for terminal in self.terminals:
            self._send_outputs_to_terminal(terminal)

    def _send_outputs_to_terminal(self, terminal):
        """Send outputs to a specific terminal widget."""
        dm = self.data_manager

        # Clear the terminal first
        terminal.config(state="normal")
        terminal.delete(1.0, "end")
        
        print("🔄 Updating terminal with system data...")
        
        # Ticket Sales and Boarding/Disembarking
        terminal.insert("end", "=== STATION DATA ===\n")
        for block_num, station_name in dm.station_location:  # ← Removed enumerate
            block_idx = block_num - 1  # ← Convert to zero-based index
            terminal.insert("end", f"Station {station_name} (Block {block_num}):\n")
            terminal.insert("end", f"  Tickets Sold: {int(dm.ticket_sales[block_idx])}\n")  # ← Use block_idx
            terminal.insert("end", f"  Passengers Boarding: {int(dm.passengers_boarding[block_idx])}\n")  # ← Use block_idx
            terminal.insert("end", f"  Passengers Disembarking: {int(dm.passengers_disembarking[block_idx])}\n\n")  # ← Use block_idx

        # Track Circuit Signals / Occupancy
        terminal.insert("end", "=== BLOCK OCCUPANCY ===\n")
        for block in dm.blocks:
            occupancy = getattr(block, 'occupancy', 0)
            if occupancy != 0:  # Only show occupied blocks
                terminal.insert("end", f"Block {block.block_number}: OCCUPIED (value: {occupancy})\n")
        terminal.insert("end", "\n")

        # Commanded Speed and Authority
        terminal.insert("end", "=== TRAIN COMMANDS ===\n")
        for idx, train_name in enumerate(dm.active_trains):
            speed = dm.commanded_speed[idx]
            auth = dm.commanded_authority[idx]
            terminal.insert("end", f"Train {train_name}:\n")
            terminal.insert("end", f"  Commanded Speed: {speed} m/s\n")
            terminal.insert("end", f"  Commanded Authority: {auth} blocks\n\n")

        # Beacons - updated for 128-bit
        terminal.insert("end", "=== BEACON STATUS ===\n")
        active_beacons = [block for block in dm.blocks if self.is_beacon_active(block)]
        if active_beacons:
            for block in active_beacons:
                hex_string = self.beacon_to_hex(block)
                # Show first 16 bits as sample and full hex
                sample_bits = self.get_beacon_bits(block, 0, 16)
                terminal.insert("end", f"Block {block.block_number}: [{''.join(str(bit) for bit in sample_bits)}...]\n")
                terminal.insert("end", f"           Hex: {hex_string}\n")
        else:
            terminal.insert("end", "No active beacons\n")
        terminal.insert("end", "\n")

        terminal.see("end")
        terminal.config(state="disabled")
        print("✅ Terminal update complete")

    def _log_to_terminal(self, terminal, msg):
        """Append a message to a specific terminal."""
        terminal.insert("end", f"{msg}\n")
        terminal.see("end")
        terminal.config(state="disabled")
    
    def log_message(self, msg):
        """Append a message to the terminal log."""
        self.terminal.config(state="normal")
        self.terminal.insert("end", f"{msg}\n")
        self.terminal.see("end")
        self.terminal.config(state="disabled")

    def PLCupload_file(self):
        from tkinter import filedialog
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg"),
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),  # Add CSV support
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Track Data File", filetypes=filetypes)
        
        if filename:
            file_extension = filename.lower().split('.')[-1]
            
            # Handle image files
            if file_extension in ['png', 'jpg', 'jpeg']:
                self.handle_image_upload(filename)
            
            # Handle data files (including CSV)
            elif file_extension in ['xlsx', 'xls', 'csv', 'txt']:
                self.handle_data_upload(filename)
            
            else:
                self.log_to_all_terminals(f"[ERROR] Unsupported file type: {file_extension}")
                
        else:
            self.log_to_all_terminals("[WARN] File selection canceled.")

    def handle_image_upload(self, filename):
        """Handle PNG/JPG upload - replace track diagram background and clear all icons"""
        try:
            # Load and resize the new image
            new_img = Image.open(filename).resize((550, 450), Image.LANCZOS)
            self.track_bg = ImageTk.PhotoImage(new_img)
            
            # Clear EVERYTHING from the canvas first
            self.track_canvas.delete("all")  # This removes all canvas items
            
            # Add the new background image
            self.track_canvas.create_image(0, 0, image=self.track_bg, anchor="nw")
            self.track_canvas.config(scrollregion=self.track_canvas.bbox("all"))
            
            # Clear all track icons from tracking
            self.clear_all_track_icons()
            
            # Clear train items from track diagram
            if hasattr(self, "train_items"):
                self.train_items.clear()  # Clear the list, items already deleted by delete("all")
            
            # Clear any other canvas item lists
            if hasattr(self, "train_items_center"):
                self.train_items_center.clear()
            if hasattr(self, "train_items_block_canvas"):
                self.train_items_block_canvas.clear()
            
            self.log_to_all_terminals(f"[SUCCESS] Track diagram updated with: {filename.split('/')[-1]}")
            print(f"✅ Track diagram background updated with: {filename}")
            print("🧹 ALL track icons, trains, and canvas items cleared from diagram")
            
        except Exception as e:
            self.log_to_all_terminals(f"[ERROR] Failed to load image: {str(e)}")
            print(f"❌ Error loading image: {e}")

    def update_background_image(self):
        """Update the background image to fit current canvas size while maintaining aspect ratio"""
        try:
            # Get current canvas dimensions
            canvas_width = self.track_canvas.winfo_width()
            canvas_height = self.track_canvas.winfo_height()
            
            # Use minimum dimensions if canvas hasn't been drawn yet
            if canvas_width <= 1:
                canvas_width = 800  # Default width
            if canvas_height <= 1:
                canvas_height = 600  # Default height
            
            # Try to get actual PLC panel width if it exists and is visible
            reserved_right_space = 0
            if hasattr(self, 'diagram_frame'):
                # Get all children placed on the diagram frame
                for child in self.diagram_frame.winfo_children():
                    # Check if this is the PLC panel (placed widget)
                    place_info = child.place_info()
                    if place_info and place_info.get('anchor') == 'ne':
                        # This is the right-side panel
                        panel_width = child.winfo_width()
                        if panel_width > 1:  # Panel has been rendered
                            reserved_right_space = panel_width + 20  # Add some padding
                            break
            
            # Fallback to default if we couldn't measure the panel
            if reserved_right_space <= 1:
                reserved_right_space = 280  # Increased default to be safe
            
            available_width = max(canvas_width - reserved_right_space, 400)
            available_height = canvas_height
            
            # Determine which image file to use
            if hasattr(self, 'current_image_file'):
                image_file = self.current_image_file
            else:
                image_file = "GreenLineOcc.png" if hasattr(self, "selected_line") and self.selected_line.get() == "Green Line" else "GreenLineOcc.png"
            
            # Load original image to get its aspect ratio
            original_img = Image.open(image_file)
            original_width, original_height = original_img.size
            original_aspect = original_width / original_height
            
            # Calculate dimensions that fit within available space while maintaining aspect ratio
            if available_width / available_height > original_aspect:
                # Height is the limiting factor
                new_height = available_height
                new_width = int(new_height * original_aspect)
            else:
                # Width is the limiting factor
                new_width = available_width
                new_height = int(new_width / original_aspect)
            
            # Resize image maintaining aspect ratio
            bg_img = original_img.resize((new_width, new_height), Image.LANCZOS)
            self.track_bg = ImageTk.PhotoImage(bg_img)
            
            # Clear and redraw canvas
            self.track_canvas.delete("all")
            
            # Center the image in the available space (excluding reserved right space)
            x_offset = (available_width - new_width) // 2
            y_offset = (available_height - new_height) // 2
            
            # Store offsets for block marker positioning
            self.image_x_offset = x_offset
            self.image_y_offset = y_offset
            
            self.track_canvas.create_image(x_offset, y_offset, image=self.track_bg, anchor="nw")
            self.track_canvas.config(scrollregion=self.track_canvas.bbox("all"))
            
            # Redraw block markers (black dots or train icons)
            if hasattr(self, 'draw_block_markers'):
                self.draw_block_markers()
            
            # Redraw red dots if any exist (they were deleted with "all")
            if hasattr(self, 'red_dot_positions') and self.red_dot_positions:
                self.red_dots = []
                dot_radius = 3
                for x, y in self.red_dot_positions:
                    dot = self.track_canvas.create_oval(
                        x - dot_radius, y - dot_radius,
                        x + dot_radius, y + dot_radius,
                        fill='red',
                        outline='darkred',
                        width=1
                    )
                    self.red_dots.append(dot)
            
            print(f"[UI] ✅ Background image resized to {new_width}x{new_height}")
            print(f"    Original: {original_width}x{original_height} (aspect: {original_aspect:.4f})")
            print(f"    New aspect: {new_width/new_height:.4f} (difference: {abs(original_aspect - new_width/new_height):.6f})")
            print(f"    Canvas: {canvas_width}x{canvas_height}, Reserved: {reserved_right_space}px, Available: {available_width}x{available_height}")
            print(f"    Image offset: ({x_offset}, {y_offset})")
            
        except Exception as e:
            print(f"⚠️ Could not update background image: {e}")
            import traceback
            traceback.print_exc()

    def on_canvas_resize(self, event):
        """Handle canvas resize events to update background image"""
        # Debounce resize events - only update after canvas stops resizing
        if hasattr(self, '_resize_timer'):
            self.after_cancel(self._resize_timer)
        
        # Schedule update after 100ms of no resize events
        self._resize_timer = self.after(100, self.update_background_image)

    def on_canvas_click(self, event):
        """Handle canvas click events - place red dot and print coordinates"""
        x, y = event.x, event.y
        
        # Create a red dot (small circle) at the click location
        dot_radius = 3
        dot = self.track_canvas.create_oval(
            x - dot_radius, y - dot_radius,
            x + dot_radius, y + dot_radius,
            fill='red',
            outline='darkred',
            width=1
        )
        
        # Store the dot item ID
        if not hasattr(self, 'red_dots'):
            self.red_dots = []
        self.red_dots.append(dot)
        
        # Store the position for persistence across image reloads
        if not hasattr(self, 'red_dot_positions'):
            self.red_dot_positions = []
        self.red_dot_positions.append((x, y))
        
        # Print coordinates to terminal
        print(f"🔴 Clicked at coordinates: ({x}, {y})")
        
        # Also log to UI terminal if available
        if hasattr(self, 'log_to_all_terminals'):
            self.log_to_all_terminals(f"[CLICK] Coordinates: ({x}, {y})")

    def clear_red_dots(self, event=None):
        """Clear all red dots from canvas (triggered by right-click)"""
        # Delete all dot items
        if hasattr(self, 'red_dots'):
            for dot in self.red_dots:
                self.track_canvas.delete(dot)
            self.red_dots = []
        
        # Clear stored positions
        if hasattr(self, 'red_dot_positions'):
            self.red_dot_positions = []
        
        print("🧹 Cleared all red dots")
        
        # Also log to UI terminal if available
        if hasattr(self, 'log_to_all_terminals'):
            self.log_to_all_terminals("[CLEAR] All red dots cleared")

    def draw_block_markers(self):
        """Draw block markers (black dots or train icons) based on occupancy status"""
        # Determine which position dictionary to use based on selected line
        if hasattr(self, 'selected_line'):
            current_line = self.selected_line.get()
            if current_line == "Red Line":
                if not hasattr(self, 'block_marker_positions_red'):
                    return
                positions = self.block_marker_positions_red
            else:  # Green Line
                if not hasattr(self, 'block_marker_positions'):
                    return
                positions = self.block_marker_positions
        else:
            # Default to Green Line if no selection yet
            if not hasattr(self, 'block_marker_positions'):
                return
            positions = self.block_marker_positions
        
        # Get the current image offset (if image has been loaded and centered)
        x_offset = getattr(self, 'image_x_offset', 0)
        y_offset = getattr(self, 'image_y_offset', 0)
        
        # Get manual correction offsets
        x_correction = getattr(self, 'marker_offset_correction_x', 0)
        y_correction = getattr(self, 'marker_offset_correction_y', 0)
        
        # Clear existing markers
        for block_num in list(self.block_markers.keys()):
            if self.block_markers[block_num]:
                self.track_canvas.delete(self.block_markers[block_num])
        
        self.block_markers = {}
        
        # Draw marker for each block
        for block_num, (base_x, base_y) in positions.items():
            # Skip placeholder blocks (coordinates 0,0)
            if base_x == 0 and base_y == 0:
                continue
                
            # Adjust position by image offset AND manual correction
            x = base_x + x_offset + x_correction
            y = base_y + y_offset + y_correction
            
            # Check if block is occupied
            is_occupied = False
            if block_num <= len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_num - 1]
                is_occupied = hasattr(block, 'occupancy') and block.occupancy != 0
            
            if is_occupied and hasattr(self, 'train_icon') and self.train_icon:
                # Draw train icon
                marker = self.track_canvas.create_image(x, y, image=self.train_icon, anchor="center")
            else:
                # Draw black dot
                dot_radius = 4
                marker = self.track_canvas.create_oval(
                    x - dot_radius, y - dot_radius,
                    x + dot_radius, y + dot_radius,
                    fill='black',
                    outline='gray',
                    width=1
                )
            
            self.block_markers[block_num] = marker
        
        line_name = current_line if hasattr(self, 'selected_line') else "Green Line"
        print(f"[MARKERS] Drew {len(self.block_markers)} block markers for {line_name} (offset: {x_offset}, {y_offset}) (correction: {x_correction}, {y_correction})")

    def update_block_marker(self, block_num):
        """Update a single block marker based on its occupancy status"""
        # Determine which position dictionary to use based on selected line
        if hasattr(self, 'selected_line'):
            current_line = self.selected_line.get()
            if current_line == "Red Line":
                if not hasattr(self, 'block_marker_positions_red'):
                    return
                positions = self.block_marker_positions_red
            else:  # Green Line
                if not hasattr(self, 'block_marker_positions'):
                    return
                positions = self.block_marker_positions
        else:
            # Default to Green Line if no selection yet
            if not hasattr(self, 'block_marker_positions'):
                return
            positions = self.block_marker_positions
        
        if block_num not in positions:
            return
        
        # Get base position and apply image offset
        base_x, base_y = positions[block_num]
        
        # Skip placeholder blocks
        if base_x == 0 and base_y == 0:
            return
            
        x_offset = getattr(self, 'image_x_offset', 0)
        y_offset = getattr(self, 'image_y_offset', 0)
        
        # Get manual correction offsets
        x_correction = getattr(self, 'marker_offset_correction_x', 0)
        y_correction = getattr(self, 'marker_offset_correction_y', 0)
        
        # Apply both offsets and correction
        x = base_x + x_offset + x_correction
        y = base_y + y_offset + y_correction
        
        # Delete existing marker if it exists
        if block_num in self.block_markers and self.block_markers[block_num]:
            self.track_canvas.delete(self.block_markers[block_num])
        
        # Check if block is occupied
        is_occupied = False
        if block_num <= len(self.data_manager.blocks):
            block = self.data_manager.blocks[block_num - 1]
            is_occupied = hasattr(block, 'occupancy') and block.occupancy != 0
        
        if is_occupied and hasattr(self, 'train_icon') and self.train_icon:
            # Draw train icon
            marker = self.track_canvas.create_image(x, y, image=self.train_icon, anchor="center")
            print(f"[MARKER] Block {block_num} now shows train icon (occupied)")
        else:
            # Draw black dot
            dot_radius = 4
            marker = self.track_canvas.create_oval(
                x - dot_radius, y - dot_radius,
                x + dot_radius, y + dot_radius,
                fill='black',
                outline='gray',
                width=1
            )
            print(f"[MARKER] Block {block_num} now shows black dot (empty)")
        
        self.block_markers[block_num] = marker

    def clear_all_track_icons(self):
        """Completely clear all track icons and reset all tracking"""
        # Reset icon tracking dictionaries
        self.icon_item_ids = {"crossing": {}, "switch": {}, "traffic": {}}
        
        # Clear any stored icon images to free memory
        if hasattr(self, 'icons'):
            self.icons.clear()
        
        # Clear any icon images from the image cache
        if hasattr(self, 'icon_images'):
            self.icon_images.clear()
        
        print("🧹 Completely cleared all track icons and reset all tracking data")

    def process_structured_track_data(self, df, pd):
        """Process the specific CSV/Excel structure and REPLACE default data"""
        try:
            print(f"🔄 Starting data replacement with {len(df)} rows")
            
            # Clear existing station data first
            self.data_manager.station_location = []
            print("🧹 Cleared existing station data")
            
            # Map column names to handle variations
            column_mapping = {
                'block_number': ['Block Number', 'Block_Number', 'BlockNumber', 'Block No'],
                'block_length': ['Block Length (m)', 'Block_Length_m', 'BlockLength', 'Length'],
                'block_grade': ['Block Grade (%)', 'Block_Grade_%', 'Grade', 'BlockGrade'],
                'speed_limit': ['Speed Limit (Km/Hr)', 'Speed_Limit_Km_Hr', 'SpeedLimit', 'Speed'],
                'elevation': ['ELEVATION (M)', 'ELEVATION_M', 'Elevation', 'ELEVATION'],
                'infrastructure': ['Infrastructure', 'Infra', 'Features'],
                'station_side': ['Station Side', 'Station_Side', 'Side']
            }
            
            # Find actual column names in the dataframe
            actual_columns = {}
            for standard_name, possible_names in column_mapping.items():
                for possible_name in possible_names:
                    if possible_name in df.columns:
                        actual_columns[standard_name] = possible_name
                        break
            
            print(f"🔍 Found columns in file: {actual_columns}")
            print(f"📊 DataFrame columns: {list(df.columns)}")
            print(f"📊 First row sample: {df.iloc[0].to_dict() if len(df) > 0 else 'No data'}")
            
            # Reset all blocks to default state first
            self.reset_all_blocks()
            
            # Process each row to REPLACE data
            blocks_updated = 0
            for index, row in df.iterrows():
                # Get block number (handle different formats)
                block_num = None
                if 'block_number' in actual_columns:
                    try:
                        block_num = int(row[actual_columns['block_number']])
                        print(f"📋 Processing block {block_num} from row {index}")
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Could not parse block number from row {index}: {row[actual_columns['block_number']]}")
                        continue
                else:
                    # Try to infer from index or other columns
                    block_num = index + 1  # Default to row index + 1
                    print(f"📋 Inferred block {block_num} from row index {index}")
                
                if block_num and 1 <= block_num <= len(self.data_manager.blocks):
                    block = self.data_manager.blocks[block_num - 1]
                    
                    # REPLACE block length
                    if 'block_length' in actual_columns:
                        try:
                            block.length = float(row[actual_columns['block_length']])
                            print(f"   📏 Length: {block.length}m")
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Could not parse length for block {block_num}: {row[actual_columns['block_length']]}")
                            block.length = 0.0
                    
                    # REPLACE block grade
                    if 'block_grade' in actual_columns:
                        try:
                            block.grade = float(row[actual_columns['block_grade']])
                            print(f"   📈 Grade: {block.grade}%")
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Could not parse grade for block {block_num}: {row[actual_columns['block_grade']]}")
                            block.grade = 0.0
                    
                    # REPLACE speed limit
                    if 'speed_limit' in actual_columns:
                        try:
                            block.speed_limit = float(row[actual_columns['speed_limit']])
                            print(f"   🚄 Speed: {block.speed_limit}km/h")
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Could not parse speed for block {block_num}: {row[actual_columns['speed_limit']]}")
                            block.speed_limit = 0.0
                    
                    # REPLACE elevation
                    if 'elevation' in actual_columns:
                        try:
                            block.elevation = float(row[actual_columns['elevation']])
                            print(f"   🏔️ Elevation: {block.elevation}m")
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Could not parse elevation for block {block_num}: {row[actual_columns['elevation']]}")
                            block.elevation = 0.0
                    
                    # RESET infrastructure flags first
                    block.switch_state = False
                    block.crossing = False
                    
                    # Handle infrastructure (stations, switches, etc.)
                    if 'infrastructure' in actual_columns:
                        infrastructure = str(row[actual_columns['infrastructure']])
                        if pd.notna(infrastructure) and infrastructure != 'nan':
                            self.process_infrastructure(block, infrastructure)
                            print(f"   🏗️ Infrastructure: {infrastructure}")
                    
                    blocks_updated += 1
                    print(f"✅ UPDATED block {block_num}")
            
            print(f"🎯 Successfully updated {blocks_updated} blocks")
            
            # Reset ticket sales and passenger data arrays to match new station data
            self.reset_station_data_arrays()
            
            # Refresh both UIs to show the new data
            self.refresh_all_uis()
            
            self.log_to_all_terminals(f"[SUCCESS] Completely replaced track data with uploaded file - updated {blocks_updated} blocks")
            
        except Exception as e:
            print(f"❌ Error processing structured track data: {e}")
            import traceback
            traceback.print_exc()
            self.log_to_all_terminals(f"[ERROR] Data replacement failed: {str(e)}")

    def reset_all_blocks(self):
        """Reset all blocks to default state before loading new data"""
        for block in self.data_manager.blocks:
            # Reset to default values
            block.length = 0.0
            block.grade = 0.0
            block.elevation = 0.0
            block.speed_limit = 0.0
            block.switch_state = False
            block.crossing = False
            # Keep beacon and heater states as they are hardware-specific
            # block.track_heater = [0, 1]  # Optional: reset heaters too
            # block.beacon = [0] * 128     # Optional: reset beacons too

    def reset_station_data_arrays(self):
        """Reset station data arrays to match the new station configuration"""
        num_blocks = len(self.data_manager.blocks)
        
        # Reset to zero arrays
        self.data_manager.ticket_sales = [0] * num_blocks
        self.data_manager.passengers_boarding = [0] * num_blocks
        self.data_manager.passengers_disembarking = [0] * num_blocks
        
        # Pre-fill default station data for any stations found
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            if 0 <= idx < num_blocks:
                self.data_manager.ticket_sales[idx] = 0
                self.data_manager.passengers_boarding[idx] = 0
                self.data_manager.passengers_disembarking[idx] = 0

    def refresh_all_uis(self):
        """Refresh both Main UI and Test UI to show the new data"""
        # Refresh Main UI components
        self.refresh_ui()
        
        # Force update all tables and displays
        self.update_bottom_table()
        
        # Force redraw track icons
        self.draw_track_icons()
        
        # Refresh Test UI if it exists
        if hasattr(self, 'tester_reference'):
            try:
                self.tester_reference.refresh_block_table()
                self.tester_reference.refresh_station_table()
                self.tester_reference.refresh_diagram_table()
                print("🔄 Refreshed Test UI tables")
            except Exception as e:
                print(f"⚠️ Could not refresh Test UI: {e}")
        
        print("🔄 COMPLETELY refreshed all UIs with new data")
        
        # Debug: Print current block data to verify
        print("🔍 CURRENT BLOCK DATA AFTER UPDATE:")
        for i, block in enumerate(self.data_manager.blocks[:5]):  # Show first 5 blocks
            print(f"   Block {i+1}: Length={block.length}m, Grade={block.grade}%, Speed={block.speed_limit}km/h")

    def process_infrastructure(self, block, infrastructure, pd):
        """Process infrastructure information and REPLACE existing data"""
        try:
            if pd.isna(infrastructure) or infrastructure == '' or infrastructure == 'nan':
                return
            
            infrastructure = str(infrastructure).upper()
            print(f"   🏗️ Processing infrastructure: '{infrastructure}' for block {block.block_number}")
            
            # Handle stations
            if 'STATION' in infrastructure:
                station_name = self.extract_station_name(infrastructure, block)
                if station_name:
                    # Remove any existing station at this block
                    self.data_manager.station_location = [
                        (block_num, name) for block_num, name in self.data_manager.station_location 
                        if block_num != block.block_number
                    ]
                    # Add the new station
                    self.data_manager.station_location.append((block.block_number, station_name))
                    print(f"   🏢 ADDED station '{station_name}' at block {block.block_number}")
            
            # Handle switches - REPLACE switch state
            if 'SWITCH' in infrastructure:
                block.switch_state = True  # Set to right position
                print(f"   🔀 ADDED switch at block {block.block_number}")
            else:
                block.switch_state = False  # Ensure no switch if not specified
            
            # Handle crossings - REPLACE crossing state
            if 'CROSSING' in infrastructure:
                block.crossing = True
                print(f"   🚧 ADDED crossing at block {block.block_number}")
            else:
                block.crossing = False  # Ensure no crossing if not specified
                
        except Exception as e:
            print(f"❌ Error processing infrastructure for block {block.block_number}: {e}")

    def extract_station_name(self, infrastructure_text, block):
        """Extract station name from infrastructure text"""
        try:
            # Example: "STATION; PIONEER" -> "PIONEER"
            parts = str(infrastructure_text).split(';')
            for part in parts:
                clean_part = part.strip()
                if 'STATION' in clean_part.upper():
                    continue  # Skip the station keyword
                if clean_part and clean_part != 'STATION':
                    print(f"   🏢 Extracted station name: '{clean_part}'")
                    return clean_part
            
            # If no clear name, generate one
            generated_name = f"Station {block.block_number}"
            print(f"   🏢 Generated station name: '{generated_name}'")
            return generated_name
        
        except Exception as e:
            print(f"❌ Error extracting station name: {e}")
            return f"Station {block.block_number}"

    def extract_station_name(self, infrastructure_text, block):
        """Extract station name from infrastructure text"""
        try:
            # Example: "STATION; PIONEER" -> "PIONEER"
            parts = infrastructure_text.split(';')
            for part in parts:
                if 'STATION' in part.upper():
                    continue  # Skip the station keyword
                station_name = part.strip()
                if station_name and station_name != 'STATION':
                    return station_name
            
            # If no clear name, generate one
            return f"Station {self.data_manager.blocks.index(block) + 1}"
        
        except Exception as e:
            print(f"❌ Error extracting station name: {e}")
            return f"Station {self.data_manager.blocks.index(block) + 1}"

    def clear_all_track_icons(self):
        """Clear all switches, signals, and crossing icons from track diagram"""
        if hasattr(self, 'icon_item_ids'):
            for icon_type in self.icon_item_ids:
                for block_num, item in self.icon_item_ids[icon_type].items():
                    if isinstance(item, list):
                        for subitem in item:
                            self.track_canvas.delete(subitem)
                    else:
                        self.track_canvas.delete(item)
            
            # Reset the icon tracking dictionary
            self.icon_item_ids = {"crossing": {}, "switch": {}, "traffic": {}}
            
            print("🧹 Cleared all track icons from diagram")

    def log_to_all_terminals(self, message):
        """Log message to all terminal widgets"""
        for terminal in self.terminals:
            terminal.config(state="normal")
            terminal.insert("end", f"{message}\n")
            terminal.see("end")
            terminal.config(state="disabled")

    def create_block_occupancy_panel(self, parent):
        """Create Block Occupancy display panel for center area."""
        occupancy_frame = tk.Frame(parent, bg="white", highlightbackground="#d0d0d0", highlightthickness=1)
        occupancy_frame.pack(fill="x", padx=5, pady=(0, 8))
        
        tk.Label(
            occupancy_frame,
            text="Occupied Blocks",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="black"
        ).pack(pady=(5, 3))
        
        # Create a frame for the list of occupied blocks
        list_frame = tk.Frame(occupancy_frame, bg="white")
        list_frame.pack(fill="x", pady=5, padx=10)
        
        # Create a label to display occupied blocks (will be updated dynamically)
        self.occupied_blocks_label = tk.Label(
            list_frame,
            text="No blocks currently occupied",
            bg="white",
            font=("Arial", 9),
            fg="gray",
            wraplength=200,
            justify="left"
        )
        self.occupied_blocks_label.pack(pady=5)
        
        # Update the occupied blocks display
        self.update_occupied_blocks_display()
        
        return occupancy_frame
    
    def refresh_trains(self):
        # Remove old train icons first
        if hasattr(self, "train_items"):
            for item in self.train_items:
                self.track_canvas.delete(item)
        self.train_items = []

        # Draw new train positions
        if self.train_icon:
            for idx, train_name in enumerate(self.data_manager.active_trains):
                train_block = self.data_manager.train_locations[idx]
                coords = self.block_positions_occupancy.get(train_block)
                if coords:
                    x, y = coords
                    item = self.track_canvas.create_image(x, y, image=self.train_icon, anchor="center")
                    self.train_items.append(item)

    def refresh_all_trains(self):
        """Force refresh trains on all canvases"""
        print("Force refreshing all trains...")
        
        # Track Diagram canvas
        if hasattr(self, "track_canvas") and hasattr(self, "train_items"):
            self.draw_trains(canvas=self.track_canvas, items_list=self.train_items)
        
        # Station Occupancy canvas
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_block_canvas"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_block_canvas)

    def refresh_ui(self):
        # Update environmental temp (if temp_label exists)
        if hasattr(self, 'temp_label'):
            env_temp = getattr(self.data_manager, 'environmental_temp', None)
            if env_temp is not None:
                self.temp_label.config(text=f"Temperature: {env_temp}°F")
            else:
                self.temp_label.config(text="Temperature: --°F")

        # Update occupied blocks display
        self.update_occupied_blocks_display()
        
        # Update block markers on main track diagram (train icons and dots)
        if hasattr(self, 'draw_block_markers'):
            self.draw_block_markers()
        
        # Update bidirectional directions based on switches and signals
        self.refresh_bidirectional_controls()
        
        # Refresh the current view in the bottom table
        if hasattr(self, 'view_mode') and self.view_mode.get() == "station":
            self.populate_station_view()
        elif hasattr(self, 'view_mode') and self.view_mode.get() == "track":
            pass

        # Draw trains on BOTH occupancy canvases
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_block_canvas"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_block_canvas)
        
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_center"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_center)

        # Refresh the right-side Track System table (THIS WILL SHOW HEATER STATUS)
        self.update_track_system_table()

        # Refresh again in 1 second
        self.after(1000, self.refresh_ui)

    def set_heater_state(self, block, is_on, is_working):
        """Set heater state with validation"""
        if not is_working and is_on:
            print(f"⚠️ Cannot turn on heater for block {block.block_number} - heater is not working")
            return False  # Can't turn on a non-working heater
        
        block.track_heater = [1 if is_on else 0, 1 if is_working else 0]
        print(f"🔧 Block {block.block_number} heater: {'ON' if is_on else 'OFF'}, {'WORKING' if is_working else 'BROKEN'}")
        return True

    def toggle_heater(self, block_num):
        """Toggle heater on/off if it's working"""
        block = self.data_manager.blocks[block_num - 1]
        if self.is_heater_working(block):
            new_state = not self.is_heater_on(block)
            self.set_heater_state(block, new_state, True)
        else:
            print(f"❌ Cannot toggle heater for block {block_num} - heater is not working")

    def break_heater(self, block_num):
        """Break the heater (turns it off if it was on)"""
        block = self.data_manager.blocks[block_num - 1]
        was_on = self.is_heater_on(block)
        self.set_heater_state(block, False, False)  # Turn off and break
        if was_on:
            print(f"🔧 Heater broken and turned off for block {block_num}")

    def fix_heater(self, block_num):
        """Fix the heater (doesn't change on/off state)"""
        block = self.data_manager.blocks[block_num - 1]
        is_on = self.is_heater_on(block)
        self.set_heater_state(block, is_on, True)  # Keep current on/off state, set working


    def on_track_circuit_failure_change(self, block_num):
        """Called when track circuit failure checkbox is toggled."""
        if self.failure_train_circuit_var.get():
            # Activate failure
            self.murphy_failures.activate_track_circuit_failure(block_num)
        else:
            # Clear failure if it's a track circuit failure
            if self.murphy_failures.get_failure_status(block_num) == "track_circuit":
                self.murphy_failures.clear_failure(block_num)

    def on_broken_rail_failure_change(self, block_num):
        """Called when broken rail failure checkbox is toggled."""
        if self.failure_rail_var.get():
            # Activate failure
            self.murphy_failures.activate_broken_rail_failure(block_num)
        else:
            # Clear failure if it's a broken rail failure
            if self.murphy_failures.get_failure_status(block_num) == "broken_rail":
                self.murphy_failures.clear_failure(block_num)

    def on_power_failure_change(self, block_num):
        """Called when power failure checkbox is toggled."""
        if self.failure_power_var.get():
            # Activate failure
            self.murphy_failures.activate_power_failure(block_num)
        else:
            # Clear failure if it's a power failure
            if self.murphy_failures.get_failure_status(block_num) == "power":
                self.murphy_failures.clear_failure(block_num)


    # 5. Add helper method to get selected block (if you don't have one already):

    def get_selected_block_number(self):
        """
        Get the currently selected block number.
        Update this method based on how you select blocks in your UI.
        """
        # Option 1: If you have a block selection entry field
        if hasattr(self, 'block_select_var'):
            try:
                return int(self.block_select_var.get())
            except (ValueError, AttributeError):
                return 1  # Default to block 1
        
        # Option 2: If you have a selected block from clicking the diagram
        if hasattr(self, 'selected_block'):
            return self.selected_block
        
        # Option 3: Default
        return 1

    def get_switch_destination(self, block_number, switch_state):
        """
        Determine which blocks a switch connects based on block number and switch state.
        Returns a tuple of (from_block, to_block) for display.
        Based on the track diagram switches:
        - Block 12: SWITCH (12-13, 1-13)
        - Block 28: SWITCH (28-29, 150-28)
        - Block 57: SWITCH (57-Yard)
        - Block 62: SWITCH FROM YARD (Yard-62)
        - Block 76: SWITCH (76-77, 77-101)
        - Block 85: SWITCH (85-86, 100-85)
        """
        # Handle switch at block 12 (12-13, 1-13)
        if block_number == 12:
            if switch_state:  # True = main route
                return (12, 13)
            else:  # False = from block 1
                return (1, 13)
        
        # Handle switch at block 28 (28-29, 150-28)
        elif block_number == 28:
            if switch_state:  # True = main route
                return (28, 29)
            else:  # False = from block 150
                return (150, 28)
        
        # Handle switch housed at block 58 (controls traffic from 57 to yard)
        # Excel: SWITCH TO YARD (57-yard)
        elif block_number == 58:
            if switch_state:  # True = continue on main line
                return (57, 58)
            else:  # False = to yard
                return (57, "Yard")
        
        # Handle switch housed at block 62 (FROM YARD)
        elif block_number == 62:
            if switch_state:  # True = from main line
                return (62, 63)
            else:  # False = from yard
                return ("Yard", 63)
        
        # Handle switch housed at block 76 (controls junction: 76-77-78 or 76-77-101)
        # Excel: SWITCH (76-77; 77-101)
        elif block_number == 76:
            if switch_state:  # True = 76-77 path (continues to 78)
                return (76, 77)  # Shows 76→77, then train continues to 78
            else:  # False = 77-101 path (bypasses N section)
                return (77, 101)  # Shows the bypass route from 77→101
        
        # Handle switch at block 85 (85-86, 100-85)
        elif block_number == 85:
            if switch_state:  # True = main route forward
                return (85, 86)
            else:  # False = backward route (for trains from 100)
                return (100, 85)
        
        # Handle reverse direction for bidirectional switches
        elif block_number == 1:
            # Coming from block 1, can go to 2 or jump to 13 via switch
            if switch_state:
                return (1, 2)  # Normal route
            else:
                return (1, 13)  # Via switch at 12
        
        elif block_number == 100:
            # Block 100 can go to 85 via switch
            if not switch_state:  # When switch at 85 is set for 100->85
                return (100, 85)
            else:
                return (100, 101)  # Normal route
        
        elif block_number == 150:
            # Block 150 can loop back to 1 or go to 28 via switch
            if switch_state:
                return (150, 1)  # Normal loop back
            else:
                return (150, 28)  # Via switch
        
        # For any other blocks, default to next sequential block
        return (block_number, block_number + 1)


    # 6. Update your update_track_system_table to show failure status:

    def update_track_system_table(self):
        """Refresh the Switch/Signal/Crossing/Heater table with failure status."""
        if not hasattr(self, "track_sys_tree"):
            return

        self.track_sys_tree.delete(*self.track_sys_tree.get_children())
        infra_map = getattr(self.data_manager, "infrastructure_data", {})
        rows = []
        
        for b in self.data_manager.blocks:
            has_switch = b.block_number in self.switch_blocks or getattr(b, "switch_state", False)
            has_signal = b.block_number in self.light_states or getattr(b, "light_state", None) is not None
            has_crossing = b.block_number in self.crossing_blocks or getattr(b, "crossing", False)
            
            has_station = False
            infra = str(infra_map.get(b.block_number, "")).upper()
            if "STATION" in infra:
                has_station = True
            if any(block_num == b.block_number for block_num, _ in self.data_manager.station_location):
                has_station = True
            
            if has_switch or has_signal or has_crossing or has_station:
                # Check for power failure
                has_power = self.murphy_failures.has_power(b.block_number)
                
                # Switch state
                if has_switch:
                    current_switch_state = getattr(b, "switch_state", False)
                    route_info = self.get_switch_destination(b.block_number, current_switch_state)
                    # route_info is now a tuple (from_block, to_block)
                    if isinstance(route_info, tuple) and len(route_info) == 2:
                        from_block, to_block = route_info
                        # Format the display string
                        if from_block == "Yard":
                            switch_state = f"Yard to {to_block}"
                        elif to_block == "Yard":
                            switch_state = f"{from_block} to Yard"
                        else:
                            switch_state = f"{from_block} to {to_block}"
                    else:
                        # Fallback for any unexpected format
                        switch_state = f"To {route_info}"
                else:
                    switch_state = "--"
                
                # Signal state (off if power failure)
                if has_signal:
                    if not has_power:
                        signal_display = "Red (NO POWER)"
                    else:
                        signal_state = getattr(b, "traffic_light_state", 0)
                        # Convert state to color name based on two-bit representation
                        # bit0 = signal_state & 1, bit1 = signal_state & 2
                        # 00 (0) = Red, 01 (1) = Yellow, 10 (2) = Green, 11 (3) = Super Green
                        if signal_state == 0:
                            signal_display = "Red"
                        elif signal_state == 1:
                            signal_display = "Yellow"
                        elif signal_state == 2:
                            signal_display = "Green"
                        elif signal_state == 3:
                            signal_display = "Super Green"
                        else:
                            signal_display = f"Unknown ({signal_state})"
                else:
                    signal_display = "--"
                
                # Crossing state (inactive if power failure)
                if has_crossing:
                    if not has_power:
                        crossing_state = "NO POWER"
                    else:
                        crossing_state = "Active" if getattr(b, "crossing", False) else "Inactive"
                else:
                    crossing_state = "--"
                
                # Heater status
                if has_station and hasattr(self, 'heater_manager'):
                    heater_on = self.heater_manager.is_heater_on(b)
                    heater_working = self.heater_manager.is_heater_working(b)
                    block_temp_f = self.heater_manager.get_block_temperature(b.block_number)
                    
                    heater_status = "ON" if heater_on else "OFF"
                    heater_display = f"{heater_status} ({block_temp_f:.1f}°F)"
                else:
                    heater_display = "--"
                
                # Failure status
                failure_status = self.murphy_failures.get_failure_display_text(b.block_number)

                rows.append((b.block_number, switch_state, signal_display, crossing_state, 
                            heater_display, failure_status))
        
        if hasattr(self, 'track_system_sort_column') and self.track_system_sort_column:
            rows = self.apply_track_system_sort(rows, self.track_system_sort_column, 
                                            self.track_system_sort_reverse)
        
        for row in rows:
            self.track_sys_tree.insert("", "end", values=row)


    def _initialize_station_ticket_sales(self):
        """Initialize random ticket sales for all stations (0-70)."""
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            # Generate random ticket sales between 0-70
            self.data_manager.ticket_sales[idx] = self.random.randint(0, 70)
            print(f"🎫 Station {station_name} (Block {block_num}): {self.data_manager.ticket_sales[idx]} tickets waiting")
        
        # Send initial ticket sales to CTC
        for block_num, _ in self.data_manager.station_location:
            self.send_station_data_to_ctc(block_num)


    def handle_train_arrival_at_station(self, block_num):
        """
        Handle when a train arrives at a station.
        - Generates random passengers boarding (0 to ticket_sales)
        - Sends boarding count to Train Model
        - Resets ticket sales to new random value (0-70)
        - Sends updated station data to CTC
        
        Args:
            block_num (int): Block number where train arrived
        """
        # Check if this block is a station
        station_info = next((s for s in self.data_manager.station_location if s[0] == block_num), None)
        if not station_info:
            print(f"   ⚠️ Block {block_num} is not a station!")
            return  # Not a station
        
        station_name = station_info[1]
        idx = block_num - 1
        
        print(f"\n   📊 BEFORE:")
        print(f"      Ticket sales length: {len(self.data_manager.ticket_sales)}")
        print(f"      Passengers boarding length: {len(self.data_manager.passengers_boarding)}")
        print(f"      Block index: {idx}")
        
        # Get current ticket sales (passengers waiting)
        tickets_waiting = self.data_manager.ticket_sales[idx]
        print(f"      Current ticket sales at idx {idx}: {tickets_waiting}")
        
        # Generate random boarding count (0 to tickets_waiting)
        if tickets_waiting > 0:
            passengers_boarding = self.random.randint(0, tickets_waiting)
        else:
            passengers_boarding = 0
        
        # Update passengers boarding
        self.data_manager.passengers_boarding[idx] = passengers_boarding
        
        print(f"\n   🚂 TRAIN ARRIVAL at {station_name} (Block {block_num}):")
        print(f"      Passengers waiting: {tickets_waiting}")
        print(f"      Passengers boarding: {passengers_boarding}")
        
        # Send passengers boarding to Train Model
        self.send_passengers_boarding_to_train_model(block_num)
        
        # Generate new random ticket sales for next train (0-70)
        new_tickets = self.random.randint(0, 70)
        self.data_manager.ticket_sales[idx] = new_tickets
        
        print(f"      New tickets sold: {new_tickets}")
        
        print(f"\n   📊 AFTER:")
        print(f"      ticket_sales[{idx}] = {self.data_manager.ticket_sales[idx]}")
        print(f"      passengers_boarding[{idx}] = {self.data_manager.passengers_boarding[idx]}")
        
        # Send updated station data to CTC (ticket sales + disembarking)
        self.send_station_data_to_ctc(block_num)


    def send_passengers_boarding_to_train_model(self, block_num):
        """
        Send passengers boarding for a specific station block to Train Model.
        
        Args:
            block_num (int): Block number of the station
        """
        idx = block_num - 1
        if 0 <= idx < len(self.data_manager.passengers_boarding):
            passenger_count = int(self.data_manager.passengers_boarding[idx])
            
            self.server.send_to_ui("Train Model", {
                'command': 'Passengers Boarding',
                'value': passenger_count
            })
            print(f"📤 Sent passengers boarding to Train Model: Block {block_num} = {passenger_count}")


    def monitor_station_occupancy(self):
        """
        Monitor block occupancy at stations.
        When a train arrives (occupancy changes from 0 to non-zero), handle boarding.
        """
        # Initialize previous occupancy tracking if not exists
        if not hasattr(self, '_previous_station_occupancy'):
            self._previous_station_occupancy = {}
            for block_num, _ in self.data_manager.station_location:
                self._previous_station_occupancy[block_num] = 0
            print("🔍 === STARTED MONITORING STATION OCCUPANCY ===")
            print(f"   Monitoring stations: {[f'Block {b}' for b, _ in self.data_manager.station_location]}\n")
        
        # Check each station for train arrival
        for block_num, station_name in self.data_manager.station_location:
            block_idx = block_num - 1
            if block_idx < len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_idx]
                current_occupancy = getattr(block, 'occupancy', 0)
                previous_occupancy = self._previous_station_occupancy[block_num]
                
                # Debug: Print occupancy check (only on first few iterations)
                if not hasattr(self, '_debug_count'):
                    self._debug_count = 0
                
                if self._debug_count < 3:  # Only print first 3 times
                    print(f"   Checking Block {block_num} ({station_name}): prev={previous_occupancy}, curr={current_occupancy}")
                
                # Detect train arrival (occupancy changed from 0 to non-zero)
                if previous_occupancy == 0 and current_occupancy != 0:
                    print(f"\n🚉 === TRAIN ARRIVAL DETECTED ===")
                    print(f"   Train {current_occupancy} arrived at {station_name} (Block {block_num})")
                    self.handle_train_arrival_at_station(block_num)
                    print(f"   === TRAIN ARRIVAL HANDLED ===\n")
                
                # Update previous occupancy
                self._previous_station_occupancy[block_num] = current_occupancy
        
        if self._debug_count < 3:
            self._debug_count += 1
        
        # Check again in 500ms (faster monitoring for train arrivals)
        self.after(500, self.monitor_station_occupancy)

    def prompt_and_activate_track_circuit(self):
        """Prompt for block number and activate/clear track circuit failure."""
        if self.failure_train_circuit_var.get():
            # Checkbox was just checked - activate failure
            block_num = simpledialog.askinteger(
                "Track Circuit Failure",
                "Enter block number for Track Circuit Failure:",
                minvalue=1,
                maxvalue=len(self.data_manager.blocks)
            )
            if block_num:
                self.on_track_circuit_failure_change(block_num)
            else:
                # User cancelled - uncheck the box
                self.failure_train_circuit_var.set(False)
        else:
            # Checkbox was just unchecked - clear failure
            block_num = simpledialog.askinteger(
                "Clear Track Circuit Failure",
                "Enter block number to clear failure:",
                minvalue=1,
                maxvalue=len(self.data_manager.blocks)
            )
            if block_num:
                self.on_track_circuit_failure_change(block_num)
            else:
                # User cancelled - keep box checked
                self.failure_train_circuit_var.set(True)

    def _create_train_from_wayside(self, speed, authority):
        """Automatically create a train object when Wayside sends new speed/authority."""
        # Initialize starting ID if not set yet
        if not hasattr(self.data_manager, "next_train_id"):
            self.data_manager.next_train_id = 11000

        # Assign new train ID
        train_id = self.data_manager.next_train_id
        self.data_manager.next_train_id += 1

        # Register new train in data manager
        self.data_manager.active_trains.append(f"Train {train_id}")
        self.data_manager.commanded_speed.append(speed)
        self.data_manager.commanded_authority.append(authority)
        self.data_manager.train_occupancy.append(0)

        print(f"[TRAIN CREATED] ID={train_id}, Speed={speed} m/s, Authority={authority} blocks")

        # Refresh dropdowns and terminals
        self.train_combo["values"] = self.data_manager.active_trains
        self.train_combo.set(f"Train {train_id}")
        self.send_outputs()
    
    def _create_train_from_yard(self, speed, authority):
        """Create a new train specifically from the Yard/Block 63, starting at block 63."""
        # Initialize starting ID if not set yet
        if not hasattr(self.data_manager, "next_train_id"):
            self.data_manager.next_train_id = 11000

        # Assign new train ID
        train_id = self.data_manager.next_train_id
        self.data_manager.next_train_id += 1
        
        # Create train identifier
        train_name = f"Train_{train_id}"

        # Register new train in data manager
        self.data_manager.active_trains.append(train_name)
        
        # Ensure train_locations list exists and is properly sized
        if not hasattr(self.data_manager, 'train_locations'):
            self.data_manager.train_locations = []
        
        # Ensure the list is the same size as active_trains
        while len(self.data_manager.train_locations) < len(self.data_manager.active_trains) - 1:
            self.data_manager.train_locations.append(0)
        
        # Add this train at block 63
        self.data_manager.train_locations.append(63)  # Start at block 63
        
        # Set commanded speed and authority
        self.data_manager.commanded_speed.append(speed if speed is not None else 0)
        self.data_manager.commanded_authority.append(authority if authority is not None else 0)
        
        # Initialize train occupancy (passengers)
        self.data_manager.train_occupancy.append(0)

        print(f"🚂 [YARD/BLOCK 63 TRAIN CREATED] ID={train_id}, Starting at Block 63")
        print(f"   Initial Speed={speed} m/s, Authority={authority} blocks")
        print(f"   Active trains: {self.data_manager.active_trains}")
        print(f"   Train locations: {self.data_manager.train_locations}")
        print(f"   Array sizes: active_trains={len(self.data_manager.active_trains)}, commanded_speed={len(self.data_manager.commanded_speed)}, commanded_authority={len(self.data_manager.commanded_authority)}")

        # Update UI elements if they exist
        if hasattr(self, 'train_combo'):
            self.train_combo["values"] = self.data_manager.active_trains
            self.train_combo.set(train_name)
        
        # Send creation notification to other modules
        try:
            self.server.send_to_ui("Train Model", {
                "command": "new_train",
                "train_id": train_name,
                "block_number": 63,
                "commanded_speed": speed,
                "commanded_authority": authority
            })
            
            self.server.send_to_ui("CTC", {
                "command": "train_dispatched",
                "train_id": train_name,
                "from": "Yard/Block63",
                "entry_block": 63
            })
        except Exception as e:
            print(f"⚠️ Error sending train creation notifications: {e}")
        
        # Refresh UI - but don't let errors stop us
        try:
            self.refresh_ui()
        except Exception as e:
            print(f"⚠️ Error during refresh_ui: {e}")
        
        # Send outputs - but catch any errors
        try:
            self.send_outputs()
        except Exception as e:
            print(f"⚠️ Error during send_outputs: {e}")
        
        return train_name


    def prompt_and_activate_broken_rail(self):
        """Prompt for block number and activate/clear broken rail failure."""
        if self.failure_rail_var.get():
            block_num = simpledialog.askinteger(
                "Broken Rail Failure",
                "Enter block number for Broken Rail Failure:",
                minvalue=1,
                maxvalue=len(self.data_manager.blocks)
            )
            if block_num:
                self.on_broken_rail_failure_change(block_num)
            else:
                self.failure_rail_var.set(False)
        else:
            block_num = simpledialog.askinteger(
                "Clear Broken Rail Failure",
                "Enter block number to clear failure:",
                minvalue=1,
                maxvalue=len(self.data_manager.blocks)
            )
            if block_num:
                self.on_broken_rail_failure_change(block_num)
            else:
                self.failure_rail_var.set(True)

    def prompt_and_activate_power(self):
        """Prompt for block number and activate/clear power failure."""
        if self.failure_power_var.get():
            block_num = simpledialog.askinteger(
                "Power Failure",
                "Enter block number for Power Failure:",
                minvalue=1,
                maxvalue=len(self.data_manager.blocks)
            )
            if block_num:
                self.on_power_failure_change(block_num)
            else:
                self.failure_power_var.set(False)
        else:
            block_num = simpledialog.askinteger(
                "Clear Power Failure",
                "Enter block number to clear failure:",
                minvalue=1,
                maxvalue=len(self.data_manager.blocks)
            )
            if block_num:
                self.on_power_failure_change(block_num)
            else:
                self.failure_power_var.set(True)
    
    def on_closing(self):
        """Handle application closing"""
        print("Closing application...")
        self.server.running = False
        if self.server.server_socket:
            try:
                self.server.server_socket.close()
            except:
                pass
        self.root.destroy()

    # ============================================================================
    # Add these methods to your TrackModelUI class
    # ============================================================================
    # ---------------- OUTPUT METHODS (Sending Data) ----------------

    def send_all_outputs(self):
        """Send all outputs to appropriate UIs. Call this periodically or on state change."""
        self.send_all_station_data_to_ctc()
        self.send_failure_modes_to_wayside()
        self.send_block_occupancy_to_wayside()
        self.send_block_occupancy_to_train_model()
        self.send_commanded_speed_to_train_model()
        self.send_commanded_authority_to_train_model()
        self.send_beacons_to_train_model()
        self.send_passengers_boarding_to_train_model()
        self.send_light_states_to_train_controller()

    def send_station_data_to_ctc(self, block_num):
        """
        Send both ticket sales and passengers disembarking for a station to CTC.
        Sends as a 2-element array: [ticket_sales, passengers_disembarking]
        
        Args:
            block_num (int): Block number of the station
        """
        idx = block_num - 1
        if 0 <= idx < len(self.data_manager.ticket_sales):
            ticket_count = int(self.data_manager.ticket_sales[idx])
            disembarking_count = int(self.data_manager.passengers_disembarking[idx])
            
            # Send as 2-element array
            self.server.send_to_ui("CTC", {
                'command': 'TP',
                'value': [ticket_count, disembarking_count]
            })
            print(f"📤 Sent station data to CTC: [tickets={ticket_count}, disembarking={disembarking_count}]")

    def send_all_station_data_to_ctc(self):
        """
        Send ticket sales and passengers disembarking for ALL stations to CTC.
        This is called periodically by send_all_outputs().
        """
        for block_num, station_name in self.data_manager.station_location:
            self.send_station_data_to_ctc(block_num)

    def send_failure_modes_to_wayside(self):
        """Send failure modes to Wayside Controller."""
        failures = self.murphy_failures.get_all_failures()
        
        failure_data = {}
        for block_num, failure_type in failures.items():
            failure_data[block_num] = {
                'failure_type': failure_type,
                'traversable': self.murphy_failures.is_traversable(block_num)
            }
        
        self.server.send_to_ui("Wayside Controller", {
            'command': 'failure_modes',
            'data': failure_data
        })
        print(f"📤 Sent failure modes to Wayside Controller ({len(failures)} failures)")

    def send_block_occupancy_to_wayside(self):
        """Send block occupancy to Wayside Controller (Track SW and Track HW)."""
        # Send individual occupancy updates in the flat format Wayside expects
        occupied_count = 0
        unoccupied_count = 0
        
        for block in self.data_manager.blocks:
            # Send all blocks so Wayside knows both occupied and unoccupied states
            is_occupied = block.occupancy != 0
            
            # Send to Track SW with proper command format
            self.server.send_to_ui("Track SW", {
                'command': 'update_occupancy', 
                'value': {
                    'track': 'Green',
                    'block': str(block.block_number),  # Send as string
                    'occupied': is_occupied  # Boolean value
                }
            })
            
            if is_occupied:
                occupied_count += 1
            else:
                unoccupied_count += 1
        
        # Also send bulk format to Track HW for backward compatibility
        occupancy_data = {}
        for block in self.data_manager.blocks:
            if block.occupancy != 0:  # Only occupied blocks in bulk format
                occupancy_data[block.block_number] = block.occupancy
        
        self.server.send_to_ui("Track HW", {
            'command': 'Block Occupancy', 
            'data': occupancy_data
        })
        
        print(f"📤 Sent block occupancy to Wayside: {occupied_count} occupied, {unoccupied_count} unoccupied blocks")
    
    def send_bulk_occupancy_to_wayside(self):
        """Send bulk occupancy data to Wayside Controller as a dictionary."""
        # Create occupancy data dictionary (block_number: boolean)
        occupancy_data = {}
        for block in self.data_manager.blocks:
            occupancy_data[block.block_number] = block.occupancy != 0
        
        # Send in the flat format with all occupancy data at once
        self.server.send_to_ui("Track SW", {
            'track': 'Green',
            'block': 'all',  # Special indicator for bulk update
            'occupied': occupancy_data  # Dictionary of block_num: boolean
        })
        
        print(f"📤 Sent bulk occupancy data to Track SW: {len(occupancy_data)} blocks")

    def send_block_occupancy_to_train_model(self):
        """Send block occupancy to Train Model."""
        occupancy_data = {}
        for block in self.data_manager.blocks:
            occupancy_data[block.block_number] = block.occupancy
        
        self.server.send_to_ui("Train Model", {
            'command': 'block_occupancy',
            'data': occupancy_data
        })
        print(f"📤 Sent block occupancy to Train Model")

    def send_commanded_speed_to_train_model(self):
        """Send commanded speed to Train Model."""
        speed_data = {}
        for i, train_id in enumerate(self.data_manager.active_trains):
            if i < len(self.data_manager.commanded_speed):
                speed_data[train_id] = self.data_manager.commanded_speed[i]
        
        self.server.send_to_ui("Train Model", {
            'command': 'commanded_speed',
            'data': speed_data
        })
        print(f"📤 Sent commanded speed to Train Model")

    def send_commanded_authority_to_train_model(self):
        """Send commanded authority to Train Model."""
        authority_data = {}
        for i, train_id in enumerate(self.data_manager.active_trains):
            if i < len(self.data_manager.commanded_authority):
                authority_data[train_id] = self.data_manager.commanded_authority[i]
        
        self.server.send_to_ui("Train Model", {
            'command': 'commanded_authority',
            'data': authority_data
        })
        print(f"📤 Sent commanded authority to Train Model")

    def send_beacons_to_train_model(self):
        """Send beacon data to Train Model."""
        beacon_data = {}
        for block in self.data_manager.blocks:
            # Only send if beacon can be sent (no track circuit or power failure)
            if self.murphy_failures.can_send_beacon(block.block_number):
                if hasattr(block, 'beacon') and block.beacon:
                    beacon_data[block.block_number] = block.beacon
        
        self.server.send_to_ui("Train Model", {
            'command': 'beacons',
            'data': beacon_data
        })
        print(f"📤 Sent beacons to Train Model ({len(beacon_data)} blocks)")

    def send_passengers_boarding_to_train_model(self):
        """Send passengers boarding data to Train Model."""
        boarding_data = {}
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            boarding_data[block_num] = {
                'station_name': station_name,
                'passengers_boarding': int(self.data_manager.passengers_boarding[idx])
            }
        
        self.server.send_to_ui("Train Model", {
            'command': 'passengers_boarding',
            'data': boarding_data
        })
        print(f"📤 Sent passengers boarding to Train Model")

    def send_light_states_to_train_controller(self):
        """Send traffic light states to Train Controller as two-bit boolean arrays."""
        light_data = {}
        for block_num in self.light_states:
            if block_num <= len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_num - 1]
                # Check if block has power
                if self.murphy_failures.has_power(block_num):
                    state = getattr(block, 'traffic_light_state', 0)
                    # Convert state (0-3) to two-bit boolean array [bit0, bit1]
                    # State 0: [False, False], State 1: [True, False], 
                    # State 2: [False, True], State 3: [True, True]
                    light_data[block_num] = [bool(state & 1), bool(state & 2)]
                else:
                    light_data[block_num] = [False, False]  # No power = lights off
        
        self.server.send_to_ui("Train Controller", {
            'command': 'Light States',
            'data': light_data
        })
        print(f"📤 Sent light states to Train Controller as two-bit boolean arrays")


    # ---------------- INPUT HANDLERS (Update _process_message) ----------------

    def _process_message(self, message, source_ui_id):
        """Process incoming messages from other UIs"""
        try:
            print(f"📨 Received from {source_ui_id}: {message}")
            
            # Extract command (ensure string type)
            command = message.get('command')
            if command is not None and not isinstance(command, str):
                command = str(command)
            
            # Extract value (no type conversion - keep as-is)
            value = message.get('value')
            
            # Extract data (no type conversion - keep as-is)
            data = message.get('data')  # Added support for 'data' field
            
            # Extract block_number and convert to int if it's a string
            block_number = message.get('block_number')
            if block_number is not None:
                if isinstance(block_number, str):
                    try:
                        block_number = int(block_number)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert block_number '{block_number}' to int")
                        block_number = None
                elif not isinstance(block_number, int):
                    try:
                        block_number = int(block_number)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert block_number '{block_number}' to int")
                        block_number = None
            
            # ============================================================
            # COMMANDED SPEED AND AUTHORITY - Combined command
            # Receives from Wayside: separate fields (block_number, commanded_speed, commanded_authority)
            # Sends to Train Model: array format [block_number, commanded_speed, commanded_authority]
            # Special case: If block_number is "Yard", create a new train that starts from Yard to block 63
            # ============================================================
            if command == 'Speed and Authority':
                # Accept Wayside Controller format: separate fields in message
                commanded_speed = message.get('commanded_speed')
                commanded_authority = message.get('commanded_authority')
                block_num = message.get('block_number')
                train_id = message.get('train_id')
                
                # Convert numeric values from strings if needed (do this first)
                if commanded_speed is not None and isinstance(commanded_speed, str):
                    try:
                        commanded_speed = float(commanded_speed)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert commanded_speed '{commanded_speed}' to float")
                        commanded_speed = None
                
                if commanded_authority is not None and isinstance(commanded_authority, str):
                    try:
                        commanded_authority = int(commanded_authority)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert commanded_authority '{commanded_authority}' to int")
                        commanded_authority = None
                
                # Check if this is a Yard dispatch (new train creation)
                # Accept either "Yard" string or block number 63
                is_yard_dispatch = False
                
                # Check for "Yard" string
                if isinstance(block_num, str) and block_num.upper() == "YARD":
                    is_yard_dispatch = True
                    print(f"🚂 YARD DISPATCH DETECTED (from 'Yard') - Creating new train")
                # Check for block 63 (with no existing train)
                elif block_num == 63 or (isinstance(block_num, str) and block_num == "63"):
                    # Check if there's already a train at block 63
                    block_63_occupied = False
                    if 63 <= len(self.data_manager.blocks):
                        block_63 = self.data_manager.blocks[62]  # Block 63 (index 62)
                        if hasattr(block_63, 'occupancy') and block_63.occupancy != 0:
                            block_63_occupied = True
                    
                    # Only treat as yard dispatch if block 63 is not occupied AND no trains exist
                    if not block_63_occupied and not train_id:
                        # Check if any trains already exist
                        if not self.data_manager.active_trains:
                            is_yard_dispatch = True
                            print(f"🚂 YARD DISPATCH DETECTED (from Block 63) - Creating new train")
                            # Convert block_num to int if it's a string
                            if isinstance(block_num, str):
                                block_num = 63
                        else:
                            # Use existing train instead of creating a duplicate
                            train_id = self.data_manager.active_trains[-1]
                            print(f"⚠️ Block 63 command received, but train already exists. Using: {train_id}")
                
                if is_yard_dispatch:
                    # Create a new train for yard dispatch
                    new_train_id = self._create_train_from_yard(commanded_speed, commanded_authority)
                    train_id = new_train_id
                    
                    # Set initial actual speed for the new train (starts at commanded speed)
                    if commanded_speed and commanded_speed > 0:
                        self.train_actual_speeds[new_train_id] = float(commanded_speed)
                        self.train_positions_in_block[new_train_id] = 0
                        import time
                        self.last_movement_update[new_train_id] = time.time()
                        print(f"🚄 Set initial actual speed for {new_train_id}: {commanded_speed} m/s")
                    
                    # Set/ensure position at block 63 (entry from yard)
                    block_num = 63
                    
                    # Set occupancy at block 63 - CRITICAL: This must happen
                    try:
                        if 63 <= len(self.data_manager.blocks):
                            yard_entry_block = self.data_manager.blocks[62]  # Block 63 (index 62)
                            # Initialize occupancy if it doesn't exist
                            if not hasattr(yard_entry_block, 'occupancy'):
                                yard_entry_block.occupancy = 0
                                print(f"[DEBUG] Initialized occupancy attribute for block 63")
                            
                            # Extract train number from train_id (e.g., "Train_11000" -> 11000)
                            train_num = int(new_train_id.split('_')[1]) if '_' in new_train_id else 1
                            yard_entry_block.occupancy = train_num
                            print(f"✅ Set initial occupancy at Block 63 for {new_train_id}")
                            print(f"[DEBUG] Block 63 occupancy is now: {yard_entry_block.occupancy}")
                            
                            # Send occupancy update to other modules
                            try:
                                self.server.send_to_ui("Train Model", {
                                    "command": "block_occupancy",
                                    "value": {63: train_num}
                                })
                                self.server.send_to_ui("Track SW", {
                                    "command": "block_occupancy", 
                                    "value": {63: train_num}
                                })
                                self.server.send_to_ui("Track HW", {
                                    "command": "block_occupancy",
                                    "value": {63: train_num}
                                })
                            except Exception as e:
                                print(f"⚠️ Error sending occupancy updates: {e}")
                    except Exception as e:
                        print(f"❌ CRITICAL: Failed to set block 63 occupancy: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    # Log the yard dispatch
                    try:
                        for terminal in self.terminals:
                            terminal.config(state="normal")
                            terminal.insert("end", f"🚂 YARD DISPATCH: {new_train_id} → Block 63\n")
                            terminal.insert("end", f"   Speed: {commanded_speed} m/s, Authority: {commanded_authority} blocks\n")
                            terminal.see("end")
                            terminal.config(state="disabled")
                    except Exception as e:
                        print(f"⚠️ Error updating terminal: {e}")
                    
                    # Update the occupied blocks display - CRITICAL
                    try:
                        self.update_occupied_blocks_display()
                        print("[DEBUG] Called update_occupied_blocks_display after yard dispatch")
                        
                        # UPDATE BLOCK MARKER TO SHOW TRAIN ICON ON MAP
                        if hasattr(self, 'update_block_marker'):
                            self.update_block_marker(63)
                            print("[DEBUG] Updated block marker for block 63 - train should now be visible on map")
                    except Exception as e:
                        print(f"❌ Error updating occupied blocks display: {e}")
                    
                    # Force a full UI refresh to ensure everything updates
                    try:
                        self.refresh_ui()
                        print("[DEBUG] Called refresh_ui after yard dispatch")
                    except Exception as e:
                        print(f"⚠️ Error during refresh_ui: {e}")
                    
                # Convert block_num to int if it's not already (and not "Yard")
                elif block_num is not None and isinstance(block_num, str):
                    try:
                        block_num = int(block_num)
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not convert block_num '{block_num}' to int")
                        block_num = None
                
                # If not a yard dispatch and no train_id, create train ONLY if no trains exist yet
                if not is_yard_dispatch and not train_id:
                    # Only create a new train if we don't have any active trains
                    if not self.data_manager.active_trains:
                        self._create_train_from_wayside(commanded_speed, commanded_authority)
                        train_id = self.data_manager.active_trains[-1] if self.data_manager.active_trains else None
                        print(f"✅ Created new train (none existed): {train_id}")
                    else:
                        # Use the most recent active train instead of creating duplicates
                        train_id = self.data_manager.active_trains[-1]
                        print(f"⚠️ No train_id provided in command, using existing train: {train_id}")
                
                # Also support legacy array format for backwards compatibility
                if commanded_speed is None and isinstance(value, list) and len(value) == 3:
                    block_num = value[0] if not isinstance(value[0], str) else int(value[0])
                    commanded_speed = value[1] if not isinstance(value[1], str) else float(value[1])
                    commanded_authority = value[2] if not isinstance(value[2], str) else int(value[2])
                
                if commanded_speed is not None and commanded_authority is not None and block_num is not None:
                    
                    # If no train_id provided, try to find train on this block
                    if not train_id:
                        # Look for a train on this block
                        if block_num <= len(self.data_manager.blocks):
                            block = self.data_manager.blocks[block_num - 1]
                            if hasattr(block, 'occupancy') and block.occupancy != 0:
                                # Use the train ID from block occupancy
                                train_id = f"Train_{block.occupancy}"
                            else:
                                # Default to using block number as train identifier
                                train_id = f"Train_1"
                                
                    # Update commanded speed and authority for the specific train (if it exists)
                    if train_id in self.data_manager.active_trains:
                        idx = self.data_manager.active_trains.index(train_id)
                        self.data_manager.commanded_speed[idx] = commanded_speed
                        self.data_manager.commanded_authority[idx] = commanded_authority
                        print(f"✅ Updated commanded values for {train_id}: Speed={commanded_speed}, Authority={commanded_authority}")
                        
                        # Send array format to Train Model: [block_number, commanded_speed, commanded_authority]
                        speed_authority_array = [block_num, commanded_speed, commanded_authority]
                        self.server.send_to_ui("Train Model", {
                            "command": "Speed and Authority",
                            "train_id": train_id,
                            "value": speed_authority_array
                        })
                        print(f"📤 Sent Speed and Authority array to Train Model: {speed_authority_array}")
                    else:
                        print(f"⚠️ Train {train_id} not found in active trains (will still display in Train Details). Available: {self.data_manager.active_trains}")
                else:
                    print(f"⚠️ Invalid Speed and Authority format. Got speed={commanded_speed}, auth={commanded_authority}, block={block_num}")
            
            # ============================================================
            # SWITCH POSITIONS - Update switch states
            # value should be a string like "76-77" where 76 is current block, 77 is next block
            # OR a dict like {5: "76-77", 10: "85-86"} for multiple switches
            # ============================================================
            elif command == 'Switch Positions':
                def parse_switch_direction(switch_string, switch_block_num=None):
                    """
                    Parse a switch direction string like "76-77" to determine switch state.
                    Returns True for one direction, False for the other.
                    
                    The logic determines which way the switch should be set based on:
                    - The from-block and to-block numbers
                    - The switch block's typical connections
                    - Known switch configurations from track layout
                    """
                    if not isinstance(switch_string, str) or '-' not in switch_string:
                        print(f"⚠️ Invalid switch format: {switch_string} (expected 'from-to' format)")
                        return None
                    
                    parts = switch_string.split('-')
                    if len(parts) != 2:
                        print(f"⚠️ Invalid switch format: {switch_string} (expected exactly two parts)")
                        return None
                    
                    try:
                        from_block = int(parts[0].strip())
                        to_block = int(parts[1].strip())
                    except (ValueError, TypeError):
                        print(f"⚠️ Could not parse blocks from: {switch_string}")
                        return None
                    
                    # Determine switch direction based on from/to blocks
                    # The switch state depends on the track layout and connections
                    
                    # Special handling for known switch configurations
                    # These are common switch patterns in track systems:
                    
                    # 1. Fork switches (one track splitting into two)
                    #    - Main line continues straight (usually higher block number) = True
                    #    - Diverging line (branch) = False
                    
                    # 2. Merge switches (two tracks joining into one)  
                    #    - From main line = True
                    #    - From branch line = False
                    
                    # 3. Crossover switches (between parallel tracks)
                    #    - Staying on same track = True
                    #    - Crossing to other track = False
                    
                    # Check if this is a known switch block with specific routing
                    if switch_block_num and switch_block_num in self.switch_blocks:
                        # Add specific switch logic here based on your track layout
                        # Example patterns:
                        
                        # Switches that connect sequential blocks vs branches
                        if abs(to_block - from_block) == 1:
                            # Sequential blocks - likely main line
                            # Forward direction (increasing) = True, Backward = still sequential
                            return to_block > from_block
                        elif abs(to_block - from_block) > 10:
                            # Large jump in block numbers - likely a branch/crossover
                            return False
                    
                    # Default logic: 
                    # - Forward progression (increasing block numbers) = True (main/straight)
                    # - Backward or large jumps = False (diverging/branch)
                    if to_block == from_block + 1:
                        # Direct forward progression
                        return True
                    elif to_block == from_block - 1:
                        # Direct backward progression  
                        return False
                    elif to_block > from_block:
                        # Forward but not sequential - likely branching forward
                        return True
                    else:
                        # Backward or branching backward
                        return False
                
                if isinstance(value, dict):
                    # Multiple switches: {block_num: "from-to", ...}
                    for block_num, switch_string in value.items():
                        # Convert block_num from string to int if needed
                        if isinstance(block_num, str):
                            try:
                                block_num = int(block_num)
                            except (ValueError, TypeError):
                                print(f"⚠️ Could not convert block_num key '{block_num}' to int")
                                continue
                        
                        if 1 <= block_num <= len(self.data_manager.blocks):
                            block = self.data_manager.blocks[block_num - 1]
                            # Parse the from-to string to get context
                            parts = switch_string.split('-') if '-' in switch_string else []
                            from_block = int(parts[0].strip()) if len(parts) == 2 else 0
                            to_block = int(parts[1].strip()) if len(parts) == 2 else 0
                            
                            state = parse_switch_direction(switch_string, block_num)
                            if state is not None:
                                block.switch_state = state
                                if from_block and to_block:
                                    self.log_switch_change(block_num, from_block, to_block, state)
                                else:
                                    print(f"✅ Updated switch at block {block_num}: {'Right/Forward' if state else 'Left/Backward'} (from {switch_string})")
                    self.refresh_bidirectional_controls()  # Update bidirectional directions
                    self.refresh_ui()
                    
                elif isinstance(value, str) and '-' in value:
                    # Single switch update with "from-to" format
                    # If block_number is provided, use it as the switch block
                    # Otherwise, try to determine the switch block from the from/to blocks
                    
                    if block_number:
                        # Switch block explicitly specified
                        if 1 <= block_number <= len(self.data_manager.blocks):
                            block = self.data_manager.blocks[block_number - 1]
                            # Parse the from-to string to get context
                            parts = value.split('-')
                            from_block = int(parts[0].strip()) if len(parts) == 2 else 0
                            to_block = int(parts[1].strip()) if len(parts) == 2 else 0
                            
                            state = parse_switch_direction(value, block_number)
                            if state is not None:
                                block.switch_state = state
                                if from_block and to_block:
                                    self.log_switch_change(block_number, from_block, to_block, state)
                                else:
                                    print(f"✅ Updated switch at block {block_number}: {'Right/Forward' if state else 'Left/Backward'} (from {value})")
                                self.refresh_bidirectional_controls()
                                self.refresh_ui()
                    else:
                        # Try to determine switch block from the from-to string
                        parts = value.split('-')
                        if len(parts) == 2:
                            try:
                                from_block = int(parts[0].strip())
                                to_block = int(parts[1].strip())
                                # The switch is typically at or near the from_block
                                if 1 <= from_block <= len(self.data_manager.blocks):
                                    block = self.data_manager.blocks[from_block - 1]
                                    state = parse_switch_direction(value, from_block)
                                    if state is not None:
                                        block.switch_state = state
                                        self.log_switch_change(from_block, from_block, to_block, state)
                                        self.refresh_bidirectional_controls()
                                        self.refresh_ui()
                            except (ValueError, TypeError):
                                print(f"⚠️ Could not parse switch position from: {value}")
                
                # Keep backward compatibility with old boolean format
                elif isinstance(value, bool) and block_number:
                    if 1 <= block_number <= len(self.data_manager.blocks):
                        block = self.data_manager.blocks[block_number - 1]
                        block.switch_state = value
                        route_info = self.get_switch_destination(block_number, value)
                        if isinstance(route_info, tuple) and len(route_info) == 2:
                            from_block, to_block = route_info
                            if from_block == "Yard":
                                destination_text = f"Yard to {to_block}"
                            elif to_block == "Yard":
                                destination_text = f"{from_block} to Yard"
                            else:
                                destination_text = f"{from_block} to {to_block}"
                        else:
                            destination_text = f"To {route_info}"
                        print(f"✅ Updated switch at block {block_number}: {destination_text} (legacy boolean format)")
                        self.refresh_bidirectional_controls()
                        self.refresh_ui()
                        
                else:
                    print(f"⚠️ Unrecognized switch position format. Expected 'from-to' string or dict, got: {type(value)} = {value}")
            
            # ============================================================
            # LIGHT STATES / SIGNALS - From Wayside Controller
            # Receives as two-bit boolean arrays: [bit0, bit1]
            # ============================================================
            elif command == 'Light States':
                if isinstance(data, dict):
                    for block_num, bit_array in data.items():
                        # Convert block_num from string to int if needed
                        if isinstance(block_num, str):
                            try:
                                block_num = int(block_num)
                            except (ValueError, TypeError):
                                print(f"⚠️ Could not convert block_num key '{block_num}' to int")
                                continue
                        
                        if 1 <= block_num <= len(self.data_manager.blocks):
                            block = self.data_manager.blocks[block_num - 1]
                            # Convert two-bit boolean array to state (0-3)
                            # [False, False] = 0, [True, False] = 1,
                            # [False, True] = 2, [True, True] = 3
                            if isinstance(bit_array, list) and len(bit_array) == 2:
                                state = (1 if bit_array[0] else 0) + (2 if bit_array[1] else 0)
                                block.traffic_light_state = state
                                print(f"✅ Updated signal at block {block_num}: State {state} from bits {bit_array}")
                            else:
                                print(f"⚠️ Invalid bit array format for block {block_num}: {bit_array}")
                    self.refresh_bidirectional_controls()  # Update bidirectional directions
                    self.refresh_ui()
                elif isinstance(value, dict):
                    for block_num, bit_array in value.items():
                        # Convert block_num from string to int if needed
                        if isinstance(block_num, str):
                            try:
                                block_num = int(block_num)
                            except (ValueError, TypeError):
                                print(f"⚠️ Could not convert block_num key '{block_num}' to int")
                                continue
                        
                        if 1 <= block_num <= len(self.data_manager.blocks):
                            block = self.data_manager.blocks[block_num - 1]
                            # Convert two-bit boolean array to state (0-3)
                            if isinstance(bit_array, list) and len(bit_array) == 2:
                                state = (1 if bit_array[0] else 0) + (2 if bit_array[1] else 0)
                                block.traffic_light_state = state
                                print(f"✅ Updated signal at block {block_num}: State {state} from bits {bit_array}")
                            else:
                                print(f"⚠️ Invalid bit array format for block {block_num}: {bit_array}")
                    self.refresh_bidirectional_controls()  # Update bidirectional directions
                    self.refresh_ui()
                elif block_number and value is not None:
                    if 1 <= block_number <= len(self.data_manager.blocks):
                        block = self.data_manager.blocks[block_number - 1]
                        # Convert two-bit boolean array to state (0-3)
                        if isinstance(value, list) and len(value) == 2:
                            state = (1 if value[0] else 0) + (2 if value[1] else 0)
                            block.traffic_light_state = state
                            print(f"✅ Updated signal at block {block_number}: State {state} from bits {value}")
                        else:
                            print(f"⚠️ Invalid bit array format for block {block_number}: {value}")
                        self.refresh_bidirectional_controls()  # Update bidirectional directions
                        self.refresh_ui()

            # ============================================================
            # CURRENT SPEED - From Train Model (Passenger_UI)
            # Receives current/actual speed for a train to calculate movement
            # Command format from Passenger_UI: {'command': 'Current Speed', 'value': speed}
            # ============================================================
            elif command == 'Current Speed' or command == 'current_speed' or command == 'actual_speed' or command == 'actualSpeed':
                # Handle speed update from Train Model
                speed = value  # Speed in m/s or mph (Passenger_UI sends in mph)
                train_id = message.get('train_id')
                
                # If no train_id provided, determine from active trains
                if not train_id and speed is not None:
                    # Passenger_UI doesn't send train_id, so we need to determine which train
                    # Assume it's for the most recently deployed train or first active train
                    if self.data_manager.active_trains:
                        train_id = self.data_manager.active_trains[-1]  # Most recent train
                        print(f"📍 No train_id in Current Speed message, assuming it's for {train_id}")
                
                if speed is not None:
                    # Convert speed to float if needed
                    if isinstance(speed, str):
                        try:
                            speed = float(speed)
                        except (ValueError, TypeError):
                            print(f"⚠️ Could not convert speed '{speed}' to float")
                            speed = 0
                    
                    # Convert from mph to m/s if needed (Passenger_UI sends in mph)
                    # 1 mph = 0.44704 m/s
                    speed_ms = speed * 0.44704
                    
                    if train_id:
                        # Store actual speed for this train
                        self.train_actual_speeds[train_id] = speed_ms
                        print(f"🚄 Updated current speed for {train_id}: {speed:.1f} mph ({speed_ms:.1f} m/s)")
                        
                        # Initialize position tracking if new train
                        if train_id not in self.train_positions_in_block:
                            self.train_positions_in_block[train_id] = 0
                            import time
                            self.last_movement_update[train_id] = time.time()
                            
                            # Find which block this train is on
                            if train_id in self.data_manager.active_trains:
                                idx = self.data_manager.active_trains.index(train_id)
                                if idx < len(self.data_manager.train_locations):
                                    block_num = self.data_manager.train_locations[idx]
                                    print(f"   Train {train_id} is on block {block_num}")
                    else:
                        print(f"⚠️ Could not determine train for speed update: {speed} mph")
                else:
                    print(f"⚠️ Invalid current speed message: speed={speed}")
            
            
            # ============================================================            # PASSENGERS DISEMBARKING - From Train Model (Passenger_UI)            # Command format from Passenger_UI: {'command': 'Passenger Disembarking', 'value': disembarking}            # ============================================================            elif command == 'Passenger Disembarking' or command == 'Passengers Disembarking':                disembarking = value                                # Handle block_number if provided (legacy format)                if block_number is not None:                    idx = block_number - 1                    if 0 <= idx < len(self.data_manager.passengers_disembarking):                        if isinstance(disembarking, str):                            try:                                disembarking = int(disembarking)                            except (ValueError, TypeError):                                disembarking = 0                                                self.data_manager.passengers_disembarking[idx] = disembarking                        print(f"✅ Passengers disembarking at block {block_number}: {disembarking}")                                                if block_number in self.station_blocks:                            self.send_station_data_to_ctc(block_number)                                                if hasattr(self, 'view_mode') and self.view_mode.get() == "station":                            self.populate_station_view()                else:                    # Passenger_UI doesn't send block_number, determine from train location                    if isinstance(disembarking, str):                        try:                            disembarking = int(disembarking)                        except (ValueError, TypeError):                            disembarking = 0                                        # Try to find the train                    train_id = message.get('train_id')                    if not train_id and self.data_manager.active_trains:                        train_id = self.data_manager.active_trains[-1]  # Most recent train                        print(f"📍 No train_id, using {train_id}")                                        # Find train's current block                    if train_id and train_id in self.data_manager.active_trains:                        idx = self.data_manager.active_trains.index(train_id)                        if idx < len(self.data_manager.train_locations):                            block_num = self.data_manager.train_locations[idx]                            block_idx = block_num - 1                                                        if 0 <= block_idx < len(self.data_manager.passengers_disembarking):                                self.data_manager.passengers_disembarking[block_idx] = disembarking                                print(f"✅ Passengers disembarking at block {block_num} (train {train_id}): {disembarking}")                                                                if block_num in self.station_blocks:                                    self.send_station_data_to_ctc(block_num)                                                                if hasattr(self, 'view_mode') and self.view_mode.get() == "station":                                    self.populate_station_view()                    else:                        print(f"⚠️ Could not determine location for {disembarking} disembarking passengers")            
            # ============================================================
            elif command == 'Passengers Disembarking':
                if block_number is not None:
                    idx = block_number - 1
                    if 0 <= idx < len(self.data_manager.passengers_disembarking):
                        # Convert value to int if it's a string
                        if isinstance(value, str):
                            try:
                                value = int(value)
                            except (ValueError, TypeError):
                                print(f"⚠️ Could not convert value '{value}' to int")
                                value = 0
                        
                        self.data_manager.passengers_disembarking[idx] = value
                        print(f"✅ Received passengers disembarking from Train Model: Block {block_number} = {value}")
                        
                        # Forward to CTC immediately (sends both ticket sales and disembarking)
                        self.send_station_data_to_ctc(block_number)
                        
                        # Update UI if in station view
                        if self.view_mode.get() == "station":
                            self.populate_station_view()
            
            # ============================================================
            # TRAIN OCCUPANCY - From Train Model
            # ============================================================
            elif command == 'Train Occupancy' or command == 'train_occupancy':
                # Handle train occupancy from Passenger_UI
                passenger_count = value
                train_id = message.get('train_id')
                
                if not train_id and self.data_manager.active_trains:
                    train_id = self.data_manager.active_trains[-1]  # Most recent train
                    print(f"📍 No train_id in Train Occupancy, using {train_id}")
                
                if train_id in self.data_manager.active_trains:
                    idx = self.data_manager.active_trains.index(train_id)
                    if isinstance(passenger_count, str):
                        try:
                            passenger_count = int(passenger_count)
                        except (ValueError, TypeError):
                            passenger_count = 0
                    
                    self.data_manager.train_occupancy[idx] = passenger_count
                    print(f"✅ Updated train occupancy for {train_id}: {passenger_count} passengers")
                    
                    # Update UI if needed
                    if hasattr(self, 'tester_reference') and hasattr(self.tester_reference, 'refresh_train_details'):
                        self.tester_reference.refresh_train_details()
                else:
                    print(f"⚠️ Could not find train for occupancy update: {passenger_count} passengers")
            
            # ============================================================
            # TEST COMMAND
            # ============================================================
            elif command == 'test_command':
                print(f"🧪 Test message received: {value}")
            
            # ============================================================
            # ACTUAL SPEED - From Train Model
            # Receives actual speed for a train to calculate movement
            # ============================================================
            elif command == 'actual_speed' or command == 'actualSpeed':
                train_id = message.get('train_id')
                speed = value  # Speed in m/s
                
                if train_id and speed is not None:
                    # Convert speed to float if needed
                    if isinstance(speed, str):
                        try:
                            speed = float(speed)
                        except (ValueError, TypeError):
                            print(f"⚠️ Could not convert speed '{speed}' to float")
                            speed = 0
                    
                    # Store actual speed for this train
                    self.train_actual_speeds[train_id] = speed
                    print(f"🚄 Updated actual speed for {train_id}: {speed:.1f} m/s")
                    
                    # If this is a new train, initialize its position tracking
                    if train_id not in self.train_positions_in_block:
                        self.train_positions_in_block[train_id] = 0
                        import time
                        self.last_movement_update[train_id] = time.time()
                        
                        # Find which block this train is on
                        if train_id in self.data_manager.active_trains:
                            idx = self.data_manager.active_trains.index(train_id)
                            if idx < len(self.data_manager.train_locations):
                                block_num = self.data_manager.train_locations[idx]
                                print(f"   Train {train_id} is on block {block_num}")
                else:
                    print(f"⚠️ Invalid actual speed message: train_id={train_id}, speed={speed}")
            
            # ============================================================
            # REQUEST DATA - Another UI wants our data
            # ============================================================
            elif command == 'request_all_data':
                print(f"📤 Sending all data to {source_ui_id}")
                self.send_all_outputs()
            
            # ============================================================
            # SWITCH STATES - From Wayside Controller
            # Updates switch positions/directions
            # ============================================================
            elif command == 'switch_states':
                switches = message.get('switches', value)
                
                if switches:
                    print(f"🔀 Received switch states from {source_ui_id}")
                    
                    # Handle array of switch states
                    if isinstance(switches, list):
                        # Define switch block mapping based on Green Line switches
                        switch_block_mapping = {
                            0: 13,   # Switch at block 13
                            1: 29,   # Switch at block 29
                            2: 57,   # Switch at block 57
                            3: 63,   # Switch at block 63
                            4: 77,   # Switch at block 77
                            5: 85,   # Switch at block 85
                        }
                        
                        for idx, direction in enumerate(switches):
                            if idx in switch_block_mapping:
                                block_num = switch_block_mapping[idx]
                                if 1 <= block_num <= len(self.data_manager.blocks):
                                    block = self.data_manager.blocks[block_num - 1]
                                    # Normalize direction for consistency
                                    if direction in ["normal", False, 0, "0"]:
                                        direction = "normal"
                                    elif direction in ["reverse", True, 1, "1"]:
                                        direction = "reverse"
                                    else:
                                        direction = "normal"
                                    
                                    # Show routing path if configured
                                    if hasattr(self, "switch_routing") and block_num in self.switch_routing:
                                        next_block = self.switch_routing[block_num][direction]
                                        print(f"   Switch {block_num}: {direction} → routes to block {next_block}")
                                    # Store switch direction in block
                                    block.switch_direction = direction
                                    
                                    # Update switch states dictionary
                                    if not hasattr(self, 'switch_states'):
                                        self.switch_states = {}
                                    self.switch_states[block_num] = direction
                                    
                                    print(f"   Updated switch at block {block_num}: {direction}")
                                    
                                    # Mark block as having a switch
                                    self.switch_blocks.add(block_num)
                    
                    # Refresh relevant UI components
                    self.refresh_track_data_table()
                    self.refresh_track_system_table()
                    self.update_switch_display()
            
            elif command == 'update_switch':
                # Handle individual switch updates
                track = value.get('track')
                block = value.get('block')
                direction = value.get('direction')
                
                if block and direction:
                    print(f"🔀 Switch update: Block {block} -> {direction}")
                    
                    if isinstance(block, str):
                        block = int(block)
                        
                    if 1 <= block <= len(self.data_manager.blocks):
                        block_obj = self.data_manager.blocks[block - 1]
                        
                        # Store switch state
                        block_obj.switch_direction = direction
                        
                        # Update switch states dictionary
                        if not hasattr(self, 'switch_states'):
                            self.switch_states = {}
                        self.switch_states[block] = direction
                        
                        # Mark block as having a switch
                        self.switch_blocks.add(block)
                        
                        print(f"✅ Updated switch at block {block}: {direction}")
                        
                        # Update displays
                        self.refresh_track_data_table()
                        self.refresh_track_system_table()
                        self.update_switch_display()
            
            # ============================================================
            # BLOCK OCCUPANCY - From Train Model
            # Updates which blocks are occupied by trains
            # Can be: single value, [block_num, occupancy], or {block_num: occupancy}
            # ============================================================
            elif command == 'block_occupancy':
                if isinstance(value, list) and len(value) == 2:
                    # Format: [block_number, occupancy_value]
                    block_num = value[0]
                    occupancy = value[1]
                    
                    if isinstance(block_num, str):
                        block_num = int(block_num)
                    
                    if 1 <= block_num <= len(self.data_manager.blocks):
                        block = self.data_manager.blocks[block_num - 1]
                        block.occupancy = occupancy
                        # Check if train is at a switch and show routing
                        if occupancy != 0 and hasattr(self, "switch_routing") and block_num in self.switch_routing:
                            dir = self.switch_states.get(block_num, "normal")
                            next = self.switch_routing[block_num][dir]
                            print(f"   🚂 Train_{occupancy} at switch {block_num} ({dir}) → next block {next}")
                    print(f"✅ Updated block {block_num} occupancy: {occupancy}")
                        
                    # Update train location tracking if train moved
                    if occupancy != 0:
                        # Find train with this occupancy number
                        train_id = f"Train_{occupancy}"
                        if train_id in self.data_manager.active_trains:
                            idx = self.data_manager.active_trains.index(train_id)
                            old_location = self.data_manager.train_locations[idx] if idx < len(self.data_manager.train_locations) else 0
                            
                            if old_location != block_num:
                                self.data_manager.train_locations[idx] = block_num
                                print(f"   Train {train_id} moved from block {old_location} to block {block_num}")
                                
                                # Reset position tracking for new block
                                if train_id in self.train_positions_in_block:
                                    self.train_positions_in_block[train_id] = 0
                    
                    self.update_occupied_blocks_display()
                    
                    # Update block marker (dot/train icon)
                    if hasattr(self, 'update_block_marker'):
                        self.update_block_marker(block_num)
                    
                    # Forward occupancy update to Wayside Controller
                    self.send_block_occupancy_update(block_num, occupancy)
                        
                elif isinstance(value, dict):
                    # Format: {block_num: occupancy, ...}
                    for block_num, occupancy in value.items():
                        if isinstance(block_num, str):
                            block_num = int(block_num)
                        
                        if 1 <= block_num <= len(self.data_manager.blocks):
                            block = self.data_manager.blocks[block_num - 1]
                            block.occupancy = occupancy
                            # Check if train is at a switch and show routing
                            if occupancy != 0 and hasattr(self, "switch_routing") and block_num in self.switch_routing:
                                dir = self.switch_states.get(block_num, "normal")
                                next = self.switch_routing[block_num][dir]
                                print(f"   🚂 Train_{occupancy} at switch {block_num} ({dir}) → next block {next}")
                            print(f"✅ Updated block {block_num} occupancy: {occupancy}")
                            
                            # Update train tracking
                            if occupancy != 0:
                                train_id = f"Train_{occupancy}"
                                if train_id in self.data_manager.active_trains:
                                    idx = self.data_manager.active_trains.index(train_id)
                                    if idx < len(self.data_manager.train_locations):
                                        self.data_manager.train_locations[idx] = block_num
                                        
                                        # Reset position tracking
                                        if train_id in self.train_positions_in_block:
                                            self.train_positions_in_block[train_id] = 0
                            
                            # Forward occupancy update to Wayside Controller
                            self.send_block_occupancy_update(block_num, occupancy)
                            
                            # Update block marker (dot/train icon)
                            if hasattr(self, 'update_block_marker'):
                                self.update_block_marker(block_num)
                    
                    self.update_occupied_blocks_display()
                else:
                    print(f"⚠️ Unknown block occupancy format: {type(value)} = {value}")
            else:
                print(f"⚠️ Unknown command: {command}")
        
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()


    # ---------------- PERIODIC OUTPUT UPDATES ----------------

    def start_output_updates(self):
        """Start periodic output updates (every 5 seconds)."""
        self.send_all_outputs()
        # Also send occupancy updates to Wayside
        self.send_block_occupancy_to_wayside()
        self.after(5000, self.start_output_updates)  # Send every 5 seconds

    def test_block_occupancy(self, block_num, occupancy):
        """Test method to simulate receiving block occupancy"""
        if block_num is None:
            block_num = self.random.randint(1, len(self.data_manager.blocks))
        if occupancy is None:
            occupancy = self.random.randint(0, 1)  # 0 or 1
        
        # Test with array format: [block_num, occupancy]
        test_occupancy = [block_num, occupancy]
        
        print(f"\n🧪 TEST BLOCK OCCUPANCY:")
        print(f"   Sending: {test_occupancy}")
        
        # Simulate receiving the occupancy command
        self._process_message({
            'command': 'block_occupancy',
            'value': test_occupancy
        }, "TEST_SIMULATION")
        
        # Also test the dictionary format
        test_occupancy_dict = {block_num: occupancy}
        print(f"\n🧪 TEST BLOCK OCCUPANCY (dict format):")
        print(f"   Sending: {test_occupancy_dict}")
        
        self._process_message({
            'command': 'block_occupancy',
            'value': test_occupancy_dict
        }, "TEST_SIMULATION")

# ---------------- Run Application ----------------
if __name__ == "__main__":
    manager = UI_Variables.TrackDataManager()
    app = TrackModelUI(manager)
    tester = TrackModelTestUI(app, manager)
    
    # Store reference to test UI for refreshing
    app.tester_reference = tester

    # Start periodic output updates after a delay
    app.after(3000, app.start_output_updates)
    
    # Verify integration
    print("\n" + "="*60)
    print("SYSTEM INTEGRATION CHECK")
    print("="*60)
    print(f"Main UI manager: {app.data_manager}")
    print(f"Test UI manager: {tester.manager}") 
    print(f"Same instance: {app.data_manager is tester.manager}")
    print(f"Bidirectional data shared: {hasattr(manager, 'bidirectional_directions')}")
    print(f"Socket server running: {app.server.running}")
    print(f"Allowed connections: {app.server.allowed_connections}")
    print(f"Connected clients: {list(app.server.connected_clients.keys())}")
    print("="*60 + "\n")
    
    # Test sending data (optional - uncomment to test immediately)
    # print("🧪 Testing data transmission...")
    # app.send_all_outputs()
    
    tester.lift()
    app.mainloop()