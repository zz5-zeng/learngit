@echo off
setlocal

python -m PyInstaller --noconfirm --clean --onefile --windowed --name PunchClock app.py
if errorlevel 1 exit /b 1

if exist "dist\PunchClock.exe" copy /Y "dist\PunchClock.exe" "%USERPROFILE%\Desktop\PunchClock.exe"

echo Build complete.
endlocal
