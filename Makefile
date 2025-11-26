.PHONY: help install dev up down logs clean test lint format migrate

help:
	@echo "IndoStar Naturals - Available Commands"
	@echo "======================================="
	@echo "install      - Install all dependencies"
	@echo "dev          - Start development servers"
	@echo "up           - Start Docker containers"
	@echo "down         - Stop Docker containers"
	@echo "logs         - View Docker logs"
	@echo "clean        - Clean build artifacts"
	@echo "test         - Run all tests"
	@echo "lint         - Lint all code"
	@echo "format       - Format all code"
	@echo "migrate      - Run database migrations"
	@echo "init-db      - Initialize database with migrations"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:5173"
	docker-compose up postgres redis -d
	@echo "Start backend: cd backend && uvicorn app.main:app --reload"
	@echo "Start frontend: cd frontend && npm run dev"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/.pytest_cache backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.cache

test:
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

lint:
	@echo "Linting backend..."
	cd backend && flake8 app/
	@echo "Linting frontend..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend..."
	cd backend && black app/
	@echo "Formatting frontend..."
	cd frontend && npm run format

migrate:
	cd backend && alembic upgrade head

init-db:
	cd backend && python scripts/init_db.py
