#!/bin/bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
python manage.py collectstatic --noinput
deactivate  # Deactivate virtual environment
