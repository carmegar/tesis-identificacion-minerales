"""
Genera imagenes individuales de cada paso del pipeline de procesamiento.
Usa un espectro real de Pirita para demostrar cada transformacion.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import cv2
import os

OUTPUT_DIR = "diagramas/pipeline_pasos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Espectro de ejemplo (Pirita - tiene picos claros de Fe y S)
SPECTRUM_PATH = "espectros_externos/SFU/EDS_Pyrite.jpg"


def create_step_figure(step_num, title, description, main_content_func, extra_info=None):
    """Crea una figura estandarizada para cada paso."""
    fig = plt.figure(figsize=(12, 8))

    # Colores segun tipo de paso
    colors = {
        0: '#3498DB',   # Entrada - Azul
        1: '#27AE60',   # Procesamiento - Verde
        2: '#27AE60',
        3: '#9B59B6',   # Transformacion - Purpura
        4: '#9B59B6',
        5: '#9B59B6',
        6: '#9B59B6',
        7: '#9B59B6',
        8: '#9B59B6',
        9: '#9B59B6',
        10: '#E74C3C',  # Salida - Rojo
    }

    color = colors.get(step_num, '#7F8C8D')

    # Titulo superior
    fig.text(0.5, 0.95, f'Paso {step_num}: {title}', fontsize=18, fontweight='bold',
             ha='center', va='center', color=color)
    fig.text(0.5, 0.90, description, fontsize=11, ha='center', va='center',
             color='#7F8C8D', style='italic')

    # Area principal para el contenido
    ax_main = fig.add_axes([0.08, 0.12, 0.84, 0.72])

    # Ejecutar la funcion de contenido
    main_content_func(ax_main, fig)

    # Info extra en la parte inferior
    if extra_info:
        fig.text(0.5, 0.04, extra_info, fontsize=10, ha='center', va='center',
                 color='#2C3E50', family='monospace',
                 bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#BDC3C7'))

    return fig


def paso_0_entrada(ax, fig):
    """Paso 0: Entrada del sistema."""
    ax.axis('off')

    # Simular icono de archivo DOCX
    docx_box = FancyBboxPatch((0.3, 0.3), 0.4, 0.5, boxstyle="round,pad=0.02",
                               facecolor='#2B579A', edgecolor='#1E3F66', linewidth=3,
                               transform=ax.transAxes)
    ax.add_patch(docx_box)

    # Texto DOCX
    ax.text(0.5, 0.65, 'DOCX', fontsize=28, fontweight='bold', ha='center', va='center',
            color='white', transform=ax.transAxes)
    ax.text(0.5, 0.5, 'Archivo del\nMicroscopio', fontsize=14, ha='center', va='center',
            color='#B8D4E8', transform=ax.transAxes)
    ax.text(0.5, 0.35, 'EDS_Pyrite.docx', fontsize=11, ha='center', va='center',
            color='#7FB3D5', transform=ax.transAxes, family='monospace')

    # Contenido del DOCX
    ax.text(0.5, 0.15, 'Contiene: Imagen del espectro EDS embebida', fontsize=10,
            ha='center', va='center', color='#5D6D7E', transform=ax.transAxes)


def paso_1_extraccion(ax, fig):
    """Paso 1: Extraccion de imagen del DOCX."""
    # Cargar imagen
    img = cv2.imread(SPECTRUM_PATH)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    ax.imshow(img_rgb)
    ax.set_title('Imagen extraida del documento DOCX', fontsize=12, pad=10)
    ax.axis('off')

    # Agregar dimensiones
    h, w = img.shape[:2]
    ax.text(0.02, 0.02, f'Dimensiones: {w} x {h} x 3 (RGB)', fontsize=10,
            transform=ax.transAxes, color='white',
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))


def paso_2_lectura(ax, fig):
    """Paso 2: Lectura como float normalizado."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_rgb = cv2.cvtColor(img_float, cv2.COLOR_BGR2RGB)

    ax.imshow(img_rgb)
    ax.set_title('Imagen convertida a float32 normalizado (0.0 - 1.0)', fontsize=12, pad=10)
    ax.axis('off')

    # Mostrar rango de valores
    ax.text(0.02, 0.02, f'Rango: [{img_float.min():.2f}, {img_float.max():.2f}]', fontsize=10,
            transform=ax.transAxes, color='white',
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))


