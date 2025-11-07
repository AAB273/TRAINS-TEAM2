# launch_both.py - FIXED VERSION
import subprocess
import time
import os
import sys

def launch_uis():
    print("Starting both UIs with socket communication...")
    
    # Get the current directory of the launcher
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Start Main UI
    main_ui_process = subprocess.Popen([sys.executable, 'main.py'], cwd=current_dir)
    
    # Wait for Main UI to start its server
    time.sleep(3)
    
    # Start Test UI  
    test_ui_process = subprocess.Popen([sys.executable, 'Wayside_Test_UI.py'], cwd=current_dir)
    
    print("Both UIs started - they will automatically connect via sockets")
    
    try:
        # Wait for both processes
        main_ui_process.wait()
        test_ui_process.wait()
    except KeyboardInterrupt:
        print("Stopping both UIs...")
        main_ui_process.terminate()
        test_ui_process.terminate()

if __name__ == "__main__":
    launch_uis()