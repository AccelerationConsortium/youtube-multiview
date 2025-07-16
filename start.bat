@echo off
echo Starting YouTube MultiView...
cd /d "%~dp0"
pip install flask
python app.py
pause
