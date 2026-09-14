# Diccionario de datos

Este proyecto trabaja con cinco grupos principales de datos.

## WIGGA

Medidas ambientales tomadas por sensores WIGGA en los bloques B27, B34, B35 y B38.

Variables esperadas:

- Temperatura
- Humedad relativa
- Humedad maxima y minima
- DPV
- Radiacion PAR
- Punto de rocio
- Gramos de agua
- EVT
- Voltaje de bateria

Uso analitico:

- Comparar variables ambientales entre bloques.
- Revisar evolucion por fecha y hora.
- Relacionar temperatura, humedad, DPV y radiacion.

## Cortinas

Registros de apertura y cierre de cortinas con motores para los cuatro bloques.

Incluye:

- Hora de apertura
- Porcentaje de apertura
- Duracion de apertura
- Hora de cierre
- Porcentaje de cierre
- Duracion de cierre
- Observaciones en frentes y puertas
- Lado A y lado B

Uso analitico:

- Evaluar comportamiento operativo de cortinas.
- Revisar aperturas por bloque, fecha, lado y elemento.
- Cruzar apertura/cierre contra variables ambientales.

## Analisis Apertura

Tablas de referencia para analizar las aperturas de los bloques con porcentajes,
medidas fisicas y datos calculados.

Se separa en dos archivos limpios:

- `analisis_apertura_limpio.csv`: medidas base y aperturas en metros.
- `analisis_apertura_areas_limpio.csv`: areas calculadas en m2, brechas y porcentajes.

Uso analitico:

- Comparar aperturas teoricas, reales y maximas permitidas.
- Contextualizar los movimientos registrados en cortinas.
- Evaluar aprovechamiento real de ventilacion frente a la capacidad maxima y teorica.

## EcoWitt

Variables ambientales externas o generales tomadas por EcoWitt.

Incluye:

- Temperatura
- Rafaga de viento
- Presion
- Velocidad del viento
- Lluvia
- Humedad
- Direccion del viento

Uso analitico:

- Comparar condiciones externas contra condiciones internas de los bloques.

## Apogee

Variables de radiacion/luz tomadas por Apogee.

Incluye:

- PPFD
- Lux

Uso analitico:

- Comparar luz/radiacion con WIGGA y con el comportamiento de cortinas.

## Criterios de limpieza

La limpieza es conservadora:

- El Excel original permanece intacto en `Datos/Raw/`.
- Los ceros validos se conservan, por ejemplo radiacion `0`, lluvia `0` o apertura `0`.
- Solo se eliminan duplicados exactos.
- Las filas con fechas vacias o invalidas se eliminan solo cuando no se pueden usar para analisis temporal.
- Los duplicados por llave de negocio se reportan, pero no se eliminan automaticamente porque pueden representar eventos validos.
- Los nulos se reportan para decidir mas adelante si se imputan, se filtran o se dejan como ausencia real de medicion.
