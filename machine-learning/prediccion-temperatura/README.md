# Predicción de temperatura a una hora

Proyecto en Python para estimar la temperatura de un invernadero una hora después de la última medición disponible.

La serie se trabaja con intervalos de 30 minutos. A partir de los datos se crean rezagos temporales y variables cíclicas de hora y día de la semana. El modelo utilizado es Random Forest.

## Flujo

1. Cargar y validar el CSV.
2. Ordenar la serie por fecha.
3. Ajustar los registros a intervalos de 30 minutos.
4. Crear rezagos de temperatura y variables temporales.
5. Entrenar el modelo con los registros disponibles.
6. Generar la predicción una hora adelante.

## Ejecutar

```bash
pip install -r requirements.txt
jupyter notebook notebook.ipynb
```

[Ver notebook](notebook.ipynb) · [Abrir en Colab](https://colab.research.google.com/github/juandavidtejedormedina-hub/app-streamlite/blob/main/machine-learning/prediccion-temperatura/notebook.ipynb)

El archivo [temperatura_sintetica.csv](datos/temperatura_sintetica.csv) permite ejecutar el notebook sin usar datos reales. También puede generarse nuevamente con:

```bash
python generar_datos_demo.py
```

## Formato de entrada

| Columna | Formato |
| --- | --- |
| `DateTime` | Fecha y hora |
| `Temperatura` | Valor numérico en °C |

El ejemplo usa separador `;`.

Esta versión pública permite revisar el flujo completo de preparación, entrenamiento e inferencia. Los resultados con datos sintéticos sirven para probar el código y no representan precisión en condiciones reales de cultivo.

[Volver a Machine Learning](../README.md)
