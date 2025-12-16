#!/bin/bash
# Install dependencies
pip install -r requirements-azure.txt

# Create uploads directory
mkdir -p uploads

# Run database migrations if needed
# python -m alembic upgrade head

# Start the application
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120
