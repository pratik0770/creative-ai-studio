"""Initialize database schema. Run once on first deploy or via `python database/init_db.py`."""

from database.connection import get_engine
from database.models import Base
from cloud.logging_config import get_logger, setup_logging

log = get_logger(__name__)


def init_db() -> None:
    setup_logging()
    engine = get_engine()
    log.info("Creating database tables…")
    Base.metadata.create_all(bind=engine)
    log.info("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
