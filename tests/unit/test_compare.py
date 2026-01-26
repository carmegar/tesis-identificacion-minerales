"""
Pruebas unitarias para el módulo de comparación de espectros.
"""
import pytest
import numpy as np

from src.analysis.compare import calcular_similitud, compare_spectrum


@pytest.mark.unit
class TestCalcularSimilitud:
    """Pruebas para el cálculo de similitud de coseno."""
    
    def test_vectores_identicos(self):
        """Test con vectores idénticos (similitud = 1.0)."""
        vector1 = np.array([1, 2, 3, 4])
        vector2 = np.array([1, 2, 3, 4])
        
        similitud = calcular_similitud(vector1, vector2)
        assert abs(similitud - 1.0) < 1e-6
    
    def test_vectores_ortogonales(self):
        """Test con vectores ortogonales (similitud = 0.0)."""
        vector1 = np.array([1, 0, 0])
        vector2 = np.array([0, 1, 0])
        
        similitud = calcular_similitud(vector1, vector2)
        assert abs(similitud - 0.0) < 1e-6
    
    def test_vectores_opuestos(self):
        """Test con vectores opuestos (similitud = -1.0)."""
        vector1 = np.array([1, 2, 3])
        vector2 = np.array([-1, -2, -3])
        
        similitud = calcular_similitud(vector1, vector2)
        assert abs(similitud - (-1.0)) < 1e-6
    
    def test_vectores_normalizados(self, normalized_test_vectors):
        """Test con vectores normalizados pre-definidos."""
        base = normalized_test_vectors['base']
        similar = normalized_test_vectors['similar']
        different = normalized_test_vectors['different']
        
        # Similitud entre base y similar debe ser alta
        sim_high = calcular_similitud(base, similar)
        assert sim_high > 0.8
        
        # Similitud entre base y different debe ser menor
        sim_low = calcular_similitud(base, different)
        assert sim_low < sim_high
    
    def test_vector_norma_cero(self):
        """Test con vector de norma cero."""
        vector1 = np.array([1, 2, 3])
        vector_zero = np.array([0, 0, 0])
        
        similitud = calcular_similitud(vector1, vector_zero)
        assert similitud == 0.0
        
        similitud2 = calcular_similitud(vector_zero, vector1)  
        assert similitud2 == 0.0
    
    def test_precision_numerica(self):
        """Test de precisión numérica con vectores muy pequeños."""
        vector1 = np.array([1e-10, 2e-10, 3e-10])
        vector2 = np.array([2e-10, 4e-10, 6e-10])  # Múltiplo de vector1
        
        similitud = calcular_similitud(vector1, vector2)
        assert abs(similitud - 1.0) < 1e-6


@pytest.mark.unit
@pytest.mark.database
class TestCompareSpectrum:
    """Pruebas para la comparación de espectros en base de datos."""
    
    def test_compare_spectrum_basic(self, populated_test_db):
        """Test básico de comparación de espectros."""
        test_db, muestras = populated_test_db
        
        # Comparar la primera muestra contra las demás
        muestra_base = muestras[0]
        resultados = compare_spectrum(test_db, muestra_base.id, similitud_umbral=0.0)
        
        # Should find other 2 samples
        assert len(resultados) == 2
        
        # Verificar estructura de resultados
        for muestra_id, nombre, similitud in resultados:
            assert isinstance(muestra_id, int)
            assert isinstance(nombre, str)
            assert isinstance(similitud, (float, np.floating))
            assert -1.0 <= similitud <= 1.0
    
    def test_compare_spectrum_with_threshold(self, populated_test_db):
        """Test de comparación con umbral de similitud."""
        test_db, muestras = populated_test_db
        
        muestra_base = muestras[0]
        
        # Umbral alto - debe filtrar resultados
        resultados_altos = compare_spectrum(
            test_db, muestra_base.id, similitud_umbral=0.8
        )
        
        # Umbral bajo - debe incluir más resultados  
        resultados_bajos = compare_spectrum(
            test_db, muestra_base.id, similitud_umbral=0.1
        )
        
        # Con umbral más bajo debe haber más o igual cantidad de resultados
        assert len(resultados_bajos) >= len(resultados_altos)
        
        # Todos los resultados deben superar el umbral correspondiente
        for _, _, sim in resultados_altos:
            assert sim >= 0.8
        
        for _, _, sim in resultados_bajos:
            assert sim >= 0.1
    
    def test_compare_spectrum_ordering(self, populated_test_db):
        """Test que los resultados estén ordenados por similitud descendente."""
        test_db, muestras = populated_test_db
        
        muestra_base = muestras[0]
        resultados = compare_spectrum(test_db, muestra_base.id, similitud_umbral=0.0)
        
        if len(resultados) > 1:
            similitudes = [sim for _, _, sim in resultados]
            
            # Verificar orden descendente
            for i in range(len(similitudes) - 1):
                assert similitudes[i] >= similitudes[i + 1]
    
    def test_compare_spectrum_nonexistent_id(self, test_db):
        """Test con ID de muestra inexistente."""
        with pytest.raises(ValueError, match="no tiene espectro almacenado"):
            compare_spectrum(test_db, 99999, similitud_umbral=0.5)
    
    def test_compare_spectrum_single_sample(self, test_db, sample_mineral_data):
        """Test con solo una muestra en la base de datos."""
        from src.database.queries import insert_muestra, insert_espectro
        
        # Insertar una sola muestra
        muestra = insert_muestra(
            test_db, 
            sample_mineral_data['nombre'],
            sample_mineral_data['investigador']
        )
        insert_espectro(test_db, muestra.id, sample_mineral_data['vector'])
        
        # No debe haber resultados (no hay otras muestras para comparar)
        resultados = compare_spectrum(test_db, muestra.id, similitud_umbral=0.0)
        assert len(resultados) == 0
    
    def test_compare_identical_vectors(self, test_db):
        """Test con vectores idénticos."""
        from src.database.queries import insert_muestra, insert_espectro
        
        vector_identico = np.array([0.1, 0.2, 0.3] * 67, dtype=np.float32)
        
        # Insertar dos muestras con el mismo vector
        muestra1 = insert_muestra(test_db, "Mineral_A", "Researcher")
        insert_espectro(test_db, muestra1.id, vector_identico)
        
        muestra2 = insert_muestra(test_db, "Mineral_B", "Researcher")
        insert_espectro(test_db, muestra2.id, vector_identico.copy())
        
        resultados = compare_spectrum(test_db, muestra1.id, similitud_umbral=0.0)
        
        assert len(resultados) == 1
        _, nombre, similitud = resultados[0]
        assert nombre == "Mineral_B"
        assert abs(similitud - 1.0) < 1e-6  # Similitud perfecta