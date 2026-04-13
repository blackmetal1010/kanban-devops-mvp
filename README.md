# Kanban DevOps MVP

Base funcional del proyecto Kanban con enfoque DevOps para Ubuntu Server 22.04.

## Servicios incluidos

- FastAPI (API)
- PostgreSQL 15
- Redis 7
- Frontend estatico con Nginx
- Prometheus
- Grafana

## Requisitos

- Docker Engine
- Docker Compose Plugin

## Arranque rapido

1. Verifica la configuracion de Compose:

	docker compose config

2. Levanta todos los servicios:

	docker compose up -d --build

3. Comprueba estado:

	docker compose ps

## URLs

- Frontend: http://localhost:8080
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Credenciales iniciales

- Grafana user: admin
- Grafana pass: definida en .env (GRAFANA_ADMIN_PASSWORD)

## Siguientes pasos recomendados

- Implementar autenticacion JWT y modelos SQLAlchemy.
- Crear migraciones con Alembic.
- Añadir endpoints RF-1 a RF-6.
- Integrar tests y pipeline CI/CD en GitLab.
 
