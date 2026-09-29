#!/bin/bash
pip3 install -r requirements.txt >/dev/null 2>&1
nohup python3 bgie_app.py >/dev/null 2>&1 &
