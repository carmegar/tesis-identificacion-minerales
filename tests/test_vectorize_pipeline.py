# tests/test_vectorize_pipeline.py

"""
Test completo del pipeline de vectorización de espectros EDS.
"""
import numpy as np
import pytest

from src.analysis.vectorize import vectorize_spectrum


def test_vectorize_spectrum_with_magnetita():
    """Test de vectorización usando muestra de magnetita."""
    # Archivo de prueba
    test_file = "data/Eds_magnetita.docx"
    
    # Extraer vector usando archivo directo
    try:
        from src.parsers.docx_parser import extract_and_vectorize_spectrum
        vector = extract_and_vectorize_spectrum(test_file, vector_size=200)
        
        # Verificaciones básicas
        assert vector is not None, "El vector no debe ser None"
        assert isinstance(vector, np.ndarray), "Debe retornar un numpy array"
        assert len(vector) == 200, "El vector debe tener 200 dimensiones"
        assert np.isclose(np.linalg.norm(vector), 1.0, atol=1e-6), "El vector debe estar normalizado"
        assert not np.any(np.isnan(vector)), "No debe contener valores NaN"
        
        print(f"✅ Test exitoso: Vector de {len(vector)} dimensiones generado correctamente")
        print(f"📊 Norma del vector: {np.linalg.norm(vector):.6f}")
        print(f"📈 Rango de valores: [{vector.min():.4f}, {vector.max():.4f}]")
        
    except Exception as e:
        pytest.fail(f"Error en el pipeline de vectorización: {e}")


if __name__ == "__main__":
    test_vectorize_spectrum_with_magnetita()
