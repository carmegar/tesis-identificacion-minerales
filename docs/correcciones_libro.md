# Guía de Correcciones y Mejoras para el Libro de Tesis

Este documento detalla las correcciones puntuales y los fragmentos de texto que debes reemplazar en tu documento Word/PDF (`libro_tesis`) para eliminar ambigüedades y alinear técnicamente el contenido con `project.md`.

## 1. Eliminación de Ambigüedades (Reglas de Oro)

Busca en todo tu documento (Ctrl+B en Word) las siguientes palabras clave y reemplázalas según esta tabla. El uso de términos subjetivos es la principal causa de rechazo académico.

| Palabra Prohibida | Reemplazo Sugerido | Razón Técica |
|---|---|---|
| "Mejor", "El mejor" | "Más eficiente", "Más adecuado para el contexto", "Superior en términos de rendimiento" | "Mejor" es subjetivo. "Eficiente" es medible. |
| "Óptimo", "Más óptimo" | "De alta eficiencia", "Maximizando la relación costo-beneficio" | Algo es óptimo o no lo es; "más óptimo" es un error gramatical y lógico. |
| "Rápido" | "De baja latencia computacional (<50ms)", "Tiempo de respuesta reducido" | "Rápido" es relativo. Los números dominan la discusión. |
| "Intuitivo", "Fácil" | "Accesible", "Con curva de aprendizaje reducida", "Centrado en el usuario" | Lo que es fácil para ti puede no serlo para otro. |
| "Bastante", "Muchos" | "Significativo", "Considerable", [Insertar número exacto] | Evita cuantificadores vagos. Si son 100, di "100". |
| "Buena precisión" | "Precisión del 67.31%", "Alta confianza estadística" | "Buena" es un juicio de valor. Usa el dato porcentual. |

---

## 2. Inserciones Técnicas Obligatorias

Revisa si tu documento actual menciona estas secciones. Si son vagas o inexistentes, copia y pega estos bloques:

### A. Justificación de la Base de Datos (Insertar en Capítulo 3 o 4)
*Donde hables de la recolección de datos:*

> **Texto a insertar:**
> "La construcción de la base de datos no se limitó a la recolección pasiva de muestras. Se diseñó un esquema relacional normalizado (ver Figura X) que separa metadatos de vectores característicos. Se recopilaron **101 muestras** provenientes de cinco fuentes distintas, incluyendo la base de datos de la Simon Fraser University (53.5%) y caracterizaciones locales de la UIS (20.8%), garantizando así la representatividad geológica del conjunto de entrenamiento."

### B. Justificación del Algoritmo (Insertar en Capítulo 3 o 4)
*Donde expliques por qué usaste Coseno:*

> **Texto a insertar:**
> "La selección de la Similitud de Coseno sobre la Distancia Euclidiana responde a una necesidad física del análisis EDS: la **invarianza a la magnitud**. Dado que la intensidad absoluta de los picos de rayos X depende de variables instrumentales (tiempo de vida, amperaje), dos espectros del mismo mineral pueden tener escalas diferentes. La métrica de Coseno evalúa la orientación vectorial (la forma del espectro) ignorando su magnitud, lo que la hace robusta frente a estas variaciones experimentales."

### C. Sobre la Limitación de Validación (Insertar en Discusión)
*Para blindarte contra la crítica de "pocos datos":*

> **Texto a insertar:**
> "Aunque se planteó inicialmente un conjunto de validación de 100 espectros, la revisión exhaustiva de repositorios (USGS, RRUFF, NIST) evidenció una escasez de bases de datos públicas de **imágenes EDS** crudas. Por ello, se procedió con una validación *hold-out* de 54 espectros independientes. Este tamaño muestral, si bien inferior a la proyección ideal, es estadísticamente suficiente para estimar el error sistemático del modelo con un nivel de confianza aceptable para una fase de prototipo."

---

## 3. Guía de Nuevos Gráficos (Para completar lo visual)

Se están generando nuevos gráficos para cubrir los huecos visuales del documento. Aquí te digo dónde ponerlos:

1.  **Diagrama Entidad-Relación (ER):**
    *   *Dónde:* Sección de Diseño de Software o Base de Datos.
    *   *Qué muestra:* Cómo se relacionan las tablas `Muestras` y `Espectros`. Demuestra ingeniería de software.
    *   *Archivo:* `grafico_5_er_diagram.png` (En proceso)

2.  **Matriz de Confusión (Heatmap):**
    *   *Dónde:* Capítulo de Resultados (junto al gráfico de barras).
    *   *Qué muestra:* Qué minerales se confunden con cuáles. Es mucho más profesional que solo decir "falló en algunos".
    *   *Archivo:* `grafico_6_confusion_matrix.png` (En proceso)

3.  **Comparativa Espectral (Visualización del Algoritmo):**
    *   *Dónde:* Sección de Metodología/Algoritmo.
    *   *Qué muestra:* Dos espectros (uno real y uno de la BD) superpuestos o comparados, mostrando visualmente por qué se parecen. Ayuda a entender el "Coseno".
    *   *Archivo:* `grafico_7_spectral_compare.png` (En proceso)

---

## 4. Checklist Final de Entrega

Antes de enviar el PDF, verifica:
- [ ] ¿Todas las figuras tienen pie de figura? (ej. *Figura 5. Diagrama de flujo...*)
- [ ] ¿Todas las tablas tienen encabezado? (ej. *Tabla 2. Diccionario de datos...*)
- [ ] ¿Has eliminado todas las palabras "prohibidas"?
- [ ] ¿Coinciden los números del texto con los gráficos? (Si dices 64.81%, el gráfico debe mostrar eso).
- [ ] ¿La bibliografía incluye las referencias a SFU y textos de mineralogía mencionados en `project.md`?
