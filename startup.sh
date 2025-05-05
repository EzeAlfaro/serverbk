#!/bin/bash
# Fuerza instalación incluso si hay caché
python -m pip install --force-reinstall -r /home/site/wwwroot/requirements.txt
# Inicia la app
gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 300 app:app