import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.simpledialog as simpledialog
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer

# from CTC_Office import CTC_Main_Screen
# from CTC_Office import CTC_Schedule_Screen
# from CTC_Office import CTC_Test_UI

# #necessary to import the clock from the parent directory#
# import clock

# # CTC Files
# from CTC_Office import CTC_UI


# Wayside HW Controller Files
from WC_HW_MainUI import WC_HW_MainUI



class UIServer:
    def __init__(self):
        self.clients = {}  # e.g., {"CTC": ctc_ui, "Track Model": track_ui, ...}

    def register(self, ui_name, ui_instance):
        self.clients[ui_name] = ui_instance

    def send_to_UI(self, target_name, message, source=None):
        """Deliver message to another UI"""
        target = self.clients.get(target_name)
        if target:
            target._process_message(message, source)
        else:
            print(f"⚠️ No target UI named '{target_name}'")


manager = UI_Variables.TrackDataManager()


# CTC_UI.main()
# WaysideControllerSoftware = 
 WaysideControllerHardware = WC_HW_MainUI(manager)
# TrackModel = UI_Structure.TrackModelUI(manager)
# TrainModel = 
# TrainControllerSoftware = 
# TrainControllerHardware = 






































# import subprocess
# import time
# import sys
# import os


# def launch_both_guis():
#     # Replace these with your exact filepaths
#     PASSENGER_UI_PATH = r"/home/siram/TRAINS-TEAM2/Wayside_Controller/HW/WC_HW_MainUI"  # Use raw string or forward slashes
#     Main_Screen_UI_PATH = r"/home/siram/TRAINS-TEAM2/CTC_Office/CTC_Main_Screen.py"
#     Schedule_Screen_UI_PATH = r"/home/siram/TRAINS-TEAM2/CTC_Office/CTC_Schedule_Screen.py"
    
#     # Verify files exist
#     if not os.path.exists(PASSENGER_UI_PATH):
#         print(f"❌ Main UI not found at: {PASSENGER_UI_PATH}")
#         return
        
#     if not os.path.exists(Main_Screen_UI_PATH): 
#         print(f"❌ Main Screen UI not found at: {Main_Screen_UI_PATH}")
#         return
    
#     if not os.path.exists(Schedule_Screen_UI_PATH): 
#         print(f"❌ Schedule Screen UI not found at: {Schedule_Screen_UI_PATH}")
#         return

#     print(f"✅ Found Main UI: {PASSENGER_UI_PATH}")
#     print(f"✅ Found Main Screen UI: {Main_Screen_UI_PATH}")
#     print(f"✅ Found Schedule Screen UI: {Schedule_Screen_UI_PATH}")
#     print()
    
#     try:
#         print("🚆 Launching Passenger GUI...")
#         passenger_process = subprocess.Popen([sys.executable, PASSENGER_UI_PATH])
        
#         # Wait for socket server to start
#         print("⏳ Waiting for Main GUI socket server to start...")
     
        
#         print("🧪 Launching Main Screen UI...")
#         test_process = subprocess.Popen([sys.executable, Main_Screen_UI_PATH])
        
#         print("🧪 Launching Schedule Screen UI...")
#         schedule_process = subprocess.Popen([sys.executable, Schedule_Screen_UI_PATH])

#         print("✅ Both GUIs launched successfully!")
#         print("💡 Close this window to terminate both applications.")
        
#         # Wait for processes
#         passenger_process.wait()
#         test_process.wait()
#         schedule_process.wait()

#     except KeyboardInterrupt:
#         print("\n🛑 Shutting down both GUIs...")
#     except Exception as e:
#         print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     launch_both_guis()