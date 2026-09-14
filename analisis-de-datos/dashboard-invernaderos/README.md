# Análisis de variables ambientales y cortinas

Aplicaciones Streamlit recuperadas del trabajo de seguimiento de invernaderos. Permiten explorar temperatura, humedad relativa, radiación PAR y contenido de agua, junto con registros de apertura y cierre de cortinas.

Esta edición utiliza nombres genéricos y fuentes locales. Incluye código del desarrollo original y un generador nuevo de datos sintéticos para demostrarlo sin publicar registros de las fincas.

## Ejecutar

Desde esta carpeta:

```bash
pip install -r requirements.txt
python generar_datos_demo.py
streamlit run dashboard.py
```

La variante centrada en cortinas por día se abre con:

```bash
streamlit run dashboard_cortinas.py
```

## Funciones

- Filtros por bloque y periodo, con gráficos temporales interactivos.
- Comparación de variables ambientales y registros de apertura/cierre.
- Exploración de correlaciones y comportamiento diario.
- Lectura, normalización y validación de fechas y columnas desde Excel.

Los cuatro bloques de demostración utilizan series inventadas. Una correlación visible en la demo no representa una relación causal ni un hallazgo de operación real.

## Datos y adaptación

`generar_datos_demo.py` crea `datos/variables_sinteticas.xlsx` y `datos/cortinas_sinteticas.xlsx`. Cada archivo usa una hoja por bloque. El generador muestra los nombres de columnas y sirve como ejemplo del esquema esperado.

Para usar otros datos, preparar archivos con ese esquema y ajustar las rutas locales del código. Las comparaciones con estaciones externas son funciones del desarrollo original; no están alimentadas en esta demo de una sola finca. Los videos, mapas, logos y descargas automáticas corporativas se retiraron.

El documento histórico titulado “Power BI” describe esta aplicación en Streamlit. Aquí se presenta con la tecnología que utiliza realmente. [Estado del material Power BI](../../power-bi/README.md).

[Volver a análisis de datos](../README.md)
