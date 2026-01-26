#!/usr/bin/env python3
"""
Script principal para ejecutar todas las pruebas del sistema de identificación de minerales.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_environment():
    """Configura el entorno para las pruebas."""
    os.environ['TESTING'] = '1'
    os.environ['PYTHONPATH'] = str(Path.cwd())


def run_tests(test_type='all', verbose=False, coverage=False, fast=False):
    """
    Ejecuta pruebas según el tipo especificado.
    
    Args:
        test_type: Tipo de pruebas ('unit', 'integration', 'functional', 'all')
        verbose: Mostrar salida detallada
        coverage: Generar reporte de cobertura
        fast: Ejecutar solo pruebas rápidas
    """
    setup_environment()
    
    # Comandos base
    cmd = ['pytest']
    
    # Configurar directorio de pruebas según el tipo
    if test_type == 'unit':
        cmd.append('tests/unit')
    elif test_type == 'integration':
        cmd.append('tests/integration') 
    elif test_type == 'functional':
        cmd.append('tests/functional')
    elif test_type == 'all':
        cmd.append('tests/')
    else:
        print(f"Tipo de prueba inválido: {test_type}")
        return False
    
    # Opciones de pytest
    if verbose:
        cmd.extend(['-v', '-s'])
    else:
        cmd.append('-q')
    
    # Filtros de marcadores
    if fast:
        cmd.extend(['-m', 'not slow'])
    
    # Cobertura
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    # Opciones adicionales
    cmd.extend(['--tb=short', '--strict-markers'])
    
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: pytest no está instalado. Ejecuta: pip install pytest")
        return False
    except Exception as e:
        print(f"Error ejecutando pruebas: {e}")
        return False


def validate_test_environment():
    """Valida que el entorno de pruebas esté correctamente configurado."""
    print("🔍 Validando entorno de pruebas...")
    
    issues = []
    
    # Verificar estructura de directorios
    required_dirs = [
        'tests/',
        'tests/unit/', 
        'tests/integration/',
        'tests/functional/',
        'tests/fixtures/',
        'tests/test_data/',
        'src/',
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"❌ Directorio faltante: {dir_path}")
        else:
            print(f"✅ Directorio encontrado: {dir_path}")
    
    # Verificar archivos de configuración
    config_files = [
        'pytest.ini',
        'tests/conftest.py',
        'tests/fixtures/test_data_manager.py'
    ]
    
    for file_path in config_files:
        if not Path(file_path).exists():
            issues.append(f"❌ Archivo faltante: {file_path}")
        else:
            print(f"✅ Archivo de configuración: {file_path}")
    
    # Verificar datos de prueba
    test_data_path = Path('tests/test_data')
    if test_data_path.exists():
        docx_files = list(test_data_path.glob('*.docx'))
        print(f"✅ Archivos DOCX disponibles: {len(docx_files)}")
        if len(docx_files) < 5:
            issues.append(f"⚠️  Pocos archivos DOCX: {len(docx_files)} (recomendado: >5)")
    else:
        issues.append("❌ Directorio test_data no encontrado")
    
    # Verificar dependencias
    try:
        import pytest
        print("✅ pytest está instalado")
    except ImportError:
        issues.append("❌ pytest no está instalado")
    
    try:
        import numpy
        print("✅ numpy está disponible") 
    except ImportError:
        issues.append("❌ numpy no está disponible")
    
    # Verificar módulos del proyecto
    try:
        from src.analysis.vectorize import vectorize_spectrum
        from src.analysis.compare import compare_spectrum
        from src.database.connection import SessionLocal
        print("✅ Módulos del proyecto importables")
    except ImportError as e:
        issues.append(f"❌ Error importando módulos: {e}")
    
    # Mostrar resultados
    if issues:
        print("\n🚨 Problemas encontrados:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n🎉 Entorno de pruebas validado correctamente!")
        return True


def show_test_statistics():
    """Muestra estadísticas de las pruebas disponibles."""
    print("📊 Estadísticas del entorno de pruebas:")
    
    # Contar archivos de prueba
    test_dirs = {
        'Unitarias': 'tests/unit/',
        'Integración': 'tests/integration/',
        'Funcionales': 'tests/functional/'
    }
    
    total_tests = 0
    for test_type, test_dir in test_dirs.items():
        if Path(test_dir).exists():
            test_files = list(Path(test_dir).glob('test_*.py'))
            print(f"  {test_type}: {len(test_files)} archivos")
            total_tests += len(test_files)
        else:
            print(f"  {test_type}: Directorio no encontrado")
    
    print(f"  Total: {total_tests} archivos de prueba")
    
    # Estadísticas de datos de prueba
    test_data_path = Path('tests/test_data')
    if test_data_path.exists():
        docx_files = list(test_data_path.glob('*.docx'))
        print(f"  Archivos DOCX: {len(docx_files)}")
        
        # Tipos de minerales detectados
        mineral_types = set()
        for file in docx_files:
            name_lower = file.stem.lower()
            for mineral in ['magnetita', 'calcita', 'malaquita', 'yeso', 'pirita']:
                if mineral in name_lower:
                    mineral_types.add(mineral)
        
        print(f"  Tipos de minerales: {len(mineral_types)} ({', '.join(sorted(mineral_types))})")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Ejecutor de pruebas para el sistema de identificación de minerales'
    )
    
    parser.add_argument(
        'test_type', 
        nargs='?', 
        default='all',
        choices=['unit', 'integration', 'functional', 'all'],
        help='Tipo de pruebas a ejecutar (default: all)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Salida detallada'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true', 
        help='Generar reporte de cobertura'
    )
    
    parser.add_argument(
        '-f', '--fast',
        action='store_true',
        help='Ejecutar solo pruebas rápidas (excluye marcador "slow")'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Solo validar el entorno de pruebas'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Mostrar estadísticas del entorno de pruebas'
    )
    
    args = parser.parse_args()
    
    # Mostrar estadísticas si se solicita
    if args.stats:
        show_test_statistics()
        return
    
    # Validar entorno
    if args.validate or not validate_test_environment():
        if args.validate:
            return
        print("\n❌ El entorno de pruebas tiene problemas. Usa --validate para más detalles.")
        sys.exit(1)
    
    # Ejecutar pruebas
    print(f"\n🚀 Ejecutando pruebas {args.test_type}...")
    success = run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        fast=args.fast
    )
    
    if success:
        print("\n✅ Todas las pruebas completadas exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron.")
        sys.exit(1)


if __name__ == '__main__':
    main()