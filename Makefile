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
		echo "  docker-compose up --build -d"; \
		echo "  docker exec bridge_line_backend alembic upgrade head"; \
	fi

# Start Docker environment
start:
	@echo "Starting Docker environment..."
	docker-compose up -d
	@echo "Environment started successfully."
	@echo "Access URLs:"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Frontend: http://localhost:3000"

# Stop Docker environment
stop:
	@echo "Stopping Docker environment..."
	docker-compose down
	@echo "Environment stopped successfully."

# Restart Docker environment
restart:
	@echo "Restarting Docker environment..."
	docker-compose restart
	@echo "Environment restarted successfully."

# Show logs
logs:
	@echo "Showing logs..."
	docker-compose logs -f

# Show backend logs
backend:
	@echo "Showing backend logs..."
	docker-compose logs -f backend

# Rebuild containers
build:
	@echo "Rebuilding containers..."
	docker-compose build
	@echo "Build completed successfully."

# Run tests
test:
	@echo "Running tests..."
	docker exec bridge_line_backend pytest
	@echo "Tests completed successfully."

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
	docker-compose down -v
	docker system prune -f
	@echo "Cleanup completed successfully."

# Complete environment reset
reset: clean setup

# Database reset
db-reset:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	@echo "Database restarted."
	@echo "Please run migrations: make migrate"

# Backend shell access
backend-shell:
	@echo "Accessing backend container shell..."
	docker exec -it bridge_line_backend /bin/bash

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
	@echo "Docker Compose: $$(docker-compose --version 2>/dev/null || echo 'Not installed')"
	@if [ -d "frontend" ]; then \
		echo "Node.js: $$(node --version 2>/dev/null || echo 'Not installed')"; \
		echo "npm: $$(npm --version 2>/dev/null || echo 'Not installed')"; \
	fi 

# Database related commands
db-test-connection:
	docker-compose run --rm backend python scripts/test_db_connection.py

db-test-connection-local:
	cd backend && python scripts/test_db_connection.py

db-check-migrations:
	docker-compose run --rm backend python scripts/check_migrations.py

db-check-migrations-local:
	cd backend && python scripts/check_migrations.py

db-init:
	docker-compose exec postgres psql -U bridge_user -d bridge_line_db -f /docker-entrypoint-initdb.d/init_db.sql

db-init-test:
	docker-compose exec postgres psql -U bridge_user -d postgres -f /docker-entrypoint-initdb.d/init_test_db.sql

db-migrate:
	docker-compose exec backend alembic upgrade head

db-migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(message)"

db-status:
	docker-compose exec backend alembic current

db-history:
	docker-compose exec backend alembic history

# Test related commands
test-db:
	cd backend && python -m pytest tests/ -v --tb=short

test-db-unit:
	cd backend && python -m pytest tests/ -v --tb=short -k "not integration"

# Development environment
dev-setup:
	docker-compose up -d postgres redis
	@echo "Waiting for database to start..."
	@$(call wait,10)
	$(MAKE) db-init
	@echo "Running migrations with temporary backend container..."
	docker-compose run --rm backend alembic upgrade head
	@echo "Starting development server..."
	docker-compose run --rm -p 8000:8000 backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-stop:
	docker-compose down

# Cross-platform wait function
define wait
	@$(WAIT_CMD)
endef 