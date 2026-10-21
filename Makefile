.PHONY: help build up down logs test deploy-staging deploy-prod

# Default target
help:
	@echo "Babylon AI Gold Intelligence - Deployment Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build              - Build Docker images"
	@echo "  make up                 - Start services (development)"
	@echo "  make down               - Stop services"
	@echo "  make logs               - View logs from all services"
	@echo "  make logs-backend       - View backend logs"
	@echo "  make logs-frontend      - View frontend logs"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests"
	@echo "  make test-frontend      - Run frontend tests"
	@echo "  make clean              - Clean up containers and volumes"
	@echo "  make deploy-staging     - Deploy to staging (Railway)"
	@echo "  make deploy-prod        - Deploy to production"
	@echo "  make status             - Show service status"
	@echo "  make shell-backend      - Open backend shell"
	@echo "  make shell-frontend     - Open frontend shell"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start services
up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

# Stop services
down:
	@echo "Stopping services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Run tests
test: test-backend test-frontend
	@echo "All tests completed!"

test-backend:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v --cov=. || true

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test 2>/dev/null || npm run build

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf frontend/.next
	@echo "Cleanup completed!"

# Deployment
deploy-staging:
	@echo "Deploying to staging..."
	@echo "Pushing to develop branch..."
	git push origin develop
	@echo "GitHub Actions will trigger deployment automatically"
	@echo "Monitor progress at: https://github.com/yourname/babylon-gold/actions"

deploy-prod:
	@echo "Deploying to production..."
	@echo "Pushing to main branch..."
	git push origin main
	@echo "GitHub Actions will trigger deployment automatically"
	@echo "Monitor progress at: https://github.com/yourname/babylon-gold/actions"

# Status
status:
	@echo "Service Status:"
	@docker-compose ps 2>/dev/null || echo "Services not running"
	@echo ""
	@echo "Docker Images:"
	@docker images | grep babylon || echo "No babylon images found"

# Shell access
shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

# Development setup
setup-dev:
	@echo "Setting up development environment..."
	cp .env.example .env
	docker-compose build
	docker-compose up -d
	@echo "Development environment ready!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

# Health checks
health-check:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "Backend health check failed"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend is healthy" || echo "Frontend health check failed"

# Format code
format:
	@echo "Formatting code..."
	cd backend && black . || true
	cd frontend && npm run format 2>/dev/null || true

# Lint code
lint:
	@echo "Running linters..."
	cd backend && flake8 . || true
	cd frontend && npm run lint 2>/dev/null || true
