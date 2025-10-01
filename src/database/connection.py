# src/database/connection.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración de base de datos según el entorno
def get_database_url():
    """Retorna la URL de la base de datos según el entorno."""
    if os.getenv('TESTING'):
        return "sqlite:///:memory:"  # Base de datos en memoria para tests
    return "sqlite:///minerales_eds.db"  # Base de datos normal

DATABASE_URL = get_database_url()

# Configurar echo basado en el entorno (silencioso durante tests)
echo_sql = not bool(os.getenv('TESTING'))

engine = create_engine(DATABASE_URL, echo=echo_sql)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
