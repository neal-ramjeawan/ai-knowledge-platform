.PHONY: up down logs migrate api-shell db-shell ps

up:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker exec -i ai_knowledge_db psql -U ai_user -d ai_knowledge < backend/migrations/001_initial_schema.sql

api-shell:
	docker exec -it ai_knowledge_api sh

db-shell:
	docker exec -it ai_knowledge_db psql -U ai_user -d ai_knowledge

ps:
	docker-compose ps