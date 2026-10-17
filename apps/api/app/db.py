"""SQLAlchemy 2 database setup; SQLite is the safe local default."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", os.getenv("AGENTSCOPE_DATABASE_URL", "sqlite:///./agentscope.db"))
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Startup remains usable without a separate migration command. Alembic remains the
    # authoritative schema upgrade path for deployments.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
