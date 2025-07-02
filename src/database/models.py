# src/database/models.py
import json

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        func)
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

class EspectroVectorizado(Base):
    __tablename__ = "espectros_vectorizados"

    id = Column(Integer, primary_key=True, index=True)
    muestra_id = Column(Integer, ForeignKey("muestras.id"))
    # Almacenamos el vector como JSON string (compatible con SQLite)
    vector_json = Column(Text, nullable=False)

    muestra = relationship("Muestra", back_populates="espectro_vector")

    @property
    def vector(self):
        """Convierte el JSON string de vuelta a lista de números."""
        return json.loads(self.vector_json)

    @vector.setter
    def vector(self, value):
        """Convierte la lista/array de números a JSON string."""
        import numpy as np
        if isinstance(value, np.ndarray):
            value = value.tolist()
        self.vector_json = json.dumps(value)
