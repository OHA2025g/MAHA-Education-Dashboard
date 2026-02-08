.PHONY: help build up down restart logs clean backup restore

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

logs-mongodb: ## View MongoDB logs
	docker-compose logs -f mongodb

ps: ## Show running containers
	docker-compose ps

clean: ## Stop services and remove volumes (⚠️ deletes data)
	docker-compose down -v

clean-all: clean ## Stop services, remove volumes and images
	docker-compose down -v --rmi all

rebuild: ## Rebuild and restart all services
	docker-compose up -d --build

backup: ## Backup MongoDB data
	@echo "Creating MongoDB backup..."
	docker-compose exec -T mongodb mongodump --archive > backup_$(shell date +%Y%m%d_%H%M%S).archive
	@echo "Backup created: backup_$(shell date +%Y%m%d_%H%M%S).archive"

restore: ## Restore MongoDB from backup (usage: make restore BACKUP=backup_file.archive)
	@if [ -z "$(BACKUP)" ]; then \
		echo "Error: Please specify BACKUP file. Usage: make restore BACKUP=backup_file.archive"; \
		exit 1; \
	fi
	@echo "Restoring from $(BACKUP)..."
	cat $(BACKUP) | docker-compose exec -T mongodb mongorestore --archive
	@echo "Restore completed"

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-mongodb: ## Open MongoDB shell
	docker-compose exec mongodb mongosh

status: ## Check health status of all services
	docker-compose ps
	@echo ""
	@echo "Health checks:"
	@docker-compose exec -T backend curl -s http://localhost:8002/api/health || echo "Backend: Unhealthy"
	@docker-compose exec -T frontend wget -q -O- http://localhost/health || echo "Frontend: Unhealthy"

