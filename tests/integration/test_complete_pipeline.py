"""
Pruebas de integración para el pipeline completo del sistema de identificación.
"""
import pytest
import numpy as np
from pathlib import Path

from src.parsers.docx_parser import extract_and_vectorize_spectrum
from src.database.queries import insert_muestra, insert_espectro
from src.analysis.compare import compare_spectrum


@pytest.mark.integration
@pytest.mark.spectrum
@pytest.mark.slow
class TestCompletePipeline:
    """Pruebas de integración del flujo completo de identificación."""
    
    def test_complete_identification_workflow(self, test_db, test_docx_files):
        """Test del flujo completo: extracción -> vectorización -> comparación."""
        if len(test_docx_files) < 2:
            pytest.skip("Se necesitan al menos 2 archivos DOCX para esta prueba")
        
        # 1. Poblar base de datos con muestras de referencia
        muestras_referencia = []
        for i, docx_file in enumerate(test_docx_files[:3]):  # Usar 3 como referencia
            vector = extract_and_vectorize_spectrum(str(docx_file))
            if vector is not None:
                muestra = insert_muestra(
                    test_db,
                    f"Referencia_{docx_file.stem}",
                    "Test_Researcher"
                )
                insert_espectro(test_db, muestra.id, vector)
                muestras_referencia.append((muestra, vector))
        
        if len(muestras_referencia) < 2:
            pytest.skip("No se pudieron extraer suficientes vectores de referencia")
        
        # 2. Procesar nueva muestra para identificación
        if len(test_docx_files) > 3:
            nueva_muestra_file = test_docx_files[3]
        else:
            nueva_muestra_file = test_docx_files[0]  # Reusar uno existente
            
        nuevo_vector = extract_and_vectorize_spectrum(str(nueva_muestra_file))
        if nuevo_vector is None:
            pytest.skip("No se pudo extraer vector de la nueva muestra")
        
        nueva_muestra = insert_muestra(
            test_db,
            f"Nueva_Muestra_{nueva_muestra_file.stem}",
            "Test_User"
        )
        insert_espectro(test_db, nueva_muestra.id, nuevo_vector)
        
        # 3. Realizar comparación
        resultados = compare_spectrum(test_db, nueva_muestra.id, similitud_umbral=0.0)
        
        # 4. Verificar resultados
        assert len(resultados) >= 1  # Debe encontrar al menos una coincidencia
        assert len(resultados) <= len(muestras_referencia)
        
        # Verificar estructura de resultados
        for muestra_id, nombre, similitud in resultados:
            assert isinstance(muestra_id, int)
            assert nombre.startswith("Referencia_")
            assert -1.0 <= similitud <= 1.0
        
        # Verificar orden descendente
        if len(resultados) > 1:
            similitudes = [sim for _, _, sim in resultados]
            for i in range(len(similitudes) - 1):
                assert similitudes[i] >= similitudes[i + 1]
    
    def test_similar_spectra_identification(self, test_db):
        """Test de identificación con espectros artificialmente similares."""
        # Crear vector base
        base_vector = np.random.rand(200).astype(np.float32)
        base_vector = base_vector / np.linalg.norm(base_vector)
        
        # Crear variaciones del vector base
        variaciones = []
        nombres_minerales = ["Magnetita_Base", "Magnetita_Similar", "Hematita_Diferente"]
        
        for i, nombre in enumerate(nombres_minerales):
            if i == 0:  # Vector base
                vector = base_vector.copy()
            elif i == 1:  # Vector similar (90% + ruido)
                vector = base_vector * 0.9 + np.random.normal(0, 0.05, 200)
                vector = vector / np.linalg.norm(vector)
            else:  # Vector diferente
                vector = np.random.rand(200).astype(np.float32)
                vector = vector / np.linalg.norm(vector)
            
            muestra = insert_muestra(test_db, nombre, "Synthetic_Researcher")
            insert_espectro(test_db, muestra.id, vector)
            variaciones.append((muestra, vector))
        
        # Comparar vector base contra los demás
        base_muestra = variaciones[0][0]
        resultados = compare_spectrum(test_db, base_muestra.id, similitud_umbral=0.3)
        
        # Debe encontrar ambos (similar y diferente)
        assert len(resultados) == 2
        
        # El similar debe tener mayor similitud
        resultados_dict = {nombre: sim for _, nombre, sim in resultados}
        
        assert "Magnetita_Similar" in resultados_dict
        assert "Hematita_Diferente" in resultados_dict
        assert resultados_dict["Magnetita_Similar"] > resultados_dict["Hematita_Diferente"]
        assert resultados_dict["Magnetita_Similar"] > 0.7  # Alta similitud
    
    def test_edge_case_empty_database(self, test_db, test_docx_files):
        """Test con base de datos vacía."""
        if not test_docx_files:
            pytest.skip("No hay archivos DOCX disponibles")
        
        # Insertar solo una muestra (sin referencias para comparar)
        vector = extract_and_vectorize_spectrum(str(test_docx_files[0]))
        if vector is None:
            pytest.skip("No se pudo extraer vector")
        
        muestra = insert_muestra(test_db, "Unica_Muestra", "Test_User")
        insert_espectro(test_db, muestra.id, vector)
        
        # No debe haber resultados de comparación
        resultados = compare_spectrum(test_db, muestra.id, similitud_umbral=0.0)
        assert len(resultados) == 0
    
    def test_multiple_mineral_types_identification(self, test_db):
        """Test con múltiples tipos de minerales claramente diferenciados."""
        mineral_data = [
            ("Cuarzo", np.array([1.0, 0.0, 0.0, 0.5] * 50)),
            ("Feldespato", np.array([0.0, 1.0, 0.0, 0.3] * 50)),
            ("Mica", np.array([0.0, 0.0, 1.0, 0.7] * 50)),
            ("Calcita", np.array([0.5, 0.5, 0.5, 0.2] * 50))
        ]
        
        muestras = []
        for nombre, vector_base in mineral_data:
            # Normalizar vector
            vector = vector_base.astype(np.float32)
            vector = vector / np.linalg.norm(vector)
            
            muestra = insert_muestra(test_db, nombre, "Mineralogist")
            insert_espectro(test_db, muestra.id, vector)
            muestras.append(muestra)
        
        # Probar identificación de una muestra similar al Cuarzo
        cuarzo_similar = np.array([0.9, 0.1, 0.0, 0.45] * 50).astype(np.float32)
        cuarzo_similar = cuarzo_similar / np.linalg.norm(cuarzo_similar)
        
        muestra_test = insert_muestra(test_db, "Cuarzo_Test", "Test_User")
        insert_espectro(test_db, muestra_test.id, cuarzo_similar)
        
        resultados = compare_spectrum(test_db, muestra_test.id, similitud_umbral=0.5)
        
        # Debe identificar Cuarzo como el más similar
        assert len(resultados) >= 1
        mejor_match = resultados[0]
        assert mejor_match[1] == "Cuarzo"  # Nombre del mineral
        assert mejor_match[2] > 0.8  # Alta similitud
    
    def test_batch_processing(self, test_db, test_docx_files):
        """Test de procesamiento en lote de múltiples muestras."""
        if len(test_docx_files) < 3:
            pytest.skip("Se necesitan al menos 3 archivos para procesamiento en lote")
        
        muestras_procesadas = []
        vectores_extraidos = []
        
        # Procesar múltiples archivos
        for docx_file in test_docx_files[:5]:  # Máximo 5 para no ser muy lento
            vector = extract_and_vectorize_spectrum(str(docx_file))
            if vector is not None:
                muestra = insert_muestra(
                    test_db,
                    f"Batch_{docx_file.stem}",
                    "Batch_Processor"
                )
                insert_espectro(test_db, muestra.id, vector)
                muestras_procesadas.append(muestra)
                vectores_extraidos.append(vector)
        
        # Verificar que se procesaron muestras
        assert len(muestras_procesadas) >= 2
        
        # Verificar que todos los vectores están normalizados
        for vector in vectores_extraidos:
            norm = np.linalg.norm(vector)
            assert abs(norm - 1.0) < 1e-6
        
        # Comparar primera muestra contra las demás
        if len(muestras_procesadas) > 1:
            resultados = compare_spectrum(
                test_db, 
                muestras_procesadas[0].id, 
                similitud_umbral=0.0
            )
            assert len(resultados) == len(muestras_procesadas) - 1