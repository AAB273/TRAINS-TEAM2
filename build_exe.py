import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'launch_all_modules.py',
    '--onedir',
    '--windowed',
    '--hidden-import=PIL',
    '--hidden-import=playsound',
    '--hidden-import=pandas'
])
