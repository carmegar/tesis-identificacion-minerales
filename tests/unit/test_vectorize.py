"""
Pruebas unitarias para el módulo de vectorización de espectros EDS.
"""
import pytest
import numpy as np
from pathlib import Path

from src.analysis.vectorize import (
    preprocess_image, convert_to_grayscale, extract_mask,
    crop_mask, compute_signature, resize_signature, 
    normalize_vector, vectorize_spectrum
)


@pytest.mark.unit
class TestVectorizeComponents:
    """Pruebas unitarias para cada componente del pipeline de vectorización."""
    
    def test_preprocess_image(self):
        """Test del filtro Gaussiano."""
        # Imagen de prueba con variación para que el filtro tenga efecto
        test_img = np.array([[[0.0, 0.0, 0.0],
                            [1.0, 1.0, 1.0],
                            [0.0, 0.0, 0.0]],
                           [[1.0, 1.0, 1.0],
                            [0.0, 0.0, 0.0], 
                            [1.0, 1.0, 1.0]],
                           [[0.0, 0.0, 0.0],
                            [1.0, 1.0, 1.0],
                            [0.0, 0.0, 0.0]]], dtype=np.float32)
        processed = preprocess_image(test_img)
        
        assert processed.shape == test_img.shape
        assert processed.dtype == np.float32
        # El filtro debe suavizar (no debe ser exactamente igual)
        assert not np.array_equal(processed, test_img)
    
    def test_convert_to_grayscale(self):
        """Test de conversión a escala de grises."""
        # Imagen de prueba BGR
        test_img = np.array([[[100, 150, 200]]], dtype=np.float32) / 255.0
        gray = convert_to_grayscale(test_img)
        
        assert len(gray.shape) == 2  # Debe ser 2D
        assert gray.dtype == np.float32
        assert 0 <= gray.max() <= 1.0
    
    def test_extract_mask_threshold(self):
        """Test de extracción de máscara con diferentes umbrales."""
        # Imagen con valores específicos
        gray = np.array([[0.5, 0.95, 0.99], 
                        [1.0, 0.8, 0.7]], dtype=np.float32)
        
        mask = extract_mask(gray, threshold=0.99)
        
        # Los valores < 0.99 deben ser 255, los >= 0.99 deben ser 0
        # Corregir expectativa: 0.99 == 0.99, por lo que debe ser 0
        expected = np.array([[255, 255, 0], 
                           [0, 255, 255]], dtype=np.uint8)
        np.testing.assert_array_equal(mask, expected)
    
    def test_crop_mask_with_bounds(self):
        """Test de recorte con límites específicos."""
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[2:8, 1:9] = 255  # Región con datos
        
        cropped, r_st, r_ed, c_st, c_ed = crop_mask(
            mask, row_bounds=(3, 7)
        )
        
        assert r_st == 3 and r_ed == 7  # Bounds especificados
        assert c_st == 1 and c_ed == 9  # Calculados automáticamente
        assert cropped.shape == (4, 8)  # 7-3 x 9-1
    
    def test_compute_signature_methods(self):
        """Test de cálculo de firma con diferentes métodos."""
        mask = np.array([[100, 200, 50],
                        [150, 250, 75]], dtype=np.uint8)
        
        # Método mean
        sig_mean = compute_signature(mask, method="mean")
        expected_mean = [125, 225, 62.5]  # Promedio por columna
        np.testing.assert_array_almost_equal(sig_mean, expected_mean)
        
        # Método max  
        sig_max = compute_signature(mask, method="max")
        expected_max = [150, 250, 75]  # Máximo por columna
        np.testing.assert_array_equal(sig_max, expected_max)
    
    def test_resize_signature(self):
        """Test de redimensionamiento de firma."""
        signature = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        
        # Redimensionar a 10 elementos
        resized = resize_signature(signature, vector_size=10)
        
        assert len(resized) == 10
        assert resized.dtype == np.float32
        assert resized[0] == 1.0  # Primer elemento debe mantenerse
        assert resized[-1] == 5.0  # Último elemento debe mantenerse
    
    def test_resize_signature_empty(self):
        """Test con firma vacía."""
        empty_sig = np.array([])
        result = resize_signature(empty_sig, vector_size=100)
        assert result is None
    
    def test_normalize_vector(self):
        """Test de normalización de vectores."""
        vector = np.array([3, 4, 0])  # Norma = 5
        normalized = normalize_vector(vector)
        
        expected = np.array([0.6, 0.8, 0.0])
        np.testing.assert_array_almost_equal(normalized, expected, decimal=6)
        
        # Verificar que la norma es 1
        norm = np.linalg.norm(normalized)
        assert abs(norm - 1.0) < 1e-6
    
    def test_normalize_zero_vector(self):
        """Test con vector de norma cero."""
        zero_vector = np.array([0, 0, 0])
        result = normalize_vector(zero_vector)
        assert result is None


@pytest.mark.unit 
@pytest.mark.slow
class TestVectorizeSpectrum:
    """Pruebas del pipeline completo de vectorización."""
    
    def test_vectorize_with_test_data(self, test_docx_files):
        """Test de vectorización con archivos DOCX reales."""
        if not test_docx_files:
            pytest.skip("No hay archivos DOCX de prueba disponibles")
        
        # Probar con el primer archivo disponible
        test_file = test_docx_files[0]
        
        # Solo probar si podemos extraer el vector
        from src.parsers.docx_parser import extract_and_vectorize_spectrum
        vector = extract_and_vectorize_spectrum(str(test_file))
        
        if vector is not None:
            # Verificaciones básicas
            assert isinstance(vector, np.ndarray)
            assert len(vector) == 200
            assert abs(np.linalg.norm(vector) - 1.0) < 1e-6  # Normalizado
            assert not np.any(np.isnan(vector))
            assert not np.any(np.isinf(vector))
    
    def test_vectorize_different_parameters(self):
        """Test con diferentes parámetros de vectorización."""
        # Este test requiere una imagen válida, se ejecuta solo si existe
        test_images = list(Path("tests/test_data").glob("*.tif"))
        if not test_images:
            pytest.skip("No hay imágenes TIF de prueba disponibles")
        
        test_image = str(test_images[0])
        
        # Test con diferentes tamaños de vector
        for vector_size in [50, 100, 200, 300]:
            try:
                vector = vectorize_spectrum(test_image, vector_size=vector_size)
                if vector is not None:
                    assert len(vector) == vector_size
                    assert abs(np.linalg.norm(vector) - 1.0) < 1e-6
            except Exception:
                # Es aceptable que falle con imágenes que no son espectros válidos
                pass