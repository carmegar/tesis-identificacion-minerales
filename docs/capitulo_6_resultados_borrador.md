# CAPÍTULO 6. RESULTADOS Y DISCUSIÓN

Este capítulo presenta los resultados obtenidos tras la implementación del sistema de identificación de minerales, estructurados de acuerdo con los objetivos específicos planteados. Se detalla el diseño de la base de datos, la validación del algoritmo de comparación espectral, la arquitectura de la aplicación y el análisis de desempeño utilizando un conjunto de datos de prueba independiente.

## 6.1. Resultado del Objetivo 1: Diseño y Estructuración de la Base de Datos

Para dar cumplimiento al primer objetivo específico, se diseñó y pobló una base de datos relacional optimizada para el almacenamiento eficiente de firmas espectrales. A diferencia de un almacenamiento en archivos planos, el uso de una base de datos relacional (SQLite) permitió garantizar la integridad referencial y facilitar la escalabilidad del sistema.

### 6.1.1. Estructura de Datos
Se definieron dos entidades principales: `Muestras` y `Espectros_Vectorizados`. Esta separación asegura que los metadatos administrativos puedan actualizarse independientemente de los vectores característicos matemáticos. La estructura de campos seleccionada se detalla en la **Tabla 1**.

**Tabla 1. Diccionario de Datos del Sistema**

| Entidad | Campo | Tipo de Dato | Descripción y Justificación Técnica |
|---|---|---|---|
| **Muestras** | `id` | INTEGER (PK) | Identificador único autoincremental para indexación rápida. |
| | `nombre_muestra` | TEXT | Etiqueta mineralógica estandarizada. |
| | `fuente` | TEXT | Origen del espectro (Ej. "SFU", "UIS-Guatiguara") para trazabilidad. |
| | `ruta_imagen` | TEXT | Referencia al archivo fuente original (DOCX/JPG). |
| **Espectros** | `id` | INTEGER (PK) | Identificador único del vector. |
| | `muestra_id` | INTEGER (FK) | Clave foránea que vincula el vector con sus metadatos. |
| | `vector_json` | TEXT | Array serializado de 200 valores flotantes. Se utilizó formato JSON por su portabilidad y compatibilidad nativa con múltiples lenguajes de programación. |

### 6.1.2. Composición de la Base de Datos
Se alcanzó un total de **101 muestras** procesadas y almacenadas, superando el indicador inicial planteado de 100 muestras. Para asegurar la robustez del sistema frente a la variabilidad geológica, se recopilaron espectros de cinco fuentes diferentes, incluyendo bases de datos internacionales (Simon Fraser University) y muestras locales del laboratorio de Guatiguara.

La distribución mineralógica, presentada en la **Figura 6.1**, evidencia una cobertura mayoritaria de silicatos (45%), lo cual es consistente con la abundancia natural de este grupo en la corteza terrestre, seguido por sulfuros, óxidos y grupos menores.

> **[INSERTAR AQUÍ: grafico_1_distribucion.png]**
> *Figura 6.1. Distribución porcentual de grupos mineralógicos en la base de datos de entrenamiento (n=101).*

## 6.2. Resultado del Objetivo 2: Sistema de Comparación Espectral

El núcleo del sistema de identificación se fundamenta en un algoritmo de comparación vectorial. Tras evaluar distintas métricas de distancia, se seleccionó la **Similitud de Coseno**.

### 6.2.1. Justificación del Algoritmo
Se realizó una evaluación comparativa frente a la Distancia Euclidiana. Se concluyó que la Distancia Euclidiana no era adecuada para este contexto debido a su sensibilidad a la magnitud absoluta de los picos espectrales, la cual varía significativamente según el tiempo de exposición y la corriente del haz de electrones durante el análisis EDS.

Por el contrario, la similitud de coseno mide el coseno del ángulo entre dos vectores, lo que la hace matemáticamente invariante a la escala (magnitud) de los vectores. Esto permite que el sistema identifique correctamente un mineral independientemente de si el espectro fue adquirido en 30 segundos o en 2 minutos, siempre que la proporción relativa de los picos característicos se mantenga.

### 6.2.2. Pipeline de Procesamiento
Para transformar las imágenes de espectros EDS en vectores matemáticos comparables, se implementó un pipeline de procesamiento de imágenes con seis etapas críticas, ilustrado en la **Figura 6.2**.

> **[INSERTAR AQUÍ: grafico_2_pipeline.png]**
> *Figura 6.2. Pipeline de procesamiento: desde la imagen cruda hasta el vector normalizado.*

