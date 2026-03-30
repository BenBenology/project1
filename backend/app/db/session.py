"""SQLAlchemy engine and session management."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings
from backend.app.db.base import Base

settings = get_settings()


def _create_engine():
    """Create the SQLAlchemy engine and ensure the SQLite path exists."""
    database_url = settings.database_url
    if database_url.startswith("sqlite:///"):
        db_path = database_url.removeprefix("sqlite:///")
        resolved_path = Path(db_path)
        if not resolved_path.is_absolute():
            resolved_path = Path.cwd() / resolved_path
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Create database tables for the current backend state."""
    import backend.app.db.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for request-scoped usage if needed later."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
