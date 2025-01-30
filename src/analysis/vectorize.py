# src/analysis/vectorize.py
import cv2
import numpy as np


def vectorize_spectrum(image_path, vector_size=200):
    """
    Procesa la imagen del espectro, detecta la línea roja y la convierte en un vector de longitud 'vector_size'.
    Devuelve un numpy array de floats normalizados (rango 0-1 o norma unitaria).
    """
    # 1. Lee la imagen
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"No se pudo leer la imagen en {image_path}")

    # 2. Convertir a espacio HSV (u otro) para aislar color rojo
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Máscara para color rojo (esto es un ejemplo; hay que ajustar rangos)
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 | mask2

    # 3. Queremos proyectar la intensidad horizontalmente para formar un vector
    # Suponiendo que el espectro va de izquierda (0 keV) a derecha (10 keV)
    # Sumamos máscara por filas o columnas, según la orientación
    # Aquí sumamos por columnas (axis=0) para obtener un perfil horizontal
    horizontal_profile = np.sum(mask, axis=0)  # shape -> (width,)

    # 4. Redimensionamos a vector_size usando interpolación
    # (Podríamos usar np.interp o cv2.resize)
    # horizontal_profile es 1D; convertimos a 2D para usar cv2.resize
    hp_2d = np.expand_dims(horizontal_profile, axis=0)  # shape (1, width)
    target_size = (vector_size, 1)  # Queremos 'vector_size' de ancho
    resized = cv2.resize(hp_2d, target_size, interpolation=cv2.INTER_AREA)  # (1, vector_size)

    # Convertimos de nuevo a 1D
    spectrum_vector = resized.flatten().astype(float)

    # 5. Normalizar (norma L2 para que la magnitud total sea 1)
    norm = np.linalg.norm(spectrum_vector)
    if norm == 0:
        # Evitar división por cero
        return np.zeros(vector_size, dtype=float)
    normalized_vector = spectrum_vector / norm

    return normalized_vector
