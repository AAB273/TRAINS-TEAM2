import tkinter as tk
import pandas as pd
from tkinter import ttk
from PIL import Image, ImageTk
import UI_Variables
import tkinter.simpledialog as simpledialog
from Test_UI import TrackModelTestUI  # Test/debug UI
from FileUploadManager import FileUploadManager
from TrackDiagramDrawer import TrackDiagramDrawer
from TrackDirectionController import TrackDirectionController
from HeaterSystemManager import HeaterSystemManager
from BeaconManager import BeaconManager

class TrackModelUI(tk.Tk):
    def __init__(self, manager: UI_Variables.TrackDataManager):
        super().__init__()
        self.title("Track Model UI")
        self.geometry("1300x850")
        self.configure(bg="navy")

        self.switch_blocks = {5}
        self.crossing_blocks = {4}
        self.signal_blocks = {6, 11}
        self.station_blocks = {10, 15}  # pulled from TrackDataManager default stations

        # Same as diagram coordinates
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

        # Use the shared TrackDataManager
        self.data_manager = manager

        for b in self.data_manager.blocks:
            if not hasattr(b, "traffic_light_state"):
                b.traffic_light_state = 0

        style = ttk.Style(self)
        style.configure("Large.TCheckbutton", font=("Arial", 11), padding=5)

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

        # ---------------- Modular System Managers ----------------
        self.file_manager = FileUploadManager(self)
        self.diagram_drawer = TrackDiagramDrawer(self, self.data_manager)
        self.direction_controller = TrackDirectionController(self)
        self.heater_manager = HeaterSystemManager(self)

        # Build UI
        self.create_left_panel(left_frame)
        self.create_center_panel(center_frame)
        self.create_bottom_table(center_frame)


        self.after(1000, self.direction_controller.force_bidirectional_table_visible)

        # Refresh periodically
        self.after(1000, self.refresh_ui)

    # ---------------- Helper ----------------
    def make_card(self, parent, title=None):
        card = tk.Frame(parent, bg="white", bd=2, relief="ridge")
        if title:
            tk.Label(card, text=title, font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
        return card

    # ---------------- Left Panel ----------------
    def create_left_panel(self, parent):
        # Logo
        try:
            img = Image.open("blt logo.png").resize((120, 120))
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self.logo_img, bg="navy").pack(pady=10)
        except:
            tk.Label(parent, text="Logo not found", bg="navy", fg="white").pack(pady=10)

        # Environment Temp
        temp_card = self.make_card(parent, "Environment")

        def set_environment_temp():
            new_temp = simpledialog.askfloat("Set Temperature", "Enter new environmental temperature (°C):")
            if new_temp is not None:
                self.data_manager.environmental_temp = new_temp
                self.temp_label.config(text=f"Temperature: {new_temp}°C")

        tk.Button(temp_card, text="Set Environmental Temp", command=set_environment_temp).pack(padx=10, pady=10)
        self.temp_label = tk.Label(
            temp_card,
            text=f"Temperature: {getattr(self.data_manager, 'environmental_temp', '--')}°C",
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

        # Failure Modes
        fail_card = self.make_card(parent, "Murphy Failure Modes")
        self.failure_train_circuit_var = tk.BooleanVar(value=False)
        self.failure_rail_var = tk.BooleanVar(value=False)
        self.failure_power_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            fail_card, text="Train Circuit", variable=self.failure_train_circuit_var,
            command=self.on_failure_changed, style="Large.TCheckbutton"
        ).pack(pady=10, padx=5, fill='x', expand=True)
        ttk.Checkbutton(
            fail_card, text="Broken Railroads", variable=self.failure_rail_var,
            command=self.on_failure_changed, style="Large.TCheckbutton"
        ).pack(pady=10, padx=5, fill='x', expand=True)
        ttk.Checkbutton(
            fail_card, text="Power", variable=self.failure_power_var,
            command=self.on_failure_changed, style="Large.TCheckbutton"
        ).pack(pady=10, padx=5, fill='x', expand=True)
        fail_card.pack(fill="x", pady=10)

        # Filters
        filter_card = self.make_card(parent, "Table View")
        self.filter_card = filter_card

        self.view_mode = tk.StringVar(value="track")
        self.view_tabs = ttk.Notebook(filter_card)
        self.track_tab = tk.Frame(self.view_tabs, bg="white")
        self.station_tab = tk.Frame(self.view_tabs, bg="white")

        self.view_tabs.add(self.track_tab, text="Track View")
        self.view_tabs.add(self.station_tab, text="Station View")
        self.view_tabs.pack(fill="x", padx=5, pady=5)
        self.view_tabs.bind("<<NotebookTabChanged>>", self.on_view_tab_change)

        self.init_filter_checkbuttons()
        filter_card.pack(fill="x", pady=10)

    def init_filter_checkbuttons(self):
        # Destroy previous checkbuttons first
        for widget in self.filter_card.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.destroy()

        options = ["All Blocks", "Switch Blocks", "Crossing Blocks", "Station Blocks",
                "Bidirectional Blocks", "Signal Blocks"] if self.view_mode.get() == "track" else \
                ["All Stations", "Boarding Stations", "Waiting Stations"]

        for opt in options:
            if opt not in self.filter_vars:
                self.filter_vars[opt] = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.filter_card, text=opt, bg="white", variable=self.filter_vars[opt])
            cb.pack(anchor="w", padx=10)

    def update_train_info(self, event):
        idx = self.train_combo.current()
        occ = self.data_manager.train_occupancy[idx]
        spd = self.data_manager.commanded_speed[idx]
        auth = self.data_manager.commanded_authority[idx]
        self.train_info.config(
            text=f"Occupancy: {occ} People\nCommanded Speed: {spd} m/s\nCommanded Authority: {auth} blocks"
        )

    # ---------------- Center Panel ----------------
    def create_center_panel(self, parent):
        # Create card for notebook with fixed height (same as before)
        card = self.make_card(parent)
        card.pack(fill="both", expand=True)
        card.config(height=500)  # fixed height to prevent shrinking
        card.pack_propagate(False)

        # Use a simple notebook layout
        notebook = ttk.Notebook(card)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Track Diagram
        frame1 = tk.Frame(notebook, bg="white")
        notebook.add(frame1, text="Track Switches and Signals")
        self.diagram_frame = frame1
        
        # Build track diagram (using the existing method that uses self.diagram_frame)
        self.build_track_diagram()

        # ADD PLC PANEL TO TAB 1 - place it in the top-right corner
        plc_panel1 = self.file_manager.create_PLCupload_panel(frame1)
        plc_panel1.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Tab 2: Block/Station Occupancy
        frame2 = tk.Frame(notebook, bg="white")
        notebook.add(frame2, text="Block and Station Occupancy")

        # --- Add Blue Line image to tab 2 ---
        try:
            bg_img2 = Image.open("Blue Line.png").resize((900, 450), Image.LANCZOS)
            self.block_view_bg = ImageTk.PhotoImage(bg_img2)
            self.block_canvas = tk.Canvas(frame2, bg="white", height=450, width=900, highlightthickness=0)
            self.block_canvas.pack(fill="x", padx=10, pady=10)
            self.block_canvas.create_image(0, 0, image=self.block_view_bg, anchor="nw")
            self.block_canvas.config(scrollregion=self.block_canvas.bbox("all"))
            
            # Initialize train items for the center panel occupancy tab
            self.train_items_center = []
            
        except Exception as e:
            print("⚠️ Could not load Blue Line.png for Block/Station tab:", e)
            self.block_canvas = tk.Canvas(frame2, bg="white", height=450, width=900)
            self.block_canvas.pack(fill="x", padx=10, pady=10)
            self.train_items_center = []

        # ADD PLC PANEL TO TAB 2 - place it in the top-right corner
        plc_panel2 = self.file_manager.create_PLCupload_panel(frame2)
        plc_panel2.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    # ---------------- Bottom Table ----------------
    def create_bottom_table(self, parent):
        card = self.make_card(parent, "Track / Station Data")
        card.pack(fill="both", expand=True)
        self.table_frame = tk.Frame(card, bg="white")
        self.table_frame.pack(fill="both", expand=True)

        # Initialize Treeview once
        self.columns_track = ("Block", "Grade", "Elevation", "Length", "Speed Limit", "Heaters", "Beacons")
        self.columns_station = ("Block", "Station", "Ticket Sales", "Passengers Boarding", "Passengers Disembarking")
        self.tree = ttk.Treeview(self.table_frame, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_bottom_table()

    def update_bottom_table(self):
        if self.view_mode.get() == "track":
            self.show_track_view()
        else:
            self.show_station_view()
        # Filters remain intact; no destroying checkbuttons
        self.init_filter_checkbuttons()

    def refresh_block_table(self):
        """Refresh the block table display"""
        self.update_bottom_table()

    def show_track_view(self):
        """Display the track table view with active filters applied."""

        # --- Define filter sets (use your actual block locations) ---
        switch_blocks = {5, 6, 11}
        crossing_blocks = {4}
        signal_blocks = {6, 11}
        station_blocks = {10, 15}
        # All blocks are bidirectional, so we'll include all block numbers 1-15
        bidirectional_blocks = set(range(1, 16))  # Blocks 1 through 15

        # --- Configure columns ---
        self.tree.config(columns=self.columns_track)
        for col in self.columns_track:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120, anchor="center")

        # --- Clear existing rows ---
        self.tree.delete(*self.tree.get_children())

        # --- Get filter states ---
        show_all = self.filter_vars["All Blocks"].get()
        show_switch = self.filter_vars["Switch Blocks"].get()
        show_crossing = self.filter_vars["Crossing Blocks"].get()
        show_station = self.filter_vars["Station Blocks"].get()
        show_bidirectional = self.filter_vars["Bidirectional Blocks"].get()  # New filter
        show_signal = self.filter_vars["Signal Blocks"].get()

        # --- Insert filtered rows ---
        for b in self.data_manager.blocks:
            num = b.block_number

            # Determine if block should be shown
            if show_all:
                show = True
            else:
                show = False
                if show_switch and num in switch_blocks:
                    show = True
                elif show_crossing and num in crossing_blocks:
                    show = True
                elif show_station and num in station_blocks:
                    show = True
                elif show_bidirectional and num in bidirectional_blocks:  # New condition
                    show = True
                elif show_signal and num in signal_blocks:
                    show = True

            # Insert visible blocks
            if show:
                heater_display = f"{'On' if self.heater_manager.is_heater_on(b) else 'Off'}/{'Working' if self.heater_manager.is_heater_working(b) else 'Broken'}"
            
                # Simple beacon display - only show Active/Inactive
                beacon_active = BeaconManager.is_beacon_active(b)
                beacon_display = "Active" if beacon_active else "Inactive"
            
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        b.block_number,
                        f"{b.grade}%",
                        f"{b.elevation}m",
                        f"{b.length}m",
                        f"{b.speed_limit} km/h",
                        heater_display,
                        beacon_display,
                    ),
                )

    def show_station_view(self):
        """Display station data with Blue Line image and dynamic train positions."""
        
        # --- Configure columns for station view ---
        self.tree.config(columns=self.columns_station)
        for col in self.columns_station:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        
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
                blue_line_img = Image.open("Blue Line.png").resize((900, 450), Image.LANCZOS)
                self.block_bg_img = ImageTk.PhotoImage(blue_line_img)
                self.block_canvas = tk.Canvas(self.block_frame, bg="white", height=450, width=900, highlightthickness=0)
                self.block_canvas.pack(fill="x", padx=10, pady=10)
                self.block_canvas.create_image(0, 0, image=self.block_bg_img, anchor="nw")
                self.block_canvas.config(scrollregion=self.block_canvas.bbox("all"))
            except Exception as e:
                print("⚠️ Could not load Blue Line.png for occupancy view:", e)
                self.block_canvas = tk.Canvas(self.block_frame, bg="white", height=450, width=900)
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

        print("🔍 === Checking Block Occupancy ===")
        occupied_blocks = []
        
        # Check all blocks for occupancy
        for i, block in enumerate(self.data_manager.blocks):
            block_num = i + 1
            occupancy_value = getattr(block, 'occupancy', 0)
            if occupancy_value != 0:
                occupied_blocks.append(block_num)
                print(f"   Block {block_num}: OCCUPIED (value: {occupancy_value})")
        
        print(f"   Found {len(occupied_blocks)} occupied blocks: {occupied_blocks}")
        
        trains_drawn = 0
        # Draw trains for occupied blocks
        for block_num in occupied_blocks:
            coords = self.block_positions_occupancy.get(block_num)
            if coords:
                x, y = coords
                item = canvas.create_image(x, y, image=self.train_icon, anchor="center")
                items_list.append(item)
                trains_drawn += 1
                print(f"   🚂 Drawing train at block {block_num}, coordinates: {coords}")
            else:
                print(f"   ❌ Block {block_num} occupied but no coordinates available")

        print(f"🎯 Total trains drawn: {trains_drawn}")
        print("=====================================")

    def on_view_tab_change(self, event):
        tab = self.view_tabs.tab(self.view_tabs.select(), "text")
        self.view_mode.set("track" if tab == "Track View" else "station")
        self.update_bottom_table()

    def on_all_blocks_toggle(self):
        """Toggles all other checkbuttons when All Blocks is clicked."""
        all_on = self.filter_vars["All Blocks"].get()
        for key, var in self.filter_vars.items():
            if key != "All Blocks":
                var.set(all_on)
        self.refresh_block_table()

    # ---------------- Create canvas, load images, initial draw (replace your build_track_diagram) ----------------
    def build_track_diagram(self):
        # Container for the diagram and PLC upload
        diagram_container = tk.Frame(self.diagram_frame, bg="white")
        diagram_container.pack(fill="both", expand=True)

        # Canvas inside left side of container
        self.track_canvas = tk.Canvas(diagram_container, bg="white", height=450)
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
            bg_img = Image.open("Blue Line.png").resize((900, 450), Image.LANCZOS)
            self.track_bg = ImageTk.PhotoImage(bg_img)
            self.track_canvas.create_image(0, 0, image=self.track_bg, anchor="nw")
            self.track_canvas.config(scrollregion=self.track_canvas.bbox("all"))
        except Exception as e:
            print("⚠️ Could not load background Blue Line.png:", e)

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
        self.diagram_drawer.draw_track_icons()


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
        for idx, station in enumerate(dm.station_location):
            block_num, station_name = station
            terminal.insert("end", f"Station {station_name} (Block {block_num}):\n")
            terminal.insert("end", f"  Tickets Sold: {int(dm.ticket_sales[idx])}\n")
            terminal.insert("end", f"  Passengers Boarding: {int(dm.passengers_boarding[idx])}\n")
            terminal.insert("end", f"  Passengers Disembarking: {int(dm.passengers_disembarking[idx])}\n\n")

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

        # Heater Status
