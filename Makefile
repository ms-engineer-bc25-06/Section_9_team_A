# Bridge Line Development Makefile
# Compatible with Windows, Mac OS, and Linux

# OS detection
ifeq ($(OS),Windows_NT)
    # Windows
    WAIT_CMD = timeout /t $(1) /nobreak > nul 2>&1 || ping -n $(1) 127.0.0.1 > nul 2>&1
    RM_CMD = del /q
    MKDIR_CMD = mkdir
else
    # Unix-like systems (Linux, Mac OS)
    WAIT_CMD = sleep $(1)
    RM_CMD = rm -rf
    MKDIR_CMD = mkdir -p
endif

.PHONY: help setup start stop restart logs clean build test migrate frontend backend

# Default target
help:
	@echo "Bridge Line Development Commands"
	@echo ""
	@echo "Environment Setup:"
	@echo "  make setup     - Initial development environment setup"
	@echo "  make start     - Start Docker environment"
	@echo "  make stop      - Stop Docker environment"
	@echo "  make restart   - Restart Docker environment"
	@echo ""
	@echo "Development:"
	@echo "  make logs      - Show logs"
	@echo "  make build     - Rebuild containers"
	@echo "  make test      - Run tests"
	@echo "  make migrate   - Run database migrations"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend  - Start frontend development server"
	@echo ""
	@echo "Backend:"
	@echo "  make backend   - Show backend logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean     - Remove containers and volumes"

# Initial development environment setup
setup:
	@echo "Starting Bridge Line development environment setup..."
	@if [ -f "scripts/dev-setup-mac.sh" ]; then \
		chmod +x scripts/dev-setup-mac.sh && ./scripts/dev-setup-mac.sh; \
	elif [ -f "scripts/dev-setup.sh" ]; then \
		chmod +x scripts/dev-setup.sh && ./scripts/dev-setup.sh; \
	elif [ -f "scripts/dev-setup.ps1" ]; then \
		powershell -ExecutionPolicy Bypass -File scripts/dev-setup.ps1; \
	else \
		echo "Setup script not found."; \
		echo "Please run the following commands manually:"; \
		echo "  docker compose up --build -d"; \
		echo "  docker exec bridge_line_backend alembic upgrade head"; \
	fi

# Start Docker environment
start:
	@echo "Starting Docker environment..."
	@echo "Step 1: Starting database services..."
	docker compose up -d postgres redis
	@echo "Waiting for database services to be ready..."
	@$(call wait,20)
	@echo "Step 2: Starting backend service..."
	docker compose up -d backend
	@echo "Waiting for backend service to be ready..."
	@$(call wait,30)
	@echo "Environment started successfully."
	@echo "Access URLs:"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Database: localhost:5432"
	@echo "  Redis: localhost:6379"
	@echo ""
	@echo "Checking service status..."
	@docker compose ps
	@echo ""
	@echo "Checking backend health..."
	@$(call wait,10)
	@docker compose logs --tail=10 backend

# Stop Docker environment
stop:
	@echo "Stopping Docker environment..."
	docker compose down
	@echo "Environment stopped successfully."

# Restart Docker environment
restart:
	@echo "Restarting Docker environment..."
	docker compose restart
	@echo "Environment restarted successfully."

# Show logs
logs:
	@echo "Showing logs..."
	docker compose logs -f

# Show backend logs
backend:
	@echo "Showing backend logs..."
	docker compose logs -f backend

# Check backend status
backend-status:
	@echo "Checking backend service status..."
	@docker compose ps backend
	@echo ""
	@echo "Backend health check:"
	@docker compose exec backend curl -f http://localhost:8000/health || echo "Backend is not responding"

# Debug backend startup issues
backend-debug:
	@echo "Debugging backend startup issues..."
	@echo "1. Checking if backend image exists:"
	@docker images | findstr bridge-line-backend || echo "Backend image not found"
	@echo ""
	@echo "2. Checking backend container logs:"
	@docker compose logs --tail=50 backend
	@echo ""
	@echo "3. Checking backend container status:"
	@docker compose ps backend

# Rebuild containers
build:
	@echo "Rebuilding containers..."
	docker compose build
	@echo "Build completed successfully."

# Testing and Quality Assurance
test: test-backend test-frontend
	@echo "✅ All tests completed!"

test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm test -- --coverage --watchAll=false

test-backend-unit:
	@echo "🧪 Running backend unit tests..."
	@cd backend && python -m pytest tests/ -m "unit" -v

test-backend-integration:
	@echo "🧪 Running backend integration tests..."
	@cd backend && python -m pytest tests/ -m "integration" -v

test-frontend-unit:
	@echo "🧪 Running frontend unit tests..."
	@cd frontend && npm test -- --coverage --watchAll=false --testPathPattern="__tests__"

test-e2e:
	@echo "🧪 Running E2E tests..."
	@cd frontend && npm run cypress:run

# Linting and Formatting
lint: lint-backend lint-frontend
	@echo "✅ All linting completed!"

lint-backend:
	@echo "🔍 Linting backend code..."
	@cd backend && python -m flake8 app/ --max-line-length=88 --extend-ignore=E203,W503

