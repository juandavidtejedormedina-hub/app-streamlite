# Dashboard de invernaderos

Aplicación en Streamlit para explorar variables ambientales y registros de apertura de cortinas. El proyecto trabaja con temperatura, humedad relativa, radiación PAR y contenido de agua, además de eventos de apertura y cierre.

La versión pública usa datos sintéticos para conservar la estructura del proyecto sin incluir información operativa de las fincas.

## Funciones principales

- Filtros por bloque y rango de fechas.
- Gráficos temporales interactivos.
- Comparación de variables ambientales.
- Revisión de apertura y cierre de cortinas.
- Correlaciones y comportamiento diario.
- Lectura y validación de archivos Excel.

## Ejecutar

```bash
pip install -r requirements.txt
python generar_datos_demo.py
streamlit run dashboard.py
```

Para la vista enfocada en cortinas:

```bash
streamlit run dashboard_cortinas.py
```

`generar_datos_demo.py` crea dos archivos de ejemplo dentro de `datos/`: uno para variables ambientales y otro para cortinas.

Los datos de demostración no corresponden a mediciones reales. Las correlaciones visibles en la aplicación deben interpretarse únicamente como ejemplos de funcionamiento.

[Volver a análisis de datos](../README.md)
