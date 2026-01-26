# 📚 Documentación Técnica del Sistema de Identificación de Minerales mediante Espectros EDS

## 📋 Introducción

Este documento explica en detalle cómo funciona cada archivo del aplicativo de identificación de minerales mediante espectros EDS. El sistema utiliza técnicas de procesamiento de imágenes y análisis de similitud para identificar minerales a partir de sus espectros de energía dispersiva (EDS).

## 🏗️ Arquitectura del Sistema

El aplicativo sigue una arquitectura modular dividida en las siguientes capas:

- **Aplicación Web** (`app.py`): Interfaz de usuario desarrollada en Streamlit
- **Capa de Análisis** (`src/analysis/`): Módulos para vectorización y comparación de espectros
- **Capa de Base de Datos** (`src/database/`): Modelos, conexiones y consultas
- **Capa de Parsers** (`src/parsers/`): Extracción de imágenes de documentos DOCX
- **Scripts de Utilidad**: Configuración y población de datos

---

## 🔍 Descripción Detallada de Archivos

### 📱 Aplicación Principal

#### `app.py` - Aplicación Web MVP

**Propósito:** Interfaz web interactiva desarrollada con Streamlit para que los usuarios puedan subir espectros EDS y obtener identificaciones de minerales.

**Funciones principales:**

1. **`setup_database()`**
   - Inicializa las tablas de la base de datos si no existen
   - Se ejecuta al inicio de la aplicación

2. **`show_database_stats()`**
   - Muestra estadísticas básicas de la base de datos
   - Cuenta total de muestras y muestras con espectros vectorizados
   - Presenta la información en columnas usando métricas de Streamlit

3. **`show_mineral_database()`**
   - Muestra una tabla interactiva con todos los minerales en la base de datos
   - Incluye ID, nombre del mineral, investigador y fecha
   - Utiliza DataFrame de pandas para la visualización

4. **`identify_mineral()`**
   - **Función central del sistema**
   - Permite subir archivos DOCX con espectros EDS
   - Procesa el archivo temporal usando `extract_and_vectorize_spectrum()`
   - Guarda el nuevo espectro en la base de datos
   - Compara contra todos los minerales conocidos usando similitud de coseno
   - Muestra resultados ordenados por similitud con niveles de confianza:
     - **Alta (>80%)**: Identificación muy probable
     - **Media (60-80%)**: Posible identificación
     - **Baja (<60%)**: Requiere análisis adicional

5. **`main()`**
   - Configura la interfaz de Streamlit
   - Maneja la navegación entre páginas (Inicio, Identificar, Base de Datos, Información)
   - Proporciona información técnica del algoritmo

**Flujo de trabajo:**
1. Usuario sube archivo DOCX
2. Se crea archivo temporal
3. Se extrae y vectoriza el espectro
4. Se guarda en la base de datos
5. Se compara con todos los minerales existentes
6. Se muestran resultados ordenados por similitud

---

### 🧠 Capa de Análisis

#### `src/analysis/vectorize.py` - Vectorización de Espectros

**Propósito:** Convierte imágenes de espectros EDS en vectores numéricos normalizados que pueden ser comparados matemáticamente.

**Pipeline de procesamiento:**

1. **`read_image_float(image_path)`**
   - Lee imagen y la convierte a formato float32 normalizado (0-1)
   - Convierte imágenes en escala de grises a BGR si es necesario
   - **Entrada:** Ruta de imagen
   - **Salida:** Array numpy float32 normalizado

2. **`preprocess_image(img)`**
   - Aplica filtro Gaussiano (5x5) para reducir ruido
   - Suaviza la imagen para mejor procesamiento posterior
   - **Parámetros:** Kernel 5x5, sigma automático

3. **`convert_to_grayscale(img)`**
   - Convierte imagen BGR a escala de grises
   - Necesario para la segmentación binaria