def paso_3_filtrado(ax, fig):
    """Paso 3: Filtro Gaussiano."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0

    # Aplicar filtro Gaussiano
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)

    # Mostrar antes y despues
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.25, 0.4, 0.55])
    ax2 = fig.add_axes([0.52, 0.25, 0.4, 0.55])

    ax1.imshow(cv2.cvtColor(img_float, cv2.COLOR_BGR2RGB))
    ax1.set_title('Antes (con ruido)', fontsize=11, fontweight='bold')
    ax1.axis('off')

    ax2.imshow(cv2.cvtColor(img_filtered, cv2.COLOR_BGR2RGB))
    ax2.set_title('Despues (suavizado)', fontsize=11, fontweight='bold')
    ax2.axis('off')

    # Flecha
    fig.text(0.5, 0.52, '→', fontsize=30, ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.45, 'Kernel\n5x5', fontsize=9, ha='center', va='center', color='#7F8C8D')


def paso_4_escala_gris(ax, fig):
    """Paso 4: Conversion a escala de grises."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)

    # Convertir a escala de grises
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)

    # Mostrar antes y despues
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.25, 0.4, 0.55])
    ax2 = fig.add_axes([0.52, 0.25, 0.4, 0.55])

    ax1.imshow(cv2.cvtColor(img_filtered, cv2.COLOR_BGR2RGB))
    ax1.set_title('Color (3 canales BGR)', fontsize=11, fontweight='bold')
    ax1.axis('off')

    ax2.imshow(img_gray, cmap='gray')
    ax2.set_title('Escala de grises (1 canal)', fontsize=11, fontweight='bold')
    ax2.axis('off')

    # Info
    fig.text(0.5, 0.52, '→', fontsize=30, ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.45, 'BGR2GRAY', fontsize=9, ha='center', va='center',
             color='#7F8C8D', family='monospace')


def paso_5_binarizacion(ax, fig):
    """Paso 5: Binarizacion."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)

    # Crear mascara binaria
    threshold = 0.99
    mask = (img_gray < threshold).astype(np.float32) * 255

    # Mostrar antes y despues
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.25, 0.4, 0.55])
    ax2 = fig.add_axes([0.52, 0.25, 0.4, 0.55])

    ax1.imshow(img_gray, cmap='gray')
    ax1.set_title('Escala de grises', fontsize=11, fontweight='bold')
    ax1.axis('off')

    ax2.imshow(mask, cmap='gray')
    ax2.set_title('Mascara binaria', fontsize=11, fontweight='bold')
    ax2.axis('off')

    # Info
    fig.text(0.5, 0.52, '→', fontsize=30, ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.45, 'umbral\n< 0.99', fontsize=9, ha='center', va='center', color='#7F8C8D')


def paso_6_recorte(ax, fig):
    """Paso 6: Recorte de region de interes."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)
    mask = (img_gray < 0.99).astype(np.float32) * 255

    # Recortar ROI
    row_bounds = (150, 250)
    col_sum = np.sum(mask, axis=0)
    cols_with_data = np.where(col_sum > 0)[0]

    if len(cols_with_data) > 0:
        col_start, col_end = cols_with_data[0], cols_with_data[-1]
    else:
        col_start, col_end = 0, mask.shape[1]

    mask_cropped = mask[row_bounds[0]:row_bounds[1], col_start:col_end]

    # Mostrar antes y despues
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.25, 0.4, 0.55])
    ax2 = fig.add_axes([0.52, 0.25, 0.4, 0.55])

    # Mostrar mascara con rectangulo de ROI
    ax1.imshow(mask, cmap='gray')
    rect = plt.Rectangle((col_start, row_bounds[0]), col_end-col_start, row_bounds[1]-row_bounds[0],
                          fill=False, edgecolor='red', linewidth=2)
    ax1.add_patch(rect)
    ax1.set_title('Mascara completa + ROI', fontsize=11, fontweight='bold')
    ax1.axis('off')

    ax2.imshow(mask_cropped, cmap='gray')
    ax2.set_title(f'Region recortada ({mask_cropped.shape[1]}x{mask_cropped.shape[0]})',
                  fontsize=11, fontweight='bold')
    ax2.axis('off')

    # Info
    fig.text(0.5, 0.52, '→', fontsize=30, ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.45, f'filas\n{row_bounds[0]}-{row_bounds[1]}', fontsize=9,
             ha='center', va='center', color='#7F8C8D')


