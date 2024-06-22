#!/bin/bash

# Activate virtual environment
venv\Scripts\activate  # Adjust path if necessary for your project structure

# Install dependencies
pip install -r requirements.txt

# Collect static files (Django specific)
python manage.py collectstatic --noinput

# Deactivate virtual environment
deactivate