lint-frontend:
	@echo "🔍 Linting frontend code..."
	@cd frontend && npm run lint

format: format-backend format-frontend
	@echo "✨ All formatting completed!"

format-backend:
	@echo "✨ Formatting backend code..."
	@cd backend && python -m black app/ --line-length=88
	@cd backend && python -m isort app/ --profile=black

format-frontend:
	@echo "✨ Formatting frontend code..."
	@cd frontend && npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

# Type checking
type-check: type-check-backend type-check-frontend
	@echo "✅ All type checking completed!"

type-check-backend:
	@echo "🔍 Type checking backend code..."
	@cd backend && python -m mypy app/ --ignore-missing-imports

type-check-frontend:
	@echo "🔍 Type checking frontend code..."
	@cd frontend && npm run type-check

# Quality check (lint + format + test)
quality: lint format test
	@echo "🎉 Quality check completed!"

# Quick quality check (lint + format only)
quality-quick: lint format
	@echo "🎉 Quick quality check completed!"

# Run database migrations
migrate:
	@echo "Running database migrations..."
	docker exec bridge_line_backend alembic upgrade head
	@echo "Migrations completed successfully."

# Create new migration
migrate-create:
	@echo "Creating new migration..."
	@read -p "Enter migration name: " name; \
	docker exec bridge_line_backend alembic revision --autogenerate -m "$$name"
	@echo "Migration created successfully."

# Start frontend development server
frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Cleanup
clean:
	@echo "Running cleanup..."
	docker compose down -v
	docker system prune -f
	@echo "Cleanup completed successfully."

# Complete environment reset
reset: clean setup

# Database reset
db-reset:
	@echo "Resetting database..."
	docker compose down -v
	docker compose up -d postgres
	@echo "Database restarted."
	@echo "Please run migrations: make migrate"

# Backend shell access
backend-shell:
	@echo "Accessing backend container shell..."
	docker exec -it bridge_line_backend /bin/bash

# Start backend only
backend-start:
	@echo "Starting backend service only..."
	docker compose up -d backend
	@echo "Backend service started."
	@echo "Access URL: http://localhost:8000"

# Restart backend only
backend-restart:
	@echo "Restarting backend service only..."
	docker compose restart backend
	@echo "Backend service restarted."

# Database shell access
db-shell:
	@echo "Accessing database container shell..."
	docker exec -it bridge_line_postgres psql -U bridge_user -d bridge_line_db

# Check environment variables
env-check:
	@echo "Checking environment variables..."
	@if [ -f "backend/.env" ]; then \
		echo "backend/.env exists."; \
	else \
		echo "backend/.env not found."; \
		if [ -f "backend/.env.example" ]; then \
			echo "Please create .env from backend/.env.example"; \
		fi; \
	fi

# Check dependencies
deps-check:
	@echo "Checking dependencies..."
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Docker Compose: $$(docker compose version 2>/dev/null || echo 'Not installed')"
	@if [ -d "frontend" ]; then \
		echo "Node.js: $$(node --version 2>/dev/null || echo 'Not installed')"; \
		echo "npm: $$(npm --version 2>/dev/null || echo 'Not installed')"; \
	fi 

# Database related commands
db-test-connection:
	docker compose run --rm backend python scripts/test_db_connection.py

db-test-connection-local:
	cd backend && python scripts/test_db_connection.py

db-check-migrations:
	docker compose run --rm backend python scripts/check_migrations.py

db-check-migrations-local:
	cd backend && python scripts/check_migrations.py

db-init:
	docker compose exec postgres psql -U bridge_user -d bridge_line_db -f /docker-entrypoint-initdb.d/init_db.sql

db-init-test:
	docker compose exec postgres psql -U bridge_line_postgres psql -U bridge_user -d postgres -f /docker-entrypoint-initdb.d/init_test_db.sql

db-migrate:
	docker compose exec backend alembic upgrade head

db-migrate-create:
	docker compose exec backend alembic revision --autogenerate -m "$(message)"

db-status:
	docker compose exec backend alembic current

db-history:
	docker compose exec backend alembic current

# Test related commands
test-db:
	cd backend && python -m pytest tests/ -v --tb=short

test-db-unit:
	cd backend && python -m pytest tests/ -v --tb=short -k "not integration"

# Development environment
dev-setup:
	docker compose up -d postgres redis python
	@echo "Waiting for database to start..."
	@$(call wait,10)
	$(MAKE) db-init
	@echo "Running migrations with temporary backend container..."
	docker compose run --rm backend alembic upgrade head
	@echo "Starting development server..."
	docker compose run --rm -p 8000:8000 backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-stop:
	docker compose down

# Cross-platform wait function
define wait
	@$(WAIT_CMD)
endef

# クロスプラットフォーム対応のwait関数
ifeq ($(OS),Windows_NT)
    # Windows用のwait関数（PowerShellを使用）
    define wait
		@powershell -Command "Start-Sleep -Seconds $(1)"
    endef
else
    # Unix系用のwait関数（MacOS、Linux対応）
    define wait
		@sleep $(1)
    endef
endif 