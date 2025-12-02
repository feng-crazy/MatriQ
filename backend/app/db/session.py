from contextlib import contextmanager
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
