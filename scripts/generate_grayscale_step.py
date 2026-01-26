"""
Genera imagen mostrando el paso de conversion BGR a escala de grises del pipeline.
"""

import matplotlib.pyplot as plt
import cv2
import os

OUTPUT_DIR = "diagramas"

# Usar un espectro EDS con picos claros (Pirita: Fe, S)
img_path = "espectros_externos/SFU/EDS_Pyrite.jpg"

# Leer imagen en BGR (como lo hace OpenCV por defecto)
img_bgr = cv2.imread(img_path)

# Convertir BGR a RGB para mostrar correctamente en matplotlib
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# Convertir a escala de grises (paso del pipeline)
img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

# Crear figura con dos subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Imagen original en color
axes[0].imshow(img_rgb)
axes[0].set_title('Imagen Original (BGR/Color)', fontsize=14, fontweight='bold', pad=10)
axes[0].axis('off')

# Agregar anotacion
axes[0].text(0.5, -0.08, 'Espectro EDS con 3 canales de color (B, G, R)',
             transform=axes[0].transAxes, ha='center', fontsize=10, color='#7F8C8D')

# Imagen en escala de grises
axes[1].imshow(img_gray, cmap='gray')
axes[1].set_title('Escala de Grises (Monocromatico)', fontsize=14, fontweight='bold', pad=10)
axes[1].axis('off')

# Agregar anotacion
axes[1].text(0.5, -0.08, 'Espectro EDS con 1 canal de intensidad (0-255)',
             transform=axes[1].transAxes, ha='center', fontsize=10, color='#7F8C8D')

# Flecha entre las imagenes
fig.text(0.5, 0.5, '→', fontsize=40, ha='center', va='center',
         fontweight='bold', color='#E74C3C')
fig.text(0.5, 0.42, 'cv2.cvtColor(\n  BGR2GRAY)', fontsize=9, ha='center', va='center',
         family='monospace', color='#2C3E50')

# Titulo general
fig.suptitle('Paso 4 del Pipeline: Conversion a Escala de Grises',
             fontsize=16, fontweight='bold', y=1.02)

# Subtitulo con explicacion
fig.text(0.5, 0.02,
         'La conversion reduce la complejidad de 3 canales a 1, preservando la informacion de intensidad de los picos espectrales',
         ha='center', fontsize=10, color='#34495E', style='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'conversion_escala_grises.png'),
            bbox_inches='tight', facecolor='white', edgecolor='none', dpi=150)
plt.close()

print(f"Generado: {OUTPUT_DIR}/conversion_escala_grises.png")

# Mostrar dimensiones para contexto
print(f"\nDimensiones:")
print(f"  - Original (BGR): {img_bgr.shape} -> Alto x Ancho x 3 canales")
print(f"  - Escala grises:  {img_gray.shape} -> Alto x Ancho (1 canal implicito)")
