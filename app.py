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
                                  get_all_muestras_with_vectors, get_muestra_by_id,
                                  insert_espectro, insert_muestra, update_muestra, delete_muestra)
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
                
                # Almacenar el vector en session_state para uso posterior
                st.session_state['current_vector'] = vector
                st.session_state['uploaded_filename'] = uploaded_file.name
                
                # Comparar contra la base de datos usando una muestra temporal
                st.subheader("🔍 Resultados de Identificación")
                
                session = SessionLocal()
                try:
                    # Crear una muestra temporal solo para comparación (no persistir)
                    temp_muestra = insert_muestra(
                        session=session,
                        nombre_muestra=f"TEMP_COMPARISON_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        investigador="TEMP",
                        ruta_imagen=uploaded_file.name
                    )
                    
                    insert_espectro(session, muestra_id=temp_muestra.id, vector=vector)
                    
                    resultados = compare_spectrum(session, temp_muestra.id, similitud_umbral=0.0)
                    
                    # Eliminar la muestra temporal después de obtener resultados
                    delete_muestra(session, temp_muestra.id)
                    
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
                        
                        # Almacenar resultados en session_state para mostrar después
                        st.session_state['comparison_results'] = resultados
                
                finally:
                    session.close()
                
                # Botón para guardar la muestra en la base de datos
                st.markdown("---")
                st.subheader("💾 Guardar Muestra en Base de Datos")
                
                if st.button("📁 Guardar esta muestra", type="primary", help="Guarda la muestra analizada en la base de datos"):
                    st.session_state['show_save_form'] = True
                
                # Mostrar formulario de guardado si se activó
                if st.session_state.get('show_save_form', False):
                    show_save_sample_form()
                    
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
        ["🏠 Inicio", "🔍 Identificar Mineral", "📊 Base de Datos", "⚙️ Gestión de Muestras", "ℹ️ Información"]
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
    
    elif page == "⚙️ Gestión de Muestras":
        manage_samples()
    
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


def show_save_sample_form():
    """Muestra el formulario para guardar la muestra analizada."""
    if 'current_vector' not in st.session_state:
        st.error("❌ No hay datos de muestra para guardar. Por favor, analiza una muestra primero.")
        return
    
    st.subheader("📝 Información de la Muestra")
    st.info("Completa la información para guardar la muestra en la base de datos:")
    
    with st.form(key="save_sample_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_muestra = st.text_input(
                "Nombre de la muestra *",
                placeholder="Ej: Cuarzo-001",
                help="Nombre identificativo de la muestra"
            )
        
        with col2:
            investigador = st.text_input(
                "Investigador",
                placeholder="Nombre del investigador",
                value="Usuario Web",
                help="Nombre del investigador responsable"
            )
        
        col1_btn, col2_btn = st.columns([1, 4])
        with col1_btn:
            submit_save = st.form_submit_button("💾 Guardar Muestra", type="primary")
        
        if submit_save:
            if not nombre_muestra.strip():
                st.error("❌ El nombre de la muestra es obligatorio.")
                return
            
            # Guardar la muestra en la base de datos
            session = SessionLocal()
            try:
                nueva_muestra = insert_muestra(
                    session=session,
                    nombre_muestra=nombre_muestra.strip(),
                    investigador=investigador.strip() if investigador.strip() else "Usuario Web",
                    ruta_imagen=st.session_state.get('uploaded_filename', 'archivo_subido.docx')
                )
                
                insert_espectro(session, muestra_id=nueva_muestra.id, vector=st.session_state['current_vector'])
                
                st.success(f"✅ Muestra '{nombre_muestra}' guardada exitosamente con ID: {nueva_muestra.id}")
                
                # Mostrar resumen de los resultados de comparación si están disponibles
                if 'comparison_results' in st.session_state and st.session_state['comparison_results']:
                    st.write("**Recordatorio de resultados de identificación:**")
                    mejor_match = st.session_state['comparison_results'][0]
                    st.write(f"• Mejor coincidencia: {mejor_match[1]} ({mejor_match[2]:.2%} similitud)")
                
                # Limpiar session_state
                if 'current_vector' in st.session_state:
                    del st.session_state['current_vector']
                if 'uploaded_filename' in st.session_state:
                    del st.session_state['uploaded_filename']
                if 'comparison_results' in st.session_state:
                    del st.session_state['comparison_results']
                if 'show_save_form' in st.session_state:
                    del st.session_state['show_save_form']
                    
                st.info("💡 Puedes ver todas las muestras guardadas en la pestaña '📊 Base de Datos'")
                
            except Exception as e:
                st.error(f"❌ Error al guardar la muestra: {str(e)}")
            finally:
                session.close()


