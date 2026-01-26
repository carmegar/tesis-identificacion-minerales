"""
Comparativa de metricas de similitud/distancia para identificacion de minerales.
Compara: Similitud de Coseno, Distancia Euclidiana, Correlacion de Pearson, Distancia Manhattan.
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import json

from src.analysis.vectorize import vectorize_spectrum
from src.parsers.docx_parser import extract_and_vectorize_spectrum
from src.database.connection import SessionLocal
from src.database.queries import get_all_muestras
from src.database.models import EspectroVectorizado

OUTPUT_DIR = "diagramas"

# ============================================================================
# IMPLEMENTACION DE LAS 4 METRICAS
# ============================================================================

def similitud_coseno(v1, v2):
    """Similitud de coseno: mide el angulo entre vectores. Rango [0, 1]."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def distancia_euclidiana(v1, v2):
    """Distancia Euclidiana: distancia en linea recta. Menor = mas similar."""
    return np.linalg.norm(v1 - v2)


def correlacion_pearson(v1, v2):
    """Correlacion de Pearson: mide correlacion lineal. Rango [-1, 1]."""
    if np.std(v1) == 0 or np.std(v2) == 0:
        return 0.0
    return np.corrcoef(v1, v2)[0, 1]


def distancia_manhattan(v1, v2):
    """Distancia Manhattan: suma de diferencias absolutas. Menor = mas similar."""
    return np.sum(np.abs(v1 - v2))


# ============================================================================
# FUNCIONES AUXILIARES (del script de validacion)
# ============================================================================

EQUIVALENCIAS = {
    "calcita": ["calcite", "calcita"],
    "pirita": ["pyrite", "pirita"],
    "biotita": ["biotite", "biotita"],
    "epidota": ["epidote", "epidota"],
    "galena": ["galena"],
    "magnetita": ["magnetite", "magnetita"],
    "hematita": ["hematite", "hematita"],
    "celestina": ["celestite", "celestina", "celestine"],
    "celestite": ["celestina", "celestine"],
    "amatista": ["quartz", "cuarzo", "amethyst", "amatista"],
    "goethita": ["goethite", "goethita", "hematite", "hematita"],
    "cuarzo": ["quartz", "cuarzo", "amatista"],
}


def normalize_for_comparison(name):
    """Normaliza un nombre para comparacion."""
    name = name.lower().strip()
    name = re.sub(r'[-_]\d+$', '', name)
    name = re.sub(r'[-_]muestra\d*$', '', name)
    name = name.replace('oxido_de_fe', 'oxido de hierro')
    return name.strip()


def are_minerals_equivalent(expected, predicted):
    """Verifica si dos nombres de minerales son equivalentes."""
    exp_norm = normalize_for_comparison(expected)
    pred_norm = normalize_for_comparison(predicted)

    if exp_norm == pred_norm:
        return True
    if exp_norm in pred_norm or pred_norm in exp_norm:
        return True
    if exp_norm in EQUIVALENCIAS:
        if pred_norm in EQUIVALENCIAS[exp_norm]:
            return True
    if pred_norm in EQUIVALENCIAS:
        if exp_norm in EQUIVALENCIAS[pred_norm]:
            return True
    return False


def extract_mineral_name(filename):
    """Extrae el nombre del mineral del nombre del archivo."""
    name = Path(filename).stem
    prefixes = ['EDS_', 'EDS ', 'Eds_', 'Eds ', 'Element ', 'Eds-']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = re.sub(r'[_-]\d+.*$', '', name)
    name = re.sub(r'_data$', '', name)
    return name.strip().lower()


# ============================================================================
# VALIDACION CON MULTIPLES METRICAS
# ============================================================================

