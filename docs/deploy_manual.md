# Manual de despliegue a producción

## 1. Workflow utilizado

- GitHub Actions → workflow: **CD Manual Deploy**  
- Rama permitida: **`main`** (solo se despliega código ya fusionado en producción).

## 2. Secrets necesarios

El workflow requiere estos secrets configurados en el repositorio de GitHub:

- `DEPLOY_SSH_KEY`: clave privada del usuario SSH que despliega en el servidor.
- `DEPLOY_HOST`: IP o nombre DNS del servidor de producción.
- `DEPLOY_USER`: usuario SSH remoto con permisos para ejecutar Docker.
- `DEPLOY_PATH`: ruta absoluta del proyecto en el servidor (por ejemplo `/home/rad/Desktop/Proyecto_Devops/DespliegueAplicación/kanban-devops-mvp`).

Sin estos cuatro valores definidos el despliegue fallará en las primeras etapas de validación.

## 3. Qué hace el workflow (resumen técnico)

Cuando se ejecuta **CD Manual Deploy** sobre `main`, las etapas principales son:

1. **Checkout**  
   Descarga el código de la rama `main` en el runner de GitHub.

2. **Validación de secrets**  
   Comprueba que `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_USER` y `DEPLOY_PATH` están definidos y no vacíos.  
   Si falta alguno, el job se detiene antes de tocar el servidor.

3. **Configuración de SSH**  
   - Carga la clave privada en un agente SSH.  
   - Prepara el acceso sin contraseña al servidor indicado en `DEPLOY_HOST` con el usuario `DEPLOY_USER`.

4. **Sincronización de código (rsync)**  
   - Copia el código del repositorio al directorio `DEPLOY_PATH` del servidor.  
   - Excluye explícitamente `.git`, `__pycache__`, `.pytest_cache` y `.env`.

5. **Backup predeploy**  
   - Ejecuta en el servidor un `pg_dump` antes del despliegue y guarda el resultado en `backups/deploy/predeploy_<timestamp>.sql`.

6. **`preflight_production.sh`**  
   Lanza un preflight remoto que verifica:
   - que existe `.env` con variables necesarias,
   - que `APP_ENV=prod` está configurado,
   - que los archivos `docker-compose.yml` y `docker-compose.prod.yml` son válidos.

7. **`docker compose up -d --build`**  
   En el servidor, dentro de `DEPLOY_PATH`, ejecuta:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

   Esto:
   - construye de nuevo las imágenes necesarias,
   - recrea los servicios si hay cambios,
   - levanta todo el stack en segundo plano con el perfil de producción.

8. **`smoke_check.sh`**

   El workflow ejecuta el script `./scripts/smoke_check.sh` en el servidor para validar el estado del despliegue.
   Este script:

    - Comprueba que los servicios `api`, `db`, `redis`, `frontend`, `prometheus` y `grafana` están en estado `running` mediante `docker compose ps`;

        - Realiza peticiones HTTP a la API:
        - `/health`
        - `/version`
        - `/docs`
        - `/metrics`

    - Si alguna de estas comprobaciones falla, el script termina con código distinto de 0 y el job de GitHub Actions marca el despliegue como fallido.  

    - El script evita falsos negativos durante el arranque

        `El problema principal suele ser que fallaba demasiado pronto aunque la API acabe levantandose bien.`

    - Tiene reintentos

9. **Política de retención de backups**  
   Tras un despliegue correcto, se ejecuta el script de retención que elimina backups antiguos según la política definida (por ejemplo mantener solo los últimos N días). Así se evita llenar el disco del servidor con copias obsoletas.

## 4. Puertos finales del entorno de producción

Con el perfil de producción (`docker-compose.yml` + `docker-compose.prod.yml`), la exposición queda así:

- **API (FastAPI)**  
  - Host: `0.0.0.0`  
  - Puerto: `8000`  
  - Uso: consumo interno y pruebas desde el servidor (p.ej. `curl http://localhost:8000/health`).

- **Frontend (Nginx)**  
  - Host: `0.0.0.0`  
  - Puerto externo: `8080` → puerto `80` del contenedor.
  - Uso: entrada principal de usuarios al Kanban.

- **Prometheus**  
  - Host: `127.0.0.1` (solo accesible desde el propio servidor)  
  - Puerto externo: `9091` → `9090` dentro del contenedor.
  - Uso: interfaz de Prometheus (`/targets`, `/graph`) para métricas y debugging.

- **Grafana**  
  - Host: `127.0.0.1` (solo accesible desde el propio servidor)  
  - Puerto externo: `3001` → `3000` dentro del contenedor.
  - Uso: visualización de dashboards de monitorización.

- En el perfil de producción, PostgreSQL y Redis no se exponen al exterior; su acceso queda limitado a la red interna de Docker.

## 5. Estado esperado tras el deploy

Comprobar estado del stack:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

Comprobar API:

```bash
curl http://localhost:8000/health 
```

Comprobar Prometheus:

```bash
curl http://127.0.0.1:9091/-/healthy
```

Comprobar Grafana:

```bash
curl -I http://127.0.0.1:3001/login
```

- Se puede acceder al frontend en http://<DEPLOY_HOST>:8080 y usar el Kanban con normalidad;

- En Prometheus todos los targets relevantes están UP y en Grafana se visualizan los dashboards configurados.

## 6. Problemas frecuentes

Con cosas que suelen fallar en despliegues manuales:

- `APP_ENV` distinto de `prod`
- valores placeholder en `.env`
- contraseña de PostgreSQL desalineada con el volumen existente
- conflicto de puertos en Prometheus/Grafana
- smoke check demasiado temprano
