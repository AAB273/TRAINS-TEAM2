import tkinter as tk
from tkinter import messagebox
from ui.plc_dialog import PLCDialog

class Header(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, bg='#1a1a4d', height=80)
        self.pack_propagate(False)
        self.data = data
        
        self.create_widgets()
    
    def create_widgets(self):
        # Logo
        logo_img = tk.PhotoImage(file="/mnt/c/Users/Home/classes/Fall 2025/Trains/UI Images/blt logo.png")
        logo_img_small = logo_img.subsample(12, 12)
        logo_label = tk.Label(self, image=logo_img_small, bg='#4a7c8c')
        logo_label.image = logo_img_small
        logo_label.pack(side=tk.LEFT, padx=5)

        # CENTRALIZED LINE TABS - These control the entire UI
        self.create_line_tabs()

        # Fault LED
        fault_led = tk.Label(self, text="Fault LED", bg='#cc3333', 
                            fg='white', width=10, height=3, font=('Arial', 10, 'bold'))
        fault_led.pack(side=tk.LEFT, padx=5)
        
        # PLC Upload button and dialog
        self.plc_dialog = PLCDialog(self)
        
        plc_frame = tk.Frame(self, bg='white', relief=tk.RAISED, borderwidth=2)
        plc_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(plc_frame, text="PLC Program Upload", bg='white', 
                font=('Arial', 10, 'bold')).pack(pady=2)
        tk.Button(plc_frame, text="Select PLC File", bg='white', 
                 command=self.plc_dialog.show).pack(pady=2, padx=10)
        
        # Run PLC button
        tk.Button(self, text="Run PLC", bg='white', width=12, 
                 height=2, font=('Arial', 10, 'bold'),
                 command=self.run_plc).pack(side=tk.LEFT, padx=10)
        
        # Right side indicators with toggles
        self.create_mode_controls()
    
    def create_mode_controls(self):
        right_frame = tk.Frame(self, bg='#1a1a4d')
        right_frame.pack(side=tk.RIGHT, padx=10)
        
        # MM LED with toggle
        mm_frame = tk.Frame(right_frame, bg='#1a1a4d')
        mm_frame.pack(side=tk.LEFT, padx=5)
        self.mm_led = tk.Label(mm_frame, text="MM LED", bg='#666666', fg='white',
                width=8, height=2, font=('Arial', 10, 'bold'))
        self.mm_led.pack()
        self.mm_toggle = tk.Checkbutton(mm_frame, bg='#1a1a4d', activebackground='#1a1a4d',
                                       command=self.toggle_maintenance)
        self.mm_toggle.pack()
        
        # TEST with toggle
        test_frame = tk.Frame(right_frame, bg='#1a1a4d')
        test_frame.pack(side=tk.LEFT, padx=5)
        self.test_led = tk.Label(test_frame, text="TEST", bg='#666666', fg='white',
                width=8, height=2, font=('Arial', 10, 'bold'))
        self.test_led.pack()
        self.test_toggle = tk.Checkbutton(test_frame, bg='#1a1a4d', activebackground='#1a1a4d',
                                         command=self.toggle_test)
        self.test_toggle.pack()
    
    def toggle_maintenance(self):
        new_mode = not self.data.maintenance_mode
        self.data.set_maintenance_mode(new_mode)
        if new_mode:
            self.mm_led.config(bg='#ffaa33')
        else:
            self.mm_led.config(bg='#666666')
    
    def toggle_test(self):
        new_mode = not self.data.test_mode
        self.data.set_test_mode(new_mode)
        if new_mode:
            self.test_led.config(bg='white', fg='black')
        else:
            self.test_led.config(bg='#666666', fg='white')
    
    def run_plc(self):
        print("Running PLC...")
        messagebox.showinfo("PLC Status", "PLC is now running!")

    def create_line_tabs(self):
        """Create centralized line tabs that sync across the UI"""
        tab_frame = tk.Frame(self, bg='#1a1a4d')
        tab_frame.pack(side=tk.LEFT, padx=20)
        
        # Create tab buttons with commands - FIXED: using set_current_line instead of set_line
        self.blue_tab = tk.Button(tab_frame, text="Blue", bg='#6666ff', width=8,
                                 command=lambda: self.data.set_current_line("Blue"))
        self.blue_tab.pack(side=tk.LEFT)
        
        self.green_tab = tk.Button(tab_frame, text="Green", bg='#66cc66', width=8,
                                  command=lambda: self.data.set_current_line("Green"))
        self.green_tab.pack(side=tk.LEFT)
        
        self.red_tab = tk.Button(tab_frame, text="Red", bg='#ff6666', width=8,
                                command=lambda: self.data.set_current_line("Red"))
        self.red_tab.pack(side=tk.LEFT)
        
        # Set initial active tab
        self.update_tab_appearance()
        
        # Connect callback for when line changes
        self.data.on_line_change.append(self.update_tab_appearance)

    def set_line(self, line):
        """Set the current line and update all UI components"""
        print(f"Setting line to: {line}")
        self.data.set_current_line(line)
        self.data.filter_data_by_line(line)
    
    def update_tab_appearance(self):
        """Update tab colors to show active line"""
        active_bg = {'Blue': '#3366ff', 'Green': '#33aa33', 'Red': '#ff3333'}
        inactive_bg = {'Blue': "#a8a8ee", 'Green': "#aadaaa", 'Red': "#eb9595"}
        
        current = self.data.current_line
        print(f"Updating tab appearance for: {current}")
        
        self.blue_tab.config(bg=active_bg['Blue'] if current == "Blue" else inactive_bg['Blue'])
        self.green_tab.config(bg=active_bg['Green'] if current == "Green" else inactive_bg['Green'])
        self.red_tab.config(bg=active_bg['Red'] if current == "Red" else inactive_bg['Red'])