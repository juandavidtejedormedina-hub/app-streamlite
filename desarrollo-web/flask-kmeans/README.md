# Flask + K-Means

Aplicación web sencilla que conecta un formulario en Flask con un modelo K-Means.

El modelo se entrena con seis pares de valores de ingresos y gastos generados para el ejemplo. Cuando el usuario ingresa nuevos valores, la aplicación devuelve el cluster asignado.

## Ejecutar

```bash
pip install -r requirements.txt
python modelo.py
python app.py
```

Luego abrir:

`http://127.0.0.1:5000`

`modelo.py` genera localmente el archivo `modelo_kmeans.pkl`.

Este proyecto sirve como ejemplo de integración entre un modelo de Machine Learning y una aplicación web. Los datos son artificiales y los números de cluster no tienen significado financiero por sí mismos.

[Repositorio original](https://github.com/juandavidtejedormedina-hub/appweb-Flaskrender) · [Volver a desarrollo web](../README.md)
