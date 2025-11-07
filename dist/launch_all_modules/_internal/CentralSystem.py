import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.simpledialog as simpledialog
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from TrainSocketServer import TrainSocketServer



# # CTC Files
# from CTC_Office import CTC_Main_Screen
# from CTC_Office import CTC_Schedule_Screen
# from CTC_Office import CTC_Test_UI

# #necessary to import the clock from the parent directory#
# import clock
# from CTC_Office import CTC_UI


# Wayside SW Files


#Wayside HW Files



# Track Model Files
from Track_Model import UI_Structure
from Track_Model import UI_Variables


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
# WaysideControllerHardware = 
TrackModel = UI_Structure.TrackModelUI(manager)
# TrainModel = 
# TrainControllerSoftware = 
# TrainControllerHardware = 
