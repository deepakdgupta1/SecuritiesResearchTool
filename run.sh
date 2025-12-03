#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please run 'poetry install' first."
    exit 1
fi

# Add current directory to PYTHONPATH to ensure backend package is found
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Check if database is running
echo "Checking database status..."
if ! sudo docker compose ps --services --filter "status=running" | grep -q "db"; then
    echo "Database is not running. Starting it now..."
    sudo docker compose up -d
    
    # Wait for health check
    echo "Waiting for database to be ready..."
    until sudo docker compose ps db --format json | grep -q '"Health":"healthy"'; do
        echo -n "."
        sleep 1
    done
    echo " Database is ready!"
fi

# Start FastAPI server
# Reload is enabled for development
echo "Starting Securities Research Tool API..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