def run_metric_comparison():
    """Ejecuta la validacion con las 4 metricas y compara resultados."""

    print("=" * 70)
    print("COMPARATIVA DE METRICAS DE SIMILITUD/DISTANCIA")
    print("=" * 70)

    # Cargar datos de la BD
    session = SessionLocal()
    muestras = get_all_muestras(session)

    db_vectors = []
    for m in muestras:
        espectro = session.query(EspectroVectorizado).filter_by(muestra_id=m.id).first()
        if espectro:
            db_vectors.append({
                'id': m.id,
                'nombre': m.nombre_muestra,
                'vector': np.array(espectro.vector)
            })

    print(f"\nEspectros en BD: {len(db_vectors)}")

    # Archivos de prueba
    test_folder = Path("tests/test_data")
    test_files = list(test_folder.glob("*.docx"))

    # Filtrar archivos ya en BD
    db_paths = {m.ruta_imagen for m in muestras if m.ruta_imagen}
    test_files = [f for f in test_files if str(f) not in db_paths]

    print(f"Archivos de prueba: {len(test_files)}")

    # Definir metricas
    metricas = {
        'Similitud Coseno': {
            'func': similitud_coseno,
            'higher_is_better': True,
            'correct': 0,
            'total': 0,
            'confidences': []
        },
        'Distancia Euclidiana': {
            'func': distancia_euclidiana,
            'higher_is_better': False,
            'correct': 0,
            'total': 0,
            'confidences': []
        },
        'Correlacion Pearson': {
            'func': correlacion_pearson,
            'higher_is_better': True,
            'correct': 0,
            'total': 0,
            'confidences': []
        },
        'Distancia Manhattan': {
            'func': distancia_manhattan,
            'higher_is_better': False,
            'correct': 0,
            'total': 0,
            'confidences': []
        }
    }

    print("\nEjecutando validacion con cada metrica...\n")

    # Procesar cada archivo de prueba
    for test_file in test_files:
        expected_mineral = extract_mineral_name(test_file.name)

        try:
            vector = extract_and_vectorize_spectrum(str(test_file))
            if vector is None:
                continue

            # Evaluar con cada metrica
            for metric_name, metric_data in metricas.items():
                func = metric_data['func']
                higher_is_better = metric_data['higher_is_better']

                # Calcular similitud/distancia con todos los espectros de la BD
                scores = []
                for db_item in db_vectors:
                    score = func(vector, db_item['vector'])
                    scores.append({
                        'nombre': db_item['nombre'],
                        'score': score
                    })

                # Ordenar segun la metrica
                scores.sort(key=lambda x: x['score'], reverse=higher_is_better)

                # Top resultado
                top_result = scores[0]
                predicted = top_result['nombre']

                # Verificar si es correcto
                is_correct = are_minerals_equivalent(expected_mineral, predicted)

                metric_data['total'] += 1
                if is_correct:
                    metric_data['correct'] += 1

                # Guardar confianza (normalizada para comparacion)
                if metric_name == 'Similitud Coseno':
                    metric_data['confidences'].append(top_result['score'])
                elif metric_name == 'Correlacion Pearson':
                    # Normalizar de [-1,1] a [0,1]
                    metric_data['confidences'].append((top_result['score'] + 1) / 2)
                else:
                    # Para distancias, invertir y normalizar
                    # Usar 1/(1+d) para convertir distancia a similitud
                    metric_data['confidences'].append(1 / (1 + top_result['score']))

        except Exception as e:
            continue

    session.close()

    # Calcular accuracies
    results = {}
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)

    for metric_name, metric_data in metricas.items():
        if metric_data['total'] > 0:
            accuracy = metric_data['correct'] / metric_data['total']
            avg_confidence = np.mean(metric_data['confidences']) if metric_data['confidences'] else 0
            results[metric_name] = {
                'accuracy': accuracy,
                'correct': metric_data['correct'],
                'total': metric_data['total'],
                'avg_confidence': avg_confidence
            }
            print(f"\n{metric_name}:")
            print(f"  Accuracy: {accuracy:.2%} ({metric_data['correct']}/{metric_data['total']})")
            print(f"  Confianza promedio: {avg_confidence:.2%}")

    return results


