# Arquitectura del Sistema de Identificación de Minerales EDS

## Resumen
Sistema web para identificación automática de minerales mediante análisis de espectros EDS (Energy Dispersive Spectroscopy) obtenidos con microscopía electrónica de barrido.

## Arquitectura de Capas

### 🗄️ Capa de Datos (SQLite)
- **Base de datos**: `minerales_eds.db`
- **Tablas principales**:
  - `muestras`: Información de las muestras minerales
  - `espectros_vectorizados`: Vectores normalizados de 200 dimensiones
- **Almacenamiento**: Vectores como JSON para compatibilidad con SQLite

### 🧠 Capa de Procesamiento
**Módulos principales:**
- `src/parsers/docx_parser.py`: Extracción de imágenes desde archivos DOCX
- `src/analysis/vectorize.py`: Pipeline de vectorización de espectros
- `src/analysis/compare.py`: Algoritmos de comparación y similitud

**Pipeline de procesamiento:**
1. Extracción de imagen (400x512x3 píxeles)
2. Preprocesamiento (filtro Gaussiano)
3. Segmentación binaria (umbralización)
4. Recorte inteligente de región de interés
5. Cálculo de perfil espectral
6. Redimensionado a 200 dimensiones
7. Normalización L2

### 🖥️ Capa de Presentación (Streamlit)
- **Interfaz web interactiva**
- **Funcionalidades**:
  - Carga de archivos DOCX
  - Visualización de base de datos
  - Resultados de identificación con confianza
  - Estadísticas del sistema

### 🔧 Capa de Datos/ORM
- **SQLAlchemy**: Mapeo objeto-relacional
- **Modelos**: `Muestra` y `EspectroVectorizado`
- **Operaciones CRUD** optimizadas

## Algoritmo de Identificación

### Vectorización
```
Imagen EDS → Escala de grises → Máscara binaria → Perfil → Vector normalizado
```

### Comparación
- **Métrica**: Similitud de coseno
- **Umbral de confianza**:
  - `> 80%`: Identificación muy probable
  - `60-80%`: Posible identificación
  - `< 60%`: Requiere análisis adicional

## Tecnologías Utilizadas

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Backend | Python 3.9+ | Lógica principal |
| Procesamiento | OpenCV | Análisis de imágenes |
| Cálculos | NumPy | Operaciones matemáticas |
| Base de datos | SQLite + SQLAlchemy | Almacenamiento |
| Frontend | Streamlit | Interfaz web |
| Documentos | python-docx | Procesamiento DOCX |

## Estructura del Proyecto

```
├── app.py                    # Aplicación web principal
├── populate_database.py      # Script de población de BD
├── setup_mvp.py             # Configuración automática
├── src/
│   ├── analysis/            # Algoritmos de procesamiento
│   ├── database/            # Modelos y conexiones
│   ├── parsers/             # Procesamiento de archivos
│   └── main.py              # Script de prueba
├── tests/                   # Tests del sistema
├── muestrasdatos/           # Dataset de entrenamiento
└── docs/                    # Documentación

```

## Métricas de Rendimiento

- **Vectorización**: ~100ms por espectro
- **Comparación**: ~50ms contra base de datos completa
- **Precisión**: Variable según calidad del espectro
- **Escalabilidad**: Lineal con tamaño de base de datos
