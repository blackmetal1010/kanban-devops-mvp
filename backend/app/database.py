from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis connection — lazy; errors surface only on actual use
try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=2)
except Exception:
    redis_client = None  # type: ignore[assignment]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
