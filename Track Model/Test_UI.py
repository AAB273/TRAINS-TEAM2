import tkinter as tk
from tkinter import ttk
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
        tk.Label(frame, text="Blocks", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        columns = ("Block", "Length", "Grade", "Elevation", "Speed Limit", "Heater", "Beacon")
        self.tree_blocks = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_blocks.heading(col, text=col)
            self.tree_blocks.column(col, width=80, anchor="center")
        self.tree_blocks.pack(fill="x", padx=10, pady=5)

        # Populate with current data
        self.refresh_block_table()

        # Editing buttons
        edit_frame = tk.Frame(frame, bg="white")
        edit_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(edit_frame, text="Edit Selected Block", command=self.edit_selected_block).pack(side="left", padx=5)
        tk.Button(edit_frame, text="Refresh Table", command=self.refresh_block_table).pack(side="left", padx=5)

        # Station data below blocks
        tk.Label(frame, text="Stations", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        station_columns = ("Block", "Station", "Ticket Sales", "Boarding", "Disembarking")
        self.tree_stations = ttk.Treeview(frame, columns=station_columns, show="headings", height=5)
        for col in station_columns:
            self.tree_stations.heading(col, text=col)
            self.tree_stations.column(col, width=100, anchor="center")
        self.tree_stations.pack(fill="x", padx=10, pady=5)
        self.refresh_station_table()

    def refresh_block_table(self):
        for row in self.tree_blocks.get_children():
            self.tree_blocks.delete(row)
        for b in self.manager.blocks:
            self.tree_blocks.insert("", "end", values=(b.block_number, b.length, b.grade,
                                                       b.elevation, b.speed_limit, b.track_heater, b.beacon))

    def refresh_station_table(self):
        for row in self.tree_stations.get_children():
            self.tree_stations.delete(row)
        for idx, (block_num, station_name) in enumerate(self.manager.station_location):
            self.tree_stations.insert("", "end", values=(block_num, station_name,
                                                         self.manager.ticket_sales[idx],
                                                         self.manager.passengers_boarding[idx],
                                                         self.manager.passengers_disembarking[idx]))

    def edit_selected_block(self):
        selected = self.tree_blocks.selection()
        if not selected:
            return
        item = self.tree_blocks.item(selected[0])
        values = item["values"]
        block_idx = int(values[0]) - 1
        block = self.manager.blocks[block_idx]

        # Popup to edit values
        popup = tk.Toplevel(self)
        popup.title(f"Edit Block {block.block_number}")
        popup.geometry("300x350")

        entries = {}
        for idx, attr in enumerate(["length", "grade", "elevation", "speed_limit", "track_heater", "beacon"]):
            tk.Label(popup, text=attr.capitalize()).pack()
            val = getattr(block, attr)
            e = tk.Entry(popup)
            e.insert(0, str(val))
            e.pack()
            entries[attr] = e

        def save_changes():
            for attr, entry in entries.items():
                val = entry.get()
                # Convert to correct type
                if attr in ["length", "speed_limit", "elevation", "grade"]:
                    val = float(val)
                elif attr in ["track_heater", "beacon"]:
                    val = val.lower() in ["true", "1", "yes"]
                setattr(block, attr, val)
            self.refresh_block_table()
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
        self.refresh_train_table()

        tk.Button(frame, text="Edit Selected Train", command=self.edit_selected_train).pack(pady=5)

    def refresh_train_table(self):
        for row in self.tree_trains.get_children():
            self.tree_trains.delete(row)
        for idx, name in enumerate(self.manager.active_trains):
            self.tree_trains.insert("", "end", values=(name,
                                                       self.manager.train_occupancy[idx],
                                                       self.manager.commanded_speed[idx],
                                                       self.manager.commanded_authority[idx]))

    def edit_selected_train(self):
        selected = self.tree_trains.selection()
        if not selected:
            return
        item = self.tree_trains.item(selected[0])
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

        # Simple list of switches, crossings, signals
        self.diagram_tree = ttk.Treeview(frame, columns=("Block", "Switch", "Crossing", "Signal", "Occupancy"), show="headings")
        for col in ("Block", "Switch", "Crossing", "Signal", "Occupancy"):
            self.diagram_tree.heading(col, text=col)
            self.diagram_tree.column(col, width=100, anchor="center")
        self.diagram_tree.pack(fill="x", padx=10, pady=5)

        self.refresh_diagram_table()

        tk.Button(frame, text="Edit Selected Element", command=self.edit_selected_diagram).pack(pady=5)

    def refresh_diagram_table(self):
        for row in self.diagram_tree.get_children():
            self.diagram_tree.delete(row)
        for b in self.manager.blocks:
            self.diagram_tree.insert("", "end", values=(b.block_number,
                                                        b.switch_state,
                                                        b.crossing,
                                                        b.signal,
                                                        b.occupancy))

    def edit_selected_diagram(self):
        selected = self.diagram_tree.selection()
        if not selected:
            return
        item = self.diagram_tree.item(selected[0])
        idx = self.diagram_tree.index(selected[0])
        block = self.manager.blocks[idx]

        popup = tk.Toplevel(self)
        popup.title(f"Edit Diagram Block {block.block_number}")
        popup.geometry("300x250")

        entries = {}
        for attr in ["switch_state", "crossing", "signal", "occupancy"]:
            tk.Label(popup, text=attr.capitalize()).pack()
            val = getattr(block, attr)
            e = tk.Entry(popup)
            e.insert(0, str(val))
            e.pack()
            entries[attr] = e

        def save_changes():
            for attr, entry in entries.items():
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