def paso_7_firma(ax, fig):
    """Paso 7: Firma espectral (perfil 1D)."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)
    mask = (img_gray < 0.99).astype(np.float32) * 255

    row_bounds = (150, 250)
    col_sum = np.sum(mask, axis=0)
    cols_with_data = np.where(col_sum > 0)[0]
    col_start, col_end = cols_with_data[0], cols_with_data[-1]
    mask_cropped = mask[row_bounds[0]:row_bounds[1], col_start:col_end]

    # Calcular firma (media por columna)
    signature = np.mean(mask_cropped, axis=0)

    # Mostrar
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.45, 0.84, 0.35])
    ax2 = fig.add_axes([0.08, 0.12, 0.84, 0.28])

    ax1.imshow(mask_cropped, cmap='gray', aspect='auto')
    ax1.set_title('Region recortada (2D)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Filas')
    ax1.set_xticks([])

    ax2.plot(signature, color='#9B59B6', linewidth=2)
    ax2.fill_between(range(len(signature)), signature, alpha=0.3, color='#9B59B6')
    ax2.set_title('Firma espectral: media por columna (1D)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Columnas')
    ax2.set_ylabel('Intensidad media')
    ax2.set_xlim(0, len(signature))
    ax2.grid(alpha=0.3)


def paso_8_resize(ax, fig):
    """Paso 8: Redimensionar a 200 dimensiones."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)
    mask = (img_gray < 0.99).astype(np.float32) * 255

    row_bounds = (150, 250)
    col_sum = np.sum(mask, axis=0)
    cols_with_data = np.where(col_sum > 0)[0]
    col_start, col_end = cols_with_data[0], cols_with_data[-1]
    mask_cropped = mask[row_bounds[0]:row_bounds[1], col_start:col_end]
    signature = np.mean(mask_cropped, axis=0)

    # Redimensionar a 200
    vector_size = 200
    resized = np.interp(
        np.linspace(0, len(signature)-1, vector_size),
        np.arange(len(signature)),
        signature
    )

    # Mostrar
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.45, 0.84, 0.35])
    ax2 = fig.add_axes([0.08, 0.12, 0.84, 0.28])

    ax1.plot(signature, color='#7F8C8D', linewidth=1.5, label=f'Original ({len(signature)} dims)')
    ax1.set_title(f'Firma original: {len(signature)} dimensiones', fontsize=11, fontweight='bold')
    ax1.set_xlim(0, len(signature))
    ax1.grid(alpha=0.3)
    ax1.set_ylabel('Intensidad')

    ax2.plot(resized, color='#9B59B6', linewidth=2, label=f'Redimensionado ({vector_size} dims)')
    ax2.fill_between(range(len(resized)), resized, alpha=0.3, color='#9B59B6')
    ax2.set_title(f'Firma redimensionada: {vector_size} dimensiones (interpolacion lineal)',
                  fontsize=11, fontweight='bold')
    ax2.set_xlabel('Dimension')
    ax2.set_ylabel('Intensidad')
    ax2.set_xlim(0, vector_size)
    ax2.grid(alpha=0.3)


