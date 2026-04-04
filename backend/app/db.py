"""
Database connection and session management for PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL") or \
    f"postgresql://{os.getenv('POSTGRES_USER', 'malware_user')}:{os.getenv('POSTGRES_PASSWORD', 'malware_pass')}@{os.getenv('POSTGRES_HOST', 'db')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'malware_db')}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
