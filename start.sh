#!/bin/bash
echo "Starting YouTube MultiView..."
cd "$(dirname "$0")"
pip install flask
python app.py
