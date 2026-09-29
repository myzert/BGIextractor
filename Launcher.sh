#!/bin/bash
pip3 install -r requirements.txt >/dev/null 2>&1
nohup python3 bgi_toolkit.py >/dev/null 2>&1 &
