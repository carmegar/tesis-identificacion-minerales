# src/main.py

from src.analysis.compare import compare_spectrum
from src.database.connection import SessionLocal
from src.database.queries import (count_muestras, create_tables,
                                  insert_espectro, insert_muestra)
from src.parsers.docx_parser import extract_and_vectorize_spectrum


def main():
    # Crear tablas si no existen
    create_tables()
    session = SessionLocal()

    docx_file = "data/Eds_magnetita.docx"  # Ajusta la ruta a tu archivo real

    # 1. Extraer y vectorizar la imagen con shape (400,512,3)
    vector = extract_and_vectorize_spectrum(docx_file, vector_size=200)

    if vector is None:
        print("No se encontró ninguna imagen con shape (400,512,3) en el documento.")
        return

    # 2. Insertar una muestra en la BD (ejemplo)
    nueva_muestra = insert_muestra(
        session=session,
        nombre_muestra="Magnetita - Muestra de Prueba",
        investigador="Sistema de Prueba"
    )

    # 3. Asociar el vector en la tabla espectros_vectorizados
    insert_espectro(session, muestra_id=nueva_muestra.id, vector=vector)
    print(f"Muestra '{nueva_muestra.nombre_muestra}' guardada con ID={nueva_muestra.id}")

    # 4. Mostrar estadísticas
    total_muestras = count_muestras(session)
    print(f"Total de muestras en la base de datos: {total_muestras}")

    # 5. Comparar contra otras muestras (si existen)
    if total_muestras > 1:
        resultados = compare_spectrum(session, nueva_muestra.id, similitud_umbral=0.5)
        if resultados:
            print("Resultados de comparación (umbral=0.5):")
            for (mid, nombre, sim) in resultados:
                print(f"  - MuestraID={mid} ({nombre}): similitud={sim:.2f}")
        else:
            print("No hay otras muestras con espectro o ninguna supera el umbral de similitud.")
    else:
        print("Esta es la primera muestra en la base de datos.")

    session.close()

if __name__ == "__main__":
    main()
