# src/parsers/docx_parser.py
import os
import uuid

from docx import Document


def extract_spectrum_image(docx_path, images_folder="data/images"):
    """
    Lee el archivo .docx, extrae la primera imagen (asumiendo que es el espectro)
    y la guarda en images_folder. Retorna la ruta a la imagen extraída.
    """
    doc = Document(docx_path)

    # Asegurarnos de que la carpeta de imágenes existe
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    extracted_image_path = None
    for shape in doc.inline_shapes:
        rId = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
        image_part = doc.part.related_parts[rId]
        image_bytes = image_part.blob

        new_image_name = f"spectrum_{uuid.uuid4()}.png"
        extracted_image_path = os.path.join(images_folder, new_image_name)

        with open(extracted_image_path, "wb") as f:
            f.write(image_bytes)

        # Solo extraemos la primera imagen
        break

    return extracted_image_path
