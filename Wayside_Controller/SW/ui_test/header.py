import tkinter as tk
from tkinter import ttk

class Header:
    def __init__(self, root, track_config):
        self.root = root
        self.track_config = track_config
        
        self.header_frame = tk.Frame(root, bg="#1a1a4d")
        self.header_frame.pack(fill='x', pady=8)

        self.create_header()
    
    def create_header(self):
        # Logo
        try:
            logo_img = tk.PhotoImage(file="blt logo.png")
            logo_img_small = logo_img.subsample(12, 12)
            logo_label = tk.Label(self.header_frame, image=logo_img_small, bg='#1a1a4d')  # Fixed: use self.header_frame
            logo_label.image = logo_img_small  # Keep a reference
            logo_label.pack(side='left', padx=15)
        except:
            print("not working making image")
            
            
        # Testing Interface title - CENTERED
        title_frame = tk.Frame(self.header_frame, bg="#1a1a4d")
        title_frame.pack(side='left', expand=True, fill='x')  # Expand to fill available space
        
        UIheader = tk.Label(title_frame, text="Testing Interface", font=("Arial", 28), 
                        fg='white', bg="#4f4f4f", highlightbackground='white', highlightthickness=2,
                        padx=15, pady=8)
        UIheader.pack(expand=True)  # This centers the label within the frame
        