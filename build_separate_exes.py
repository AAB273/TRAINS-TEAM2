import subprocess
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(script_dir, 'lib')
requirements_file = os.path.join(script_dir, 'requirements.txt')

print("=" * 60)
print("TRAINS TEAM 2 - BUILD SYSTEM (MULTI-EXE, SHARED FILES)")
print("=" * 60)

# ----------------------------------------------------------------------
# Shared files/folders to include for ALL modules
# Write relative paths from your project root here
# E.g., "shared_config", "assets", "common_images"
# ----------------------------------------------------------------------
shared_data_paths = [
    # "shared_config",
    # "assets",
    # "common_images",
]

# ----------------------------------------------------------------------
# 1) Install dependencies to lib/
# ----------------------------------------------------------------------
print("\n[1/4] Installing dependencies to lib/ folder...")
if not os.path.exists(requirements_file):
    print(f"ERROR: requirements.txt not found at {requirements_file}")
    sys.exit(1)

os.makedirs(lib_dir, exist_ok=True)

try:
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install',
        '-r', requirements_file,
        '-t', lib_dir,
        '--no-deps',
    ])
    print("✓ Dependencies installed to lib/ folder")
except Exception as e:
    print(f"ERROR installing dependencies: {e}")
    sys.exit(1)

# ----------------------------------------------------------------------
# 2) Collect hidden imports from lib/
# ----------------------------------------------------------------------
print("\n[2/4] Collecting hidden imports...")
hidden_imports = []
if os.path.exists(lib_dir):
    for item in os.listdir(lib_dir):
        if os.path.isdir(os.path.join(lib_dir, item)) and not item.startswith('_'):
            hidden_imports.append(f'--hidden-import={item}')
            print(f"  + {item}")

# ----------------------------------------------------------------------
# 3) Define all EXEs to build
# ----------------------------------------------------------------------
targets = [
    {"name": "Launcher", "script": "wrapper.py", "console": False},
    {"name": "CTC_UI", "script": os.path.join("CTC_Office", "CTC_UI.py"), "console": False},
    {"name": "Wayside_SW", "script": os.path.join("Wayside_Controller", "SW", "main.py"), "console": False},
    {"name": "Track_Model_UI", "script": os.path.join("Track_Model", "UI_Structure.py"), "console": False},
    {"name": "Train_Model_UI", "script": os.path.join("Train Model", "Passenger_UI.py"), "console": False},
    {"name": "Train_SW_UI", "script": os.path.join("train_controller_sw", "Driver_UI.py"), "console": False},
]

dist_root = os.path.join(script_dir, "dist")
bundle_name = "TrainsSuite"
bundle_dist = os.path.join(dist_root, bundle_name)
build_dir = os.path.join(script_dir, "build")

os.makedirs(dist_root, exist_ok=True)
os.makedirs(build_dir, exist_ok=True)

print("\n[3/4] Building executables with PyInstaller...")

import PyInstaller.__main__

for target in targets:
    script_path = os.path.join(script_dir, target["script"])
    if not os.path.exists(script_path):
        print(f"WARNING: script not found, skipping: {script_path}")
        continue

    print(f"\n--- Building {target['name']} from {target['script']} ---")

    base_args = [
        script_path,
        "--onedir",
        f"--name={target['name']}",
        f"--distpath={bundle_dist}",
        f"--workpath={build_dir}",
        f"--specpath={build_dir}",
        "--add-data=" + lib_dir + os.pathsep + "lib",

        # Include shared data into root of dist folder (accessible by all modules)
    ] + [
        f"--add-data={os.path.join(script_dir, path)}{os.pathsep}{path}" for path in shared_data_paths
    ] + [
        "--collect-all=PIL",
        "--collect-all=playsound",
        "--collect-all=tkinter",
        "--collect-all=pandas",
        "--copy-metadata=pyinstaller",
        "--noupx"
    ] + hidden_imports

    if not target["console"]:
        base_args.append("--noconsole")

    try:
        PyInstaller.__main__.run(base_args)
        print(f"✓ Built {target['name']}")
    except Exception as e:
        print(f"ERROR building {target['name']}: {e}")

# ----------------------------------------------------------------------
# 4) Final message
# ----------------------------------------------------------------------
print("\n[4/4] Verifying bundle...")

if os.path.exists(bundle_dist):
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"All EXEs and shared files are in: {bundle_dist}")
    print("\nTo distribute:")
    print(f" 1. Zip the entire folder: {bundle_dist}")
    print("  2. Send the zip to users.")
    print("  3. Users unzip anywhere and run Launcher/Launcher.exe")
    print("  4. No Python, no pip, no libraries needed on target machines.")
    print("=" * 60)
else:
    print(f"ERROR: Bundle folder not found at {bundle_dist}")
    sys.exit(1)
