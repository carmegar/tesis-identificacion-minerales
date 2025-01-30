# src/main.py

import os

from src.analysis.compare import compare_spectrum
from src.analysis.vectorize import vectorize_spectrum
from src.database.connection import SessionLocal
from src.database.queries import create_tables, insert_espectro, insert_muestra
from src.parsers.docx_parser import extract_spectrum_image


def main():
    # 1. Crear tablas
    create_tables()

    # 2. Iniciar sesión en BD
    session = SessionLocal()

    # 3. EJEMPLO: Cargar un .docx, extraer imagen, vectorizar y guardar
    docx_file = "data\Eds magnetita.docx"  # Ajusta la ruta a tu archivo .docx
    if not os.path.exists(docx_file):
        print(f"Archivo {docx_file} no existe. Por favor, coloca un ejemplo válido.")
        return

    # a) Extraer la imagen del espectro
    spectrum_img_path = extract_spectrum_image(docx_file, images_folder="data/images")
    if not spectrum_img_path:
        print("No se encontró ninguna imagen en el .docx")
        return

    # b) Crear la muestra en la BD
    nueva_muestra = insert_muestra(
        session=session,
        nombre_muestra="Magnetita",
        investigador="Carlos Meza",
        ruta_imagen=spectrum_img_path
    )

    # c) Vectorizar la imagen
    vector = vectorize_spectrum(spectrum_img_path, vector_size=200)

    # d) Guardar el vector en la BD
    insert_espectro(session=session, muestra_id=nueva_muestra.id, vector=vector)

    print(f"Muestra '{nueva_muestra.nombre_muestra}' almacenada con ID={nueva_muestra.id}")

    # 4. EJEMPLO: Comparar esa muestra contra las demás
    # (si no hay otras muestras, obviamente no habrá resultados)
    resultados = compare_spectrum(session, muestra_id=nueva_muestra.id, similitud_umbral=0.5)
    if resultados:
        print("Resultados de comparación:")
        for (mid, nombre, sim) in resultados:
            print(f"  - MuestraID={mid} ({nombre}): similitud={sim:.2f}")
    else:
        print("No hay otras muestras o ninguna supera el umbral de similitud.")

    session.close()

if __name__ == "__main__":
    main()
