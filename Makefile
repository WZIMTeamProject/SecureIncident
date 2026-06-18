COMPOSE_LOCAL = docker-compose.local.yml
COMPOSE_PROD  = docker-compose.yml

# --- local dev ---

up:
	docker-compose -f $(COMPOSE_LOCAL) up --build

down:
	docker-compose -f $(COMPOSE_LOCAL) down

logs:
	docker-compose -f $(COMPOSE_LOCAL) logs -f

ps:
	docker-compose -f $(COMPOSE_LOCAL) ps

db:
	docker-compose -f $(COMPOSE_LOCAL) up -d db

# --- production (remote server) ---

prod-up:
	docker-compose -f $(COMPOSE_PROD) pull
	docker-compose -f $(COMPOSE_PROD) up -d

prod-down:
	docker-compose -f $(COMPOSE_PROD) down

prod-logs:
	docker-compose -f $(COMPOSE_PROD) logs -f

.PHONY: up down logs ps db prod-up prod-down prod-logs
