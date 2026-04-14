# Checklist de Evidencias para Memoria y Defensa

## 1. Evidencias de arquitectura

1. Diagrama de componentes (frontend, api, db, redis, prometheus, grafana).
2. Explicacion de red interna docker y puertos expuestos en produccion.
3. Justificacion de produccion unica en Ubuntu 22.04.
4. Captura de docker compose ps con todos los servicios en running.

Comandos de evidencia:

  docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

## 2. Evidencias de funcionalidad RF-1 a RF-6

1. RF-1 autenticacion: registro, login y endpoint me.
2. RF-2 proyectos: crear y listar proyectos.
3. RF-3 tareas: crear y mover TODO -> IN_PROGRESS -> DONE.
4. RF-4 comentarios: crear, listar y borrar logico.
5. RF-5 permisos: owner asigna, viewer no crea tareas.
6. RF-6 estadisticas: endpoint de stats por proyecto.

Recomendacion:

- Guardar capturas de respuestas de API docs y/o terminal curl.
- Guardar una traza temporal de IDs (usuario, proyecto, tarea) para explicar la demo.

## 3. Evidencias de calidad de software

1. Pipeline CI en verde en main.
2. Jobs clave aprobados:
   1. Config Safety Check
   2. Backend Tests (Python 3.11)
   3. Alembic Migration Check (PostgreSQL)
3. Evidencia de pruebas de integracion.

## 4. Evidencias de despliegue

1. Ejecucion correcta de CD Manual Deploy (check verde).
2. Validacion preflight con APP_ENV=prod.
3. Backup predeploy generado en backups/deploy.
4. Smoke check final en OK.
5. Retencion de backups ejecutada.

## 5. Evidencias de datos y migraciones

1. Revision de Alembic en head.
2. Script de arranque aplicando migraciones en startup.
3. Evidencia de no usar create_all en produccion.

Comando de evidencia:

  docker compose exec -T api alembic current

## 6. Evidencias de observabilidad

1. Endpoint metrics operativo.
2. Prometheus healthy.
3. Grafana accesible y dashboards cargados.
4. Explicacion de por que grafana/prometheus van limitados a localhost en prod.

## 7. Evidencias de backup y recuperacion

1. Backup manual ejecutado correctamente.
2. Politica de retencion aplicada.
3. Restore probado en ventana de prueba y resultado documentado.

Comandos de evidencia:

  ./scripts/backup_postgres.sh
  KEEP_COUNT=14 ./scripts/backup_retention.sh
  ./scripts/restore_postgres.sh <archivo.sql>

## 8. Evidencias de seguridad

1. Secretos en GitHub Actions configurados (sin exponer valores).
2. .env no sincronizado por CI/CD.
3. Puertos db y redis no expuestos en prod.
4. APP_ENV=prod validado por preflight.
5. JWT_SECRET y contrasenas robustas.

## 9. Evidencias para anexos de memoria

1. Enlace a PR principal y commits relevantes.
2. Capturas de Actions (CI y CD).
3. Capturas de API docs y smoke check.
4. Capturas de estado final de servicios.
5. Capturas de dashboard Grafana y targets Prometheus.

## 10. Cierre para tribunal

1. Que problema resuelve el proyecto.
2. Que mejora aporta frente a despliegue manual tradicional.
3. Riesgos detectados y mitigaciones aplicadas.
4. Limites actuales y siguientes mejoras realistas.
