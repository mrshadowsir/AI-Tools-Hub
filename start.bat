@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py serve.py
  exit /b
)
where python >nul 2>nul
if %errorlevel%==0 (
  python serve.py
  exit /b
)
echo Python 3 is not installed.
echo Install with: winget install -e --id Python.Python.3.12
pause