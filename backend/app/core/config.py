from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    APP_VERSION: str = "0.1.0"

    POSTGRES_DB: str = "kanban_db"
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "change_me"
    DATABASE_URL: str = "postgresql+psycopg://app_user:change_me@db:5432/kanban_db"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()