def paso_9_normalizacion(ax, fig):
    """Paso 9: Normalizacion L2."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)
    mask = (img_gray < 0.99).astype(np.float32) * 255

    row_bounds = (150, 250)
    col_sum = np.sum(mask, axis=0)
    cols_with_data = np.where(col_sum > 0)[0]
    col_start, col_end = cols_with_data[0], cols_with_data[-1]
    mask_cropped = mask[row_bounds[0]:row_bounds[1], col_start:col_end]
    signature = np.mean(mask_cropped, axis=0)

    vector_size = 200
    resized = np.interp(
        np.linspace(0, len(signature)-1, vector_size),
        np.arange(len(signature)),
        signature
    )

    # Normalizar L2
    norm = np.linalg.norm(resized)
    normalized = resized / norm

    # Mostrar
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.45, 0.84, 0.35])
    ax2 = fig.add_axes([0.08, 0.12, 0.84, 0.28])

    ax1.plot(resized, color='#7F8C8D', linewidth=1.5)
    ax1.set_title(f'Antes: ||v|| = {norm:.2f}', fontsize=11, fontweight='bold')
    ax1.set_xlim(0, vector_size)
    ax1.grid(alpha=0.3)
    ax1.set_ylabel('Intensidad')

    ax2.plot(normalized, color='#9B59B6', linewidth=2)
    ax2.fill_between(range(len(normalized)), normalized, alpha=0.3, color='#9B59B6')
    ax2.set_title(f'Despues: ||v|| = {np.linalg.norm(normalized):.2f} (vector unitario)',
                  fontsize=11, fontweight='bold')
    ax2.set_xlabel('Dimension')
    ax2.set_ylabel('Valor normalizado')
    ax2.set_xlim(0, vector_size)
    ax2.grid(alpha=0.3)


def paso_10_vector_final(ax, fig):
    """Paso 10: Vector final."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)
    mask = (img_gray < 0.99).astype(np.float32) * 255

    row_bounds = (150, 250)
    col_sum = np.sum(mask, axis=0)
    cols_with_data = np.where(col_sum > 0)[0]
    col_start, col_end = cols_with_data[0], cols_with_data[-1]
    mask_cropped = mask[row_bounds[0]:row_bounds[1], col_start:col_end]
    signature = np.mean(mask_cropped, axis=0)

    vector_size = 200
    resized = np.interp(
        np.linspace(0, len(signature)-1, vector_size),
        np.arange(len(signature)),
        signature
    )

    norm = np.linalg.norm(resized)
    normalized = resized / norm

    # Mostrar vector final
    ax.clear()
    fig.delaxes(ax)

    ax1 = fig.add_axes([0.08, 0.35, 0.84, 0.45])

    # Grafico del vector
    ax1.bar(range(vector_size), normalized, color='#E74C3C', width=1.0, alpha=0.8)
    ax1.set_title('Vector Final: 200 dimensiones normalizadas', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Dimension (0-199)')
    ax1.set_ylabel('Valor')
    ax1.set_xlim(0, vector_size)
    ax1.grid(alpha=0.3, axis='y')

    # Mostrar primeros y ultimos valores
    values_text = f'Primeros 5 valores: [{", ".join([f"{v:.4f}" for v in normalized[:5]])}...]'
    fig.text(0.5, 0.18, values_text, fontsize=10, ha='center', va='center',
             color='#2C3E50', family='monospace')

    values_text2 = f'Ultimos 5 valores: [...{", ".join([f"{v:.4f}" for v in normalized[-5:]])}]'
    fig.text(0.5, 0.12, values_text2, fontsize=10, ha='center', va='center',
             color='#2C3E50', family='monospace')


def main():
    """Genera todas las imagenes de los pasos del pipeline."""
    print("=" * 60)
    print("GENERANDO IMAGENES DE CADA PASO DEL PIPELINE")
    print("=" * 60)
    print(f"\nUsando espectro: {SPECTRUM_PATH}")
    print(f"Directorio de salida: {OUTPUT_DIR}/\n")

    steps = [
        (0, 'ENTRADA', 'Archivo DOCX del microscopio', paso_0_entrada,
         'Formato: Microsoft Word (.docx) con imagen embebida'),

        (1, 'EXTRACCION', 'Obtiene la imagen del espectro EDS del documento', paso_1_extraccion,
         'python-docx extrae imagenes embebidas del archivo'),

        (2, 'LECTURA', 'Convierte la imagen a formato float normalizado (0-1)', paso_2_lectura,
         'img.astype(float32) / 255.0'),

        (3, 'FILTRADO', 'Aplica filtro Gaussiano para reducir ruido', paso_3_filtrado,
         'cv2.GaussianBlur(img, (5,5), 0)'),

        (4, 'ESCALA DE GRISES', 'Convierte de 3 canales (BGR) a 1 canal', paso_4_escala_gris,
         'cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)'),

        (5, 'BINARIZACION', 'Crea mascara binaria separando espectro del fondo', paso_5_binarizacion,
         'mask = (gray < 0.99) * 255'),

        (6, 'RECORTE', 'Aisla la region de interes del espectro', paso_6_recorte,
         'mask[150:250, col_start:col_end]'),

        (7, 'FIRMA ESPECTRAL', 'Calcula el perfil 1D (media por columna)', paso_7_firma,
         'signature = np.mean(mask_cropped, axis=0)'),

        (8, 'REDIMENSIONAR', 'Interpola a 200 dimensiones fijas', paso_8_resize,
         'np.interp(..., vector_size=200)'),

        (9, 'NORMALIZACION L2', 'Normaliza el vector a norma unitaria', paso_9_normalizacion,
         'vector / np.linalg.norm(vector)'),

        (10, 'VECTOR FINAL', 'Array de 200 floats listo para comparacion', paso_10_vector_final,
         'Listo para calcular similitud de coseno'),
    ]

    for step_num, title, description, func, extra_info in steps:
        print(f"  Generando paso {step_num}: {title}...")

        fig = create_step_figure(step_num, title, description, func, extra_info)

        filename = f"paso_{step_num:02d}_{title.lower().replace(' ', '_').replace('/', '_')}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        plt.savefig(filepath, bbox_inches='tight', facecolor='white', dpi=150)
        plt.close()

        print(f"    -> {filename}")

    print("\n" + "=" * 60)
    print(f"COMPLETADO: {len(steps)} imagenes generadas en {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
