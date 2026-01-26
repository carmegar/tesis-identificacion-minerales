"""
Genera 3 imagenes para la exposicion:
1. Resultados de pruebas de software
2. Comparacion objetivos vs logros
3. Concepto de vectorizacion
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Wedge, Arc
import matplotlib.patches as mpatches
import os

OUTPUT_DIR = "diagramas"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_testing_results():
    """Genera imagen visual de resultados de pruebas."""
    fig = plt.figure(figsize=(14, 10))

    # Titulo
    fig.text(0.5, 0.95, 'Resultados de Pruebas de Software', fontsize=20, fontweight='bold',
             ha='center', va='center', color='#2C3E50')
    fig.text(0.5, 0.90, 'Suite de testing automatizado con pytest', fontsize=12,
             ha='center', va='center', color='#7F8C8D', style='italic')

    # =========================================================================
    # SECCION 1: Metricas principales (circulos grandes)
    # =========================================================================
    ax_metrics = fig.add_axes([0.05, 0.55, 0.9, 0.32])
    ax_metrics.axis('off')
    ax_metrics.set_xlim(0, 10)
    ax_metrics.set_ylim(0, 3)

    metrics = [
        ('36', 'Tests\nTotales', '#3498DB', 1.5),
        ('97%', 'Tests\nExitosos', '#27AE60', 4),
        ('79%', 'Cobertura\nCodigo', '#9B59B6', 6.5),
        ('<1s', 'Tiempo\nEjecucion', '#E67E22', 9),
    ]

    for value, label, color, x in metrics:
        # Circulo grande
        circle = Circle((x, 1.5), 0.9, facecolor=color, edgecolor='#2C3E50',
                        linewidth=3, alpha=0.9)
        ax_metrics.add_patch(circle)
        # Valor
        ax_metrics.text(x, 1.65, value, fontsize=24, fontweight='bold',
                       ha='center', va='center', color='white')
        # Label
        ax_metrics.text(x, 1.1, label, fontsize=10, ha='center', va='center',
                       color='white')

    # =========================================================================
    # SECCION 2: Desglose de tests por tipo
    # =========================================================================
    ax_breakdown = fig.add_axes([0.05, 0.18, 0.45, 0.35])

    test_types = ['Unitarias', 'Integracion', 'Funcionales']
    test_counts = [23, 8, 5]
    colors = ['#3498DB', '#27AE60', '#E74C3C']

    bars = ax_breakdown.barh(test_types, test_counts, color=colors, edgecolor='#2C3E50',
                             linewidth=2, height=0.6)

    ax_breakdown.set_xlabel('Cantidad de tests', fontsize=11)
    ax_breakdown.set_title('Distribucion por Tipo de Prueba', fontsize=12,
                          fontweight='bold', pad=10)
    ax_breakdown.set_xlim(0, 30)
    ax_breakdown.grid(axis='x', alpha=0.3)

    # Agregar valores en las barras
    for bar, count in zip(bars, test_counts):
        ax_breakdown.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                         f'{count}', va='center', fontsize=12, fontweight='bold',
                         color='#2C3E50')

    # =========================================================================
    # SECCION 3: Modulos cubiertos
    # =========================================================================
    ax_modules = fig.add_axes([0.55, 0.18, 0.4, 0.35])
    ax_modules.axis('off')

    ax_modules.text(0.5, 0.95, 'Modulos con Cobertura', fontsize=12,
                   fontweight='bold', ha='center', transform=ax_modules.transAxes)

    modules = [
        ('vectorize.py', '85%', '#27AE60'),
        ('compare.py', '92%', '#27AE60'),
        ('queries.py', '78%', '#F39C12'),
        ('models.py', '70%', '#F39C12'),
        ('docx_parser.py', '65%', '#E67E22'),
    ]

    for i, (name, coverage, color) in enumerate(modules):
        y = 0.8 - i * 0.17
        # Barra de progreso
        rect_bg = FancyBboxPatch((0.05, y - 0.04), 0.7, 0.1,
                                  boxstyle="round,pad=0.02",
                                  facecolor='#ECF0F1', edgecolor='#BDC3C7',
                                  transform=ax_modules.transAxes)
        ax_modules.add_patch(rect_bg)

        width = float(coverage.replace('%', '')) / 100 * 0.7
        rect_fill = FancyBboxPatch((0.05, y - 0.04), width, 0.1,
                                    boxstyle="round,pad=0.02",
                                    facecolor=color, edgecolor='none',
                                    transform=ax_modules.transAxes)
        ax_modules.add_patch(rect_fill)

        ax_modules.text(0.02, y, name, fontsize=9, va='center',
                       transform=ax_modules.transAxes, family='monospace')
        ax_modules.text(0.78, y, coverage, fontsize=9, va='center',
                       fontweight='bold', color=color, transform=ax_modules.transAxes)

    # =========================================================================
    # SECCION 4: Resultado final
    # =========================================================================
    result_box = FancyBboxPatch((0.15, 0.02), 0.7, 0.12,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#27AE60', edgecolor='#1E8449',
                                 linewidth=3, transform=fig.transFigure)
    fig.patches.append(result_box)

    fig.text(0.5, 0.08, '✓ SISTEMA VALIDADO: 36/37 tests exitosos - Listo para produccion',
             fontsize=14, fontweight='bold', ha='center', va='center', color='white')

    plt.savefig(f'{OUTPUT_DIR}/resultados_pruebas.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("Generado: resultados_pruebas.png")


def generate_objectives_comparison():
    """Genera imagen comparando objetivos vs logros."""
    fig = plt.figure(figsize=(14, 10))

    # Titulo
    fig.text(0.5, 0.95, 'Cumplimiento de Objetivos del Proyecto', fontsize=20,
             fontweight='bold', ha='center', va='center', color='#2C3E50')
    fig.text(0.5, 0.90, 'Comparacion entre metas planteadas y resultados obtenidos',
             fontsize=12, ha='center', va='center', color='#7F8C8D', style='italic')

    # =========================================================================
    # Objetivos especificos con barras de progreso
    # =========================================================================
    ax_obj = fig.add_axes([0.08, 0.35, 0.84, 0.5])
    ax_obj.axis('off')

    objectives = [
        {
            'num': '1',
            'title': 'Base de datos con minimo 100 espectros',
            'target': 100,
            'achieved': 101,
            'unit': 'espectros',
            'status': 'SUPERADO',
            'color': '#27AE60'
        },
        {
            'num': '2',
            'title': 'Sistema de comparacion con similitud de coseno',
            'target': 100,
            'achieved': 100,
            'unit': '% implementado',
            'status': 'CUMPLIDO',
            'color': '#27AE60'
        },
        {
            'num': '3',
            'title': 'Aplicacion web funcional e integrada',
            'target': 100,
            'achieved': 100,
            'unit': '% funcional',
            'status': 'CUMPLIDO',
            'color': '#27AE60'
        },
        {
            'num': '4',
            'title': 'Validacion con minimo 100 espectros de prueba',
            'target': 100,
            'achieved': 54,
            'unit': 'espectros',
            'status': 'PARCIAL',
            'color': '#F39C12'
        },
    ]

    for i, obj in enumerate(objectives):
        y = 0.85 - i * 0.22

        # Numero de objetivo
        circle = Circle((0.03, y), 0.035, facecolor=obj['color'],
                        edgecolor='#2C3E50', linewidth=2, transform=ax_obj.transAxes)
        ax_obj.add_patch(circle)
        ax_obj.text(0.03, y, obj['num'], fontsize=12, fontweight='bold',
                   ha='center', va='center', color='white', transform=ax_obj.transAxes)

        # Titulo del objetivo
        ax_obj.text(0.08, y + 0.04, obj['title'], fontsize=11, fontweight='bold',
                   va='center', transform=ax_obj.transAxes, color='#2C3E50')

        # Barra de progreso (fondo)
        rect_bg = FancyBboxPatch((0.08, y - 0.06), 0.7, 0.06,
                                  boxstyle="round,pad=0.01",
                                  facecolor='#ECF0F1', edgecolor='#BDC3C7',
                                  transform=ax_obj.transAxes)
        ax_obj.add_patch(rect_bg)

        # Barra de progreso (logro)
        progress = min(obj['achieved'] / obj['target'], 1.0)
        rect_fill = FancyBboxPatch((0.08, y - 0.06), 0.7 * progress, 0.06,
                                    boxstyle="round,pad=0.01",
                                    facecolor=obj['color'], edgecolor='none',
                                    transform=ax_obj.transAxes)
        ax_obj.add_patch(rect_fill)

        # Meta (indicador)
        ax_obj.text(0.78, y - 0.03, '|', fontsize=16, va='center', ha='center',
                   transform=ax_obj.transAxes, color='#2C3E50', fontweight='bold')

        # Valores
        ax_obj.text(0.82, y - 0.03, f'{obj["achieved"]}/{obj["target"]}',
                   fontsize=10, va='center', transform=ax_obj.transAxes,
                   color='#2C3E50', fontweight='bold')
        ax_obj.text(0.82, y - 0.07, obj['unit'], fontsize=8, va='center',
                   transform=ax_obj.transAxes, color='#7F8C8D')

        # Status badge
        badge = FancyBboxPatch((0.92, y - 0.04), 0.07, 0.05,
                                boxstyle="round,pad=0.01",
                                facecolor=obj['color'], edgecolor='none',
                                transform=ax_obj.transAxes)
        ax_obj.add_patch(badge)
        ax_obj.text(0.955, y - 0.015, obj['status'], fontsize=7,
                   ha='center', va='center', color='white', fontweight='bold',
                   transform=ax_obj.transAxes)

    # =========================================================================
    # Resumen estadistico
    # =========================================================================
    ax_summary = fig.add_axes([0.08, 0.08, 0.84, 0.22])
    ax_summary.axis('off')

    # Caja de resumen
    summary_box = FancyBboxPatch((0.02, 0.1), 0.96, 0.85,
                                  boxstyle="round,pad=0.02",
                                  facecolor='#EBF5FB', edgecolor='#3498DB',
                                  linewidth=2, transform=ax_summary.transAxes)
    ax_summary.add_patch(summary_box)

    ax_summary.text(0.5, 0.8, 'RESUMEN DE CUMPLIMIENTO', fontsize=12,
                   fontweight='bold', ha='center', transform=ax_summary.transAxes,
                   color='#2C3E50')

    # Metricas de resumen
    summary_metrics = [
        ('3/4', 'Objetivos\nCumplidos', '#27AE60'),
        ('75%', 'Tasa de\nExito', '#27AE60'),
        ('101', 'Espectros en\nBase de Datos', '#3498DB'),
        ('64.8%', 'Accuracy de\nIdentificacion', '#9B59B6'),
    ]

    for i, (value, label, color) in enumerate(summary_metrics):
        x = 0.12 + i * 0.22
        ax_summary.text(x, 0.5, value, fontsize=20, fontweight='bold',
                       ha='center', va='center', color=color,
                       transform=ax_summary.transAxes)
        ax_summary.text(x, 0.22, label, fontsize=9, ha='center', va='center',
                       color='#5D6D7E', transform=ax_summary.transAxes)

    # Mensaje final positivo
    final_box = FancyBboxPatch((0.1, 0.01), 0.8, 0.08,
                                boxstyle="round,pad=0.02",
                                facecolor='#27AE60', edgecolor='#1E8449',
                                linewidth=2, transform=fig.transFigure)
    fig.patches.append(final_box)

    fig.text(0.5, 0.05, '✓ PROYECTO EXITOSO: Sistema funcional desplegado en produccion',
             fontsize=13, fontweight='bold', ha='center', va='center', color='white')

    plt.savefig(f'{OUTPUT_DIR}/comparacion_objetivos.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("Generado: comparacion_objetivos.png")


def generate_vectorization_concept():
    """Genera imagen explicando el concepto de vectorizacion."""
    fig = plt.figure(figsize=(16, 9))

    # Titulo
    fig.text(0.5, 0.95, 'Concepto de Vectorizacion de Espectros EDS', fontsize=20,
             fontweight='bold', ha='center', va='center', color='#2C3E50')
    fig.text(0.5, 0.90, 'Transformacion de imagen 2D a vector numerico 1D para comparacion matematica',
             fontsize=12, ha='center', va='center', color='#7F8C8D', style='italic')

    # =========================================================================
    # IMAGEN 2D (Espectro original)
    # =========================================================================
    ax1 = fig.add_axes([0.03, 0.35, 0.25, 0.45])

    # Crear espectro simulado 2D
    np.random.seed(42)
    spectrum_2d = np.zeros((100, 200))
    # Agregar picos
    for pos, height, width in [(40, 0.9, 8), (100, 0.6, 10), (150, 1.0, 6), (180, 0.4, 12)]:
        for row in range(100):
            spectrum_2d[row, :] += height * np.exp(-((np.arange(200) - pos) ** 2) / (2 * width**2))
    # Agregar ruido
    spectrum_2d += np.random.normal(0, 0.05, spectrum_2d.shape)
    spectrum_2d = np.clip(spectrum_2d, 0, 1)

    ax1.imshow(spectrum_2d, cmap='hot', aspect='auto')
    ax1.set_title('1. Imagen del Espectro\n(Matriz 2D)', fontsize=11, fontweight='bold', pad=10)
    ax1.set_xlabel('Energia (pixeles)', fontsize=9)
    ax1.set_ylabel('Intensidad (filas)', fontsize=9)

    # Dimensiones
    ax1.text(0.5, -0.15, '200 x 100 pixeles', fontsize=9, ha='center',
             transform=ax1.transAxes, color='#7F8C8D')

    # =========================================================================
    # FLECHA 1
    # =========================================================================
    fig.text(0.30, 0.57, '→', fontsize=40, ha='center', va='center', color='#3498DB')
    fig.text(0.30, 0.50, 'Media por\ncolumna', fontsize=9, ha='center', va='center',
             color='#3498DB', fontweight='bold')

    # =========================================================================
    # PERFIL 1D (Firma espectral)
    # =========================================================================
    ax2 = fig.add_axes([0.35, 0.35, 0.25, 0.45])

    # Calcular perfil 1D
    profile_1d = np.mean(spectrum_2d, axis=0)

    ax2.plot(profile_1d, color='#E74C3C', linewidth=2)
    ax2.fill_between(range(len(profile_1d)), profile_1d, alpha=0.3, color='#E74C3C')
    ax2.set_title('2. Perfil Espectral\n(Vector 1D)', fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel('Posicion', fontsize=9)
    ax2.set_ylabel('Intensidad media', fontsize=9)
    ax2.set_xlim(0, 200)
    ax2.grid(alpha=0.3)

    # Dimensiones
    ax2.text(0.5, -0.15, '200 valores', fontsize=9, ha='center',
             transform=ax2.transAxes, color='#7F8C8D')

    # =========================================================================
    # FLECHA 2
    # =========================================================================
    fig.text(0.62, 0.57, '→', fontsize=40, ha='center', va='center', color='#27AE60')
    fig.text(0.62, 0.50, 'Normalizar\nL2', fontsize=9, ha='center', va='center',
             color='#27AE60', fontweight='bold')

    # =========================================================================
    # VECTOR NORMALIZADO
    # =========================================================================
    ax3 = fig.add_axes([0.67, 0.35, 0.30, 0.45])

    # Normalizar
    normalized = profile_1d / np.linalg.norm(profile_1d)

    # Mostrar como barras
    colors = ['#E74C3C' if v > normalized.mean() + normalized.std() else '#3498DB'
              for v in normalized]
    ax3.bar(range(len(normalized)), normalized, color=colors, width=1.0, alpha=0.8)
    ax3.set_title('3. Vector Final Normalizado\n(||v|| = 1.0)', fontsize=11, fontweight='bold', pad=10)
    ax3.set_xlabel('Dimension', fontsize=9)
    ax3.set_ylabel('Valor normalizado', fontsize=9)
    ax3.set_xlim(0, 200)
    ax3.grid(alpha=0.3, axis='y')

    # Dimensiones
    ax3.text(0.5, -0.15, '200 floats normalizados', fontsize=9, ha='center',
             transform=ax3.transAxes, color='#7F8C8D')

    # =========================================================================
    # REPRESENTACION MATEMATICA
    # =========================================================================
    ax_math = fig.add_axes([0.05, 0.05, 0.9, 0.22])
    ax_math.axis('off')

    # Caja de fondo
    math_box = FancyBboxPatch((0.02, 0.1), 0.96, 0.85,
                               boxstyle="round,pad=0.02",
                               facecolor='#F8F9FA', edgecolor='#BDC3C7',
                               linewidth=2, transform=ax_math.transAxes)
    ax_math.add_patch(math_box)

    ax_math.text(0.5, 0.8, 'Representacion Matematica del Vector', fontsize=12,
                fontweight='bold', ha='center', transform=ax_math.transAxes, color='#2C3E50')

    # Vector como array
    vector_text = 'v = [0.0521, 0.0489, 0.0612, 0.0834, 0.1245, ..., 0.0523, 0.0412, 0.0398]'
    ax_math.text(0.5, 0.55, vector_text, fontsize=11, ha='center',
                transform=ax_math.transAxes, color='#2C3E50', family='monospace',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='#BDC3C7'))

    # Propiedades
    props = [
        ('200 dimensiones', '#3498DB'),
        ('Norma = 1.0', '#27AE60'),
        ('Valores en [0, 1]', '#9B59B6'),
        ('Invariante a escala', '#E74C3C'),
    ]

    for i, (prop, color) in enumerate(props):
        x = 0.12 + i * 0.22
        badge = FancyBboxPatch((x - 0.08, 0.15), 0.16, 0.18,
                                boxstyle="round,pad=0.02",
                                facecolor=color, edgecolor='none', alpha=0.9,
                                transform=ax_math.transAxes)
        ax_math.add_patch(badge)
        ax_math.text(x, 0.24, prop, fontsize=9, ha='center', va='center',
                    color='white', fontweight='bold', transform=ax_math.transAxes)

    plt.savefig(f'{OUTPUT_DIR}/concepto_vectorizacion.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("Generado: concepto_vectorizacion.png")


def main():
    """Genera las 3 imagenes solicitadas."""
    print("=" * 60)
    print("GENERANDO IMAGENES PARA EXPOSICION")
    print("=" * 60)
    print()

    generate_testing_results()
    generate_objectives_comparison()
    generate_vectorization_concept()

    print()
    print("=" * 60)
    print("COMPLETADO: 3 imagenes generadas en diagramas/")
    print("=" * 60)


if __name__ == "__main__":
    main()
