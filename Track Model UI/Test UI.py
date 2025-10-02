import tkinter as tk
from tkinter import ttk
from UI_Test import load_data  # your backend loader


class EditableTree(ttk.Treeview):
    def __init__(self, parent, data_ref=None, update_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.data_ref = data_ref  # reference to backend list/dict
        self.update_callback = update_callback
        self.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.identify_row(event.y)
        col = self.identify_column(event.x)
        col_index = int(col[1:]) - 1

        x, y, w, h = self.bbox(row_id, col)
        value = self.item(row_id, "values")[col_index]

        entry = tk.Entry(self, width=w, justify="center")
        entry.insert(0, value)
        entry.place(x=x, y=y, width=w, height=h)

        def save_edit(event):
            new_val = entry.get()
            vals = list(self.item(row_id, "values"))
            vals[col_index] = new_val
            self.item(row_id, values=vals)
            entry.destroy()

            # Update backend if callback provided
            if self.update_callback:
                self.update_callback(row_id, col_index, new_val)

        entry.bind("<Return>", save_edit)
        entry.focus_set()


class TestUI(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.title("Track Model Test UI (Editable)")
        self.geometry("1200x700")
        self.data = data

        # Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.create_blocks_tab(notebook)
        self.create_trains_tab(notebook)
        self.create_infra_tab(notebook)
        self.create_stations_tab(notebook)
        self.create_failures_tab(notebook)

    # ---------------- Blocks Tab ----------------
    def create_blocks_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Blocks")

        cols = ("Block", "Grade", "Elevation", "Length", "Speed Limit", "Heater")
        tree = EditableTree(frame, columns=cols, show="headings",
                            update_callback=self.update_block_data)
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for b in self.data["blocks"]:
            tree.insert("", "end", values=(
                getattr(b, "block_number", "--"),
                getattr(b, "grade", "--"),
                getattr(b, "elevation", "--"),
                getattr(b, "length", "--"),
                getattr(b, "speed_limit", "--"),
                getattr(b, "track_heater", "--"),
            ))

    def update_block_data(self, row_id, col_index, new_val):
        i = int(row_id[1:], 16) % len(self.data["blocks"])  # crude map row → index
        b = self.data["blocks"][i]
        if col_index == 1:
            b.grade = float(new_val)
        elif col_index == 2:
            b.elevation = float(new_val)
        elif col_index == 3:
            b.length = float(new_val)
        elif col_index == 4:
            b.speed_limit = float(new_val)
        elif col_index == 5:
            b.track_heater = new_val

    # ---------------- Trains Tab ----------------
    def create_trains_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Trains")

        cols = ("Train ID", "Commanded Speed", "Commanded Authority", "Occupancy")
        tree = EditableTree(frame, columns=cols, show="headings",
                            update_callback=self.update_train_data)
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for i, tid in enumerate(self.data["active_trains"]):
            tree.insert("", "end", values=(
                tid,
                self.data["commanded_speed"][i],
                self.data["commanded_authority"][i],
                self.data["train_occupancy"][i],
            ))

    def update_train_data(self, row_id, col_index, new_val):
        i = int(row_id[1:], 16) % len(self.data["active_trains"])
        if col_index == 0:
            self.data["active_trains"][i] = new_val
        elif col_index == 1:
            self.data["commanded_speed"][i] = float(new_val)
        elif col_index == 2:
            self.data["commanded_authority"][i] = float(new_val)
        elif col_index == 3:
            self.data["train_occupancy"][i] = int(new_val)

    # ---------------- Infrastructure Tab ----------------
    def create_infra_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Switches/Lights/Xings")

        cols = ("Switches", "Lights", "Crossings", "Directions", "Heaters Work")
        tree = EditableTree(frame, columns=cols, show="headings",
                            update_callback=self.update_infra_data)
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for i in range(len(self.data["switch_positions"])):
            tree.insert("", "end", values=(
                self.data["switch_positions"][i],
                self.data["light_states"][i],
                self.data["railway_crossing"][i],
                self.data["track_direction"][i],
                self.data["heaters_work"][i],
            ))

    def update_infra_data(self, row_id, col_index, new_val):
        i = int(row_id[1:], 16) % len(self.data["switch_positions"])
        if col_index == 0:
            self.data["switch_positions"][i] = int(new_val)
        elif col_index == 1:
            self.data["light_states"][i] = new_val
        elif col_index == 2:
            self.data["railway_crossing"][i] = int(new_val)
        elif col_index == 3:
            self.data["track_direction"][i] = int(new_val)
        elif col_index == 4:
            self.data["heaters_work"][i] = int(new_val)

    # ---------------- Stations Tab ----------------
    def create_stations_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Stations")

        cols = ("Block", "Station Name", "Boarding", "Disembarking", "Tickets")
        tree = EditableTree(frame, columns=cols, show="headings",
                            update_callback=self.update_station_data)
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for i, (block, name) in enumerate(self.data["station_location"]):
            tree.insert("", "end", values=(
                block,
                name,
                self.data["passengers_boarding"][i],
                self.data["passengers_disembarking"][i],
                self.data["ticket_sales"][i],
            ))

    def update_station_data(self, row_id, col_index, new_val):
        i = int(row_id[1:], 16) % len(self.data["station_location"])
        block, name = self.data["station_location"][i]
        if col_index == 1:
            self.data["station_location"][i] = (block, new_val)
        elif col_index == 2:
            self.data["passengers_boarding"][i] = int(new_val)
        elif col_index == 3:
            self.data["passengers_disembarking"][i] = int(new_val)
        elif col_index == 4:
            self.data["ticket_sales"][i] = int(new_val)

    # ---------------- Failures Tab ----------------
    def create_failures_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Failures")

        cols = ("Block", "Failure Mode")
        tree = EditableTree(frame, columns=cols, show="headings",
                            update_callback=self.update_fail_data)
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for i, f in enumerate(self.data["failure_modes"]):
            tree.insert("", "end", values=(i + 1, f))

    def update_fail_data(self, row_id, col_index, new_val):
        i = int(row_id[1:], 16) % len(self.data["failure_modes"])
        if col_index == 1:
            self.data["failure_modes"][i] = new_val


if __name__ == "__main__":
    data = load_data()
    app = TestUI(data)
    app.mainloop()
