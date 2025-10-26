@echo off

REM Development startup script for Windows

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration before running the service.
    pause
    exit /b 1
)

REM Start the service
echo Starting YouTube Transcription API...
docker-compose up --build