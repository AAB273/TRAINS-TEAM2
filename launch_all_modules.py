import subprocess
import sys
import os
import time
from pathlib import Path

# Add lib folder to Python path so it finds bundled libraries
exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
lib_dir = os.path.join(exe_dir, 'lib')
if os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)

if os.environ.get('TRAINS_LAUNCHER_RUNNING') == '1':
    print("ERROR: Recursive launch detected!")
    sys.exit(1)

def launch_all():
    print("\n" + "="*60)
    print("TRAINS TEAM 2 - UNIFIED CONTROL SYSTEM")
    print(f"Running from: {exe_dir}")
    print("="*60 + "\n")
    
    modules = [
        ("Train Model", "Train Model/Passenger_UI.py"),
        ("Train SW", "train_controller_sw/Driver_UI.py"),
    ]
    
    processes = []
    
    # Set environment for subprocesses
    env = os.environ.copy()
    env['PYTHONPATH'] = exe_dir + os.pathsep + env.get('PYTHONPATH', '')
    env['TRAINS_LAUNCHER_RUNNING'] = '1'
    
    print("Starting modules...\n")
    for module_name, module_file in modules:
        file_path = os.path.join(exe_dir, module_file)
        
        if os.path.exists(file_path):
            print(f"  > Launching {module_name}")
            try:
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