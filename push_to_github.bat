@echo off
echo ========================================
echo   Push CodeLens AI to GitHub
echo ========================================
echo.

set /p USERNAME="Enter your GitHub username: "

echo.
echo Connecting to GitHub repository...
git remote remove origin 2>nul
git remote add origin https://github.com/%USERNAME%/CodeLens.git

echo.
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Push Failed!
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. GitHub authentication required
    echo 2. Repository doesn't exist
    echo 3. No internet connection
    echo.
    echo Try this:
    echo 1. Make sure you're logged into GitHub
    echo 2. Repository name is: CodeLens
    echo 3. Run: git push -u origin main
    echo.
) else (
    echo.
    echo ========================================
    echo   Success!
    echo ========================================
    echo.
    echo Your project is now on GitHub!
    echo Visit: https://github.com/%USERNAME%/CodeLens
    echo.
)

pause
