@echo off
echo ========================================
echo   CodeLens AI - Startup Script
echo ========================================
echo.

echo [1/3] Starting MongoDB...
start "MongoDB" cmd /k "mongod --dbpath C:\data\db"
timeout /t 3 /nobreak > nul

echo [2/3] Starting Backend API...
start "Backend API" cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak > nul

echo [3/3] Starting Frontend...
start "Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   All services starting...
echo ========================================
echo.
echo   MongoDB:  Running in separate window
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application...
pause > nul

start http://localhost:3000

echo.
echo Application opened in browser!
echo Close this window when done.
pause