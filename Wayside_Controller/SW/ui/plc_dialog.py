import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os

class PLCDialog:
    def __init__(self, parent):
        self.parent = parent
        
        # Create PLC upload frame (initially hidden)
        self.frame = tk.Frame(parent.winfo_toplevel(), bg='white', relief='raised', bd=3)
        self.create_widgets()
        
    def create_widgets(self):
        # Title with icon
        title = tk.Label(self.frame, text="PLC Program Upload", 
                                   font=("Arial", 18, "bold"), bg='white', fg='#1a1a4d')
        title.pack(pady=15)
        
        # Instructions
        instructions = tk.Label(self.frame, 
                               text="Upload your PLC program file (.plc, .txt, .csv)", 
                               font=("Arial", 10), bg='white', fg='gray', wraplength=350)
        instructions.pack(pady=5)
        
        # Upload button
        upload_button = ttk.Button(self.frame, text="Choose File", 
                                     command=self.PLCupload_file, width=20)  # FIXED THIS LINE
        upload_button.pack(pady=10)
        
        # File status display
        self.file_status = tk.Label(self.frame, text="No file selected", 
                                   font=("Arial", 10), bg='white', fg='gray', 
                                   wraplength=350, justify='center')
        self.file_status.pack(pady=5)
        
        # Confirm upload button (initially disabled)
        self.upload_confirm_button = ttk.Button(self.frame, 
                                               text="Upload to Controller", 
                                               command=self.confirm_upload, 
                                               state='disabled', width=20)
        self.upload_confirm_button.pack(pady=10)
        
        # Add some visual separation
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=5)
        
        # Upload history label
        self.history_label = tk.Label(self.frame, text="Last upload: Never", 
                                     font=("Arial", 9), bg='white', fg='darkgray')
        self.history_label.pack(pady=5)
        
        # Close button
        close_button = ttk.Button(self.frame, text="Close", 
                                 command=self.hide, width=20)
        close_button.pack(pady=10)
    
    def PLCupload_file(self): 
        """Select any PLC Python file and store its path for the controller"""
        file_types = [("PLC Program", "*.py"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(
            title="Select PLC Program File",
            filetypes=file_types
        )

        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # KB

            # Display file info
            self.file_status.config(
                text=f"{file_name}\n({file_size:.1f} KB)",
                fg="green",
                font=("Arial", 10, "bold")
            )

            self.upload_confirm_button.config(state="normal")
            self.file_path = file_path

            # ✅ make sure the parent panel (LeftPanel) remembers this path
            self.parent.selected_plc_file = file_path
            print(f"✅ PLC file selected: {file_path}")
        else:
            self.file_status.config(text="No file selected", fg="gray")
    
    def confirm_upload(self):
        if hasattr(self, 'file_path'):
            # Simulate upload process
            self.file_status.config(text="Uploading...", fg="blue")
            self.parent.after(2000, self.upload_complete)  # Simulate 2 second upload
        else:
            messagebox.showwarning("No File", "Please select a file first!")
    
    def upload_complete(self):
        self.file_status.config(text="✓ Upload Complete!", fg="green")
        self.upload_confirm_button.config(state='disabled')
        messagebox.showinfo("Success", "PLC program uploaded successfully!")
        
        # Update history
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_label.config(text=f"Last upload: {now}")
        
        # Reset after 3 seconds
        self.parent.after(3000, self.reset_upload)
    
    def reset_upload(self):
        self.file_status.config(text="No file selected", fg="gray", font=("Arial", 10))
        self.upload_confirm_button.config(state='disabled')
        if hasattr(self, 'file_path'):
            del self.file_path
    
    def show(self):
        self.frame.place(x=50, y=50, width=400, height=350)
        self.frame.lift()
        
    def hide(self):
        self.frame.place_forget()