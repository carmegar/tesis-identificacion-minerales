"""
Script para generar diagramas para la documentación de la tesis.
Genera: Diagrama ER, Pipeline, Fórmula de Coseno, Interpretación de Vectores, Espectro en Escala de Grises
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Wedge
import numpy as np
import os
import cv2
from docx import Document
from io import BytesIO

# Configuración general
OUTPUT_DIR = "diagramas"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurar matplotlib para mejor calidad
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'DejaVu Sans'


def generate_er_diagram():
    """Genera el diagrama Entidad-Relación de la base de datos."""
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Colores
    header_color = '#2C3E50'
    pk_color = '#E74C3C'
    fk_color = '#3498DB'
    field_color = '#ECF0F1'
    border_color = '#34495E'

    # === TABLA MUESTRAS ===
    # Header
    header1 = FancyBboxPatch((0.5, 4.5), 4, 0.7, boxstyle="round,pad=0.02",
                              facecolor=header_color, edgecolor=border_color, linewidth=2)
    ax.add_patch(header1)
    ax.text(2.5, 4.85, 'MUESTRAS', fontsize=14, fontweight='bold',
            color='white', ha='center', va='center')

    # Campos
    fields1 = [
        ('id', 'INTEGER', 'PK', pk_color),
        ('nombre_muestra', 'STRING', 'NOT NULL', field_color),
        ('fecha', 'DATETIME', 'DEFAULT NOW()', field_color),
        ('investigador', 'STRING', 'NULLABLE', field_color),
        ('ruta_imagen', 'STRING', 'NULLABLE', field_color),
    ]

    for i, (name, dtype, constraint, color) in enumerate(fields1):
        y = 4.3 - i * 0.6
        rect = FancyBboxPatch((0.5, y - 0.25), 4, 0.5, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor=border_color, linewidth=1)
        ax.add_patch(rect)

        if constraint == 'PK':
            ax.text(0.7, y, f'{name}', fontsize=10, fontweight='bold', va='center', color='white')
            ax.text(2.5, y, dtype, fontsize=9, va='center', color='white')
            ax.text(3.8, y, constraint, fontsize=8, fontweight='bold', va='center', color='white')
        else:
            ax.text(0.7, y, f'{name}', fontsize=10, va='center')
            ax.text(2.5, y, dtype, fontsize=9, va='center', color='#7F8C8D')
            ax.text(3.5, y, constraint, fontsize=8, va='center', color='#95A5A6')

    # === TABLA ESPECTROS_VECTORIZADOS ===
    # Header
    header2 = FancyBboxPatch((7, 4.5), 4.5, 0.7, boxstyle="round,pad=0.02",
                              facecolor=header_color, edgecolor=border_color, linewidth=2)
    ax.add_patch(header2)
    ax.text(9.25, 4.85, 'ESPECTROS_VECTORIZADOS', fontsize=12, fontweight='bold',
            color='white', ha='center', va='center')

    # Campos
    fields2 = [
        ('id', 'INTEGER', 'PK', pk_color),
        ('muestra_id', 'INTEGER', 'FK', fk_color),
        ('vector_json', 'TEXT', 'NOT NULL', field_color),
    ]

    for i, (name, dtype, constraint, color) in enumerate(fields2):
        y = 4.3 - i * 0.6
        rect = FancyBboxPatch((7, y - 0.25), 4.5, 0.5, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor=border_color, linewidth=1)
        ax.add_patch(rect)

        if constraint in ['PK', 'FK']:
            ax.text(7.2, y, f'{name}', fontsize=10, fontweight='bold', va='center', color='white')
            ax.text(9, y, dtype, fontsize=9, va='center', color='white')
            ax.text(10.5, y, constraint, fontsize=8, fontweight='bold', va='center', color='white')
        else:
            ax.text(7.2, y, f'{name}', fontsize=10, va='center')
            ax.text(9, y, dtype, fontsize=9, va='center', color='#7F8C8D')
            ax.text(10.5, y, constraint, fontsize=8, va='center', color='#95A5A6')

    # Nota sobre vector_json
    ax.text(9.25, 2.4, '(JSON array de 200 floats)', fontsize=8,
            ha='center', va='center', color='#7F8C8D', style='italic')

    # === LINEA DE RELACION ===
    # Línea horizontal
    ax.plot([4.5, 7], [4.05, 4.05], color=border_color, linewidth=2)

    # Símbolo 1 (lado muestras)
    ax.text(4.7, 4.25, '1', fontsize=12, fontweight='bold', va='center')
    ax.plot([4.5, 4.5], [3.9, 4.2], color=border_color, linewidth=2)

    # Símbolo 1 (lado espectros)
    ax.text(6.7, 4.25, '1', fontsize=12, fontweight='bold', va='center')
    ax.plot([7, 7], [3.9, 4.2], color=border_color, linewidth=2)

    # Etiqueta de relación
    ax.text(5.75, 4.4, 'tiene', fontsize=10, ha='center', va='center',
            style='italic', color='#7F8C8D')

    # === LEYENDA ===
    legend_y = 1.2
    ax.add_patch(FancyBboxPatch((1, legend_y), 0.4, 0.3, boxstyle="round,pad=0.02",
                                 facecolor=pk_color, edgecolor=border_color))
    ax.text(1.6, legend_y + 0.15, 'PK = Primary Key', fontsize=9, va='center')

    ax.add_patch(FancyBboxPatch((4, legend_y), 0.4, 0.3, boxstyle="round,pad=0.02",
                                 facecolor=fk_color, edgecolor=border_color))
    ax.text(4.6, legend_y + 0.15, 'FK = Foreign Key', fontsize=9, va='center')

    ax.add_patch(FancyBboxPatch((7.5, legend_y), 0.4, 0.3, boxstyle="round,pad=0.02",
                                 facecolor=field_color, edgecolor=border_color))
    ax.text(8.1, legend_y + 0.15, 'Campo regular', fontsize=9, va='center')

    # Título
    ax.text(6, 6.5, 'Diagrama Entidad-Relación: Base de Datos de Espectros EDS',
            fontsize=14, fontweight='bold', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'diagrama_er.png'), bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: diagrama_er.png")


def generate_pipeline_diagram():
    """Genera el diagrama del pipeline de procesamiento."""
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')

    # Colores para diferentes tipos de pasos
    colors = {
        'input': '#3498DB',      # Azul - entrada
        'process': '#2ECC71',    # Verde - procesamiento
        'transform': '#9B59B6',  # Púrpura - transformación
        'output': '#E74C3C',     # Rojo - salida
    }

    steps = [
        ('Archivo DOCX\no Imagen JPG', 'input', 'Entrada del sistema'),
        ('1. EXTRACCION', 'process', 'Obtiene imagen del espectro EDS'),
        ('2. LECTURA', 'process', 'Lee imagen como float (0-1)'),
        ('3. FILTRADO', 'transform', 'Filtro Gaussiano 5x5'),
        ('4. ESCALA GRIS', 'transform', 'Convierte a monocanal'),
        ('5. BINARIZACION', 'transform', 'Mascara binaria (umbral 0.99)'),
        ('6. RECORTE', 'transform', 'Aisla region de interes'),
        ('7. FIRMA', 'transform', 'Perfil espectral (media/columna)'),
        ('8. RESIZE', 'transform', 'Redimensiona a 200 dimensiones'),
        ('9. NORMALIZACION', 'transform', 'Normaliza con norma L2'),
        ('VECTOR FINAL\n[0.1, 0.2, ...]', 'output', 'Array de 200 floats'),
    ]

    box_height = 0.9
    box_width = 4.5
    start_y = 13
    spacing = 1.15
    center_x = 5

    for i, (name, step_type, desc) in enumerate(steps):
        y = start_y - i * spacing
        color = colors[step_type]

        # Caja principal
        rect = FancyBboxPatch((center_x - box_width/2, y - box_height/2),
                               box_width, box_height,
                               boxstyle="round,pad=0.03",
                               facecolor=color, edgecolor='#2C3E50', linewidth=2,
                               alpha=0.9)
        ax.add_patch(rect)

        # Texto del paso
        ax.text(center_x, y, name, fontsize=11, fontweight='bold',
                ha='center', va='center', color='white')

        # Descripción a la derecha
        ax.text(center_x + box_width/2 + 0.3, y, desc, fontsize=9,
                ha='left', va='center', color='#7F8C8D', style='italic')

        # Flecha hacia abajo (excepto el último)
        if i < len(steps) - 1:
            arrow_y = y - box_height/2 - 0.05
            ax.annotate('', xy=(center_x, arrow_y - 0.15),
                       xytext=(center_x, arrow_y),
                       arrowprops=dict(arrowstyle='->', color='#2C3E50', lw=2))

    # Leyenda
    legend_items = [
        ('Entrada', colors['input']),
        ('Procesamiento', colors['process']),
        ('Transformacion', colors['transform']),
        ('Salida', colors['output']),
    ]

    for i, (label, color) in enumerate(legend_items):
        x = 0.5 + i * 2.3
        rect = FancyBboxPatch((x, 0.3), 0.4, 0.3, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#2C3E50')
        ax.add_patch(rect)
        ax.text(x + 0.5, 0.45, label, fontsize=8, va='center')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'pipeline_procesamiento.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: pipeline_procesamiento.png")


def generate_cosine_formula():
    """Genera la imagen con la fórmula de similitud de coseno."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')

    # Fórmula principal con LaTeX
    formula = r'$\text{similitud}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \times \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i \times B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}$'

    ax.text(0.5, 0.65, formula, fontsize=18, ha='center', va='center',
            transform=ax.transAxes)

    # Explicación de términos
    explanations = [
        r'$\mathbf{A}, \mathbf{B}$: Vectores de características espectrales (200 dimensiones)',
        r'$\mathbf{A} \cdot \mathbf{B}$: Producto punto de los vectores',
        r'$\|\mathbf{A}\|, \|\mathbf{B}\|$: Normas L2 (magnitudes) de los vectores',
        r'$n = 200$: Dimensión del espacio vectorial',
    ]

    for i, exp in enumerate(explanations):
        ax.text(0.5, 0.35 - i * 0.1, exp, fontsize=11, ha='center', va='center',
                transform=ax.transAxes, color='#2C3E50')

    # Título
    ax.text(0.5, 0.9, 'Formula de Similitud de Coseno', fontsize=16,
            fontweight='bold', ha='center', va='center', transform=ax.transAxes)

    # Rango de valores
    ax.text(0.5, 0.02, 'Rango: [0, 1] donde 1 = vectores identicos, 0 = vectores ortogonales',
            fontsize=10, ha='center', va='center', transform=ax.transAxes,
            color='#E74C3C', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'formula_similitud_coseno.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: formula_similitud_coseno.png")


def generate_vector_interpretation():
    """Genera la interpretación gráfica de vectores idénticos y ortogonales."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # === VECTORES IDENTICOS (similitud = 1) ===
    ax1 = axes[0]
    ax1.set_xlim(-0.5, 2)
    ax1.set_ylim(-0.5, 2)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)

    # Vector A
    ax1.annotate('', xy=(1.5, 1.2), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=3))
    ax1.text(1.6, 1.3, r'$\mathbf{A}$', fontsize=14, color='#E74C3C', fontweight='bold')

    # Vector B (idéntico, ligeramente desplazado para visualización)
    ax1.annotate('', xy=(1.45, 1.15), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#3498DB', lw=3, linestyle='--'))
    ax1.text(1.55, 1.0, r'$\mathbf{B}$', fontsize=14, color='#3498DB', fontweight='bold')

    # Ángulo
    theta = np.linspace(0, np.arctan(1.2/1.5), 30)
    r = 0.4
    ax1.plot(r * np.cos(theta), r * np.sin(theta), 'g-', lw=2)
    ax1.text(0.5, 0.15, r'$\theta = 0°$', fontsize=12, color='#27AE60')

    ax1.set_title(r'Vectores Identicos: $\cos(0°) = 1$', fontsize=14, fontweight='bold', pad=10)
    ax1.text(0.75, -0.35, 'Similitud = 100%', fontsize=12, ha='center',
             color='#27AE60', fontweight='bold')
    ax1.set_xlabel('Dimension 1')
    ax1.set_ylabel('Dimension 2')

    # === VECTORES ORTOGONALES (similitud = 0) ===
    ax2 = axes[1]
    ax2.set_xlim(-0.5, 2)
    ax2.set_ylim(-0.5, 2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linewidth=0.5)
    ax2.axvline(x=0, color='k', linewidth=0.5)

    # Vector A (horizontal)
    ax2.annotate('', xy=(1.5, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=3))
    ax2.text(1.6, 0.1, r'$\mathbf{A}$', fontsize=14, color='#E74C3C', fontweight='bold')

    # Vector B (vertical)
    ax2.annotate('', xy=(0, 1.5), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#3498DB', lw=3))
    ax2.text(0.1, 1.6, r'$\mathbf{B}$', fontsize=14, color='#3498DB', fontweight='bold')

    # Ángulo recto
    ax2.plot([0.2, 0.2, 0], [0, 0.2, 0.2], 'g-', lw=2)
    ax2.text(0.35, 0.35, r'$\theta = 90°$', fontsize=12, color='#27AE60')

    ax2.set_title(r'Vectores Ortogonales: $\cos(90°) = 0$', fontsize=14, fontweight='bold', pad=10)
    ax2.text(0.75, -0.35, 'Similitud = 0%', fontsize=12, ha='center',
             color='#E74C3C', fontweight='bold')
    ax2.set_xlabel('Dimension 1')
    ax2.set_ylabel('Dimension 2')

    # Título general
    fig.suptitle('Interpretacion Geometrica de la Similitud de Coseno',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'interpretacion_vectores.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: interpretacion_vectores.png")


def generate_grayscale_spectrum():
    """Extrae y muestra un espectro en escala de grises desde un DOCX."""
    # Buscar un archivo DOCX de muestra
    sample_dir = "muestrasdatos/Muestras Tesis"
    docx_files = [f for f in os.listdir(sample_dir) if f.endswith('.docx')]

    if not docx_files:
        print("No se encontraron archivos DOCX")
        return

    docx_path = os.path.join(sample_dir, docx_files[0])
    mineral_name = docx_files[0].replace('.docx', '')

    print(f"Procesando: {docx_path}")

    # Extraer imagen del DOCX
    doc = Document(docx_path)
    img_data = None

    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            img_data = rel.target_part.blob
            break

    if img_data is None:
        print("No se encontró imagen en el DOCX")
        return

    # Convertir a numpy array
    nparr = np.frombuffer(img_data, np.uint8)
    img_color = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_color is None:
        print("Error al decodificar imagen")
        return

    # Convertir a RGB para matplotlib
    img_rgb = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)

    # Convertir a escala de grises
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    # Aplicar filtro gaussiano
    img_filtered = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # Crear figura con subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Imagen original
    axes[0].imshow(img_rgb)
    axes[0].set_title('1. Imagen Original (Color)', fontsize=12, fontweight='bold')
    axes[0].axis('off')

    # Escala de grises
    axes[1].imshow(img_gray, cmap='gray')
    axes[1].set_title('2. Escala de Grises', fontsize=12, fontweight='bold')
    axes[1].axis('off')

    # Con filtro gaussiano
    axes[2].imshow(img_filtered, cmap='gray')
    axes[2].set_title('3. Filtro Gaussiano 5x5', fontsize=12, fontweight='bold')
    axes[2].axis('off')

    # Título general
    fig.suptitle(f'Procesamiento de Espectro EDS: {mineral_name}',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'espectro_escala_grises.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    # También guardar solo la imagen en escala de grises
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.imshow(img_gray, cmap='gray')
    ax2.set_title(f'Espectro EDS en Escala de Grises\n{mineral_name}',
                  fontsize=14, fontweight='bold')
    ax2.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'espectro_gris_solo.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    print("Generado: espectro_escala_grises.png")
    print("Generado: espectro_gris_solo.png")


def main():
    """Genera todos los diagramas."""
    print("=" * 50)
    print("Generando diagramas para la tesis...")
    print("=" * 50)
    print()

    generate_er_diagram()
    generate_pipeline_diagram()
    generate_cosine_formula()
    generate_vector_interpretation()
    generate_grayscale_spectrum()

    print()
    print("=" * 50)
    print(f"Todos los diagramas han sido guardados en: {OUTPUT_DIR}/")
    print("=" * 50)

    # Listar archivos generados
    files = os.listdir(OUTPUT_DIR)
    print("\nArchivos generados:")
    for f in files:
        filepath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(filepath) / 1024
        print(f"  - {f} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
