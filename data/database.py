# data/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Замени postgres:postgres на свой логин и пароль от PostgreSQL, если они отличаются
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/readability_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Зависимость для получения сессии БД в контроллерах FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()