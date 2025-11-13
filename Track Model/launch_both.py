import subprocess
import time
import sys
import os

def launch_both_guis():
    # Replace these with your exact filepaths
    PASSENGER_UI_PATH = "CTC_Office/CTC_UI.py"
    TEST_UI_PATH = "Track Model/UI_Structure.py"
    
    # Verify files exist
    if not os.path.exists(PASSENGER_UI_PATH):
        print(f"❌ Passenger UI not found at: {PASSENGER_UI_PATH}")
        return
        
    if not os.path.exists(TEST_UI_PATH): 
        print(f"❌ Test UI not found at: {TEST_UI_PATH}")
        return
    
    print(f"✅ Found Passenger UI: {PASSENGER_UI_PATH}")
    print(f"✅ Found Test UI: {TEST_UI_PATH}")
    print()
    
    try:
        print("🚆 Launching Passenger GUI...")
        passenger_process = subprocess.Popen([sys.executable, PASSENGER_UI_PATH])
        
        # Wait for socket server to start
        print("⏳ Waiting for Passenger GUI socket server to start...")
     
        
        print("🧪 Launching Test UI...")
        test_process = subprocess.Popen([sys.executable, TEST_UI_PATH])
        
        print("✅ Both GUIs launched successfully!")
        print("💡 Close this window to terminate both applications.")
        
        # Wait for processes
        passenger_process.wait()
        test_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down both GUIs...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_both_guis()