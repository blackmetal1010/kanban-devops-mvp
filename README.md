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

1. Levanta todos los servicios:

 docker compose up -d --build

1. Comprueba estado:

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
- Incluye job adicional de migraciones: `alembic upgrade/downgrade/upgrade` sobre PostgreSQL real.

## Entrega continua (CD manual)

- Workflow de despliegue: `.github/workflows/cd-manual.yml`
- Trigger: manual (`workflow_dispatch`) y solo desde rama `main`.
- Escenario objetivo: servidor unico Ubuntu Server 22.04 (produccion unica).
- Estrategia: sincroniza codigo por SSH al servidor, crea backup predeploy de PostgreSQL y ejecuta `docker compose up -d --build`.
- Nota de seguridad: el workflow excluye `.env` en `rsync` para no sobreescribir secretos remotos.
- Validacion postdeploy: ejecuta `./scripts/smoke_check.sh` remoto (servicios, health, version, docs, metrics).

Secrets requeridos en GitHub:

- `DEPLOY_SSH_KEY`: clave privada SSH del usuario de despliegue.
- `DEPLOY_HOST`: host/IP del servidor Ubuntu.
- `DEPLOY_USER`: usuario SSH remoto.
- `DEPLOY_PATH`: ruta absoluta del proyecto en el servidor remoto.

## Backup y restauracion (produccion)

Scripts incluidos:

- `scripts/backup_postgres.sh`: genera backup SQL en `backups/manual/`.
- `scripts/restore_postgres.sh <ruta_backup.sql>`: restaura backup SQL en la BD activa.
- `scripts/smoke_check.sh`: valida estado de servicios y endpoints clave tras despliegue.

Uso recomendado:

1. Crear backup manual antes de cambios grandes:

 ./scripts/backup_postgres.sh

1. Restaurar en caso de rollback de datos:

 ./scripts/restore_postgres.sh backups/manual/postgres_YYYYmmdd_HHMMSS.sql

## Migraciones de base de datos (Alembic)

La API aplica migraciones al iniciar el contenedor (`alembic upgrade head`).

Comandos utiles:

1. Ejecutar migraciones manualmente:

 docker compose exec -T api alembic upgrade head

1. Ver revision actual:

 docker compose exec -T api alembic current

1. Crear una nueva migracion (cuando cambie el modelo):

 docker compose exec -T api alembic revision --autogenerate -m "descripcion_cambio"

1. Probar downgrade controlado:

 docker compose exec -T api alembic downgrade -1
