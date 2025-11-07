import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'launch_all_modules.py',
    '--onedir',
    '--windowed',
    '--add-data', 'CTC_Office:CTC_Office',
    '--add-data', 'Wayside_Controller:Wayside_Controller',
    '--add-data', 'Track_Model:Track_Model',
    '--add-data', 'Train Model:Train Model',
    '--add-data', 'train_controller_sw:train_controller_sw',
])
