# Demo Practica para Tutores (15-20 minutos)

Objetivo: demostrar valor funcional y DevOps de extremo a extremo.

## 0. Preparacion previa (antes de la exposicion)

1. Tener servicios levantados en servidor de produccion.
2. Tener una cuenta de prueba preparada o crearla en vivo.
3. Tener navegador con pestañas listas:
   1. Frontend
   2. API docs
   3. Actions
   4. Grafana (opcional)
4. Tener terminal conectada al servidor (o a la VM) para comandos de evidencia.

## 1. Apertura (1-2 minutos)

Mensaje sugerido:

- Este proyecto implementa un Kanban con backend FastAPI y enfoque DevOps.
- Incluye CI, CD manual, migraciones, monitorizacion, backup y smoke checks.

## 2. Estado de plataforma (2 minutos)

Mostrar en terminal:

  docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

Resultado esperado:

- api, db, redis, frontend, prometheus, grafana en running/healthy.

## 3. Flujo funcional end-to-end (7-9 minutos)

### 3.1 Registro y login (RF-1)

- Entrar en API docs.
- Ejecutar register y luego login.
- Copiar token bearer.
- Ejecutar me para confirmar identidad.

### 3.2 Crear proyecto (RF-2)

- Crear proyecto con nombre de demo.
- Listar proyectos y mostrar el recien creado.

### 3.3 Crear y mover tarea (RF-3)

- Crear tarea en TODO.
- Actualizar a IN_PROGRESS.
- Actualizar a DONE.
- Explicar regla de transiciones validas.

### 3.4 Colaboracion (RF-4)

- Crear comentario en tarea.
- Listar comentarios ordenados.
- Editar comentario propio.

### 3.5 Permisos y asignacion (RF-5)

- Crear un segundo usuario.
- Agregar como MEMBER o VIEWER.
- Asignar tarea como OWNER.
- Mostrar que viewer no puede crear tarea.

### 3.6 Estadisticas (RF-6)

- Llamar endpoint de stats del proyecto.
- Mostrar total, todo, in_progress, done y pct_complete.

## 4. Evidencia DevOps (4-5 minutos)

### 4.1 CI en verde

- Mostrar ultima ejecucion en Actions con:
  1. Config Safety Check
  2. Backend Tests
  3. Alembic Migration Check

### 4.2 CD manual en verde

- Mostrar run de Deploy via SSH exitoso.
- Enfatizar etapas:
  1. validate secrets
  2. backup predeploy
  3. deploy prod profile
  4. smoke check

### 4.3 Salud y observabilidad

Mostrar en terminal:

  ./scripts/smoke_check.sh
  docker compose exec -T api alembic current

Resultado esperado:

- Smoke check en OK.
- Alembic en head.

## 5. Backup y recuperacion (2 minutos)

Mostrar:

  ./scripts/backup_postgres.sh
  KEEP_COUNT=14 ./scripts/backup_retention.sh

Explicar:

- Antes de deploy se crea backup automatico.
- Existe script de restore para contingencias.

## 6. Cierre (1 minuto)

Mensaje sugerido:

- El proyecto cumple RF-1 a RF-6 y requisitos operativos clave.
- Se despliega con control y evidencia.
- Se puede mantener con procedimientos claros de operacion.

## 7. Preguntas tipicas de tutores y respuesta corta

1. Por que CD manual y no automatico total
- Por control pedagogico y seguridad en produccion unica.

2. Que pasa si falla un deploy
- Existe backup predeploy y scripts de recuperacion.

3. Como garantizas cambios de esquema
- Alembic gestiona migraciones versionadas.

4. Como pruebas permisos
- Tests de integracion y validaciones por rol.
