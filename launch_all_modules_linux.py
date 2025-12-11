import subprocess
import sys
import time
import os
import platform
from pathlib import Path

if os.environ.get('TRAINS_LAUNCHER_RUNNING') == '1':
    print("ERROR: Recursive launch detected!")
    sys.exit(1)

def launch_in_terminal_wsl(module_name, file_path, exe_dir, env):
    """Launch a subprocess in its own terminal window for WSL/Ubuntu."""
    try:
        # WSL specific: check if we're in WSL
        is_wsl = 'microsoft' in platform.uname().release.lower()
        
        # Use absolute paths
        abs_file_path = os.path.abspath(file_path)
        python_exe = sys.executable
        
        # Check if file exists
        if not os.path.exists(abs_file_path):
            print(f"  ! File does not exist: {abs_file_path}")
            return False
        
        # For WSL/Ubuntu, use xterm or gnome-terminal
        # First try to detect which terminal is available
        terminal_emulator = None
        
        # Check for common terminals
        terminals_to_try = ['gnome-terminal', 'xterm', 'konsole', 'xfce4-terminal', 'mate-terminal']
        for term in terminals_to_try:
            try:
                result = subprocess.run(['which', term], capture_output=True, text=True, timeout=1)
                if result.returncode == 0:
                    terminal_emulator = term
                    break
            except:
                continue
        
        if not terminal_emulator:
            # If no terminal found, try running directly
            print(f"  ! No terminal emulator found for {module_name}, running in background")
            return launch_in_background(module_name, file_path, exe_dir, env)
        
        # Build the command based on the terminal emulator
        if terminal_emulator == 'gnome-terminal':
            cmd = [
                'gnome-terminal',
                '--title', f'TRAINS - {module_name}',
                '--', 'bash', '-c',
                f'cd "{exe_dir}" && echo "=== {module_name} ===" && "{python_exe}" -u "{abs_file_path}" && echo "Process completed. Press Enter to close..." && read'
            ]
        elif terminal_emulator == 'xterm':
            cmd = [
                'xterm',
                '-title', f'TRAINS - {module_name}',
                '-hold', '-e',
                f'cd "{exe_dir}"; echo "=== {module_name} ==="; "{python_exe}" -u "{abs_file_path}"; echo "Process completed. Press Enter to close..."; read'
            ]
        elif terminal_emulator == 'konsole':
            cmd = [
                'konsole',
                '--title', f'TRAINS - {module_name}',
                '--noclose', '-e',
                f'bash -c \'cd "{exe_dir}"; echo "=== {module_name} ==="; "{python_exe}" -u "{abs_file_path}"; echo "Process completed. Press Enter to close..."; read\''
            ]
        else:
            # Generic fallback
            cmd = [
                terminal_emulator,
                '-e', f'bash -c \'cd "{exe_dir}"; echo "=== {module_name} ==="; "{python_exe}" -u "{abs_file_path}"; echo "Process completed. Press Enter to close..."; read\''
            ]
        
        # Debug: print the command
        print(f"    Command: {' '.join(cmd[:4])}...")
        
        # Launch the process
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=exe_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(0.5)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process ended quickly, check for errors
            stdout, stderr = process.communicate()
            if stderr:
                print(f"    Error: {stderr.decode('utf-8', errors='ignore')[:200]}")
            return launch_in_background(module_name, file_path, exe_dir, env)
        
        return True
        
    except Exception as e:
        print(f"  ! Failed to launch {module_name} in terminal: {e}")
        return launch_in_background(module_name, file_path, exe_dir, env)

