from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging
from typing import Generator
from app.utils.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection():
    try:
        db = SessionLocal()
        # b.close()
        print("Database connected successfully...🚀")
    except OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        raise Exception(f"Database connection failed: {e}")