4. **`extract_mask(gray, threshold=0.99)`**
   - **Función clave para segmentación**
   - Crea máscara binaria separando espectro del fondo
   - Píxeles < umbral = espectro (255), píxeles >= umbral = fondo (0)
   - Umbral alto (0.99) porque el fondo es típicamente blanco

5. **`crop_mask(mask, row_bounds=None)`**
   - Recorta la máscara a la región de interés del espectro
   - **Recorte horizontal:** Busca columnas con píxeles no-cero
   - **Recorte vertical:** Usa row_bounds (150,250) para enfocarse en la región del espectro
   - **Salida:** Máscara recortada y coordenadas de recorte

6. **`compute_signature(mask_cropped, method="mean")`**
   - Calcula la "firma" del espectro
   - **Método "mean":** Promedio de intensidades por columna (perfil horizontal)
   - **Método "max":** Valor máximo por columna
   - **Resultado:** Array 1D que representa el perfil del espectro

7. **`resize_signature(signature, vector_size=200)`**
   - Redimensiona la firma a tamaño fijo (200 dimensiones)
   - Usa interpolación lineal para mantener la forma del espectro
   - **Importante:** Tamaño fijo permite comparación entre espectros diferentes

8. **`normalize_vector(vec)`**
   - Normaliza usando norma L2 (euclidiana)
   - **Fórmula:** vector / ||vector||₂
   - **Propósito:** Hace que la comparación sea independiente de la intensidad absoluta

9. **`vectorize_spectrum(image_path, vector_size=200, threshold=0.99, row_bounds=(150,250), method="mean")`**
   - **Función principal** que ejecuta todo el pipeline
   - **Parámetros configurables:**
     - `vector_size`: Dimensiones del vector final (default: 200)
     - `threshold`: Umbral de binarización (default: 0.99)
     - `row_bounds`: Límites verticales para recorte (default: 150-250)
     - `method`: Método de cálculo de firma ("mean" o "max")

**Algoritmo de vectorización paso a paso:**
```
Imagen EDS → Float32 → Filtro Gaussiano → Escala de grises → 
Máscara binaria → Recorte ROI → Firma espectral → 
Redimensionamiento → Normalización L2 → Vector final
```

#### `src/analysis/compare.py` - Comparación de Espectros

**Propósito:** Compara espectros vectorizados usando similitud de coseno para identificar minerales.

**Funciones principales:**

1. **`calcular_similitud(vector1, vector2)`**
   - **Implementa similitud de coseno**
   - **Fórmula:** cos(θ) = (A·B) / (||A|| × ||B||)
   - **Rango:** [-1, 1], donde 1 = idénticos, 0 = perpendiculares, -1 = opuestos
   - **Ventaja:** Independiente de la magnitud, se enfoca en la forma del espectro
   - Maneja casos especiales (vectores con norma 0)

2. **`compare_spectrum(session, muestra_id, similitud_umbral=0.5)`**
   - **Función principal de comparación**
   - **Proceso:**
     1. Obtiene el vector de la muestra base desde la BD
     2. Carga todos los otros vectores de espectros
     3. Calcula similitud de coseno contra cada uno
     4. Ordena resultados por similitud (descendente)
     5. Filtra por umbral mínimo de similitud
   - **Salida:** Lista de tuplas (muestra_id, nombre_mineral, similitud)

**¿Por qué similitud de coseno?**
- **Invariante a escala:** No importa la intensidad absoluta del espectro
- **Enfoque en forma:** Compara la forma característica del espectro
- **Robusta al ruido:** Menos sensible a variaciones en intensidad
- **Interpretable:** Valores entre 0-1 fáciles de entender como porcentajes

---

### 🗄️ Capa de Base de Datos

#### `src/database/models.py` - Modelos de Datos

**Propósito:** Define la estructura de las tablas usando SQLAlchemy ORM.

**Modelos principales:**

