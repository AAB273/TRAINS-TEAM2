import subprocess
import sys
import time
import os
import platform
from pathlib import Path

if os.environ.get('TRAINS_LAUNCHER_RUNNING') == '1':
    print("ERROR: Recursive launch detected!")
    sys.exit(1)

def launch_in_terminal(module_name, file_path, exe_dir, env):
    """Launch a subprocess in its own terminal window (Windows)."""
    try:
        # Windows: use start command with cmd.exe
        # Use absolute path for both Python executable and script
        abs_file_path = os.path.abspath(file_path)
        python_exe = sys.executable  # Use the same Python interpreter as the launcher
        
        command = f'start "TRAINS - {module_name}" cmd.exe /k "cd /d {exe_dir} && "{python_exe}" -u "{abs_file_path}" && pause"'
        
        subprocess.Popen(
            command,
            shell=True,
            env=env,
            cwd=exe_dir
        )
        return True
    except Exception as e:
        print(f"  ! Failed to launch {module_name}: {e}")
        return None

def launch_all():
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    print("\n" + "="*60)
    print("TRAINS TEAM 2 - UNIFIED CONTROL SYSTEM")
    print(f"Running from: {exe_dir}")
    print("="*60 + "\n")
    
    modules = [
        #("CTC", "CTC_Office/CTC_UI.py"),
        #("Track SW", "Wayside_Controller/SW/main.py"),
        #("Track Model", "Track Model/UI_Structure.py"),
        ("Train Model", "Train Model/Passenger_UI.py"),
        #("Train SW", "train_controller_sw/Driver_UI.py"),
        #("Train HW","HW_Train_Controller/TC_HW_MainUI.py"),
        
        ("Test UI","Train Model/Test_UI.py")
    ]
    
    # Set PYTHONPATH to include exe_dir so imports work
    env = os.environ.copy()
    env['PYTHONPATH'] = exe_dir + os.pathsep + env.get('PYTHONPATH', '')
    env['TRAINS_LAUNCHER_RUNNING'] = '1'
    
    print("Starting modules in separate terminals...\n")
    successful_launches = 0
    
    for module_name, module_file in modules:
        file_path = os.path.join(exe_dir, module_file)
        
        if os.path.exists(file_path):
            print(f"  > Launching {module_name}")
            if launch_in_terminal(module_name, file_path, exe_dir, env):
                print(f"    SUCCESS: {module_name} started in new terminal")
                successful_launches += 1
                time.sleep(1)
        else:
            print(f"  ! File not found: {file_path}")
    
    time.sleep(2)
    
    print("\n" + "="*60)
    print(f"SUCCESS: {successful_launches} modules launched in separate terminals!")
    print("All modules are running in their own terminal windows.")
    print("Close individual terminal windows to stop specific modules.")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        launch_all()
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Press Enter to exit...")
        input()