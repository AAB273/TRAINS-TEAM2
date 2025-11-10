import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'launch_all_modules.py',
    '--onedir',
    '--hidden-import=PIL',
    '--hidden-import=PIL',
    '--hidden-import=numpy',
    '--hidden-import=pandas',
])