def launch_in_background(module_name, file_path, exe_dir, env):
    """Launch a subprocess in background with logging."""
    try:
        abs_file_path = os.path.abspath(file_path)
        python_exe = sys.executable
        
        # Create logs directory
        log_dir = os.path.join(exe_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{module_name.replace(' ', '_')}_{timestamp}.log")
        
        with open(log_file, 'w') as f:
            f.write(f"=== {module_name} ===\n")
            f.write(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python: {python_exe}\n")
            f.write(f"Script: {abs_file_path}\n")
            f.write(f"Directory: {exe_dir}\n")
            f.write("="*50 + "\n\n")
        
        # Launch process
        process = subprocess.Popen(
            [python_exe, '-u', abs_file_path],
            env=env,
            cwd=exe_dir,
            stdout=open(log_file, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Save PID
        pid_file = os.path.join(log_dir, f"{module_name.replace(' ', '_')}.pid")
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"    Running in background (PID: {process.pid})")
        print(f"    Log: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"  ! Failed to launch {module_name} in background: {e}")
        return False

def launch_all():
    # Get the script directory - IMPORTANT: This should be the project root
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # In WSL/VS Code, we might need to navigate to the project root
    # Look for common project structure indicators
    project_root = script_dir
    for indicator in ['.git', 'requirements.txt', 'README.md', 'train_controller_sw', 'Track Model']:
        test_path = os.path.join(project_root, indicator)
        if os.path.exists(test_path):
            # We're in the right place
            break
    
    # If we're in a subdirectory, go up until we find project files
    max_levels = 5
    for i in range(max_levels):
        found_project = False
        for indicator in ['train_controller_sw', 'Track Model', 'Train Model', 'CTC_Office']:
            test_path = os.path.join(project_root, indicator)
            if os.path.exists(test_path):
                found_project = True
                break
        
        if found_project:
            break
        else:
            # Go up one level
            project_root = os.path.dirname(project_root)
            if project_root == '/':
                break
    
    print("\n" + "="*60)
    print("TRAINS TEAM 2 - UNIFIED CONTROL SYSTEM")
    print(f"Launcher directory: {script_dir}")
    print(f"Project root: {project_root}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("="*60 + "\n")
    
    # Define modules with relative paths from project root
    modules = [
        #("CTC", "CTC_Office/CTC_UI.py"),
        #("Track SW", "Wayside_Controller/SW/main.py"),
        #("Track Model", "Track Model/UI_Structure.py"),
        ("Train Model", "Train Model/Passenger_UI.py"),
        ("Train SW", "train_controller_sw/Driver_UI.py"),
        #("Train HW", "HW_Train_Controller/TC_HW_MainUI.py"),
        ("Test UI", "Train Model/Test_UI.py")
    ]
    
    # Check which modules exist
    available_modules = []
    for module_name, module_path in modules:
        full_path = os.path.join(project_root, module_path)
        if os.path.exists(full_path):
            available_modules.append((module_name, module_path))
            print(f"  ✓ Found: {module_name} -> {full_path}")
        else:
            print(f"  ✗ Missing: {module_name} -> {full_path}")
    
    if not available_modules:
        print("\nERROR: No module files found!")
        print("Make sure you're running from the correct directory.")
        print("Expected to find files in paths like:")
        for module_name, module_path in modules[:3]:
            print(f"  {module_path}")
        return
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
    env['TRAINS_LAUNCHER_RUNNING'] = '1'
    
    print(f"\nLaunching {len(available_modules)} modules from {project_root}...\n")
    successful_launches = 0
    
    for module_name, module_path in available_modules:
        full_path = os.path.join(project_root, module_path)
        
        print(f"  > Launching {module_name}")
        print(f"    Path: {full_path}")
        
        if launch_in_terminal_wsl(module_name, full_path, project_root, env):
            print(f"    ✓ {module_name} launched successfully")
            successful_launches += 1
        else:
            print(f"    ✗ Failed to launch {module_name}")
        
        time.sleep(1)  # Give time between launches
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {successful_launches}/{len(available_modules)} modules launched")
    print(f"{'='*60}\n")
    
    if successful_launches > 0:
        print("Next steps:")
        print("1. Check the terminal windows that opened")
        print("2. If modules didn't open in terminals, check log files in 'logs/' directory")
        print("3. Wait for all modules to initialize (check for any error messages)")
        
        # Create management script
        create_management_script(project_root)
        
        # Interactive options
        try:
            print("\nOptions:")
            print("  [Enter] - Exit launcher (modules keep running)")
            print("  'stop'  - Stop all modules and exit")
            print("  'logs'  - Show recent logs")
            
            user_input = input("\n> ").strip().lower()
            
            if user_input == 'stop':
                print("\nStopping all modules...")
                subprocess.run(['pkill', '-f', 'python.*(UI|main)'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("All modules stopped.")
            elif user_input == 'logs':
                show_recent_logs(project_root)
                
        except KeyboardInterrupt:
            print("\n\nLauncher interrupted.")
            print("Modules continue running in background.")
    else:
        print("\nERROR: No modules were launched successfully!")
        print("Possible issues:")
        print("1. Check that all Python files exist")
        print("2. Make sure you have required dependencies installed")
        print("3. Check terminal emulator installation (try: sudo apt install xterm)")

def create_management_script(project_root):
    """Create a management script."""
    script_path = os.path.join(project_root, "manage_trains.sh")
    
    script_content = """#!/bin/bash
# TRAINS System Management
# Usage: ./manage_trains.sh [command]

case "$1" in
    stop)
        echo "Stopping all TRAINS modules..."
        pkill -f "python.*(Passenger_UI|Driver_UI|CTC_UI|UI_Structure|main|Test_UI)"
        echo "Done."
        ;;
    status)
        echo "Active TRAINS processes:"
        ps aux | grep -E "python.*(Passenger_UI|Driver_UI|CTC_UI|UI_Structure|main|Test_UI)" | grep -v grep
        ;;
    logs)
        if [ -d "logs" ]; then
            echo "Recent logs:"
            find logs/ -name "*.log" -type f -exec ls -lh {} \\; | head -10
            echo ""
            echo "View a log: tail -f logs/FILENAME.log"
        else
            echo "No logs directory."
        fi
        ;;
    help|*)
        echo "TRAINS Management Commands:"
        echo "  ./manage_trains.sh stop    - Stop all modules"
        echo "  ./manage_trains.sh status  - Show running processes"
        echo "  ./manage_trains.sh logs    - List log files"
        ;;
esac
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        print(f"✓ Management script: {script_path}")
    except:
        print("Note: Could not create management script")

def show_recent_logs(project_root):
    """Show recent log files."""
    log_dir = os.path.join(project_root, "logs")
    if os.path.exists(log_dir):
        print(f"\nRecent logs in {log_dir}:")
        logs = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        logs.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
        
        for log in logs[:5]:
            log_path = os.path.join(log_dir, log)
            size = os.path.getsize(log_path)
            mtime = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(log_path)))
            print(f"  {log} ({size/1024:.1f} KB, {mtime})")
    else:
        print("No logs directory found.")

if __name__ == "__main__":
    try:
        launch_all()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()