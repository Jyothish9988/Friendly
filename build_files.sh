#!/bin/bash

# Activate virtual environment (assuming venv is your virtual environment directory)
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Collect static files (Django specific)
python manage.py collectstatic --noinput

# Deactivate virtual environment
deactivate
