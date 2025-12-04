import subprocess
import time
import sys
import os

def launch_both_guis():
    # Replace these with your exact filepaths
    WAYSIDE_UI_PATH = "CTC_Office/CTC_UI.py"
    TRACK_MODEL_UI_PATH = "Track Model/UI_Structure.py"

    # Verify both files exist
    for name, path in [
        ("Wayside Controller", WAYSIDE_UI_PATH),
        ("Track Model UI", TRACK_MODEL_UI_PATH)
    ]:
        if not os.path.exists(path):
            print(f"❌ {name} not found at: {path}")
            return
        print(f"✅ Found {name}: {path}")

    print()

    wayside_process = track_model_process = None

    try:
        print("🚆 Launching Wayside Controller GUI...")
        wayside_process = subprocess.Popen([sys.executable, WAYSIDE_UI_PATH])

        # Optional short delay to ensure socket/server startup
        print("⏳ Waiting for Wayside Controller to initialize...")
        time.sleep(1.5)

        print("🧪 Launching Track Model UI...")
        track_model_process = subprocess.Popen([sys.executable, TRACK_MODEL_UI_PATH])

        print("\n✅ Both GUIs launched successfully!")
        print("💡 Close this window or press Ctrl+C to terminate both applications.\n")

        # Wait for both GUIs to close
        wayside_process.wait()
        track_model_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down both GUIs...")
        for p in [wayside_process, track_model_process]:
            if p is not None:
                p.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_both_guis()
