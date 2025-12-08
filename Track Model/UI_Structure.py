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
        # GREEN LINE SWITCHES
        self.switch_routing_green = {
            12: {"normal": 13, "reverse": 13},    # Switch housed at 12: (12-13; 1-13)
            28: {"normal": 29, "reverse": 150},   # Switch housed at 28: (28-29; 150-28)
            57: {"normal": 58, "reverse": 151},   # Switch at 58: controls 57→58 (normal) or 57→yard 151 (reverse)
            62: {"normal": 63, "reverse": 63},    # Switch housed at 62: from main line or yard to 63
            76: {"normal": 78, "reverse": 101},   # Switch housed at 76: controls junction at 77 (76-77-78 or 76-77-101)
            85: {"normal": 86, "reverse": 100}    # Switch housed at 85: (85-86; 100-85)
        }
        
        # RED LINE SWITCHES
        # Based on Excel: Switch notation (X-Y; Z-W) means block can route to Y (normal) or W (reverse)
        self.switch_routing_red = {
            9: {"normal": 10, "reverse": 75},     # Yard: continue to 10 (normal) or to yard block 75 (reverse)
            15: {"normal": 16, "reverse": 1},     # Loop switch: 15→16 (normal) or 15→1 (reverse, closes loop)
            27: {"normal": 28, "reverse": 76},    # Branch: 27→28 (normal) or 27→76 (reverse, to end section)
            32: {"normal": 33, "reverse": 72},    # Branch: 32→33 (normal) or 32→72 (reverse, backward jump)
            38: {"normal": 39, "reverse": 71},    # Branch: 38→39 (normal) or 38→71 (reverse, backward jump)
            43: {"normal": 44, "reverse": 67},    # Branch: 43→44 (normal) or 43→67 (reverse, backward jump)
            52: {"normal": 53, "reverse": 66},    # Loop switch: 52→53 (normal) or 52→66 (reverse, forward jump)
            # Bidirectional entries for loop switches (allows entering from either direction)
            1: {"normal": 2, "reverse": 16},      # From block 1: go to 2 (normal) or to 16 via switch 15 (reverse)
            16: {"normal": 17, "reverse": 15},    # From block 16: go to 17 (normal) or to 15 (reverse, can then go to 1)
            53: {"normal": 54, "reverse": 52},    # From block 53: go to 54 (normal) or back to 52 via switch (reverse)
            66: {"normal": 67, "reverse": 52},    # From block 66: go to 67 (normal) or back to 52 via switch (reverse)
        }
        
        # Default to Green Line switches (will be updated based on selected line)
        self.switch_routing = self.switch_routing_green
        self.crossing_blocks = set()
        # Traffic light blocks:
        # Green Line: {1, 62, 76, 100, 150}
        # Red Line: {1, 10, 15, 28, 32, 39, 43, 53, 66, 67, 71, 72, 76}
        self.light_states = {1, 10, 15, 28, 32, 39, 43, 53, 62, 66, 67, 71, 72, 76, 100, 150}
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
                pass
                # print("[UI] Green Line Track Data successfully loaded on launch.")
            else:
                pass
                # print("[UI] Failed to load Green Line Track Data.")
        else:
            pass
            # print("[UI] Track Data.xlsx not found in directory.")

        # Initialize managers - AFTER data is loaded
        self.file_manager = FileUploadManager(self.data_manager, ui_reference=self)
        self.heater_manager = HeaterSystemManager(self.data_manager)
        self.diagram_drawer = TrackDiagramDrawer(self, self.data_manager)


        # --- Auto-load Green Line track data from Excel on startup ---
        if not self.file_manager.auto_load_green_line():
            pass
            # print("[UI]  Green Line data could not be loaded automatically.")

        # --- POPULATE INFRASTRUCTURE SETS AFTER LOADING ---
        self._populate_infrastructure_sets()

        # Initialize traffic light states and occupancy for all blocks
        for b in self.data_manager.blocks:
            if not hasattr(b, "traffic_light_state"):
                b.traffic_light_state = 0
            if not hasattr(b, "occupancy"):
                b.occupancy = 0
            if not hasattr(b, "crossing_state"):
                b.crossing_state = False  # False = inactive/up, True = active/down

        # Set initial environmental temperature
        if self.data_manager.environmental_temp is None:
            self.data_manager.environmental_temp = 70.0
            # print("[Heater] Initial environmental temperature set to 70.0°F")
        
        # Initialize all block temperatures to environmental temp
        self.heater_manager.initialize_all_temperatures()

        # NOW initialize ticket sales AFTER blocks are loaded
        self._initialize_station_ticket_sales()

        self.update_station_boarding_data()
        
        # Track previous authority values to detect when it reaches 0
        self._previous_train_authority = {}
        
        # Track which station block each train is stopped at (for beacon transmission on departure)
        self._trains_stopped_at_station = {}  # train_id -> block_number

        # Start monitoring station occupancy AFTER everything is ready
        self.after(1000, self.monitor_station_occupancy)
        
        # Start monitoring train authority for passenger boarding
        self.after(2000, self.monitor_train_authority_for_boarding)

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
                    pass
                    # Here you could apply the failure to the backend (TrackDataManager, etc.)
                    # print(f"Applying {failure_name} failure to Block {block}")
                    # Example if you have data_manager:
                    # self.data_manager.set_failure(block, failure_name)

                else:
                    messagebox.showinfo("Cancelled", f"No block selected for {failure_name}.")
                    var.set(False)  # Uncheck if cancelled

            else:
                pass
                # Failure unchecked (cleared)
                # print(f"{failure_name} states updated")
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
        # Data Upload Section (moved from right side)
        # ============================================================
        plc_card = self.make_card(parent, "Data Upload")
        
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
        # print(f"[UI] Switching to {selected}")
        
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
                # print(f"[UI]  {selected} data successfully loaded.")
                
                # Update switch routing based on selected line
                if selected == "Red Line":
                    self.switch_routing = self.switch_routing_red
                    # print(f"[UI]  Switched to Red Line switch routing ({len(self.switch_routing_red)} switches)")
                else:  # Green Line
                    self.switch_routing = self.switch_routing_green
                    # print(f"[UI]  Switched to Green Line switch routing ({len(self.switch_routing_green)} switches)")
                
                # Update the track diagram image
                try:
                    # Store the current image file for future resizes
                    self.current_image_file = image_file
                    
                    # Update the background image
                    self.update_background_image()
                except Exception as e:
                    pass
                    # print(f" Could not load {image_file}: {e}")
                
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
                    
                    # print(f"[UI]  Rebuilt bidirectional controls for {selected}")
                
                # Refresh the tables to show the new data
                self.refresh_track_data_table()
                self.refresh_track_system_table()
                
                # Update station boarding data
                self.update_station_boarding_data()
                
                # Reinitialize station ticket sales
                self._initialize_station_ticket_sales()
                
                # Reinitialize station beacons with 128-bit arrays
                self.initialize_station_beacons()
                
                # print(f"[UI]  Successfully switched to {selected}")
                
            else:
                pass
                # print(f"[UI] Failed to load {selected} data.")
                
        except Exception as e:
            print(f"[UI]  Error switching to {selected}: {e}")
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
        
        # # print("[UI] Track Data table refreshed")
    
    def refresh_track_system_table(self):
        """Refresh the Track Elements table."""
        self.update_track_system_table()
        # # print("[UI] Track System table refreshed")


    # ============================================================
    # Add these methods to handle block occupancy
    # ============================================================

    def update_train_info(self, event):
        """Display train information in the Train Details Panel."""
        try:
            idx = self.train_combo.current()
            train_name = self.train_combo.get()
            
            # Get train data with safe defaults
            occ = self.data_manager.train_occupancy[idx] if idx < len(self.data_manager.train_occupancy) else 0
            spd = self.data_manager.commanded_speed[idx] if idx < len(self.data_manager.commanded_speed) else 0
            auth = self.data_manager.commanded_authority[idx] if idx < len(self.data_manager.commanded_authority) else 0
            
            # Update the display
            self.train_info.config(
                text=f"Occupancy: {occ} People\nCommanded Speed: {spd} m/s\nCommanded Authority: {auth} blocks"
            )
            
        except Exception as e:
            pass
        
        
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
        # #     print(" Could not load Red and Green Line.png for Block/Station tab:", e)
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
                # print(" Could not load Red and Green Line.png for occupancy view:", e)
                self.block_canvas = tk.Canvas(self.block_frame, bg="white", height=450, width=550)
                self.block_canvas.pack(fill="x", padx=10, pady=10)

            # Load Train Image
            if not hasattr(self, "train_icon"):
                try:
                    train_img = Image.open("Train_Right.png").resize((40, 40), Image.LANCZOS)
                    self.train_icon = ImageTk.PhotoImage(train_img)
                except Exception as e:
                    # print(" Could not load Train_Right.png:", e)
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
            # print(" No train icon available")
            return
        if canvas is None:
            # print(" No canvas available")
            return
        if items_list is None:
            # print(" No items_list available")
            return

        # Remove previous train images
        for item in items_list:
            canvas.delete(item)
        items_list.clear()

        # # print("🔍 === Checking Block Occupancy ===")
        occupied_blocks = []
        
        # Check all blocks for occupancy
        for i, block in enumerate(self.data_manager.blocks):
            block_num = i + 1
            occupancy_value = getattr(block, 'occupancy', 0)
            if occupancy_value != 0:
                occupied_blocks.append(block_num)
                # # print(f"   Block {block_num}: OCCUPIED (value: {occupancy_value})")
        
        # # print(f"   Found {len(occupied_blocks)} occupied blocks: {occupied_blocks}")
        
        trains_drawn = 0
        # Draw trains for occupied blocks
        for block_num in occupied_blocks:
            coords = self.block_positions_occupancy.get(block_num)
            if coords:
                x, y = coords
                item = canvas.create_image(x, y, image=self.train_icon, anchor="center")
                items_list.append(item)
                trains_drawn += 1
                # # print(f"    Drawing train at block {block_num}, coordinates: {coords}")
            else:
                pass
                # print(f"    Block {block_num} occupied but no coordinates available")

        # # print(f" Total trains drawn: {trains_drawn}")
        # # print("=====================================")

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
            pass
            # print(f"[WARN] Could not load Train_Right.png: {e}")


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
                1: (478, 22),
                2: (488, 31),
                3: (495, 42),
                4: (506, 59),
                5: (515, 67),
                6: (535, 71),
                # Blocks 7-16: adjusting by +115 instead of +265 (shifted 150 left)
                7: (438 + 115, 68),   # 553
                8: (458 + 115, 60),   # 573
                9: (462 + 115, 34),   # 577
                10: (434 + 115, 24),  # 549
                11: (403 + 115, 18),  # 518
                12: (376 + 115, 15),  # 491
                13: (330 + 115, 15),  # 442
                14: (321 + 115, 15),  # 433
                15: (312 + 115, 15),  # 424
                16: (303 + 115, 15),  # 417
                # Blocks 17-28: same +115 compensation
                17: (274 + 115, 18),  # 386
                18: (261 + 115, 23),  # 374
                19: (252 + 115, 33),  # 364
                20: (248 + 115, 48),  # 358
                21: (247 + 115, 65),  # 359
                22: (247 + 115, 74),  # 359
                23: (247 + 115, 83),  # 358
                24: (247 + 115, 92),  # 358
                25: (247 + 115, 101),  # 359
                26: (247 + 115, 110), # 357
                27: (247 + 115, 119), # 358
                28: (247 + 115, 128), # 359
                # Blocks 29-57: +5 compensation (moved 10 left from +15)
                29: (357 + 5, 138),  # 365
                30: (357 + 5, 147),  # 364
                31: (357 + 5, 156),  # 364
                32: (357 + 5, 165),  # 365
                33: (359 + 5, 179),  # 366
                34: (365 + 5, 194),  # 370
                35: (377 + 5, 206),  # 379
                36: (394 + 5, 210),  # 403
                37: (402 + 5, 210),  # 409
                38: (410 + 5, 210),  # 415
                39: (418 + 5, 210),  # 420
                40: (426 + 5, 210),  # 426
                41: (434 + 5, 210),  # 432
                42: (442 + 5, 210),  # 438
                43: (450 + 5, 210),  # 444
                44: (458 + 5, 210),  # 452
                45: (466 + 5, 210),  # 459
                46: (474 + 5, 210),  # 465
                47: (482 + 5, 210),  # 472
                48: (490 + 5, 210),  # 478
                49: (498 + 5, 210),  # 482
                50: (506 + 5, 210),  # 490
                51: (514 + 5, 210),  # 501
                52: (522 + 5, 210),  # 507
                53: (530 + 5, 210),  # 514
                54: (538 + 5, 210),  # 521
                55: (546 + 5, 210),  # 533
                56: (554 + 5, 210),  # 545
                57: (562 + 5, 210),  # 556
                # Blocks 58-62: Updated coordinates
                58: (599, 211),
                59: (614, 217),
                60: (626, 228),
                61: (637, 241),
                62: (646, 258),
                # Blocks 63-76: +122 compensation (moved 3 left from +125)
                63: (528 + 122, 280),  # 653
                64: (528 + 122, 296),  # 653
                65: (528 + 122, 314),  # 652
                66: (528 + 122, 334),  # 652
                67: (528 + 122, 352),  # 652
                68: (528 + 122, 372),  # 652
                69: (528 + 122, 410),  # 653
                70: (525 + 122, 430),  # 647
                71: (517 + 122, 451),  # 640
                72: (506 + 122, 466),  # 628
                73: (491 + 122, 478),  # 613
                74: (456 + 122, 484),  # 578
                75: (425 + 122, 484),  # 547
                76: (396 + 122, 484),  # 522
                # Blocks 77-104: +1 compensation (moved 2 right from -1) - PERFECT!
                77: (477 + 1, 484),  # 478
                78: (469 + 1, 484),  # 465
                79: (461 + 1, 484),  # 455
                80: (453 + 1, 484),  # 447
                81: (445 + 1, 484),  # 439
                82: (437 + 1, 484),  # 431
                83: (429 + 1, 484),  # 425
                84: (421 + 1, 484),  # 416
                85: (413 + 1, 484),  # 409

                86: (378 + 1, 484),  # 380
                87: (367 + 1, 484),  # 369
                88: (358 + 1, 484),  # 359
                89: (338 + 1, 483),  # 338
                90: (328 + 1, 471),  # 329
                91: (322 + 1, 453),  # 321
                92: (322 + 1, 435),  # 323
                93: (325 + 1, 420),  # 326
                94: (332 + 1, 409),  # 331
                95: (346 + 1, 404),  # 347
                96: (358 + 1, 416),  # 359
                97: (364 + 1, 432),  # 363
                98: (367 + 1, 452),  # 368
                99: (369 + 1, 464),  # 368
                100: (376 + 1, 472), # 376

                101: (498 + 1, 468), # 497
                102: (520 + 1, 452), # 519
                103: (533 + 1, 452), # 531
                104: (546 + 1, 452), # 544

                # Blocks 105-150: +118 compensation (moved 2 right from +116) - PERFECT!
                105: (452 + 118, 452), # 570
                106: (472 + 118, 445), # 590
                107: (488 + 118, 432), # 606
                108: (500 + 118, 415), # 617
                109: (507 + 118, 394), # 623

                110: (508 + 118, 368), # 624
                111: (508 + 118, 359), # 622
                112: (508 + 118, 350), # 623
                113: (508 + 118, 341), # 623
                114: (508 + 118, 332), # 624
                115: (508 + 118, 323), # 625
                116: (508 + 118, 314), # 624

                117: (506 + 118, 291), # 623
                118: (499 + 118, 272), # 617
                119: (486 + 118, 254), # 604
                120: (469 + 118, 243), # 587
                121: (450 + 118, 238), # 568

                122: (438 + 118, 237), # 545
                123: (430 + 118, 237), # 540
                124: (422 + 118, 237), # 534
                125: (414 + 118, 237), # 527
                126: (406 + 118, 237), # 521
                127: (398 + 118, 237), # 515
                128: (390 + 118, 237), # 508
                129: (382 + 118, 237), # 503
                130: (374 + 118, 237), # 495
                131: (366 + 118, 237), # 488
                132: (358 + 118, 237), # 479
                133: (350 + 118, 237), # 474
                134: (342 + 118, 237), # 465
                135: (334 + 118, 237), # 458
                136: (326 + 118, 237), # 452
                137: (318 + 118, 237), # 445
                138: (310 + 118, 237), # 436
                139: (302 + 118, 237), # 431
                140: (294 + 118, 237), # 420
                141: (286 + 118, 237), # 412
                142: (278 + 118, 237), # 398
                143: (270 + 118, 237), # 390

                144: (249 + 118, 236), # 367
                145: (232 + 118, 230), # 350
                146: (223 + 118, 219), # 339
                147: (220 + 118, 199), # 337
                148: (220 + 118, 188), # 337
                149: (220 + 118, 177), # 337
                150: (229 + 118, 152), # 345
            }
            
            # Define block marker positions for Red Line (blocks 1-76 for now)
            self.block_marker_positions_red = {
                1: (558, 126),
                2: (567, 122),
                3: (576, 118),
                4: (581, 95),
                5: (589, 86),
                6: (601, 80),
                7: (628, 80),
                8: (644, 85),
                9: (659, 94),
                10: (654, 125),
                11: (639, 131),
                12: (621, 133),
                13: (582, 133),
                14: (565, 133),
                15: (549, 133),
                
                16: (532, 133),
                17: (524, 133),
                18: (516, 133),
                19: (508, 133),
                20: (500, 133),
                21: (487, 135),
                22: (478, 139),
                23: (469, 145),

                24: (466, 166),
                25: (466, 174),
                26: (466, 182),
                27: (466, 190),
                28: (466, 198),
                29: (466, 206),
                30: (466, 214),
                31: (466, 222),
                32: (466, 230),
                33: (466, 238),
                34: (466, 246),
                35: (466, 254),
                36: (466, 262),
                37: (466, 270),
                38: (466, 278),
                39: (466, 286),
                40: (466, 294),
                41: (466, 302),
                42: (466, 310),
                43: (466, 318),
                44: (466, 326),
                45: (466, 334),

                46: (466, 348),
                47: (455, 367),
                48: (435, 380),
                49: (403, 384),
                50: (394, 384),
                51: (385, 384),
                52: (376, 384),
                53: (367, 384),
                54: (358, 384),

                55: (330, 379),
                56: (311, 362),
                57: (301, 340),
                58: (303, 310),
                59: (310, 297),
                60: (320, 286),
                61: (343, 292),
                62: (351, 317),
                63: (354, 341),
                64: (357, 367),
                65: (365, 373),
                66: (374, 377),

                67: (454, 318),
                68: (441, 304),
                69: (441, 296),
                70: (441, 288),
                71: (454, 274),
                72: (454, 225),
                73: (441, 214),
                74: (441, 206),
                75: (441, 198),
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
            pass
            # print(" Could not load background Red and Green Line.png:", e)

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
            # print(" Train icon loaded successfully")
        except Exception as e:
            pass
            # print(f" Could not load Train_Right.png: {e}")

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
                    # print(f" Failed to load {path}: {e}")
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
        
        # print("[UI] Populating infrastructure sets from Excel data...")
        
        for block_num, infrastructure in infra_map.items():
            infrastructure_upper = str(infrastructure).upper()
            
            # Check for switches
            if "SWITCH" in infrastructure_upper:
                self.switch_blocks.add(block_num)
                # print(f"   Found switch at block {block_num}")
                
                # Initialize switch direction for this block
                if 1 <= block_num <= len(self.data_manager.blocks):
                    block = self.data_manager.blocks[block_num - 1]
                    if not hasattr(block, 'switch_direction'):
                        # SPECIAL CASE: Block 62 must default to 'reverse' for yard spawning
                        if block_num == 62:
                            block.switch_direction = 'reverse'  # Yard→63 position
                        else:
                            block.switch_direction = 'normal'  # Default direction
                    # Also initialize in switch_states dictionary
                    self.switch_states[block_num] = getattr(block, 'switch_direction', 'normal')
            
            # Check for crossings
            if "CROSSING" in infrastructure_upper:
                self.crossing_blocks.add(block_num)
                # print(f"   Found crossing at block {block_num}")
            
            # Check for stations
            if "STATION" in infrastructure_upper:
                self.station_blocks.add(block_num)
                # print(f"  🚉 Found station at block {block_num}")
        
        # print(f"[UI] Infrastructure summary:")
        # print(f"  Switches: {sorted(self.switch_blocks)}")
        # print(f"  Crossings: {sorted(self.crossing_blocks)}")
        # print(f"  Stations: {sorted(self.station_blocks)}")
        # print(f"  Signals (hardcoded): {sorted(self.light_states)}")

    def start_temperature_update_loop(self):
        """Start periodic temperature updates (every 1 second)"""
        try:
            if hasattr(self, 'heater_manager'):
                # Update all temperatures and heater states
                self.heater_manager.update_all_temperatures()
                
                # The refresh_ui method will handle updating the display
                # No need to call it separately here since it's already on a timer
                
        except Exception as e:
            pass
            # print(f" Temperature update error: {e}")
        
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
            # print("[UI] Initialized bidirectional directions for Red Line")
        else:
            # Green Line bidirectional blocks (default)
            self.data_manager.bidirectional_directions = {
                "Blocks 13-28": 0,
                "Blocks 77-85": 0  # N section - bidirectional blocks
            }
            # print("[UI] Initialized bidirectional directions for Green Line")

    def _initialize_station_ticket_sales(self):
        """Initialize random ticket sales and boarding/disembarking for all stations."""
        # print("🎫 === INITIALIZING STATION DATA ===")
        
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
                
                # print(f"   Station {station_name} (Block {block_num}): {ticket_count} tickets, {boarding_count} boarding")
        
        # print("   === STATION DATA INITIALIZATION COMPLETE ===\n")
        
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
                        pass
                        # print(f"🎫 {station_name} (Block {block_num}): {current_tickets} → {self.data_manager.ticket_sales[idx]} (+{new_tickets})")

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
        # print(f"[DEBUG] update_occupied_blocks_display called")
        
        if not hasattr(self, 'occupied_blocks_label'):
            # print("[DEBUG] occupied_blocks_label doesn't exist yet")
            return
            
        if not hasattr(self, 'data_manager') or not hasattr(self.data_manager, 'blocks'):
            # print("[DEBUG] data_manager or blocks not available")
            return
        
        # print(f"[DEBUG] Checking {len(self.data_manager.blocks)} blocks for occupancy")
        occupied = []
        
        # Check all blocks for occupancy
        for i, block in enumerate(self.data_manager.blocks):
            # Initialize occupancy attribute if it doesn't exist
            if not hasattr(block, 'occupancy'):
                block.occupancy = 0
            
            # Special check for block 63
            if i == 62:  # Block 63 is at index 62
                pass
                # print(f"[DEBUG] Block 63 occupancy value: {block.occupancy}")
            
            if block.occupancy != 0:
                occupied.append(f"Block {i+1}: Train {block.occupancy}")
                # print(f"[DEBUG] Found occupied block {i+1} with train {block.occupancy}")
        
        # print(f"[DEBUG] Total occupied blocks found: {len(occupied)}")
        # print(f"[DEBUG] Occupied list: {occupied}")
        
        if occupied:
            display_text = "\n".join(occupied)
            self.occupied_blocks_label.config(
                text=display_text,
                fg="black"
            )
            # print(f"[DEBUG] Updated occupied blocks display with {len(occupied)} blocks")
            # print(f"[DEBUG] Display text: {display_text}")
        else:
            self.occupied_blocks_label.config(
                text="No blocks currently occupied",
                fg="gray"
            )
            # # print("[DEBUG] Set display to 'No blocks currently occupied'")
        
        # Force UI update
        try:
            self.occupied_blocks_label.update()
            # # print("[DEBUG] Forced label update")
        except Exception as e:
            pass
            # # print(f"[DEBUG] Could not force update: {e}")
            # print("")

    def log_to_terminal(self, message):
        """Log a message to the UI Event Log / Terminal"""
        for terminal in self.terminals:
            terminal.config(state="normal")
            terminal.insert("end", f"{message}\n")
            terminal.see("end")
            terminal.config(state="disabled")
    
    def update_switch_display(self):
        """Update the display of switch states in the UI."""
        # print(f"[DEBUG] update_switch_display called")
        
        # Update switch status labels if they exist
        if hasattr(self, 'switch_status_labels'):
            for block_num, label in self.switch_status_labels.items():
                if block_num in self.switch_states:
                    direction = self.switch_states[block_num]
                    label.config(text=f"Switch {block_num}: {direction}")
                    # print(f"[DEBUG] Updated switch display for block {block_num}: {direction}")
        
        # Update switch blocks in the data manager
        for block_num in self.switch_blocks:
            if 1 <= block_num <= len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_num - 1]
                if hasattr(block, 'switch_direction'):
                    pass
                    # print(f"[DEBUG] Block {block_num} switch direction: {block.switch_direction}")
        
        # Refresh the track data and system tables to show updated switch states
        try:
            self.refresh_track_data_table()
            self.refresh_track_system_table()
            # print("[DEBUG] Refreshed tables after switch update")
        except Exception as e:
            pass
            # print(f"[DEBUG] Could not refresh tables: {e}")


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
            
            # Set status text based on direction and group
            if group_name == "Blocks 13-28":
                # Use special text for Blocks 13-28
                if direction == 0:
                    status_text = "Left and Down"
                elif direction == 1:
                    status_text = "Up and Right"
                else:  # direction == 2
                    status_text = "--"
            else:
                # Use standard text for other groups (e.g., Blocks 77-85)
                if direction == 0:
                    status_text = "Left"
                elif direction == 1:
                    status_text = "Right"
                else:  # direction == 2
                    status_text = "--"
            
            self.bidir_controls[group_name].set(status_text)
    
    def determine_bidirectional_direction(self, group_name):
        """
        Determine the direction for bidirectional blocks based on traffic light states.
        
        For Green Line:
        - Blocks 13-28: Based on lights at blocks 1 and 150
          - Both red: "--"
          - Light 1 not red AND Light 150 red: "Left and Down"
          - Light 150 not red AND Light 1 red: "Up and Right"
          - Both not red: "--" (default, should not happen)
        
        - Blocks 77-85: Based on lights at blocks 76 and 100
          - Both red: "--"
          - Light 76 not red AND Light 100 red: "Left"
          - Light 100 not red AND Light 76 red: "Right"
          - Both not red: "--" (default, should not happen)
        
        Returns: 0 for Left/Left and Down, 1 for Right/Up and Right, 2 for "--"
        """
        if not hasattr(self.data_manager, 'blocks') or not self.data_manager.blocks:
            return 2  # Default to "--" if no data
        
        # Get traffic light states for the control blocks
        if group_name == "Blocks 13-28":
            # Blocks 13-28 controlled by lights at blocks 1 and 150
            light_1_state = 0
            light_150_state = 0
            
            if len(self.data_manager.blocks) > 0:  # Block 1 at index 0
                block_1 = self.data_manager.blocks[0]
                if hasattr(block_1, 'traffic_light_state'):
                    light_1_state = block_1.traffic_light_state
            
            if len(self.data_manager.blocks) > 149:  # Block 150 at index 149
                block_150 = self.data_manager.blocks[149]
                if hasattr(block_150, 'traffic_light_state'):
                    light_150_state = block_150.traffic_light_state
            
            # Apply logic
            light_1_red = (light_1_state == 0)
            light_150_red = (light_150_state == 0)
            
            if light_1_red and light_150_red:
                return 2  # Both red -> "--"
            elif not light_1_red and light_150_red:
                return 0  # Light 1 not red, Light 150 red -> "Left and Down"
            elif not light_150_red and light_1_red:
                return 1  # Light 150 not red, Light 1 red -> "Up and Right"
            else:
                return 2  # Both not red (should not happen) -> "--"
        
        elif group_name == "Blocks 77-85":
            # Blocks 77-85 controlled by lights at blocks 76 and 100
            light_76_state = 0
            light_100_state = 0
            
            if len(self.data_manager.blocks) > 75:  # Block 76 at index 75
                block_76 = self.data_manager.blocks[75]
                if hasattr(block_76, 'traffic_light_state'):
                    light_76_state = block_76.traffic_light_state
            
            if len(self.data_manager.blocks) > 99:  # Block 100 at index 99
                block_100 = self.data_manager.blocks[99]
                if hasattr(block_100, 'traffic_light_state'):
                    light_100_state = block_100.traffic_light_state
            
            # Apply logic
            light_76_red = (light_76_state == 0)
            light_100_red = (light_100_state == 0)
            
            if light_76_red and light_100_red:
                return 2  # Both red -> "--"
            elif not light_76_red and light_100_red:
                return 0  # Light 76 not red, Light 100 red -> "Left"
            elif not light_100_red and light_76_red:
                return 1  # Light 100 not red, Light 76 red -> "Right"
            else:
                return 2  # Both not red (should not happen) -> "--"
        
        # For any other groups (Red Line, etc.), default to Left
        return 0

    def toggle_bidirectional_direction(self, group_name):
        """Main UI toggle - now just a placeholder since Test UI controls"""
        # print(f" Main UI toggle for {group_name} - Test UI is the controller")

    def save_bidirectional_direction(self, group_name):
        """Main UI save - now just a placeholder"""
        # print(f" Main UI save for {group_name} - Test UI controls changes")

    def refresh_bidirectional_controls(self):
        """Refresh all bidirectional controls based on current switches and signals"""
        # # print(" Refreshing bidirectional controls based on switches and signals")
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
                # print(f"[MOVEMENT] Initialized tracking for {train_id} at block {current_block_num}")
            
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
                # Check if train has arrived at yard (marked while at block 57)
                if hasattr(self, 'trains_at_yard') and train_id in self.trains_at_yard:
                    # Train has arrived at yard - remove from service
                    # print(f" Train {train_id} Arrived at Yard - Removing from service")
                    
                    # Clear current block occupancy (block 57 where train is)
                    if current_block_num <= len(self.data_manager.blocks):
                        current_block = self.data_manager.blocks[current_block_num - 1]
                        current_block.occupancy = 0
                        self.send_block_occupancy_update(current_block_num, 0)
                    
                    # Remove from active trains
                    if train_id in self.data_manager.active_trains:
                        train_index = self.data_manager.active_trains.index(train_id)
                        self.data_manager.active_trains.pop(train_index)
                        if train_index < len(self.data_manager.train_locations):
                            self.data_manager.train_locations.pop(train_index)
                        if train_index < len(self.data_manager.commanded_speed):
                            self.data_manager.commanded_speed.pop(train_index)
                        if train_index < len(self.data_manager.commanded_authority):
                            self.data_manager.commanded_authority.pop(train_index)
                    
                    # Clean up train tracking data
                    if train_id in self.train_positions_in_block:
                        del self.train_positions_in_block[train_id]
                    if train_id in self.train_actual_speeds:
                        del self.train_actual_speeds[train_id]
                    if train_id in self.train_directions:
                        del self.train_directions[train_id]
                    if train_id in self.last_movement_update:
                        del self.last_movement_update[train_id]
                    
                    # Remove from yard arrival set
                    self.trains_at_yard.remove(train_id)
                    
                    # Update display
                    self.update_occupied_blocks_display()
                    
                    continue  # Skip to next train
                
                # Move to next block
                next_block = self.get_next_block(current_block_num, train_idx)
                
                if next_block and next_block <= len(self.data_manager.blocks):
                    # Clear current block occupancy
                    if current_block_num <= len(self.data_manager.blocks):
                        current_block = self.data_manager.blocks[current_block_num - 1]
                        current_block.occupancy = 0
                        # print(f"[MOVEMENT] {train_id} leaving block {current_block_num}")
                    
                    # Set new block occupancy
                    new_block = self.data_manager.blocks[next_block - 1]
                    train_num = int(train_id.split('_')[1]) if '_' in train_id else int(train_id.replace('Train', '').strip())
                    new_block.occupancy = train_num
                    
                    # Update train location
                    self.data_manager.train_locations[train_idx] = next_block
                    
                    # Reset position in new block (account for overflow)
                    overflow = self.train_positions_in_block[train_id] - block_length
                    self.train_positions_in_block[train_id] = overflow
                    
                    # print(f"[MOVEMENT] {train_id} entered block {next_block} (speed: {actual_speed:.1f} m/s)")
                    
                    # Send occupancy updates to other modules
                    self.send_block_occupancy_update(current_block_num, 0)
                    self.send_block_occupancy_update(next_block, train_num)
                    
                    # Update the display
                    self.update_occupied_blocks_display()
                else:
                    pass
                    # print(f"[MOVEMENT] {train_id} reached end of authority at block {current_block_num}")
            
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
        # DEBUG: Log when train reaches critical switch blocks
        if current_block in [1, 15, 16, 52, 53, 66]:
            self.log_to_terminal(f"\n{'='*60}")
            self.log_to_terminal(f"[SWITCH DEBUG] Block {current_block}: train_idx={train_idx}")
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                train_mode = self.train_directions.get(train_id, 'forward') if hasattr(self, 'train_directions') else 'N/A'
                self.log_to_terminal(f"[SWITCH DEBUG]   Train {train_id}, mode={train_mode}")
            current_line = getattr(self, 'selected_line', None)
            line_name = current_line.get() if current_line else 'None'
            self.log_to_terminal(f"[SWITCH DEBUG]   Current line={line_name}")
            self.log_to_terminal(f"{'='*60}\n")
        
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
                # print(f"[AUTHORITY] {train_id} has reached authority limit ({authority} blocks)")
                return None  # Stop at authority limit
            
            # Increment blocks traveled
            self.train_blocks_traveled[train_id] += 1
        
        # ============================================================
        # SPECIAL ROUTING RULES - BIDIRECTIONAL AND SWITCHES
        # ============================================================
        
        
        # RULE 1: End of line - Block 150 goes to 28 (GREEN LINE ONLY)
        if current_block == 150:
            # Check if we're on Green Line (block 150 only exists on Green Line)
            current_line = getattr(self, 'selected_line', None)
            is_green_line = current_line and current_line.get() == "Green Line"
            
            if is_green_line:
                # Set backward loop mode when entering from 150
                if train_idx < len(self.data_manager.active_trains):
                    train_id = self.data_manager.active_trains[train_idx]
                    self.train_directions[train_id] = 'backward_loop'
                # print(f"[ROUTING] GREEN LINE: Block 150 → 28 (End of line return, entering backward loop)")
                return 28  # Go to 28 from 150
            
            # If somehow on Red Line at block 150 (shouldn't happen), just continue forward
            return current_block + 1
        
        # RULE 1b: Switch housed at block 28 controls routing from 28
        # GREEN LINE: SWITCH (28-29; 150-28) - can route to 150
        # RED LINE: SWITCH (27-28; 27-76) - different switch, normal forward routing
        # From 150 (Green Line only): Block 150 → 28 → 27, then continues backward up the track
        elif current_block == 28:
            # Check current line
            current_line = getattr(self, 'selected_line', None)
            is_green_line = current_line and current_line.get() == "Green Line"
            
            # Check if this train is in backward loop mode (coming from 150)
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for Red Line backward mode FIRST
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Red Line backward mode - continue backward to 27
                    # print(f"[ROUTING] RED LINE backward: Block 28 → 27")
                    return 27
                
                # Check for Green Line backward loop mode (coming from 150) - GREEN LINE ONLY
                if is_green_line and self.train_directions.get(train_id) == 'backward_loop':
                    # Train came from 150 → 28, now continue backward to 27
                    # Stay in backward_loop mode to continue backward through the track
                    # print(f"[ROUTING] GREEN LINE backward loop (from 150): Block 28 → 27 (continuing backward)")
                    return 27  # Continue backward to 27, don't exit to 29
            
            # Normal forward routing (coming from block 27)
            # GREEN LINE: Check switch for routing to 150 or 29
            if is_green_line:
                if len(self.data_manager.blocks) > 27:
                    block_28 = self.data_manager.blocks[27]  # Switch housed at block 28 (index 27)
                    if hasattr(block_28, 'switch_state'):
                        if block_28.switch_state:  # True = Normal = To block 29
                            return 29  # Continue forward
                        else:  # False = Reverse = Loop to 150
                            # Set backward loop mode to continue from 150
                            if train_idx < len(self.data_manager.active_trains):
                                train_id = self.data_manager.active_trains[train_idx]
                                self.train_directions[train_id] = 'backward_loop'
                            # print(f"[ROUTING] GREEN LINE: Block 28 → 150 (Loop via switch 28)")
                            return 150  # Send to 150
            
            # RED LINE or default: continue to block 29
            return 29

        # RULE 2: Switch housed at block 12 controls junction at blocks 1, 12, and 13
        # Excel: SWITCH (12-13; 1-13)
        # Position "12-13" (True/Normal): At block 13, enter backward loop → 12 → 11 → ... → 1 → 13
        # Position "1-13" (False/Reverse): Allows direct route 1 → 13
        
        elif current_block == 13:
            # Check if train is in backward loop mode (from 150→28→27→...→13)
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for Red Line backward mode FIRST
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Red Line backward mode - continue backward
                    next_block = current_block - 1
                    # print(f"[ROUTING] RED LINE backward: Block {current_block} → {next_block}")
                    return next_block
                
                # Check for Green Line backward loop modes
                if self.train_directions.get(train_id) == 'backward_loop':
                    # Continue backward loop from 13 to 12
                    # print(f"[ROUTING] Backward loop (150): Block 13 → 12")
                    return 12
                
                # Check if train is in backward loop from switch 12 (13→12→...→1→13)
                if self.train_directions.get(train_id) == 'backward_loop_12':
                    # Continue backward through loop
                    # print(f"[ROUTING] Backward loop (switch 12): Block 13 → 12")
                    return 12
            
            # Check switch at block 12 to determine routing from block 13
            if len(self.data_manager.blocks) > 11:
                block_12 = self.data_manager.blocks[11]  # Switch housed at block 12 (index 11)
                if hasattr(block_12, 'switch_state'):
                    if block_12.switch_state:  # True = "12-13" = Enter backward loop
                        # Set backward loop mode for switch 12
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            self.train_directions[train_id] = 'backward_loop_12'
                        # print(f"[ROUTING] Block 13 → 12 (Entering backward loop via switch 12)")
                        return 12
                    else:  # False = "1-13" = Normal forward
                        return 14  # Continue forward normally
            return 14  # Default forward
        
        # RED LINE RULE: Block 9 - Yard access (RED LINE ONLY)
        # Switch housed at block 9 controls yard access
        # Only affects trains coming FROM block 8 (forward direction)
        # Trains coming FROM block 10 (backward) ignore the switch
        elif current_block == 9:
            # Check current line
            current_line = getattr(self, 'selected_line', None)
            is_green_line = current_line and current_line.get() == "Green Line"
            is_red_line = current_line and current_line.get() == "Red Line"
            
            # Check if train is in any backward mode FIRST (Green Line or Red Line)
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for Green Line backward loop mode (GREEN LINE ONLY)
                if is_green_line and self.train_directions.get(train_id) == 'backward_loop':
                    # Green Line backward loop - continue backward from 9 to 8
                    # print(f"[ROUTING] GREEN LINE backward loop: Block 9 → 8 (continuing backward)")
                    return 8
                
                # Check for Red Line backward mode
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Train is in backward mode (coming from block 10)
                    # Ignore yard switch and continue backward to block 8
                    # print(f"[ROUTING] RED LINE backward: Block 9 → 8 (ignoring yard switch)")
                    return 8
            
            # Not in backward mode - check for Red Line yard switch logic
            if is_red_line:
                # Train is going forward (from block 8)
                # Check yard switch at block 9
                if len(self.data_manager.blocks) > 8:
                    block_9 = self.data_manager.blocks[8]  # Switch housed at block 9 (index 8)
                    if hasattr(block_9, 'switch_state'):
                        if not block_9.switch_state:  # False = Normal = Continue on main line
                            # print(f"[ROUTING] RED LINE: Block 9 → 10 (continue on main line)")
                            return 10  # Continue to 10
                        else:  # True = To Yard (swapped logic to match display)
                            # Train is going to yard - mark for removal
                            if train_idx < len(self.data_manager.active_trains):
                                train_id = self.data_manager.active_trains[train_idx]
                                # print(f" Train {train_id} Arrived at Yard (Red Line Block 9)")
                                
                                # Mark this train for removal (will be handled in train movement logic)
                                if not hasattr(self, 'trains_at_yard'):
                                    self.trains_at_yard = set()
                                self.trains_at_yard.add(train_id)
                            
                            # Return None to stop routing this train
                            # print(f"[ROUTING] RED LINE: Block 9 → Yard (train marked for removal)")
                            return None
            
            # Not Red Line OR default: continue to block 10
            return 10
        
        elif 2 <= current_block <= 12:
            # Check if train is in backward loop mode (from 150→28→27→...or from switch 12)
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for Red Line entering loop mode (from block 16→15→14→...→1)
                if self.train_directions.get(train_id) == 'entering_loop_15':
                    # Continue backward through loop
                    next_block = current_block - 1
                    # print(f"[ROUTING] RED LINE entering loop: Block {current_block} → {next_block}")
                    return next_block
                
                # Check for Red Line backward mode FIRST
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Red Line backward mode - continue backward
                    next_block = current_block - 1
                    # print(f"[ROUTING] RED LINE backward: Block {current_block} → {next_block}")
                    return next_block
                
                # Check for Green Line backward loop modes
                if self.train_directions.get(train_id) in ['backward_loop', 'backward_loop_12']:
                    # Continue backward
                    next_block = current_block - 1
                    # print(f"[ROUTING] Backward loop: Block {current_block} → {next_block}")
                    return next_block
            
            # Normal forward progression
            return current_block + 1
        
        elif current_block == 1:
            # Check if train is in backward loop mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for entering loop mode (from block 16→15→...→1)
                if self.train_directions.get(train_id) == 'entering_loop_15':
                    # Train completed the loop circuit, check switch to determine exit
                    if len(self.data_manager.blocks) > 14:
                        block_15 = self.data_manager.blocks[14]
                        switch_state = getattr(block_15, 'switch_state', None)
                        
                        self.log_to_terminal(f"[BLOCK 1 LOOP EXIT] Completed loop, switch_state={switch_state}")
                        
                        if switch_state:  # True = 1-16 connection, exit to 16
                            self.train_directions[train_id] = 'forward'
                            # print(f"[ROUTING] RED LINE: Completed loop circuit, block 1 → 16 (exiting loop)")
                            return 16
                        else:  # False = continue through loop again to 2
                            # print(f"[ROUTING] RED LINE: Continuing through loop, block 1 → 2")
                            return 2
                    
                    # Default: exit to 16
                    self.train_directions[train_id] = 'forward'
                    # print(f"[ROUTING] RED LINE: Completed loop circuit, block 1 → 16 (exiting loop)")
                    return 16
                
                # Check for Red Line backward mode FIRST
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Red Line backward mode - reached block 1
                    # Always exit backward mode and go to block 16 to rejoin main track
                    self.train_directions[train_id] = 'forward'
                    # print(f"[ROUTING] RED LINE: Reached block 1 in backward mode, exiting to main track → 16")
                    return 16
                
                # If in backward loop from 150, exit based on switch position
                if self.train_directions.get(train_id) == 'backward_loop':
                    self.train_directions[train_id] = 'forward'
                    
                    # Check switch at block 12 to determine where to exit
                    if len(self.data_manager.blocks) > 11:
                        block_12 = self.data_manager.blocks[11]  # Switch housed at block 12 (index 11)
                        if hasattr(block_12, 'switch_state'):
                            if not block_12.switch_state:  # False = "1-13" = Jump to 13
                                # print(f"[ROUTING] Exiting backward loop (150) at block 1 → 13 (via switch 12)")
                                return 13
                    
                    # Default: continue forward to 2
                    # print(f"[ROUTING] Exiting backward loop (150) at block 1 → 2")
                    return 2
                
                # If in backward loop from switch 12, exit to 13
                if self.train_directions.get(train_id) == 'backward_loop_12':
                    self.train_directions[train_id] = 'forward'
                    # print(f"[ROUTING] Exiting backward loop (switch 12) at block 1 → 13")
                    return 13
            
            # Not in any special mode - normal forward progression
            # Check for RED LINE - on Red Line, block 1 always continues to block 2 in normal forward mode
            current_line = getattr(self, 'selected_line', None)
            is_red_line = current_line and current_line.get() == "Red Line"
            
            if is_red_line:
                # Normal forward mode on Red Line: continue to block 2
                self.log_to_terminal(f"[BLOCK 1 NORMAL] Forward mode, continuing to block 2")
                # print(f"[ROUTING] RED LINE: Block 1 → 2 (normal forward)")
                return 2
            
            # Green Line: Check switch at block 12 for normal routing
            if len(self.data_manager.blocks) > 11:
                block_12 = self.data_manager.blocks[11]  # Switch housed at block 12 (index 11)
                if hasattr(block_12, 'switch_state'):
                    if not block_12.switch_state:  # False = "1-13" = Allow 1 → 13 shortcut
                        # print(f"[ROUTING] Block 1 → 13 (via switch 12 in '1-13' position)")
                        return 13
                    else:  # True = "12-13" = Normal forward progression
                        return 2
            
            # Default: normal forward to 2
            return 2
        
        # RULE 3: Blocks 14-27 - Handle backward loop mode from 150→28
        elif (14 == current_block) or (17 <= current_block <= 26):
            # Note: Block 27 is excluded and handled by specific rule below
            # Note: Blocks 15 and 16 are excluded and handled by specific rules below
            # Check if train is in backward loop mode (from 150→28→27→...)
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for Red Line entering loop mode (from block 16→15→14→...→1)
                if self.train_directions.get(train_id) == 'entering_loop_15':
                    # Continue backward through loop
                    next_block = current_block - 1
                    # print(f"[ROUTING] RED LINE entering loop: Block {current_block} → {next_block}")
                    return next_block
                
                # Check for Red Line backward mode FIRST
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Red Line backward mode - continue backward
                    next_block = current_block - 1
                    # print(f"[ROUTING] RED LINE backward: Block {current_block} → {next_block}")
                    return next_block
                
                # Check for Green Line backward loop mode
                if self.train_directions.get(train_id) == 'backward_loop':
                    # Continue backward
                    next_block = current_block - 1
                    # print(f"[ROUTING] Backward loop (150): Block {current_block} → {next_block}")
                    return next_block
            
            # Normal forward progression
            return current_block + 1
        
        # RULE 4: Switch housed at block 58 (Yard access from block 57)
        # Excel: SWITCH TO YARD (57-yard) - switch housed at block 58
        # Position 1: 57 → 58 (continue on main line)
        # Position 2: 57 → yard (train arrives at yard and is removed)
        # NOTE: This is GREEN LINE ONLY! On Red Line, block 57 is just normal track
        # RULE 4: Block 57 - Check for backward mode first
        elif current_block == 57:
            # Check if train is in Red Line backward mode FIRST
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # In backward mode: continue backward to 56
                    # print(f"[ROUTING] RED LINE backward: Block 57 → 56")
                    return 56
            
            # Not in backward mode - check if we're on Green Line for yard switch
            current_line = getattr(self, 'selected_line', None)
            is_green_line = current_line and current_line.get() == "Green Line"
            
            if is_green_line:
                # Green Line: Check yard switch at block 58
                if len(self.data_manager.blocks) > 57:
                    block_58 = self.data_manager.blocks[57]  # Switch housed at block 58 (index 57)
                    if hasattr(block_58, 'switch_state'):
                        if block_58.switch_state:  # True = Normal = Continue on main line
                            return 58  # Continue to 58
                        else:  # False = Reverse = Go to yard
                            # Train is going to yard - mark for removal
                            if train_idx < len(self.data_manager.active_trains):
                                train_id = self.data_manager.active_trains[train_idx]
                                # print(f" Train {train_id} Arrived at Yard (Green Line)")
                                
                                # Mark this train for removal (will be handled in train movement logic)
                                if not hasattr(self, 'trains_at_yard'):
                                    self.trains_at_yard = set()
                                self.trains_at_yard.add(train_id)
                            
                            # Return None to stop routing this train
                            return None
            
            # Red Line OR Green Line default: continue to block 58
            return 58
        
        # RULE 5: Block 62 - Check for backward mode
        elif current_block == 62:
            # Check if train is in Red Line backward mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # In backward mode: continue backward to 61
                    # print(f"[ROUTING] RED LINE backward: Block 62 → 61")
                    return 61
            
            # Normal forward mode: go to 63 (yard entry or normal)
            return 63
        
        # ============================================================
        # RED LINE BACKWARD LOOP: Block 66 → 52 → 51 → ... → 16
        # When train reaches block 66 (from switch 52 jump), it loops
        # back and travels backward until reaching switch 15 at block 16
        # ============================================================
        
        # RED LINE RULE 1: Block 66 - Check mode before routing
        elif current_block == 66:
            # Check if we're on Red Line
            current_line = getattr(self, 'selected_line', None)
            is_red_line = current_line and current_line.get() == "Red Line"
            
            if is_red_line:
                # Check if train is already in backward mode
                if train_idx < len(self.data_manager.active_trains):
                    train_id = self.data_manager.active_trains[train_idx]
                    train_mode = self.train_directions.get(train_id, 'forward')
                    
                    # DEBUG: Show mode at block 66
                    self.log_to_terminal(f"[BLOCK 66 DEBUG] Train mode = {train_mode}")
                    
                    if train_mode == 'red_backward_66_to_16':
                        # In backward mode (came from switch 52 jump), continue backward
                        # print(f"[ROUTING] RED LINE backward: Block 66 → 65 (continuing backward)")
                        return 65
                    else:
                        # In forward mode - arrived at 66 normally via 65→66
                        # Exit the loop and go to 52, set backward mode to continue backward from 52
                        self.train_directions[train_id] = 'red_backward_66_to_16'
                        # print(f"[ROUTING] RED LINE forward: Block 66 → 52 (exiting loop, entering backward mode)")
                        return 52
                
                # Default: exit to 52
                return 52
            else:
                # Green Line: normal progression
                return 67
        
        # RED LINE RULE 2: Blocks 52 down to 17 - Backward traversal
        elif 17 <= current_block <= 52:
            # Check if train is in Red Line backward mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                train_mode = self.train_directions.get(train_id, 'forward')
                
                # DEBUG: Log mode at block 52
                if current_block == 52:
                    self.log_to_terminal(f"[BLOCK 52 BACKWARD CHECK] Train mode = {train_mode}")
                
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # BACKWARD MODE: Check for backward-only switches
                    
                    # DEBUG: Confirm entering backward mode logic at block 52
                    if current_block == 52:
                        self.log_to_terminal(f"[BLOCK 52 BACKWARD] Entering backward mode logic, should go to block 51")
                    
                    # Switch 32 (backward-only): When at block 33 going backward
                    if current_block == 33:
                        self.log_to_terminal(f"[BLOCK 33 ENTRY] Entered block 33 routing (backward mode), train_idx={train_idx}")
                        
                        current_line = getattr(self, 'selected_line', None)
                        is_red_line = current_line and current_line.get() == "Red Line"
                        self.log_to_terminal(f"[BLOCK 33 LINE CHECK] is_red_line = {is_red_line}")
                        
                        # Get train info for logging
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            current_mode = self.train_directions.get(train_id, 'forward')
                            self.log_to_terminal(f"[BLOCK 33 MODE CHECK] Train {train_id} mode = {current_mode}")
                        
                        # Check Red Line switch routing directly (not self.switch_routing which may be set to Green)
                        has_switch_routing_red = hasattr(self, 'switch_routing_red')
                        switch_32_in_routing = 32 in self.switch_routing_red if has_switch_routing_red else False
                        self.log_to_terminal(f"[BLOCK 33 SWITCH CHECK] has_switch_routing_red = {has_switch_routing_red}")
                        self.log_to_terminal(f"[BLOCK 33 SWITCH CHECK] 32 in switch_routing_red = {switch_32_in_routing}")
                        
                        if is_red_line and has_switch_routing_red and switch_32_in_routing:
                            # Get the block object to check its switch_state
                            if len(self.data_manager.blocks) > 31:
                                block_32 = self.data_manager.blocks[31]  # Block 32 (index 31)
                                
                                # Check both switch_direction and switch_state
                                switch_direction = getattr(block_32, 'switch_direction', None)
                                switch_state_bool = getattr(block_32, 'switch_state', None)
                                
                                # Determine if switch is in reverse
                                is_reverse = False
                                if switch_state_bool is not None and isinstance(switch_state_bool, bool):
                                    is_reverse = switch_state_bool
                                elif switch_direction is not None:
                                    is_reverse = (switch_direction == "reverse")
                                
                                switch_state = "reverse" if is_reverse else "normal"
                            else:
                                switch_state = "normal"
                            self.log_to_terminal(f"[BLOCK 33 SWITCH STATE] switch_state = '{switch_state}'")
                            
                            if switch_state == "normal":
                                # Normal: 33→32 (continue backward)
                                self.log_to_terminal(f"[BLOCK 33 ROUTING] Normal position: 33 → 32 (continue backward)")
                                # print(f"[ROUTING] RED LINE backward: Block 33 → 32 (Switch 32 normal)")
                                return 32
                            else:  # reverse
                                # Reverse: 33→72 (backward jump), then enter forward mode for 72→73→74→75→76
                                if train_idx < len(self.data_manager.active_trains):
                                    train_id = self.data_manager.active_trains[train_idx]
                                    self.train_directions[train_id] = 'red_branch_32_to_76_forward'
                                    self.log_to_terminal(f"[BLOCK 33 ROUTING] Reverse position: 33 → 72, setting mode = 'red_branch_32_to_76_forward'")
                                # print(f"[ROUTING] RED LINE backward: Block 33 → 72 (Switch 32 reverse jump, entering forward mode)")
                                return 72
                        else:
                            self.log_to_terminal(f"[BLOCK 33 WARNING] Switch routing check failed - falling through")
                    
                    
                    # Switch 43 (backward-only): When at block 44 going backward
                    elif current_block == 44:
                        self.log_to_terminal(f"[BLOCK 44 ENTRY] Entered block 44 routing (backward mode), train_idx={train_idx}")
                        
                        current_line = getattr(self, 'selected_line', None)
                        is_red_line = current_line and current_line.get() == "Red Line"
                        self.log_to_terminal(f"[BLOCK 44 LINE CHECK] is_red_line = {is_red_line}")
                        
                        # Get train info for logging
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            current_mode = self.train_directions.get(train_id, 'forward')
                            self.log_to_terminal(f"[BLOCK 44 MODE CHECK] Train {train_id} mode = {current_mode}")
                        
                        # Check Red Line switch routing directly (not self.switch_routing which may be set to Green)
                        has_switch_routing_red = hasattr(self, 'switch_routing_red')
                        switch_43_in_routing = 43 in self.switch_routing_red if has_switch_routing_red else False
                        self.log_to_terminal(f"[BLOCK 44 SWITCH CHECK] has_switch_routing_red = {has_switch_routing_red}")
                        self.log_to_terminal(f"[BLOCK 44 SWITCH CHECK] 43 in switch_routing_red = {switch_43_in_routing}")
                        
                        if is_red_line and has_switch_routing_red and switch_43_in_routing:
                            # Get the block object to check its switch_state
                            if len(self.data_manager.blocks) > 42:
                                block_43 = self.data_manager.blocks[42]  # Block 43 (index 42)
                                
                                # Check both switch_direction and switch_state
                                switch_direction = getattr(block_43, 'switch_direction', None)
                                switch_state_bool = getattr(block_43, 'switch_state', None)
                                
                                # Determine if switch is in reverse
                                is_reverse = False
                                if switch_state_bool is not None and isinstance(switch_state_bool, bool):
                                    is_reverse = switch_state_bool
                                elif switch_direction is not None:
                                    is_reverse = (switch_direction == "reverse")
                                
                                switch_state = "reverse" if is_reverse else "normal"
                            else:
                                switch_state = "normal"
                            self.log_to_terminal(f"[BLOCK 44 SWITCH STATE] switch_state = '{switch_state}'")
                            
                            if switch_state == "normal":
                                # Normal: 44→43 (continue backward)
                                self.log_to_terminal(f"[BLOCK 44 ROUTING] Normal position: 44 → 43 (continue backward)")
                                # print(f"[ROUTING] RED LINE backward: Block 44 → 43 (Switch 43 normal)")
                                return 43
                            else:  # reverse
                                # Reverse: 44→67 (backward jump), then enter forward mode for 67→68→69→70→71
                                if train_idx < len(self.data_manager.active_trains):
                                    train_id = self.data_manager.active_trains[train_idx]
                                    self.train_directions[train_id] = 'red_branch_43_to_71_forward'
                                    self.log_to_terminal(f"[BLOCK 44 ROUTING] Reverse position: 44 → 67, setting mode = 'red_branch_43_to_71_forward'")
                                # print(f"[ROUTING] RED LINE backward: Block 44 → 67 (Switch 43 reverse jump, entering forward mode)")
                                return 67
                        else:
                            self.log_to_terminal(f"[BLOCK 44 WARNING] Switch routing check failed - falling through")
                    
                    
                    # Continue backward (decrementing block numbers)
                    next_block = current_block - 1
                    
                    # DEBUG: Log the routing decision for block 52
                    if current_block == 52:
                        self.log_to_terminal(f"[BLOCK 52 BACKWARD] Routing backward: 52 → {next_block}")
                    
                    # print(f"[ROUTING] RED LINE backward: Block {current_block} → {next_block}")
                    return next_block
            
            # FORWARD MODE: Check for forward-only switches
            current_line = getattr(self, 'selected_line', None)
            is_red_line = current_line and current_line.get() == "Red Line"
            
            # Switch 27 (forward-only): When at block 27 going forward
            if is_red_line and current_block == 27:
                self.log_to_terminal(f"[BLOCK 27 ENTRY] Entered block 27 routing, train_idx={train_idx}")
                self.log_to_terminal(f"[BLOCK 27 LINE CHECK] is_red_line = {is_red_line}")
                
                # Get train info for logging
                if train_idx < len(self.data_manager.active_trains):
                    train_id = self.data_manager.active_trains[train_idx]
                    current_mode = self.train_directions.get(train_id, 'forward')
                    self.log_to_terminal(f"[BLOCK 27 MODE CHECK] Train {train_id} mode = {current_mode}")
                
                # Check Red Line switch routing directly (not self.switch_routing which may be set to Green)
                has_switch_routing_red = hasattr(self, 'switch_routing_red')
                switch_27_in_routing = 27 in self.switch_routing_red if has_switch_routing_red else False
                self.log_to_terminal(f"[BLOCK 27 SWITCH CHECK] has_switch_routing_red = {has_switch_routing_red}")
                self.log_to_terminal(f"[BLOCK 27 SWITCH CHECK] 27 in switch_routing_red = {switch_27_in_routing}")
                
                if has_switch_routing_red and switch_27_in_routing:
                    # Get the block object to check its switch_state
                    if len(self.data_manager.blocks) > 26:
                        block_27 = self.data_manager.blocks[26]  # Block 27 (index 26)
                        
                        # Check both switch_direction and switch_state
                        switch_direction = getattr(block_27, 'switch_direction', None)
                        switch_state_bool = getattr(block_27, 'switch_state', None)
                        
                        # Determine if switch is in reverse
                        is_reverse = False
                        if switch_state_bool is not None and isinstance(switch_state_bool, bool):
                            is_reverse = switch_state_bool
                        elif switch_direction is not None:
                            is_reverse = (switch_direction == "reverse")
                        
                        switch_state = "reverse" if is_reverse else "normal"
                    self.log_to_terminal(f"[BLOCK 27 SWITCH STATE] switch_state = '{switch_state}'")
                    
                    if switch_state == "normal":
                        # Normal: 27→28 (continue forward)
                        self.log_to_terminal(f"[BLOCK 27 ROUTING] Normal position: 27 → 28")
                        # print(f"[ROUTING] RED LINE forward: Block 27 → 28 (Switch 27 normal)")
                        return 28
                    else:  # reverse
                        # Reverse: 27→76 (forward branch), then enter reverse mode for 76→75→74→73→72
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            self.train_directions[train_id] = 'red_branch_27_to_76_reverse'
                            self.log_to_terminal(f"[BLOCK 27 ROUTING] Reverse position: 27 → 76, setting mode = 'red_branch_27_to_76_reverse'")
                        # print(f"[ROUTING] RED LINE forward: Block 27 → 76 (Switch 27 reverse branch, entering reverse mode)")
                        return 76
                else:
                    self.log_to_terminal(f"[BLOCK 27 WARNING] Switch routing check failed - falling through to default")
            
            
            # Switch 38 (forward-only): When at block 38 going forward
            elif is_red_line and current_block == 38:
                self.log_to_terminal(f"[BLOCK 38 ENTRY] Entered block 38 routing, train_idx={train_idx}")
                self.log_to_terminal(f"[BLOCK 38 LINE CHECK] is_red_line = {is_red_line}")
                
                # Get train info for logging
                if train_idx < len(self.data_manager.active_trains):
                    train_id = self.data_manager.active_trains[train_idx]
                    current_mode = self.train_directions.get(train_id, 'forward')
                    self.log_to_terminal(f"[BLOCK 38 MODE CHECK] Train {train_id} mode = {current_mode}")
                
                # Check Red Line switch routing directly (not self.switch_routing which may be set to Green)
                has_switch_routing_red = hasattr(self, 'switch_routing_red')
                switch_38_in_routing = 38 in self.switch_routing_red if has_switch_routing_red else False
                self.log_to_terminal(f"[BLOCK 38 SWITCH CHECK] has_switch_routing_red = {has_switch_routing_red}")
                self.log_to_terminal(f"[BLOCK 38 SWITCH CHECK] 38 in switch_routing_red = {switch_38_in_routing}")
                
                if has_switch_routing_red and switch_38_in_routing:
                    # Get the block object to check its switch_state
                    if len(self.data_manager.blocks) > 37:
                        block_38 = self.data_manager.blocks[37]  # Block 38 (index 37)
                        
                        # Check both switch_direction and switch_state
                        switch_direction = getattr(block_38, 'switch_direction', None)
                        switch_state_bool = getattr(block_38, 'switch_state', None)
                        
                        # Determine if switch is in reverse
                        is_reverse = False
                        if switch_state_bool is not None and isinstance(switch_state_bool, bool):
                            is_reverse = switch_state_bool
                        elif switch_direction is not None:
                            is_reverse = (switch_direction == "reverse")
                        
                        switch_state = "reverse" if is_reverse else "normal"
                    self.log_to_terminal(f"[BLOCK 38 SWITCH STATE] switch_state = '{switch_state}'")
                    
                    if switch_state == "normal":
                        # Normal: 38→39 (continue forward)
                        self.log_to_terminal(f"[BLOCK 38 ROUTING] Normal position: 38 → 39")
                        # print(f"[ROUTING] RED LINE forward: Block 38 → 39 (Switch 38 normal)")
                        return 39
                    else:  # reverse
                        # Reverse: 38→71 (forward jump), then enter reverse mode for 71→70→69→68→67
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            self.train_directions[train_id] = 'red_branch_38_to_71_reverse'
                            self.log_to_terminal(f"[BLOCK 38 ROUTING] Reverse position: 38 → 71, setting mode = 'red_branch_38_to_71_reverse'")
                        # print(f"[ROUTING] RED LINE forward: Block 38 → 71 (Switch 38 reverse jump, entering reverse mode)")
                        return 71
                else:
                    self.log_to_terminal(f"[BLOCK 38 WARNING] Switch routing check failed - falling through to default")
            
            
            # Switch 52 (forward mode)
            elif is_red_line and current_block == 52:
                # DEBUG: This should NOT run if train is in backward mode
                if train_idx < len(self.data_manager.active_trains):
                    train_id = self.data_manager.active_trains[train_idx]
                    train_mode = self.train_directions.get(train_id, 'forward')
                    self.log_to_terminal(f"[BLOCK 52 FORWARD CHECK] WARNING: Forward switch check triggered! Train mode = {train_mode}")
                
                # Check switch 52 direction
                if len(self.data_manager.blocks) > 51:
                    block_52 = self.data_manager.blocks[51]  # Block 52 (index 51)
                    
                    # Check both switch_direction (string from Wayside) and switch_state (boolean from Test UI)
                    switch_direction = getattr(block_52, 'switch_direction', None)
                    switch_state = getattr(block_52, 'switch_state', None)
                    
                    # DEBUG: Show both values
                    self.log_to_terminal(f"[BLOCK 52 DEBUG] switch_direction={switch_direction}, switch_state={switch_state}")
                    
                    # Determine if switch is in reverse position
                    # PRIORITY: Use switch_state (boolean from Test UI) if it exists, otherwise use switch_direction
                    is_reverse = False
                    if switch_state is not None and isinstance(switch_state, bool):
                        # From Test UI: True = reverse (52-66 connection), False = normal (52-53 connection)
                        is_reverse = switch_state
                        self.log_to_terminal(f"[BLOCK 52 DEBUG] Using switch_state (boolean) = {switch_state}, is_reverse: {is_reverse}")
                    elif switch_direction is not None:
                        # From Wayside: check if it's "reverse"
                        is_reverse = (switch_direction == "reverse")
                        self.log_to_terminal(f"[BLOCK 52 DEBUG] Using switch_direction (string) = '{switch_direction}', is_reverse: {is_reverse}")
                    
                    if not is_reverse:
                        return 53  # Continue normally to 53
                    else:
                        # Jump to 66 - set backward mode BEFORE routing
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            self.train_directions[train_id] = 'red_backward_66_to_16'
                        # print(f"[ROUTING] RED LINE: Block 52 → 66 (Switch 52 jump, entering backward mode)")
                        return 66
            
            # Default: normal forward progression
            return current_block + 1
        
        # RED LINE RULE 3: Block 16 - Check switch 15 when in backward mode
        elif current_block == 16:
            self.log_to_terminal(f"[BLOCK 16 ENTRY] Entered block 16 routing, train_idx={train_idx}")
            
            # Check current line
            current_line = getattr(self, 'selected_line', None)
            is_green_line = current_line and current_line.get() == "Green Line"
            is_red_line = current_line and current_line.get() == "Red Line"
            
            # Check if train is in Red Line backward mode from 66
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                current_mode = self.train_directions.get(train_id, 'forward')
                self.log_to_terminal(f"[BLOCK 16 MODE CHECK] Train {train_id} mode = {current_mode}")
                # print(f"[DEBUG] Block 16: Train {train_id} mode = {current_mode}")
                
                # Check for Green Line backward loop mode FIRST (GREEN LINE ONLY)
                if is_green_line and self.train_directions.get(train_id) == 'backward_loop':
                    # Green Line backward loop - continue backward from 16 to 15
                    # print(f"[ROUTING] GREEN LINE backward loop: Block 16 → 15 (continuing backward)")
                    return 15
                
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # At switch 15, check which way to route
                    self.log_to_terminal(f"[BLOCK 16 BACKWARD] In red_backward_66_to_16 mode")
                    # print(f"[ROUTING] RED LINE backward: Reached block 16 (switch 15 junction)")
                    
                    # Check switch 15 state (use actual block.switch_state boolean)
                    if len(self.data_manager.blocks) > 14:
                        block_15 = self.data_manager.blocks[14]  # Switch at block 15 (index 14)
                        if hasattr(block_15, 'switch_state'):
                            # After swap: True = "1 to 16", False = "15 to 16"
                            if block_15.switch_state:  # True = checked = "1 to 16"
                                # Exit backward loop, go to block 1
                                self.train_directions[train_id] = 'forward'
                                # print(f"[ROUTING] RED LINE: Block 16 → 1 (Switch 15 set to '1 to 16', exit backward loop)")
                                return 1
                            else:  # False = unchecked = "15 to 16"
                                # Continue backward to block 15
                                # print(f"[ROUTING] RED LINE: Block 16 → 15 (Switch 15 set to '15 to 16', continue backward)")
                                return 15
                    
                    # Default: continue backward to 15
                    return 15
            else:
                self.log_to_terminal(f"[BLOCK 16 WARNING] train_idx {train_idx} out of range, active_trains length = {len(self.data_manager.active_trains)}")
            
            # Not in red_backward_66_to_16 mode, but might still be going backward
            # Check if on Red Line and if switch 15 should control routing
            self.log_to_terminal(f"[BLOCK 16 LINE CHECK] is_red_line = {is_red_line}")
            
            if is_red_line:
                # Check if train is in ANY backward mode (not just red_backward_66_to_16)
                train_id = self.data_manager.active_trains[train_idx] if train_idx < len(self.data_manager.active_trains) else None
                self.log_to_terminal(f"[BLOCK 16 TRAIN ID] train_id = {train_id}")
                
                is_any_backward = False
                if train_id and hasattr(self, 'train_directions'):
                    train_mode = self.train_directions.get(train_id, 'forward')
                    # Check for any backward mode (explicit check for backward modes only)
                    is_any_backward = 'backward' in train_mode.lower()
                    self.log_to_terminal(f"[BLOCK 16 MODE] train_mode = {train_mode}, is_any_backward = {is_any_backward}")
                
                # If in any backward mode, check switch 15 for routing
                if is_any_backward:
                    self.log_to_terminal(f"[BLOCK 16 ANY BACKWARD] Detected backward mode")
                    if len(self.data_manager.active_trains) > 14:
                        block_15 = self.data_manager.blocks[14]  # Switch at block 15
                        if hasattr(block_15, 'switch_state'):
                            # After swap: True = "1 to 16", False = "15 to 16"
                            if block_15.switch_state:  # True = checked = "1 to 16"
                                # Exit to block 1
                                self.train_directions[train_id] = 'forward'
                                # print(f"[ROUTING] RED LINE: Block 16 → 1 (Switch 15 set to '1 to 16', backward mode)")
                                return 1
                            else:  # False = unchecked = "15 to 16"
                                # Continue backward to block 15
                                # print(f"[ROUTING] RED LINE: Block 16 → 15 (Switch 15 set to '15 to 16', backward mode)")
                                return 15
                
                # FORWARD MODE: Block 16 always routes to 17 in forward mode
                # The switch does NOT affect forward routing
                # It only affects backward mode routing (to exit the loop)
                else:
                    self.log_to_terminal(f"[BLOCK 16 FORWARD MODE] Normal forward, routing to block 17")
                    # print(f"[ROUTING] RED LINE: Block 16 → 17 (normal forward)")
                    return 17
            
            # Default: forward to block 17
            self.log_to_terminal(f"[BLOCK 16 DEFAULT] Falling through to default, returning 17")
            # print(f"[ROUTING] Block 16 → 17 (forward)")
            return 17
        
        # RED LINE RULE 4: Block 15 - Handle backward mode exit
        elif current_block == 15:
            # Check current line
            current_line = getattr(self, 'selected_line', None)
            is_green_line = current_line and current_line.get() == "Green Line"
            
            # Check if train is in Red Line backward mode OR Green Line backward loop mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                
                # Check for entering loop mode (from block 16)
                if self.train_directions.get(train_id) == 'entering_loop_15':
                    # Continue backward through loop circuit
                    # print(f"[ROUTING] RED LINE entering loop: Block 15 → 14")
                    return 14
                
                # Check for Red Line backward mode
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Continue backward from 15 to 14
                    # print(f"[ROUTING] RED LINE backward: Block 15 → 14 (continuing backward)")
                    return 14
                
                # Check for Green Line backward loop mode (from 150→28→27→...→15) - GREEN LINE ONLY
                if is_green_line and self.train_directions.get(train_id) == 'backward_loop':
                    # Continue backward from 15 to 14
                    # print(f"[ROUTING] GREEN LINE backward loop: Block 15 → 14 (continuing backward)")
                    return 14
            
            # Not in backward mode: normal forward to block 16
            # Switch 15 does NOT affect forward routing from block 15
            # It only affects backward mode routing at block 16
            # print(f"[ROUTING] RED LINE: Block 15 → 16 (normal forward)")
            return 16
        
        # RED LINE RULE 5: Blocks 1-14 - Check if in backward mode, if so exit
        elif 1 <= current_block <= 14:
            # Check if train is in Red Line backward mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'red_backward_66_to_16':
                    # Continue backward
                    if current_block > 1:
                        next_block = current_block - 1
                        # print(f"[ROUTING] RED LINE backward: Block {current_block} → {next_block}")
                        return next_block
                    else:
                        # Reached block 1, exit backward mode
                        self.train_directions[train_id] = 'forward'
                        # print(f"[ROUTING] RED LINE: Reached block 1, exiting backward mode → 2")
                        return 2
            
            # Not in backward mode: normal forward progression
            # Check for any special routing at block 1
            if current_block == 1:
                if hasattr(self, 'switch_routing') and 1 in self.switch_routing:
                    switch_state = self.switch_states.get(1, "normal")
                    if switch_state == "normal":
                        return 2
                    else:  # reverse
                        return 16  # Jump to block 16
            
            return current_block + 1  # Default forward
        
        # ============================================================
        # END RED LINE BACKWARD LOOP
        # ============================================================
        
        # RED LINE RULE 6: Blocks 53-76 - Handle backward mode, branch switches, and jump destinations
        elif 53 <= current_block <= 76:
            # Check if train is in any special mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                current_mode = self.train_directions.get(train_id, 'forward')
                
                # ====================================================================
                # BRANCH SWITCH MODES (Switches 27, 32, 38, 43)
                # ====================================================================
                
                # Mode: red_branch_27_to_76_reverse
                # Path: 27→76→75→74→73→72, then exit to 33 in forward mode
                if current_mode == 'red_branch_27_to_76_reverse':
                    self.log_to_terminal(f"[BRANCH MODE 27] Train {train_id} in red_branch_27_to_76_reverse at block {current_block}")
                    if current_block == 76:
                        # Just entered from 27, continue backward to 75
                        self.log_to_terminal(f"[BRANCH MODE 27] Block 76 → 75 (reverse mode)")
                        # print(f"[ROUTING] RED LINE branch 27: Block 76 → 75 (reverse mode)")
                        return 75
                    elif current_block == 72:
                        # Reached end of branch, exit to 33 in forward mode
                        self.train_directions[train_id] = 'forward'
                        self.log_to_terminal(f"[BRANCH MODE 27] Block 72 → 33 (exiting branch to forward mode)")
                        # print(f"[ROUTING] RED LINE branch 27: Block 72 → 33 (exiting branch to forward mode)")
                        return 33
                    elif 73 <= current_block <= 75:
                        # Continue backward
                        next_block = current_block - 1
                        self.log_to_terminal(f"[BRANCH MODE 27] Block {current_block} → {next_block} (reverse mode)")
                        # print(f"[ROUTING] RED LINE branch 27: Block {current_block} → {next_block} (reverse mode)")
                        return next_block
                
                # Mode: red_branch_38_to_71_reverse
                # Path: 38→71→70→69→68→67, then exit to 44 in forward mode
                elif current_mode == 'red_branch_38_to_71_reverse':
                    self.log_to_terminal(f"[BRANCH MODE 38] Train {train_id} in red_branch_38_to_71_reverse at block {current_block}")
                    if current_block == 71:
                        # Just entered from 38, continue backward to 70
                        self.log_to_terminal(f"[BRANCH MODE 38] Block 71 → 70 (reverse mode)")
                        # print(f"[ROUTING] RED LINE branch 38: Block 71 → 70 (reverse mode)")
                        return 70
                    elif current_block == 67:
                        # Reached end of branch, exit to 44 in forward mode
                        self.train_directions[train_id] = 'forward'
                        self.log_to_terminal(f"[BRANCH MODE 38] Block 67 → 44 (exiting branch to forward mode)")
                        # print(f"[ROUTING] RED LINE branch 38: Block 67 → 44 (exiting branch to forward mode)")
                        return 44
                    elif 68 <= current_block <= 70:
                        # Continue backward
                        next_block = current_block - 1
                        self.log_to_terminal(f"[BRANCH MODE 38] Block {current_block} → {next_block} (reverse mode)")
                        # print(f"[ROUTING] RED LINE branch 38: Block {current_block} → {next_block} (reverse mode)")
                        return next_block
                
                # Mode: red_branch_32_to_76_forward
                # Path: 33→72→73→74→75→76, then exit to 27 in reverse mode
                elif current_mode == 'red_branch_32_to_76_forward':
                    self.log_to_terminal(f"[BRANCH MODE 32] Train {train_id} in red_branch_32_to_76_forward at block {current_block}")
                    if current_block == 72:
                        # Just entered from 33, continue forward to 73
                        self.log_to_terminal(f"[BRANCH MODE 32] Block 72 → 73 (forward mode)")
                        # print(f"[ROUTING] RED LINE branch 32: Block 72 → 73 (forward mode)")
                        return 73
                    elif current_block == 76:
                        # Reached end of branch, exit to 27 in reverse mode
                        self.train_directions[train_id] = 'red_backward_66_to_16'  # Use standard backward mode
                        self.log_to_terminal(f"[BRANCH MODE 32] Block 76 → 27 (exiting branch to reverse mode)")
                        # print(f"[ROUTING] RED LINE branch 32: Block 76 → 27 (exiting branch to reverse mode)")
                        return 27
                    elif 73 <= current_block <= 75:
                        # Continue forward
                        next_block = current_block + 1
                        self.log_to_terminal(f"[BRANCH MODE 32] Block {current_block} → {next_block} (forward mode)")
                        # print(f"[ROUTING] RED LINE branch 32: Block {current_block} → {next_block} (forward mode)")
                        return next_block
                
                # Mode: red_branch_43_to_71_forward
                # Path: 44→67→68→69→70→71, then exit to 38 in reverse mode
                elif current_mode == 'red_branch_43_to_71_forward':
                    self.log_to_terminal(f"[BRANCH MODE 43] Train {train_id} in red_branch_43_to_71_forward at block {current_block}")
                    if current_block == 67:
                        # Just entered from 44, continue forward to 68
                        self.log_to_terminal(f"[BRANCH MODE 43] Block 67 → 68 (forward mode)")
                        # print(f"[ROUTING] RED LINE branch 43: Block 67 → 68 (forward mode)")
                        return 68
                    elif current_block == 71:
                        # Reached end of branch, exit to 38 in reverse mode
                        self.train_directions[train_id] = 'red_backward_66_to_16'  # Use standard backward mode
                        self.log_to_terminal(f"[BRANCH MODE 43] Block 71 → 38 (exiting branch to reverse mode)")
                        # print(f"[ROUTING] RED LINE branch 43: Block 71 → 38 (exiting branch to reverse mode)")
                        return 38
                    elif 68 <= current_block <= 70:
                        # Continue forward
                        next_block = current_block + 1
                        self.log_to_terminal(f"[BRANCH MODE 43] Block {current_block} → {next_block} (forward mode)")
                        # print(f"[ROUTING] RED LINE branch 43: Block {current_block} → {next_block} (forward mode)")
                        return next_block
                
                # ====================================================================
                # STANDARD RED LINE BACKWARD MODE (red_backward_66_to_16)
                # ====================================================================
                
                elif current_mode == 'red_backward_66_to_16':
                    # Train is in standard backward mode
                    # This can happen if train jumped to block 67 or 72 via backward switches
                    # OR if train exited from branch modes above
                    
                    # Continue backward from jump destinations or branch exits
                    if current_block == 72:
                        # Could be from switch 32 jump OR from branch 32 exit
                        # Continue backward: 72→71→70→...
                        # print(f"[ROUTING] RED LINE backward: Block 72 → 71 (continuing backward)")
                        return 71
                    elif current_block == 67:
                        # Could be from switch 43 jump OR from branch 43 exit
                        # Continue backward: 67→66→... (66 will loop back to 52)
                        # print(f"[ROUTING] RED LINE backward: Block 67 → 66 (continuing backward)")
                        return 66
                    elif current_block >= 54:
                        # Normal backward progression in this range
                        next_block = current_block - 1
                        # print(f"[ROUTING] RED LINE backward: Block {current_block} → {next_block}")
                        return next_block
                    else:  # current_block == 53
                        # From 53, go back to 52
                        # print(f"[ROUTING] RED LINE backward: Block 53 → 52")
                        return 52
            
            # Not in any special mode: normal forward progression
            # Blocks 71 and 76 can be reached via forward jumps
            return current_block + 1  # Normal forward
        
        # RULE 7: Block 77 and beyond (Green Line specific, but keeping for compatibility)
        # Switch is housed at block 76 but only affects backward traffic from N section
        elif current_block == 76:
            return 77  # Always go to 77 from 76 (forward direction)
        
        # RULE 8: Block 77 routing - controlled by switch at block 76
        # Excel: SWITCH (76-77; 77-101) - switch housed at block 76
        # Forward (from 76): ALWAYS goes 77 → 78 (cannot bypass to 101)
        # Backward (from 78): Can go 77 → 101 (bypass) OR 77 → 78 (loop back into N section)
        elif current_block == 77:
            # Check if this train is in backward N section mode (coming from 78)
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'backward_n_section':
                    # Train is traveling backward through N section (from 78)
                    # Check switch at block 76 to decide routing
                    if len(self.data_manager.blocks) > 75:
                        block_76 = self.data_manager.blocks[75]  # Switch housed at block 76 (index 75)
                        if hasattr(block_76, 'switch_state'):
                            if block_76.switch_state:  # True = Normal = Loop back into N section
                                # Don't exit backward mode, loop back to 78
                                # print(f"[ROUTING] Block 77 → 78 (Looping back into N section via switch at 76)")
                                return 78
                            else:  # False = Reverse = Exit to 101
                                # Exit backward traversal at 77, continue to 101
                                self.train_directions[train_id] = 'forward'
                                # print(f"[ROUTING] Exiting N section backward traversal at block 77 → 101 (via switch at 76)")
                                return 101
                    # Default: exit to 101
                    self.train_directions[train_id] = 'forward'
                    # print(f"[ROUTING] Exiting N section backward traversal at block 77 → 101")
                    return 101
            
            # Forward direction (from block 76) - ALWAYS goes to 78
            # Cannot bypass to 101 from forward direction
            return 78  # Enter N section
        
        # RULE 9: Normal progression through N section (78-84)
        elif 78 <= current_block < 85:
            # First check if this train is in backward N section mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'backward_n_section':
                    next_block = self.get_next_block_backward_n_section(current_block)
                    if next_block == 101:
                        # Exiting backward traversal, reset to forward
                        self.train_directions[train_id] = 'forward'
                        # print(f"[ROUTING] Exiting N section backward traversal at block {current_block} → 101")
                    elif next_block:
                        pass
                        # print(f"[ROUTING] N section backward: Block {current_block} → {next_block}")
                    return next_block
            # Normal forward progression
            return current_block + 1  # Normal ascending: 78→79→80→81→82→83→84→85
        
        # RULE 9b: Switch housed at block 85
        elif current_block == 85:
            # First check if this train is in backward N section mode
            if train_idx < len(self.data_manager.active_trains):
                train_id = self.data_manager.active_trains[train_idx]
                if self.train_directions.get(train_id) == 'backward_n_section':
                    next_block = self.get_next_block_backward_n_section(current_block)
                    if next_block:
                        pass
                        # print(f"[ROUTING] N section backward: Block 85 → {next_block}")
                    return next_block
            
            # Normal forward routing (not in backward mode)
            if len(self.data_manager.blocks) > 84:
                block_85 = self.data_manager.blocks[84]  # Switch housed at block 85 (index 84)
                if hasattr(block_85, 'switch_state'):
                    if block_85.switch_state:  # True = To block 86
                        return 86  # Normal forward progression
                    else:  # False = Would be for backward entry from 100
                        # But when AT block 85 (coming from 84), we always go forward to 86
                        return 86
            return 86  # Default forward to 86
        
        # RULE 10: Normal progression from 86-99
        elif 86 <= current_block <= 99:
            return current_block + 1  # Continue ascending
        
        # RULE 11: Block 100 → 85 (BIDIRECTIONAL backward entry to N section)
        elif current_block == 100:
            # Check if switch at 85 is set for backward entry
            if len(self.data_manager.blocks) > 84:
                block_85 = self.data_manager.blocks[84]  # Block 85 at index 84
                if hasattr(block_85, 'switch_state'):
                    if not block_85.switch_state:  # False = Allow 100→85 backward route
                        # print(f"[ROUTING] Block 100 → 85 (BIDIRECTIONAL: Backward entry to N section)")
                        # Mark this train as going backward through N section
                        if train_idx < len(self.data_manager.active_trains):
                            train_id = self.data_manager.active_trains[train_idx]
                            self.train_directions[train_id] = 'backward_n_section'
                        return 85  # DESCENDING: 100 → 85
                    else:
                        return 101  # Normal ascending to 101
            # Default: continue ascending
            return 101
        
        # RULE 12: Continue normal progression 101-149
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
            
            # print(f" Sent to Track SW: Block {block_num} {'occupied' if occupancy != 0 else 'unoccupied'}")
            
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
                                # print(f" BEACON ACTIVATED at Block {block_num} for {train_id}")
                                # print(f"   Next station: {beacon_message['beacon_info']['next_station_name']}")
                                # print(f"   Distance: {beacon_message['beacon_info']['distance_to_next_station']}m")
                                # Send to Train SW for train controller
                                self.server.send_to_ui("Train SW", beacon_message)
                                # print(f" Beacon data sent to Train SW")
                                # Report to CTC
                                self.server.send_to_ui("CTC", {
                                    "command": "beacon_activated",
                                    "block": block_num,
                                    "train_id": train_id,
                                    "station_info": beacon_message['beacon_info']
                                })
                                # print(f" Beacon activation reported to CTC")
            # print(f" Sent occupancy update: Block {block_num} = {occupancy}")
            
        except Exception as e:
            print(f" Error sending occupancy update: {e}")
    
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
            
            # print(f" Switch at Block {block_num}: {direction_text} ({path_type})")
            # print(f"   Route: {path_description}")
        else:
            pass
            # print(f" Updated switch at Block {block_num}: {direction_text}")
            # print(f"   Route: {path_description}")
        
        # Special handling for switch at block 85
        # When switch routes from 100→85 (state=False), set N section (77-85) to face right
        if block_num == 85 or (from_block == 85 and to_block in [84, 86]):
            if hasattr(self.data_manager, 'bidirectional_directions'):
                if not state:  # Switch set to Left/Diverging (100→85→84 route)
                    # Set blocks 77-85 to face right (1) for backward travel
                    self.data_manager.bidirectional_directions["Blocks 77-85"] = 1
                    # print(f"    N Section (Blocks 77-85) set to Right → for backward travel")
                    # Update the display
                    if "Blocks 77-85" in self.bidir_controls:
                        self.bidir_controls["Blocks 77-85"].set("Right →")
                else:  # Switch set to Right/Straight (normal forward route)
                    # Set blocks 77-85 to face left (0) for normal forward travel
                    self.data_manager.bidirectional_directions["Blocks 77-85"] = 0
                    # print(f"    N Section (Blocks 77-85) set to ← Left for forward travel")
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
            # print("=== BIDIRECTIONAL TABLE VISIBILITY DEBUG ===")
            # print(f"Treeview exists: {self.bidir_tree is not None}")
            # print(f"Treeview mapped: {self.bidir_tree.winfo_ismapped()}")
            # print(f"Treeview width: {self.bidir_tree.winfo_width()}")
            # print(f"Treeview height: {self.bidir_tree.winfo_height()}")
            # print(f"Treeview x: {self.bidir_tree.winfo_x()}")
            # print(f"Treeview y: {self.bidir_tree.winfo_y()}")
            # print(f"Parent visible: {self.bidir_tree.winfo_parent()}")
            
            # Try to force focus and selection to make it visible
            children = self.bidir_tree.get_children()
            if children:
                self.bidir_tree.focus(children[0])
                self.bidir_tree.selection_set(children[0])
            
            # print("=============================================")
    
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
                # print(f" Clicked on {group_name} in column {column}")
                self.toggle_bidirectional_direction(group_name)

    def debug_bidirectional_table(self):
        """Debug method to check the current state of the bidirectional table"""
        if hasattr(self, 'bidir_tree'):
            # print("=== BIDIRECTIONAL TABLE DEBUG ===")
            # print(f"Treeview exists: {self.bidir_tree is not None}")
            # print(f"Number of rows: {len(self.bidir_tree.get_children())}")
            
            for item in self.bidir_tree.get_children():
                values = self.bidir_tree.item(item, "values")
                # print(f"  Row: {values}")
            
            # print(f"Data manager state: {getattr(self.data_manager, 'bidirectional_directions', 'NO DATA')}")
            # print("=================================")


    def send_outputs(self):
        """Only refresh terminals when Send Outputs button is clicked"""
        # print(" Manual terminal refresh triggered by Send Outputs button")
        for terminal in self.terminals:
            self._send_outputs_to_terminal(terminal)

    def _send_outputs_to_terminal(self, terminal):
        """Send outputs to a specific terminal widget."""
        dm = self.data_manager

        # Clear the terminal first
        terminal.config(state="normal")
        terminal.delete(1.0, "end")
        
        # print(" Updating terminal with system data...")
        
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
        # print(" Terminal update complete")

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
            # print(f" Track diagram background updated with: {filename}")
            # print("🧹 ALL track icons, trains, and canvas items cleared from diagram")
            
        except Exception as e:
            self.log_to_all_terminals(f"[ERROR] Failed to load image: {str(e)}")
            print(f" Error loading image: {e}")

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
            
            # print(f"[UI]  Background image resized to {new_width}x{new_height}")
            # print(f"    Original: {original_width}x{original_height} (aspect: {original_aspect:.4f})")
            # print(f"    New aspect: {new_width/new_height:.4f} (difference: {abs(original_aspect - new_width/new_height):.6f})")
            # print(f"    Canvas: {canvas_width}x{canvas_height}, Reserved: {reserved_right_space}px, Available: {available_width}x{available_height}")
            # print(f"    Image offset: ({x_offset}, {y_offset})")
            
        except Exception as e:
            # print(f" Could not update background image: {e}")
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
        # print(f" Clicked at coordinates: ({x}, {y})")
        
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
        
        # print("🧹 Cleared all red dots")
        
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
                # Check if block has a Murphy failure
                has_failure = False
                if hasattr(self, 'murphy_failures') and self.murphy_failures:
                    has_failure = self.murphy_failures.has_failure(block_num)
                
                # Draw dot - blue if failure, black otherwise
                dot_radius = 4
                dot_color = 'blue' if has_failure else 'black'
                marker = self.track_canvas.create_oval(
                    x - dot_radius, y - dot_radius,
                    x + dot_radius, y + dot_radius,
                    fill=dot_color,
                    outline='gray',
                    width=1
                )
            
            self.block_markers[block_num] = marker
        
        line_name = current_line if hasattr(self, 'selected_line') else "Green Line"
        # print(f"[MARKERS] Drew {len(self.block_markers)} block markers for {line_name} (offset: {x_offset}, {y_offset}) (correction: {x_correction}, {y_correction})")

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
            # DIAGNOSTIC: Check why block might not be in positions
            if 57 <= block_num <= 60 and hasattr(self, 'selected_line'):
                current_line = self.selected_line.get()
                if current_line == "Red Line":
                    pass
                    # print(f" [RED LINE DEBUG] update_block_marker: Block {block_num} NOT in positions dict!")
                    # print(f"   - Positions dict keys: {sorted(positions.keys())[:10]}...{sorted(positions.keys())[-10:]}")
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
            log_msg = f"[MARKER] Block {block_num} now shows train icon (occupied)"
            
            # DIAGNOSTIC: Enhanced logging for Red Line blocks 57-60
            if 57 <= block_num <= 60 and hasattr(self, 'selected_line'):
                current_line = self.selected_line.get()
                if current_line == "Red Line":
                    log_msg += f" at position ({x}, {y})"
                    log_msg += f" [base: ({base_x}, {base_y}), offsets: x={x_offset}, y={y_offset}, correction: x={x_correction}, y={y_correction}]"
            
            # print(log_msg)
        else:
            # Check if block has a Murphy failure
            has_failure = False
            if hasattr(self, 'murphy_failures') and self.murphy_failures:
                has_failure = self.murphy_failures.has_failure(block_num)
            
            # Draw dot - blue if failure, black otherwise
            dot_radius = 4
            dot_color = 'blue' if has_failure else 'black'
            marker = self.track_canvas.create_oval(
                x - dot_radius, y - dot_radius,
                x + dot_radius, y + dot_radius,
                fill=dot_color,
                outline='gray',
                width=1
            )
            # print(f"[MARKER] Block {block_num} now shows {'blue' if has_failure else 'black'} dot ({'failure active' if has_failure else 'empty'})")
        
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
        
        # print("🧹 Completely cleared all track icons and reset all tracking data")

    def process_structured_track_data(self, df, pd):
        """Process the specific CSV/Excel structure and REPLACE default data"""
        try:
            # print(f" Starting data replacement with {len(df)} rows")
            
            # Clear existing station data first
            self.data_manager.station_location = []
            # print("🧹 Cleared existing station data")
            
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
            
            # print(f"🔍 Found columns in file: {actual_columns}")
            # print(f" DataFrame columns: {list(df.columns)}")
            # print(f" First row sample: {df.iloc[0].to_dict() if len(df) > 0 else 'No data'}")
            
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
                        # print(f" Processing block {block_num} from row {index}")
                    except (ValueError, TypeError) as e:
                        print(f" Could not parse block number from row {index}: {row[actual_columns['block_number']]}")
                        continue
                else:
                    # Try to infer from index or other columns
                    block_num = index + 1  # Default to row index + 1
                    # print(f" Inferred block {block_num} from row index {index}")
                
                if block_num and 1 <= block_num <= len(self.data_manager.blocks):
                    block = self.data_manager.blocks[block_num - 1]
                    
                    # REPLACE block length
                    if 'block_length' in actual_columns:
                        try:
                            block.length = float(row[actual_columns['block_length']])
                            # print(f"    Length: {block.length}m")
                        except (ValueError, TypeError) as e:
                            print(f" Could not parse length for block {block_num}: {row[actual_columns['block_length']]}")
                            block.length = 0.0
                    
                    # REPLACE block grade
                    if 'block_grade' in actual_columns:
                        try:
                            block.grade = float(row[actual_columns['block_grade']])
                            # print(f"    Grade: {block.grade}%")
                        except (ValueError, TypeError) as e:
                            print(f" Could not parse grade for block {block_num}: {row[actual_columns['block_grade']]}")
                            block.grade = 0.0
                    
                    # REPLACE speed limit
                    if 'speed_limit' in actual_columns:
                        try:
                            block.speed_limit = float(row[actual_columns['speed_limit']])
                            # print(f"    Speed: {block.speed_limit}km/h")
                        except (ValueError, TypeError) as e:
                            print(f" Could not parse speed for block {block_num}: {row[actual_columns['speed_limit']]}")
                            block.speed_limit = 0.0
                    
                    # REPLACE elevation
                    if 'elevation' in actual_columns:
                        try:
                            block.elevation = float(row[actual_columns['elevation']])
                            # print(f"    Elevation: {block.elevation}m")
                        except (ValueError, TypeError) as e:
                            print(f" Could not parse elevation for block {block_num}: {row[actual_columns['elevation']]}")
                            block.elevation = 0.0
                    
                    # RESET infrastructure flags first
                    block.switch_state = False
                    block.crossing = False
                    
                    # Handle infrastructure (stations, switches, etc.)
                    if 'infrastructure' in actual_columns:
                        infrastructure = str(row[actual_columns['infrastructure']])
                        if pd.notna(infrastructure) and infrastructure != 'nan':
                            self.process_infrastructure(block, infrastructure)
                            # print(f"    Infrastructure: {infrastructure}")
                    
                    blocks_updated += 1
                    # print(f" UPDATED block {block_num}")
            
            # print(f" Successfully updated {blocks_updated} blocks")
            
            # Reset ticket sales and passenger data arrays to match new station data
            self.reset_station_data_arrays()
            
            # Refresh both UIs to show the new data
            self.refresh_all_uis()
            
            self.log_to_all_terminals(f"[SUCCESS] Completely replaced track data with uploaded file - updated {blocks_updated} blocks")
            
        except Exception as e:
            print(f" Error processing structured track data: {e}")
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
                # print(" Refreshed Test UI tables")
            except Exception as e:
                pass
                # print(f" Could not refresh Test UI: {e}")
        
        # print(" COMPLETELY refreshed all UIs with new data")
        
        # Debug: Print current block data to verify
        # print("🔍 CURRENT BLOCK DATA AFTER UPDATE:")
        for i, block in enumerate(self.data_manager.blocks[:5]):  # Show first 5 blocks
            pass
            # print(f"   Block {i+1}: Length={block.length}m, Grade={block.grade}%, Speed={block.speed_limit}km/h")

    def process_infrastructure(self, block, infrastructure, pd):
        """Process infrastructure information and REPLACE existing data"""
        try:
            if pd.isna(infrastructure) or infrastructure == '' or infrastructure == 'nan':
                return
            
            infrastructure = str(infrastructure).upper()
            # print(f"    Processing infrastructure: '{infrastructure}' for block {block.block_number}")
            
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
                    # print(f"    ADDED station '{station_name}' at block {block.block_number}")
            
            # Handle switches - REPLACE switch state
            if 'SWITCH' in infrastructure:
                block.switch_state = True  # Set to right position
                # print(f"    ADDED switch at block {block.block_number}")
            else:
                block.switch_state = False  # Ensure no switch if not specified
            
            # Handle crossings - REPLACE crossing state
            if 'CROSSING' in infrastructure:
                block.crossing = True
                # print(f"    ADDED crossing at block {block.block_number}")
            else:
                block.crossing = False  # Ensure no crossing if not specified
                
        except Exception as e:
            print(f" Error processing infrastructure for block {block.block_number}: {e}")

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
                    # print(f"    Extracted station name: '{clean_part}'")
                    return clean_part
            
            # If no clear name, generate one
            generated_name = f"Station {block.block_number}"
            # print(f"    Generated station name: '{generated_name}'")
            return generated_name
        
        except Exception as e:
            print(f" Error extracting station name: {e}")
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
            print(f" Error extracting station name: {e}")
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
            
            # print("🧹 Cleared all track icons from diagram")

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
        # print("Force refreshing all trains...")
        
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
            # print(f" Cannot turn on heater for block {block.block_number} - heater is not working")
            return False  # Can't turn on a non-working heater
        
        block.track_heater = [1 if is_on else 0, 1 if is_working else 0]
        # print(f"🔧 Block {block.block_number} heater: {'ON' if is_on else 'OFF'}, {'WORKING' if is_working else 'BROKEN'}")
        return True

    def toggle_heater(self, block_num):
        """Toggle heater on/off if it's working"""
        block = self.data_manager.blocks[block_num - 1]
        if self.is_heater_working(block):
            new_state = not self.is_heater_on(block)
            self.set_heater_state(block, new_state, True)
        else:
            pass
            # print(f" Cannot toggle heater for block {block_num} - heater is not working")

    def break_heater(self, block_num):
        """Break the heater (turns it off if it was on)"""
        block = self.data_manager.blocks[block_num - 1]
        was_on = self.is_heater_on(block)
        self.set_heater_state(block, False, False)  # Turn off and break
        if was_on:
            pass
            # print(f"🔧 Heater broken and turned off for block {block_num}")

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
        
        # ============================================================
        # RED LINE SWITCHES
        # ============================================================
        
        # Handle switch at block 15 (RED LINE)
        # Excel: SWITCH (15-16; 1-16)
        elif block_number == 15:
            if switch_state:  # True = loop closure
                return (1, 16)  # Shows that block 1 connects to 16 via switch 15
            else:  # False = normal route
                return (15, 16)
        
        # Handle switch at block 9 (RED LINE - Yard access)
        elif block_number == 9:
            if switch_state:  # True = to yard
                return (9, "Yard")
            else:  # False = normal route
                return (9, 10)
        
        # Handle switch at block 27 (RED LINE - Branch)
        elif block_number == 27:
            if switch_state:  # True = branch to end section
                return (27, 76)
            else:  # False = normal route
                return (27, 28)
        
        # Handle switch at block 32 (RED LINE - Branch)
        elif block_number == 32:
            if switch_state:  # True = backward jump
                return (33, 72)
            else:  # False = normal route
                return (32, 33)
        
        # Handle switch at block 38 (RED LINE - Branch)
        elif block_number == 38:
            if switch_state:  # True = backward jump
                return (39, 71)
            else:  # False = normal route
                return (38, 39)
        
        # Handle switch at block 43 (RED LINE - Branch)
        elif block_number == 43:
            if switch_state:  # True = backward jump
                return (44, 67)
            else:  # False = normal route
                return (43, 44)
        
        # Handle switch at block 52 (RED LINE - Loop switch)
        elif block_number == 52:
            if switch_state:  # True = forward jump to loop
                return (52, 66)
            else:  # False = normal route
                return (52, 53)
        
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
                            signal_display = "Green"
                        elif signal_state == 2:
                            signal_display = "Yellow"
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
                        crossing_state = "Active" if getattr(b, "crossing_state", False) else "Inactive"
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
            # print(f"🎫 Station {station_name} (Block {block_num}): {self.data_manager.ticket_sales[idx]} tickets waiting")
        
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
            # print(f"    Block {block_num} is not a station!")
            return  # Not a station
        
        station_name = station_info[1]
        idx = block_num - 1
        
        # print(f"\n    BEFORE:")
        # print(f"      Ticket sales length: {len(self.data_manager.ticket_sales)}")
        # print(f"      Passengers boarding length: {len(self.data_manager.passengers_boarding)}")
        # print(f"      Block index: {idx}")
        
        # Get current ticket sales (passengers waiting)
        tickets_waiting = self.data_manager.ticket_sales[idx]
        # print(f"      Current ticket sales at idx {idx}: {tickets_waiting}")
        
        # Generate random boarding count (0 to tickets_waiting)
        if tickets_waiting > 0:
            passengers_boarding = self.random.randint(0, tickets_waiting)
        else:
            passengers_boarding = 0
        
        # Update passengers boarding
        self.data_manager.passengers_boarding[idx] = passengers_boarding
        
        # print(f"\n    TRAIN ARRIVAL at {station_name} (Block {block_num}):")
        # print(f"      Passengers waiting: {tickets_waiting}")
        # print(f"      Passengers boarding: {passengers_boarding}")
        
        # Send passengers boarding to Train Model
        self.send_passengers_boarding_to_train_model(block_num)
        
        # Generate new random ticket sales for next train (0-70)
        new_tickets = self.random.randint(0, 70)
        self.data_manager.ticket_sales[idx] = new_tickets
        
        # print(f"      New tickets sold: {new_tickets}")
        
        # print(f"\n    AFTER:")
        # print(f"      ticket_sales[{idx}] = {self.data_manager.ticket_sales[idx]}")
        # print(f"      passengers_boarding[{idx}] = {self.data_manager.passengers_boarding[idx]}")
        
        # Send updated station data to CTC (ticket sales + disembarking)
        self.send_station_data_to_ctc(block_num)


    def send_passengers_boarding_to_train_model(self, block_num):
        """
        Send passengers boarding for a specific station block to Train Model.
        Called when a train stops at a station (authority reaches 0).
        
        Args:
            block_num (int): Block number of the station
        
        Returns:
            bool: True if boarding data was sent successfully, False otherwise
        """
        try:
            idx = block_num - 1
            
            # Validate block index
            if not (0 <= idx < len(self.data_manager.passengers_boarding)):
                return False
            
            # Get passenger count
            passenger_count = int(self.data_manager.passengers_boarding[idx])
            
            # Prepare message for Train Model
            boarding_message = {
                'command': 'Passengers Boarding',
                'value': passenger_count,
                'block_number': block_num
            }
            
            # Send to Train Model
            self.server.send_to_ui("Train Model", boarding_message)
            
            print(f"Sent passengers boarding to Train Model:")
            # print(f"   Block {block_num}: {passenger_count} passengers")
            
            return True
            
        except Exception as e:
            return False

    def send_beacon_data_on_departure(self, train_id, block_num):
        """
        Send 128-bit beacon array to Train Model when a train departs from a station.
        Called when train authority increases from 0 (train starts moving after stop).
        
        Args:
            train_id (str): ID of the departing train
            block_num (int): Block number of the station being departed
        
        Returns:
            bool: True if beacon data was sent successfully, False otherwise
        """
        try:
            # Get beacon data for this station block
            beacon_message = self.beacon_manager.format_beacon_message(block_num, train_id)
            
            if beacon_message:
                # Send to Train Model
                self.server.send_to_ui("Train Model", beacon_message)
                
                # Get station name for logging
                station_info = next(
                    (s for s in self.data_manager.station_location if s[0] == block_num), 
                    None
                )
                station_name = station_info[1] if station_info else f"Block {block_num}"
                
                print(f"Sent beacon data to Train Model:")
                print(f"   Train: {train_id}")
                print(f"   Departed from: {station_name} (Block {block_num})")
                print(f"   Beacon array: 128-bit unique identifier")
                
                return True
            else:
                # No beacon data for this block (shouldn't happen if train was stopped at station)
                return False
                
        except Exception as e:
            return False


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
            # print("🔍 === STARTED MONITORING STATION OCCUPANCY ===")
            # print(f"   Monitoring stations: {[f'Block {b}' for b, _ in self.data_manager.station_location]}\n")
        
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
                    pass
                    # print(f"   Checking Block {block_num} ({station_name}): prev={previous_occupancy}, curr={current_occupancy}")
                
                # Detect train arrival (occupancy changed from 0 to non-zero)
                if previous_occupancy == 0 and current_occupancy != 0:
                    # print(f"\n === TRAIN ARRIVAL DETECTED ===")
                    # print(f"   Train {current_occupancy} arrived at {station_name} (Block {block_num})")
                    self.handle_train_arrival_at_station(block_num)
                    # print(f"   === TRAIN ARRIVAL HANDLED ===\n")
                
                # Update previous occupancy
                self._previous_station_occupancy[block_num] = current_occupancy
        
        if self._debug_count < 3:
            self._debug_count += 1
        
        # Check again in 500ms (faster monitoring for train arrivals)
        self.after(500, self.monitor_station_occupancy)

    def monitor_train_authority_for_boarding(self):
        """
        Monitor train authority values and trigger:
        1. Passenger boarding when authority reaches 0 (train stops) at a station
        2. Beacon transmission when authority increases from 0 (train departs) from a station
        
        This is called periodically (every 500ms) to check authority changes.
        """
        try:
            # Check each active train
            for idx, train_id in enumerate(self.data_manager.active_trains):
                if idx < len(self.data_manager.commanded_authority):
                    current_authority = self.data_manager.commanded_authority[idx]
                    
                    # Get previous authority (default to -1 if first check)
                    previous_authority = self._previous_train_authority.get(train_id, -1)
                    
                    # ARRIVAL: Check if authority just reached 0 (train stopped)
                    if previous_authority > 0 and current_authority == 0:
                        # Authority reached 0 - check if train is at a station
                        if idx < len(self.data_manager.train_locations):
                            block_num = self.data_manager.train_locations[idx]
                            
                            # Check if this block has a station
                            station_info = next(
                                (s for s in self.data_manager.station_location if s[0] == block_num), 
                                None
                            )
                            
                            if station_info:
                                station_name = station_info[1]
                                
                                # Record that this train is stopped at this station
                                self._trains_stopped_at_station[train_id] = block_num
                                
                                # Handle passenger boarding
                                self.handle_train_arrival_at_station(block_num)
                    
                    # DEPARTURE: Check if authority increased from 0 (train departing)
                    elif previous_authority == 0 and current_authority > 0:
                        # Train is starting to move after being stopped
                        # Check if this train was stopped at a station
                        if train_id in self._trains_stopped_at_station:
                            departure_block = self._trains_stopped_at_station[train_id]
                            
                            # Send beacon data for the station the train is leaving
                            self.send_beacon_data_on_departure(train_id, departure_block)
                            
                            # Remove from stopped trains tracking
                            del self._trains_stopped_at_station[train_id]
                    
                    # Update previous authority
                    self._previous_train_authority[train_id] = current_authority
        
        except Exception as e:
            pass
        
        # Schedule next check
        self.after(500, self.monitor_train_authority_for_boarding)

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
            self.data_manager.next_train_id = 1

        # Assign new train ID
        train_id = self.data_manager.next_train_id
        self.data_manager.next_train_id += 1

        # Register new train in data manager
        train_name = f"Train_{train_id}"
        self.data_manager.active_trains.append(train_name)
        self.data_manager.commanded_speed.append(speed)
        self.data_manager.commanded_authority.append(authority)
        self.data_manager.train_occupancy.append(0)
        
        # Initialize train actual speed to 0 (will be updated by Train Model)
        self.train_actual_speeds[train_name] = 0
        self.train_positions_in_block[train_name] = 0
        import time
        self.last_movement_update[train_name] = time.time()

        # print(f"[TRAIN CREATED] ID={train_id}, Speed={speed} m/s, Authority={authority} blocks")

        # Refresh dropdowns and terminals
        self.train_combo["values"] = self.data_manager.active_trains
        self.train_combo.set(train_name)
        self.send_outputs()
    
    def _create_train_from_yard(self, speed, authority):
        """Create a new train specifically from the Yard/Block 63, starting at block 63."""
        # Initialize starting ID if not set yet
        if not hasattr(self.data_manager, "next_train_id"):
            self.data_manager.next_train_id = 1

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

        # print(f" [YARD/BLOCK 63 TRAIN CREATED] ID={train_id}, Starting at Block 63")
        # print(f"   Initial Speed={speed} m/s, Authority={authority} blocks")
        # print(f"   Active trains: {self.data_manager.active_trains}")
        # print(f"   Train locations: {self.data_manager.train_locations}")
        # print(f"   Array sizes: active_trains={len(self.data_manager.active_trains)}, commanded_speed={len(self.data_manager.commanded_speed)}, commanded_authority={len(self.data_manager.commanded_authority)}")

        # Update UI elements if they exist
        if hasattr(self, 'train_combo'):
            self.train_combo["values"] = self.data_manager.active_trains
            self.train_combo.set(train_name)
        
        # Send creation notification to other modules
        try:
            # Send new train notification (without speed/authority)
            self.server.send_to_ui("Train Model", {
                "command": "new_train",
                "train_id": train_name,
                "block_number": 63
            })
            
            # Send commanded speed separately
            self.server.send_to_ui("Train Model", {
                "command": "Commanded Speed",
                "value": speed,
                "train_id": train_name
            })
            
            # Send commanded authority separately
            self.server.send_to_ui("Train Model", {
                "command": "Commanded Authority",
                "value": authority,
                "train_id": train_name
            })
            
            self.server.send_to_ui("CTC", {
                "command": "train_dispatched",
                "train_id": train_name,
                "from": "Yard/Block63",
                "entry_block": 63
            })
        except Exception as e:
            print(f" Error sending train creation notifications: {e}")
        
        # Refresh UI - but don't let errors stop us
        try:
            self.refresh_ui()
        except Exception as e:
            print(f" Error during refresh_ui: {e}")
        
        # Send outputs - but catch any errors
        try:
            self.send_outputs()
        except Exception as e:
            print(f" Error during send_outputs: {e}")
        
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
        # print("Closing application...")
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
        # NOTE: send_passengers_boarding_to_train_model is called ONLY when train authority 
        # reaches 0 at a station (via handle_train_arrival_at_station), not on every refresh
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
            # print(f" Sent station data to CTC: [tickets={ticket_count}, disembarking={disembarking_count}]")

    def send_all_station_data_to_ctc(self):
        """
        Send ticket sales and passengers disembarking for ALL stations to CTC.
        Format: [ticket_sales (int), passengers_disembarking (int), line_color (str)]
        Uses 0 if no ticket sales or passengers disembarking are generated.
        Line color is either "Red" or "Green" based on the selected line.
        This is called periodically by send_all_outputs().
        """
        # Get the current line and extract color
        current_line = self.selected_line.get() if hasattr(self, 'selected_line') else "Green Line"
        line_color = "Red" if "Red" in current_line else "Green"
        
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            
            # Get ticket sales, default to 0 if not available
            ticket_count = 0
            if hasattr(self.data_manager, 'ticket_sales') and 0 <= idx < len(self.data_manager.ticket_sales):
                ticket_count = int(self.data_manager.ticket_sales[idx])
            
            # Get passengers disembarking, default to 0 if not available
            disembarking_count = 0
            if hasattr(self.data_manager, 'passengers_disembarking') and 0 <= idx < len(self.data_manager.passengers_disembarking):
                disembarking_count = int(self.data_manager.passengers_disembarking[idx])
            
            # Send as [ticket_sales, passengers_disembarking, line_color] format
            self.server.send_to_ui("CTC", {
                'command': 'TP',
                'value': [ticket_count, disembarking_count, line_color]
            })
            # print(f" Sent station data to CTC for {station_name} (Block {block_num}): [tickets={ticket_count}, disembarking={disembarking_count}, line={line_color}]")

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
        # print(f" Sent failure modes to Wayside Controller ({len(failures)} failures)")

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
        
        # print(f" Sent block occupancy to Wayside: {occupied_count} occupied, {unoccupied_count} unoccupied blocks")
    
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
        
        # print(f" Sent bulk occupancy data to Track SW: {len(occupancy_data)} blocks")

    def send_block_occupancy_to_train_model(self):
        """Send block occupancy to Train Model."""
        occupancy_data = {}
        for block in self.data_manager.blocks:
            occupancy_data[block.block_number] = block.occupancy
        
        self.server.send_to_ui("Train Model", {
            'command': 'block_occupancy',
            'data': occupancy_data
        })
        # print(f" Sent block occupancy to Train Model")

    def send_commanded_speed_to_train_model(self):
        """Send commanded speed to Train Model - individual message per train."""
        for i, train_id in enumerate(self.data_manager.active_trains):
            if i < len(self.data_manager.commanded_speed):
                speed = self.data_manager.commanded_speed[i]
                self.server.send_to_ui("Train Model", {
                    'command': 'Commanded Speed',
                    'value': speed,
                    'train_id': train_id
                })
        # print(f" Sent commanded speed to Train Model")

    def send_commanded_authority_to_train_model(self):
        """Send commanded authority to Train Model - individual message per train."""
        for i, train_id in enumerate(self.data_manager.active_trains):
            if i < len(self.data_manager.commanded_authority):
                authority = self.data_manager.commanded_authority[i]
                self.server.send_to_ui("Train Model", {
                    'command': 'Commanded Authority',
                    'value': authority,
                    'train_id': train_id
                })
        # print(f" Sent commanded authority to Train Model")

    def send_beacons_to_train_model(self):
        """Send beacon data to Train Model only for occupied blocks."""
        beacon_data = {}
        
        for block in self.data_manager.blocks:
            # Only send beacon if:
            # 1. Block is occupied
            # 2. Beacon can be sent (no track circuit or power failure)
            # 3. Block has beacon data
            if (block.occupancy and 
                self.murphy_failures.can_send_beacon(block.block_number) and
                hasattr(block, 'beacon') and block.beacon):
                beacon_data[block.block_number] = block.beacon
        
        # Only send message if there are occupied blocks with beacons
        if beacon_data:
            self.server.send_to_ui("Train Model", {
                'command': 'Beacon',
                'data': beacon_data
            })
            # print(f"Sent beacons to Train Model ({len(beacon_data)} occupied blocks)")

    def send_passengers_boarding_to_train_model(self):
        """
        [DEPRECATED - DO NOT USE]
        This method sends ALL passengers boarding data for ALL stations.
        
        Use send_passengers_boarding_to_train_model(block_num) instead, which is called
        automatically when a train's authority reaches 0 at a station.
        
        Keeping this method for backwards compatibility but it should NOT be called
        from send_all_outputs or any periodic refresh function.
        """
        boarding_data = {}
        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            boarding_data[block_num] = {
                'station_name': station_name,
                'passengers_boarding': int(self.data_manager.passengers_boarding[idx])
            }
        
        self.server.send_to_ui("Train Model", {
            'command': 'Passengers Boarding',
            'data': boarding_data
        })
        print(f" Sent passengers boarding to Train Model")

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
        # print(f" Sent light states to Train Controller as two-bit boolean arrays")


    # ---------------- INPUT HANDLERS (Update _process_message) ----------------

    def _process_message(self, message, source_ui_id):
        """Process incoming messages from other UIs"""
        try:
            # print(f"📨 Received from {source_ui_id}: {message}")
            
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
                        print(f" Could not convert block_number '{block_number}' to int")
                        block_number = None
                elif not isinstance(block_number, int):
                    try:
                        block_number = int(block_number)
                    except (ValueError, TypeError):
                        print(f" Could not convert block_number '{block_number}' to int")
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
                        print(f" Could not convert commanded_speed '{commanded_speed}' to float")
                        commanded_speed = None
                
                if commanded_authority is not None and isinstance(commanded_authority, str):
                    try:
                        commanded_authority = int(commanded_authority)
                    except (ValueError, TypeError):
                        print(f" Could not convert commanded_authority '{commanded_authority}' to int")
                        commanded_authority = None
                
                # Check if this is a Yard dispatch (new train creation)
                # Accept either "Yard" string or block number 63
                is_yard_dispatch = False
                
                # Check for "Yard" string
                if isinstance(block_num, str) and block_num.upper() == "YARD":
                    is_yard_dispatch = True
                    # print(f" YARD DISPATCH DETECTED (from 'Yard') - Creating new train")
                # Check for block 63 (with no existing train)
                elif block_num == 63 or (isinstance(block_num, str) and block_num == "63"):
                    # Check if there's already a train at block 63
                    block_63_occupied = False
                    if 63 <= len(self.data_manager.blocks):
                        block_63 = self.data_manager.blocks[62]  # Block 63 (index 62)
                        if hasattr(block_63, 'occupancy') and block_63.occupancy != 0:
                            block_63_occupied = True
                    
                    # CHECK SWITCH STATE AT BLOCK 62 (controls entry to block 63 from yard)
                    switch_allows_yard_entry = False
                    if 62 <= len(self.data_manager.blocks):
                        block_62 = self.data_manager.blocks[61]  # Block 62 (index 61)
                        
                        # Check if switch is in the correct position (reverse = yard to 63)
                        if hasattr(block_62, 'switch_direction'):
                            switch_direction = block_62.switch_direction
                            # Reverse position allows trains from yard to enter block 63
                            if switch_direction == "reverse":
                                switch_allows_yard_entry = True
                                # print(f" Switch at block 62 is in REVERSE (yard→63) - allowing train spawn")
                            else:
                                # print(f" Switch at block 62 is in NORMAL (main line→63) - blocking train spawn from yard")
                                pass
                        else:
                            # If no switch direction set, check switch_states dictionary
                            if hasattr(self, 'switch_states') and 62 in self.switch_states:
                                switch_direction = self.switch_states[62]
                                if switch_direction == "reverse":
                                    switch_allows_yard_entry = True
                                    # print(f" Switch at block 62 (from dict) is in REVERSE - allowing train spawn")
                            else:
                                # Default to allowing if switch state is unknown (backwards compatibility)
                                switch_allows_yard_entry = True
                                # print(f" Switch state at block 62 unknown - defaulting to allow")
                    else:
                        # If block 62 doesn't exist, allow spawn (backwards compatibility)
                        switch_allows_yard_entry = True
                    
                    # Only treat as yard dispatch if:
                    # 1. Block 63 is not occupied
                    # 2. No train_id provided
                    # 3. Switch at block 62 allows yard entry (reverse position)
                    if not block_63_occupied and not train_id and switch_allows_yard_entry:
                        # Check if any trains already exist
                        if not self.data_manager.active_trains:
                            is_yard_dispatch = True
                            # print(f" YARD DISPATCH DETECTED (from Block 63) - Creating new train")
                            # Convert block_num to int if it's a string
                            if isinstance(block_num, str):
                                block_num = 63
                        else:
                            # Use existing train instead of creating a duplicate
                            train_id = self.data_manager.active_trains[-1]
                            # print(f" Block 63 command received, but train already exists. Using: {train_id}")
                    elif not switch_allows_yard_entry:
                        # Log that spawn was blocked due to switch position
                        try:
                            for terminal in self.terminals:
                                terminal.config(state="normal")
                                terminal.insert("end", f" YARD DISPATCH BLOCKED: Switch at block 62 not in yard→63 position\n")
                                terminal.see("end")
                                terminal.config(state="disabled")
                        except Exception as e:
                            pass
                        # print(f" Cannot spawn train at block 63: switch at block 62 not in correct position")
                
                if is_yard_dispatch:
                    # Create a new train for yard dispatch
                    new_train_id = self._create_train_from_yard(commanded_speed, commanded_authority)
                    train_id = new_train_id
                    
                    # Initialize train position tracking (actual speed will be received from Train Model)
                    self.train_actual_speeds[new_train_id] = 0  # Start at 0, will be updated by Train Model
                    self.train_positions_in_block[new_train_id] = 0
                    import time
                    self.last_movement_update[new_train_id] = time.time()
                    # print(f" Initialized position tracking for {new_train_id}, waiting for actual speed from Train Model")
                    
                    # Set/ensure position at block 63 (entry from yard)
                    block_num = 63
                    
                    # Set occupancy at block 63 - CRITICAL: This must happen
                    try:
                        if 63 <= len(self.data_manager.blocks):
                            yard_entry_block = self.data_manager.blocks[62]  # Block 63 (index 62)
                            # Initialize occupancy if it doesn't exist
                            if not hasattr(yard_entry_block, 'occupancy'):
                                yard_entry_block.occupancy = 0
                                # print(f"[DEBUG] Initialized occupancy attribute for block 63")
                            
                            # Extract train number from train_id (e.g., "Train_11000" -> 11000)
                            train_num = int(new_train_id.split('_')[1]) if '_' in new_train_id else 1
                            yard_entry_block.occupancy = train_num
                            # print(f" Set initial occupancy at Block 63 for {new_train_id}")
                            # print(f"[DEBUG] Block 63 occupancy is now: {yard_entry_block.occupancy}")
                            
                            # Send occupancy update to other modules
                            try:
                                self.server.send_to_ui("Train Model", {
                                    "command": "Block Occupancy",
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
                                print(f" Error sending occupancy updates: {e}")
                    except Exception as e:
                        # print(f" CRITICAL: Failed to set block 63 occupancy: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    # Log the yard dispatch
                    try:
                        for terminal in self.terminals:
                            terminal.config(state="normal")
                            terminal.insert("end", f" YARD DISPATCH: {new_train_id} → Block 63\n")
                            terminal.insert("end", f"   Speed: {commanded_speed} m/s, Authority: {commanded_authority} blocks\n")
                            terminal.see("end")
                            terminal.config(state="disabled")
                    except Exception as e:
                        print(f" Error updating terminal: {e}")
                    
                    # Update the occupied blocks display - CRITICAL
                    try:
                        self.update_occupied_blocks_display()
                        # print("[DEBUG] Called update_occupied_blocks_display after yard dispatch")
                        
                        # UPDATE BLOCK MARKER TO SHOW TRAIN ICON ON MAP
                        if hasattr(self, 'update_block_marker'):
                            self.update_block_marker(63)
                            # print("[DEBUG] Updated block marker for block 63 - train should now be visible on map")
                    except Exception as e:
                        print(f" Error updating occupied blocks display: {e}")
                    
                    # Force a full UI refresh to ensure everything updates
                    try:
                        self.refresh_ui()
                        # print("[DEBUG] Called refresh_ui after yard dispatch")
                    except Exception as e:
                        print(f" Error during refresh_ui: {e}")
                    
                # Convert block_num to int if it's not already (and not "Yard")
                elif block_num is not None and isinstance(block_num, str):
                    try:
                        block_num = int(block_num)
                    except (ValueError, TypeError):
                        print(f" Could not convert block_num '{block_num}' to int")
                        block_num = None
                
                # If not a yard dispatch and no train_id, create train ONLY if no trains exist yet
                if not is_yard_dispatch and not train_id:
                    # Only create a new train if we don't have any active trains
                    if not self.data_manager.active_trains:
                        self._create_train_from_wayside(commanded_speed, commanded_authority)
                        train_id = self.data_manager.active_trains[-1] if self.data_manager.active_trains else None
                        # print(f" Created new train (none existed): {train_id}")
                    else:
                        # Use the most recent active train instead of creating duplicates
                        train_id = self.data_manager.active_trains[-1]
                        # print(f" No train_id provided in command, using existing train: {train_id}")
                
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
                        # print(f" Updated commanded values for {train_id}: Speed={commanded_speed}, Authority={commanded_authority}")
                        
                        # Send commanded speed to Train Model
                        self.server.send_to_ui("Train Model", {
                            "command": "Commanded Speed",
                            "value": commanded_speed,
                            "train_id": train_id
                        })
                        
                        # Send commanded authority to Train Model
                        self.server.send_to_ui("Train Model", {
                            "command": "Commanded Authority",
                            "value": commanded_authority,
                            "train_id": train_id
                        })
                        # print(f" Sent Commanded Speed and Authority to Train Model for {train_id}")
                    else:
                        pass
                        # print(f" Train {train_id} not found in active trains (will still display in Train Details). Available: {self.data_manager.active_trains}")
                else:
                    pass
                    # print(f" Invalid Speed and Authority format. Got speed={commanded_speed}, auth={commanded_authority}, block={block_num}")
            
            # ============================================================
            # SWITCH STATES - From Wayside Controller (bulk update)
            # Format: [line_indicator, pos1, pos2, pos3, ...]
            # line_indicator: 0 = Green Line, 1 = Red Line
            # Positions are sent in order of block numbers (lowest to highest)
            # Position values: 0 = reverse, 1 = normal
            # Example: [0, 1, 0, 1, 1, 1, 1] for Green Line switches
            # ============================================================
            elif command == 'switch_states':
                if isinstance(value, list) and len(value) >= 1:
                    # First element is line indicator
                    line_indicator = value[0]
                    line_name = "Green Line" if line_indicator == 0 else "Red Line" if line_indicator == 1 else "Unknown"
                    
                    # print(f" Received switch states from {source_ui_id}")
                    
                    # Get the switch blocks for the current line
                    if line_indicator == 0:  # Green Line
                        switch_blocks = sorted(self.switch_routing_green.keys())
                    elif line_indicator == 1:  # Red Line
                        switch_blocks = sorted([k for k in self.switch_routing_red.keys() if k not in [1, 16]])  # Exclude bidirectional entries
                    else:
                        # print(f" Unknown line indicator: {line_indicator}")
                        switch_blocks = []
                    
                    # Process each switch position
                    for i, pos in enumerate(value[1:]):  # Skip first element (line_indicator)
                        if i < len(switch_blocks):
                            block_num = switch_blocks[i]
                            
                            # Update the switch state
                            if 1 <= block_num <= len(self.data_manager.blocks):
                                block = self.data_manager.blocks[block_num - 1]
                                # FLIPPED LOGIC: 0 = True (reverse), 1 = False (normal)
                                block.switch_state = not bool(pos)
                                
                                direction = "normal" if pos else "reverse"
                                # print(f"   Updated switch at block {block_num}: {direction}")
                                
                                # Log the switch routing if available
                                if line_indicator == 0 and block_num in self.switch_routing_green:
                                    next_block = self.switch_routing_green[block_num][direction]
                                    # print(f"   Switch {block_num}: {direction} → routes to block {next_block}")
                                elif line_indicator == 1 and block_num in self.switch_routing_red:
                                    next_block = self.switch_routing_red[block_num][direction]
                                    # print(f"   Switch {block_num}: {direction} → routes to block {next_block}")
                    
                    # Refresh UI to show switch updates
                    self.refresh_bidirectional_controls()
                    self.refresh_ui()
                    # print(f"[DEBUG] update_switch_display called")
                else:
                    pass
                    # print(f" Invalid switch_states format: {value}")
            
            # ============================================================
            # RAILROAD CROSSINGS - From Wayside Controller
            # Format: [line_indicator, crossing_state]
            # line_indicator: 0 = Green Line, 1 = Red Line
            # crossing_state: bool (True = active/down, False = inactive/up)
            # Values are received sorted from lowest to highest block number
            # SPLIT BETWEEN Track SW and Track HW based on block ranges
            # Example: [0, True] or [1, False]
            # ============================================================
            elif command == 'rc_states':
                if isinstance(value, list):
                    # print(f" Received railroad crossing states from {source_ui_id}")
                    
                    # Get all blocks with crossings for the current line
                    # You'll need to determine which blocks have crossings
                    # For now, using crossing_blocks set if it exists
                    if hasattr(self, 'crossing_blocks') and self.crossing_blocks:
                        crossing_block_list = sorted(list(self.crossing_blocks))
                    else:
                        # If no crossing_blocks set, you may need to define them
                        # Green Line example blocks with crossings (adjust as needed)
                        crossing_block_list = []  # Add your crossing block numbers here
                    
                    # Filter crossing blocks based on which controller sent the message
                    filtered_crossing_blocks = self.get_blocks_for_controller(source_ui_id, crossing_block_list)
                    
                    # Process each crossing state
                    for i, state in enumerate(value):
                        if i < len(filtered_crossing_blocks):
                            block_num = filtered_crossing_blocks[i]
                            
                            # Convert integer to boolean: 0 = False (inactive/up), 1 = True (active/down)
                            try:
                                crossing_active = bool(int(state))
                                
                                # Update the block's crossing state
                                if 1 <= block_num <= len(self.data_manager.blocks):
                                    block = self.data_manager.blocks[block_num - 1]
                                    block.crossing_state = crossing_active
                                    state_text = "ACTIVE (DOWN)" if crossing_active else "INACTIVE (UP)"
                                    # print(f"   Updated railroad crossing at block {block_num}: {state_text} (from {source_ui_id})")
                            except (ValueError, TypeError) as e:
                                print(f"   Could not parse crossing state for block {block_num}: {state}")
                    
                    # Refresh UI to show crossing updates
                    self.refresh_bidirectional_controls()
                    self.refresh_ui()
                    # print(f"[DEBUG] Railroad crossing states updated from {source_ui_id}")
                else:
                    pass
                    # print(f" Invalid rc_states format: {value}")
            
            # ============================================================
            # LIGHT STATES / SIGNALS - From Wayside Controller
            # Format: [line_indicator, [bit0, bit1]]
            # line_indicator: 0 = Green Line, 1 = Red Line
            # light_state: two-bit boolean array [bit0, bit1]
            # Bit encoding: [False, False] = 0, [True, False] = 1, [False, True] = 2, [True, True] = 3
            # Values are received sorted from lowest to highest block number
            # SPLIT BETWEEN Track SW and Track HW based on block ranges
            # Example: [0, [False, True]] = Green Line, State 2
            # ============================================================
            elif command == 'light_states':
                if isinstance(value, list):
                    # print(f" Received light states from {source_ui_id}")
                    
                    # Get all blocks with lights for the current line
                    current_line = self.selected_line.get() if hasattr(self, 'selected_line') else "Green Line"
                    
                    # Determine which blocks have lights based on current line
                    if "Green" in current_line:
                        light_blocks = sorted(self.light_states)  # Green Line: {1, 62, 76, 100, 150}
                    else:
                        # Red Line would have different light blocks - adjust as needed
                        light_blocks = sorted(self.light_states)  # Use all light blocks
                    
                    # Filter light blocks based on which controller sent the message
                    filtered_light_blocks = self.get_blocks_for_controller(source_ui_id, light_blocks)
                    
                    # Process each light state
                    for i, bit_array in enumerate(value):
                        if i < len(filtered_light_blocks):
                            block_num = filtered_light_blocks[i]
                            
                            # Convert string bits to boolean
                            if isinstance(bit_array, list) and len(bit_array) == 2:
                                try:
                                    bit0 = bool(int(bit_array[0]))  # '1' -> True, '0' -> False
                                    bit1 = bool(int(bit_array[1]))
                                    
                                    # Update the block's light state
                                    if 1 <= block_num <= len(self.data_manager.blocks):
                                        block = self.data_manager.blocks[block_num - 1]
                                        state = (1 if bit0 else 0) + (2 if bit1 else 0)
                                        block.traffic_light_state = state
                                        # print(f"   Updated signal at block {block_num}: State {state} from bits [{bit0}, {bit1}] (from {source_ui_id})")
                                except (ValueError, TypeError) as e:
                                    print(f"   Could not parse bit array for block {block_num}: {bit_array}")
                    
                    # Refresh UI to show light updates
                    self.refresh_bidirectional_controls()
                    self.refresh_ui()
                    # print(f"[DEBUG] Light states updated from {source_ui_id}")
                else:
                    pass
                    # print(f" Invalid light_states format: {value}")


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
                        # print(f" No train_id in Current Speed message, assuming it's for {train_id}")
                
                if speed is not None:
                    # Convert speed to float if needed
                    if isinstance(speed, str):
                        try:
                            speed = float(speed)
                        except (ValueError, TypeError):
                            print(f" Could not convert speed '{speed}' to float")
                            speed = 0
                    
                    # Convert from mph to m/s if needed (Passenger_UI sends in mph)
                    # 1 mph = 0.44704 m/s
                    speed_ms = speed * 0.44704
                    
                    if train_id:
                        # Store actual speed for this train
                        self.train_actual_speeds[train_id] = speed_ms
                        # print(f" Updated current speed for {train_id}: {speed:.1f} mph ({speed_ms:.1f} m/s)")
                        
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
                                    # print(f"   Train {train_id} is on block {block_num}")
                    else:
                        print(f" Could not determine train for speed update: {speed} mph")
                else:
                    pass
                    # print(f" Invalid current speed message: speed={speed}")
        

            # ============================================================            
            # # PASSENGERS DISEMBARKING - From Train Model (Passenger_UI)            # Command format from Passenger_UI: {'command': 'Passenger Disembarking', 'value': disembarking}            # ============================================================            elif command == 'Passenger Disembarking' or command == 'Passengers Disembarking':                disembarking = value                                # Handle block_number if provided (legacy format)                if block_number is not None:                    idx = block_number - 1                    if 0 <= idx < len(self.data_manager.passengers_disembarking):                        if isinstance(disembarking, str):                            try:                                disembarking = int(disembarking)                            except (ValueError, TypeError):                                disembarking = 0                                                self.data_manager.passengers_disembarking[idx] = disembarking                        print(f" Passengers disembarking at block {block_number}: {disembarking}")                                                if block_number in self.station_blocks:                            self.send_station_data_to_ctc(block_number)                                                if hasattr(self, 'view_mode') and self.view_mode.get() == "station":                            self.populate_station_view()                else:                    # Passenger_UI doesn't send block_number, determine from train location                    if isinstance(disembarking, str):                        try:                            disembarking = int(disembarking)                        except (ValueError, TypeError):                            disembarking = 0                                        # Try to find the train                    train_id = message.get('train_id')                    if not train_id and self.data_manager.active_trains:                        train_id = self.data_manager.active_trains[-1]  # Most recent train                        print(f" No train_id, using {train_id}")                                        # Find train's current block                    if train_id and train_id in self.data_manager.active_trains:                        idx = self.data_manager.active_trains.index(train_id)                        if idx < len(self.data_manager.train_locations):                            block_num = self.data_manager.train_locations[idx]                            block_idx = block_num - 1                                                        if 0 <= block_idx < len(self.data_manager.passengers_disembarking):                                self.data_manager.passengers_disembarking[block_idx] = disembarking                                print(f" Passengers disembarking at block {block_num} (train {train_id}): {disembarking}")                                                                if block_num in self.station_blocks:                                    self.send_station_data_to_ctc(block_num)                                                                if hasattr(self, 'view_mode') and self.view_mode.get() == "station":                                    self.populate_station_view()                    else:                        print(f" Could not determine location for {disembarking} disembarking passengers")            
            # ============================================================
            elif command in ['Passengers Disembarking', 'Passenger Disembarking']:
                train_id = message.get('train_id')
                disembarking = value
                
                # Convert value to int if it's a string
                if isinstance(disembarking, str):
                    try:
                        disembarking = int(disembarking)
                    except (ValueError, TypeError):
                        print(f"Could not convert disembarking value '{disembarking}' to int")
                        disembarking = 0
                
                # Determine which block the train is at
                block_number = message.get('block_number')
                
                if block_number is None and train_id:
                    # Find block from train location
                    if train_id in self.data_manager.active_trains:
                        idx = self.data_manager.active_trains.index(train_id)
                        if idx < len(self.data_manager.train_locations):
                            block_number = self.data_manager.train_locations[idx]
                
                if block_number is not None:
                    block_idx = block_number - 1
                    if 0 <= block_idx < len(self.data_manager.passengers_disembarking):
                        self.data_manager.passengers_disembarking[block_idx] = disembarking
                        
                        print(f"Received passengers disembarking:")
                        # print(f"   Train: {train_id if train_id else 'Unknown'}")
                        # print(f"   Block: {block_number}")
                        # print(f"   Passengers: {disembarking}")
                        
                        # Forward to CTC immediately (sends both ticket sales and disembarking)
                        self.send_station_data_to_ctc(block_number)
                        print(f"Forwarded disembarking data to CTC")
                        
                        # Update UI if in station view
                        if hasattr(self, 'view_mode') and self.view_mode.get() == "station":
                            self.populate_station_view()
                    else:
                        print(f"Invalid block index {block_idx} for passengers_disembarking")
                else:
                    print(f"Could not determine block location for disembarking passengers")
            
            # ============================================================
            # TRAIN OCCUPANCY - From Train Model
            # ============================================================
            elif command == 'Train Occupancy' or command == 'train_occupancy':
                # Handle train occupancy from Train Model
                passenger_count = value
                train_id = message.get('train_id')
                
                if not train_id and self.data_manager.active_trains:
                    train_id = self.data_manager.active_trains[-1]  # Most recent train
                    print(f"No train_id in Train Occupancy, using {train_id}")
                
                if train_id and train_id in self.data_manager.active_trains:
                    idx = self.data_manager.active_trains.index(train_id)
                    if isinstance(passenger_count, str):
                        try:
                            passenger_count = int(passenger_count)
                        except (ValueError, TypeError):
                            passenger_count = 0
                    
                    # Ensure train_occupancy list is properly sized
                    while len(self.data_manager.train_occupancy) <= idx:
                        self.data_manager.train_occupancy.append(0)
                    
                    self.data_manager.train_occupancy[idx] = passenger_count
                    print(f"Updated train occupancy for {train_id}: {passenger_count} passengers")
                    
                    # Update Train Details Panel if this train is selected
                    if hasattr(self, 'train_info') and hasattr(self, 'train_combo') and self.train_combo.get() == train_id:
                        self.update_train_info(None)
                    
                    # Update test UI if needed
                    if hasattr(self, 'tester_reference') and hasattr(self.tester_reference, 'refresh_train_details'):
                        self.tester_reference.refresh_train_details()
                else:
                    print(f"Could not find train for occupancy update: {passenger_count} passengers")
            
            # ============================================================
            # TEST COMMAND
            # ============================================================
            elif command == 'test_command':
                pass
                # print(f" Test message received: {value}")
            
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
                            print(f" Could not convert speed '{speed}' to float")
                            speed = 0
                    
                    # Store actual speed for this train
                    self.train_actual_speeds[train_id] = speed
                    # print(f" Updated actual speed for {train_id}: {speed:.1f} m/s")
                    
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
                                # print(f"   Train {train_id} is on block {block_num}")
                else:
                    pass
                    # print(f" Invalid actual speed message: train_id={train_id}, speed={speed}")
            
            # ============================================================
            # REQUEST DATA - Another UI wants our data
            # ============================================================
            elif command == 'request_all_data':
                # print(f" Sending all data to {source_ui_id}")
                self.send_all_outputs()
            
            # ============================================================
            # SWITCH STATES - From Wayside Controller
            # Updates switch positions/directions
            # SPLIT BETWEEN Track SW and Track HW based on block ranges
            # ============================================================
            elif command == 'switch_states':
                switches = message.get('switches', value)
                
                if switches:
                    # print(f" Received switch states from {source_ui_id}")
                    
                    # Handle array of switch states
                    if isinstance(switches, list):
                        # Determine which line we're on
                        current_line = getattr(self, 'selected_line', None)
                        is_red_line = current_line and current_line.get() == "Red Line"
                        
                        # Define switch block mapping based on current line
                        if is_red_line:
                            # Red Line switch mapping
                            switch_block_mapping = {
                                0: 9,    # Yard switch
                                1: 15,   # Loop switch (1-15-16)
                                2: 27,   # Branch switch
                                3: 32,   # Branch switch
                                4: 38,   # Branch switch
                                5: 43,   # Branch switch
                                6: 52,   # Loop switch (52-53-66)
                            }
                        else:
                            # Green Line switch mapping
                            switch_block_mapping = {
                                0: 13,   # Switch at block 13 (actually housed at 12)
                                1: 29,   # Switch at block 29 (actually housed at 28)
                                2: 57,   # Switch at block 57 (actually housed at 58)
                                3: 63,   # Switch at block 63 (actually housed at 62)
                                4: 77,   # Switch at block 77 (actually housed at 76)
                                5: 85,   # Switch at block 85
                            }
                        
                        for idx, direction in enumerate(switches):
                            if idx in switch_block_mapping:
                                block_num = switch_block_mapping[idx]
                                
                                # Only process switches that belong to this controller
                                if source_ui_id == "Track SW" and not self.is_track_sw_block(block_num):
                                    continue  # Skip - this switch belongs to Track HW
                                elif source_ui_id == "Track HW" and self.is_track_sw_block(block_num):
                                    continue  # Skip - this switch belongs to Track SW
                                
                                if 1 <= block_num <= len(self.data_manager.blocks):
                                    block = self.data_manager.blocks[block_num - 1]
                                    
                                    # DEBUG: Log what we received for Red Line switches
                                    if block_num in [27, 32, 38, 43]:
                                        self.log_to_terminal(f"[SWITCH UPDATE] Received update for block {block_num}")
                                        self.log_to_terminal(f"[SWITCH UPDATE]   Raw direction: {repr(direction)}")
                                    
                                    # Normalize direction for consistency
                                    if direction in ["normal", False, 0, "0"]:
                                        direction = "normal"
                                    elif direction in ["reverse", True, 1, "1"]:
                                        direction = "reverse"
                                    else:
                                        direction = "normal"
                                    
                                    # DEBUG: Log normalized direction
                                    if block_num in [27, 32, 38, 43]:
                                        self.log_to_terminal(f"[SWITCH UPDATE]   Normalized direction: {direction}")
                                    
                                    # Show routing path if configured
                                    if hasattr(self, "switch_routing") and block_num in self.switch_routing:
                                        next_block = self.switch_routing[block_num][direction]
                                        # print(f"   Switch {block_num}: {direction} → routes to block {next_block} (from {source_ui_id})")
                                    # Store switch direction in block
                                    block.switch_direction = direction
                                    
                                    # Update switch states dictionary
                                    if not hasattr(self, 'switch_states'):
                                        self.switch_states = {}
                                    self.switch_states[block_num] = direction
                                    
                                    # DEBUG: Confirm storage
                                    if block_num in [27, 32, 38, 43]:
                                        self.log_to_terminal(f"[SWITCH UPDATE]   Stored in switch_states[{block_num}] = '{direction}'")
                                    
                                    # print(f"   Updated switch at block {block_num}: {direction} (from {source_ui_id})")
                                    
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
                    # print(f" Switch update: Block {block} -> {direction}")
                    
                    if isinstance(block, str):
                        block = int(block)
                    
                    # Only process switches that belong to this controller
                    if source_ui_id == "Track SW" and not self.is_track_sw_block(block):
                        # print(f" Ignoring switch update for block {block} - belongs to Track HW")
                        pass
                    elif source_ui_id == "Track HW" and self.is_track_sw_block(block):
                        # print(f" Ignoring switch update for block {block} - belongs to Track SW")
                        pass
                    elif 1 <= block <= len(self.data_manager.blocks):
                        block_obj = self.data_manager.blocks[block - 1]
                        
                        # DEBUG: Log what we received for Red Line switches
                        if block in [27, 32, 38, 43]:
                            self.log_to_terminal(f"[SWITCH UPDATE SINGLE] Received update for block {block}")
                            self.log_to_terminal(f"[SWITCH UPDATE SINGLE]   Raw direction: {repr(direction)}")
                        
                        # Store switch state
                        block_obj.switch_direction = direction
                        
                        # Update switch states dictionary
                        if not hasattr(self, 'switch_states'):
                            self.switch_states = {}
                        self.switch_states[block] = direction
                        
                        # DEBUG: Confirm storage
                        if block in [27, 32, 38, 43]:
                            self.log_to_terminal(f"[SWITCH UPDATE SINGLE]   Stored in switch_states[{block}] = '{direction}'")
                        
                        # Mark block as having a switch
                        self.switch_blocks.add(block)
                        
                        # print(f" Updated switch at block {block}: {direction} (from {source_ui_id})")
                        
                        # Update displays
                        self.refresh_track_data_table()
                        self.refresh_track_system_table()
                        self.update_switch_display()
                        
                        # Update displays
                        self.refresh_track_data_table()
                        self.refresh_track_system_table()
                        self.update_switch_display()
        
        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()


    # ---------------- HELPER METHODS FOR TRACK SW/HW SPLIT ----------------
    
    def is_track_sw_block(self, block_num):
        """
        Determine if a block is controlled by Track SW based on current line.
        
        Green Line: Track SW controls blocks 63-149
        Red Line: Track SW controls blocks 25-48 and 67-76
        
        Returns True if block is controlled by Track SW, False if Track HW
        """
        current_line = self.selected_line.get() if hasattr(self, 'selected_line') else "Green Line"
        
        if "Green" in current_line:
            # Green Line: Track SW controls 63-149
            return 63 <= block_num <= 149
        else:
            # Red Line: Track SW controls 25-48 and 67-76
            return (25 <= block_num <= 48) or (67 <= block_num <= 76)
    
    def get_blocks_for_controller(self, source_ui_id, block_list):
        """
        Filter a list of blocks based on which controller sent the message.
        
        Args:
            source_ui_id: "Track SW" or "Track HW"
            block_list: List of block numbers to filter
            
        Returns:
            Filtered list of blocks that belong to the sending controller
        """
        if source_ui_id == "Track SW":
            return [block for block in block_list if self.is_track_sw_block(block)]
        elif source_ui_id == "Track HW":
            return [block for block in block_list if not self.is_track_sw_block(block)]
        else:
            # If source is unknown, return all blocks (backwards compatibility)
            return block_list

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
        
        # print(f"\n TEST BLOCK OCCUPANCY:")
        # print(f"   Sending: {test_occupancy}")
        
        # Simulate receiving the occupancy command
        self._process_message({
            'command': 'block_occupancy',
            'value': test_occupancy
        }, "TEST_SIMULATION")
        
        # Also test the dictionary format
        test_occupancy_dict = {block_num: occupancy}
        # print(f"\n TEST BLOCK OCCUPANCY (dict format):")
        # print(f"   Sending: {test_occupancy_dict}")
        
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
    # print("\n" + "="*60)
    # print("SYSTEM INTEGRATION CHECK")
    # print("="*60)
    # print(f"Main UI manager: {app.data_manager}")
    # print(f"Test UI manager: {tester.manager}") 
    # print(f"Same instance: {app.data_manager is tester.manager}")
    # print(f"Bidirectional data shared: {hasattr(manager, 'bidirectional_directions')}")
    # print(f"Socket server running: {app.server.running}")
    # print(f"Allowed connections: {app.server.allowed_connections}")
    # print(f"Connected clients: {list(app.server.connected_clients.keys())}")
    # print("="*60 + "\n")
    
    # Test sending data (optional - uncomment to test immediately)
    # # print(" Testing data transmission...")
    # app.send_all_outputs()
    
    tester.lift()
    app.mainloop()