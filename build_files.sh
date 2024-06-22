#!/bin/bash
python3.9 -m venv venv
pip install -r requirements.txt
python manage.py collectstatic --noinput
