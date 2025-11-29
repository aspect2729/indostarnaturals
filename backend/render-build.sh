#!/usr/bin/env bash
# Render build script - runs on every deployment
set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Build completed successfully!"