1. **`Muestra`** (Tabla: "muestras")
   - **`id`**: Clave primaria autoincremental
   - **`nombre_muestra`**: Nombre del mineral (ej: "CUARZO", "MAGNETITA")
   - **`fecha`**: Timestamp de creación (automático)
   - **`investigador`**: Quién proporcionó la muestra (opcional)
   - **`ruta_imagen`**: Ruta del archivo DOCX original (opcional)
   - **Relación:** 1:1 con EspectroVectorizado

2. **`EspectroVectorizado`** (Tabla: "espectros_vectorizados")
   - **`id`**: Clave primaria autoincremental
   - **`muestra_id`**: Clave foránea hacia Muestra
   - **`vector_json`**: Vector almacenado como JSON string
   - **Propiedades especiales:**
     - **`vector` (getter)**: Convierte JSON → lista de números
     - **`vector` (setter)**: Convierte lista/array → JSON string
   - **Relación:** N:1 con Muestra

**Decisiones de diseño:**
- **SQLite compatible:** Usa JSON para arrays (SQLite no tiene tipo array nativo)
- **Separación de datos:** Metadatos en una tabla, vectores en otra
- **Relaciones explícitas:** Facilita consultas complejas
- **Conversión automática:** Properties para manejo transparente de vectores

#### `src/database/connection.py` - Conexión a Base de Datos

**Propósito:** Configura la conexión a SQLite de manera flexible para desarrollo y testing.

**Funciones principales:**

1. **`get_database_url()`**
   - **Producción:** `sqlite:///minerales_eds.db` (archivo persistente)
   - **Testing:** `sqlite:///:memory:` (base de datos en memoria)
   - **Control:** Variable de entorno `TESTING`

**Configuración:**
- **Engine:** Configurado con echo condicional (silencioso en tests)
- **SessionLocal:** Factory para crear sesiones de base de datos
- **Patrón:** Dependency injection para facilitar testing

#### `src/database/queries.py` - Operaciones de Base de Datos

**Propósito:** Encapsula todas las operaciones CRUD de la base de datos.

**Funciones principales:**

1. **`create_tables()`**
   - Crea todas las tablas definidas en models.py
   - Idempotente: no falla si ya existen

2. **`insert_muestra(session, nombre_muestra, investigador=None, ruta_imagen=None)`**
   - Inserta nueva muestra en la base de datos
   - **Commit automático** y refresh para obtener ID
   - **Retorna:** Objeto Muestra con ID asignado

3. **`insert_espectro(session, muestra_id, vector)`**
   - Asocia vector de espectro con una muestra
   - **Conversión automática:** Array numpy → JSON string
   - **Validación:** Verifica que muestra_id existe

4. **Consultas de lectura:**
   - **`get_all_muestras(session)`**: Todas las muestras
   - **`get_muestra_by_id(session, muestra_id)`**: Muestra específica
   - **`get_espectro_by_muestra_id(session, muestra_id)`**: Espectro de una muestra
   - **`count_muestras(session)`**: Contador total
   - **`get_all_muestras_with_vectors(session)`**: Solo muestras con espectros

**Patrón de uso:**
```python
session = SessionLocal()
try:
    # Operaciones de base de datos
    result = query_function(session, parameters)
finally:
    session.close()  # Importante: siempre cerrar
```

---

### 📄 Capa de Parsers

#### `src/parsers/docx_parser.py` - Extracción de Espectros de DOCX

**Propósito:** Extrae imágenes de espectros EDS desde documentos Word (.docx) y las vectoriza.

**Función principal:**

**`extract_and_vectorize_spectrum(docx_path, vector_size=200, temp_folder="data/temp_images")`**

**Algoritmo detallado:**

1. **Apertura del documento**
   - Usa `python-docx` para acceder al archivo DOCX
   - Accede a las relaciones internas del documento

2. **Extracción de imágenes**
   - Recorre todas las relaciones del documento (`doc.part.rels.values()`)
   - Identifica relaciones de tipo "image"
   - Extrae cada imagen como blob binario
   - Guarda temporalmente con nombre único (UUID)

