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
        for col in station_columns:
            self.tree_stations.heading(col, text=col)
            self.tree_stations.column(col, width=100, anchor="center")
        self.tree_stations.pack(fill="x", padx=10, pady=5)

        # Station editing buttons
        edit_station_frame = tk.Frame(frame, bg="white")
        edit_station_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(edit_station_frame, text="Edit Selected Station", command=self.edit_selected_station).pack(side="left", padx=5)
        tk.Button(edit_station_frame, text="Refresh Table", command=self.refresh_station_table).pack(side="left", padx=5)

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
        popup.geometry("300x350")

        entries = {}
        for attr in ["length", "grade", "elevation", "speed_limit", "track_heater", "beacon"]:
            tk.Label(popup, text=attr.capitalize()).pack()
            val = getattr(block, attr)
            e = tk.Entry(popup)
            e.insert(0, str(val))
            e.pack()
            entries[attr] = e

        def save_changes():
            for attr, entry in entries.items():
                val = entry.get()
                if attr in ["length", "speed_limit", "elevation", "grade"]:
                    val = float(val)
                elif attr in ["track_heater", "beacon"]:
                    val = val.lower() in ["true", "1", "yes"]
                setattr(block, attr, val)
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

        self.tree_stations.delete(*self.tree_stations.get_children())
        # Sort stations by block number
        stations_sorted = sorted(self.manager.station_location, key=lambda x: x[0])
        for block_num, station_name in stations_sorted:
            idx = block_num - 1  # map to full-length data lists
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

    def refresh_diagram_table(self):
        # Remember selected block number
        selected = self.diagram_tree.selection()
        selected_block_num = None
        if selected:
            item = self.diagram_tree.item(selected[0])
            if item["values"]:
                selected_block_num = item["values"][0]

        # Clear and repopulate
        self.diagram_tree.delete(*self.diagram_tree.get_children())

        switch_blocks = {5}
        crossing_blocks = {4}
        signal_blocks = {6, 11}

        for b in self.manager.blocks:
            switch_display = bool(b.switch_state) if b.block_number in switch_blocks else "-"
            crossing_display = bool(b.crossing) if b.block_number in crossing_blocks else "-"
            signal_display = bool(b.signal) if b.block_number in signal_blocks else "-"
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

        # Reselect previously selected block
        if selected_block_num is not None:
            for item_id in self.diagram_tree.get_children():
                if self.diagram_tree.item(item_id)["values"][0] == selected_block_num:
                    self.diagram_tree.selection_set(item_id)
                    self.diagram_tree.focus(item_id)
                    break

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

    def toggle_traffic_light(self, block_num):
        block = self.manager.blocks[block_num - 1]
        block.traffic_light_state = (getattr(block, "traffic_light_state", 0) + 1) % 4
        if hasattr(self.master, "draw_track_icons"):
            self.master.draw_track_icons()

    def edit_selected_diagram(self):
        selected = self.diagram_tree.selection()
        if not selected:
            return
        idx = self.diagram_tree.index(selected[0])
        block = self.manager.blocks[idx]

        popup = tk.Toplevel(self)
        popup.title(f"Edit Diagram Block {block.block_number}")
        popup.geometry("300x250")

        switch_blocks = {5}
        crossing_blocks = {4}
        signal_blocks = {6, 11}

        entries = {}
        for attr in ["switch_state", "crossing", "signal", "occupancy"]:
            tk.Label(popup, text=attr.capitalize()).pack()
            val = getattr(block, attr)
            e = tk.Entry(popup)
            e.insert(0, str(val))

            if attr == "switch_state" and block.block_number not in switch_blocks:
                e.config(state="disabled")
            elif attr == "crossing" and block.block_number not in crossing_blocks:
                e.config(state="disabled")
            elif attr == "signal" and block.block_number not in signal_blocks:
                e.config(state="disabled")

            e.pack()
            entries[attr] = e

        def save_changes():
            for attr, entry in entries.items():
                if entry['state'] == 'disabled':
                    continue
                val = entry.get()
                if attr in ["switch_state", "crossing", "signal"]:
                    val = val.lower() in ["true", "1", "yes"]
                elif attr == "occupancy":
                    val = int(val)
                setattr(block, attr, val)
            self.refresh_diagram_table()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_changes).pack(pady=10)

    # ---------------- Periodic refresh ----------------
    def refresh_ui(self):
        self.refresh_block_table()
        self.refresh_station_table()
        self.refresh_train_table()
        self.refresh_diagram_table()
        self.after(1000, self.refresh_ui)