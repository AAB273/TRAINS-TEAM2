import subprocess
import time
import sys
import os

def launch_four_guis():
    # Define paths for all four GUIs
    PASSENGER_UI_PATH = "Wayside_Controller/SW/main.py"
    CTC_UI_PATH = "CTC_Office/CTC_UI.py"
    WAYSIDE_HW_UI_PATH = "Wayside_Controller/HW/WC_HW_MainUI.py"
    TRACK_MODEL_UI_PATH = "Track Model/UI_Structure.py"  # New Track Model UI
    
    # List of all GUI paths to verify
    gui_paths = [
        ("Passenger UI", PASSENGER_UI_PATH),
        ("CTC Office UI", CTC_UI_PATH),
        ("Wayside HW UI", WAYSIDE_HW_UI_PATH),
        ("Track Model UI", TRACK_MODEL_UI_PATH)  # Added fourth GUI
    ]
    
    # Verify all files exist
    print("🔍 Verifying GUI files...")
    for name, path in gui_paths:
        if not os.path.exists(path):
            print(f"❌ {name} not found at: {path}")
            return
        print(f"✅ Found {name}: {path}")
    
    print()
    
    # Initialize process variables
    processes = [None] * 4
    
    try:
        # Launch Passenger GUI first
        print("🚆 Launching Passenger GUI...")
        processes[0] = subprocess.Popen([sys.executable, PASSENGER_UI_PATH])
        
        print("⏳ Waiting for Passenger GUI socket server to start...")
        time.sleep(1.5)  # Small delay for initialization
        
        # Launch CTC Office UI
        print("🏢 Launching CTC Office UI...")
        processes[1] = subprocess.Popen([sys.executable, CTC_UI_PATH])
        
        # Launch Wayside HW UI
        print("🛠️ Launching Wayside HW UI...")
        processes[2] = subprocess.Popen([sys.executable, WAYSIDE_HW_UI_PATH])
        
        #Launch Track Model UI
        print("🛤️ Launching Track Model UI...")
        # Launch Track Model UI
        # print("🛤️ Launching Track Model UI...")
        processes[3] = subprocess.Popen([sys.executable, TRACK_MODEL_UI_PATH])
        
        print("\n✅ All 4 GUIs launched successfully!")
        print("📋 Running Applications:")
        print("   1. Passenger UI")
        print("   2. CTC Office UI")
        print("   3. Wayside Hardware UI")
        print("   4. Track Model UI")
        print("\n💡 Close this window or press Ctrl+C to terminate all applications.\n")
        
        # Wait for all processes to complete
        for process in processes:
            if process is not None:
                process.wait()
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all GUIs...")
        for process in processes:
            if process is not None:
                try:
                    process.terminate()
                except:
                    pass
        print("✅ All GUIs terminated.")
    except Exception as e:
        print(f"❌ Error: {e}")
        # Clean up any running processes
        for process in processes:
            if process is not None:
                try:
                    process.terminate()
                except:
                    pass

if __name__ == "__main__":
    launch_four_guis()