3. **Búsqueda del espectro EDS**
   - **Criterio específico:** Imagen con dimensiones exactas (400, 512, 3)
   - **Justificación:** Los espectros EDS del dataset tienen estas dimensiones específicas
   - Usa OpenCV para leer y verificar dimensiones

4. **Vectorización inmediata**
   - En cuanto encuentra la imagen correcta, la vectoriza usando `vectorize_spectrum()`
   - **Parámetros:** vector_size=200 para consistencia
   - Rompe el bucle después de encontrar la primera coincidencia

5. **Limpieza**
   - **Importante:** Borra todas las imágenes temporales extraídas
   - Evita acumulación de archivos temporales
   - Se ejecuta independientemente del éxito/fallo

**Ventajas del diseño:**
- **Robusto:** Maneja documentos con múltiples imágenes
- **Específico:** Solo procesa imágenes del tamaño correcto
- **Eficiente:** Para en la primera imagen válida
- **Limpio:** No deja archivos temporales

---

### 🛠️ Scripts de Utilidad

#### `populate_database.py` - Población de Base de Datos

**Propósito:** Script para procesar en lote todos los archivos DOCX de muestras conocidas y poblar la base de datos.

**Funciones principales:**

1. **`extract_mineral_name(filename)`**
   - **Entrada:** Nombre de archivo (ej: "EDS ALBITA_02.docx")
   - **Proceso:**
     1. Quita extensión .docx
     2. Remueve prefijos comunes ("EDS ", "Eds ", "Element ")
     3. Separa por underscore o números
     4. Toma la primera parte y la convierte a mayúsculas
   - **Salida:** Nombre limpio del mineral (ej: "ALBITA")

2. **`populate_database()`**
   - **Proceso completo de población:**
     1. **Inicialización:** Crea tablas si no existen
     2. **Descubrimiento:** Busca archivos DOCX en "muestrasdatos/Muestras Tesis/"
     3. **Procesamiento por archivo:**
        - Extrae nombre del mineral del filename
        - Vectoriza el espectro usando `extract_and_vectorize_spectrum()`
        - Inserta muestra y espectro en la BD
        - Maneja errores individualmente
     4. **Estadísticas:** Reporta éxitos, errores y total final

**Características importantes:**
- **Tolerancia a fallos:** Continúa si un archivo falla
- **Logging detallado:** Reporta progreso y errores
- **Estadísticas finales:** Resumen completo del procesamiento
- **Batch processing:** Procesa múltiples archivos automáticamente

#### `setup_mvp.py` - Configuración Automática

**Propósito:** Script de configuración que automatiza la instalación y configuración inicial del sistema.

**Funciones principales:**

1. **`check_python_version()`**
   - Verifica Python >= 3.9
   - **Justificación:** Compatibilidad con bibliotecas modernas
   - Termina ejecución si la versión es incompatible

2. **`install_dependencies()`**
   - Instala paquetes desde requirements.txt
   - Usa el mismo intérprete Python que ejecuta el script
   - **Comando:** `python -m pip install -r requirements.txt`

3. **`populate_database()`**
   - Ejecuta populate_database.py como subproceso
   - **Interactivo:** Pregunta al usuario antes de poblar
   - Maneja errores gracefully

4. **`run_command(command, description)`**
   - **Utilidad general** para ejecutar comandos del sistema
   - Captura stdout y stderr
   - Reporta éxito/fallo con mensajes claros

**Flujo de configuración:**
1. Verificación de versión Python
2. Instalación de dependencias
3. Población opcional de base de datos
4. Instrucciones para ejecutar la aplicación

#### `src/main.py` - Script de Pruebas

**Propósito:** Script de desarrollo para probar el pipeline completo con una muestra individual.

