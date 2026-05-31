from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.utils.config import get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()
_engine = create_engine(
    f"sqlite:///{_settings.sqlite_path}",
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from backend.database import models  # noqa: F401  (register tables)

    Base.metadata.create_all(_engine)


def get_session() -> Session:
    return SessionLocal()
