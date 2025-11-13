import subprocess
import sys
import os
import time
from pathlib import Path

def launch_railway_systems():
    """Launch both Railway Control System and Test Interface"""
    
    # Get the directory where THIS launcher script is located
    launcher_dir = Path(__file__).parent
    print(f"📂 Launcher directory: {launcher_dir}")
    
    print("🚂 Wayside Controller Systems Launcher")
    print("=" * 50)
    
    # Define the specific file paths - launcher is in SW folder, so files are in same directory
    main_ui_file = launcher_dir / "main.py"
    test_ui_file = launcher_dir / "Wayside_Test_UI.py"
    
    print(f"📁 Main UI: {main_ui_file}")
    print(f"📁 Test UI: {test_ui_file}")
    print("=" * 50)
    
    # Check if files exist
    if not main_ui_file.exists():
        print(f"❌ Main UI file not found: {main_ui_file}")
        print("Please make sure launcher.py is in the same folder as main.py and Wayside_Test_UI.py")
        return
    
    if not test_ui_file.exists():
        print(f"❌ Test UI file not found: {test_ui_file}")
        print("Please make sure launcher.py is in the same folder as main.py and Wayside_Test_UI.py")
        return
    
    try:
        # Launch Main Wayside Controller
        main_process = subprocess.Popen([sys.executable, str(main_ui_file)])
        print("Main Wayside Controller started")
        
        # Wait for main UI to initialize
        print("Waiting for main system to initialize...")
        time.sleep(3)
        
        # Launch Test Interface
        test_process = subprocess.Popen([sys.executable, str(test_ui_file)])
        print("Wayside Test Interface started")
        
        #print("\n🎯 Both systems are now running!")
        #print("   - Main Wayside Controller: Port 12342")
        #print("   - Wayside Test Interface: Port 22342")
        #print("\n⏹️  Press Ctrl+C in this window to stop both systems")
        
        # Keep the launcher running and handle shutdown
        try:
            # Wait for both processes
            main_process.wait()
            test_process.wait()
        except KeyboardInterrupt:
            print("\nStopping both systems...")
            main_process.terminate()
            test_process.terminate()
            print("✅ Both systems stopped gracefully")
            
    except FileNotFoundError:
        print("❌ Python executable not found. Make sure Python is installed and in your PATH.")
    except Exception as e:
        print(f"❌ Error launching systems: {e}")

if __name__ == "__main__":
    launch_railway_systems()