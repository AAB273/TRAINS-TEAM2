import subprocess
import sys
import os
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(script_dir, 'lib')
requirements_file = os.path.join(script_dir, 'requirements.txt')

print("="*60)
print("TRAINS TEAM 2 - BUILD SYSTEM")
print("="*60)

# Step 1: Install libraries to shared lib/ folder
print("\n[1/3] Installing dependencies to lib/ folder...")
if not os.path.exists(requirements_file):
    print(f"ERROR: requirements.txt not found at {requirements_file}")
    sys.exit(1)

try:
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install',
        '-r', requirements_file,
        '-t', lib_dir,
        '--no-deps'  # Avoid duplicate dependency issues
    ])
    print("✓ Dependencies installed to lib/ folder")
except Exception as e:
    print(f"ERROR installing dependencies: {e}")
    sys.exit(1)

# Step 2: Collect all library names for hidden imports
print("\n[2/3] Collecting hidden imports...")
hidden_imports = []
if os.path.exists(lib_dir):
    for item in os.listdir(lib_dir):
        if os.path.isdir(os.path.join(lib_dir, item)) and not item.startswith('_'):
            hidden_imports.append(f'--hidden-import={item}')
            print(f"  + {item}")

# Step 3: Build with PyInstaller
print("\n[3/3] Building executable with PyInstaller...")

build_args = [
    os.path.join(script_dir, 'launch_all_modules.py'),
    '--onedir',
    '--name=TRAINS_Unified_Control',
    '--distpath=' + os.path.join(script_dir, 'dist'),
    '--workpath=' + os.path.join(script_dir, 'build'),
    '--specpath=' + os.path.join(script_dir, 'build'),
    '--windowed',
    '--add-data=' + lib_dir + os.pathsep + 'lib',  # Bundle lib folder
] + hidden_imports

try:
    import PyInstaller.__main__
    PyInstaller.__main__.run(build_args)
    print("\n✓ Build complete!")
except Exception as e:
    print(f"ERROR during build: {e}")
    sys.exit(1)

# Step 4: Verify the build
exe_folder = os.path.join(script_dir, 'dist', 'TRAINS_Unified_Control')
if os.path.exists(exe_folder):
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)
    print(f"Location: {exe_folder}")
    print("\nTo distribute:")
    print("  1. Commit 'lib/' folder to your repo")
    print("  2. Share the 'dist/TRAINS_Unified_Control/' folder")
    print("  3. Recipients just run: TRAINS_Unified_Control.exe")
    print("  4. No Python, no pip, no libraries needed!")
    print("="*60)
else:
    print(f"ERROR: Build folder not found at {exe_folder}")
    sys.exit(1)