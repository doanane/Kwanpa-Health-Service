#!/bin/bash
# startup.sh

# Install dependencies
pip install -r requirements.txt



# Start Gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000