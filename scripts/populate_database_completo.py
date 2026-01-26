"""
Script para poblar la base de datos con espectros EDS de múltiples fuentes.
Soporta:
- Imágenes JPG directas (SFU)
- Archivos DOCX (muestras originales)
"""

import os
import sys
import re
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.vectorize import vectorize_spectrum
from src.parsers.docx_parser import extract_and_vectorize_spectrum
from src.database.connection import SessionLocal
from src.database.queries import create_tables, insert_muestra, insert_espectro, get_all_muestras


def extract_mineral_name(filename: str) -> str:
    """Extrae el nombre del mineral del nombre del archivo."""
    # Quitar extensión
    name = Path(filename).stem

    # Patrones comunes
    # EDS_Galena.jpg -> Galena
    # EDS galena.docx -> Galena
    # Eds_magnetita.docx -> Magnetita

    # Quitar prefijos comunes
    prefixes = ['EDS_', 'EDS ', 'Eds_', 'Eds ', 'Element ', 'MUESTRA-', 'MUESTRA ']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Quitar sufijos numéricos como _001, _02, etc.
    name = re.sub(r'[_-]\d+$', '', name)
    name = re.sub(r'_\d+ago$', '', name)  # Para nombres como _23ago

    # Capitalizar primera letra
    name = name.strip().title()

    return name


def vectorize_image_file(image_path: str, vector_size: int = 200):
    """
    Vectoriza una imagen JPG directamente.
    Ajusta row_bounds según el tamaño de la imagen.
    """
    import cv2

    img = cv2.imread(image_path)
    if img is None:
        return None

    height = img.shape[0]

    # Ajustar row_bounds proporcionalmente
    # Original: (150, 250) para imagen de 400px de alto
    # SFU: ~404px de alto
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


def process_jpg_files(folder: str, session, source: str = "SFU"):
    """Procesa archivos JPG de una carpeta."""
    processed = 0
    failed = []

    jpg_files = list(Path(folder).glob("*.jpg"))
    print(f"\nProcesando {len(jpg_files)} archivos JPG de {source}...")

    for jpg_path in jpg_files:
        mineral_name = extract_mineral_name(jpg_path.name)

        try:
            vector = vectorize_image_file(str(jpg_path))

            if vector is not None:
                muestra = insert_muestra(
                    session,
                    nombre_muestra=mineral_name,
                    investigador=source,
                    ruta_imagen=str(jpg_path)
                )
                insert_espectro(session, muestra.id, vector)
                print(f"  [OK] {mineral_name}")
                processed += 1
            else:
                print(f"  [FAIL] {mineral_name} - No se pudo vectorizar")
                failed.append(mineral_name)
        except Exception as e:
            print(f"  [ERROR] {mineral_name}: {e}")
            failed.append(mineral_name)

    return processed, failed


def process_docx_files(folder: str, session, source: str = "UIS"):
    """Procesa archivos DOCX de una carpeta."""
    processed = 0
    failed = []

    docx_files = list(Path(folder).glob("*.docx"))
    print(f"\nProcesando {len(docx_files)} archivos DOCX de {source}...")

    for docx_path in docx_files:
        mineral_name = extract_mineral_name(docx_path.name)

        try:
            vector = extract_and_vectorize_spectrum(str(docx_path))

            if vector is not None:
                muestra = insert_muestra(
                    session,
                    nombre_muestra=mineral_name,
                    investigador=source,
                    ruta_imagen=str(docx_path)
                )
                insert_espectro(session, muestra.id, vector)
                print(f"  [OK] {mineral_name}")
                processed += 1
            else:
                print(f"  [SKIP] {mineral_name} - Sin imagen válida")
                failed.append(mineral_name)
        except Exception as e:
            print(f"  [ERROR] {mineral_name}: {e}")
            failed.append(mineral_name)

    return processed, failed


def main():
    """Función principal para poblar la base de datos."""

    print("="*60)
    print("POBLANDO BASE DE DATOS CON ESPECTROS EDS")
    print("="*60)

    # Crear tablas si no existen
    create_tables()

    # Crear sesión
    session = SessionLocal()

    # Verificar estado actual
    muestras_existentes = get_all_muestras(session)
    print(f"\nMuestras existentes en BD: {len(muestras_existentes)}")

    # Si ya hay muestras, preguntar si limpiar
    if len(muestras_existentes) > 0:
        print("\nLa BD ya tiene muestras. Se agregarán las nuevas sin duplicar.")
        existing_names = {m.nombre_muestra.lower() for m in muestras_existentes}
    else:
        existing_names = set()

    total_processed = 0
    total_failed = []

    # 1. Procesar espectros de SFU (JPG)
    sfu_folder = "espectros_externos/SFU"
    if Path(sfu_folder).exists():
        proc, fail = process_jpg_files(sfu_folder, session, source="SFU")
        total_processed += proc
        total_failed.extend(fail)

    # 2. Procesar espectros originales (DOCX)
    original_folder = "muestrasdatos/Muestras Tesis"
    if Path(original_folder).exists():
        proc, fail = process_docx_files(original_folder, session, source="UIS-Guatiguara")
        total_processed += proc
        total_failed.extend(fail)

    # 3. Procesar espectros adicionales de data/
    data_folder = "data"
    if Path(data_folder).exists():
        docx_in_data = list(Path(data_folder).glob("*.docx"))
        if docx_in_data:
            proc, fail = process_docx_files(data_folder, session, source="UIS-Guatiguara")
            total_processed += proc
            total_failed.extend(fail)

    session.close()

    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE POBLACIÓN")
    print("="*60)
    print(f"Espectros procesados exitosamente: {total_processed}")
    print(f"Espectros fallidos: {len(total_failed)}")

    if total_failed:
        print(f"\nFallidos: {', '.join(total_failed[:10])}")
        if len(total_failed) > 10:
            print(f"  ... y {len(total_failed) - 10} más")

    # Verificar total en BD
    session = SessionLocal()
    total_final = len(get_all_muestras(session))
    session.close()

    print(f"\nTOTAL EN BASE DE DATOS: {total_final} espectros")

    return total_processed


if __name__ == "__main__":
    main()
