import subprocess
import sys
import os
import time
import platform
from pathlib import Path

if os.environ.get('TRAINS_LAUNCHER_RUNNING') == '1':
    print("ERROR: Recursive launch detected!")
    sys.exit(1)

def launch_all():
    # Get the directory where this script is running from
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # When running from PyInstaller exe, go up one level to get to the actual bundle root
    if os.path.basename(exe_dir) == '_internal':
        exe_dir = os.path.dirname(exe_dir)
    
    # Add lib folder to Python path so it finds bundled libraries
    lib_dir = os.path.join(exe_dir, 'lib')
    if os.path.exists(lib_dir):
        sys.path.insert(0, lib_dir)
        print(f"✓ Added lib folder to path: {lib_dir}")
    else:
        print(f"✗ WARNING: lib folder not found at: {lib_dir}")
    
    print("\n" + "="*60)
    print("TRAINS TEAM 2 - UNIFIED CONTROL SYSTEM")
    print(f"Running from: {exe_dir}")
    print(f"Operating System: {platform.system()}")
    print("="*60 + "\n")
    
    modules = [
        ("CTC", "CTC_Office/CTC_UI.py"),
        ("Track SW", "Wayside_Controller/SW/main.py"),
        ("Track Model", "Track Model/UI_Structure.py"),
        ("Train Model", "Train Model/Passenger_UI.py"),
        ("Train SW", "train_controller_sw/Driver_UI.py"),
    ]
    
    processes = []
    
    # Set environment for subprocesses
    env = os.environ.copy()
    env['PYTHONPATH'] = exe_dir + os.pathsep + env.get('PYTHONPATH', '')
    
    print("Starting modules...\n")
    for module_name, module_file in modules:
        file_path = os.path.join(exe_dir, module_file)
        
        print(f"  Checking for {module_name} at: {file_path}")
        if os.path.exists(file_path):
            print(f"  > Launching {module_name}")
            try:
                # Platform-specific process startup (Windows only)
                startupinfo = None
                if platform.system() == 'Windows':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    [sys.executable, file_path],
                    cwd=exe_dir,
                    env=env,
                    startupinfo=startupinfo
                )
                processes.append((module_name, process))
                print(f"    SUCCESS: {module_name} started")
                time.sleep(2)
            except Exception as e:
                print(f"  ! Failed to launch {module_name}: {e}")
        else:
            print(f"  ! File not found: {file_path}")
    
    time.sleep(3)
    
    print("\n" + "="*60)
    print(f"SUCCESS: {len(processes)} modules launched!")
    print("Press Ctrl+C to stop all modules...")
    print("="*60 + "\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down modules...")
        for name, process in processes:
            try:
                print(f"  Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"    {name} stopped")
            except subprocess.TimeoutExpired:
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