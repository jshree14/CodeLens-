@echo off
echo ========================================
echo   CodeLens AI - Setup Script
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [2/4] Installing Frontend Dependencies...
call npm install
if errorlevel 1 (
    echo Error: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Setting up Environment...
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo Created backend\.env file
    echo Please add your GEMINI_API_KEY to backend\.env
) else (
    echo backend\.env already exists
)

echo.
echo [4/4] Verifying Installation...
python --version
node --version
npm --version

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Add your GEMINI_API_KEY to backend\.env
echo 2. Make sure MongoDB is installed and running
echo 3. Run start.bat to launch the application
echo.
echo Get Gemini API key: https://makersuite.google.com/app/apikey
echo.
pause
