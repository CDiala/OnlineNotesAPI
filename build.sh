#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip

pip3 install -r requirements.txt

python3 manage.py collectstatic --no-input
python3 manage.py makemigrations
python3 manage.py migrate