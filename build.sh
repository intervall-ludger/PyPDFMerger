#!/bin/bash

# PyInstaller for onefile
pyinstaller --onefile --windowed --icon=icon.ico --add-data="./icon.ico;." --add-data="drag_and_drop.png;." --noconsole pypdfmerger.py --noconfirm

# PyInstaller for onedir
pyinstaller --onedir --windowed --icon=icon.ico --add-data="./icon.ico;."  --add-data="drag_and_drop.png;." --noconsole pypdfmerger.py --noconfirm