1.  **Preprocesamiento:** Aplicación de filtro Gaussiano (kernel 5x5) para reducir el ruido aleatorio inherente a la señal electrónica.
2.  **Binarización:** Separación de la señal espectral del fondo mediante umbralización adaptativa.
3.  **Extracción de Firma:** Conversión de la morfología de la imagen a una señal 1D.
4.  **Normalización:** Redimensionamiento vectorial a 200 dimensiones y normalización L2, garantizando que todos los vectores tengan longitud unitaria para optimizar el cálculo del producto punto.

La implementación final en Python, utilizando la librería NumPy, logra tiempos de comparación promedio inferiores a 50 milisegundos por consulta, cumpliendo con los requisitos de eficiencia computacional.

## 6.3. Resultado del Objetivo 3: Desarrollo de la Aplicación

La herramienta de software se construyó bajo una arquitectura modular de tres capas, separando claramente la interfaz de usuario de la lógica de negocio y el acceso a datos.

### 6.3.1. Arquitectura del Sistema
Como se muestra en la **Figura 6.3**, el diseño desacoplado permite que el módulo de análisis (`Compare.py`) funcione de manera independiente.

> **[INSERTAR AQUÍ: grafico_3_arquitectura.png]**
> *Figura 6.3. Arquitectura modular de tres capas implementada en el sistema.*

*   **Capa de Presentación:** Desarrollada con Streamlit, ofrece una interfaz web accesible sin necesidad de instalación local compleja.
*   **Capa de Lógica:** Contiene los algoritmos de vectorización y comparación descritos previamente.
*   **Capa de Datos:** Gestiona las consultas SQL y la persistencia en el archivo `minerales_eds.db`.

Esta arquitectura ha demostrado ser robusta, permitiendo la migración del despliegue desde un entorno local a la nube (Streamlit Cloud) sin requerir cambios en el código fuente de la lógica de procesamiento.

## 6.4. Resultado del Objetivo 4: Validación y Análisis de Desempeño

La etapa final del proyecto consistió en validar la precisión y confiabilidad del sistema utilizando un conjunto de datos de prueba independiente a los datos de entrenamiento (validación *hold-out*).

### 6.4.1. Conjunto de Validación
Se recopiló un conjunto de validación compuesto por **54 espectros independientes**. Es importante notar que, aunque el objetivo inicial planteaba 100 espectros de validación, la escasa disponibilidad de bases de datos públicas de imágenes EDS (a diferencia de espectros Raman o XRD) limitó el tamaño de la muestra. Sin embargo, este conjunto es estadísticamente significativo para detectar patrones de error y estimar la precisión del sistema.

### 6.4.2. Métricas de Desempeño
Se evaluó el sistema comparando la etiqueta real del mineral (Ground Truth) frente a la predicción del algoritmo. Los resultados globales se resumen en la **Figura 6.4**.

> **[INSERTAR AQUÍ: grafico_4_validacion.png]**
> *Figura 6.4. Resultados de la validación: Aciertos vs Fallos sobre 54 muestras de prueba.*

Las métricas cuantitativas obtenidas son:

*   **Exactitud General (Accuracy):** 64.81% (35 aciertos de 54 pruebas).
*   **Exactitud Ajustada:** 67.31%. Esta métrica excluye los casos donde el mineral de prueba no existía en la base de datos de entrenamiento (ej. Amatista), ya que es técnicamente imposible que el sistema clasifique correctamente una clase desconocida.
*   **Nivel de Confianza Promedio:** 96.18%. Este alto valor indica que, cuando el sistema encuentra una coincidencia, la similitud vectorial es muy alta.

### 6.4.3. Análisis de Resultados
El análisis detallado de la matriz de confusión revela dos comportamientos diferenciados:

1.  **Casos de Alta Precisión:** Minerales con firmas espectrales únicas y bien representados en la base de datos, como la **Galena, Pirita, Albita y Magnetita**, obtuvieron una tasa de acierto del 100%. Esto confirma que el algoritmo de similitud de coseno es altamente efectivo para minerales puros con composición química distintiva.

2.  **Casos de Alerta:** Se identificaron confusiones recurrentes en muestras complejas. Específicamente, las muestras de **Malaquita** fueron frecuentemente confundidas con Labradorita o Magnetita. Este error se atribuye a dos factores: la presencia de mezclas minerales en la muestra física (impurezas) y la similitud morfológica de los espectros en la región de baja energía.

En conclusión, el sistema demuestra ser una herramienta de apoyo eficaz para la pre-clasificación rápida de minerales comunes, aunque requiere supervisión experta para la interpretación de muestras con mezclas complejas o minerales poco frecuentes.
