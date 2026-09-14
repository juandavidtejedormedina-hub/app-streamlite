# Variables derivadas

Las variables derivadas se generan despues de la limpieza, desde los CSV de
`Datos/Procesados/`, y se guardan en `Datos/Analiticos/`.

La regla del proyecto es crear columnas solo si ayudan a una pregunta
analitica posterior. Por eso se evitan variables redundantes o etiquetas con
umbrales no definidos por negocio.

## WIGGA

Se generan variables para analizar ciclos, dinamica reciente y condiciones de
riesgo:

- Variables temporales: anio, mes, dia, semana, hora decimal y periodo del dia.
- Variables ciclicas: seno/coseno de hora y dia del anio.
- `es_dia`: identifica presencia de radiacion sin borrar radiacion `0`.
- `intervalo_minutos`: detecta huecos entre mediciones por bloque.
- `diferencia_temp_punto_rocio_c` y `riesgo_condensacion`.
- Amplitudes de temperatura y humedad.
- Cambios frente a la medicion anterior.
- Rezagos exactos de 1h, 6h y 24h por bloque.
- Diferencias contra 1h y 24h.
- Promedios moviles de 3h, 6h y 24h.
- Acumulados de radiacion y maximos/minimos diarios hasta el momento.

No se crean variables objetivo futuras todavia, porque pertenecen a una etapa
de prediccion/modelado y no a la base estadistica inicial.

## Cortinas

Se generan variables para analizar horarios y operacion:

- Hora de apertura/cierre en minuto del dia.
- Hora de apertura/cierre en formato decimal.
- Duracion abierta en minutos.
- Indicador de observacion.
- Tipo de elemento: frente, puerta u otro.

## EcoWitt

Se generan variables para clima externo:

- Variables temporales y ciclicas.
- Intervalo entre mediciones.
- Componentes `u` y `v` del viento.
- Sector de viento.
- Cambio de temperatura.
- Promedios moviles de temperatura y humedad en 1h.

## Apogee

Se generan variables para luz/radiacion:

- Variables temporales y ciclicas.
- Intervalo entre mediciones.
- Indicador de presencia de luz.
- Promedio movil de PPFD y lux en 1h.

## Analisis Apertura

Se generan variables para comparar capacidad y apertura real:

- Codigo de bloque en formato `B27`, `B34`, `B35`, `B38`.
- Brecha entre apertura maxima permitida y apertura real.
- Uso de apertura maxima permitida.
- Relacion entre apertura real y apertura teorica.

La hoja original se separa en dos tablas limpias:

- `analisis_apertura_limpio.csv`: medidas de apertura en metros.
- `analisis_apertura_areas_limpio.csv`: areas calculadas en m2.

En la tabla de areas se agregan indicadores porcentuales legibles:

- `uso_area_maxima_pct`
- `uso_area_teorica_pct`
- `brecha_ventilacion_pct_maxima`
- `perdida_operativa_pct`
