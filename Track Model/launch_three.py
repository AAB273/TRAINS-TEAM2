import subprocess
import time
import sys
import os

def launch_three_guis():
    # Replace these with your exact filepaths
    PASSENGER_UI_PATH = "Train Model/Passenger_UI.py"
    TRACK_MODEL_UI_PATH = "Track Model/UI_Structure.py"
    TEST_UI_PATH = "Train Model/Test_UI.py"  # ✅ Third GUI

    # Verify files exist
    for name, path in [
        ("Passenger UI", PASSENGER_UI_PATH),
        ("Track Model UI", TRACK_MODEL_UI_PATH),
        ("Test UI", TEST_UI_PATH)
    ]:
        if not os.path.exists(path):
            print(f"❌ {name} not found at: {path}")
            return
        print(f"✅ Found {name}: {path}")

    print()

    passenger_process = test_process = track_model_process = None

    try:
        print("🚆 Launching Passenger GUI...")
        passenger_process = subprocess.Popen([sys.executable, PASSENGER_UI_PATH])

        print("⏳ Waiting for Passenger GUI socket server to start...")
        time.sleep(1.5)  # small delay to let it initialize

        print("🧪 Launching Track Model UI...")
        track_model_process = subprocess.Popen([sys.executable, TRACK_MODEL_UI_PATH])

        print("🧰 Launching Test UI...")
        test_process = subprocess.Popen([sys.executable, TEST_UI_PATH])

        print("\n✅ All 3 GUIs launched successfully!")
        print("💡 Close this window or press Ctrl+C to terminate all applications.\n")

        # Wait for all processes to complete
        passenger_process.wait()
        track_model_process.wait()
        test_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down all GUIs...")
        for p in [passenger_process, track_model_process, test_process]:
            if p is not None:
                p.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_three_guis()
