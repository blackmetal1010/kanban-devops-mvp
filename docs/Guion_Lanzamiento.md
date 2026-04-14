# Despliegue de la aplicación en producción

En esta sección se detallan los pasos para desplegar la aplicación en un entorno de producción, incluyendo la configuración de servicios, verificación del estado y solución de problemas comunes.

## PASO 1: Preparación del entorno

Ejecutar terminal command:  

```bash
ls -la
```

1. Ir a la carpeta correcta del proyecto

```bash
cd /home/rad/Desktop/Proyecto_Devops/DespliegueAplicación/kanban-devops-mvp
```

1. Comprobaciones previas (una vez por sesión)

```bash
sudo docker --version
sudo docker compose version
sudo docker info >/dev/null && echo "Docker OK"
```

Si sale error de permisos con Docker:

- Cierra sesión y vuelve a entrar, o Ejecuta: newgrp docker

1. Arranque para pruebas normales (dev/local)

3.1 Validar configuración:

```bash
sudo docker compose config >/dev/null && echo "Compose OK"
```

3.2 Levantar todos los servicios definidos:

```bash
sudo docker compose up -d --build
```

3.3 Ver estado:

```bash
sudo docker compose ps
```

1. Verificar que todo está vivo
4.1 Smoke test del proyecto:

```bash
sudo ./smoke_check.sh
```

4.2 Endpoints útiles:

- Frontend: <http://localhost:8080>
- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

Importante y real de tu compose actual:

- En docker-compose.yml, Prometheus y Grafana no publican puertos al host.
- Si quieres acceder desde host a monitorización, usa el perfil de producción (paso 5), que sí publica:
  - Prometheus en 127.0.0.1:9091
  - Grafana en 127.0.0.1:3001

1. Arranque con perfil de producción (para pruebas de despliegue)
5.1 Preflight obligatorio:

```bash
sudo ./preflight_production.sh
```

Este script exige que en .env:

- APP_ENV=prod
- No haya valores de ejemplo/dev.

5.2 Levantar stack producción:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

5.3 Verificar:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

```bash
sudo ./smoke_check.sh
```

1. Flujo integral de despliegue (recomendado para tareas de operación)
Ya lo tienes automatizado en deploy_production.sh. Ejecuta:

```bash
sudo ./deploy_production.sh
```

```bash
deploy_production.sh
```

Ese script hace:

- preflight
- backup de PostgreSQL
- up -d --build con compose + prod
- smoke check
- retención de backups

1. Comandos de operación diaria

Ver logs API:

```bash
sudo docker compose logs -f --tail=120 api
```

Parar servicios (sin borrar datos):

```bash
sudo docker compose stop
```

Parar y borrar contenedores/red (manteniendo volúmenes):

```bash
sudo docker compose down
```

Parar y borrar también volúmenes (borra datos de BD y Grafana):

```bash
sudo docker compose down -v
```

Si quieres, te preparo el mismo flujo en formato “copiar y pegar” para:

1. modo desarrollo diario, o
2. modo defensa/demo (con checks finales), según el escenario que vayas a usar ahora.
