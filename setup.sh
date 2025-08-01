#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete! Activate the virtual environment with: source .venv/bin/activate"
