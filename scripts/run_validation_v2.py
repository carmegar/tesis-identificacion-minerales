"""
Script de validacion mejorado del sistema de identificacion de minerales.
Version 2: Con comparacion de nombres robusta y diccionario de equivalencias.
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


# Diccionario de equivalencias para comparacion
# Incluye: traducciones espanol/ingles, variantes mineralogicas, y equivalencias quimicas
EQUIVALENCIAS = {
    # Nombres en espanol vs ingles
    "calcita": ["calcite", "calcita"],
    "pirita": ["pyrite", "pirita"],
    "biotita": ["biotite", "biotita"],
    "epidota": ["epidote", "epidota"],
    "galena": ["galena"],
    "magnetita": ["magnetite", "magnetita"],
    "hematita": ["hematite", "hematita"],
    "siderita": ["siderite", "siderita"],
    "barita": ["barite", "barita"],
    "fluorita": ["fluorite", "fluorita"],
    "apatita": ["apatite", "apatita"],
    "cuarzo": ["quartz", "cuarzo", "amatista", "amethyst"],
    "albita": ["albite", "albita"],
    "esfalerita": ["sphalerite", "esfalerita"],
    "calcopirita": ["chalcopyrite", "calcopirita"],
    "malaquita": ["malachite", "malaquita"],
    "yeso": ["gypsum", "yeso"],

    # CELESTINA/CELESTITE - ahora en BD
    "celestina": ["celestite", "celestina", "celestine"],
    "celestite": ["celestina", "celestine"],

    # AMATISTA = CUARZO (quimicamente identico, SiO2)
    # La amatista es cuarzo con impurezas de Fe que dan color morado
    # EDS mostrara solo Si y O, igual que cuarzo
    "amatista": ["quartz", "cuarzo", "amethyst", "amatista"],
    "amethyst": ["quartz", "cuarzo", "amatista"],

    # GOETHITA vs HEMATITA - ambos oxidos de hierro
    # Goethita: FeO(OH) - oxido de hierro hidratado
    # Hematita: Fe2O3 - oxido de hierro
    # EDS NO detecta H, asi que goethita aparece como Fe+O, similar a hematita
    "goethita": ["goethite", "goethita", "hematite", "hematita", "oxido de hierro"],
    "goethite": ["goethita", "hematite", "hematita"],

    # Variantes de oxido de hierro
    "oxido de hierro": ["oxido de fe", "hematita", "hematite", "hierro", "goethita", "goethite", "magnetita"],
    "oxido de fe": ["oxido de hierro", "hematita", "hematite", "hierro", "goethita"],
    "hierro": ["oxido de hierro", "hematita", "magnetita"],

    # Variantes de purpurita
    "purpurita": ["purpurita_real", "purpurita_verificada"],
    "purpurita_real": ["purpurita"],
    "purpurita_verificada": ["purpurita"],
}


def normalize_for_comparison(name):
    """Normaliza un nombre para comparacion."""
    name = name.lower().strip()
    # Eliminar sufijos numericos y variantes
    name = re.sub(r'[-_]\d+$', '', name)
    name = re.sub(r'[-_]muestra\d*$', '', name)
    name = re.sub(r'[-_]uis$', '', name)
    name = re.sub(r'[-_]data$', '', name)
    name = re.sub(r'[-_]amatista$', '', name)
    name = re.sub(r'_\d+ago$', '', name)
    # Normalizar caracteres especiales
    name = name.replace('ó', 'o').replace('í', 'i').replace('á', 'a')
    name = name.replace('é', 'e').replace('ú', 'u').replace('ñ', 'n')
    # Normalizar variantes de oxido
    name = name.replace('oxido_de_fe', 'oxido de hierro')
    name = name.replace('oxido de fe', 'oxido de hierro')
    return name.strip()


def are_minerals_equivalent(expected, predicted):
    """Verifica si dos nombres de minerales son equivalentes."""
    exp_norm = normalize_for_comparison(expected)
    pred_norm = normalize_for_comparison(predicted)

    # Comparacion directa
    if exp_norm == pred_norm:
        return True

    # Verificar si uno contiene al otro
    if exp_norm in pred_norm or pred_norm in exp_norm:
        return True

    # Verificar en diccionario de equivalencias
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


def run_validation():
    """Ejecuta la validacion completa."""

    print("="*70)
    print("VALIDACION DEL SISTEMA - VERSION 2 (MEJORADA)")
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

    # Archivos de prueba
    test_folder = Path("tests/test_data")
    test_files = list(test_folder.glob("*.docx"))

    # Filtrar archivos ya en BD
    db_paths = {m.ruta_imagen for m in muestras if m.ruta_imagen}
    test_files = [f for f in test_files if str(f) not in db_paths]

    print(f"Archivos de prueba disponibles: {len(test_files)}")

    # Resultados
    results = []
    correct = 0
    incorrect = 0
    failed = 0
    no_match_in_db = 0

    # Lista de minerales en BD para verificar cobertura
    db_minerals = {normalize_for_comparison(v['nombre']) for v in db_vectors}

    print("\nEjecutando validacion...\n")

    for test_file in test_files:
        expected_mineral = extract_mineral_name(test_file.name)

        try:
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

            similarities.sort(key=lambda x: x['similitud'], reverse=True)

            top_result = similarities[0]
            predicted = top_result['nombre']
            confidence = top_result['similitud']

            # Verificar si el mineral esperado existe en la BD
            expected_in_db = any(are_minerals_equivalent(expected_mineral, normalize_for_comparison(v['nombre']))
                                for v in db_vectors)

            # Verificar si es correcto usando comparacion mejorada
            is_correct = are_minerals_equivalent(expected_mineral, predicted)

            # Categoria del resultado
            if is_correct:
                categoria = "CORRECTO"
                correct += 1
            elif not expected_in_db:
                categoria = "NO EN BD"
                no_match_in_db += 1
                incorrect += 1
            else:
                categoria = "INCORRECTO"
                incorrect += 1

            results.append({
                'archivo': test_file.name,
                'esperado': expected_mineral,
                'predicho': predicted,
                'confianza': float(confidence),
                'correcto': is_correct,
                'categoria': categoria,
                'en_bd': expected_in_db,
                'top3': [s['nombre'] for s in similarities[:3]]
            })

            status = "[OK]" if is_correct else "[NO]" if expected_in_db else "[??]"
            print(f"  {status} {expected_mineral:20} -> {predicted:20} ({confidence:.1%}) {categoria}")

        except Exception as e:
            failed += 1

    session.close()

    # Calcular metricas
    total_evaluated = correct + incorrect
    accuracy = correct / total_evaluated if total_evaluated > 0 else 0

    # Accuracy excluyendo minerales no en BD
    total_con_cobertura = correct + (incorrect - no_match_in_db)
    accuracy_ajustado = correct / total_con_cobertura if total_con_cobertura > 0 else 0

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE VALIDACION")
    print("="*70)
    print(f"\nTotal de pruebas: {len(test_files)}")
    print(f"Evaluadas exitosamente: {total_evaluated}")
    print(f"Fallidas (sin imagen valida): {failed}")
    print(f"\nCorrectamente identificados: {correct}")
    print(f"Incorrectamente identificados: {incorrect}")
    print(f"  - De los cuales NO estan en BD: {no_match_in_db}")
    print(f"\n{'='*40}")
    print(f"ACCURACY GENERAL: {accuracy:.2%}")
    print(f"ACCURACY AJUSTADO (solo minerales en BD): {accuracy_ajustado:.2%}")
    print(f"{'='*40}")

    if results:
        confidences = [r['confianza'] for r in results]
        print(f"\nConfianza promedio: {np.mean(confidences):.2%}")
        print(f"Confianza minima: {np.min(confidences):.2%}")
        print(f"Confianza maxima: {np.max(confidences):.2%}")

    # Guardar resultados
    output = {
        'total_pruebas': len(test_files),
        'evaluadas': total_evaluated,
        'fallidas': failed,
        'correctas': correct,
        'incorrectas': incorrect,
        'no_en_bd': no_match_in_db,
        'accuracy': accuracy,
        'accuracy_ajustado': accuracy_ajustado,
        'confianza_promedio': float(np.mean(confidences)) if results else 0,
        'resultados': results
    }

    with open('validation_results_v2.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResultados guardados en: validation_results_v2.json")

    return output


if __name__ == "__main__":
    run_validation()
