#!/bin/sh
flask db init
flask db migrate
flask db upgrade

gunicorn --worker-class eventlet -w 1 -b :8000 app:app --access-logfile ./logs/log.txt --log-level debug 