# Kanban DevOps MVP

A production-ready Kanban board application built with modern DevOps practices.

```
┌─────────────────────────────────────────────────────────────┐
│                     Architecture                            │
│                                                             │
│  Browser ──▶ Nginx (port 80)                                │
│               ├── /         → Frontend (HTML/CSS/JS)        │
│               └── /api/*    → FastAPI Backend (port 8000)   │
│                                   ├── PostgreSQL 15          │
│                                   └── Redis 7                │
│                                                             │
│  Monitoring:  Prometheus (9090) ──▶ Grafana (3000)          │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Backend API    | FastAPI (Python 3.11) + JWT auth  |
| Database       | PostgreSQL 15                     |
| Cache          | Redis 7                           |
| Frontend       | Pure HTML5 / CSS3 / Vanilla JS    |
| Reverse Proxy  | Nginx                             |
| Containers     | Docker + Docker Compose           |
| CI/CD          | GitLab CI/CD                      |
| Monitoring     | Prometheus + Grafana              |
| Automation     | Ansible playbooks                 |

## Quick Start

### Prerequisites
- Docker >= 24 and Docker Compose v2
- (Optional) Python 3.11+ for local development

### 1. Clone and configure

```bash
git clone <repo-url>
cd kanban-devops-mvp
cp .env.example .env
# Edit .env — at minimum, set SECRET_KEY and POSTGRES_PASSWORD
```

### 2. Start the application

```bash
docker compose up -d
```

The app will be available at **http://localhost**.

### 3. (Optional) Start monitoring

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin123)

## API Documentation

With the backend running, visit:
- **Swagger UI**: http://localhost/api/docs
- **ReDoc**: http://localhost/api/redoc

### Key endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/token | Login (get JWT) |
| POST | /api/auth/register | Register new user |
| GET | /api/auth/me | Current user info |
| GET/POST | /api/projects/ | List / create projects |
| GET/PUT/DELETE | /api/projects/{id} | Get / update / delete project |
| GET/POST | /api/tasks/ | List / create tasks |
| GET/PUT/DELETE | /api/tasks/{id} | Get / update / delete task |

## Local Development

```bash
cd backend
pip install -r requirements.txt
# Start postgres + redis via docker compose
docker compose up db redis -d
# Run backend
uvicorn app.main:app --reload --port 8000
```

### Running Tests

```bash
cd backend
pytest app/tests/ -v
```

## Project Structure

```
.
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── main.py     # App entrypoint
│   │   ├── config.py   # Settings (pydantic-settings)
│   │   ├── models/     # SQLAlchemy ORM models
│   │   ├── schemas/    # Pydantic request/response schemas
│   │   ├── routers/    # API route handlers
│   │   ├── core/       # Security & dependencies
│   │   └── tests/      # pytest test suite
│   └── alembic/        # Database migrations
├── frontend/           # Static HTML/CSS/JS Kanban board
├── nginx/              # Nginx reverse proxy config
├── monitoring/         # Prometheus + Grafana configs
├── ansible/            # Deployment automation playbooks
├── scripts/            # backup.sh, restore.sh, healthcheck.sh
├── docker-compose.yml
└── docker-compose.monitoring.yml
```

## Deployment (Ansible)

```bash
# 1. Edit ansible/inventory/hosts.ini with your server details
# 2. Run setup (first time only)
ansible-playbook ansible/playbooks/setup.yml
# 3. Deploy
ansible-playbook ansible/playbooks/deploy.yml
```

## Backup & Restore

```bash
# Create backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backups/kanban_backup_20240101_120000.tar.gz

# Health check
./scripts/healthcheck.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Run tests: `cd backend && pytest app/tests/ -v`
4. Commit and push
5. Open a Pull Request

## License

MIT
