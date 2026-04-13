# PR: RF-4 Comentarios + RF-5 Permisos y Roles

## Resumen
Este PR consolida dos bloques funcionales:
- RF-4: comentarios sobre tareas (crear, listar, editar propio, borrar lógico propio).
- RF-5: permisos por rol en proyecto y asignación de tareas.

## Objetivo
Mejorar la colaboración en tareas Kanban con:
- Trazabilidad conversacional en cada tarea.
- Control explícito de acceso y edición según rol y asignación.

## Alcance
### RF-4 Comentarios
- Integración de router de comentarios en la aplicación.
- Creación de modelo Comment para persistencia.
- Creación de esquemas de entrada/salida para comentarios.
- Validaciones básicas de texto y ownership para editar/borrar.

Archivos:
- backend/app/main.py
- backend/app/models/comment.py
- backend/app/routers/comments.py
- backend/app/schemas/comment.py

### RF-5 Permisos y Roles
- Definición de roles de proyecto: OWNER, MEMBER, VIEWER.
- Endpoint para alta/actualización de miembros por OWNER.
- Endpoint para listado de miembros por OWNER.
- Restricciones en tareas:
  - OWNER y MEMBER crean.
  - VIEWER no crea.
  - Solo OWNER asigna.
  - Solo OWNER o usuario asignado edita.
  - Solo OWNER elimina.
- Tests de integración para reglas RF-5.

Archivos:
- backend/app/routers/projects.py
- backend/app/routers/tasks.py
- backend/app/schemas/project.py
- backend/app/schemas/task.py
- backend/tests/integration/test_permissions_rf5.py

## Cambios Fuera De Alcance
- No incluye CI/CD.
- No incluye migraciones Alembic.
- No incluye cambios de frontend.

## Riesgos y Mitigaciones
- Riesgo: discrepancia entre comportamiento esperado y códigos HTTP en no autorizados.
- Mitigación: tests de integración para casos owner/member/viewer y edición por asignado.

- Riesgo: caída de API por imports incompletos al registrar nuevos routers.
- Mitigación: integración completa modelo/esquema/router en el mismo bloque RF-4.

## Validación Realizada
- Arranque estable de servicios con Docker Compose.
- Verificación de rama remota publicada:
  - feature/rf4-rf5-estabilizacion
- Suite de pruebas existente mantenida y test RF-5 agregado.

## Checklist Técnico
- [x] Código compilable en contenedor API.
- [x] Router de comentarios registrado en app.
- [x] Modelo y esquema de comentarios presentes.
- [x] Roles OWNER/MEMBER/VIEWER aplicados en rutas de tareas.
- [x] Endpoint de asignación de tarea restringido a OWNER.
- [x] Test de permisos RF-5 agregado.
- [x] Commits separados por funcionalidad.
- [x] Rama remota publicada y trackeada.

## Commits
- feat(rf4): integrar comentarios en app y crear modelo/esquema
- feat(rf5): roles de proyecto y permisos de asignacion de tareas

## Plan De Rollback
- Revertir commit RF-5 si se detecta regresión en permisos.
- Revertir commit RF-4 si se detecta incidencia en comentarios.
- Mantener rollback granular por commits separados.

## Evidencia Sugerida Para Reviewer
- Capturas de endpoints en /docs:
  - /api/projects/{project_id}/tasks/{task_id}/comments
  - /api/projects/{project_id}/members
  - /api/projects/{project_id}/tasks/{task_id}/assign
- Resultado de pruebas de integración relevantes.

## Notas Para Merge
- Recomendado: squash merge por bloque RF-4/RF-5 solo si se conserva trazabilidad en descripción.
- Si se requiere bisect fino, mantener merge commit con ambos commits visibles.
