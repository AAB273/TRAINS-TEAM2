import subprocess
import sys
import time
import os
from pathlib import Path

def launch_all():
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    print("\n" + "="*60)
    print("TRAINS TEAM 2 - UNIFIED CONTROL SYSTEM")
    print(f"Running from: {exe_dir}")
    print("="*60 + "\n")
    
    modules = [
        ("Train Model", "Train Model/Passenger_UI.py"),
        ("Train SW", "train_controller_sw/Driver_UI.py"),
        ("Track SW", "Wayside_Controller/SW/main.py"),
        ("CTC", "CTC_Office/CTC_UI.py"),
        ("Track Model", "Track_Model/UI_Structure.py"),
    ]
    
    processes = []
    
    print("Starting modules...\n")
    for module_name, module_file in modules:
        file_path = os.path.join(exe_dir, module_file)
        
        if os.path.exists(file_path):
            print(f"  > Launching {module_name} from {file_path}")
            try:
                process = subprocess.Popen(
                    [sys.executable, file_path],
                    cwd=exe_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_CONSOLE  # Open in new window
                )
                processes.append((module_name, process))
                print(f"    SUCCESS: {module_name} started (PID: {process.pid})")
                time.sleep(2)  # Increased delay between launches
            except Exception as e:
                print(f"  ! Failed to launch {module_name}: {e}")
        else:
            print(f"  ! File not found: {file_path}")
    
    time.sleep(3)
    
    control_panel_file = os.path.join(exe_dir, "client", "main_control_panel.py")
    if os.path.exists(control_panel_file):
        print(f"  > Launching Control Panel")
        try:
            process = subprocess.Popen(
                [sys.executable, control_panel_file],
                cwd=exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            processes.append(("Control Panel", process))
            print(f"    SUCCESS: Control Panel started (PID: {process.pid})")
        except Exception as e:
            print(f"  ! Failed to launch Control Panel: {e}")
    else:
        print(f"  ! Control panel not found: {control_panel_file}")
    
    print("\n" + "="*60)
    print(f"SUCCESS: {len(processes)} modules launched!")
    print("Press Ctrl+C to stop all modules...")
    print("="*60 + "\n")
    
    try:
        while True:
            time.sleep(1)
            # Check if any processes have crashed
            for name, process in processes:
                if process.poll() is not None:
                    print(f"WARNING: {name} has stopped (Exit code: {process.poll()})")
    except KeyboardInterrupt:
        print("\n\nShutting down modules...")
        for name, process in processes:
            try:
                print(f"  Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"    {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"    Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"    Error stopping {name}: {e}")
        print("SUCCESS: All modules stopped")


if __name__ == "__main__":
    try:
        launch_all()
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Press Enter to exit...")
        input()