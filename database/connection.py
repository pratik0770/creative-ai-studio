from __future__ import annotations

import threading
from typing import Optional

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings
from cloud.logging_config import get_logger

log = get_logger(__name__)

_engine: Optional[sqlalchemy.Engine] = None
_SessionLocal: Optional[sessionmaker] = None
_lock = threading.Lock()


def _build_engine() -> sqlalchemy.Engine:
    """Build the SQLAlchemy engine.

    Priority:
      1. Cloud SQL Python Connector  (production, CLOUD_SQL_INSTANCE set)
      2. Direct PostgreSQL URL        (DB_HOST set, or explicit DB_URL)
      3. SQLite fallback              (DEBUG=true, no DB configured — dev only)
    """
    # ── 1. Production: Cloud SQL connector ────────────────────────────────────
    if settings.CLOUD_SQL_INSTANCE and not settings.DEBUG:
        try:
            from google.cloud.sql.connector import Connector, IPTypes

            connector = Connector()

            def _getconn():
                return connector.connect(
                    settings.CLOUD_SQL_INSTANCE,
                    "pg8000",
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    db=settings.DB_NAME,
                    ip_type=IPTypes.PUBLIC,
                )

            engine = create_engine(
                "postgresql+pg8000://",
                creator=_getconn,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800,
            )
            log.info("Connected via Cloud SQL Python Connector")
            return engine
        except Exception as exc:
            log.error("Cloud SQL connector failed, falling back: %s", exc)

    # ── 2. Explicit DB_URL override or PostgreSQL host ─────────────────────────
    explicit_url = settings.DB_URL
    if explicit_url:
        engine = create_engine(explicit_url, pool_size=5, max_overflow=2,
                               pool_timeout=30, pool_recycle=1800)
        log.info("Connected via DB_URL override")
        return engine

    if settings.DB_HOST and settings.DB_HOST not in ("", "localhost") or (
        settings.DB_HOST == "localhost" and not settings.DEBUG
    ):
        url = settings.database_url
        engine = create_engine(url, pool_size=5, max_overflow=2,
                               pool_timeout=30, pool_recycle=1800)
        log.info("Connected to PostgreSQL at %s:%s/%s",
                 settings.DB_HOST, settings.DB_PORT, settings.DB_NAME)
        return engine

    # ── 3. SQLite fallback (local dev only) ────────────────────────────────────
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dev.db")
    url = f"sqlite:///{db_path}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    log.warning("Using SQLite dev database at %s (NOT for production)", db_path)
    return engine


def get_engine() -> sqlalchemy.Engine:
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                _engine = _build_engine()
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal()


def check_connection() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        log.error("DB connection check failed: %s", exc)
        return False
