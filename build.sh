#!/bin/bash
# build.sh - Build script for Render deployment

echo "🚀 Starting HEWAL3 Backend Build Process..."

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Creating uploads directory..."
mkdir -p uploads

echo "🔧 Setting up database..."
python -c "
from app.database import create_tables
from app.config import settings
print('Environment:', settings.ENVIRONMENT)
print('Database URL:', settings.DATABASE_URL)
create_tables()
"

echo "✅ Build completed successfully!"