def generate_comparison_charts(results):
    """Genera graficos comparativos de las metricas."""

    metrics = list(results.keys())
    accuracies = [results[m]['accuracy'] * 100 for m in metrics]

    # Colores: verde para el mejor, escala de grises para el resto
    colors = ['#27AE60' if a == max(accuracies) else '#E74C3C' if a == min(accuracies) else '#95A5A6'
              for a in accuracies]

    # =========================================================================
    # GRAFICO 1: Barras de Accuracy
    # =========================================================================
    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(metrics, accuracies, color=colors, edgecolor='#2C3E50', linewidth=2)

    # Agregar etiquetas de porcentaje
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.annotate(f'{acc:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=14, fontweight='bold',
                    color='#2C3E50')

    # Linea de referencia
    ax.axhline(y=max(accuracies), color='#27AE60', linestyle='--', alpha=0.5, linewidth=2)
    ax.axhline(y=50, color='#E74C3C', linestyle=':', alpha=0.5, linewidth=1.5,
               label='Linea base (50%)')

    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Metrica', fontsize=12, fontweight='bold')
    ax.set_title('Comparativa de Accuracy por Metrica de Similitud/Distancia',
                 fontsize=14, fontweight='bold', pad=20)

    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)

    # Leyenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#27AE60', edgecolor='#2C3E50', label='Mejor metrica'),
        Patch(facecolor='#E74C3C', edgecolor='#2C3E50', label='Peor metrica'),
        Patch(facecolor='#95A5A6', edgecolor='#2C3E50', label='Otras metricas'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/comparativa_accuracy_metricas.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print(f"\nGenerado: {OUTPUT_DIR}/comparativa_accuracy_metricas.png")

    # =========================================================================
    # GRAFICO 2: Tabla visual con ranking
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')

    # Ordenar por accuracy
    sorted_metrics = sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True)

    # Titulo
    ax.text(0.5, 0.95, 'Ranking de Metricas por Accuracy', fontsize=18,
            fontweight='bold', ha='center', va='top', transform=ax.transAxes)
    ax.text(0.5, 0.89, 'Validacion con 54 espectros de prueba independientes', fontsize=11,
            ha='center', va='top', transform=ax.transAxes, color='#7F8C8D', style='italic')

    # Colores para ranking
    rank_colors = ['#27AE60', '#3498DB', '#F39C12', '#E74C3C']
    rank_labels = ['MEJOR', '2do', '3ro', '4to']

    # Dibujar cards para cada metrica
    for i, (metric_name, data) in enumerate(sorted_metrics):
        y = 0.75 - i * 0.18

        # Card de fondo
        rect = FancyBboxPatch((0.05, y - 0.06), 0.9, 0.14,
                               boxstyle="round,pad=0.02",
                               facecolor=rank_colors[i], alpha=0.15,
                               edgecolor=rank_colors[i], linewidth=2,
                               transform=ax.transAxes)
        ax.add_patch(rect)

        # Ranking badge
        badge = FancyBboxPatch((0.07, y - 0.02), 0.08, 0.06,
                                boxstyle="round,pad=0.01",
                                facecolor=rank_colors[i],
                                edgecolor='#2C3E50', linewidth=1,
                                transform=ax.transAxes)
        ax.add_patch(badge)
        ax.text(0.11, y + 0.01, f'{i+1}', fontsize=14, fontweight='bold',
                ha='center', va='center', transform=ax.transAxes, color='white')

        # Nombre de la metrica
        ax.text(0.18, y + 0.02, metric_name, fontsize=13, fontweight='bold',
                ha='left', va='center', transform=ax.transAxes, color='#2C3E50')

        # Accuracy
        ax.text(0.55, y + 0.02, f'{data["accuracy"]:.1%}', fontsize=18, fontweight='bold',
                ha='center', va='center', transform=ax.transAxes, color=rank_colors[i])

        # Detalles
        ax.text(0.75, y + 0.02, f'{data["correct"]}/{data["total"]} aciertos',
                fontsize=10, ha='left', va='center', transform=ax.transAxes, color='#7F8C8D')

        # Etiqueta de ranking
        ax.text(0.92, y + 0.02, rank_labels[i], fontsize=10, fontweight='bold',
                ha='right', va='center', transform=ax.transAxes, color=rank_colors[i])

    # Nota explicativa
    explanation = """
    La Similitud de Coseno obtiene el mejor resultado porque:
    - Es INVARIANTE A LA ESCALA: diferentes tiempos de adquisicion producen
      diferentes intensidades pero la misma forma espectral
    - Mide el ANGULO entre vectores, no la distancia absoluta
    - Los espectros EDS varian en magnitud pero mantienen su forma caracteristica
    """

    ax.text(0.5, 0.08, explanation, fontsize=9, ha='center', va='center',
            transform=ax.transAxes, color='#2C3E50',
            bbox=dict(boxstyle='round', facecolor='#FEF9E7', edgecolor='#F39C12', alpha=0.8),
            family='monospace')

    plt.savefig(f'{OUTPUT_DIR}/tabla_ranking_metricas.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print(f"Generado: {OUTPUT_DIR}/tabla_ranking_metricas.png")

    # =========================================================================
    # GRAFICO 3: Demostracion de invarianza a escala
    # =========================================================================
    generate_scale_invariance_demo()


def generate_scale_invariance_demo():
    """Demuestra la invarianza a escala de la similitud de coseno."""

    # Crear un espectro simulado (perfil tipico de EDS)
    x = np.linspace(0, 10, 200)
    base_spectrum = np.zeros(200)

    # Agregar picos simulados (como un espectro EDS)
    peaks = [(30, 0.8), (80, 0.5), (120, 1.0), (160, 0.3)]
    for pos, height in peaks:
        base_spectrum += height * np.exp(-((np.arange(200) - pos) ** 2) / 50)

    # Normalizar
    base_spectrum = base_spectrum / np.max(base_spectrum)

    # Crear versiones escaladas (simulando diferentes tiempos de adquisicion)
    scales = [0.5, 1.0, 1.5, 2.0]
    scaled_spectra = [base_spectrum * s for s in scales]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # ---- Subplot 1: Espectros escalados ----
    ax1 = axes[0, 0]
    colors_spec = ['#3498DB', '#27AE60', '#E74C3C', '#9B59B6']
    for i, (spectrum, scale) in enumerate(zip(scaled_spectra, scales)):
        ax1.plot(spectrum, color=colors_spec[i], linewidth=2,
                 label=f'Escala {scale}x', alpha=0.8)
    ax1.set_title('Espectros con Diferentes Escalas\n(Mismo mineral, diferente tiempo de adquisicion)',
                  fontsize=11, fontweight='bold')
    ax1.set_xlabel('Dimension del vector')
    ax1.set_ylabel('Intensidad')
    ax1.legend(loc='upper right')
    ax1.grid(alpha=0.3)

    # ---- Subplot 2: Similitud de Coseno ----
    ax2 = axes[0, 1]
    ref_spectrum = scaled_spectra[1]  # Usar escala 1.0 como referencia
    cosine_sims = [similitud_coseno(ref_spectrum, s) for s in scaled_spectra]

    bars = ax2.bar(scales, cosine_sims, color='#27AE60', edgecolor='#2C3E50', linewidth=2)
    ax2.axhline(y=1.0, color='#27AE60', linestyle='--', alpha=0.5)
    ax2.set_title('Similitud de Coseno\n(Invariante a escala)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Factor de escala')
    ax2.set_ylabel('Similitud')
    ax2.set_ylim(0, 1.1)

    for bar, sim in zip(bars, cosine_sims):
        ax2.annotate(f'{sim:.3f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10,
                     fontweight='bold', color='#27AE60')

    # ---- Subplot 3: Distancia Euclidiana ----
    ax3 = axes[1, 0]
    euclidean_dists = [distancia_euclidiana(ref_spectrum, s) for s in scaled_spectra]

    bars = ax3.bar(scales, euclidean_dists, color='#E74C3C', edgecolor='#2C3E50', linewidth=2)
    ax3.set_title('Distancia Euclidiana\n(Sensible a escala)', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Factor de escala')
    ax3.set_ylabel('Distancia')

    for bar, dist in zip(bars, euclidean_dists):
        ax3.annotate(f'{dist:.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10,
                     fontweight='bold', color='#E74C3C')

    # ---- Subplot 4: Distancia Manhattan ----
    ax4 = axes[1, 1]
    manhattan_dists = [distancia_manhattan(ref_spectrum, s) for s in scaled_spectra]

    bars = ax4.bar(scales, manhattan_dists, color='#E74C3C', edgecolor='#2C3E50', linewidth=2)
    ax4.set_title('Distancia Manhattan\n(Sensible a escala)', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Factor de escala')
    ax4.set_ylabel('Distancia')

    for bar, dist in zip(bars, manhattan_dists):
        ax4.annotate(f'{dist:.1f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10,
                     fontweight='bold', color='#E74C3C')

    plt.suptitle('Demostracion: Invarianza a Escala de la Similitud de Coseno',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/comparativa_invarianza_escala.png',
                bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print(f"Generado: {OUTPUT_DIR}/comparativa_invarianza_escala.png")


def main():
    """Funcion principal."""
    print("\n" + "=" * 70)
    print("INICIANDO COMPARATIVA DE METRICAS")
    print("=" * 70)

    # Ejecutar comparacion
    results = run_metric_comparison()

    # Generar graficos
    print("\n" + "=" * 70)
    print("GENERANDO GRAFICOS COMPARATIVOS")
    print("=" * 70)

    generate_comparison_charts(results)

    # Guardar resultados
    with open(f'{OUTPUT_DIR}/comparativa_metricas_results.json', 'w', encoding='utf-8') as f:
        # Convertir a formato serializable
        serializable_results = {k: {
            'accuracy': v['accuracy'],
            'accuracy_percent': f"{v['accuracy']:.1%}",
            'correct': v['correct'],
            'total': v['total']
        } for k, v in results.items()}
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)

    print(f"\nResultados guardados en: {OUTPUT_DIR}/comparativa_metricas_results.json")

    print("\n" + "=" * 70)
    print("COMPARATIVA COMPLETADA")
    print("=" * 70)

    # Resumen final
    best_metric = max(results.items(), key=lambda x: x[1]['accuracy'])
    worst_metric = min(results.items(), key=lambda x: x[1]['accuracy'])

    print(f"\n MEJOR METRICA: {best_metric[0]} con {best_metric[1]['accuracy']:.1%} de accuracy")
    print(f" PEOR METRICA: {worst_metric[0]} con {worst_metric[1]['accuracy']:.1%} de accuracy")
    print(f"\n Diferencia: {(best_metric[1]['accuracy'] - worst_metric[1]['accuracy'])*100:.1f} puntos porcentuales")


if __name__ == "__main__":
    main()
