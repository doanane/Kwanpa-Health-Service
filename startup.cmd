@echo off
:: startup.cmd

echo Installing Python dependencies...
pip install -r requirements.txt

echo Starting HEWAL3 API...
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000