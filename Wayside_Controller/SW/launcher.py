import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class UILauncher:
    def __init__(self):
        self.main_ui = None
        self.test_ui = None
        self.communicator = None
        
    def run_main_ui_only(self):
        """Run only the main UI"""
        try:
            from main import RailwayControlSystem
            root = tk.Tk()
            self.main_ui = RailwayControlSystem(root)
            root.title("Wayside Controller - Main System")
            print("Main UI started successfully")
            root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Main UI: {e}")
    
    
    def run_both_sequential(self):
        """Run UIs in same thread"""
        try:
            from main import RailwayControlSystem
            from Wayside_Test_UI import RailwayControlSystem as TestUI
            from ui_communicator import UICommunicator
            
            print("Starting both UIs...")
            
            # Create main UI
            main_root = tk.Tk()
            self.main_ui = RailwayControlSystem(main_root)
            main_root.title("Wayside Controller - Main System")
            
            # Create test UI as Toplevel window
            test_root = tk.Toplevel(main_root)
            self.test_ui = TestUI(test_root)
            test_root.title("Wayside Controller - Test Interface")
            
            # Connect them
            self.communicator = UICommunicator(self.main_ui, self.test_ui)
            
            print("Both UIs started with communication enabled")
            
            # Start main loop (both windows will run)
            main_root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start connected UIs: {e}")
            import traceback
            traceback.print_exc()
    
    def create_launcher_ui(self):
        """Create launcher interface"""
        launcher_root = tk.Tk()
        launcher_root.title("Wayside Controller Launcher")
        launcher_root.geometry("450x350")
        launcher_root.configure(bg='#1a1a4d')
        
        # Header
        header = tk.Frame(launcher_root, bg='#1a1a4d')
        header.pack(fill='x', pady=20)
        
        tk.Label(header, text="Wayside Controller", 
                font=("Arial", 20, "bold"), 
                bg='#1a1a4d', fg='white').pack()
        
        tk.Label(header, text="Select Launch Option", 
                font=("Arial", 12), 
                bg='#1a1a4d', fg='white').pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(launcher_root, bg='#1a1a4d')
        button_frame.pack(pady=20)
        
        # Launch buttons
        tk.Button(button_frame, text="Main UI Only", 
                 command=lambda: [launcher_root.destroy(), self.run_main_ui_only()],
                 width=25, height=2, bg='#4CAF50', fg='white', font=("Arial", 11)).pack(pady=8)
        
        tk.Button(button_frame, text="Both UIs (Connected)", 
                 command=lambda: [launcher_root.destroy(), self.run_both_sequential()],
                 width=25, height=2, bg='#FF9800', fg='white', font=("Arial", 11)).pack(pady=8)
        
        # Info
        info_frame = tk.Frame(launcher_root, bg='#1a1a4d')
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(info_frame, text="Connected mode: Test UI controls Main UI data", 
                font=("Arial", 9), bg='#1a1a4d', fg='#cccccc').pack()

        launcher_root.mainloop()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        launcher = UILauncher()
        option = sys.argv[1].lower()
        if option == "main":
            launcher.run_main_ui_only()
        elif option == "both":
            launcher.run_both_sequential() 
        else:
            print("Usage: python launcher.py [main|test|both]")
            print("No arguments will show the launcher UI")
            launcher.create_launcher_ui()
    else:
        launcher = UILauncher()
        launcher.create_launcher_ui()

if __name__ == "__main__":
    main()