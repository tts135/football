@echo off
cd /d "%~dp0"
call e:\pyPreoject\football\venv\Scripts\activate.bat
cd webapp
python app.py
pause