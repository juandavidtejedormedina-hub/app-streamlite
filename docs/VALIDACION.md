# Validación del portafolio

Las verificaciones usan datos sintéticos. El script de comprobación se ejecuta desde la raíz:

```bash
pip install -r requirements-validacion.txt
MPLBACKEND=Agg python verificar_portafolio.py
```

El mismo comando se ejecuta automáticamente en cada `push` y `pull request` mediante [GitHub Actions](../.github/workflows/portfolio-checks.yml).

Se requiere Node.js para las pruebas de codecs. `MPLBACKEND=Agg` selecciona el backend sin ventana de Matplotlib; en Windows puede definirse como variable de entorno antes de ejecutar Python.

## Resultado de la revisión

Septiembre de 2026, Python 3.12: **seis pruebas funcionales correctas**, incluyendo **22 comprobaciones de codecs**. Los dos dashboards cargaron sin excepciones; también se comprobaron las vistas WIGA, Cortinas, Promedio y Varianza de la aplicación principal. Los nuevos documentos y su navegación pasaron la comprobación automática de enlaces. Las dependencias utilizadas están fijadas en `requirements-validacion.txt`.

## Comprobaciones

- Sintaxis del código Python y esquema de los siete notebooks.
- Existencia de los destinos locales enlazados en Markdown.
- Entrenamiento e inferencia de temperatura con el CSV sintético, horizonte de una hora y rechazo de predicción al faltar un rezago.
- Formulario Flask: apertura, predicción de ejemplo y rechazo de entradas no numéricas, infinitas o negativas.
- Conversiones, campos de estado y rechazo de entradas anómalas en los tres codecs JavaScript.
- Carga de los dos dashboards y cambio de vistas de la aplicación principal mediante `AppTest` de Streamlit con Excel sintéticos.

## Límites

No se repitieron entrenamientos de TensorFlow/Keras, inferencia con Ollama ni ensayos con sensores físicos. El pipeline completo depende del libro Excel original, que no se publica; se revisó su sintaxis. El informe Bank Marketing se publica como evidencia documental, sin recalcular sus resultados. Las pruebas iniciales de los dashboards no equivalen a comprobar todas las combinaciones de filtros.
