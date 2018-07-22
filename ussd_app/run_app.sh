#!/usr/bin/env bash
# Start Gunicorn processes
echo "Starting Gunicorn"
exec gunicorn manage:app --bind 0.0.0.0:8000