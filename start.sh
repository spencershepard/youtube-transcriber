#!/bin/bash

# Development startup script

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running the service."
    exit 1
fi

# Start the service
echo "Starting YouTube Transcription API..."
docker-compose up --build