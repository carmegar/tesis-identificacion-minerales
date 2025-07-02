# src/parsers/docx_parser.py

import os
import uuid

import cv2
from docx import Document

from src.analysis.vectorize import vectorize_spectrum


def extract_and_vectorize_spectrum(docx_path, vector_size=200, temp_folder="data/temp_images"):
    """
    1. Extrae todas las imágenes de docx_path y las guarda temporalmente en temp_folder.
    2. Busca la imagen con shape (400, 512, 3) (la de tu espectro).
    3. Vectoriza esa imagen usando vectorize_spectrum.
    4. Borra todas las imágenes extraídas.
    5. Retorna el vector si la encontró, o None si no la halló.

    Requiere:
      - La función vectorize_spectrum en src/analysis/vectorize.py
      - docx y opencv instalados.
    """

    # 1. Abrir el documento .docx
    doc = Document(docx_path)

    # Crear la carpeta temporal si no existe
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    extracted_paths = []

    # 2. Recorrer todas las relaciones para extraer imágenes
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            out_filename = f"docimg_{uuid.uuid4()}.png"
            out_path = os.path.join(temp_folder, out_filename)
            with open(out_path, "wb") as f:
                f.write(rel.target_part.blob)
            extracted_paths.append(out_path)

    # 3. Buscar la imagen con shape (400,512,3)
    chosen_vector = None
    for img_path in extracted_paths:
        img = cv2.imread(img_path)
        if img is not None and img.shape == (400, 512, 3):
            # Vectorizar de inmediato
            chosen_vector = vectorize_spectrum(img_path, vector_size=vector_size)
            # Ya no buscamos más, rompe el bucle
            break

    # 4. Borrar todas las imágenes extraídas
    for img_path in extracted_paths:
        os.remove(img_path)

    # 5. Devolver el vector (None si no encontró la imagen con shape (400,512,3))
    return chosen_vector
