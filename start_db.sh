#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting Securities Research Tool Database..."
sudo docker compose up -d

echo "Database status:"
sudo docker compose ps
