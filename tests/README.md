# Entorno de Pruebas - Sistema de Identificación de Minerales EDS

## 🧪 Estructura del Entorno de Pruebas

```
tests/
├── conftest.py                     # Configuración global y fixtures
├── pytest.ini                     # Configuración de pytest (raíz del proyecto)
├── run_tests.py                    # Script principal para ejecutar pruebas (raíz)
├── 
├── unit/                          # Pruebas unitarias
│   ├── test_vectorize.py          # Pruebas del módulo de vectorización
│   └── test_compare.py            # Pruebas del módulo de comparación
│
├── integration/                   # Pruebas de integración
│   ├── test_complete_pipeline.py  # Pipeline completo de identificación
│   └── test_legacy_pipeline.py    # Test original migrado
│
├── functional/                    # Pruebas funcionales
│   └── test_app.py                # Pruebas de la aplicación Streamlit
│
├── fixtures/                      # Utilidades y datos de prueba
│   └── test_data_manager.py       # Administrador de datos de prueba
│
└── test_data/                     # Archivos de muestra para pruebas
    ├── *.docx                     # 54 archivos DOCX con espectros EDS
    └── (minerales variados)
```

## 📊 Datos de Prueba Disponibles

### Archivos DOCX de Espectros Reales (54 archivos)
- **Magnetita**: 6 archivos
- **Malaquita**: 10 archivos  
- **Yeso**: 3 archivos
- **Calcita**: 3 archivos
- **Purpurita**: 4 archivos
- **Goethita**: 2 archivos
- **Otros minerales**: Amatista, Biotita, Epidota, Celestina, Óxido de Fe, Pirita, Siderita, etc.

### Datos Sintéticos
- Vectores generados algorítmicamente para pruebas controladas
- Patrones conocidos de similitud para validación
- Casos extremos y edge cases

## 🚀 Ejecución de Pruebas

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Comandos Básicos

#### Ejecutar todas las pruebas
```bash
python run_tests.py
# o
pytest tests/
```

#### Por tipo de prueba
```bash
python run_tests.py unit          # Solo pruebas unitarias
python run_tests.py integration   # Solo pruebas de integración  
python run_tests.py functional    # Solo pruebas funcionales
```

#### Con opciones adicionales
```bash
python run_tests.py --verbose     # Salida detallada
python run_tests.py --coverage    # Reporte de cobertura
python run_tests.py --fast        # Solo pruebas rápidas
```

#### Validación del entorno
```bash
python run_tests.py --validate    # Validar configuración
python run_tests.py --stats       # Mostrar estadísticas
```

### Comandos pytest directos
```bash
# Pruebas específicas por marcador
pytest -m "unit"                  # Solo pruebas unitarias
pytest -m "integration"           # Solo pruebas de integración
pytest -m "not slow"             # Excluir pruebas lentas

# Pruebas específicas por archivo
pytest tests/unit/test_vectorize.py
pytest tests/integration/test_complete_pipeline.py

# Con cobertura de código
pytest --cov=src --cov-report=html

# Ejecutar en paralelo (si tienes pytest-xdist)
pytest -n auto
```

## 🏷️ Marcadores de Pruebas

- `@pytest.mark.unit` - Pruebas unitarias rápidas
- `@pytest.mark.integration` - Pruebas de integración entre módulos
- `@pytest.mark.functional` - Pruebas de funcionalidad completa
- `@pytest.mark.slow` - Pruebas que toman tiempo (>5 segundos)
- `@pytest.mark.database` - Pruebas que requieren base de datos
- `@pytest.mark.spectrum` - Pruebas de procesamiento de espectros EDS

## 🔧 Configuración del Entorno

### Variables de Entorno
- `TESTING=1` - Activa el modo de pruebas (base de datos en memoria)
- `PYTHONPATH=.` - Asegura importación correcta de módulos

### Base de Datos
- **Producción**: SQLite en archivo (`minerales_eds.db`)
- **Pruebas**: SQLite en memoria (`:memory:`) para aislamiento
- **Configuración**: Automática mediante `TESTING` env var

### Fixtures Principales

#### `test_db`
Base de datos temporal para cada test, garantiza aislamiento completo.

#### `sample_mineral_data`
Datos básicos de un mineral para pruebas simples.

#### `populated_test_db` 
Base de datos pre-poblada con múltiples muestras.

#### `test_docx_files`
Lista de archivos DOCX reales disponibles para pruebas.

#### `normalized_test_vectors`
Vectores con similitudes conocidas para pruebas de comparación.

## 📈 Tipos de Pruebas Implementadas

### Pruebas Unitarias (`tests/unit/`)
- **Vectorización**: Cada componente del pipeline de procesamiento
- **Comparación**: Cálculos de similitud de coseno
- **Validación**: Normalización, manejo de errores, casos extremos

### Pruebas de Integración (`tests/integration/`)
- **Pipeline Completo**: Extracción → Vectorización → Comparación
- **Flujo de Datos**: Base de datos ↔ Algoritmos ↔ Interfaz
- **Consistencia**: Validación cruzada entre componentes

### Pruebas Funcionales (`tests/functional/`)
- **Interfaz Web**: Simulación de interacciones del usuario
- **Casos de Uso**: Flujos completos de identificación
- **Integridad**: Validación de datos en contexto real

## 🎯 Objetivos de Calidad

### Cobertura de Código
- **Meta**: >80% cobertura en módulos críticos
- **Prioridad**: `src/analysis/`, `src/database/`, `src/parsers/`

### Rendimiento
- **Unitarias**: <1 segundo cada una
- **Integración**: <10 segundos cada una  
- **Funcionales**: <30 segundos cada una

### Robustez
- **Casos extremos**: Archivos corruptos, vectores vacíos, BD desconectada
- **Validación**: Todos los inputs y outputs
- **Recuperación**: Manejo elegante de errores

## 🔍 Debugging y Troubleshooting

### Logs de Pruebas
```bash
pytest -v -s --tb=long  # Máximo detalle de errores
```

### Pruebas Específicas
```bash
pytest tests/unit/test_vectorize.py::TestVectorizeComponents::test_normalize_vector -v
```

### Reporte de Cobertura
```bash
pytest --cov=src --cov-report=html
# Ver: htmlcov/index.html
```

### Validación del Entorno
```bash
python run_tests.py --validate
```

## 🚨 Problemas Comunes

1. **ImportError**: Verificar `PYTHONPATH` y estructura de archivos
2. **Database errors**: Comprobar que `TESTING=1` esté configurado
3. **FileNotFoundError**: Validar que existan archivos en `test_data/`
4. **Timeout**: Usar `--fast` para pruebas rápidas durante desarrollo

## 📚 Recursos Adicionales

- [Documentación pytest](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Streamlit Testing](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps)