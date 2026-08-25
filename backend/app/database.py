"""
Database setup.

Uses SQLite locally (zero-config, file-based) and Postgres in production
via the DATABASE_URL env var (set automatically by Render/Railway).
Swapping engines requires no code changes elsewhere — that's the point
of going through SQLAlchemy's engine/session abstraction.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backtester.db")

# SQLite needs this flag for use with FastAPI's multi-threaded request handling.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, always closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
