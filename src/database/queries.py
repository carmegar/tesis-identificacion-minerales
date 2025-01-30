# src/database/queries.py
from sqlalchemy.orm import Session

from .connection import SessionLocal, engine
from .models import Base, EspectroVectorizado, Muestra


def create_tables():
    Base.metadata.create_all(bind=engine)

def insert_muestra(session: Session, nombre_muestra: str, investigador: str, ruta_imagen: str):
    nueva = Muestra(
        nombre_muestra=nombre_muestra,
        investigador=investigador,
        ruta_imagen=ruta_imagen
    )
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    return nueva

def insert_espectro(session: Session, muestra_id: int, vector):
    """
    Crea un EspectroVectorizado asociado a la muestra y retorna el objeto.
    'vector' debe ser una lista (o np.array) con floats normalizados.
    """
    e = EspectroVectorizado(
        muestra_id=muestra_id,
        vector=vector
    )
    session.add(e)
    session.commit()
    session.refresh(e)
    return e

def get_all_muestras(session: Session):
    return session.query(Muestra).all()

def get_muestra_by_id(session: Session, muestra_id: int):
    return session.query(Muestra).filter(Muestra.id == muestra_id).first()

def get_espectro_by_muestra_id(session: Session, muestra_id: int):
    return session.query(EspectroVectorizado).filter_by(muestra_id=muestra_id).first()
