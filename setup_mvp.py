#!/usr/bin/env python3
"""
Script de configuración automática para el MVP de Identificación de Minerales
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Ejecuta un comando y maneja errores."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Error: Se requiere Python 3.9 o superior")
        print(f"Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True


def install_dependencies():
    """Instala las dependencias del proyecto."""
    if not os.path.exists("requirements.txt"):
        print("❌ Error: No se encontró el archivo requirements.txt")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Instalando dependencias"
    )


def populate_database():
    """Ejecuta el script de población de la base de datos."""
    if not os.path.exists("populate_database.py"):
        print("❌ Error: No se encontró el script populate_database.py")
        return False
    
    return run_command(
        f"{sys.executable} populate_database.py",
        "Poblando la base de datos con las muestras"
    )


def main():
    print("🔬 Configuración del MVP - Sistema de Identificación de Minerales EDS")
    print("=" * 70)
    
    # Verificar versión de Python
    if not check_python_version():
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Error: No se pudieron instalar las dependencias")
        sys.exit(1)
    
    # Poblar base de datos
    print(f"\n📊 ¿Deseas poblar la base de datos con las muestras de la carpeta 'muestrasdatos'?")
    response = input("Esto procesará todos los archivos DOCX encontrados (s/n): ").lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        if not populate_database():
            print("\n⚠️  Advertencia: Error al poblar la base de datos")
            print("Puedes ejecutar 'python populate_database.py' manualmente más tarde")
    else:
        print("📝 Base de datos no poblada. Puedes ejecutar 'python populate_database.py' más tarde")
    
    print("\n" + "=" * 70)
    print("🎉 ¡Configuración completada!")
    print("\n🚀 Para ejecutar la aplicación, usa:")
    print("   streamlit run app.py")
    print("\n📋 Comandos útiles:")
    print("   python populate_database.py  # Poblar base de datos")
    print("   python src/main.py          # Probar procesamiento individual")
    print("   streamlit run app.py        # Ejecutar aplicación web")


if __name__ == "__main__":
    main() 