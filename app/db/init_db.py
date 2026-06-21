from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
        print("Database initialized and seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
