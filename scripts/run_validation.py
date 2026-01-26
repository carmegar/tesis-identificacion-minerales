"""
Script de validación del sistema de identificación de minerales.
Ejecuta pruebas con espectros de test_data y calcula métricas.
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from src.analysis.vectorize import vectorize_spectrum
from src.analysis.compare import calcular_similitud
from src.parsers.docx_parser import extract_and_vectorize_spectrum
from src.database.connection import SessionLocal
from src.database.queries import get_all_muestras
from src.database.models import EspectroVectorizado


def extract_mineral_name(filename: str) -> str:
    """Extrae el nombre del mineral del nombre del archivo."""
    name = Path(filename).stem
    prefixes = ['EDS_', 'EDS ', 'Eds_', 'Eds ', 'Element ', 'Eds-']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = re.sub(r'[_-]\d+.*$', '', name)
    name = re.sub(r'_data$', '', name)
    return name.strip().lower()


def normalize_mineral_name(name: str) -> str:
    """Normaliza el nombre del mineral para comparación."""
    name = name.lower().strip()
    # Mapeo de nombres equivalentes
    equivalents = {
        'magnetita': 'magnetita',
        'calcita': 'calcite',
        'malaquita': 'malaquita',
        'pirita': 'pyrite',
        'biotita': 'biotite',
        'epidota': 'epidote',
        'goethita': 'goethita',
        'celestina': 'celestite',
        'galena': 'galena',
        'yeso': 'yeso',
        'calcite': 'calcite',
        'pyrite': 'pyrite',
        'biotite': 'biotite',
        'epidote': 'epidote',
    }
    return equivalents.get(name, name)


def run_validation():
    """Ejecuta la validación completa."""

    print("="*70)
    print("VALIDACIÓN DEL SISTEMA DE IDENTIFICACIÓN DE MINERALES")
    print("="*70)

    # Cargar todos los vectores de la BD
    session = SessionLocal()
    muestras = get_all_muestras(session)

    db_vectors = []
    for m in muestras:
        espectro = session.query(EspectroVectorizado).filter_by(muestra_id=m.id).first()
        if espectro:
            db_vectors.append({
                'id': m.id,
                'nombre': m.nombre_muestra,
                'vector': np.array(espectro.vector),
                'fuente': m.investigador
            })

    print(f"\nEspectros en BD de entrenamiento: {len(db_vectors)}")

    # Archivos de prueba (que no están en entrenamiento)
    test_folder = Path("tests/test_data")
    test_files = list(test_folder.glob("*.docx"))

    # Filtrar archivos que ya están en la BD
    db_paths = {m.ruta_imagen for m in muestras if m.ruta_imagen}
    test_files = [f for f in test_files if str(f) not in db_paths]

    print(f"Archivos de prueba disponibles: {len(test_files)}")

    # Resultados de validación
    results = []
    correct = 0
    incorrect = 0
    failed = 0

    print("\nEjecutando validación...\n")

    for test_file in test_files:
        expected_mineral = extract_mineral_name(test_file.name)

        try:
            # Vectorizar espectro de prueba
            vector = extract_and_vectorize_spectrum(str(test_file))

            if vector is None:
                failed += 1
                continue

            # Calcular similitud con todos los espectros de la BD
            similarities = []
            for db_item in db_vectors:
                sim = calcular_similitud(vector, db_item['vector'])
                similarities.append({
                    'nombre': db_item['nombre'],
                    'similitud': sim,
                    'fuente': db_item['fuente']
                })

            # Ordenar por similitud
            similarities.sort(key=lambda x: x['similitud'], reverse=True)

            # Top 1 resultado
            top_result = similarities[0]
            predicted = top_result['nombre'].lower()
            confidence = top_result['similitud']

            # Verificar si es correcto (comparación flexible)
            expected_norm = normalize_mineral_name(expected_mineral)
            predicted_norm = normalize_mineral_name(predicted)

            is_correct = (expected_norm in predicted_norm or
                         predicted_norm in expected_norm or
                         expected_norm == predicted_norm)

            results.append({
                'archivo': test_file.name,
                'esperado': expected_mineral,
                'predicho': top_result['nombre'],
                'confianza': confidence,
                'correcto': is_correct,
                'top3': [s['nombre'] for s in similarities[:3]]
            })

            if is_correct:
                correct += 1
                status = "✓"
            else:
                incorrect += 1
                status = "✗"

            print(f"  {status} {expected_mineral:20} → {top_result['nombre']:20} ({confidence:.2%})")

        except Exception as e:
            failed += 1
            print(f"  ! {test_file.name}: Error - {e}")

    session.close()

    # Calcular métricas
    total_evaluated = correct + incorrect
    accuracy = correct / total_evaluated if total_evaluated > 0 else 0

    # Calcular precisión por mineral
    mineral_stats = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})

    for r in results:
        expected = normalize_mineral_name(r['esperado'])
        predicted = normalize_mineral_name(r['predicho'].lower())

        if r['correcto']:
            mineral_stats[expected]['tp'] += 1
        else:
            mineral_stats[expected]['fn'] += 1
            mineral_stats[predicted]['fp'] += 1

    # Imprimir resumen
    print("\n" + "="*70)
    print("RESUMEN DE VALIDACIÓN")
    print("="*70)
    print(f"\nTotal de pruebas: {len(test_files)}")
    print(f"Evaluadas exitosamente: {total_evaluated}")
    print(f"Fallidas (sin imagen válida): {failed}")
    print(f"\nCorrectamente identificados: {correct}")
    print(f"Incorrectamente identificados: {incorrect}")
    print(f"\n{'='*30}")
    print(f"ACCURACY: {accuracy:.2%}")
    print(f"{'='*30}")

    # Distribución de confianza
    if results:
        confidences = [r['confianza'] for r in results]
        print(f"\nConfianza promedio: {np.mean(confidences):.2%}")
        print(f"Confianza mínima: {np.min(confidences):.2%}")
        print(f"Confianza máxima: {np.max(confidences):.2%}")

    # Guardar resultados en JSON
    output = {
        'total_pruebas': len(test_files),
        'evaluadas': total_evaluated,
        'fallidas': failed,
        'correctas': correct,
        'incorrectas': incorrect,
        'accuracy': accuracy,
        'confianza_promedio': float(np.mean(confidences)) if results else 0,
        'resultados': results
    }

    with open('validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResultados guardados en: validation_results.json")

    return output


if __name__ == "__main__":
    run_validation()
