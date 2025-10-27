@echo off
echo YouTube Transcriber API - Startup Script
echo =========================================

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    if exist .env.template (
        copy .env.template .env
    ) else if exist .env.example (
        copy .env.example .env
    ) else (
        echo Error: No template file found. Please create a .env file manually.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Created .env file. Please edit it with your configuration:
    echo    - Set PROXY_TYPE (webshare, brightdata, or leave empty)
    echo    - Add your proxy credentials if using a proxy
    echo    - Optionally set API_TOKEN for authentication
    echo.
    echo Press any key to open the .env file for editing...
    pause >nul
    notepad .env
    echo.
)

echo Choose startup method:
echo 1. Docker (Recommended for production)
echo 2. Local Python (Development)
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting with Docker...
    docker-compose up --build
) else if "%choice%"=="2" (
    echo Starting with local Python...
    echo Make sure you have installed dependencies: pip install -r requirements.txt
    python main.py
) else if "%choice%"=="3" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)