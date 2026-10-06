#!/bin/bash
cd /home/xia/htdocs/xia.ar/backend
pkill -f python3 main.py 2>/dev/null
python3 main.py
