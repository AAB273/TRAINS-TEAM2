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


class TrackModelUI(tk.Tk):
    def __init__(self, manager: UI_Variables.TrackDataManager):
        super().__init__()
        self.title("Track Model UI")
        self.geometry("1300x850")
        self.configure(bg="navy")

        # UI 1 - Can communicate with UI 2 and UI 3
        self.server = TrainSocketServer(port=12345, ui_id="UI_Structure")
        self.server.set_allowed_connections(["Test_UI","ui_3"])
        self.server.start_server(self._process_message)
        self.server.connect_to_ui('localhost',12346,"Test_UI")

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

        self.file_manager = FileUploadManager(self)
        self.heater_manager = HeaterSystemManager(self)
        self.diagram_drawer = TrackDiagramDrawer(self, self.data_manager)
        self.socket_server = TrainSocketServer(self)

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

        # Build UI
        self.create_left_panel(left_frame)
        self.create_center_panel(center_frame)
        self.create_bottom_table(center_frame)

        # Refresh periodically
        self.after(1000, self.refresh_ui)

    def _process_message(self,message,source_ui_id):
        try:
            print(f"Received message from {source_ui_id}: {message}")

            command = message.get('command')
            value = message.get('value')
            
            if command == 'test_command':
                print(f"Message is Processed")
        except Exception as e:
            print(f"Error Processing Message: {e}")

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

        options = ["All Blocks", "Switch Blocks", "Crossing Blocks", "Station Blocks", "Signal Blocks"] if self.view_mode.get() == "track" else \
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
        plc_panel1 = self.create_PLCupload_panel(frame1)
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
        plc_panel2 = self.create_PLCupload_panel(frame2)
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
                        f"{b.elevation} ft",
                        f"{b.length} mi",
                        f"{b.speed_limit} mph",
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

        # --- Draw Crossing (Block 4) ---
        block_cross = self.data_manager.blocks[3]  # index 3 → block 4
        x, y = self.block_positions.get(4, (0, 0))
        img_path = "Crossing_On.png" if block_cross.crossing else "Crossing_Off.png"
        img_obj = load_resized_image(img_path, size=(96, 96))  # slightly smaller
        if img_obj:
            self.icon_item_ids["crossing"][4] = self.track_canvas.create_image(
                x, y + 40, image=img_obj, anchor="center"
            )

        # --- Draw Switch (Block 5) ---
        block_switch = self.data_manager.blocks[4]  # index 4 → block 5
        x, y = self.block_positions.get(5, (0, 0))
        img_path = "Lever_Right.png" if block_switch.switch_state else "Lever_Left.png"
        img_obj = load_resized_image(img_path, size=(64, 64))  # keep doubled size
        if img_obj:
            self.icon_item_ids["switch"][5] = self.track_canvas.create_image(
                x, y, image=img_obj, anchor="center"
            )

        # Draw all traffic lights dynamically based on block numbers
        for b in self.data_manager.blocks:
            if getattr(b, "block_number", None) in [6, 11]:
                self.draw_traffic_light(b.block_number, b.traffic_light_state)

    def draw_traffic_light(self, block_num, state, light_size=16):
        """Draw a traffic light with 4 positions. Handle both traffic_light_state and signal attributes."""
        
        # Convert 2-bit signal to single state if needed
        if isinstance(state, list) and len(state) == 2:
            # Convert [bit1, bit2] to integer 0-3
            state = (state[0] << 1) | state[1]
        
        x, y = self.block_positions.get(block_num, (0,0))
        spacing = 4
        num_lights = 4
        padding = 4

        # Clear previous if exists
        if "traffic" not in self.icon_item_ids:
            self.icon_item_ids["traffic"] = {}
        if block_num in self.icon_item_ids["traffic"]:
            for item in self.icon_item_ids["traffic"][block_num]:
                self.track_canvas.delete(item)

        items = []

        # Rectangle height covers all lights + spacing + padding
        rect_height = num_lights * light_size + (num_lights - 1) * spacing + 2*padding
        rect_width = light_size + 2*padding
        rect_top = y - rect_height//2
        rect_bottom = y + rect_height//2
        rect_left = x - rect_width//2
        rect_right = x + rect_width//2

        # Draw black background
        rect = self.track_canvas.create_rectangle(rect_left, rect_top, rect_right, rect_bottom,
                                                fill="black", outline="black")
        items.append(rect)

        # Draw lights
        lights = ["red", "yellow", "green", "lime"]  # top → bottom
        for i, color in enumerate(lights):
            fill_color = color if state == i else "gray"
            cx1 = x - light_size//2
            cy1 = rect_top + padding + i*(light_size + spacing)
            cx2 = x + light_size//2
            cy2 = cy1 + light_size
            circle = self.track_canvas.create_oval(cx1, cy1, cx2, cy2, fill=fill_color, outline="white")
            items.append(circle)

        self.icon_item_ids["traffic"][block_num] = items

    def draw_signal(self, block_num, state):
        # state is 0-3 representing 00, 01, 10, 11
        colors = ["gray", "yellow", "green", "lime"]  # map 0-3
        color = colors[state]
        x, y = self.block_positions.get(block_num, (0,0))
        size = 10
        self.track_canvas.create_oval(x-size, y-size, x+size, y+size, fill=color)

    def create_PLCupload_panel(self, parent):
            """Creates separate PLC upload and terminal panels to the right of the track diagram."""
            outer_frame = tk.Frame(parent, bg="white")

            # --- PLC UPLOAD SECTION ---
            plc_frame = tk.Frame(outer_frame, bg="white", highlightbackground="#d0d0d0", highlightthickness=1)
            plc_frame.pack(fill="x", padx=5, pady=(0, 8))

            tk.Label(
                plc_frame,
                text="Upload your Track Data file (.png, .csv, .txt, .xlsx)",
                font=("Arial", 9),
                bg='white',
                fg='gray',
                wraplength=200,
                justify="center"
            ).pack(pady=3)

            ttk.Button(
                plc_frame,
                text="Choose File",
                command=self.file_manager.upload_track_file,
                width=18
            ).pack(pady=5)

            file_status = tk.Label(
                plc_frame,
                text="No file selected",
                font=("Arial", 9),
                bg='white',
                fg='gray'
            )
            file_status.pack(pady=3)

            history_label = tk.Label(
                plc_frame,
                text="Last upload: Never",
                font=("Arial", 8),
                bg='white',
                fg='darkgray'
            )
            history_label.pack(pady=3)

            # --- BIDIRECTIONAL BLOCK CONTROLS (WITH BUTTONS LIKE TEST UI) ---
            bidir_frame = tk.Frame(outer_frame, bg="white", highlightbackground="#d0d0d0", highlightthickness=1)
            bidir_frame.pack(fill="x", padx=5, pady=(0, 8))
        

            # --- TERMINAL / EVENT LOG SECTION ---
            terminal_frame = tk.Frame(outer_frame, bg="white", highlightbackground="#d0d0d0", highlightthickness=1)
            terminal_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

            tk.Label(
                terminal_frame,
                text="Event Log / Terminal",
                font=("Arial", 9, "bold"),
                bg="white",
                fg="black"
            ).pack(anchor="w", padx=5, pady=(3, 3))

            term_inner = tk.Frame(terminal_frame, bg="white")
            term_inner.pack(fill="both", expand=True, padx=5, pady=(0, 5))

            # Create terminal widget
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
            
            # STORE THIS TERMINAL REFERENCE
            self.terminals.append(terminal)

            scrollbar = ttk.Scrollbar(term_inner, command=terminal.yview)
            scrollbar.pack(side="right", fill="y")
            terminal.config(yscrollcommand=scrollbar.set)

            # --- SEND OUTPUTS BUTTON ---
            send_button = ttk.Button(outer_frame, text="Send Outputs", command=self.send_outputs)
            send_button.pack(pady=(5, 10), padx=5, anchor="s")

            send_button = ttk.Button(outer_frame, text="Send Beacon Data", command=self.send_outputs)
            send_button.pack(pady=(5, 10), padx=5, anchor="s")

            return outer_frame

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
            new_img = Image.open(filename).resize((900, 450), Image.LANCZOS)
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

    def extract_station_name(self, infrastructure_text):
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

        # REMOVED: Automatic terminal refresh - terminal only updates on button click now

        # Draw trains on BOTH occupancy canvases:
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_block_canvas"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_block_canvas)
        
        if hasattr(self, "block_canvas") and hasattr(self, "train_items_center"):
            self.draw_trains(canvas=self.block_canvas, items_list=self.train_items_center)

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
    
    def on_closing():
        """Handle application closing"""
        print("Closing application...")
        self.server.running = False
        if self.server.server_socket:
            try:
                self.server.server_socket.close()
            except:
                pass
        self.root.destroy()

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
