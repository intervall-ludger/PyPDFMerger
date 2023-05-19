#!/bin/bash

# PyInstaller for onefile
pyinstaller --onefile --windowed --icon=icon.ico --add-data="./icon.ico;." --noconsole pypdfmerger.py --noconfirm

# PyInstaller for onedir
pyinstaller --onedir --windowed --icon=icon.ico --add-data="./icon.ico;." --noconsole pypdfmerger.py --noconfirm
