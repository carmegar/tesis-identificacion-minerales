#!/usr/bin/env python3
"""
Script para poblar la base de datos con todas las muestras EDS
de la carpeta muestrasdatos/Muestras Tesis/
"""

import glob
import os
from pathlib import Path

from src.database.connection import SessionLocal
from src.database.queries import (count_muestras, create_tables,
                                  insert_espectro, insert_muestra)
from src.parsers.docx_parser import extract_and_vectorize_spectrum


def extract_mineral_name(filename):
    """
    Extrae el nombre del mineral del nombre del archivo.
    Ejemplos:
    - "EDS ALBITA_02.docx" -> "ALBITA"
    - "Eds broncita_001.docx" -> "BRONCITA" 
    - "EDS galena.docx" -> "GALENA"
    """
    # Quitar extensión
    name = filename.replace('.docx', '')
    
    # Quitar prefijos comunes
    name = name.replace('EDS ', '')
    name = name.replace('Eds ', '')
    name = name.replace('Element ', '')
    
    # Tomar la primera parte antes de _ o números
    import re
    name = re.split(r'[_\d]', name)[0]
    
    return name.strip().upper()


def populate_database():
    """Procesa todos los archivos DOCX y los agrega a la base de datos."""
    
    # Crear tablas si no existen
    create_tables()
    session = SessionLocal()
    
    # Buscar todos los archivos DOCX en la carpeta de muestras
    muestras_path = "muestrasdatos/Muestras Tesis/*.docx"
    docx_files = glob.glob(muestras_path)
    
    if not docx_files:
        print(f"No se encontraron archivos DOCX en {muestras_path}")
        return
    
    print(f"Encontrados {len(docx_files)} archivos DOCX para procesar...")
    
    success_count = 0
    error_count = 0
    
    for docx_file in docx_files:
        filename = os.path.basename(docx_file)
        mineral_name = extract_mineral_name(filename)
        
        print(f"\nProcesando: {filename}")
        print(f"Mineral identificado: {mineral_name}")
        
        try:
            # Extraer y vectorizar espectro
            vector = extract_and_vectorize_spectrum(docx_file, vector_size=200)
            
            if vector is None:
                print(f"❌ No se encontró espectro válido en {filename}")
                error_count += 1
                continue
            
            # Insertar muestra en la BD
            nueva_muestra = insert_muestra(
                session=session,
                nombre_muestra=mineral_name,
                investigador="Dataset Tesis",
                ruta_imagen=docx_file
            )
            
            # Insertar vector del espectro
            insert_espectro(session, muestra_id=nueva_muestra.id, vector=vector)
            
            print(f"✅ Procesado exitosamente: ID={nueva_muestra.id}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error procesando {filename}: {str(e)}")
            error_count += 1
            continue
    
    # Estadísticas finales
    total_muestras = count_muestras(session)
    print(f"\n=== RESUMEN ===")
    print(f"Archivos procesados exitosamente: {success_count}")
    print(f"Archivos con errores: {error_count}")
    print(f"Total de muestras en la base de datos: {total_muestras}")
    
    session.close()


if __name__ == "__main__":
    populate_database() 