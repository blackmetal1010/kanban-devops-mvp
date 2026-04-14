# Plantilla de Presentacion (10-12 Slides)

Uso recomendado: 12-15 minutos de presentacion + 5 minutos de preguntas.

## Slide 1. Portada

Titulo sugerido:

- Kanban DevOps MVP: Desarrollo, Despliegue y Operacion en Produccion Unica

Contenido:

- Nombre completo
- Centro educativo
- Modulo / curso
- Tutor/a
- Fecha

Objetivo del slide:

- Presentar el alcance del proyecto de forma profesional y clara.

## Slide 2. Problema y objetivo

Contenido:

- Problema: gestion manual de tareas sin automatizacion ni trazabilidad operativa.
- Objetivo: construir una aplicacion Kanban con flujo DevOps completo.
- Resultado esperado: CI + CD manual, observabilidad, backups y seguridad basica.

Objetivo del slide:

- Dejar claro que no es solo una app, sino un sistema operable.

## Slide 3. Arquitectura de la solucion

Contenido:

- Frontend (Nginx)
- API FastAPI
- PostgreSQL
- Redis
- Prometheus
- Grafana
- GitHub Actions (CI/CD)

Visual sugerido:

- Diagrama de bloques con flechas de comunicacion.

Evidencia a mostrar:

- Estado de servicios desde terminal:

  docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

## Slide 4. Requisitos funcionales (RF-1 a RF-6)

Contenido:

- RF-1: autenticacion JWT
- RF-2: proyectos
- RF-3: tareas y estados
- RF-4: comentarios
- RF-5: roles y permisos
- RF-6: estadisticas

Objetivo del slide:

- Mostrar cobertura funcional completa del proyecto.

## Slide 5. Demo funcional (parte 1)

Contenido demo en vivo:

- Registro + login + me
- Crear proyecto
- Crear tarea
- Cambiar estado TODO -> IN_PROGRESS -> DONE

Evidencia:

- Mostrar ejecucion desde API docs.

Mensaje clave:

- El flujo principal de negocio funciona extremo a extremo.

## Slide 6. Demo funcional (parte 2)

Contenido demo en vivo:

- Crear comentario en tarea
- Agregar miembro con rol
- Asignar tarea como owner
- Probar restriccion de permisos (viewer no crea)

Evidencia:

- Endpoint de stats RF-6 con conteos y porcentaje.

Mensaje clave:

- El sistema aplica control de acceso real por rol.

## Slide 7. Calidad y testing

Contenido:

- Pruebas de integracion para RF principales.
- CI en GitHub Actions con checks:
  - Config Safety Check
  - Backend Tests
  - Alembic Migration Check

Evidencia a mostrar:

- Captura de run en verde en Actions.

## Slide 8. Despliegue a produccion unica

Contenido:

- CD Manual Deploy ejecutado desde main.
- Runner self-hosted en red local.
- Preflight de produccion + backup predeploy.
- Smoke check postdeploy.

Evidencia a mostrar:

- Log de CD en verde.

Mensaje clave:

- El despliegue esta controlado, validado y repetible.

## Slide 9. Migraciones y datos

Contenido:

- Alembic como control de esquema versionado.
- Upgrade automatico en arranque API.
- Verificacion de revision en head.

Evidencia:

  docker compose exec -T api alembic current

Mensaje clave:

- Evitas drift de esquema y despliegues inconsistentes.

## Slide 10. Observabilidad y operacion

Contenido:

- Endpoint /metrics disponible.
- Prometheus para scraping.
- Grafana para dashboards.
- Logs y salud operativa.

Evidencia:

  ./scripts/smoke_check.sh

Mensaje clave:

- El sistema no solo corre, tambien se puede monitorear.

## Slide 11. Backup, recuperacion y seguridad

Contenido:

- Backup manual y predeploy automatizado.
- Retencion de backups.
- Restore documentado.
- Secretos en GitHub Actions.
- .env no sincronizado por CD.

Evidencia:

  ./scripts/backup_postgres.sh
  KEEP_COUNT=14 ./scripts/backup_retention.sh

Mensaje clave:

- Hay estrategia operativa ante fallos.

## Slide 12. Conclusiones y mejoras futuras

Contenido:

- Objetivos cumplidos: RF-1 a RF-6 + pipeline DevOps.
- Valor educativo: ciclo completo desarrollo-despliegue-operacion.
- Mejoras futuras realistas:
  - HTTPS con reverse proxy
  - alertas avanzadas
  - hardening adicional de imagenes

Cierre sugerido:

- Proyecto listo para operar en produccion unica de forma controlada.

---

## Guion de tiempo sugerido

- Slide 1-2: 2 minutos
- Slide 3-4: 2 minutos
- Slide 5-6 (demo funcional): 4 minutos
- Slide 7-9: 3 minutos
- Slide 10-11: 2 minutos
- Slide 12: 1 minuto

Total: 14 minutos aprox.

## Material de apoyo recomendado

- Checklist de evidencias: docs/MEMORIA_DEFENSA_CHECKLIST.md
- Guia de demo: docs/DEMO_PRACTICA_TUTORES.md
- Checklist go-live: docs/GO_LIVE_CHECKLIST.md
- Guia de despliegue: docs/deploy_manual.md

## Preguntas tipicas del tribunal y respuesta corta

1. Por que CD manual y no automatico total
- Para mantener control de cambios en produccion unica y reducir riesgo de despliegues no supervisados.

2. Que pasa si un despliegue falla
- Existe backup predeploy, smoke check y scripts de recuperacion.

3. Como garantizas coherencia de base de datos
- Alembic versiona y aplica migraciones de forma controlada.

4. Como validas permisos
- Mediante pruebas de integracion y reglas por rol en API.
