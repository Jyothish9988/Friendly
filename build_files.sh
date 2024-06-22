#!/bin/bash


# Activate virtual environment
source /absolute/path/to/venv/bin/activate  # Replace with actual absolute path to your virtual environment

# Install dependencies
/absolute/path/to/venv/bin/pip install -r requirements.txt

# Collect static files
/absolute/path/to/venv/bin/python manage.py collectstatic --noinput

# Deactivate virtual environment
deactivate
pip3.9 install -r requirements.txt
