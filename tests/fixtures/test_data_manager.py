"""
Administrador de datos de prueba para el sistema de identificación de minerales.
"""
import pytest
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from src.database.queries import insert_muestra, insert_espectro
from src.parsers.docx_parser import extract_and_vectorize_spectrum


class TestDataManager:
    """Administrador centralizado de datos de prueba."""
    
    def __init__(self, test_data_path: Path):
        self.test_data_path = Path(test_data_path)
        self.available_files = list(self.test_data_path.glob("*.docx"))
        self._cached_vectors = {}
    
    def get_available_docx_files(self, limit: Optional[int] = None) -> List[Path]:
        """Retorna lista de archivos DOCX disponibles."""
        files = self.available_files
        return files[:limit] if limit else files
    
    def extract_vector_cached(self, docx_path: Path) -> Optional[np.ndarray]:
        """Extrae vector con caché para evitar reprocesamiento."""
        if str(docx_path) not in self._cached_vectors:
            vector = extract_and_vectorize_spectrum(str(docx_path))
            self._cached_vectors[str(docx_path)] = vector
        
        return self._cached_vectors[str(docx_path)]
    
    def create_synthetic_mineral_data(self, count: int = 5) -> List[Dict]:
        """Genera datos sintéticos de minerales para pruebas."""
        mineral_types = [
            "Cuarzo", "Feldespato", "Mica", "Calcita", "Magnetita",
            "Hematita", "Pirita", "Galena", "Malaquita", "Azurita"
        ]
        
        synthetic_data = []
        for i in range(count):
            mineral_name = mineral_types[i % len(mineral_types)]
            
            # Generar vector base característico para cada tipo
            base_pattern = np.sin(np.linspace(0, 2*np.pi*i, 200))
            noise = np.random.normal(0, 0.1, 200)
            vector = base_pattern + noise
            vector = vector.astype(np.float32)
            vector = vector / np.linalg.norm(vector)  # Normalizar
            
            synthetic_data.append({
                'nombre': f"{mineral_name}_Synthetic_{i+1}",
                'investigador': f"Researcher_{chr(65+i)}",  # A, B, C, etc.
                'vector': vector,
                'tipo_mineral': mineral_name
            })
        
        return synthetic_data
    
    def populate_test_database(self, session, use_real_files: bool = True, 
                             use_synthetic: bool = True, max_real: int = 10) -> List:
        """
        Puebla base de datos de prueba con datos reales y sintéticos.
        
        Args:
            session: Sesión de base de datos
            use_real_files: Si usar archivos DOCX reales
            use_synthetic: Si incluir datos sintéticos  
            max_real: Máximo número de archivos reales a procesar
            
        Returns:
            Lista de muestras insertadas
        """
        muestras_insertadas = []
        
        # Procesar archivos reales
        if use_real_files and self.available_files:
            files_to_process = self.available_files[:max_real]
            
            for docx_file in files_to_process:
                vector = self.extract_vector_cached(docx_file)
                if vector is not None:
                    try:
                        muestra = insert_muestra(
                            session,
                            f"Real_{docx_file.stem}",
                            "Test_Extractor",
                            str(docx_file)
                        )
                        insert_espectro(session, muestra.id, vector)
                        muestras_insertadas.append(muestra)
                    except Exception as e:
                        print(f"Error procesando {docx_file}: {e}")
        
        # Agregar datos sintéticos
        if use_synthetic:
            synthetic_data = self.create_synthetic_mineral_data(5)
            for data in synthetic_data:
                try:
                    muestra = insert_muestra(
                        session,
                        data['nombre'],
                        data['investigador'],
                        f"synthetic_{data['tipo_mineral'].lower()}.tif"
                    )
                    insert_espectro(session, muestra.id, data['vector'])
                    muestras_insertadas.append(muestra)
                except Exception as e:
                    print(f"Error insertando datos sintéticos: {e}")
        
        session.commit()
        return muestras_insertadas
    
    def create_similarity_test_vectors(self) -> Dict[str, np.ndarray]:
        """Crea vectores con similitudes conocidas para pruebas."""
        # Vector base
        base = np.random.rand(200)
        base = base / np.linalg.norm(base)
        
        # Vector muy similar (95% + ruido pequeño)
        high_sim = base * 0.95 + np.random.normal(0, 0.02, 200)
        high_sim = high_sim / np.linalg.norm(high_sim)
        
        # Vector moderadamente similar (70% + ruido)
        med_sim = base * 0.7 + np.random.normal(0, 0.3, 200)
        med_sim = med_sim / np.linalg.norm(med_sim)
        
        # Vector ortogonal (similitud ~0)
        orthogonal = np.random.rand(200)
        orthogonal = orthogonal - np.dot(orthogonal, base) * base
        orthogonal = orthogonal / np.linalg.norm(orthogonal)
        
        return {
            'base': base.astype(np.float32),
            'high_similarity': high_sim.astype(np.float32),
            'medium_similarity': med_sim.astype(np.float32),
            'orthogonal': orthogonal.astype(np.float32)
        }
    
    def validate_test_environment(self) -> Dict[str, bool]:
        """Valida que el entorno de pruebas esté correctamente configurado."""
        validation_results = {
            'test_data_directory_exists': self.test_data_path.exists(),
            'has_docx_files': len(self.available_files) > 0,
            'can_extract_vectors': False,
            'database_connection': False
        }
        
        # Probar extracción de vectores
        if self.available_files:
            try:
                test_vector = self.extract_vector_cached(self.available_files[0])
                validation_results['can_extract_vectors'] = test_vector is not None
            except Exception:
                validation_results['can_extract_vectors'] = False
        
        # Probar conexión de base de datos
        try:
            from src.database.connection import SessionLocal
            session = SessionLocal()
            session.close()
            validation_results['database_connection'] = True
        except Exception:
            validation_results['database_connection'] = False
        
        return validation_results
    
    def get_test_statistics(self) -> Dict:
        """Obtiene estadísticas del entorno de pruebas."""
        stats = {
            'total_docx_files': len(self.available_files),
            'extractable_vectors': 0,
            'file_sizes': [],
            'mineral_types_detected': set()
        }
        
        # Analizar archivos disponibles
        for docx_file in self.available_files[:5]:  # Muestra limitada para estadísticas
            stats['file_sizes'].append(docx_file.stat().st_size)
            
            # Detectar tipo de mineral del nombre del archivo
            filename_lower = docx_file.stem.lower()
            for mineral in ['magnetita', 'calcita', 'malaquita', 'yeso', 'pirita', 
                          'galena', 'fluorita', 'barita', 'siderita', 'talco']:
                if mineral in filename_lower:
                    stats['mineral_types_detected'].add(mineral)
            
            # Probar extracción
            try:
                vector = self.extract_vector_cached(docx_file)
                if vector is not None:
                    stats['extractable_vectors'] += 1
            except Exception:
                pass
        
        stats['mineral_types_detected'] = list(stats['mineral_types_detected'])
        stats['average_file_size'] = np.mean(stats['file_sizes']) if stats['file_sizes'] else 0
        
        return stats


# Fixture para el administrador de datos de prueba
@pytest.fixture(scope="session")
def test_data_manager():
    """Fixture para el administrador de datos de prueba."""
    test_data_path = Path(__file__).parent.parent / "test_data"
    return TestDataManager(test_data_path)


@pytest.fixture
def rich_test_database(test_db, test_data_manager):
    """Fixture para base de datos rica en datos de prueba."""
    muestras = test_data_manager.populate_test_database(
        test_db, 
        use_real_files=True, 
        use_synthetic=True, 
        max_real=5
    )
    return test_db, muestras


@pytest.fixture
def similarity_test_vectors(test_data_manager):
    """Fixture para vectores con similitudes conocidas."""
    return test_data_manager.create_similarity_test_vectors()