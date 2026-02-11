.PHONY: help build up down restart logs clean backup restore prod

COMPOSE_FILE = docker-compose.yml
COMPOSE = docker compose -f $(COMPOSE_FILE)

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	$(COMPOSE) build

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

restart: ## Restart all services
	$(COMPOSE) restart

logs: ## View logs from all services
	$(COMPOSE) logs -f

logs-backend: ## View backend logs
	$(COMPOSE) logs -f backend

logs-frontend: ## View frontend logs
	$(COMPOSE) logs -f frontend

logs-mongodb: ## View MongoDB logs
	$(COMPOSE) logs -f mongodb

ps: ## Show running containers
	$(COMPOSE) ps

clean: ## Stop services and remove volumes (⚠️ deletes data)
	$(COMPOSE) down -v

clean-all: clean ## Stop services, remove volumes and images
	$(COMPOSE) down -v --rmi all

rebuild: ## Rebuild and restart all services
	$(COMPOSE) up -d --build

backup: ## Backup MongoDB data
	@echo "Creating MongoDB backup..."
	$(COMPOSE) exec -T mongodb mongodump --archive > backup_$(shell date +%Y%m%d_%H%M%S).archive
	@echo "Backup created: backup_$(shell date +%Y%m%d_%H%M%S).archive"

restore: ## Restore MongoDB from backup (usage: make restore BACKUP=backup_file.archive)
	@if [ -z "$(BACKUP)" ]; then \
		echo "Error: Please specify BACKUP file. Usage: make restore BACKUP=backup_file.archive"; \
		exit 1; \
	fi
	@echo "Restoring from $(BACKUP)..."
	cat $(BACKUP) | $(COMPOSE) exec -T mongodb mongorestore --archive
	@echo "Restore completed"

shell-backend: ## Open shell in backend container
	$(COMPOSE) exec backend /bin/bash

shell-mongodb: ## Open MongoDB shell
	$(COMPOSE) exec mongodb mongosh

status: ## Check health status of all services
	$(COMPOSE) ps
	@echo ""
	@echo "Health checks:"
	@$(COMPOSE) exec -T backend curl -s http://localhost:8002/api/health || echo "Backend: Unhealthy"
	@$(COMPOSE) exec -T frontend wget -q -O- http://localhost/health || echo "Frontend: Unhealthy"

# Production targets
prod-build: COMPOSE_FILE = docker-compose.prod.yml
prod-build: ## Build production images
	$(COMPOSE) build

prod-up: COMPOSE_FILE = docker-compose.prod.yml
prod-up: ## Start production services
	$(COMPOSE) up -d

prod-down: COMPOSE_FILE = docker-compose.prod.yml
prod-down: ## Stop production services
	$(COMPOSE) down

prod-restart: COMPOSE_FILE = docker-compose.prod.yml
prod-restart: ## Restart production services
	$(COMPOSE) restart

prod-logs: COMPOSE_FILE = docker-compose.prod.yml
prod-logs: ## View production logs
	$(COMPOSE) logs -f

prod-rebuild: COMPOSE_FILE = docker-compose.prod.yml
prod-rebuild: ## Rebuild and restart production services
	$(COMPOSE) up -d --build

test: ## Run backend tests
	$(COMPOSE) exec backend pytest

test-coverage: ## Run tests with coverage
	$(COMPOSE) exec backend pytest --cov=. --cov-report=html
