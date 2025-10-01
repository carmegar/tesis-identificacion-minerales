# src/database/queries.py
import json

import numpy as np
from sqlalchemy.orm import Session

from .connection import SessionLocal, engine
from .models import Base, EspectroVectorizado, Muestra


def create_tables():
    Base.metadata.create_all(bind=engine)

def insert_muestra(session: Session, nombre_muestra: str, investigador: str = None, ruta_imagen: str = None):
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
    e = EspectroVectorizado(muestra_id=muestra_id)
    e.vector = vector  # Usa el setter que convierte a JSON
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

def count_muestras(session: Session):
    """Retorna el número total de muestras en la base de datos."""
    return session.query(Muestra).count()

def get_all_muestras_with_vectors(session: Session):
    """Retorna todas las muestras que tienen vectores asociados."""
    return session.query(Muestra).join(EspectroVectorizado).all()

def update_muestra(session: Session, muestra_id: int, nombre_muestra: str = None, investigador: str = None):
    """Actualiza los campos de una muestra existente."""
    muestra = session.query(Muestra).filter(Muestra.id == muestra_id).first()
    if not muestra:
        return None
    
    if nombre_muestra is not None:
        muestra.nombre_muestra = nombre_muestra
    if investigador is not None:
        muestra.investigador = investigador
    
    session.commit()
    session.refresh(muestra)
    return muestra

def delete_muestra(session: Session, muestra_id: int):
    """Elimina una muestra y su espectro asociado de la base de datos."""
    # Primero eliminar el espectro asociado
    espectro = session.query(EspectroVectorizado).filter_by(muestra_id=muestra_id).first()
    if espectro:
        session.delete(espectro)
    
    # Luego eliminar la muestra
    muestra = session.query(Muestra).filter(Muestra.id == muestra_id).first()
    if muestra:
        session.delete(muestra)
        session.commit()
        return True
    return False
