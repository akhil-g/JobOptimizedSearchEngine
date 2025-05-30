#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package list and install necessary packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Set environment variables
export PYTHONUNBUFFERED=1

# Create and activate a virtual environment
python3 -m venv /opt/venv
source /opt/venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Create application directory
mkdir -p ~/job_app
cd ~/job_app

# Clone the repository
git clone https://github.com/akhil-g/JobOptimizedSearchEngine.git .
ls -la

# Install Python dependencies
pip install -r requirements.txt
# If needed: pip install --break-system-packages -r requirements.txt

# Run the Django application on port 8000
python3 manage.py runserver 0.0.0.0:8000
