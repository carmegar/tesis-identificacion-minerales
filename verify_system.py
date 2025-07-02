#!/usr/bin/env python3
"""
Script de verificación del sistema de identificación de minerales.
Verifica que todos los componentes estén funcionando correctamente.
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("🔍 Verificando dependencias...")
    
    required_modules = [
        'numpy', 'cv2', 'sqlalchemy', 'docx', 'streamlit', 'pandas'
    ]
    
    missing = []
    for module in required_modules:
        try:
            if module == 'cv2':
                import cv2
            elif module == 'docx':
                import docx
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"  ❌ {module}")
    
    if missing:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True


def check_project_structure():
    """Verifica la estructura del proyecto."""
    print("\n📁 Verificando estructura del proyecto...")
    
    required_files = [
        'app.py',
        'populate_database.py',
        'requirements.txt',
        'README.md',
        'src/main.py',
        'src/analysis/vectorize.py',
        'src/analysis/compare.py',
        'src/database/models.py',
        'src/database/connection.py',
        'src/database/queries.py',
        'src/parsers/docx_parser.py',
        'tests/test_vectorize_pipeline.py',
        'docs/architecture.md'
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            missing.append(file_path)
            print(f"  ❌ {file_path}")
    
    if missing:
        print(f"\n⚠️  Archivos faltantes: {', '.join(missing)}")
        return False
    
    print("✅ Estructura del proyecto correcta")
    return True


def check_database():
    """Verifica la base de datos."""
    print("\n🗄️ Verificando base de datos...")
    
    try:
        from src.database.connection import SessionLocal
        from src.database.queries import count_muestras
        
        session = SessionLocal()
        count = count_muestras(session)
        session.close()
        
        print(f"  ✅ Base de datos accesible")
        print(f"  📊 Muestras en la base de datos: {count}")
        
        if count == 0:
            print("  ⚠️  Base de datos vacía. Ejecuta 'python populate_database.py'")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en base de datos: {e}")
        return False


def check_sample_processing():
    """Verifica que el procesamiento de muestras funcione."""
    print("\n🔬 Verificando procesamiento de muestras...")
    
    try:
        from src.parsers.docx_parser import extract_and_vectorize_spectrum

        # Buscar archivo de prueba
        test_files = [
            "data/Eds_magnetita.docx",
            "data/Eds_magnetita-2.docx", 
            "data/Eds_magnetita-3.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            print("  ⚠️  No se encontraron archivos de prueba en data/")
            return True
        
        print(f"  🧪 Probando con: {test_file}")
        vector = extract_and_vectorize_spectrum(test_file, vector_size=200)
        
        if vector is not None and len(vector) == 200:
            print("  ✅ Procesamiento de espectros funcionando")
            return True
        else:
            print("  ❌ Error en procesamiento de espectros")
            return False
            
    except Exception as e:
        print(f"  ❌ Error en procesamiento: {e}")
        return False


def check_cleaned_files():
    """Verifica que los archivos innecesarios hayan sido eliminados."""
    print("\n🧹 Verificando limpieza de archivos...")
    
    unwanted_patterns = [
        '__pycache__',
        '.pytest_cache',
        'data/images/debug_',
        'data/images/mask_',
        'data/temp_images'
    ]
    
    found_unwanted = []
    for pattern in unwanted_patterns:
        if '*' in pattern or os.path.exists(pattern):
            found_unwanted.append(pattern)
    
    if found_unwanted:
        print(f"  ⚠️  Archivos temporales encontrados: {', '.join(found_unwanted)}")
    else:
        print("  ✅ Archivos temporales limpiados")
    
    return True


def main():
    """Función principal de verificación."""
    print("🔬 Verificación del Sistema de Identificación de Minerales EDS")
    print("=" * 60)
    
    checks = [
        check_dependencies,
        check_project_structure,
        check_database,
        check_sample_processing,
        check_cleaned_files
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Error en verificación: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("🎉 ¡Sistema verificado exitosamente!")
        print("\n🚀 Para usar el sistema:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Se encontraron algunos problemas.")
        print("Revisa los mensajes anteriores para solucionarlos.")
    
    print("\n📋 Comandos útiles:")
    print("   python populate_database.py  # Poblar base de datos")
    print("   python src/main.py          # Prueba individual")
    print("   python tests/test_vectorize_pipeline.py  # Test del sistema")


if __name__ == "__main__":
    main() 