#!/usr/bin/env python3
"""
Launch script for Train Control System
Starts both Train Control Hardware UI and Train Model UI simultaneously

RUN THIS FROM: /home/lucas-chen-pi/Documents/TRAINS-TEAM2/
"""

import subprocess
import time
import sys
import os

def main():
    print("=" * 60)
    print("TRAIN CONTROL SYSTEM LAUNCHER")
    print("=" * 60)
    
    processes = []
    
    try:
        # Start Train Control Hardware UI
        print("\n[1/2] Starting Train Control Hardware UI...")
        train_control = subprocess.Popen(
            ['python3', 'HW_Train_Controller/TC_HW_MainUI.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('Train Control HW', train_control))
        print("     ✓ Train Control UI started (PID: {})".format(train_control.pid))
        
        # Wait for first UI to initialize
        time.sleep(3)
        
        # Start Train Model UI
        # UPDATE THIS PATH to match your Train Model location
        print("\n[2/2] Starting Train Model UI...")
        train_model = subprocess.Popen(
            ['python3', 'TrainModel/TrainModel_UI.py'],  # ← UPDATE THIS PATH
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('Train Model', train_model))
        print("     ✓ Train Model UI started (PID: {})".format(train_model.pid))
        
        # Wait for socket connections to establish
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("ALL SYSTEMS RUNNING")
        print("=" * 60)
        print("\nPress Ctrl+C to shut down all systems\n")
        
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n⚠ WARNING: {name} has stopped (exit code: {process.returncode})")
                    raise KeyboardInterrupt
    
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
    if not os.path.exists('HW_Train_Controller/TC_HW_MainUI.py'):
        print("❌ ERROR: HW_Train_Controller/TC_HW_MainUI.py not found!")
        print("\n   This script must be run from: /home/lucas-chen-pi/Documents/TRAINS-TEAM2/")
        print("   Current directory:", os.getcwd())
        print("\n   To fix, run:")
        print("   cd /home/lucas-chen-pi/Documents/TRAINS-TEAM2/")
        print("   python3 launch_both.py")
        sys.exit(1)
    
    if not os.path.exists('TrainSocketServer.py'):
        print("⚠ WARNING: TrainSocketServer.py not found in current directory!")
        print("   Expected: /home/lucas-chen-pi/Documents/TRAINS-TEAM2/TrainSocketServer.py")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    main()
