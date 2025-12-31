DOCKER_COMPOSE:=docker-compose
SERVICE_NAME:=app

up:
	$(DOCKER_COMPOSE) up -d
.PHONY: up

down:
	$(DOCKER_COMPOSE) down
.PHONY: down

bash:
	$(DOCKER_COMPOSE) exec $(SERVICE_NAME) bash
.PHONY: bash
