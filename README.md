# Tesis: Identificación de Minerales mediante Espectros EDS

Este proyecto de tesis desarrolla una aplicación para identificar minerales a partir de espectros EDS obtenidos con microscopía electrónica de barrido. Utiliza procesamiento de imágenes y cálculos de similitud en Python.

## 🚀 MVP - Configuración Rápida

### Instalación Automática
```bash
python setup_mvp.py
```

### Instalación Manual
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Poblar la base de datos
python populate_database.py

# 3. Ejecutar la aplicación web
streamlit run app.py
```

## 🔬 Características del Sistema

- **Procesamiento automático** de archivos DOCX con espectros EDS
- **Vectorización** de espectros mediante procesamiento de imágenes
- **Base de datos SQLite** para almacenar vectores de referencia
- **Interfaz web interactiva** con Streamlit
- **Identificación** mediante similitud de coseno

## 📁 Estructura del Proyecto

```
tesis-identificacion-minerales/
├── app.py                    # Aplicación web MVP
├── populate_database.py      # Script para poblar BD
├── setup_mvp.py             # Configuración automática
├── src/
│   ├── main.py              # Script principal de prueba
│   ├── analysis/            # Módulos de análisis
│   │   ├── vectorize.py     # Vectorización de espectros
│   │   └── compare.py       # Comparación de similitud
│   ├── database/            # Módulos de base de datos
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   ├── connection.py    # Configuración BD
│   │   └── queries.py       # Operaciones CRUD
│   └── parsers/
│       └── docx_parser.py   # Extracción de imágenes DOCX
├── muestrasdatos/           # Datos de entrenamiento
│   └── Muestras Tesis/      # Archivos DOCX con espectros
└── tests/                   # Tests unitarios
```

## 🧪 Algoritmo de Identificación

1. **Extracción**: Se extrae la imagen del espectro EDS del archivo DOCX
2. **Preprocesamiento**: Se convierte a escala de grises y se aplica filtro Gaussiano
3. **Segmentación**: Se crea una máscara binaria para separar el espectro del fondo
4. **Vectorización**: Se calcula el perfil del espectro y se redimensiona a 200 dimensiones
5. **Normalización**: Se normaliza el vector para comparación
6. **Comparación**: Se calcula la similitud de coseno contra todas las muestras

## 📊 Métricas de Similitud

- **> 80%**: Identificación muy probable
- **60-80%**: Posible identificación  
- **< 60%**: Requiere análisis adicional

## 🛠️ Tecnologías Utilizadas

- **Python >= 3.9**
- **OpenCV**: Procesamiento de imágenes
- **NumPy**: Cálculos matemáticos
- **SQLAlchemy**: ORM para base de datos
- **Streamlit**: Interfaz web
- **python-docx**: Procesamiento de archivos DOCX

## 📋 Comandos Útiles

```bash
# Poblar base de datos
python populate_database.py

# Probar procesamiento individual
python src/main.py

# Ejecutar aplicación web
streamlit run app.py

# Ejecutar tests
pytest tests/
```

## 🎯 Uso del Sistema

1. **Configura el entorno**: Ejecuta `python setup_mvp.py`
2. **Abre la aplicación**: Ejecuta `streamlit run app.py`
3. **Sube un archivo DOCX** con espectro EDS en la sección "Identificar Mineral"
4. **Obtén resultados** ordenados por similitud con confianza estimada

## 📝 Notas de Desarrollo

- La base de datos se crea automáticamente en `minerales_eds.db`
- Los espectros deben tener dimensiones de 400x512x3 píxeles
- El sistema busca automáticamente estas imágenes en los archivos DOCX
- Los vectores se normalizan usando la norma L2 para comparación
