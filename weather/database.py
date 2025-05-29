# weather/database.py

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ———————— Configuration ————————
# Read the database URL from an environment variable, with a sensible default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./weather.db"
)

# Enable SQL echo for debugging if specified
ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("1", "true", "yes")

logger = logging.getLogger(__name__)
logger.debug("Using DATABASE_URL=%s (echo=%s)", DATABASE_URL, ECHO_SQL)

# Create the engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=ECHO_SQL,
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for our models
Base = declarative_base()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Call this once at application startup.
    """
    logger.info("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete.")


def get_db():
    """
    FastAPI dependency that yields a database session and
    ensures it’s closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