**Funcionalidades:**
1. **Procesamiento individual:** Procesa un archivo DOCX específico
2. **Inserción en BD:** Agrega la muestra procesada a la base de datos
3. **Comparación:** Si hay otras muestras, ejecuta comparación de similitud
4. **Estadísticas:** Muestra información de la base de datos

**Uso típico:**
- Desarrollo y debugging del pipeline
- Verificación de funcionamiento con muestras específicas
- Testing de la funcionalidad de comparación

---

## 🔄 Flujo de Datos Completo

### 1. Entrada de Datos
```
Archivo DOCX → Parser → Extracción de imágenes → Filtrado por dimensiones (400x512x3)
```

### 2. Procesamiento de Espectro
```
Imagen EDS → Vectorización (8 pasos) → Vector normalizado (200 dimensiones)
```

### 3. Almacenamiento
```
Vector + Metadatos → Base de datos SQLite → Tablas relacionales
```

### 4. Identificación
```
Nuevo espectro → Comparación con BD → Similitud de coseno → Ranking de resultados
```

### 5. Presentación
```
Resultados → Interfaz Streamlit → Visualización interactiva
```

---

## 🎯 Características Técnicas Clave

### Algoritmo de Procesamiento de Imágenes
1. **Normalización:** Conversión a float32 (0-1)
2. **Suavizado:** Filtro Gaussiano para reducir ruido
3. **Segmentación:** Umbralización binaria para separar espectro del fondo
4. **ROI Extraction:** Recorte inteligente de la región de interés
5. **Vectorización:** Cálculo de perfil espectral horizontal
6. **Normalización L2:** Vector independiente de escala

### Sistema de Similitud
- **Métrica:** Similitud de coseno
- **Ventajas:** Invariante a escala, enfoque en forma
- **Interpretación:** Porcentaje de similitud (0-100%)
- **Umbralización:** Múltiples niveles de confianza

### Arquitectura de Datos
- **Base de datos:** SQLite (portable y sin configuración)
- **ORM:** SQLAlchemy para abstracción de BD
- **Vectores:** Almacenados como JSON para compatibilidad
- **Relaciones:** 1:1 entre muestras y espectros

### Interfaz de Usuario
- **Framework:** Streamlit (web interactiva)
- **Navegación:** Múltiples páginas especializadas
- **Visualización:** DataFrames, métricas, y uploads
- **Feedback:** Mensajes de éxito/error en tiempo real

---

## 🔧 Parámetros Configurables

### Vectorización
- `vector_size`: Dimensiones del vector final (default: 200)
- `threshold`: Umbral de binarización (default: 0.99)
- `row_bounds`: Límites de recorte vertical (default: 150-250)
- `method`: Método de cálculo de perfil ("mean" o "max")

### Comparación
- `similitud_umbral`: Umbral mínimo para mostrar resultados (default: 0.5)

### Base de Datos
- `DATABASE_URL`: Ruta de la base de datos SQLite
- `echo`: Logging de consultas SQL (automático en desarrollo)

---

## 📊 Métricas de Rendimiento

### Niveles de Confianza
- **Alta (>80%)**: Identificación muy probable
- **Media (60-80%)**: Posible identificación  
- **Baja (<60%)**: Requiere análisis adicional

### Dimensiones de Trabajo
- **Imagen original**: 400 × 512 × 3 píxeles
- **Vector final**: 200 dimensiones
- **Tiempo de procesamiento**: ~1-2 segundos por espectro
- **Base de datos**: Escalable a miles de muestras

---

## 🚀 Extensibilidad

El sistema está diseñado para ser extensible:

1. **Nuevos algoritmos de vectorización:** Modificar `vectorize.py`
2. **Diferentes métricas de similitud:** Extender `compare.py`
3. **Formatos de entrada adicionales:** Agregar parsers en `parsers/`
4. **Interfaces alternativas:** La lógica está separada de la UI
5. **Bases de datos diferentes:** Configuración flexible en `connection.py`

Este diseño modular permite evolucionar el sistema según las necesidades de investigación y análisis de minerales.