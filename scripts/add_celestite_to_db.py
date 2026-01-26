"""
Script para agregar Celestite a la base de datos de entrenamiento.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from src.database.connection import SessionLocal
from src.database.queries import insert_muestra, insert_espectro, get_all_muestras
from src.analysis.vectorize import vectorize_spectrum


def vectorize_image_file(image_path: str, vector_size: int = 200):
    """Vectoriza una imagen JPG de espectro EDS."""
    img = cv2.imread(image_path)
    if img is None:
        return None

    # Ajustar parametros segun el tamano de imagen
    height = img.shape[0]
    ratio = height / 400.0
    row_start = int(150 * ratio)
    row_end = int(250 * ratio)

    return vectorize_spectrum(
        image_path,
        vector_size=vector_size,
        threshold=0.99,
        row_bounds=(row_start, row_end),
        method="mean"
    )


def main():
    print("="*60)
    print("AGREGANDO CELESTITE A LA BASE DE DATOS")
    print("="*60)

    celestite_path = Path("espectros_externos/SFU/EDS_Celestite.jpg")

    if not celestite_path.exists():
        print(f"[ERROR] No se encuentra: {celestite_path}")
        return

    # Verificar si ya existe en BD
    session = SessionLocal()
    muestras = get_all_muestras(session)
    existing_names = [m.nombre_muestra.lower() for m in muestras]

    if "celestite" in existing_names or "celestita" in existing_names or "celestina" in existing_names:
        print("[SKIP] Celestite ya existe en la BD")
        session.close()
        return

    # Vectorizar
    print(f"Procesando: {celestite_path}")
    vector = vectorize_image_file(str(celestite_path))

    if vector is None:
        print("[ERROR] No se pudo vectorizar la imagen")
        session.close()
        return

    print(f"  Vector generado: {len(vector)} dimensiones")

    # Insertar en BD
    muestra = insert_muestra(
        session,
        nombre_muestra="Celestite",
        investigador="SFU",
        ruta_imagen=str(celestite_path)
    )
    insert_espectro(session, muestra.id, vector.tolist())

    print(f"  [OK] Insertado con ID: {muestra.id}")

    # Verificar total
    total = len(get_all_muestras(session))
    print(f"\n{'='*60}")
    print(f"Total de muestras en BD: {total}")
    print("="*60)

    session.close()


if __name__ == "__main__":
    main()
