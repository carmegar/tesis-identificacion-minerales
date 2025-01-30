# src/database/models.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, DOUBLE_PRECISION
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .connection import engine

Base = declarative_base()

class Muestra(Base):
    __tablename__ = "muestras"

    id = Column(Integer, primary_key=True, index=True)
    nombre_muestra = Column(String, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    investigador = Column(String, nullable=True)
    ruta_imagen = Column(String, nullable=True)

    # Relación con la tabla de espectros vectorizados
    espectro_vector = relationship("EspectroVectorizado", uselist=False, back_populates="muestra")
    # uselist=False indica que esperamos un único vector por muestra;
    # si quisieras varios vectores por muestra, podrías usar True o un Array de vectores.

class EspectroVectorizado(Base):
    __tablename__ = "espectros_vectorizados"

    id = Column(Integer, primary_key=True, index=True)
    muestra_id = Column(Integer, ForeignKey("muestras.id"))
    # Almacenamos el vector como un ARRAY de doubles
    vector = Column(ARRAY(DOUBLE_PRECISION), nullable=False)

    muestra = relationship("Muestra", back_populates="espectro_vector")
