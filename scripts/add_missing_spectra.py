"""Agrega espectros faltantes de test_data para completar 100."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.docx_parser import extract_and_vectorize_spectrum
from src.database.connection import SessionLocal
from src.database.queries import insert_muestra, insert_espectro, get_all_muestras

# Minerales adicionales de test_data que no están en la BD
MINERALES_ADICIONALES = [
    ("tests/test_data/EDS_CALCITA_001_23ago.docx", "Calcita-Muestra1"),
    ("tests/test_data/EDS_MALAQUITA_001_23ago.docx", "Malaquita"),
    ("tests/test_data/EDS_PIRITA_001_23ago.docx", "Pirita"),
    ("tests/test_data/EDS_BIOTITA_001_12ago.docx", "Biotita-UIS"),
    ("tests/test_data/EDS_EPIDOTA_001_12ago.docx", "Epidota"),
    ("tests/test_data/Eds_goethita_001.docx", "Goethita"),
    ("tests/test_data/Eds-celestina_001.docx", "Celestina"),
]

session = SessionLocal()
count = len(get_all_muestras(session))
print(f"Muestras actuales: {count}")

added = 0
for docx_path, nombre in MINERALES_ADICIONALES:
    if count + added >= 100:
        break

    if not Path(docx_path).exists():
        print(f"[SKIP] {nombre} - archivo no existe")
        continue

    try:
        vector = extract_and_vectorize_spectrum(docx_path)
        if vector is not None:
            muestra = insert_muestra(session, nombre, "UIS-Test", docx_path)
            insert_espectro(session, muestra.id, vector)
            print(f"[OK] {nombre}")
            added += 1
        else:
            print(f"[FAIL] {nombre}")
    except Exception as e:
        print(f"[ERROR] {nombre}: {e}")

session.close()

# Verificar total
session = SessionLocal()
total = len(get_all_muestras(session))
session.close()
print(f"\nTOTAL FINAL: {total} muestras")