def manage_samples():
    """Interfaz para gestionar muestras: editar y eliminar."""
    st.header("⚙️ Gestión de Muestras")
    
    session = SessionLocal()
    try:
        muestras = get_all_muestras_with_vectors(session)
        
        if not muestras:
            st.warning("No hay muestras en la base de datos.")
            return
        
        # Selector de acción
        action = st.radio(
            "¿Qué deseas hacer?",
            ["✏️ Editar Muestra", "🗑️ Eliminar Muestra"],
            horizontal=True
        )
        
        st.markdown("---")
        
        if action == "✏️ Editar Muestra":
            st.subheader("✏️ Editar Información de Muestra")
            
            # Selector de muestra
            muestra_options = {f"{m.id} - {m.nombre_muestra}": m.id for m in muestras}
            selected_muestra = st.selectbox(
                "Selecciona la muestra a editar:",
                options=list(muestra_options.keys())
            )
            
            if selected_muestra:
                muestra_id = muestra_options[selected_muestra]
                muestra = get_muestra_by_id(session, muestra_id)
                
                if muestra:
                    st.info(f"**Muestra actual:** {muestra.nombre_muestra} | **Investigador:** {muestra.investigador or 'N/A'}")
                    
                    # Formulario de edición
                    with st.form(key=f"edit_form_{muestra_id}"):
                        new_name = st.text_input(
                            "Nuevo nombre de muestra:",
                            value=muestra.nombre_muestra,
                            help="Ingresa el nuevo nombre para la muestra"
                        )
                        new_investigador = st.text_input(
                            "Investigador:",
                            value=muestra.investigador or "",
                            help="Nombre del investigador responsable"
                        )
                        
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            submit_edit = st.form_submit_button("💾 Guardar Cambios", type="primary")
                        
                        if submit_edit:
                            if new_name.strip():
                                updated_muestra = update_muestra(
                                    session, 
                                    muestra_id, 
                                    nombre_muestra=new_name.strip(),
                                    investigador=new_investigador.strip() or None
                                )
                                if updated_muestra:
                                    st.success("✅ Muestra actualizada exitosamente!")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al actualizar la muestra.")
                            else:
                                st.error("❌ El nombre de la muestra no puede estar vacío.")
        
        elif action == "🗑️ Eliminar Muestra":
            st.subheader("🗑️ Eliminar Muestra")
            st.warning("⚠️ Esta acción eliminará permanentemente la muestra y su espectro asociado.")
            
            # Selector de muestra
            muestra_options = {f"{m.id} - {m.nombre_muestra}": m.id for m in muestras}
            selected_muestra = st.selectbox(
                "Selecciona la muestra a eliminar:",
                options=list(muestra_options.keys())
            )
            
            if selected_muestra:
                muestra_id = muestra_options[selected_muestra]
                muestra = get_muestra_by_id(session, muestra_id)
                
                if muestra:
                    st.error(f"**¿Estás seguro de que deseas eliminar:** {muestra.nombre_muestra}?")
                    st.write(f"**Investigador:** {muestra.investigador or 'N/A'}")
                    st.write(f"**Fecha:** {muestra.fecha.strftime('%Y-%m-%d %H:%M') if muestra.fecha else 'N/A'}")
                    
                    # Confirmación de eliminación
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("🗑️ Eliminar", type="primary", help="Esta acción no se puede deshacer"):
                            if delete_muestra(session, muestra_id):
                                st.success("✅ Muestra eliminada exitosamente!")
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar la muestra.")
                    with col2:
                        st.button("❌ Cancelar", help="Cancelar eliminación")
        
        # Mostrar tabla actualizada
        st.markdown("---")
        st.subheader("📋 Estado Actual de Muestras")
        show_mineral_database()
        
    finally:
        session.close()


def main():
    """Función principal de la aplicación Streamlit."""
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
        ["🏠 Inicio", "🔍 Identificar Mineral", "📊 Base de Datos", "⚙️ Gestión de Muestras", "ℹ️ Información"]
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
    
    elif page == "⚙️ Gestión de Muestras":
        manage_samples()
    
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