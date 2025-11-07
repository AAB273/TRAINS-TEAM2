import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SystemLog:
    def __init__(self, parent, main_app=None):
        self.parent = parent
        self.main_app = main_app
        self.log_callback = None  # For external callbacks
        
        self.create_log_card()

    def set_log_callback(self, callback):
        """Set the callback function for external logging"""
        self.log_callback = callback

    def create_log_card(self):
        # System Log Card - Now uses the full space since PLC section is removed
        log_card = tk.Frame(self.parent, bg="white", relief='raised', bd=2, padx=12, pady=12)
        log_card.pack(side='left', fill='both', expand=True, padx=3)
        
        tk.Label(log_card, text="System Log", font=("Arial", 14, "bold"), 
                bg="white", fg="#2d2d86").pack(anchor='w', pady=(0, 12))
        
        # Search functionality
        search_frame = tk.Frame(log_card, bg="white")
        search_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(search_frame, text="Search:", font=("Arial", 11, "bold"), bg="white").pack(side='left')
        self.search_entry = tk.Entry(search_frame, width=18, font=("Arial", 10))
        self.search_entry.pack(side='left', padx=8)
        
        ttk.Button(search_frame, text="Search", command=self.search_log, width=8).pack(side='left', padx=3)
        ttk.Button(search_frame, text="Clear", command=self.clear_search, width=8).pack(side='left', padx=3)
        
        # Log display - Now larger since PLC section is removed
        log_display_frame = tk.Frame(log_card, bg="white")
        log_display_frame.pack(fill='both', expand=True, pady=8)
        
        # Create log text widget with scrollbar - Larger now
        self.log_text = tk.Text(log_display_frame, height=12, width=40, bg='#1a1a1a', fg='#00ff00', 
                              font=("Consolas", 9), selectbackground="#4d4dff")
        log_scrollbar = ttk.Scrollbar(log_display_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Add sample log entries
        self.initialize_log()
        
        # Clear Log button
        clear_frame = tk.Frame(log_card, bg="white")
        clear_frame.pack(fill='x', pady=8)
        
        ttk.Button(clear_frame, text="Clear Log", 
                  command=self.clear_log, width=12).pack()

    def initialize_log(self):
        """Initialize the log with sample entries"""
        log_entries = [
        ]
        
        self.log_text.config(state='normal')
        for entry in log_entries:
            self.log_text.insert('end', entry + '\n')
        self.log_text.config(state='disabled')
        self.log_text.see('end')

    def search_log(self):
        """Search for text in the log"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showinfo("Search", "Please enter a search term")
            return
        
        self.log_text.config(state='normal')
        
        # Remove previous highlights
        self.log_text.tag_remove("highlight", "1.0", "end")
        
        # Search through the log (case-insensitive)
        found_count = 0
        start_pos = "1.0"
        
        while True:
            start_pos = self.log_text.search(search_term, start_pos, stopindex="end", nocase=1)
            if not start_pos:
                break
                
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.log_text.tag_add("highlight", start_pos, end_pos)
            found_count += 1
            start_pos = end_pos
        
        # Configure highlight style
        self.log_text.tag_config("highlight", background="yellow", foreground="black")
        self.log_text.config(state='disabled')
        
        if found_count > 0:
            # Scroll to first occurrence
            self.log_text.see("1.0")
            messagebox.showinfo("Search Results", f"Found {found_count} occurrence(s) of '{search_term}'")
        else:
            messagebox.showinfo("Search Results", f"No results found for '{search_term}'")

    def clear_search(self):
        """Clear search highlights"""
        self.search_entry.delete(0, 'end')
        self.log_text.config(state='normal')
        self.log_text.tag_remove("highlight", "1.0", "end")
        self.log_text.config(state='disabled')

    def clear_log(self):
        """Clear the entire log"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')
        
        # Add a new initial entry
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"{current_time} SYSTEM: Log cleared\n")
        self.log_text.config(state='disabled')
        
    def add_log_entry(self, message):
        """Add an entry to the log (called by other components)"""
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

        # Also call the external callback if set (for main app)
        if self.log_callback:
            self.log_callback(message)