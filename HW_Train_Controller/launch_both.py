#!/usr/bin/env python3
"""
Launch script for Train Control System
Starts both Train Control Hardware UI and Test Train Model simultaneously

RUN THIS FROM: C:/Users/lucas/Desktop/TRAINS-TEAM2/
"""

import subprocess
import time
import sys
import os
import threading
import signal

def main():
    print("=" * 60)
    print("TRAIN CONTROL SYSTEM LAUNCHER")
    print("=" * 60)
    print("Starting: Train Controller HW + Test Train Model")
    print("=" * 60)
    
    processes = []
    
    try:
        # Start Train Control Hardware UI
        print("\n[1/2] Starting Train Control Hardware UI...")
        train_control = subprocess.Popen(
            [sys.executable, 'HW_Train_Controller/TC_HW_MainUI.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        processes.append(('Train Control HW', train_control))
        print("     ✓ Train Control UI started (PID: {})".format(train_control.pid))
        
        # Wait for first UI to initialize
        time.sleep(5)
        
        # Start Test Train Model
        print("\n[2/2] Starting Test Train Model...")
        train_model = subprocess.Popen(
            [sys.executable, 'HW_Train_Controller/Test_Train_Model.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        processes.append(('Test Train Model', train_model))
        print("     ✓ Test Train Model started (PID: {})".format(train_model.pid))
        
        # Wait for socket connections to establish
        time.sleep(5)
        
        print("\n" + "=" * 60)
        print("ALL SYSTEMS RUNNING")
        print("=" * 60)
        print("Applications Started:")
        print("  • Train Control Hardware UI")
        print("  • Test Train Model (Simulator)")
        print("\nExpected Connections:")
        print("  • Train Controller HW ↔ Test Train Model (Sockets)")
        print("  • Windows UI ↔ Raspberry Pi GPIO Server")
        print("\nPress Ctrl+C to shut down all systems")
        print("=" * 60)
        
        # Monitor process output in real-time
        def monitor_output(process, name):
            while True:
                try:
                    output = process.stdout.readline()
                    if output:
                        print(f"[{name}] {output.strip()}")
                    # Also check stderr
                    err_output = process.stderr.readline()
                    if err_output:
                        print(f"[{name}-ERROR] {err_output.strip()}")
                except:
                    break
                time.sleep(0.1)
        
        # Start output monitoring for each process
        for name, process in processes:
            monitor_thread = threading.Thread(
                target=monitor_output, 
                args=(process, name),
                daemon=True
            )
            monitor_thread.start()
        
        # Keep the script running and monitor processes
        while True:
            time.sleep(2)
            
            all_running = True
            for name, process in processes:
                return_code = process.poll()
                if return_code is not None:
                    print(f"\n⚠ {name} has exited (code: {return_code})")
                    all_running = False
            
            if not all_running:
                print("\nOne or more applications have exited. Shutting down...")
                break
                
            # Print status every 30 seconds
            print("[Launcher] All systems running normally...")
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("SHUTTING DOWN ALL SYSTEMS")
        print("=" * 60)
        
        # Terminate all processes
        for name, process in processes:
            if process.poll() is None:  # If still running
                print(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"  ✓ {name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    print(f"  ⚠ {name} didn't stop, forcing...")
                    process.kill()
                    process.wait()
                    print(f"  ✓ {name} force stopped")
        
        print("\n" + "=" * 60)
        print("SHUTDOWN COMPLETE")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Terminating all processes...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                process.kill()
        sys.exit(1)

if __name__ == "__main__":
    # Verify we're in the correct directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    required_files = [
        'HW_Train_Controller/TC_HW_MainUI.py',
        'HW_Train_Controller/Test_Train_Model.py', 
        'TrainSocketServer.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ ERROR: Missing required files!")
        for missing in missing_files:
            print(f"   - {missing}")
        print(f"\n   This script must be run from: C:/Users/lucas/Desktop/TRAINS-TEAM2/")
        print("\n   To fix, run:")
        print("   cd C:/Users/lucas/Desktop/TRAINS-TEAM2")
        print("   python launch_both.py")
        sys.exit(1)
    
    print("✓ All required files found")
    main()