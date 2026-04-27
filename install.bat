@echo off
echo [*] Initializing Web Recon Installation (Windows)...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed. Please install Python 3.10+ and try again.
    pause
    exit /b
)

echo [*] Creating Virtual Environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [!] Failed to create venv.
    pause
    exit /b
)

echo [*] Activating Environment and Installing Requirements...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [PRO TIP] To run the tool: call venv\Scripts\activate ^& python web_recon.py --domain example.com
echo [SUCCESS] Installation Complete.
pause
