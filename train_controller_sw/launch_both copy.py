import subprocess
import sys
import os
import time
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # Go up one level from train_controller_sw

print(f"Project root: {PROJECT_ROOT}")
print(f"Script directory: {SCRIPT_DIR}")

def launch_all():
    """
    Launch all three modules: Driver UI, Passenger UI, and Test UI
    """
    print("\n" + "="*60)
    print("LAUNCHING ALL TRAIN MODULES")
    print("="*60)
    
    # Define module paths relative to project root
    modules = [
        {
            "name": "Passenger UI",
            "path": os.path.join(PROJECT_ROOT, "Train Model", "Passenger_UI.py"),
            "working_dir": os.path.join(PROJECT_ROOT, "Train Model")
        },
        {
            "name": "Driver UI", 
            "path": os.path.join(SCRIPT_DIR, "Driver_UI.py"),
            "working_dir": SCRIPT_DIR
        },
        {
            "name": "Test UI",
            "path": os.path.join(PROJECT_ROOT, "Train Model", "Test_UI.py"),
            "working_dir": os.path.join(PROJECT_ROOT, "Train Model")
        }
    ]
    
    processes = []
    
    print("\nStarting modules in sequence...")
    
    # Launch Passenger UI first (needs its server running)
    print("\n1. Launching Passenger UI...")
    passenger = modules[0]
    if os.path.exists(passenger["path"]):
        try:
            process = subprocess.Popen(
                [sys.executable, passenger["path"]],
                cwd=passenger["working_dir"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            processes.append((passenger["name"], process))
            print(f"   ✓ {passenger['name']} started")
            time.sleep(3)  # Give time for server to start
        except Exception as e:
            print(f"   ✗ Failed to start {passenger['name']}: {e}")
    else:
        print(f"   ✗ File not found: {passenger['path']}")
    
    # Launch Driver UI second
    print("\n2. Launching Driver UI...")
    driver = modules[1]
    if os.path.exists(driver["path"]):
        try:
            process = subprocess.Popen(
                [sys.executable, driver["path"]],
                cwd=driver["working_dir"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            processes.append((driver["name"], process))
            print(f"   ✓ {driver['name']} started")
            time.sleep(2)  # Give time to connect to Passenger UI
        except Exception as e:
            print(f"   ✗ Failed to start {driver['name']}: {e}")
    else:
        print(f"   ✗ File not found: {driver['path']}")
    
    # Launch Test UI last
    print("\n3. Launching Test UI...")
    test = modules[2]
    if os.path.exists(test["path"]):
        try:
            process = subprocess.Popen(
                [sys.executable, test["path"]],
                cwd=test["working_dir"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            processes.append((test["name"], process))
            print(f"   ✓ {test['name']} started")
        except Exception as e:
            print(f"   ✗ Failed to start {test['name']}: {e}")
    else:
        print(f"   ✗ File not found: {test['path']}")
    
    print("\n" + "="*60)
    print("SUCCESS: All 3 modules launched!")
    print("\nModules running:")
    for name, _ in processes:
        print(f"  • {name}")
    print("\nPress Ctrl+C in this window to stop all modules")
    print("="*60 + "\n")
    
    try:
        # Keep the launcher running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down all modules...")
        
        # Shutdown in reverse order
        for name, process in reversed(processes):
            print(f"  Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=3)
                print(f"    ✓ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"    ⚠ {name} force-killed")
            except Exception as e:
                print(f"    ✗ Error stopping {name}: {e}")
        
        print("\n✓ All modules stopped")
        time.sleep(1)

if __name__ == "__main__":
    try:
        launch_all()
    except Exception as e:
        print(f"\nERROR: {e}")
        input("\nPress Enter to exit...")