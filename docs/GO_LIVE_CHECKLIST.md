# Go Live Checklist (Produccion Unica Ubuntu 22.04)

## 1. Servidor base

- Docker Engine instalado y operativo.
- Docker Compose plugin instalado.
- Usuario de despliegue en grupo docker.
- Firewall activo con puertos necesarios:
  - 80/443 (si hay reverse proxy)
  - 8080 (frontend, si no hay reverse proxy)
  - 8000 (API, solo si debe ser publica)
  - 3000/9090 recomendados solo internos o tunel VPN.

## 2. Secretos y configuracion

- Archivo .env remoto creado manualmente (no sincronizado por CI/CD).
- APP_ENV=prod.
- JWT_SECRET robusto (>=32 chars aleatorio).
- POSTGRES_PASSWORD y GRAFANA_ADMIN_PASSWORD robustos.
- DATABASE_URL valida contra servicio db.

## 3. Migraciones y despliegue

- Preflight correcto:

  ./scripts/preflight_production.sh

- Deploy correcto:

  ./scripts/deploy_production.sh

- Revision Alembic:

  docker compose exec -T api alembic current

## 4. Verificacion postdeploy

- Smoke check OK:

  ./scripts/smoke_check.sh

- API docs disponible.
- Grafana y Prometheus accesibles segun politica de red.

## 5. Backup y recuperacion

- Backup manual probado:

  ./scripts/backup_postgres.sh

- Restore probado en ventana controlada:

  ./scripts/restore_postgres.sh <archivo.sql>

- Retencion aplicada:

  KEEP_COUNT=14 ./scripts/backup_retention.sh

## 6. Operacion continua

- Ejecutar CD manual solo desde main.
- Revisar logs postdeploy:

  docker compose logs --tail=120 api

- Mantener politica de actualizacion mensual de imagenes base.
