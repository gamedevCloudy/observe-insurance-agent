from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_DB_DIR = Path(__file__).resolve().parent.parent / "data"
_DB_PATH = _DB_DIR / "observe.db"
_DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
