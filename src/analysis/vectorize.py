import cv2
import numpy as np


def read_image_float(image_path):
    """Lee una imagen y la convierte a formato float normalizado."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    if len(img.shape) == 2 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img.astype(np.float32) / 255.0
    return img


def preprocess_image(img):
    """Aplica filtro Gaussiano para suavizar la imagen."""
    return cv2.GaussianBlur(img, (5, 5), 0)


def convert_to_grayscale(img):
    """Convierte imagen a escala de grises."""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def extract_mask(gray, threshold=0.99):
    """Crea máscara binaria basada en umbralización."""
    mask = (gray < threshold).astype(np.uint8) * 255
    return mask


def crop_mask(mask, row_bounds=None):
    """Recorta la máscara a la región de interés."""
    # Recorte horizontal
    col_sum = np.sum(mask, axis=0)
    nonzero_cols = np.where(col_sum > 0)[0]
    if nonzero_cols.size == 0:
        col_start, col_end = 0, mask.shape[1]
    else:
        col_start = nonzero_cols[0]
        col_end = nonzero_cols[-1] + 1

    # Recorte vertical: usa row_bounds si se proporciona
    if row_bounds is not None:
        row_start, row_end = row_bounds
    else:
        row_sum = np.sum(mask, axis=1)
        nonzero_rows = np.where(row_sum > 0)[0]
        if nonzero_rows.size == 0:
            row_start, row_end = 0, mask.shape[0]
        else:
            row_start = nonzero_rows[0]
            row_end = nonzero_rows[-1] + 1

    mask_cropped = mask[row_start:row_end, col_start:col_end]
    return mask_cropped, row_start, row_end, col_start, col_end


def compute_signature(mask_cropped, method="mean"):
    """Calcula la firma del espectro."""
    if method == "max":
        signature = np.max(mask_cropped, axis=0)
    else:
        signature = np.mean(mask_cropped, axis=0)
    return signature


def resize_signature(signature, vector_size=200):
    """Redimensiona la firma a un vector de tamaño fijo."""
    if signature.size == 0:
        return None
    x_old = np.arange(signature.size)
    x_new = np.linspace(0, signature.size - 1, vector_size)
    resized = np.interp(x_new, x_old, signature)
    return resized.astype(np.float32)


def normalize_vector(vec):
    """Normaliza el vector usando norma L2."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        return None
    normalized = vec / norm
    return normalized


def vectorize_spectrum(image_path, vector_size=200, threshold=0.99, row_bounds=(150,250), method="mean"):
    """
    Pipeline completo de vectorización de espectros EDS.
    
    Args:
        image_path: Ruta a la imagen del espectro
        vector_size: Tamaño final del vector (default: 200)
        threshold: Umbral para binarización (default: 0.99)
        row_bounds: Límites de filas para recorte (default: (150,250))
        method: Método de cálculo de firma ("mean" o "max")
    
    Returns:
        numpy.array: Vector normalizado del espectro o None si falla
    """
    # Pipeline de procesamiento
    img = read_image_float(image_path)
    if img is None:
        return None
        
    img = preprocess_image(img)
    gray = convert_to_grayscale(img)
    mask = extract_mask(gray, threshold=threshold)
    mask_cropped, r_st, r_ed, c_st, c_ed = crop_mask(mask, row_bounds=row_bounds)
    signature = compute_signature(mask_cropped, method=method)
    resized_sig = resize_signature(signature, vector_size=vector_size)
    
    if resized_sig is None:
        return None
        
    normalized_sig = normalize_vector(resized_sig)
    return normalized_sig