#        terminal.insert("end", "=== HEATER STATUS ===\n")
#        for block in dm.blocks:
#            if hasattr(block, 'track_heater') and isinstance(block.track_heater, list):
#                if block.track_heater[0] == 1 or block.track_heater[1] == 0:  # On or broken
#                    status = "ON" if block.track_heater[0] == 1 else "OFF"
#                    working = "WORKING" if block.track_heater[1] == 1 else "BROKEN"
#                    terminal.insert("end", f"Block {block.block_number}: {status} / {working}\n")
#        terminal.insert("end", "\n")

        terminal.insert("end", "=== BIDIRECTIONAL BLOCK DIRECTIONS ===\n")
        for group, direction in self.data_manager.bidirectional_directions.items():
            direction_text = "← Left" if direction == 0 else "Right →"
            terminal.insert("end", f"{group}: {direction_text}\n")
        terminal.insert("end", "\n")
            
        terminal.see("end")
        terminal.config(state="disabled")
        print("✅ Terminal update complete")

#        
#        terminal.see("end")
#        terminal.config(state="disabled")
#        print("✅ Terminal update complete")

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

    def process_structured_track_data(self, df):
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
                else:
                    print(f"❌ Block number {block_num} out of range (1-{len(self.data_manager.blocks)})")
            
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
        self.update_bidirectional_table()
        
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

    def process_infrastructure(self, block, infrastructure):
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

    def on_failure_changed(self):
        print("Failure states updated")

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

    # Refresh UI periodically
    def refresh_ui(self):
        # Update environmental temp
        self.temp_label.config(text=f"Temperature: {getattr(self.data_manager, 'environmental_temp', '--')}°C")

        # Update bottom table in-place
        self.update_bottom_table()

        # Redraw track icons (switches, crossings, lights)
        self.draw_track_icons()

        # Refresh bidirectional table 
        self.update_bidirectional_table()

        # REMOVED: Automatic terminal refresh - terminal only updates on button click now

        # Draw trains on BOTH occupancy canvases:
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_block_canvas"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_block_canvas)
        
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_center"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_center)

        # Refresh again in 1 second
        self.after(1000, self.refresh_ui)

# ---------------- Run Application ----------------
if __name__ == "__main__":
    manager = UI_Variables.TrackDataManager()
    app = TrackModelUI(manager)
    tester = TrackModelTestUI(app, manager)
    
    # Store reference to test UI for refreshing
    app.tester_reference = tester
    
    # Verify integration
    print("=== SYSTEM INTEGRATION CHECK ===")
    print(f"Main UI manager: {app.data_manager}")
    print(f"Test UI manager: {tester.manager}") 
    print(f"Same instance: {app.data_manager is tester.manager}")
    print(f"Bidirectional data shared: {hasattr(manager, 'bidirectional_directions')}")
    
    tester.lift()
    app.mainloop()