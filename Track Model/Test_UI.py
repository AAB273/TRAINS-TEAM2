import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import UI_Variables

class TrackModelTestUI(tk.Toplevel):
    def __init__(self, parent, manager: UI_Variables.TrackDataManager):
        super().__init__(parent)
        self.title("Track Model Test / Debug UI")
        self.geometry("800x600")
        self.configure(bg="lightgray")

        self.manager = manager
        print(f"🔗 Test UI and Main UI sharing same manager: {self.manager is parent.data_manager}")

        # ---------------- Train visualization setup ----------------
        from PIL import Image, ImageTk
        train_img = Image.open("Train_Right.png").resize((40, 40), Image.LANCZOS)
        self.train_icon = ImageTk.PhotoImage(train_img)

        self.block_positions_occupancy = {
            4: (335, 240),
            5: (400, 270),
            6: (480, 110),
            10: (550, 300),
            11: (480, 320),
            15: (600, 200)
        }
        self.train_items = []

        # ---------------- Notebook & Tabs ----------------
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- Track/Station Data Tab ----------------
        self.track_tab = tk.Frame(notebook, bg="white")
        notebook.add(self.track_tab, text="Track/Station Data")
        self.build_track_station_tab()

        # ---------------- Train Data Tab ----------------
        self.train_tab = tk.Frame(notebook, bg="white")
        notebook.add(self.train_tab, text="Train Data")
        self.build_train_tab()

        # ---------------- Diagram Data Tab ----------------
        self.diagram_tab = tk.Frame(notebook, bg="white")
        notebook.add(self.diagram_tab, text="Diagram Data")
        self.build_diagram_tab()

        # Periodically refresh UI to reflect backend changes
        self.after(1000, self.refresh_ui)

    # ---------------- Track/Station Data ----------------
    def build_track_station_tab(self):
        frame = self.track_tab

        # ---- Block Table ----
        tk.Label(frame, text="Blocks", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        columns = ("Block", "Length", "Grade", "Elevation", "Speed Limit", "Heater", "Beacon")
        self.tree_blocks = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_blocks.heading(col, text=col)
            self.tree_blocks.column(col, width=80, anchor="center")
        self.tree_blocks.pack(fill="x", padx=10, pady=5)

        # Block editing buttons
        edit_block_frame = tk.Frame(frame, bg="white")
        edit_block_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(edit_block_frame, text="Edit Selected Block", command=self.edit_selected_block).pack(side="left", padx=5)
        tk.Button(edit_block_frame, text="Refresh Table", command=self.refresh_block_table).pack(side="left", padx=5)

        self.refresh_block_table()

        # ---- Station Table ----
        tk.Label(frame, text="Stations", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        station_columns = ("Block", "Station", "Ticket Sales", "Boarding", "Disembarking")
        self.tree_stations = ttk.Treeview(frame, columns=station_columns, show="headings", height=5)

        # Configure station table columns FIRST
        for col in station_columns:
            self.tree_stations.heading(col, text=col)
            self.tree_stations.column(col, width=100, anchor="center")
        self.tree_stations.pack(fill="x", padx=10, pady=5)  # Pack station table BEFORE canvas

        # Station editing buttons
        edit_station_frame = tk.Frame(frame, bg="white")
        edit_station_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(edit_station_frame, text="Edit Selected Station", command=self.edit_selected_station).pack(side="left", padx=5)
        tk.Button(edit_station_frame, text="Refresh Table", command=self.refresh_station_table).pack(side="left", padx=5)

        # ---- Occupancy Canvas (pack this LAST so it doesn't cover other elements) ----
        self.occupancy_canvas = tk.Canvas(frame, width=900, height=450, bg="white")
        self.occupancy_canvas.pack(padx=10, pady=10)

        self.refresh_station_table()

    # ---------------- Block Table Methods ----------------
    def refresh_block_table(self):
        # Remember which block (if any) is currently selected
        selected = self.tree_blocks.selection()
        selected_block_num = None
        if selected:
            item = self.tree_blocks.item(selected[0])
            if item["values"]:
                selected_block_num = item["values"][0]

        # Clear and repopulate the table
        self.tree_blocks.delete(*self.tree_blocks.get_children())
        for b in self.manager.blocks:
            self.tree_blocks.insert(
                "", "end",
                values=(
                    b.block_number,
                    b.length,
                    b.grade,
                    b.elevation,
                    b.speed_limit,
                    b.track_heater,
                    b.beacon
                )
            )

        # Reselect the previously selected block if it still exists
        if selected_block_num is not None:
            for item_id in self.tree_blocks.get_children():
                if self.tree_blocks.item(item_id)["values"][0] == selected_block_num:
                    self.tree_blocks.selection_set(item_id)
                    self.tree_blocks.focus(item_id)
                    break

    def edit_selected_block(self):
        selected = self.tree_blocks.selection()
        if not selected:
            return
        item = self.tree_blocks.item(selected[0])
        values = item["values"]
        block_idx = int(values[0]) - 1
        block = self.manager.blocks[block_idx]

        popup = tk.Toplevel(self)
        popup.title(f"Edit Block {block.block_number}")
        popup.geometry("300x400")  # Increased height for new fields

        entries = {}
        # Existing fields
        for attr in ["length", "grade", "elevation", "speed_limit", "beacon"]:
            tk.Label(popup, text=attr.capitalize()).pack()
            val = getattr(block, attr)
            e = tk.Entry(popup)
            e.insert(0, str(val))
            e.pack()
            entries[attr] = e

        # New heater fields
        tk.Label(popup, text="Heater On (0/1)").pack()
        e_heater_on = tk.Entry(popup)
        e_heater_on.insert(0, str(block.track_heater[0] if isinstance(block.track_heater, list) else 1 if block.track_heater else 0))
        e_heater_on.pack()
        entries["heater_on"] = e_heater_on

        tk.Label(popup, text="Heater Working (0/1)").pack()
        e_heater_working = tk.Entry(popup)
        e_heater_working.insert(0, str(block.track_heater[1] if isinstance(block.track_heater, list) else 1))
        e_heater_working.pack()
        entries["heater_working"] = e_heater_working

        # Add beacon editing
        tk.Label(popup, text="Beacon (128-bit hex)").pack()
        e_beacon = tk.Entry(popup)
        beacon_hex = self.master.beacon_to_hex(block) if hasattr(self.master, 'beacon_to_hex') else "0"*32
        e_beacon.insert(0, beacon_hex)
        e_beacon.pack()
        entries["beacon"] = e_beacon

        def save_changes():
            # ... existing attribute saving ...
            
            # Beacon - handle 128-bit hex
            if "beacon" in entries:
                hex_string = entries["beacon"].get().strip().lower()
                if len(hex_string) == 32 and all(c in '0123456789abcdef' for c in hex_string):
                    if hasattr(self.master, 'beacon_from_hex'):
                        self.master.beacon_from_hex(block, hex_string)
                else:
                    messagebox.showwarning("Invalid Beacon", "Beacon must be 32-character hex string")

        def save_changes():
            for attr, entry in entries.items():
                val = entry.get()
                if attr in ["length", "speed_limit", "elevation", "grade"]:
                    val = float(val)
                elif attr in ["beacon"]:
                    val = val.lower() in ["true", "1", "yes"]
                elif attr in ["heater_on", "heater_working"]:
                    val = int(val)
                    
                if attr == "heater_on":
                    heater_on = val
                elif attr == "heater_working":
                    heater_working = val
                else:
                    setattr(block, attr, val)
            
            # Set heater state with validation
            if not heater_working and heater_on:
                messagebox.showwarning("Invalid State", "Cannot turn on a non-working heater!")
                heater_on = 0  # Force off
            
            block.track_heater = [heater_on, heater_working]
            
            self.refresh_block_table()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_changes).pack(pady=10)

    # ---------------- Station Table Methods ----------------
    def refresh_station_table(self):
        selected = self.tree_stations.selection()
        selected_block_num = None
        if selected:
            item = self.tree_stations.item(selected[0])
            if item["values"]:
                selected_block_num = item["values"][0]

        # Clear the table
        self.tree_stations.delete(*self.tree_stations.get_children())
        
        # Check if we have station data
        if not hasattr(self.manager, 'station_location') or not self.manager.station_location:
            print("No station data found in manager")
            return
            
        # Sort stations by block number and populate table
        stations_sorted = sorted(self.manager.station_location, key=lambda x: x[0])
        for block_num, station_name in stations_sorted:
            idx = block_num - 1  # map to full-length data lists
            
            # Safety check - ensure index is within bounds
            if (idx < len(self.manager.ticket_sales) and 
                idx < len(self.manager.passengers_boarding) and 
                idx < len(self.manager.passengers_disembarking)):
                
                self.tree_stations.insert(
                    "", "end",
                    values=(
                        block_num,
                        station_name,
                        self.manager.ticket_sales[idx],
                        self.manager.passengers_boarding[idx],
                        self.manager.passengers_disembarking[idx],
                    )
                )
            else:
                print(f"Index out of bounds for station at block {block_num}")

        # Reselect previous selection
        if selected_block_num is not None:
            for item_id in self.tree_stations.get_children():
                if self.tree_stations.item(item_id)["values"][0] == selected_block_num:
                    self.tree_stations.selection_set(item_id)
                    self.tree_stations.focus(item_id)
                    break

    def edit_selected_station(self):
        selected = self.tree_stations.selection()
        if not selected:
            return

        tree_idx = self.tree_stations.index(selected[0])
        block_num, station_name = sorted(self.manager.station_location, key=lambda x: x[0])[tree_idx]
        data_idx = block_num - 1  # map to full-length lists

        popup = tk.Toplevel(self)
        popup.title(f"Edit Station {station_name} (Block {block_num})")
        popup.geometry("300x250")

        entries = {}
        for label, attr in [
            ("Ticket Sales", "ticket_sales"),
            ("Passengers Boarding", "passengers_boarding"),
            ("Passengers Disembarking", "passengers_disembarking")
        ]:
            tk.Label(popup, text=label).pack()
            e = tk.Entry(popup)
            e.insert(0, str(getattr(self.manager, attr)[data_idx]))
            e.pack()
            entries[attr] = e

        def save_changes():
            try:
                self.manager.ticket_sales[data_idx] = int(entries["ticket_sales"].get())
                self.manager.passengers_boarding[data_idx] = int(entries["passengers_boarding"].get())
                self.manager.passengers_disembarking[data_idx] = int(entries["passengers_disembarking"].get())
            except ValueError:
                pass

            self.refresh_station_table()
            if hasattr(self.master, "update_bottom_table"):
                self.master.update_bottom_table()

            popup.destroy()

        tk.Button(popup, text="Save", command=save_changes).pack(pady=10)

    # ---------------- Train Data ----------------
    def build_train_tab(self):
        frame = self.train_tab
        tk.Label(frame, text="Trains", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        columns = ("Train", "Occupancy", "Commanded Speed", "Commanded Authority")
        self.tree_trains = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_trains.heading(col, text=col)
            self.tree_trains.column(col, width=120, anchor="center")
        self.tree_trains.pack(fill="x", padx=10, pady=5)

        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(fill="x", pady=5)

        self.btn_add_train = tk.Button(btn_frame, text="Add Train", command=self.add_train)
        self.btn_add_train.pack(side="left", padx=5)

        self.btn_remove_train = tk.Button(btn_frame, text="Remove Selected Train", command=self.remove_train, state="disabled")
        self.btn_remove_train.pack(side="left", padx=5)

        self.btn_edit_train = tk.Button(btn_frame, text="Edit Selected Train", command=self.edit_selected_train)
        self.btn_edit_train.pack(side="left", padx=5)

        self.tree_trains.bind("<<TreeviewSelect>>", self.on_train_select)
        self.refresh_train_table()

    def on_train_select(self, event):
        selected = self.tree_trains.selection()
        self.btn_remove_train.config(state="normal" if selected else "disabled")

    def refresh_train_table(self):
        # Remember which train is selected
        selected = self.tree_trains.selection()
        selected_train_name = None
        if selected:
            item = self.tree_trains.item(selected[0])
            if item["values"]:
                selected_train_name = item["values"][0]

        # Clear and repopulate
        self.tree_trains.delete(*self.tree_trains.get_children())
        for idx, name in enumerate(self.manager.active_trains):
            self.tree_trains.insert(
                "", "end",
                values=(
                    name,
                    self.manager.train_occupancy[idx],
                    self.manager.commanded_speed[idx],
                    self.manager.commanded_authority[idx],
                )
            )

        # Reselect previously selected train
        if selected_train_name is not None:
            for item_id in self.tree_trains.get_children():
                if self.tree_trains.item(item_id)["values"][0] == selected_train_name:
                    self.tree_trains.selection_set(item_id)
                    self.tree_trains.focus(item_id)
                    break

    def add_train(self):
        if len(self.manager.active_trains) >= 16:
            messagebox.showwarning("Limit Reached", "Maximum of 16 trains allowed.")
            return
        name = simpledialog.askstring("Add Train", "Enter train name/ID:")
        if name:
            self.manager.active_trains.append(name)
            self.manager.train_occupancy.append(0)
            self.manager.commanded_speed.append(0)
            self.manager.commanded_authority.append(0)
            self.refresh_train_table()
            if hasattr(self.master, "train_combo"):
                self.master.train_combo['values'] = self.manager.active_trains
                self.master.train_combo.set('')

    def remove_train(self):
        selected = self.tree_trains.selection()
        if not selected:
            return
        idx = self.tree_trains.index(selected[0])
        for attr in ["active_trains", "train_occupancy", "commanded_speed", "commanded_authority"]:
            getattr(self.manager, attr).pop(idx)
        self.refresh_train_table()
        if hasattr(self.master, "train_combo"):
            self.master.train_combo['values'] = self.manager.active_trains
            self.master.train_combo.set('')

    def edit_selected_train(self):
        selected = self.tree_trains.selection()
        if not selected:
            return
        idx = self.tree_trains.index(selected[0])

        popup = tk.Toplevel(self)
        popup.title(f"Edit Train {self.manager.active_trains[idx]}")
        popup.geometry("300x250")

        entries = {}
        for attr in ["train_occupancy", "commanded_speed", "commanded_authority"]:
            tk.Label(popup, text=attr.replace("_", " ").capitalize()).pack()
            val = getattr(self.manager, attr)[idx]
            e = tk.Entry(popup)
            e.insert(0, str(val))
            e.pack()
            entries[attr] = e

        def save_changes():
            for attr, entry in entries.items():
                val = float(entry.get())
                getattr(self.manager, attr).__setitem__(idx, val)
            self.refresh_train_table()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_changes).pack(pady=10)

    # ---------------- Diagram Data ----------------
    def build_diagram_tab(self):
        frame = self.diagram_tab
        tk.Label(frame, text="Diagram Elements", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        self.diagram_tree = ttk.Treeview(frame, columns=("Block", "Switch", "Crossing", "Signal", "Occupancy"), show="headings")
        for col in ("Block", "Switch", "Crossing", "Signal", "Occupancy"):
            self.diagram_tree.heading(col, text=col)
            self.diagram_tree.column(col, width=100, anchor="center")
        self.diagram_tree.pack(fill="x", padx=10, pady=5)

        self.refresh_diagram_table()
        tk.Button(frame, text="Edit Selected Element", command=self.edit_selected_diagram).pack(pady=5)

        # --- NEW: BIDIRECTIONAL BLOCK CONTROLS ---
        tk.Label(frame, text="Bidirectional Block Controls", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(20, 5))

        # Create bidirectional control table
        bidir_columns = ("Block Group", "Current Direction", "Toggle")
        self.bidir_control_tree = ttk.Treeview(frame, columns=bidir_columns, show="headings", height=3)
        
        # Configure columns
        self.bidir_control_tree.heading("Block Group", text="Block Group")
        self.bidir_control_tree.heading("Current Direction", text="Current Direction")
        self.bidir_control_tree.heading("Toggle", text="Toggle")
        
        self.bidir_control_tree.column("Block Group", width=100, anchor="center")
        self.bidir_control_tree.column("Current Direction", width=120, anchor="center")
        self.bidir_control_tree.column("Toggle", width=80, anchor="center")
        
        self.bidir_control_tree.pack(fill="x", padx=10, pady=5)

        # REMOVE THIS: Don't initialize here, use the shared one from TrackDataManager
        # if not hasattr(self.manager, 'bidirectional_directions'):
        #     self.manager.bidirectional_directions = {
        #         "Blocks 1-5": 0,
        #         "Blocks 6-10": 0,
        #         "Blocks 11-15": 0
        #     }

        # Populate the table
        self.refresh_bidirectional_table()

        # Make the table interactive
        self.bidir_control_tree.bind("<ButtonRelease-1>", self.on_bidir_control_click)

    def signal_color(self, bits):
        mapping = {
            (0, 0): "Red",
            (0, 1): "Yellow",
            (1, 0): "Green",
            (1, 1): "Super Green"
        }
        return mapping.get(tuple(bits), "Unknown")

    # ---------------- Diagram Table Refresh ----------------
    def refresh_diagram_table(self):
        selected = self.diagram_tree.selection()
        selected_block_num = None
        if selected:
            item = self.diagram_tree.item(selected[0])
            if item["values"]:
                selected_block_num = item["values"][0]

        self.diagram_tree.delete(*self.diagram_tree.get_children())

        switch_blocks = {5}
        crossing_blocks = {4}
        signal_blocks = {6, 11}

        for b in self.manager.blocks:
            switch_display = bool(b.switch_state) if b.block_number in switch_blocks else "-"
            crossing_display = bool(b.crossing) if b.block_number in crossing_blocks else "-"
            # Ensure signal is a 2-bit list
            if b.block_number in signal_blocks:
                if not hasattr(b, "signal") or not isinstance(b.signal, list):
                    b.signal = [0, 0]
                signal_display = self.signal_color(b.signal)
            else:
                signal_display = "-"

            occupancy_display = bool(b.occupancy)

            self.diagram_tree.insert(
                "", "end",
                values=(
                    b.block_number,
                    switch_display,
                    crossing_display,
                    signal_display,
                    occupancy_display,
                )
            )

        if selected_block_num is not None:
            for item_id in self.diagram_tree.get_children():
                if self.diagram_tree.item(item_id)["values"][0] == selected_block_num:
                    self.diagram_tree.selection_set(item_id)
                    self.diagram_tree.focus(item_id)
                    break

    def refresh_bidirectional_table(self):
        """Update the bidirectional control table with current directions"""
        if hasattr(self, 'bidir_control_tree'):
            # Clear existing rows
            self.bidir_control_tree.delete(*self.bidir_control_tree.get_children())
            
            # Use shared data from TrackDataManager
            if hasattr(self.manager, 'bidirectional_directions'):
                print(f"🔄 Refreshing Test UI table with data: {self.manager.bidirectional_directions}")  # DEBUG
                # Populate with current directions
                for group, direction in self.manager.bidirectional_directions.items():
                    direction_text = "← Left" if direction == 0 else "Right →"
                    toggle_text = "Click to Toggle"
                    self.bidir_control_tree.insert("", "end", values=(group, direction_text, toggle_text))
                    print(f"   Added row: {group} = {direction_text}")  # DEBUG
            else:
                print("❌ No bidirectional_directions found in manager")

    def debug_bidirectional_data(self):
        """Debug method to check bidirectional data state"""
        print("=== BIDIRECTIONAL DATA DEBUG ===")
        print(f"Test UI manager has bidirectional_directions: {hasattr(self.manager, 'bidirectional_directions')}")
        if hasattr(self.manager, 'bidirectional_directions'):
            print(f"Test UI data: {self.manager.bidirectional_directions}")
        
        if hasattr(self.master, 'data_manager'):
            print(f"Main UI data_manager has bidirectional_directions: {hasattr(self.master.data_manager, 'bidirectional_directions')}")
            if hasattr(self.master.data_manager, 'bidirectional_directions'):
                print(f"Main UI data: {self.master.data_manager.bidirectional_directions}")
        
        # Check if they're the same object
        if (hasattr(self.manager, 'bidirectional_directions') and 
            hasattr(self.master, 'data_manager') and 
            hasattr(self.master.data_manager, 'bidirectional_directions')):
            same_object = self.manager.bidirectional_directions is self.master.data_manager.bidirectional_directions
            print(f"Same object: {same_object}")
        print("=================================")

    def on_bidir_control_click(self, event):
        """Handle clicks on the bidirectional control table to toggle directions"""
        item = self.bidir_control_tree.identify_row(event.y)
        if item:
            column = self.bidir_control_tree.identify_column(event.x)
            # Only respond to clicks in the "Toggle" column (column #3)
            if column == "#3":  # Toggle column
                values = self.bidir_control_tree.item(item, "values")
                if values and len(values) > 0:
                    group_name = values[0]
                    self.toggle_bidirectional_direction(group_name)

    def toggle_switch(self, block_num):
        block = self.data_manager.blocks[block_num - 1]
        block.switch_state = not block.switch_state
        print(f"Switch at Block {block_num} is now {'Right' if block.switch_state else 'Left'}")

        if hasattr(self.master, "draw_track_icons"):
            self.master.draw_track_icons()

    def toggle_crossing(self, block_num):
        block = self.data_manager.blocks[block_num - 1]
        block.crossing = not block.crossing
        print(f"Crossing at Block {block_num} is now {'ON' if block.crossing else 'OFF'}")

        # 👇 ADD THIS RIGHT HERE
        if hasattr(self.master, "draw_track_icons"):
            self.master.draw_track_icons()

    # ---------------- Toggle Traffic Light ----------------
    def toggle_traffic_light(self, block_num):
        block = self.manager.blocks[block_num - 1]
        if not hasattr(block, "signal") or not isinstance(block.signal, list):
            block.signal = [0, 0]
        
        # Cycle through the four states
        current = block.signal
        val = (current[0] << 1 | current[1] + 1) % 4
        block.signal = [(val >> 1) & 1, val & 1]
        
        # Also update traffic_light_state for main UI compatibility
        block.traffic_light_state = val
        
        print(f"Traffic light at Block {block_num} updated: {block.signal} (state {val})")
        
        if hasattr(self.master, "draw_track_icons"):
            self.master.draw_track_icons()

    # In Test_UI.py, enhance the toggle method:
    def toggle_bidirectional_direction(self, group_name):
        """Toggle direction with proper synchronization"""
        # Use the main UI's data manager to ensure consistency
        main_manager = self.master.data_manager
        
        if hasattr(main_manager, 'bidirectional_directions') and group_name in main_manager.bidirectional_directions:
            current_direction = main_manager.bidirectional_directions[group_name]
            new_direction = 1 if current_direction == 0 else 0
            
            # Update both managers to stay in sync
            main_manager.bidirectional_directions[group_name] = new_direction
            self.manager.bidirectional_directions[group_name] = new_direction  # Keep test UI in sync
            
            # Refresh both UIs
            self.refresh_bidirectional_table()
            if hasattr(self.master, 'update_bidirectional_table'):
                self.master.update_bidirectional_table()
            
            print(f"✅ {group_name} direction synchronized: {'Right →' if new_direction == 1 else '← Left'}")

# ---------------- Edit Diagram Popup ----------------
    def edit_selected_diagram(self):
        selected = self.diagram_tree.selection()
        if not selected:
            return
        idx = self.diagram_tree.index(selected[0])
        block = self.manager.blocks[idx]

        popup = tk.Toplevel(self)
        popup.title(f"Edit Diagram Block {block.block_number}")
        popup.geometry("300x300")

        switch_blocks = {5}
        crossing_blocks = {4}
        signal_blocks = {6, 11}

        entries = {}

        # Switch
        tk.Label(popup, text="Switch State").pack()
        e_switch = tk.Entry(popup)
        e_switch.insert(0, str(block.switch_state))
        if block.block_number not in switch_blocks:
            e_switch.config(state="disabled")
        e_switch.pack()
        entries["switch_state"] = e_switch

        # Crossing
        tk.Label(popup, text="Crossing").pack()
        e_cross = tk.Entry(popup)
        e_cross.insert(0, str(block.crossing))
        if block.block_number not in crossing_blocks:
            e_cross.config(state="disabled")
        e_cross.pack()
        entries["crossing"] = e_cross

        # Signal: two bits
        if block.block_number in signal_blocks:
            if not hasattr(block, "signal") or not isinstance(block.signal, list):
                block.signal = [0, 0]
            tk.Label(popup, text="Signal Bit 1").pack()
            e_sig0 = tk.Entry(popup)
            e_sig0.insert(0, str(block.signal[0]))
            e_sig0.pack()
            tk.Label(popup, text="Signal Bit 2").pack()
            e_sig1 = tk.Entry(popup)
            e_sig1.insert(0, str(block.signal[1]))
            e_sig1.pack()
            entries["signal"] = (e_sig0, e_sig1)

        # Occupancy
        tk.Label(popup, text="Occupancy").pack()
        e_occ = tk.Entry(popup)
        e_occ.insert(0, str(block.occupancy))
        e_occ.pack()
        entries["occupancy"] = e_occ

        def save_changes():
            # Switch and crossing
            for attr in ["switch_state", "crossing", "occupancy"]:
                entry = entries[attr]
                if entry['state'] != 'disabled':
                    val = entry.get()
                    if attr in ["switch_state", "crossing"]:
                        val = val.lower() in ["true", "1", "yes"]
                    else:
                        val = int(val)
                    setattr(block, attr, val)

            # Signal
            if "signal" in entries:
                b0 = int(entries["signal"][0].get())
                b1 = int(entries["signal"][1].get())
                block.signal = [b0, b1]
                # Also update traffic_light_state
                block.traffic_light_state = (b0 << 1) | b1

            # Occupancy
            entry = entries["occupancy"]
            if entry['state'] != 'disabled':
                val = entry.get()
                # Convert to integer
                if val.lower() in ["true", "1", "yes"]:
                    val = 1
                elif val.lower() in ["false", "0", "no"]:
                    val = 0
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        val = 0
                        
                setattr(block, "occupancy", val)
                print(f"Set block {block.block_number} occupancy to {val}")

            self.refresh_diagram_table()
            
            # Force refresh on the main UI's station occupancy view
            if hasattr(self.master, "refresh_ui"):
                self.master.refresh_ui()
                print("🔄 Triggered Main UI refresh")
            
            popup.destroy()

        tk.Button(popup, text="Save", command=save_changes).pack(pady=10)

    def test_bidirectional_table(self):
        """Test method to manually verify the table works"""
        print("🧪 Testing bidirectional table...")
        if hasattr(self.manager, 'bidirectional_directions'):
            # Toggle a direction manually
            self.manager.bidirectional_directions["Blocks 1-5"] = 1
            self.refresh_bidirectional_table()
            print("✅ Manual test completed")

    def draw_trains(self, canvas, items_list):
        """Draw trains on the given canvas using block occupancy data."""
        if not self.train_icon or canvas is None or items_list is None:
            return

        # Remove previous train images
        for item in items_list:
            canvas.delete(item)
        items_list.clear()

        # Debug: identify which canvas we're drawing on
        if canvas == self.block_canvas:
            print("🟢 Drawing trains on Station Occupancy tab")
        else:
            print("🔴 Drawing trains on UNKNOWN canvas")

        # Draw trains based on block occupancy
        for block_num, coords in self.block_positions_occupancy.items():
            if 1 <= block_num <= len(self.data_manager.blocks):
                block = self.data_manager.blocks[block_num - 1]
                occupancy_value = getattr(block, 'occupancy', 0)
                
                if occupancy_value != 0:
                    x, y = coords
                    item = canvas.create_image(x, y, image=self.train_icon, anchor="center")
                    items_list.append(item)
                    print(f"  ✓ Train drawn at block {block_num}")

    # ---------------- Periodic refresh ----------------
    def refresh_ui(self):
        self.sync_with_main_ui()  # Add this line
        self.refresh_block_table()
        self.refresh_block_table()
        self.refresh_station_table()
        self.refresh_train_table()
        self.refresh_diagram_table()
        self.refresh_bidirectional_table() 
        
        # Add periodic sync with Main UI
        if hasattr(self.master, 'data_manager') and hasattr(self.master.data_manager, 'bidirectional_directions'):
            # Ensure Test UI has the same data as Main UI
            if not hasattr(self.manager, 'bidirectional_directions'):
                self.manager.bidirectional_directions = self.master.data_manager.bidirectional_directions.copy()
        
        self.after(1000, self.refresh_ui)

    # In Test_UI.py, add a sync method:
    def sync_with_main_ui(self):
        """Ensure Test UI data is synchronized with Main UI"""
        if hasattr(self.master, 'data_manager'):
            main_manager = self.master.data_manager
            
            # Sync bidirectional directions
            if hasattr(main_manager, 'bidirectional_directions'):
                if not hasattr(self.manager, 'bidirectional_directions'):
                    self.manager.bidirectional_directions = {}
                self.manager.bidirectional_directions.update(main_manager.bidirectional_directions)
            
            # Sync other critical data as needed
            print("🔄 Test UI synchronized with Main UI")