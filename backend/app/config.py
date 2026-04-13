from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Kanban DevOps MVP"
    debug: bool = False
    database_url: str = "postgresql://kanban_user:password@db:5432/kanban_db"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "changeme-please-use-a-real-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allowed_origins: List[str] = ["http://localhost", "http://localhost:80"]

    class Config:
        env_file = ".env"


settings = Settings()
