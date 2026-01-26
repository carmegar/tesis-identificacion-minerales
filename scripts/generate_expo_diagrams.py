"""
Script para generar diagramas de apoyo para la exposición.
Genera: Stack tecnológico, Arquitectura 3 capas, Capa de presentación, Modelo de datos
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np
import os

OUTPUT_DIR = "diagramas"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'DejaVu Sans'


def generate_tech_stack():
    """Genera diagrama del stack tecnológico."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Colores por categoría
    colors = {
        'lenguaje': '#3776AB',      # Azul Python
        'imagen': '#5C3D2E',        # Marrón OpenCV
        'calculo': '#013243',       # Azul oscuro NumPy
        'bd': '#CA0000',            # Rojo SQLAlchemy
        'storage': '#003B57',       # Azul SQLite
        'ui': '#FF4B4B',            # Rojo Streamlit
        'docs': '#2B579A',          # Azul Word
    }

    technologies = [
        # (nombre, version, rol, x, y, color_key, width)
        ('Python', '3.9+', 'Lenguaje de programacion', 1, 6, 'lenguaje', 3.5),
        ('OpenCV', '4.8+', 'Procesamiento de imagenes', 5.5, 6, 'imagen', 3.5),
        ('NumPy', '1.23+', 'Calculos matematicos', 10, 6, 'calculo', 3.5),
        ('SQLAlchemy', '2.0+', 'ORM (Mapeo objeto-relacional)', 1, 3.5, 'bd', 3.5),
        ('SQLite', '3.x', 'Base de datos embebida', 5.5, 3.5, 'storage', 3.5),
        ('Streamlit', '1.29+', 'Interfaz web interactiva', 10, 3.5, 'ui', 3.5),
        ('python-docx', '1.1+', 'Lectura de archivos DOCX', 5.5, 1, 'docs', 3.5),
    ]

    for name, version, role, x, y, color_key, width in technologies:
        color = colors[color_key]

        # Caja principal
        rect = FancyBboxPatch((x, y), width, 1.8, boxstyle="round,pad=0.05",
                               facecolor=color, edgecolor='#2C3E50', linewidth=2,
                               alpha=0.9)
        ax.add_patch(rect)

        # Nombre de la tecnología
        ax.text(x + width/2, y + 1.35, name, fontsize=13, fontweight='bold',
                ha='center', va='center', color='white')

        # Versión
        ax.text(x + width/2, y + 0.9, version, fontsize=10,
                ha='center', va='center', color='#E0E0E0')

        # Rol
        ax.text(x + width/2, y + 0.4, role, fontsize=8,
                ha='center', va='center', color='#CCCCCC', style='italic')

    # Flechas de conexión (flujo de datos)
    arrow_style = dict(arrowstyle='->', color='#7F8C8D', lw=2,
                       connectionstyle='arc3,rad=0.1')

    # python-docx -> OpenCV
    ax.annotate('', xy=(5.5, 3.5), xytext=(7.25, 2.8),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=1.5))

    # OpenCV -> NumPy
    ax.annotate('', xy=(10, 6.9), xytext=(9, 6.9),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=1.5))

    # NumPy -> SQLAlchemy (via SQLite)
    ax.annotate('', xy=(5.5, 4.4), xytext=(9, 4.4),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=1.5))

    # SQLAlchemy -> SQLite
    ax.annotate('', xy=(5.5, 4.4), xytext=(4.5, 4.4),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=1.5))

    # Streamlit conecta con todo
    ax.annotate('', xy=(10, 5.3), xytext=(10, 6),
                arrowprops=dict(arrowstyle='<->', color='#7F8C8D', lw=1.5))

    # Título
    ax.text(7, 7.7, 'Stack Tecnologico del Sistema', fontsize=16,
            fontweight='bold', ha='center', va='center', color='#2C3E50')

    # Leyenda de categorías
    legend_y = 0.3
    legend_items = [
        ('Lenguaje', colors['lenguaje']),
        ('Imagenes', colors['imagen']),
        ('Calculos', colors['calculo']),
        ('ORM', colors['bd']),
        ('Storage', colors['storage']),
        ('UI', colors['ui']),
        ('Docs', colors['docs']),
    ]

    for i, (label, color) in enumerate(legend_items):
        x = 0.5 + i * 1.9
        rect = FancyBboxPatch((x, legend_y), 0.3, 0.3, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#2C3E50')
        ax.add_patch(rect)
        ax.text(x + 0.4, legend_y + 0.15, label, fontsize=8, va='center')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'tecnologias_stack.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: tecnologias_stack.png")


def generate_architecture_3_layers():
    """Genera diagrama de arquitectura de 3 capas."""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Colores por capa
    layer_colors = {
        'presentacion': '#3498DB',  # Azul
        'analisis': '#27AE60',      # Verde
        'datos': '#E74C3C',         # Rojo
    }

    # === CAPA DE PRESENTACION ===
    # Marco exterior
    rect_pres = FancyBboxPatch((0.5, 7), 11, 2.5, boxstyle="round,pad=0.03",
                                facecolor='#EBF5FB', edgecolor=layer_colors['presentacion'],
                                linewidth=3)
    ax.add_patch(rect_pres)

    # Título de capa
    ax.text(6, 9.2, 'CAPA DE PRESENTACION', fontsize=12, fontweight='bold',
            ha='center', va='center', color=layer_colors['presentacion'])
    ax.text(6, 8.85, 'Interfaz Streamlit (app.py)', fontsize=9,
            ha='center', va='center', color='#7F8C8D', style='italic')

    # Componentes de presentación
    pres_components = [
        ('Inicio', 1.2, 7.8),
        ('Identificar\nMineral', 4, 7.8),
        ('Base de\nDatos', 7, 7.8),
        ('Info\nTecnica', 9.8, 7.8),
    ]

    for name, x, y in pres_components:
        rect = FancyBboxPatch((x, y), 2, 1, boxstyle="round,pad=0.03",
                               facecolor=layer_colors['presentacion'],
                               edgecolor='#2C3E50', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + 1, y + 0.5, name, fontsize=9, fontweight='bold',
                ha='center', va='center', color='white')

    # === CAPA DE ANALISIS ===
    rect_anal = FancyBboxPatch((0.5, 3.8), 11, 2.5, boxstyle="round,pad=0.03",
                                facecolor='#E9F7EF', edgecolor=layer_colors['analisis'],
                                linewidth=3)
    ax.add_patch(rect_anal)

    ax.text(6, 6, 'CAPA DE ANALISIS', fontsize=12, fontweight='bold',
            ha='center', va='center', color=layer_colors['analisis'])
    ax.text(6, 5.65, 'Logica de negocio (src/analysis/)', fontsize=9,
            ha='center', va='center', color='#7F8C8D', style='italic')

    # Componentes de análisis
    anal_components = [
        ('vectorize.py', 'Preprocesamiento\nSegmentacion\nVectorizacion', 1.5, 4.3),
        ('compare.py', 'Similitud coseno\nRanking resultados\nCalculo confianza', 7, 4.3),
    ]

    for name, desc, x, y in anal_components:
        rect = FancyBboxPatch((x, y), 3.5, 1.5, boxstyle="round,pad=0.03",
                               facecolor=layer_colors['analisis'],
                               edgecolor='#2C3E50', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + 1.75, y + 1.15, name, fontsize=10, fontweight='bold',
                ha='center', va='center', color='white')
        ax.text(x + 1.75, y + 0.5, desc, fontsize=7,
                ha='center', va='center', color='#E0E0E0')

    # Flecha entre componentes de análisis
    ax.annotate('', xy=(7, 5.05), xytext=(5, 5.05),
                arrowprops=dict(arrowstyle='->', color='#2C3E50', lw=2))

    # === CAPA DE DATOS ===
    rect_data = FancyBboxPatch((0.5, 0.6), 11, 2.5, boxstyle="round,pad=0.03",
                                facecolor='#FDEDEC', edgecolor=layer_colors['datos'],
                                linewidth=3)
    ax.add_patch(rect_data)

    ax.text(6, 2.8, 'CAPA DE DATOS', fontsize=12, fontweight='bold',
            ha='center', va='center', color=layer_colors['datos'])
    ax.text(6, 2.45, 'Persistencia (src/database/)', fontsize=9,
            ha='center', va='center', color='#7F8C8D', style='italic')

    # Componentes de datos
    data_components = [
        ('models.py', 'ORM', 1.2, 1.1),
        ('queries.py', 'CRUD', 4.2, 1.1),
        ('connection.py', 'Config', 7.2, 1.1),
        ('minerales_eds.db', 'SQLite', 9.5, 1.1),
    ]

    for name, desc, x, y in data_components:
        rect = FancyBboxPatch((x, y), 2.2, 1, boxstyle="round,pad=0.03",
                               facecolor=layer_colors['datos'],
                               edgecolor='#2C3E50', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + 1.1, y + 0.65, name, fontsize=8, fontweight='bold',
                ha='center', va='center', color='white')
        ax.text(x + 1.1, y + 0.3, desc, fontsize=8,
                ha='center', va='center', color='#E0E0E0')

    # === FLECHAS ENTRE CAPAS ===
    # Presentación -> Análisis
    ax.annotate('', xy=(6, 6.3), xytext=(6, 7),
                arrowprops=dict(arrowstyle='<->', color='#2C3E50', lw=2.5))

    # Análisis -> Datos
    ax.annotate('', xy=(6, 3.1), xytext=(6, 3.8),
                arrowprops=dict(arrowstyle='<->', color='#2C3E50', lw=2.5))

    # Título general
    ax.text(6, 9.7, 'Arquitectura de 3 Capas del Sistema', fontsize=14,
            fontweight='bold', ha='center', va='center', color='#2C3E50')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'arquitectura_3_capas.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: arquitectura_3_capas.png")


def generate_presentation_layer():
    """Genera diagrama detallado de la capa de presentación."""
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Color principal Streamlit
    streamlit_red = '#FF4B4B'
    bg_color = '#FAFAFA'

    # Marco de la aplicación (simula navegador)
    browser = FancyBboxPatch((0.5, 0.5), 13, 8, boxstyle="round,pad=0.02",
                              facecolor=bg_color, edgecolor='#CCCCCC', linewidth=2)
    ax.add_patch(browser)

    # Barra superior del navegador
    topbar = FancyBboxPatch((0.5, 7.8), 13, 0.7, boxstyle="round,pad=0.01",
                             facecolor='#F0F0F0', edgecolor='#CCCCCC', linewidth=1)
    ax.add_patch(topbar)

    # Círculos de control de ventana
    for i, color in enumerate(['#FF5F56', '#FFBD2E', '#27CA40']):
        circle = Circle((1 + i*0.4, 8.15), 0.12, facecolor=color, edgecolor='#888888', linewidth=0.5)
        ax.add_patch(circle)

    # URL
    ax.text(7, 8.15, 'localhost:8501', fontsize=9, ha='center', va='center',
            color='#666666', family='monospace')

    # Título de la aplicación
    ax.text(7, 7.3, 'Sistema de Identificacion de Minerales EDS', fontsize=14,
            fontweight='bold', ha='center', va='center', color='#2C3E50')

    # === SIDEBAR (Navegación) ===
    sidebar = FancyBboxPatch((0.8, 1), 2.8, 5.8, boxstyle="round,pad=0.02",
                              facecolor='#F8F9FA', edgecolor='#E0E0E0', linewidth=1)
    ax.add_patch(sidebar)

    ax.text(2.2, 6.5, 'Navegacion', fontsize=10, fontweight='bold',
            ha='center', va='center', color='#2C3E50')

    # Opciones del menú
    menu_items = [
        ('Inicio', '#3498DB', True),
        ('Identificar Mineral', '#27AE60', False),
        ('Base de Datos', '#9B59B6', False),
        ('Info Tecnica', '#E67E22', False),
    ]

    for i, (name, color, selected) in enumerate(menu_items):
        y = 5.8 - i * 1.1
        if selected:
            rect = FancyBboxPatch((1, y), 2.4, 0.8, boxstyle="round,pad=0.02",
                                   facecolor=color, edgecolor=color, linewidth=1)
            text_color = 'white'
        else:
            rect = FancyBboxPatch((1, y), 2.4, 0.8, boxstyle="round,pad=0.02",
                                   facecolor='white', edgecolor='#E0E0E0', linewidth=1)
            text_color = '#2C3E50'
        ax.add_patch(rect)
        ax.text(2.2, y + 0.4, name, fontsize=9, ha='center', va='center',
                color=text_color, fontweight='bold' if selected else 'normal')

    # === AREA DE CONTENIDO PRINCIPAL ===
    content = FancyBboxPatch((4, 1), 9.3, 5.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor='#E0E0E0', linewidth=1)
    ax.add_patch(content)

    # Secciones del contenido (simulando página de inicio)
    ax.text(8.65, 6.3, 'Bienvenido al Sistema', fontsize=12, fontweight='bold',
            ha='center', va='center', color='#2C3E50')

    # Cards de estadísticas
    stats = [
        ('101', 'Minerales\nen BD', '#3498DB'),
        ('200', 'Dimensiones\ndel vector', '#27AE60'),
        ('<50ms', 'Tiempo de\nrespuesta', '#E74C3C'),
    ]

    for i, (value, label, color) in enumerate(stats):
        x = 5 + i * 2.8
        rect = FancyBboxPatch((x, 4.2), 2.4, 1.8, boxstyle="round,pad=0.03",
                               facecolor=color, edgecolor='#2C3E50', linewidth=1.5,
                               alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + 1.2, 5.4, value, fontsize=16, fontweight='bold',
                ha='center', va='center', color='white')
        ax.text(x + 1.2, 4.7, label, fontsize=8,
                ha='center', va='center', color='#E0E0E0')

    # Área de carga de archivos
    upload = FancyBboxPatch((4.5, 1.5), 8.3, 2.2, boxstyle="round,pad=0.02",
                             facecolor='#F8F9FA', edgecolor='#CCCCCC',
                             linewidth=1, linestyle='--')
    ax.add_patch(upload)

    ax.text(8.65, 2.9, 'Arrastra un archivo DOCX aqui', fontsize=10,
            ha='center', va='center', color='#7F8C8D')
    ax.text(8.65, 2.4, 'o haz clic para seleccionar', fontsize=9,
            ha='center', va='center', color='#95A5A6')

    # Botón de subir
    btn = FancyBboxPatch((7.4, 1.7), 2.5, 0.5, boxstyle="round,pad=0.02",
                          facecolor=streamlit_red, edgecolor='#C0392B', linewidth=1)
    ax.add_patch(btn)
    ax.text(8.65, 1.95, 'Subir archivo', fontsize=9, fontweight='bold',
            ha='center', va='center', color='white')

    # Título general
    ax.text(7, 8.7, 'Capa de Presentacion: Interfaz Streamlit', fontsize=14,
            fontweight='bold', ha='center', va='center', color=streamlit_red)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'capa_presentacion.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: capa_presentacion.png")


def generate_data_model():
    """Genera diagrama del modelo de datos mejorado."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Colores
    header_color = '#2C3E50'
    pk_color = '#E74C3C'
    fk_color = '#3498DB'
    field_color = '#ECF0F1'
    json_color = '#9B59B6'

    # === TABLA MUESTRAS ===
    # Sombra
    shadow1 = FancyBboxPatch((0.6, 1.05), 4.5, 4.5, boxstyle="round,pad=0.02",
                              facecolor='#CCCCCC', edgecolor='none')
    ax.add_patch(shadow1)

    # Marco de la tabla
    frame1 = FancyBboxPatch((0.5, 1.2), 4.5, 4.5, boxstyle="round,pad=0.02",
                             facecolor='white', edgecolor=header_color, linewidth=2)
    ax.add_patch(frame1)

    # Header
    header1 = FancyBboxPatch((0.5, 5.2), 4.5, 0.5, boxstyle="round,pad=0.01,rounding_size=0.1",
                              facecolor=header_color, edgecolor=header_color)
    ax.add_patch(header1)
    ax.text(2.75, 5.45, 'muestras', fontsize=14, fontweight='bold',
            color='white', ha='center', va='center', family='monospace')

    # Campos tabla muestras
    fields1 = [
        ('id', 'INTEGER', 'PRIMARY KEY', pk_color),
        ('nombre_muestra', 'STRING', 'NOT NULL', field_color),
        ('fecha', 'DATETIME', 'DEFAULT NOW()', field_color),
        ('investigador', 'STRING', 'NULLABLE', field_color),
        ('ruta_imagen', 'STRING', 'NULLABLE', field_color),
    ]

    for i, (name, dtype, constraint, color) in enumerate(fields1):
        y = 4.9 - i * 0.7
        rect = FancyBboxPatch((0.7, y - 0.25), 4.1, 0.55, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#BDC3C7', linewidth=1)
        ax.add_patch(rect)

        if color == pk_color:
            ax.text(0.9, y, f'{name}', fontsize=10, fontweight='bold', va='center', color='white')
            ax.text(2.6, y, dtype, fontsize=9, va='center', color='#EEEEEE')
            ax.text(4, y, 'PK', fontsize=8, fontweight='bold', va='center', color='white',
                   bbox=dict(boxstyle='round', facecolor='#C0392B', edgecolor='none', pad=0.15))
        else:
            ax.text(0.9, y, f'{name}', fontsize=10, va='center', color='#2C3E50')
            ax.text(2.6, y, dtype, fontsize=9, va='center', color='#7F8C8D')
            ax.text(4.2, y, constraint, fontsize=7, va='center', color='#95A5A6')

    # === TABLA ESPECTROS_VECTORIZADOS ===
    # Sombra
    shadow2 = FancyBboxPatch((6.6, 2.55), 5, 3, boxstyle="round,pad=0.02",
                              facecolor='#CCCCCC', edgecolor='none')
    ax.add_patch(shadow2)

    # Marco de la tabla
    frame2 = FancyBboxPatch((6.5, 2.7), 5, 3, boxstyle="round,pad=0.02",
                             facecolor='white', edgecolor=header_color, linewidth=2)
    ax.add_patch(frame2)

    # Header
    header2 = FancyBboxPatch((6.5, 5.2), 5, 0.5, boxstyle="round,pad=0.01,rounding_size=0.1",
                              facecolor=header_color, edgecolor=header_color)
    ax.add_patch(header2)
    ax.text(9, 5.45, 'espectros_vectorizados', fontsize=12, fontweight='bold',
            color='white', ha='center', va='center', family='monospace')

    # Campos tabla espectros
    fields2 = [
        ('id', 'INTEGER', 'PRIMARY KEY', pk_color),
        ('muestra_id', 'INTEGER', 'FOREIGN KEY', fk_color),
        ('vector_json', 'TEXT', '200 floats', json_color),
    ]

    for i, (name, dtype, constraint, color) in enumerate(fields2):
        y = 4.9 - i * 0.7
        rect = FancyBboxPatch((6.7, y - 0.25), 4.6, 0.55, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#BDC3C7', linewidth=1)
        ax.add_patch(rect)

        ax.text(6.9, y, f'{name}', fontsize=10, fontweight='bold', va='center', color='white')
        ax.text(8.8, y, dtype, fontsize=9, va='center', color='#EEEEEE')

        if constraint == 'PRIMARY KEY':
            ax.text(10.5, y, 'PK', fontsize=8, fontweight='bold', va='center', color='white',
                   bbox=dict(boxstyle='round', facecolor='#C0392B', edgecolor='none', pad=0.15))
        elif constraint == 'FOREIGN KEY':
            ax.text(10.5, y, 'FK', fontsize=8, fontweight='bold', va='center', color='white',
                   bbox=dict(boxstyle='round', facecolor='#2980B9', edgecolor='none', pad=0.15))
        else:
            ax.text(10.3, y, constraint, fontsize=8, va='center', color='#EEEEEE')

    # === LINEA DE RELACION ===
    # Línea conectora
    ax.plot([5, 6.5], [4.55, 4.2], color=header_color, linewidth=2.5, solid_capstyle='round')

    # Cardinalidad
    ax.text(5.2, 4.75, '1', fontsize=14, fontweight='bold', color=header_color)
    ax.text(6.2, 4.0, '1', fontsize=14, fontweight='bold', color=header_color)

    # Etiqueta de relación
    rel_box = FancyBboxPatch((5.2, 4.1), 1.1, 0.5, boxstyle="round,pad=0.02",
                              facecolor='#FEF9E7', edgecolor='#F39C12', linewidth=1.5)
    ax.add_patch(rel_box)
    ax.text(5.75, 4.35, 'tiene', fontsize=9, ha='center', va='center',
            style='italic', color='#B7950B', fontweight='bold')

    # === LEYENDA ===
    legend_y = 0.5
    ax.text(1, legend_y + 0.5, 'Leyenda:', fontsize=10, fontweight='bold', color='#2C3E50')

    legend_items = [
        ('PK', pk_color, 'Primary Key'),
        ('FK', fk_color, 'Foreign Key'),
        ('JSON', json_color, 'Vector 200D'),
    ]

    for i, (abbr, color, desc) in enumerate(legend_items):
        x = 2.5 + i * 3
        rect = FancyBboxPatch((x, legend_y), 0.5, 0.4, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#2C3E50')
        ax.add_patch(rect)
        ax.text(x + 0.25, legend_y + 0.2, abbr, fontsize=8, fontweight='bold',
                ha='center', va='center', color='white')
        ax.text(x + 0.7, legend_y + 0.2, f'= {desc}', fontsize=9, va='center', color='#2C3E50')

    # Título
    ax.text(6, 7.5, 'Modelo de Datos: Diagrama Entidad-Relacion', fontsize=16,
            fontweight='bold', ha='center', va='center', color='#2C3E50')

    # Subtítulo
    ax.text(6, 7, 'Base de datos SQLite: minerales_eds.db', fontsize=11,
            ha='center', va='center', color='#7F8C8D', style='italic')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'modelo_datos.png'),
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Generado: modelo_datos.png")


def main():
    """Genera todos los diagramas de la exposición."""
    print("=" * 50)
    print("Generando diagramas para la exposicion...")
    print("=" * 50)
    print()

    generate_tech_stack()
    generate_architecture_3_layers()
    generate_presentation_layer()
    generate_data_model()

    print()
    print("=" * 50)
    print(f"Diagramas guardados en: {OUTPUT_DIR}/")
    print("=" * 50)

    # Listar archivos generados
    files = ['tecnologias_stack.png', 'arquitectura_3_capas.png',
             'capa_presentacion.png', 'modelo_datos.png']
    print("\nArchivos generados:")
    for f in files:
        filepath = os.path.join(OUTPUT_DIR, f)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024
            print(f"  - {f} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
