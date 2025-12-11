import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import UI_Variables
import os,sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer

class TrackModelTestUI(tk.Toplevel):
    def __init__(self, parent, manager: UI_Variables.TrackDataManager):
        super().__init__(parent)
        self.title("Track Model Test / Debug UI")
        self.geometry("800x600")
        self.configure(bg="lightgray")

        # Socket server (kept for potential future use, but train deployment uses direct data access)
        self.server = TrainSocketServer(port=12346, ui_id="Test_UI")
        self.server.set_allowed_connections(["UI_Structure", "Track Model", "Train Model", "Track HW"])

        def empty_handler(message, source_ui_id):
            print(f"Test UI received: {message} from {source_ui_id}")

        self.server.start_server(empty_handler)
        
        # Connect to Train Model for beacon signals
        self.server.connect_to_ui('localhost', 12345, "Train Model")
        self.server.connect_to_ui('localhost', 12343, "Train Model")


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

        # Status label for feedback
        self.status_label = tk.Label(self, text="Ready", bg="lightgray", fg="blue", font=("Arial", 10))
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

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

    def send_to_ui(self, command, value=None, **kwargs):
        """Send command to the target UI (creates dict for socket server)"""
        message = {'command': command}
        if value is not None:
            message['value'] = value
        
        # Add any additional kwargs to the message
        message.update(kwargs)
        
        # Send to Track Model
        target_ui = "Track Model"
        success = self.server.send_to_ui(target_ui, message)
        
        if success:
            print(f"📤 Sent {command} to {target_ui}: {message}")
            self.status_label.config(text=f"✅ Sent: {command}")
        else:
            print(f"❌ Failed to send {command} to {target_ui}")
            self.status_label.config(text=f"❌ Failed: {command}")
        return success
    
    def send_beacon(self, beacon_name, state):
        """Send beacon signal to Train Model (which forwards to Train HW/SW)"""
        print(f"\n{'='*60}")
        print(f"[BEACON] Sending {beacon_name} = {state} from Track Model Test UI")
        
        # Send beacon directly to Train Model
        message = {
            'command': beacon_name,
            'value': state
        }
        
        # Track Model forwards to Train Model
        target_ui = "Train Model"
        success = self.server.send_to_ui(target_ui, message)
        
        state_str = "Activated" if state else "Deactivated"
        if success:
            print(f"[BEACON] ✓ {beacon_name} {state_str} - sent to Train Model") #lucas
            self.status_label.config(text=f"✅ {beacon_name} {state_str}", fg="green")
        else:
            print(f"[BEACON] ✗ Failed to send {beacon_name}")
            self.status_label.config(text=f"❌ Failed: {beacon_name}", fg="red")
        print(f"{'='*60}\n")
        
        return success
    
    # ---------------- Track/Station Data ----------------
    def build_track_station_tab(self):
        frame = self.track_tab

        # ---- Block Table ----
        tk.Label(frame, text="Blocks", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        columns = ("Block", "Length", "Grade", "Elevation", "Speed Limit", "Heater")
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
            # Format beacon display to show Active/Inactive like Main UI
            beacon_display = "Active" if self.is_beacon_active(b) else "Inactive"
            
            self.tree_blocks.insert(
                "", "end",
                values=(
                    b.block_number,
                    b.length,
                    b.grade,
                    b.elevation,
                    b.speed_limit,
                    b.track_heater,
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
        popup.geometry("500x550")

        entries = {}
        
        # Existing fields
        for attr in ["length", "grade", "elevation", "speed_limit"]:
            tk.Label(popup, text=attr.capitalize()).pack()
            val = getattr(block, attr)
            e = tk.Entry(popup)
            e.insert(0, str(val))
            e.pack()
            entries[attr] = e

        # Beacon Active (simple true/false input)
        tk.Label(popup, text="Beacon Active:").pack()
        e_beacon_active = tk.Entry(popup)
        # Use the actual beacon state to determine initial value
        beacon_active = self.is_beacon_active(block)
        e_beacon_active.insert(0, str(beacon_active))
        e_beacon_active.pack()
        entries["beacon_active"] = e_beacon_active

        # Beacon fields (only edit if beacon is active)
        beacon_fields = {
            "Station Name": "station_name",
            "Track Direction": "track_direction",  
            "Secondary Block Number": "secondary_block_number",
            "Destination ID": "destination_id",
            "Distance from Destination": "distance_from_destination",
            "Primary Speed Limit": "primary_speed_limit",
            "Secondary Speed Limit": "secondary_speed_limit"
        }

        beacon_entries = {}
        for label, attr in beacon_fields.items():
            tk.Label(popup, text=label).pack()
            e = tk.Entry(popup)
            # Get current value if beacon exists and has the attribute
            current_val = ""
            if hasattr(block, 'beacon') and isinstance(block.beacon, list):
                if attr == "station_name":
                    bits = block.beacon[0:8]
                    chars = []
                    for i in range(0, len(bits), 8):
                        byte_val = int(''.join(str(b) for b in bits[i:i+8]), 2)
                        if byte_val != 0:
                            chars.append(chr(byte_val))
                    current_val = ''.join(chars)
                # Add other beacon field extractions as needed
            e.insert(0, str(current_val))
            e.pack()
            beacon_entries[attr] = e

        def save_changes():
            # Save basic block fields
            for attr in ["length", "grade", "elevation", "speed_limit"]:
                entry = entries[attr]
                val = float(entry.get())
                setattr(block, attr, val)

            # Handle beacon active/inactive
            beacon_active_val = entries["beacon_active"].get().lower() in ["true", "1", "yes"]
            
            if beacon_active_val:
                # Initialize beacon if it doesn't exist
                if not hasattr(block, 'beacon') or not isinstance(block.beacon, list) or len(block.beacon) != 128:
                    block.beacon = [0] * 128
                
                # Set beacon fields (this is a simplified version - you may need to expand this)
                # Station name (first 64 bits = 8 characters)
                station_name = beacon_entries["station_name"].get()
                for i, char in enumerate(station_name[:8]):
                    byte_val = ord(char)
                    for bit in range(8):
                        block.beacon[i*8 + bit] = (byte_val >> (7-bit)) & 1
            else:
                # Deactivate beacon (set all bits to 0)
                if hasattr(block, 'beacon'):
                    block.beacon = [0] * 128

            self.refresh_block_table()
            if hasattr(self.master, "refresh_ui"):
                self.master.refresh_ui()
            
            popup.destroy()

        tk.Button(popup, text="Save", command=save_changes).pack(pady=10)

    def is_beacon_active(self, block):
        """Check if beacon has any bits set (not all zeros)"""
        if hasattr(block, 'beacon') and isinstance(block.beacon, list) and len(block.beacon) == 128:
            return any(bit != 0 for bit in block.beacon)
        return False

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

    # ============================================================
    # NEW: TRAIN DEPLOYMENT FUNCTIONALITY
    # ============================================================
    
    def deploy_train(self):
        """Deploy a new train at a specific block with commanded speed and authority"""
        popup = tk.Toplevel(self)
        popup.title("Deploy Train")
        popup.geometry("400x300")
        
        # Block Number
        tk.Label(popup, text="Block Number (1-150):").pack(pady=5)
        block_entry = tk.Entry(popup)
        block_entry.insert(0, "63")  # Default to yard
        block_entry.pack(pady=5)
        
        # Commanded Speed
        tk.Label(popup, text="Commanded Speed (m/s):").pack(pady=5)
        speed_entry = tk.Entry(popup)
        speed_entry.insert(0, "15.0")
        speed_entry.pack(pady=5)
        
        # Commanded Authority
        tk.Label(popup, text="Commanded Authority (blocks):").pack(pady=5)
        authority_entry = tk.Entry(popup)
        authority_entry.insert(0, "10")
        authority_entry.pack(pady=5)
        
        # Train ID (optional - will auto-generate if blank)
        tk.Label(popup, text="Train ID (optional, e.g., Train_11000):").pack(pady=5)
        train_id_entry = tk.Entry(popup)
        train_id_entry.pack(pady=5)
        
        def do_deploy():
            try:
                block_num = int(block_entry.get())
                speed = float(speed_entry.get())
                authority = int(authority_entry.get())
                train_id_input = train_id_entry.get().strip()
                
                if block_num < 1 or block_num > 150:
                    messagebox.showerror("Error", "Block number must be between 1 and 150")
                    return
                
                # Generate train ID if not provided
                if not train_id_input:
                    if not hasattr(self.manager, "next_train_id"):
                        self.manager.next_train_id = 1
                    train_id = str(self.manager.next_train_id)  # Simple number like "1", "2", "3"
                    self.manager.next_train_id += 1
                else:
                    train_id = train_id_input
                
                print(f"🚂 Deploying train {train_id} at block {block_num}: Speed={speed}, Authority={authority}")
                
                # Add train to active trains list
                self.manager.active_trains.append(train_id)
                
                # Add commanded speed and authority
                self.manager.commanded_speed.append(speed)
                self.manager.commanded_authority.append(authority)
                
                # Add train occupancy (passenger count starts at 0)
                self.manager.train_occupancy.append(0)
                
                # Add train location
                if not hasattr(self.manager, 'train_locations'):
                    self.manager.train_locations = []
                self.manager.train_locations.append(block_num)
                
                # Set block occupancy to the train number
                if block_num <= len(self.manager.blocks):
                    block = self.manager.blocks[block_num - 1]
                    # Train ID is now just a simple number like "1", "2", "3"
                    train_num = int(train_id)  # Train ID is now just a simple number
                    block.occupancy = train_num
                    print(f"✅ Set block {block_num} occupancy to {train_num}")
                
                # Update Main UI if it has methods to refresh
                if hasattr(self.master, 'train_combo'):
                    self.master.train_combo['values'] = self.manager.active_trains
                    self.master.train_combo.set(train_id)
                
                if hasattr(self.master, 'update_occupied_blocks_display'):
                    self.master.update_occupied_blocks_display()
                
                if hasattr(self.master, 'update_block_marker'):
                    self.master.update_block_marker(block_num)
                    print(f"✅ Updated block marker for block {block_num}")
                
                # Set actual speed for train movement
                if hasattr(self.master, 'train_actual_speeds'):
                    self.master.train_actual_speeds[train_id] = 0  # Wait for Train Model to send actual speed
                    print(f"✅ Initialized actual speed for {train_id}: 0 m/s (waiting for Train Model)")
                
                if hasattr(self.master, 'train_positions_in_block'):
                    self.master.train_positions_in_block[train_id] = 0
                
                if hasattr(self.master, 'last_movement_update'):
                    import time
                    self.master.last_movement_update[train_id] = time.time()
                
                # Refresh Test UI
                self.refresh_train_table()
                
                print(f"✅ Train {train_id} successfully deployed!")
                print(f"   Location: Block {block_num}")
                print(f"   Speed: {speed} m/s")
                print(f"   Authority: {authority} blocks")
                print(f"   Active trains: {self.manager.active_trains}")
                
                messagebox.showinfo("Success", f"Train {train_id} deployed at block {block_num}!\n\nSpeed: {speed} m/s\nAuthority: {authority} blocks")
                popup.destroy()
                    
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Deployment failed: {e}")
                import traceback
                traceback.print_exc()
        
        tk.Button(popup, text="Deploy Train", command=do_deploy, bg="green", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack()

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

        # NEW: Deploy Train Button (main action button)
        self.btn_deploy_train = tk.Button(
            btn_frame, 
            text="🚂 Deploy Train", 
            command=self.deploy_train,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_deploy_train.pack(side="left", padx=5)

        self.btn_add_train = tk.Button(btn_frame, text="Add Train (Manual)", command=self.add_train)
        self.btn_add_train.pack(side="left", padx=5)

        self.btn_remove_train = tk.Button(btn_frame, text="Remove Selected Train", command=self.remove_train, state="disabled")
        self.btn_remove_train.pack(side="left", padx=5)

        self.btn_edit_train = tk.Button(btn_frame, text="Edit Selected Train", command=self.edit_selected_train)
        self.btn_edit_train.pack(side="left", padx=5)

        self.tree_trains.bind("<<TreeviewSelect>>", self.on_train_select)
        self.refresh_train_table()

        # ---- Beacon Controls (Red Line Switches) ----
        tk.Label(frame, text="Beacon Controls (Red Line Switches)", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        
        beacon_frame = tk.Frame(frame, bg="lightgray", relief="ridge", bd=2)
        beacon_frame.pack(fill="x", padx=10, pady=5)
        
        # Beacon1 controls
        beacon1_frame = tk.Frame(beacon_frame, bg="lightgray")
        beacon1_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(beacon1_frame, text="Beacon1 (Block 27 → 76-72):", bg="lightgray", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(beacon1_frame, text="ON", bg="green", fg="white", font=("Arial", 9, "bold"),
                 command=lambda: self.send_beacon('Beacon1', True), width=8).pack(side="left", padx=2)
        tk.Button(beacon1_frame, text="OFF", bg="red", fg="white", font=("Arial", 9, "bold"),
                 command=lambda: self.send_beacon('Beacon1', False), width=8).pack(side="left", padx=2)
        
        # Beacon2 controls
        beacon2_frame = tk.Frame(beacon_frame, bg="lightgray")
        beacon2_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(beacon2_frame, text="Beacon2 (Block 38 → 71-67):", bg="lightgray", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(beacon2_frame, text="ON", bg="green", fg="white", font=("Arial", 9, "bold"),
                 command=lambda: self.send_beacon('Beacon2', True), width=8).pack(side="left", padx=2)
        tk.Button(beacon2_frame, text="OFF", bg="red", fg="white", font=("Arial", 9, "bold"),
                 command=lambda: self.send_beacon('Beacon2', False), width=8).pack(side="left", padx=2)

        # ---------------- Current Speed Toggler Section ----------------
        tk.Label(frame, text="Current Speed Control", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        
        speed_frame = tk.Frame(frame, bg="lightblue", relief="ridge", bd=2)
        speed_frame.pack(fill="x", padx=10, pady=5)
        
        # Train selector
        train_select_frame = tk.Frame(speed_frame, bg="lightblue")
        train_select_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(train_select_frame, text="Select Train:", bg="lightblue", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        self.selected_train_var = tk.StringVar()
        self.train_selector = ttk.Combobox(train_select_frame, textvariable=self.selected_train_var, 
                                          state="readonly", width=15)
        self.train_selector.pack(side="left", padx=5)
        self.update_train_selector()  # Initialize with current trains
        
        # Speed display
        speed_display_frame = tk.Frame(speed_frame, bg="lightblue")
        speed_display_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(speed_display_frame, text="Current Speed:", bg="lightblue", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        self.current_speed_var = tk.StringVar(value="0")
        self.speed_display_label = tk.Label(speed_display_frame, textvariable=self.current_speed_var, 
                                            bg="white", fg="darkblue", font=("Arial", 16, "bold"), 
                                            width=6, relief="sunken", bd=2)
        self.speed_display_label.pack(side="left", padx=5)
        tk.Label(speed_display_frame, text="m/s", bg="lightblue", font=("Arial", 11)).pack(side="left")
        
        # Speed slider
        slider_frame = tk.Frame(speed_frame, bg="lightblue")
        slider_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(slider_frame, text="Set Speed:", bg="lightblue", font=("Arial", 10)).pack(side="left", padx=5)
        
        self.speed_slider = tk.Scale(slider_frame, from_=0, to=10000, orient="horizontal", 
                                     command=self.update_speed_display, length=250, bg="lightblue")
        self.speed_slider.set(0)
        self.speed_slider.pack(side="left", padx=5, fill="x", expand=True)
        
        # Quick speed buttons
        quick_button_frame = tk.Frame(speed_frame, bg="lightblue")
        quick_button_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(quick_button_frame, text="Quick Set:", bg="lightblue", font=("Arial", 10)).pack(side="left", padx=5)
        
        quick_speeds = [0, 1000, 2500, 5000, 7500, 10000]
        for speed in quick_speeds:
            tk.Button(quick_button_frame, text=f"{speed}", 
                     command=lambda s=speed: self.set_quick_speed(s),
                     width=6, font=("Arial", 9)).pack(side="left", padx=2)
        
        # Action buttons
        action_frame = tk.Frame(speed_frame, bg="lightblue")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(action_frame, text="✓ Apply Speed to Train Model", 
                 command=self.apply_speed_to_train,
                 bg="green", fg="white", font=("Arial", 10, "bold"),
                 width=25).pack(side="left", padx=5)
        
        tk.Button(action_frame, text="■ Emergency Stop", 
                 command=self.emergency_stop,
                 bg="darkred", fg="white", font=("Arial", 10, "bold"),
                 width=15).pack(side="left", padx=5)

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


    def signal_color(self, bits):
        mapping = {
            (0, 0): "Red",
            (0, 1): "Yellow",
            (1, 0): "Green",
            (1, 1): "Super Green"
        }
        return mapping.get(tuple(bits), "Unknown")

    def refresh_diagram_table(self):
        # Remember which block (if any) is currently selected
        selected = self.diagram_tree.selection()
        selected_block_num = None
        if selected:
            item = self.diagram_tree.item(selected[0])
            if item["values"]:
                selected_block_num = item["values"][0]
        
        # Get infrastructure sets from main UI (dynamically loaded from Excel)
        switch_blocks = getattr(self.master, 'switch_blocks', set())
        crossing_blocks = getattr(self.master, 'crossing_blocks', set())
        signal_blocks = getattr(self.master, 'light_states', set())
        
        # Clear and repopulate the table
        self.diagram_tree.delete(*self.diagram_tree.get_children())
        for block in self.manager.blocks:
            # Switch: show value only if block has a switch, otherwise "--"
            if block.block_number in switch_blocks:
                switch_val = getattr(block, "switch_state", False)
            else:
                switch_val = "--"
            
            # Crossing: show value only if block has a crossing, otherwise "--"
            if block.block_number in crossing_blocks:
                cross_val = getattr(block, "crossing", False)
            else:
                cross_val = "--"
            
            # Signal: show value only if block has a signal, otherwise "--"
            if block.block_number in signal_blocks:
                if hasattr(block, "signal") and isinstance(block.signal, list):
                    sig_val = self.signal_color(block.signal)
                else:
                    sig_val = "Unknown"
            else:
                sig_val = "--"
            
            occ_val = getattr(block, "occupancy", "")

            self.diagram_tree.insert(
                "", "end",
                values=(block.block_number, switch_val, cross_val, sig_val, occ_val)
            )
        
        # Reselect the previously selected block if it still exists
        if selected_block_num is not None:
            for item_id in self.diagram_tree.get_children():
                if self.diagram_tree.item(item_id)["values"][0] == selected_block_num:
                    self.diagram_tree.selection_set(item_id)
                    self.diagram_tree.focus(item_id)
                    break

    # Remaining methods from original Test_UI.py...
    # (Bidirectional controls, edit_selected_diagram, refresh_ui, etc.)
    
    def refresh_bidirectional_controls(self):
        """Refresh the bidirectional direction status displays"""
        if not hasattr(self, 'bidirectional_status_labels'):
            return
            
        if hasattr(self.manager, 'bidirectional_directions'):
            for group_name, label in self.bidirectional_status_labels.items():
                direction = self.manager.bidirectional_directions.get(group_name, 0)
                direction_text = 'Right →' if direction == 1 else '← Left'
                label.config(text=direction_text)

    def update_bidirectional_status(self, group_name):
        """Update status label for a specific bidirectional group"""
        if hasattr(self, 'bidirectional_status_labels') and group_name in self.bidirectional_status_labels:
            direction = self.manager.bidirectional_directions.get(group_name, 0)
            direction_text = 'Right →' if direction == 1 else '← Left'
            self.bidirectional_status_labels[group_name].config(text=direction_text)

    def toggle_bidirectional_direction(self, group_name):
        """Toggle direction for a bidirectional section"""
        if not hasattr(self.master, 'data_manager'):
            print("Warning: Cannot access main UI data manager")
            return
            
        main_manager = self.master.data_manager
        
        if not hasattr(main_manager, 'bidirectional_directions'):
            print("Warning: Main manager missing bidirectional_directions")
            return
            
        if group_name in main_manager.bidirectional_directions:
            current_direction = main_manager.bidirectional_directions[group_name]
            new_direction = 1 if current_direction == 0 else 0
            
            print(f"📝 Test UI changing {group_name} from {current_direction} to {new_direction}")
            
            # Update the shared data manager directly (Test UI controls this)
            main_manager.bidirectional_directions[group_name] = new_direction
            
            # Also update our local reference to stay in sync
            self.manager.bidirectional_directions[group_name] = new_direction
            
            # Update the status display immediately in Test UI
            self.update_bidirectional_status(group_name)
            
            # Force refresh Main UI controls
            if hasattr(self.master, 'refresh_bidirectional_controls'):
                self.master.refresh_bidirectional_controls()
                print("🔄 Main UI refresh triggered from Test UI")
            
            print(f"✅ {group_name} direction changed by Test UI: {'Right →' if new_direction == 1 else '← Left'}")

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

        # Get infrastructure sets from main UI (dynamically loaded from Excel)
        switch_blocks = getattr(self.master, 'switch_blocks', set())
        crossing_blocks = getattr(self.master, 'crossing_blocks', set())
        signal_blocks = getattr(self.master, 'light_states', set())

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
                    old_val = getattr(block, attr, None)
                    
                    if attr in ["switch_state", "crossing"]:
                        val = val.lower() in ["true", "1", "yes"]
                    else:
                        val = int(val)
                    setattr(block, attr, val)
                    
                    # Notify main UI if switch_state changed on a beacon block
                    if attr == "switch_state" and block.block_number in [27, 38]:
                        print(f"\n{'='*60}")
                        print(f"[TEST UI DEBUG] Switch state changed on beacon block {block.block_number}")
                        print(f"[TEST UI DEBUG] Old value: {old_val}")
                        print(f"[TEST UI DEBUG] New value: {val}")
                        print(f"[TEST UI DEBUG] Block occupancy: {block.occupancy}")
                        if hasattr(self.master, 'notify_switch_change_from_test_ui'):
                            print(f"[TEST UI DEBUG] Calling master.notify_switch_change_from_test_ui({block.block_number})")
                            self.master.notify_switch_change_from_test_ui(block.block_number)
                            print(f"🔔 Notified main UI of switch change on block {block.block_number}")
                        else:
                            print(f"[TEST UI DEBUG] ❌ master.notify_switch_change_from_test_ui NOT FOUND!")
                        print(f"{'='*60}\n")

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

    # ---------------- Speed Toggler Methods ----------------
    def update_train_selector(self):
        """Update the train selector dropdown with current active trains"""
        if hasattr(self, 'train_selector'):
            self.train_selector['values'] = self.manager.active_trains if self.manager.active_trains else ['No trains']
            if self.manager.active_trains and not self.selected_train_var.get():
                self.selected_train_var.set(self.manager.active_trains[0])
            elif not self.manager.active_trains:
                self.selected_train_var.set('No trains')
    
    def get_selected_train(self):
        """Get the currently selected train ID and index"""
        selected = self.selected_train_var.get()
        if not selected or selected == 'No trains' or selected not in self.manager.active_trains:
            return None, None
        train_id = selected
        train_idx = self.manager.active_trains.index(train_id)
        return train_id, train_idx
    
    def update_speed_display(self, value):
        """Update the speed display when slider moves"""
        speed = int(float(value))
        self.current_speed_var.set(str(speed))
    
    def set_quick_speed(self, speed):
        """Set speed to a preset value"""
        self.speed_slider.set(speed)
        self.current_speed_var.set(str(speed))
        self.status_label.config(text=f"Speed set to {speed} m/s", fg="blue")
    
    def apply_speed_to_train(self):
        """Apply the current speed setting by directly updating Track Model's train_actual_speeds"""
        speed_ms = int(float(self.speed_slider.get()))  # Speed in m/s
        
        # Get selected train
        train_id, train_idx = self.get_selected_train()
        if train_id is None:
            self.status_label.config(text="❌ No train selected or no active trains", fg="red")
            messagebox.showwarning("No Train Selected", "Please deploy a train first using the 'Deploy Train' button, then select it from the dropdown.")
            return
        
        print(f"\n{'='*60}")
        print(f"[TEST UI SPEED CONTROL] Setting speed for train {train_id}")
        print(f"{'='*60}")
        
        # DIRECT VARIABLE ACCESS: Update train_actual_speeds directly in Track Model
        if hasattr(self.master, 'train_actual_speeds'):
            self.master.train_actual_speeds[train_id] = speed_ms
            print(f"✓ DIRECT UPDATE: train_actual_speeds['{train_id}'] = {speed_ms} m/s")
            success = True
        else:
            print(f"✗ ERROR: master.train_actual_speeds not found!")
            self.status_label.config(text="❌ Track Model not accessible", fg="red")
            return
        
        # Update commanded speed in data manager
        if train_idx < len(self.manager.commanded_speed):
            self.manager.commanded_speed[train_idx] = speed_ms
            print(f"✓ Updated commanded_speed[{train_idx}] = {speed_ms} m/s")
        
        # Initialize movement tracking if needed
        if hasattr(self.master, 'train_positions_in_block'):
            if train_id not in self.master.train_positions_in_block:
                self.master.train_positions_in_block[train_id] = 0
                print(f"✓ Initialized train_positions_in_block['{train_id}'] = 0")
        
        if hasattr(self.master, 'last_movement_update'):
            import time
            if train_id not in self.master.last_movement_update:
                self.master.last_movement_update[train_id] = time.time()
                print(f"✓ Initialized last_movement_update['{train_id}']")
        
        if success:
            self.status_label.config(text=f"✅ Speed {speed_ms} m/s applied to Train {train_id}", fg="green")
            print(f"✓ Train {train_id} will now move at {speed_ms} m/s")
            print(f"  Track Model's update_train_movements() will handle movement")
        
        print(f"{'='*60}\n")
        
        # Refresh tables to show updated commanded speed
        self.refresh_train_table()

    
    def emergency_stop(self):
        """Emergency stop - set speed to 0 immediately by directly updating Track Model variable"""
        self.speed_slider.set(0)
        self.current_speed_var.set("0")
        
        # Get selected train
        train_id, train_idx = self.get_selected_train()
        if train_id is None:
            self.status_label.config(text="❌ No train selected", fg="red")
            return
        
        print(f"\n{'='*60}")
        print(f"[EMERGENCY STOP] Stopping train {train_id}")
        print(f"{'='*60}")
        
        # DIRECT VARIABLE ACCESS: Set train_actual_speeds to 0
        if hasattr(self.master, 'train_actual_speeds'):
            self.master.train_actual_speeds[train_id] = 0
            print(f"⚠️ DIRECT UPDATE: train_actual_speeds['{train_id}'] = 0 m/s")
            success = True
        else:
            print(f"✗ ERROR: master.train_actual_speeds not found!")
            self.status_label.config(text="❌ Track Model not accessible", fg="red")
            return
        
        # Update commanded speed
        if train_idx < len(self.manager.commanded_speed):
            self.manager.commanded_speed[train_idx] = 0
            print(f"✓ Updated commanded_speed[{train_idx}] = 0 m/s")
        
        if success:
            self.status_label.config(text=f"⚠️ EMERGENCY STOP - Train {train_id} stopped", fg="red")
            print(f"⚠️ Train {train_id} STOPPED - speed set to 0 m/s")
        
        print(f"{'='*60}\n")
        
        # Refresh to show updated speed
        self.refresh_train_table()



    def refresh_ui(self):
        """Periodic refresh - similar to main UI refresh pattern"""
        self.sync_with_main_ui()  # Sync data first
        
        # Refresh all tables and controls
        self.refresh_block_table()
        self.refresh_station_table() 
        self.refresh_train_table()
        self.refresh_diagram_table()
        self.refresh_bidirectional_controls()  # Use the new method
        self.update_train_selector()  # Update train selector dropdown
        
        # Continue periodic refresh
        self.after(1000, self.refresh_ui)

    def sync_with_main_ui(self):
        """Ensure Test UI data is synchronized with Main UI"""
        if hasattr(self.master, 'data_manager'):
            main_manager = self.master.data_manager
            
            # Sync bidirectional directions (Test UI is now controller)
            if hasattr(main_manager, 'bidirectional_directions'):
                if not hasattr(self.manager, 'bidirectional_directions'):
                    self.manager.bidirectional_directions = {}
                # Update our data with main UI data
                self.manager.bidirectional_directions.update(main_manager.bidirectional_directions)