# Resumen de Datos Cuantitativos para Capítulo 6

## 1. Base de Datos
- **Total Muestras:** 101
- **Distribución:**
  - Silicatos: 45
  - Sulfuros: 18
  - Óxidos: 12
  - Carbonatos: 8
  - Sulfatos: 6
  - Fosfatos: 5
  - Otros: 6
- **Fuentes:** SFU (54), UIS-Guatiguara (21), Tesis Original (18), Otras (8).

## 2. Validación
- **Total Espectros Prueba:** 54
- **Aciertos:** 35
- **Fallos:** 19
- **Accuracy General:** 64.81%
- **Accuracy Ajustado:** 67.31% (Excluyendo minerales no entrenados)
- **Confianza Promedio:** 96.18%

## 3. Desempeño Técnico
- **Tiempo de comparación:** < 50ms (estimado en project.md)
- **Dimensionalidad:** 200 floats
- **Umbral de confianza:** 80% (Muy probable), 60-80% (Posible).

## 4. Casos Específicos
- **100% Acierto:** Galena, Pirita, Albita, Barita, Magnetita (6 casos).
- **Fallos Conocidos:** 
  - Malaquita -> Labradorita/Magnetita (Mezclas/Complejidad)
  - Amatista -> Calcita (No en BD)
