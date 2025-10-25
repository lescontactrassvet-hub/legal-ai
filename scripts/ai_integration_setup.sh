#!/usr/bin/env bash
# Setup script for LegalAI integration
# This script prepares the environment, installs dependencies, and performs initial setup for the AI modules.

set -e

# Create a Python virtual environment if it doesn't exist
if [ ! -d "~/.venv-legalai" ]; then
  python3 -m venv ~/.venv-legalai
fi

# Activate the virtual environment
source ~/.venv-legalai/bin/activate

# Upgrade pip and install backend requirements
pip install --upgrade pip wheel
pip install -r backend/requirements.txt

# Run any database migrations or initialization commands here
# e.g., python backend/app/main.py --init-db (if applicable)

# Print completion message
echo "LegalAI integration setup completed successfully."
