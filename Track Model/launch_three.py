import subprocess
import time
import sys
import os

def launch_three_guis():
    # Replace these with your exact filepaths
    PASSENGER_UI_PATH = "Train Model/Passenger_UI.py"
    TEST_UI_PATH = "Track Model/UI_Structure.py"
    CTC_UI_PATH = "CTC_Office/CTC_UI.py"  # ✅ Third GUI (example)
    
    # Verify files exist
    for name, path in [
        ("Passenger UI", PASSENGER_UI_PATH),
        ("Test UI", TEST_UI_PATH),
        ("CTC UI", CTC_UI_PATH)
    ]:
        if not os.path.exists(path):
            print(f"❌ {name} not found at: {path}")
            return
        print(f"✅ Found {name}: {path}")
    
    print()
    
    try:
        print("🚆 Launching Passenger GUI...")
        passenger_process = subprocess.Popen([sys.executable, PASSENGER_UI_PATH])

        print("⏳ Waiting for Passenger GUI socket server to start...")
        time.sleep(1.5)  # optional small delay between launches

        print("🧪 Launching Track Model UI...")
        test_process = subprocess.Popen([sys.executable, TEST_UI_PATH])

        print("🏢 Launching CTC Office UI...")
        ctc_process = subprocess.Popen([sys.executable, CTC_UI_PATH])

        print("✅ All 3 GUIs launched successfully!")
        print("💡 Close this window to terminate all applications.\n")

        # Wait for all processes
        passenger_process.wait()
        test_process.wait()
        ctc_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down all GUIs...")
        passenger_process.terminate()
        test_process.terminate()
        ctc_process.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_three_guis()
