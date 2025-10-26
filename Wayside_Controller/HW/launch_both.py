import subprocess
import time
import sys
import os

def launch_both_guis():
    # Replace these with your exact filepaths
    MAIN_UI_PATH = r"/home/siram/TRAINS-TEAM2/Wayside_Controller/HW/WC_HW_MainUI"  # Use raw string or forward slashes
    TEST_UI_PATH = r"/home/siram/TRAINS-TEAM2/Wayside_Controller/HW/WC_HW_TestUI"
    
    # Verify files exist
    if not os.path.exists(MAIN_UI_PATH):
        print(f"❌ Main UI not found at: {MAIN_UI_PATH}")
        return
        
    if not os.path.exists(TEST_UI_PATH): 
        print(f"❌ Test UI not found at: {TEST_UI_PATH}")
        return
    
    print(f"✅ Found Main UI: {MAIN_UI_PATH}")
    print(f"✅ Found Test UI: {TEST_UI_PATH}")
    print()
    
    try:
        print("🚆 Launching Main UI...")
        main_process = subprocess.Popen([sys.executable, MAIN_UI_PATH])
        
        # Wait for socket server to start
        print("⏳ Waiting for Main UI socket server to start...")
        time.sleep(3)  # Give time for socket server to initialize
        
        print("🧪 Launching Test UI...")
        test_process = subprocess.Popen([sys.executable, TEST_UI_PATH])
        
        print("✅ Both UIs launched successfully!")
        print("💡 Close this window to terminate both applications.")
        
        # Wait for processes
        main_process.wait()
        test_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down both UIs...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_both_guis()