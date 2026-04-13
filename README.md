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

- Frontend: <http://localhost:8080>
- API docs: <http://localhost:8000/docs>
- API health: <http://localhost:8000/health>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>

## Credenciales iniciales

- Grafana user: admin
- Grafana pass: definida en .env (GRAFANA_ADMIN_PASSWORD)

## Siguientes pasos recomendados

- Crear migraciones con Alembic para entornos persistentes.
- Añadir endpoint de burndown historico (RF-6 extension opcional).
- Integrar despliegue automatico tras CI (CD) en servidor objetivo.
- Añadir backup verificado y restore drill documentado.

## Estado funcional backend

- RF-1: autenticacion y sesion JWT.
- RF-2: CRUD de proyectos.
- RF-3: CRUD de tareas y flujo TODO/IN_PROGRESS/DONE.
- RF-4: comentarios en tareas (plain text, soft-delete).
- RF-5: roles y permisos de asignacion (OWNER/MEMBER/VIEWER).
- RF-6: endpoint de estadisticas por proyecto.

## Integracion continua

- Workflow GitHub Actions: `.github/workflows/ci.yml`
- Ejecuta tests del backend en push y pull request contra main.
 