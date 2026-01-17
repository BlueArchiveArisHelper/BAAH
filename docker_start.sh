#!/bin/sh
CONTAINER_IP=$(hostname -I | cut -d ' ' -f 1)
cd /app/BAAH
python3 jsoneditor.py --no-show --host $CONTAINER_IP