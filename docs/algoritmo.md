# Algoritmo de Identificación de Minerales mediante Espectros EDS

## Resumen
Sistema que identifica minerales mediante comparación de espectros EDS (Energy Dispersive Spectroscopy) usando vectorización de imágenes y similitud de coseno.

## Flujo del Algoritmo

### 1. Extracción de la Imagen del Espectro
**Módulo**: `src/parsers/docx_parser.py`
- Se abre el archivo DOCX proporcionado por el usuario
- Se extraen todas las imágenes embebidas en el documento
- Se identifica la imagen del espectro EDS buscando dimensiones específicas (400×512×3 píxeles)
- Las imágenes temporales se eliminan tras el procesamiento

### 2. Preprocesamiento de la Imagen
**Módulo**: `src/analysis/vectorize.py`
- **Conversión a formato flotante**: La imagen se normaliza a valores entre 0 y 1
- **Filtro Gaussiano**: Se aplica suavizado con kernel 5×5 para reducir ruido
- **Conversión a escala de grises**: Se transforma la imagen RGB a un canal único

### 3. Segmentación del Espectro
- **Umbralización**: Se crea una máscara binaria separando el espectro del fondo (umbral = 0.99)
- **Recorte**: Se delimita la región de interés eliminando píxeles irrelevantes
  - Recorte horizontal: identifica columnas con información
  - Recorte vertical: usa límites predefinidos (filas 150-250) para aislar el espectro

### 4. Extracción de la Firma Espectral
- **Cálculo del perfil**: Se computa la media de intensidad por columna en la máscara
- El resultado es un vector 1D que representa la "firma" del espectro

### 5. Normalización del Vector
- **Redimensionamiento**: Se interpola la firma a 200 dimensiones fijas mediante interpolación lineal
- **Normalización L2**: Se normaliza el vector usando la norma euclidiana para garantizar comparaciones robustas

### 6. Comparación con Base de Datos
**Módulo**: `src/analysis/compare.py`
- El vector normalizado se compara contra todos los vectores almacenados en la base de datos SQLite
- **Métrica**: Similitud de coseno (producto punto entre vectores normalizados)
- **Fórmula**: `similitud = (v1 · v2) / (||v1|| × ||v2||)`
- Los resultados se ordenan descendentemente por similitud

### 7. Interpretación de Resultados
- **Similitud > 80%**: Identificación muy probable (confianza alta)
- **Similitud 60-80%**: Posible identificación (confianza media)
- **Similitud < 60%**: Requiere análisis adicional (confianza baja)

## Tecnologías Clave
- **OpenCV**: Procesamiento de imágenes y filtros
- **NumPy**: Operaciones vectoriales y cálculos matemáticos
- **SQLAlchemy**: Persistencia de vectores en SQLite
- **python-docx**: Extracción de imágenes de documentos

## Resultado Final
La aplicación retorna una lista ordenada de minerales candidatos con sus porcentajes de similitud, permitiendo al investigador identificar la muestra desconocida por comparación con patrones conocidos.
