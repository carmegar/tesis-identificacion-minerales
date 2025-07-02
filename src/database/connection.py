# src/database/connection.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración para SQLite (más simple para MVP)
DATABASE_URL = "sqlite:///minerales_eds.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
