#!/usr/bin/env python3
"""
MVP - Aplicación Web para Identificación de Minerales mediante Espectros EDS
"""

import os
import tempfile
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from src.analysis.compare import compare_spectrum
from src.database.connection import SessionLocal
from src.database.queries import (count_muestras, create_tables,
                                  get_all_muestras_with_vectors,
                                  insert_espectro, insert_muestra)
from src.parsers.docx_parser import extract_and_vectorize_spectrum


def setup_database():
    """Inicializa la base de datos si es necesario."""
    create_tables()


def show_database_stats():
    """Muestra estadísticas de la base de datos."""
    session = SessionLocal()
    try:
        total_muestras = count_muestras(session)
        muestras_with_vectors = len(get_all_muestras_with_vectors(session))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Muestras", total_muestras)
        with col2:
            st.metric("Muestras con Espectros", muestras_with_vectors)
            
    finally:
        session.close()


def show_mineral_database():
    """Muestra la tabla de minerales en la base de datos."""
    session = SessionLocal()
    try:
        muestras = get_all_muestras_with_vectors(session)
        
        if not muestras:
            st.warning("No hay muestras en la base de datos. Ejecuta el script de población primero.")
            return
        
        # Crear DataFrame para mostrar
        data = []
        for muestra in muestras:
            data.append({
                "ID": muestra.id,
                "Mineral": muestra.nombre_muestra,
                "Investigador": muestra.investigador or "N/A",
                "Fecha": muestra.fecha.strftime("%Y-%m-%d") if muestra.fecha else "N/A"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
    finally:
        session.close()


def identify_mineral():
    """Interfaz para identificar un mineral subiendo un archivo DOCX."""
    st.subheader("📤 Subir Espectro EDS para Identificación")
    
    uploaded_file = st.file_uploader(
        "Selecciona un archivo DOCX con espectro EDS",
        type=['docx'],
        help="El archivo debe contener una imagen de espectro EDS de 400x512 píxeles"
    )
    
    if uploaded_file is not None:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            with st.spinner("Procesando espectro..."):
                # Extraer y vectorizar
                vector = extract_and_vectorize_spectrum(tmp_path, vector_size=200)
                
                if vector is None:
                    st.error("❌ No se encontró un espectro válido en el archivo. Verifica que contenga una imagen de espectro EDS de 400x512 píxeles.")
                    return
                
                st.success("✅ Espectro extraído exitosamente!")
                
                # Mostrar información del vector
                st.info(f"Vector generado: {len(vector)} dimensiones")
                
                # Guardar en base de datos
                session = SessionLocal()
                try:
                    nueva_muestra = insert_muestra(
                        session=session,
                        nombre_muestra=f"Muestra desconocida - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        investigador="Usuario Web",
                        ruta_imagen=uploaded_file.name
                    )
                    
                    insert_espectro(session, muestra_id=nueva_muestra.id, vector=vector)
                    
                    # Comparar contra la base de datos
                    st.subheader("🔍 Resultados de Identificación")
                    
                    resultados = compare_spectrum(session, nueva_muestra.id, similitud_umbral=0.0)
                    
                    if not resultados:
                        st.warning("No se encontraron minerales similares en la base de datos.")
                    else:
                        st.write("Minerales más similares (ordenados por similitud):")
                        
                        # Crear DataFrame con resultados
                        df_resultados = pd.DataFrame([
                            {
                                "Mineral": nombre,
                                "Similitud": f"{sim:.2%}",
                                "Confianza": "Alta" if sim > 0.8 else "Media" if sim > 0.6 else "Baja"
                            }
                            for mid, nombre, sim in resultados[:10]  # Top 10
                        ])
                        
                        st.dataframe(df_resultados, use_container_width=True)
                        
                        # Mostrar el mejor match
                        if resultados:
                            mejor_match = resultados[0]
                            similitud = mejor_match[2]
                            mineral = mejor_match[1]
                            
                            if similitud > 0.8:
                                st.success(f"🎯 **Identificación muy probable:** {mineral} (similitud: {similitud:.2%})")
                            elif similitud > 0.6:
                                st.warning(f"🤔 **Posible identificación:** {mineral} (similitud: {similitud:.2%})")
                            else:
                                st.info(f"💡 **Sugerencia:** {mineral} (similitud: {similitud:.2%}) - Se recomienda análisis adicional")
                
                finally:
                    session.close()
                    
        finally:
            # Limpiar archivo temporal
            os.unlink(tmp_path)


def main():
    st.set_page_config(
        page_title="Identificación de Minerales EDS",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔬 Sistema de Identificación de Minerales mediante Espectros EDS")
    st.markdown("---")
    
    # Inicializar base de datos
    setup_database()
    
    # Sidebar con navegación
    st.sidebar.title("📋 Navegación")
    page = st.sidebar.selectbox(
        "Selecciona una opción:",
        ["🏠 Inicio", "🔍 Identificar Mineral", "📊 Base de Datos", "ℹ️ Información"]
    )
    
    if page == "🏠 Inicio":
        st.header("Bienvenido al Sistema de Identificación de Minerales")
        
        st.markdown("""
        Este sistema utiliza **espectros EDS** (Energy Dispersive Spectroscopy) para identificar minerales 
        mediante comparación con una base de datos de muestras conocidas.
        
        ### 🚀 Características:
        - **Procesamiento automático** de archivos DOCX con espectros EDS
        - **Vectorización** de espectros para comparación matemática
        - **Identificación** mediante similitud de coseno
        - **Base de datos** de minerales de referencia
        
        ### 📈 Estadísticas de la Base de Datos:
        """)
        
        show_database_stats()
        
        st.markdown("""
        ### 🔧 Cómo usar:
        1. Ve a "🔍 Identificar Mineral"
        2. Sube un archivo DOCX con tu espectro EDS
        3. El sistema procesará automáticamente el espectro
        4. Obtendrás una lista de minerales similares ordenados por probabilidad
        """)
    
    elif page == "🔍 Identificar Mineral":
        identify_mineral()
    
    elif page == "📊 Base de Datos":
        st.header("📊 Base de Datos de Minerales")
        
        show_database_stats()
        st.markdown("---")
        
        st.subheader("🗂️ Minerales en la Base de Datos")
        show_mineral_database()
    
    elif page == "ℹ️ Información":
        st.header("ℹ️ Información Técnica")
        
        st.markdown("""
        ### 🔬 Tecnología
        - **Python**: Lenguaje de programación principal
        - **OpenCV**: Procesamiento de imágenes de espectros
        - **SQLite**: Base de datos para almacenar vectores
        - **Streamlit**: Interfaz web interactiva
        - **NumPy**: Cálculos matemáticos y vectorización
        
        ### 📋 Algoritmo de Identificación
        1. **Extracción**: Se extrae la imagen del espectro EDS del archivo DOCX
        2. **Preprocesamiento**: Se convierte a escala de grises y se aplica filtro Gaussiano
        3. **Segmentación**: Se crea una máscara binaria para separar el espectro del fondo
        4. **Vectorización**: Se calcula el perfil del espectro y se redimensiona a 200 dimensiones
        5. **Normalización**: Se normaliza el vector para comparación
        6. **Comparación**: Se calcula la similitud de coseno contra todas las muestras
        
        ### 📊 Métricas de Similitud
        - **> 80%**: Identificación muy probable
        - **60-80%**: Posible identificación
        - **< 60%**: Requiere análisis adicional
        
        ### 👨‍💻 Desarrollado para Tesis de Identificación de Minerales
        """)


if __name__ == "__main__":
    main() 