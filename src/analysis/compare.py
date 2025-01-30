# src/analysis/compare.py
import numpy as np
from sqlalchemy.orm import Session

from src.database.models import EspectroVectorizado, Muestra


def calcular_similitud(vector1, vector2):
    """
    Retorna la similitud usando producto punto / norma (similaridad de coseno).
    """
    dot = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def compare_spectrum(session: Session, muestra_id: int, similitud_umbral=0.5):
    """
    Compara la muestra (muestra_id) contra todas las demás en la BD.
    Retorna una lista de (muestra_id, nombre_muestra, similitud) en orden descendente.
    """
    # 1. Obtener el vector de la muestra base
    base_espectro = session.query(EspectroVectorizado).filter_by(muestra_id=muestra_id).first()
    if not base_espectro:
        raise ValueError(f"La muestra con id={muestra_id} no tiene espectro almacenado.")

    base_vector = base_espectro.vector

    # 2. Cargar todas las otras muestras con sus vectores
    otras = session.query(EspectroVectorizado).filter(EspectroVectorizado.muestra_id != muestra_id).all()

    resultados = []
    for o in otras:
        sim = calcular_similitud(base_vector, o.vector)
        # Recuperamos el nombre de la muestra
        nombre = o.muestra.nombre_muestra
        resultados.append((o.muestra_id, nombre, sim))

    # 3. Ordenar por similitud
    resultados.sort(key=lambda x: x[2], reverse=True)

    # 4. Opcional: filtrar solo las que superen un cierto umbral
    resultados_filtrados = [r for r in resultados if r[2] >= similitud_umbral]

    return resultados_filtrados
