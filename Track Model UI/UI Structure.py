import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import UI_Test   # <-- backend file with data & Block class
import tkinter.simpledialog as simpledialog

class TrackModelUI(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.title("Track Model UI")
        self.geometry("1300x850")
        self.configure(bg="navy")   # full navy background

        self.data = data

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

        # Build UI
        self.create_left_panel(left_frame)
        self.create_center_panel(center_frame)
        self.create_bottom_table(center_frame)

    # ---------------- Helper ----------------
    def make_card(self, parent, title=None):
        """Helper to make a white box with optional title"""
        card = tk.Frame(parent, bg="white", bd=2, relief="ridge")
        if title:
            tk.Label(card, text=title, font=("Arial", 12, "bold"),
                     bg="white").pack(anchor="w", padx=10, pady=5)
        return card

    # ---------------- Left Panel ----------------
    def create_left_panel(self, parent):

        # --- Top-left Image / Logo ---
        img = Image.open("blt logo.png")   # replace with your image filename
        img = img.resize((120, 120))   # adjust size
        self.logo_img = ImageTk.PhotoImage(img)
        tk.Label(parent, image=self.logo_img, bg="navy").pack(pady=10)

        # Environmental Temp
        temp_card = self.make_card(parent, "Environment")

        def set_environment_temp():
            new_temp = simpledialog.askfloat("Set Temperature", "Enter new environmental temperature (°C):")
            if new_temp is not None:  # user clicked OK
                self.data["environmental_temp"] = new_temp
                self.temp_label.config(text=f"Temperature: {new_temp}°C")

        tk.Button(temp_card, text="Set Environmental Temp", command=set_environment_temp).pack(padx=10, pady=10)
        
        self.temp_label = tk.Label(temp_card, text=f"Temperature: {self.data.get('environmental_temp', '--')}°C",
            bg="white")
        self.temp_label.pack(padx=10, pady=5)
        
        temp_card.pack(fill="x", pady=10)

        # Train Details
        train_card = self.make_card(parent, "Train Details")
        self.train_combo = ttk.Combobox(train_card, values=self.data["active_trains"])
        self.train_combo.bind("<<ComboboxSelected>>", self.update_train_info)
        self.train_combo.pack(padx=10, pady=5)

        self.train_info = tk.Label(train_card, text="Occupancy: --\nCommanded Speed: --\nCommanded Authority: --",
                                   bg="white", justify="left")
        self.train_info.pack(padx=10, pady=5)
        train_card.pack(fill="x", pady=10)

        # ---------------- Failure Modes ----------------
        fail_card = self.make_card(parent, "Murphy Failure Modes")

        # Train Circuit Failure
        self.failure_train_circuit_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            fail_card,
            text="Train Circuit",
            variable=self.failure_train_circuit_var,
            command=self.on_failure_changed,   # callback handler
            style="Large.TCheckbutton"
        ).pack(pady=10, padx=5, fill='x', expand=True)
        tk.Frame(fail_card, bg='black', height=1).pack(fill='x', pady=2)

        # Broken Railroads Failure
        self.failure_rail_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            fail_card,
            text="Broken Railroads",
            variable=self.failure_rail_var,
            command=self.on_failure_changed,
            style="Large.TCheckbutton"
        ).pack(pady=10, padx=5, fill='x', expand=True)
        tk.Frame(fail_card, bg='black', height=1).pack(fill='x', pady=2)

        # Power Failure
        self.failure_power_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            fail_card,
            text="Power",
            variable=self.failure_power_var,
            command=self.on_failure_changed,
            style="Large.TCheckbutton"
        ).pack(pady=10, padx=5, fill='x', expand=True)

        fail_card.pack(fill="x", pady=10)


        # Filters
        filter_card = self.make_card(parent, "Table View")
        self.filter_card = filter_card

        # View selection (Track / Station) using tabs
        self.view_mode = tk.StringVar(value="track")
        self.view_tabs = ttk.Notebook(filter_card)
        self.track_tab = tk.Frame(self.view_tabs, bg="white")
        self.station_tab = tk.Frame(self.view_tabs, bg="white")

        self.view_tabs.add(self.track_tab, text="Track View")
        self.view_tabs.add(self.station_tab, text="Station View")
        self.view_tabs.pack(fill="x", padx=5, pady=5)

        # Track the current tab
        self.view_tabs.bind("<<NotebookTabChanged>>", self.on_view_tab_change)


        # Initialize filter checkbuttons dynamically
        self.filter_checkbuttons = {}
        self.update_filters_for_view()  # create initial checkbuttons
        filter_card.pack(fill="x", pady=10)

    def update_train_info(self, event):
        idx = self.train_combo.current()
        occ = self.data["train_occupancy"][idx]
        spd = self.data["commanded_speed"][idx]
        auth = self.data["commanded_authority"][idx]
        self.train_info.config(text=f"Occupancy: {occ} People\nCommanded Speed: {spd} m/s\nCommanded Authority: {auth} blocks")

    # ---------------- Center Panel ----------------
    def create_center_panel(self, parent):
        card = self.make_card(parent)
        card.pack(fill="both", expand=True)

        notebook = ttk.Notebook(card)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Tab 1: Track Diagram ---
        frame1 = tk.Frame(notebook, bg="white")
        notebook.add(frame1, text="Track Switches and Signals")

        try:
            img = Image.open("Track Diagram.png")
            img = img.resize((450, 550))
            self.track_img = ImageTk.PhotoImage(img)
            tk.Label(frame1, image=self.track_img, bg="white").pack(fill="both", expand=True)
        except FileNotFoundError:
            tk.Label(frame1, text="Track diagram not found", bg="white").pack(fill="both", expand=True)

        plc_panel1 = self.create_PLCupload_panel(frame1)
        plc_panel1.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # fixed in bottom-right

        # --- Tab 2: Occupancy ---
        frame2 = tk.Frame(notebook, bg="white")
        notebook.add(frame2, text="Block and Station Occupancy")

        tk.Label(frame2, text="(Occupancy view goes here)", bg="white").pack(fill="both", expand=True)

        plc_panel2 = self.create_PLCupload_panel(frame2)
        plc_panel2.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # fixed in bottom-right

    # ---------------- Bottom Table ----------------
    def create_bottom_table(self, parent):
        card = self.make_card(parent, "Track / Station Data")
        card.pack(fill="both", expand=True)

        # Table frame
        self.table_frame = tk.Frame(card, bg="white")
        self.table_frame.pack(fill="both", expand=True)

        # Initial table based on current view
        self.update_bottom_table()

    def update_bottom_table(self):
        """Update the table and filter checkbuttons based on the selected view"""
        if self.view_mode.get() == "track":
            self.show_track_view()
        else:
            self.show_station_view()

        # Update filters dynamically
        self.update_filters_for_view()

    def update_filters_for_view(self):
        """Update filter checkbuttons depending on the current view"""
        # Remove old checkbuttons
        for cb in self.filter_checkbuttons.values():
            cb.destroy()
        self.filter_checkbuttons.clear()

        # Define options based on view
        if self.view_mode.get() == "track":
            options = ["All Blocks", "Switch Blocks", "Crossing Blocks", "Station Blocks",
                       "Bidirectional Blocks", "Signal Blocks"]
        else:
            options = ["All Stations", "Boarding Stations", "Waiting Stations"]

        # Create new checkbuttons
        for opt in options:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.filter_card, text=opt, bg="white", variable=var)
            cb.pack(anchor="w", padx=10)
            self.filter_checkbuttons[opt] = cb

    def clear_table(self):
        """Helper: clear table frame before switching views"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

    def show_track_view(self):
        self.clear_table()
        columns = ("Block", "Grade", "Elevation", "Length", "Speed Limit", "Heaters", "Beacons")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")

        col_width = int(self.table_frame.winfo_width() / len(columns))
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=col_width, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate rows
        for b in self.data["blocks"]:
            self.tree.insert("", "end", values=(b.block_number, f"{b.grade}%", f"{b.elevation}m",
                                                f"{b.length}m", f"{b.speed_limit} km/h",
                                                f"{b.track_heater}", f"{b.beacon}"))

    def show_station_view(self):
        self.clear_table()
        columns = ("Block", "Station", "Ticket Sales", "Passengers Boarding", "Passengers Disembarking")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")

        # Evenly space columns
        col_width = int(self.table_frame.winfo_width() / len(columns))
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_width, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate rows from station_location
        for block_num, station_name in data["station_location"]:
            idx = block_num - 1  # align with arrays
            self.tree.insert("", "end", values=(
                block_num,                   # show block number
                station_name,                # show station name
                f"{int(self.data['ticket_sales'][idx])} Tickets",
                f"{int(self.data['passengers_boarding'][idx])} People",
                f"{int(self.data['passengers_disembarking'][idx])} People"
            ))


    def on_view_tab_change(self, event):
        tab = self.view_tabs.tab(self.view_tabs.select(), "text")
        if tab == "Track View":
            self.view_mode.set("track")
        else:
            self.view_mode.set("station")
        self.update_bottom_table()

    def PLCupload_file(self):
        from tkinter import filedialog
        filetypes = [("PLC files", "*.plc"), ("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select PLC File", filetypes=filetypes)

        if filename:
            self.file_status.config(text=f"File selected: {filename.split('/')[-1]}")
            self.history_label.config(text="Last upload: Just now")
        else:
            self.file_status.config(text="No file selected")


    def confirm_upload(self):
        # TODO: implement upload process
        self.history_label.config(text="Last upload: Just now")
        self.file_status.config(text="Upload successful!")
        self.upload_confirm_button.config(state='disabled')

    def create_PLCupload_panel(self, parent):
        PLCupload_frame = tk.Frame(parent, bg="white")

        # Instructions
        instructions = tk.Label(PLCupload_frame,
                                text="Upload your PLC program file (.plc, .txt, .csv)",
                                font=("Arial", 9), bg='white', fg='gray', wraplength=200, justify="center")
        instructions.pack(pady=3)

        # Upload button
        PLCupload_button = ttk.Button(PLCupload_frame, text="Choose File",
                                      command=self.PLCupload_file, width=18)
        PLCupload_button.pack(pady=5)

        # File status display
        self.file_status = tk.Label(PLCupload_frame, text="No file selected",
                                    font=("Arial", 9), bg='white', fg='gray',
                                    wraplength=200, justify='center')
        self.file_status.pack(pady=3)

        # Upload history label
        self.history_label = tk.Label(PLCupload_frame, text="Last upload: Never",
                                      font=("Arial", 8), bg='white', fg='darkgray')
        self.history_label.pack(pady=3)

        return PLCupload_frame

    def on_failure_changed(self):
        print("Failure states:")
        print(" Train Circuit:", self.failure_train_circuit_var.get())
        print(" Broken Railroads:", self.failure_rail_var.get())
        print(" Power:", self.failure_power_var.get())



# ---------------- Run Application ----------------
if __name__ == "__main__":
    data = UI_Test.load_data()
    app = TrackModelUI(data)
    app.mainloop()
