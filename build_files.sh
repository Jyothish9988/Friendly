#!/bin/bash
source venv/bin/activate  # Activate virtual environment
pip3.9 install -r requirements.txt
python3.9 manage.py collectstatic --noinput
deactivate  # Deactivate virtual environment
