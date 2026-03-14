from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии базы данных.
    Yields:
        Session: Сессия SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()