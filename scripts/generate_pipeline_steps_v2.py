"""
Genera imagenes mejoradas de los pasos 5-10 del pipeline.
Ajusta parametros para mejor visualizacion con espectros SFU.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import cv2
import os

OUTPUT_DIR = "diagramas/pipeline_pasos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SPECTRUM_PATH = "espectros_externos/SFU/EDS_Pyrite.jpg"


def paso_5_binarizacion_v2():
    """Paso 5: Binarizacion mejorada."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)

    # Usar umbral mas bajo para capturar los picos (que son oscuros)
    # El fondo es claro (~0.85-0.95), los picos son oscuros (~0.1-0.5)
    threshold = 0.75
    mask = (img_gray < threshold).astype(np.float32) * 255

    fig = plt.figure(figsize=(14, 7))

    # Titulo
    fig.text(0.5, 0.95, 'Paso 5: BINARIZACION', fontsize=18, fontweight='bold',
             ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.90, 'Crea mascara binaria separando los picos espectrales del fondo',
             fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    ax1 = fig.add_axes([0.05, 0.15, 0.4, 0.65])
    ax2 = fig.add_axes([0.55, 0.15, 0.4, 0.65])

    ax1.imshow(img_gray, cmap='gray')
    ax1.set_title('Escala de grises', fontsize=12, fontweight='bold')
    ax1.axis('off')
    ax1.text(0.02, 0.02, f'Rango: [{img_gray.min():.2f}, {img_gray.max():.2f}]',
             transform=ax1.transAxes, fontsize=9, color='white',
             bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

    ax2.imshow(mask, cmap='gray')
    ax2.set_title('Mascara binaria (pixeles < 0.75)', fontsize=12, fontweight='bold')
    ax2.axis('off')

    # Flecha
    fig.text(0.5, 0.47, '→', fontsize=40, ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.38, 'umbral < 0.75\n(separa picos del fondo)', fontsize=9,
             ha='center', va='center', color='#7F8C8D')

    # Codigo
    fig.text(0.5, 0.05, 'mask = (gray < threshold) * 255', fontsize=10,
             ha='center', va='center', color='#2C3E50', family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#BDC3C7'))

    plt.savefig(f'{OUTPUT_DIR}/paso_05_binarizacion.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  -> paso_05_binarizacion.png")


def paso_6_recorte_v2():
    """Paso 6: Recorte mejorado."""
    img = cv2.imread(SPECTRUM_PATH)
    img_float = img.astype(np.float32) / 255.0
    img_filtered = cv2.GaussianBlur(img_float, (5, 5), 0)
    img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)

    threshold = 0.75
    mask = (img_gray < threshold).astype(np.float32) * 255

    # Encontrar filas y columnas con datos
    row_sum = np.sum(mask, axis=1)
    col_sum = np.sum(mask, axis=0)

    rows_with_data = np.where(row_sum > row_sum.max() * 0.1)[0]
    cols_with_data = np.where(col_sum > col_sum.max() * 0.1)[0]

    if len(rows_with_data) > 0 and len(cols_with_data) > 0:
        row_start, row_end = rows_with_data[0], rows_with_data[-1]
        col_start, col_end = cols_with_data[0], cols_with_data[-1]
    else:
        row_start, row_end = 50, 350
        col_start, col_end = 50, 500

    # Agregar margen
    margin = 10
    row_start = max(0, row_start - margin)
    row_end = min(mask.shape[0], row_end + margin)
    col_start = max(0, col_start - margin)
    col_end = min(mask.shape[1], col_end + margin)

    mask_cropped = mask[row_start:row_end, col_start:col_end]

    fig = plt.figure(figsize=(14, 7))

    fig.text(0.5, 0.95, 'Paso 6: RECORTE', fontsize=18, fontweight='bold',
             ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.90, 'Aisla la region de interes eliminando bordes y texto',
             fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    ax1 = fig.add_axes([0.05, 0.15, 0.4, 0.65])
    ax2 = fig.add_axes([0.55, 0.15, 0.4, 0.65])

    ax1.imshow(mask, cmap='gray')
    rect = Rectangle((col_start, row_start), col_end-col_start, row_end-row_start,
                      fill=False, edgecolor='#E74C3C', linewidth=3)
    ax1.add_patch(rect)
    ax1.set_title('Mascara completa con ROI marcada', fontsize=12, fontweight='bold')
    ax1.axis('off')

    ax2.imshow(mask_cropped, cmap='gray')
    ax2.set_title(f'Region recortada ({mask_cropped.shape[1]} x {mask_cropped.shape[0]} px)',
                  fontsize=12, fontweight='bold')
    ax2.axis('off')

    fig.text(0.5, 0.47, '→', fontsize=40, ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.38, f'filas [{row_start}:{row_end}]\ncols [{col_start}:{col_end}]',
             fontsize=9, ha='center', va='center', color='#7F8C8D', family='monospace')

    fig.text(0.5, 0.05, 'mask_cropped = mask[row_start:row_end, col_start:col_end]',
             fontsize=10, ha='center', va='center', color='#2C3E50', family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#BDC3C7'))

    plt.savefig(f'{OUTPUT_DIR}/paso_06_recorte.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  -> paso_06_recorte.png")

    return mask_cropped, col_start, col_end, row_start, row_end


def paso_7_firma_v2(mask_cropped):
    """Paso 7: Firma espectral mejorada."""
    # Calcular firma (media por columna)
    signature = np.mean(mask_cropped, axis=0)

    fig = plt.figure(figsize=(14, 8))

    fig.text(0.5, 0.95, 'Paso 7: FIRMA ESPECTRAL', fontsize=18, fontweight='bold',
             ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.90, 'Convierte la imagen 2D en un perfil 1D calculando la media por columna',
             fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    ax1 = fig.add_axes([0.08, 0.50, 0.84, 0.32])
    ax2 = fig.add_axes([0.08, 0.12, 0.84, 0.32])

    # Mostrar imagen 2D
    ax1.imshow(mask_cropped, cmap='gray', aspect='auto')
    ax1.set_title(f'Region recortada (2D): {mask_cropped.shape[1]} columnas x {mask_cropped.shape[0]} filas',
                  fontsize=11, fontweight='bold')
    ax1.set_ylabel('Filas', fontsize=10)
    ax1.set_xlabel('Columnas', fontsize=10)

    # Dibujar flechas indicando la operacion de media
    for i in range(0, mask_cropped.shape[1], 50):
        ax1.annotate('', xy=(i, mask_cropped.shape[0]-1), xytext=(i, 0),
                     arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=0.5, alpha=0.5))

    # Mostrar firma 1D
    ax2.plot(signature, color='#9B59B6', linewidth=2)
    ax2.fill_between(range(len(signature)), signature, alpha=0.3, color='#9B59B6')
    ax2.set_title(f'Firma espectral (1D): {len(signature)} valores',
                  fontsize=11, fontweight='bold')
    ax2.set_xlabel('Posicion (columna)', fontsize=10)
    ax2.set_ylabel('Intensidad media', fontsize=10)
    ax2.set_xlim(0, len(signature))
    ax2.grid(alpha=0.3)

    # Marcar picos
    peaks_idx = np.where(signature > signature.mean() + signature.std())[0]
    if len(peaks_idx) > 0:
        ax2.scatter(peaks_idx, signature[peaks_idx], color='#E74C3C', s=20, zorder=5)

    fig.text(0.5, 0.05, 'signature = np.mean(mask_cropped, axis=0)  # Media por columna',
             fontsize=10, ha='center', va='center', color='#2C3E50', family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#BDC3C7'))

    plt.savefig(f'{OUTPUT_DIR}/paso_07_firma_espectral.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  -> paso_07_firma_espectral.png")

    return signature


def paso_8_resize_v2(signature):
    """Paso 8: Redimensionar mejorado."""
    vector_size = 200
    x_original = np.arange(len(signature))
    x_new = np.linspace(0, len(signature)-1, vector_size)
    resized = np.interp(x_new, x_original, signature)

    fig = plt.figure(figsize=(14, 8))

    fig.text(0.5, 0.95, 'Paso 8: REDIMENSIONAR', fontsize=18, fontweight='bold',
             ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.90, 'Interpola el perfil a exactamente 200 dimensiones para comparacion uniforme',
             fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    ax1 = fig.add_axes([0.08, 0.50, 0.84, 0.32])
    ax2 = fig.add_axes([0.08, 0.12, 0.84, 0.32])

    ax1.plot(signature, color='#7F8C8D', linewidth=1.5, alpha=0.8)
    ax1.fill_between(range(len(signature)), signature, alpha=0.2, color='#7F8C8D')
    ax1.set_title(f'Firma original: {len(signature)} dimensiones', fontsize=11, fontweight='bold')
    ax1.set_xlim(0, len(signature))
    ax1.set_ylabel('Intensidad', fontsize=10)
    ax1.grid(alpha=0.3)

    ax2.plot(resized, color='#9B59B6', linewidth=2)
    ax2.fill_between(range(len(resized)), resized, alpha=0.3, color='#9B59B6')
    ax2.set_title(f'Firma redimensionada: {vector_size} dimensiones (tamano fijo)',
                  fontsize=11, fontweight='bold')
    ax2.set_xlabel('Dimension', fontsize=10)
    ax2.set_ylabel('Intensidad', fontsize=10)
    ax2.set_xlim(0, vector_size)
    ax2.grid(alpha=0.3)

    # Indicar la transformacion
    fig.text(0.92, 0.65, f'{len(signature)}', fontsize=12, ha='center', color='#7F8C8D',
             fontweight='bold')
    fig.text(0.92, 0.60, '↓', fontsize=16, ha='center', color='#9B59B6')
    fig.text(0.92, 0.55, f'{vector_size}', fontsize=12, ha='center', color='#9B59B6',
             fontweight='bold')

    fig.text(0.5, 0.05, 'resized = np.interp(np.linspace(0, n-1, 200), range(n), signature)',
             fontsize=10, ha='center', va='center', color='#2C3E50', family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#BDC3C7'))

    plt.savefig(f'{OUTPUT_DIR}/paso_08_redimensionar.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  -> paso_08_redimensionar.png")

    return resized


def paso_9_normalizacion_v2(resized):
    """Paso 9: Normalizacion mejorada."""
    norm_before = np.linalg.norm(resized)
    normalized = resized / norm_before
    norm_after = np.linalg.norm(normalized)

    fig = plt.figure(figsize=(14, 8))

    fig.text(0.5, 0.95, 'Paso 9: NORMALIZACION L2', fontsize=18, fontweight='bold',
             ha='center', va='center', color='#9B59B6')
    fig.text(0.5, 0.90, 'Divide el vector por su norma euclidiana para obtener un vector unitario',
             fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    ax1 = fig.add_axes([0.08, 0.50, 0.84, 0.32])
    ax2 = fig.add_axes([0.08, 0.12, 0.84, 0.32])

    ax1.plot(resized, color='#7F8C8D', linewidth=1.5)
    ax1.fill_between(range(len(resized)), resized, alpha=0.2, color='#7F8C8D')
    ax1.set_title(f'Antes de normalizar: ||v|| = {norm_before:.2f}', fontsize=11, fontweight='bold')
    ax1.set_xlim(0, len(resized))
    ax1.set_ylabel('Intensidad', fontsize=10)
    ax1.grid(alpha=0.3)
    ax1.axhline(y=0, color='black', linewidth=0.5)

    ax2.plot(normalized, color='#9B59B6', linewidth=2)
    ax2.fill_between(range(len(normalized)), normalized, alpha=0.3, color='#9B59B6')
    ax2.set_title(f'Despues de normalizar: ||v|| = {norm_after:.4f} (vector unitario)',
                  fontsize=11, fontweight='bold')
    ax2.set_xlabel('Dimension', fontsize=10)
    ax2.set_ylabel('Valor normalizado', fontsize=10)
    ax2.set_xlim(0, len(normalized))
    ax2.grid(alpha=0.3)
    ax2.axhline(y=0, color='black', linewidth=0.5)

    # Formula
    fig.text(0.92, 0.65, f'||v|| = {norm_before:.1f}', fontsize=10, ha='center', color='#7F8C8D')
    fig.text(0.92, 0.60, '÷', fontsize=20, ha='center', color='#9B59B6')
    fig.text(0.92, 0.55, f'||v|| = {norm_after:.1f}', fontsize=10, ha='center', color='#9B59B6')

    fig.text(0.5, 0.05, 'normalized = vector / np.linalg.norm(vector)',
             fontsize=10, ha='center', va='center', color='#2C3E50', family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#BDC3C7'))

    plt.savefig(f'{OUTPUT_DIR}/paso_09_normalizacion_l2.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  -> paso_09_normalizacion_l2.png")

    return normalized


def paso_10_vector_final_v2(normalized):
    """Paso 10: Vector final mejorado."""
    fig = plt.figure(figsize=(14, 8))

    fig.text(0.5, 0.95, 'Paso 10: VECTOR FINAL', fontsize=18, fontweight='bold',
             ha='center', va='center', color='#E74C3C')
    fig.text(0.5, 0.90, 'Array de 200 floats normalizados, listo para calcular similitud de coseno',
             fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    ax = fig.add_axes([0.08, 0.30, 0.84, 0.52])

    # Grafico de barras del vector
    colors = ['#E74C3C' if v > normalized.mean() + normalized.std() else '#3498DB'
              for v in normalized]
    ax.bar(range(len(normalized)), normalized, color=colors, width=1.0, alpha=0.8)
    ax.set_title('Vector Final: 200 dimensiones normalizadas (||v|| = 1.0)',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Dimension (0-199)', fontsize=10)
    ax.set_ylabel('Valor normalizado', fontsize=10)
    ax.set_xlim(0, len(normalized))
    ax.grid(alpha=0.3, axis='y')

    # Estadisticas
    stats_text = f'Min: {normalized.min():.4f}  |  Max: {normalized.max():.4f}  |  Media: {normalized.mean():.4f}  |  Norma: {np.linalg.norm(normalized):.4f}'
    ax.text(0.5, 0.95, stats_text, transform=ax.transAxes, fontsize=9,
            ha='center', va='top', color='#2C3E50',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Mostrar algunos valores
    fig.text(0.5, 0.18, f'Primeros 5: [{", ".join([f"{v:.4f}" for v in normalized[:5]])} ...]',
             fontsize=10, ha='center', va='center', color='#2C3E50', family='monospace')
    fig.text(0.5, 0.12, f'Ultimos 5:  [... {", ".join([f"{v:.4f}" for v in normalized[-5:]])}]',
             fontsize=10, ha='center', va='center', color='#2C3E50', family='monospace')

    # Leyenda
    fig.text(0.15, 0.05, '■ Picos (valores altos)', fontsize=9, color='#E74C3C')
    fig.text(0.45, 0.05, '■ Base (valores normales)', fontsize=9, color='#3498DB')
    fig.text(0.75, 0.05, 'Listo para similitud de coseno', fontsize=9, color='#27AE60',
             fontweight='bold')

    plt.savefig(f'{OUTPUT_DIR}/paso_10_vector_final.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  -> paso_10_vector_final.png")


def main():
    """Regenera los pasos 5-10 con mejor visualizacion."""
    print("=" * 60)
    print("REGENERANDO PASOS 5-10 DEL PIPELINE (VERSION MEJORADA)")
    print("=" * 60)
    print(f"\nUsando espectro: {SPECTRUM_PATH}\n")

    # Eliminar versiones anteriores
    import glob
    old_files = glob.glob(f'{OUTPUT_DIR}/paso_0[5-9]*.png') + glob.glob(f'{OUTPUT_DIR}/paso_10*.png')
    for f in old_files:
        os.remove(f)
        print(f"  Eliminado: {os.path.basename(f)}")

    print("\nGenerando nuevas versiones:\n")

    # Generar pasos secuencialmente (cada uno depende del anterior)
    paso_5_binarizacion_v2()
    mask_cropped, _, _, _, _ = paso_6_recorte_v2()
    signature = paso_7_firma_v2(mask_cropped)
    resized = paso_8_resize_v2(signature)
    normalized = paso_9_normalizacion_v2(resized)
    paso_10_vector_final_v2(normalized)

    print("\n" + "=" * 60)
    print("COMPLETADO: 6 imagenes regeneradas")
    print("=" * 60)


if __name__ == "__main__":
    main()
