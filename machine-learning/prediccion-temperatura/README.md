# Predicción de temperatura a una hora

Adaptación pública de un notebook desarrollado para anticipar la temperatura de un invernadero. Regulariza una serie cada 30 minutos, construye 12 variables y entrena un Random Forest para estimar la temperatura una hora después de la última medición.

## Flujo

1. Leer y validar el CSV.
2. Ordenar fechas, redondear a 30 minutos y crear una malla temporal sin imputar huecos.
3. Construir temperatura actual y rezagos de 30 minutos a 24 horas, más seno/coseno de hora y día de la semana.
4. Entrenar el modelo con los registros que ya tienen objetivo conocido.
5. Predecir a una hora si están presentes todos los rezagos necesarios.

## Ejecutar

Desde esta carpeta:

```bash
pip install -r requirements.txt
jupyter notebook notebook.ipynb
```

[Ver notebook](notebook.ipynb) · [Abrir en Colab](https://colab.research.google.com/github/juandavidtejedormedina-hub/app-streamlite/blob/main/machine-learning/prediccion-temperatura/notebook.ipynb)

El archivo [temperatura_sintetica.csv](datos/temperatura_sintetica.csv) es artificial y está incluido. En Colab, descargarlo y seleccionarlo cuando el notebook solicite el CSV. Puede regenerarse con `python generar_datos_demo.py`.

## Esquema de entrada

| Columna | Formato |
| --- | --- |
| `DateTime` | Fecha y hora, por ejemplo `2026-03-01 00:00:00` |
| `Temperatura` | Valor numérico en °C; el ejemplo usa coma decimal |

Separador: punto y coma. El filtro que descarta temperaturas menores o iguales a cero es una regla heredada del histórico original; debe revisarse para otro dominio. También debe ajustarse `FECHA_INICIO_ESTABLE` a la serie utilizada.

## Alcance de los resultados

Este notebook realiza entrenamiento e inferencia, sin evaluación temporal separada. La prueba con datos sintéticos comprueba ejecución, horizonte y manejo de datos faltantes; no mide la precisión en un invernadero real. Las métricas de desarrollo mencionadas en el archivo original se retiraron porque no se recuperó el conjunto de evaluación que las sustentaba.

[Volver a Machine Learning](../README.md)
