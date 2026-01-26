"""
Configuración global de pytest y fixtures para el entorno de pruebas.
"""
import os
import pytest
import tempfile
import numpy as np
from pathlib import Path

# Configurar entorno de testing antes de importar módulos del proyecto
os.environ['TESTING'] = '1'

from src.database.connection import engine, SessionLocal
from src.database.models import Base, Muestra, EspectroVectorizado
from src.database.queries import insert_muestra, insert_espectro


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configura el entorno de testing al inicio de la sesión."""
    os.environ['TESTING'] = '1'
    yield
    # Cleanup después de todos los tests


@pytest.fixture(scope="function")
def test_db():
    """
    Crea una base de datos temporal en memoria para cada test.
    Garantiza aislamiento completo entre tests.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Limpiar todas las tablas después del test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_mineral_data():
    """Datos de prueba básicos para un mineral."""
    return {
        'nombre': 'Magnetita_Test',
        'investigador': 'Test_User',
        'vector': np.random.rand(200).astype(np.float32)
    }


@pytest.fixture
def multiple_mineral_data():
    """Datos de prueba para múltiples minerales."""
    return [
        {
            'nombre': 'Magnetita_Test_1',
            'investigador': 'Researcher_A',
            'vector': np.random.rand(200).astype(np.float32)
        },
        {
            'nombre': 'Malaquita_Test_1', 
            'investigador': 'Researcher_B',
            'vector': np.random.rand(200).astype(np.float32)
        },
        {
            'nombre': 'Calcita_Test_1',
            'investigador': 'Researcher_C', 
            'vector': np.random.rand(200).astype(np.float32)
        }
    ]


@pytest.fixture
def test_docx_files():
    """Rutas a archivos DOCX de prueba disponibles."""
    test_data_path = Path(__file__).parent / "test_data"
    docx_files = list(test_data_path.glob("*.docx"))
    return docx_files[:5]  # Limitar a 5 archivos para tests rápidos


@pytest.fixture 
def populated_test_db(test_db, multiple_mineral_data):
    """
    Base de datos de prueba pre-poblada con muestras de minerales.
    """
    muestras = []
    for data in multiple_mineral_data:
        muestra = insert_muestra(
            test_db,
            data['nombre'], 
            data['investigador'],
            f"test_path_{data['nombre']}.tif"
        )
        insert_espectro(test_db, muestra.id, data['vector'])
        muestras.append(muestra)
    
    test_db.commit()
    return test_db, muestras


@pytest.fixture
def temp_image_dir():
    """Directorio temporal para imágenes de prueba."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def normalized_test_vectors():
    """Vectores de prueba normalizados para tests de similitud."""
    # Vector base
    base_vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0] * 40)  # 200 elementos
    base_vector = base_vector / np.linalg.norm(base_vector)
    
    # Vector muy similar (95% similitud esperada)
    similar_vector = base_vector * 0.95 + np.random.normal(0, 0.01, 200)
    similar_vector = similar_vector / np.linalg.norm(similar_vector)
    
    # Vector diferente
    different_vector = np.array([5.0, 4.0, 3.0, 2.0, 1.0] * 40)
    different_vector = different_vector / np.linalg.norm(different_vector)
    
    return {
        'base': base_vector.astype(np.float32),
        'similar': similar_vector.astype(np.float32), 
        'different': different_vector.astype(np.float32)
    }


# Marcadores personalizados para diferentes tipos de pruebas
def pytest_configure(config):
    """Configuración adicional de pytest."""
    config.addinivalue_line("markers", "unit: marca pruebas unitarias")
    config.addinivalue_line("markers", "integration: marca pruebas de integración")
    config.addinivalue_line("markers", "functional: marca pruebas funcionales")
    config.addinivalue_line("markers", "slow: marca pruebas lentas")
    config.addinivalue_line("markers", "database: marca pruebas que usan base de datos")
    config.addinivalue_line("markers", "spectrum: marca pruebas de procesamiento de espectros")