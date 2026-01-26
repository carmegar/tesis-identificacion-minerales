"""
Genera diagrama del patron Modelo-Vista-Controlador (MVC) aplicado al proyecto.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import matplotlib.patches as mpatches
import numpy as np
import os

OUTPUT_DIR = "diagramas"

def generate_mvc_diagram():
    """Genera diagrama MVC del proyecto."""

    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Colores para cada capa
    colors = {
        'vista': '#3498DB',       # Azul
        'controlador': '#27AE60', # Verde
        'modelo': '#E74C3C',      # Rojo
        'usuario': '#9B59B6',     # Púrpura
        'db': '#F39C12',          # Naranja
    }

    # =========================================================================
    # TITULO
    # =========================================================================
    ax.text(8, 11.5, 'Arquitectura MVC: Sistema de Identificacion de Minerales EDS',
            fontsize=16, fontweight='bold', ha='center', va='center', color='#2C3E50')
    ax.text(8, 11.0, 'Patron Modelo-Vista-Controlador aplicado al proyecto',
            fontsize=11, ha='center', va='center', color='#7F8C8D', style='italic')

    # =========================================================================
    # USUARIO (Izquierda)
    # =========================================================================
    # Icono de usuario
    user_circle = Circle((1.5, 6), 0.6, facecolor=colors['usuario'],
                          edgecolor='#7D3C98', linewidth=2)
    ax.add_patch(user_circle)
    ax.text(1.5, 6, 'U', fontsize=20, fontweight='bold', ha='center', va='center', color='white')
    ax.text(1.5, 5.1, 'Usuario', fontsize=10, fontweight='bold', ha='center', color='#7D3C98')

    # Acciones del usuario
    user_actions = [
        'Sube archivo DOCX',
        'Ve resultados',
        'Guarda muestra',
    ]
    for i, action in enumerate(user_actions):
        ax.text(1.5, 4.3 - i*0.4, f'• {action}', fontsize=8, ha='center', color='#7F8C8D')

    # =========================================================================
    # VISTA (Streamlit)
    # =========================================================================
    vista_box = FancyBboxPatch((3.5, 3.5), 3.5, 5, boxstyle="round,pad=0.03",
                                facecolor='#EBF5FB', edgecolor=colors['vista'],
                                linewidth=3)
    ax.add_patch(vista_box)

    # Header
    vista_header = FancyBboxPatch((3.5, 8), 3.5, 0.5, boxstyle="round,pad=0.01",
                                   facecolor=colors['vista'], edgecolor=colors['vista'])
    ax.add_patch(vista_header)
    ax.text(5.25, 8.25, 'VISTA', fontsize=12, fontweight='bold',
            ha='center', va='center', color='white')

    # Contenido Vista
    ax.text(5.25, 7.5, 'Interfaz de Usuario', fontsize=10, fontweight='bold',
            ha='center', va='center', color=colors['vista'])
    ax.text(5.25, 7.1, 'Streamlit (app.py)', fontsize=9, ha='center',
            va='center', color='#5DADE2', family='monospace')

    # Componentes de la vista
    vista_components = [
        ('Inicio', 6.5),
        ('Identificar Mineral', 6.0),
        ('Base de Datos', 5.5),
        ('Info Tecnica', 5.0),
    ]

    for name, y in vista_components:
        comp_box = FancyBboxPatch((3.8, y - 0.2), 2.9, 0.4, boxstyle="round,pad=0.02",
                                   facecolor=colors['vista'], edgecolor='#2980B9',
                                   linewidth=1, alpha=0.8)
        ax.add_patch(comp_box)
        ax.text(5.25, y, name, fontsize=8, ha='center', va='center', color='white')

    # Responsabilidades
    ax.text(5.25, 4.3, 'Responsabilidades:', fontsize=8, fontweight='bold',
            ha='center', color='#2C3E50')
    vista_resp = ['Mostrar interfaz', 'Recibir archivos', 'Presentar resultados']
    for i, resp in enumerate(vista_resp):
        ax.text(5.25, 3.9 - i*0.35, f'• {resp}', fontsize=7, ha='center', color='#5D6D7E')

    # =========================================================================
    # CONTROLADOR (Lógica de Análisis)
    # =========================================================================
    ctrl_box = FancyBboxPatch((8, 3.5), 3.5, 5, boxstyle="round,pad=0.03",
                               facecolor='#E9F7EF', edgecolor=colors['controlador'],
                               linewidth=3)
    ax.add_patch(ctrl_box)

    # Header
    ctrl_header = FancyBboxPatch((8, 8), 3.5, 0.5, boxstyle="round,pad=0.01",
                                  facecolor=colors['controlador'], edgecolor=colors['controlador'])
    ax.add_patch(ctrl_header)
    ax.text(9.75, 8.25, 'CONTROLADOR', fontsize=12, fontweight='bold',
            ha='center', va='center', color='white')

    # Contenido Controlador
    ax.text(9.75, 7.5, 'Logica de Negocio', fontsize=10, fontweight='bold',
            ha='center', va='center', color=colors['controlador'])
    ax.text(9.75, 7.1, 'src/analysis/', fontsize=9, ha='center',
            va='center', color='#58D68D', family='monospace')

    # Módulos del controlador
    ctrl_modules = [
        ('vectorize.py', 'Pipeline de vectorizacion', 6.4),
        ('compare.py', 'Similitud de coseno', 5.6),
        ('docx_parser.py', 'Extraccion de imagenes', 4.8),
    ]

    for name, desc, y in ctrl_modules:
        mod_box = FancyBboxPatch((8.2, y - 0.3), 3.1, 0.6, boxstyle="round,pad=0.02",
                                  facecolor=colors['controlador'], edgecolor='#1E8449',
                                  linewidth=1, alpha=0.8)
        ax.add_patch(mod_box)
        ax.text(9.75, y + 0.05, name, fontsize=8, fontweight='bold',
                ha='center', va='center', color='white', family='monospace')
        ax.text(9.75, y - 0.2, desc, fontsize=7, ha='center', va='center', color='#E8F8F5')

    # Responsabilidades
    ax.text(9.75, 4.1, 'Responsabilidades:', fontsize=8, fontweight='bold',
            ha='center', color='#2C3E50')
    ctrl_resp = ['Procesar espectros', 'Calcular similitud', 'Coordinar flujo']
    for i, resp in enumerate(ctrl_resp):
        ax.text(9.75, 3.7 - i*0.35, f'• {resp}', fontsize=7, ha='center', color='#5D6D7E')

    # =========================================================================
    # MODELO (Base de Datos)
    # =========================================================================
    model_box = FancyBboxPatch((12.5, 3.5), 3, 5, boxstyle="round,pad=0.03",
                                facecolor='#FDEDEC', edgecolor=colors['modelo'],
                                linewidth=3)
    ax.add_patch(model_box)

    # Header
    model_header = FancyBboxPatch((12.5, 8), 3, 0.5, boxstyle="round,pad=0.01",
                                   facecolor=colors['modelo'], edgecolor=colors['modelo'])
    ax.add_patch(model_header)
    ax.text(14, 8.25, 'MODELO', fontsize=12, fontweight='bold',
            ha='center', va='center', color='white')

    # Contenido Modelo
    ax.text(14, 7.5, 'Capa de Datos', fontsize=10, fontweight='bold',
            ha='center', va='center', color=colors['modelo'])
    ax.text(14, 7.1, 'src/database/', fontsize=9, ha='center',
            va='center', color='#EC7063', family='monospace')

    # Componentes del modelo
    model_components = [
        ('models.py', 'ORM SQLAlchemy', 6.4),
        ('queries.py', 'Operaciones CRUD', 5.7),
        ('connection.py', 'Config conexion', 5.0),
    ]

    for name, desc, y in model_components:
        comp_box = FancyBboxPatch((12.7, y - 0.25), 2.6, 0.5, boxstyle="round,pad=0.02",
                                   facecolor=colors['modelo'], edgecolor='#C0392B',
                                   linewidth=1, alpha=0.8)
        ax.add_patch(comp_box)
        ax.text(14, y + 0.05, name, fontsize=8, fontweight='bold',
                ha='center', va='center', color='white', family='monospace')
        ax.text(14, y - 0.15, desc, fontsize=7, ha='center', va='center', color='#FADBD8')

    # Responsabilidades
    ax.text(14, 4.2, 'Responsabilidades:', fontsize=8, fontweight='bold',
            ha='center', color='#2C3E50')
    model_resp = ['Persistir datos', 'Consultar BD', 'Mapear objetos']
    for i, resp in enumerate(model_resp):
        ax.text(14, 3.8 - i*0.35, f'• {resp}', fontsize=7, ha='center', color='#5D6D7E')

    # =========================================================================
    # BASE DE DATOS (Abajo)
    # =========================================================================
    db_box = FancyBboxPatch((11.5, 1), 5, 1.5, boxstyle="round,pad=0.03",
                             facecolor='#FEF9E7', edgecolor=colors['db'],
                             linewidth=2)
    ax.add_patch(db_box)

    # Icono de BD
    db_icon = Circle((12.5, 1.75), 0.4, facecolor=colors['db'],
                      edgecolor='#D68910', linewidth=2)
    ax.add_patch(db_icon)
    ax.text(12.5, 1.75, 'DB', fontsize=10, fontweight='bold',
            ha='center', va='center', color='white')

    ax.text(14.5, 2.1, 'minerales_eds.db', fontsize=10, fontweight='bold',
            ha='center', va='center', color='#B7950B', family='monospace')
    ax.text(14.5, 1.7, 'SQLite - 101 espectros', fontsize=9,
            ha='center', va='center', color='#7F8C8D')
    ax.text(14.5, 1.35, 'muestras | espectros_vectorizados', fontsize=8,
            ha='center', va='center', color='#95A5A6', family='monospace')

    # =========================================================================
    # FLECHAS DE FLUJO
    # =========================================================================

    # Usuario -> Vista
    ax.annotate('', xy=(3.5, 6), xytext=(2.1, 6),
                arrowprops=dict(arrowstyle='->', color=colors['usuario'], lw=2.5))
    ax.text(2.8, 6.3, '1. Input', fontsize=8, ha='center', color=colors['usuario'], fontweight='bold')

    # Vista -> Controlador
    ax.annotate('', xy=(8, 6.5), xytext=(7, 6.5),
                arrowprops=dict(arrowstyle='->', color=colors['vista'], lw=2.5))
    ax.text(7.5, 6.85, '2. Solicitud', fontsize=8, ha='center', color=colors['vista'], fontweight='bold')

    # Controlador -> Modelo
    ax.annotate('', xy=(12.5, 6.5), xytext=(11.5, 6.5),
                arrowprops=dict(arrowstyle='->', color=colors['controlador'], lw=2.5))
    ax.text(12, 6.85, '3. Query', fontsize=8, ha='center', color=colors['controlador'], fontweight='bold')

    # Modelo -> BD
    ax.annotate('', xy=(14, 2.5), xytext=(14, 3.5),
                arrowprops=dict(arrowstyle='<->', color=colors['modelo'], lw=2.5))
    ax.text(14.6, 3, '4. SQL', fontsize=8, ha='left', color=colors['modelo'], fontweight='bold')

    # Modelo -> Controlador (respuesta)
    ax.annotate('', xy=(11.5, 5.5), xytext=(12.5, 5.5),
                arrowprops=dict(arrowstyle='->', color=colors['modelo'], lw=2, linestyle='--'))
    ax.text(12, 5.2, '5. Datos', fontsize=8, ha='center', color=colors['modelo'])

    # Controlador -> Vista (respuesta)
    ax.annotate('', xy=(7, 5.5), xytext=(8, 5.5),
                arrowprops=dict(arrowstyle='->', color=colors['controlador'], lw=2, linestyle='--'))
    ax.text(7.5, 5.2, '6. Resultado', fontsize=8, ha='center', color=colors['controlador'])

    # Vista -> Usuario (respuesta)
    ax.annotate('', xy=(2.1, 5.5), xytext=(3.5, 5.5),
                arrowprops=dict(arrowstyle='->', color=colors['vista'], lw=2, linestyle='--'))
    ax.text(2.8, 5.2, '7. Display', fontsize=8, ha='center', color=colors['vista'])

    # =========================================================================
    # FLUJO DE EJEMPLO
    # =========================================================================
    flow_box = FancyBboxPatch((0.5, 0.3), 10, 2.2, boxstyle="round,pad=0.03",
                               facecolor='#F8F9FA', edgecolor='#BDC3C7',
                               linewidth=1.5)
    ax.add_patch(flow_box)

    ax.text(5.5, 2.25, 'Ejemplo de Flujo: Identificar un Mineral', fontsize=10,
            fontweight='bold', ha='center', color='#2C3E50')

    flow_steps = [
        ('1', colors['usuario'], 'Usuario sube archivo DOCX'),
        ('2', colors['vista'], 'Vista recibe y muestra preview'),
        ('3', colors['controlador'], 'Controlador extrae y vectoriza imagen'),
        ('4', colors['modelo'], 'Modelo consulta vectores de la BD'),
        ('5', colors['controlador'], 'Controlador calcula similitud de coseno'),
        ('6', colors['vista'], 'Vista muestra Top 10 resultados'),
    ]

    for i, (num, color, text) in enumerate(flow_steps):
        x = 1 + (i % 3) * 3.2
        y = 1.6 if i < 3 else 0.8

        # Círculo con número
        circle = Circle((x, y), 0.2, facecolor=color, edgecolor='#2C3E50', linewidth=1)
        ax.add_patch(circle)
        ax.text(x, y, num, fontsize=9, fontweight='bold', ha='center', va='center', color='white')

        # Texto del paso
        ax.text(x + 0.35, y, text, fontsize=8, ha='left', va='center', color='#2C3E50')

    # =========================================================================
    # LEYENDA
    # =========================================================================
    legend_items = [
        ('Vista (UI)', colors['vista']),
        ('Controlador (Logica)', colors['controlador']),
        ('Modelo (Datos)', colors['modelo']),
        ('Base de Datos', colors['db']),
    ]

    for i, (label, color) in enumerate(legend_items):
        x = 11.5 + (i % 2) * 2.2
        y = 0.9 if i < 2 else 0.5
        rect = FancyBboxPatch((x, y - 0.15), 0.3, 0.3, boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#2C3E50')
        ax.add_patch(rect)
        ax.text(x + 0.4, y, label, fontsize=8, va='center', color='#2C3E50')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/diagrama_mvc.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print(f"Generado: {OUTPUT_DIR}/diagrama_mvc.png")


if __name__ == "__main__":
    generate_mvc_diagram()
    print("\nDiagrama MVC generado exitosamente.")
