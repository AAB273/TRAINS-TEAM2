import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import UI_Variables
import tkinter.simpledialog as simpledialog
from Test_UI import TrackModelTestUI  # Test/debug UI


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

        # Build UI
        self.create_left_panel(left_frame)
        self.create_center_panel(center_frame)
        self.create_bottom_table(center_frame)

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
        # Create card for notebook with fixed height
        card = self.make_card(parent)
        card.pack(fill="both", expand=True)
        card.config(height=500)  # fixed height to prevent shrinking
        card.pack_propagate(False)

        # Create notebook inside the card
        notebook = ttk.Notebook(card)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- Tab 1: Track Diagram ----------------
        frame1 = tk.Frame(notebook, bg="white")
        frame1.pack(fill="both", expand=True)
        notebook.add(frame1, text="Track Switches and Signals")

        # Save reference so build_track_diagram can use it
        self.diagram_frame = frame1

        # Build canvas and icons
        self.build_track_diagram()

        # ---------------- Tab 2: Block/Station Table ----------------
        frame2 = tk.Frame(notebook, bg="white")
        frame2.pack(fill="both", expand=True)
        notebook.add(frame2, text="Block and Station Occupancy")
        tk.Label(frame2, text="(Occupancy view goes here)", bg="white").pack(fill="both", expand=True)

#        self.create_PLCupload_panel(frame1).place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
#        self.create_PLCupload_panel(frame2).place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

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

    def show_track_view(self):
        """Display the track table view with active filters applied."""

        # --- Define filter sets (use your actual block locations) ---
        switch_blocks = {5, 6, 11}
        crossing_blocks = {4}
        signal_blocks = {6, 11}
        station_blocks = {10, 15}

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
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        b.block_number,
                        f"{b.grade}%",
                        f"{b.elevation}m",
                        f"{b.length}m",
                        f"{b.speed_limit} km/h",
                        f"{b.track_heater}",
                        f"{b.beacon}",
                    ),
                )

    def show_station_view(self):
        self.tree.config(columns=self.columns_station)
        for col in self.columns_station:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.delete(*self.tree.get_children())

        for block_num, station_name in self.data_manager.station_location:
            idx = block_num - 1
            self.tree.insert("", "end", values=(block_num, station_name,
                                                f"{int(self.data_manager.ticket_sales[idx])} Tickets",
                                                f"{int(self.data_manager.passengers_boarding[idx])} Boarding",
                                                f"{int(self.data_manager.passengers_disembarking[idx])} Leaving"))

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
        # Create canvas on the diagram_frame so icons can be drawn on top of the background
        self.track_canvas = tk.Canvas(self.diagram_frame, bg="white", height=450)
        self.track_canvas.pack(fill="both", expand=True)

        # Load (and persist) background image onto canvas if available
        try:
            bg_img = Image.open("Blue Line.png").resize((900, 450), Image.LANCZOS)
            self.track_bg = ImageTk.PhotoImage(bg_img)
            # Draw background at top-left (0,0), anchor NW so coordinates align
            self.track_canvas.create_image(0, 0, image=self.track_bg, anchor="nw")
            # make canvas size match image
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

        # where we will keep canvas item ids for icons (so we can update/delete them)
        self.icon_item_ids = {"crossing": {}, "switch": {}}

        # Define block -> (x, y) coordinates (adjust to your diagram)
        self.block_positions = {
            4: (340, 200),   # Crossing (example coordinates)
            5: (400, 240),   # Switch
            6: (500, 240),   # Traffic Light
            11: (700, 240),   # Traffic Light
        }

        # Draw initial icons
        self.draw_track_icons()

    def draw_track_icons(self):
        """Draw switch, crossing, and traffic light icons on the diagram based on current states."""
        # Clear previous icons
        for icons in self.icon_item_ids.values():
            for item in icons.values():
                if isinstance(item, list):
                    for subitem in item:
                        self.track_canvas.delete(subitem)
                else:
                    self.track_canvas.delete(item)
        self.icon_item_ids = {"switch": {}, "crossing": {}, "traffic": {}}

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

        # --- Draw Traffic Light 1 (Block 6) ---
        block_traffic1 = self.data_manager.blocks[5]  # index 5 → block 6
        self.draw_traffic_light(6, getattr(block_traffic1, "traffic_light_state", 0), light_size=16)

        # --- Draw Traffic Light 2 (Block 11) ---
        block_traffic2 = self.data_manager.blocks[10]  # index 10 → block 11
        self.draw_traffic_light(11, getattr(block_traffic2, "traffic_light_state", 0), light_size=16)


    def draw_traffic_light(self, block_num, state, light_size=16):
        """Draw a traffic light with 4 positions. Only the active state lights up."""
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
        self.history_label.config(text="Last upload: Just now")
        self.file_status.config(text="Upload successful!")
        self.upload_confirm_button.config(state='disabled')

#    def create_PLCupload_panel(self, parent):
#        frame = tk.Frame(parent, bg="white")
#        tk.Label(frame, text="Upload your PLC program file (.plc, .txt, .csv)",
#                 font=("Arial", 9), bg='white', fg='gray', wraplength=200, justify="center").pack(pady=3)
#        ttk.Button(frame, text="Choose File", command=self.PLCupload_file, width=18).pack(pady=5)
#        self.file_status = tk.Label(frame, text="No file selected", font=("Arial", 9), bg='white', fg='gray')
#        self.file_status.pack(pady=3)
#        self.history_label = tk.Label(frame, text="Last upload: Never", font=("Arial", 8), bg='white', fg='darkgray')
#        self.history_label.pack(pady=3)
#        return frame

    def on_failure_changed(self):
        print("Failure states updated")

    # Refresh UI periodically
    def refresh_ui(self):
        # Update environmental temp
        self.temp_label.config(text=f"Temperature: {getattr(self.data_manager, 'environmental_temp', '--')}°C")

        # Update bottom table in-place
        self.update_bottom_table()

        # Redraw track icons with latest states
        self.draw_track_icons()

        # Refresh again in 1 second
        self.after(1000, self.refresh_ui)

# ---------------- Run Application ----------------
if __name__ == "__main__":
    # Shared TrackDataManager
    manager = UI_Variables.TrackDataManager()

    # Main UI
    app = TrackModelUI(manager)

    # Test/debug UI (Toplevel)
    tester = TrackModelTestUI(app, manager)
    tester.lift()

    app.mainloop()