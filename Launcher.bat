@echo off
echo Installing dependencies if missing...
pip install -r requirements.txt >nul 2>&1
start pythonw bgi_toolkit.py
exit
