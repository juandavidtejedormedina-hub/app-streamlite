# Flask + K-Means

Demostración de integración entre un modelo de clustering y una aplicación web. El modelo agrupa seis pares de ingresos/gastos artificiales; el formulario asigna un grupo a un nuevo par numérico.

## Ejecutar

Desde esta carpeta:

```bash
pip install -r requirements.txt
python modelo.py
python app.py
```

Abrir `http://127.0.0.1:5000`. El modelo se genera localmente como `modelo_kmeans.pkl`; no se distribuye un binario serializado.

## Alcance

Es un ejemplo de conexión entre backend y ML. Los seis registros son de demostración: no constituyen una segmentación financiera validada. Los identificadores de cluster son etiquetas arbitrarias. La versión pública valida entradas no numéricas, infinitas y negativas.

[Repositorio original](https://github.com/juandavidtejedormedina-hub/appweb-Flaskrender) · [Volver a desarrollo web](../README.md)
