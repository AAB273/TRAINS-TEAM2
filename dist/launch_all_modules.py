"""
This script launches ALL modules + control panel in ONE executable
Place this file in your TRAINS-TEAM2 root directory
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def launch_all():
    """Launch all modules and control panel"""
    
    print("\n" + "="*60)
    print("TRAINS TEAM 2 - UNIFIED CONTROL SYSTEM")
    print("="*60 + "\n")
    
    # List of modules to launch
    modules = [
        ("Train Model", "Passenger_UI.py"),
        ("Train SW", "Driver_UI.py"),
        ("Track SW", "main.py"),
        ("CTC", "CTC_UI.py"),
        ("Track Model", "UI_Structure.py"),
    ]
    
    processes = []
    
    # Launch each module
    print("Starting modules...\n")
    for module_name, module_file in modules:
        file_path = Path(module_file)
        
        if file_path.exists():
            print(f"  ▶ Launching {module_name}...")
            try:
                # Launch in subprocess (won't block)
                process = subprocess.Popen(
                    [sys.executable, str(file_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                processes.append(process)
                time.sleep(1)  # Small delay between launches
            except Exception as e:
                print(f"  ✗ Failed to launch {module_name}: {e}")
        else:
            print(f"  ✗ File not found: {module_file}")
    
    # Wait a moment for modules to start
    print("\n  Waiting for modules to initialize...")
    time.sleep(3)
    
    # Launch control panel
    control_panel_file = Path("client/main_control_panel.py")
    if control_panel_file.exists():
        print(f"  ▶ Launching Control Panel...")
        try:
            subprocess.Popen(
                [sys.executable, str(control_panel_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            print(f"  ✗ Failed to launch Control Panel: {e}")
    else:
        print(f"  ✗ Control panel not found: {control_panel_file}")
    
    print("\n" + "="*60)
    print("✓ All modules launched!")
    print("="*60 + "\n")
    
    # Keep the launcher running
    print("Press Ctrl+C to stop all modules...\n")
    try:
        # Wait indefinitely
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down modules...")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        print("✓ All modules stopped")


if __name__ == "__main__":
    launch_all()