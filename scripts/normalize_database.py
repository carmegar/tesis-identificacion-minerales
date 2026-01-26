"""
Script para normalizar nombres de minerales en la base de datos.
Elimina sufijos innecesarios y estandariza la nomenclatura.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.connection import SessionLocal
from src.database.queries import get_all_muestras, update_muestra


# Diccionario de normalizaciones específicas
NORMALIZACIONES = {
    "Calcita-Muestra1": "Calcita",
    "Biotita-UIS": "Biotita",
    "Oxido de hierro": "Óxido de Hierro",
    "Purpurita02": "Purpurita",
    "Mntio3": "MnTiO3",
}


def normalize_name(name: str) -> str:
    """Normaliza el nombre de un mineral."""

    # Primero verificar si hay una normalización específica
    if name in NORMALIZACIONES:
        return NORMALIZACIONES[name]

    # Eliminar sufijos numéricos como -Muestra1, _001, etc.
    # Pero mantener nombres compuestos como GRANATE-ALMANDINO

    # Capitalizar correctamente (Title Case)
    # Excepciones para fórmulas químicas
    if name.upper() == name:  # Si está todo en mayúsculas
        name = name.title()

    return name


def main():
    print("="*60)
    print("NORMALIZANDO NOMBRES EN BASE DE DATOS")
    print("="*60)

    session = SessionLocal()
    muestras = get_all_muestras(session)

    cambios = []

    for muestra in muestras:
        nombre_original = muestra.nombre_muestra
        nombre_normalizado = normalize_name(nombre_original)

        if nombre_original != nombre_normalizado:
            cambios.append((muestra.id, nombre_original, nombre_normalizado))
            update_muestra(session, muestra.id, nombre_muestra=nombre_normalizado)
            print(f"  [{muestra.id}] '{nombre_original}' -> '{nombre_normalizado}'")

    session.close()

    print(f"\n{'='*60}")
    print(f"Normalizaciones realizadas: {len(cambios)}")
    print("="*60)

    return cambios


if __name__ == "__main__":
    main()
