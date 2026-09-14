# Pipeline de preparación de datos de invernaderos

Código recuperado de [Pagina-Web](https://github.com/juandavidtejedormedina-hub/Pagina-Web). Organiza la preparación de datos ambientales y de operación antes del análisis estadístico.

| Etapa | Archivo | Función |
| --- | --- | --- |
| Limpieza | [limpiar_datos.py](procesamiento/limpiar_datos.py) | Normalización de columnas, fechas, duplicados y registro de reglas aplicadas |
| Variables derivadas | [generar_variables.py](procesamiento/generar_variables.py) | Variables temporales/cíclicas, rezagos y acumulados |
| Base estadística | [preparar_analisis_estadistico.py](procesamiento/preparar_analisis_estadistico.py) | Preparación de tablas y reportes para análisis |

## Datos requeridos

Los registros de operación no se incluyen. El código espera un libro local en `Datos/Raw/Datos Excel.xlsx`, con las hojas y columnas utilizadas en el desarrollo original. Consultar el [diccionario](docs/diccionario_datos.md), la [descripción de variables derivadas](docs/variables_derivadas.md) y las constantes de `limpiar_datos.py` para preparar el esquema.

Estos archivos constituyen código recuperado para revisión. Para una demostración ejecutable sin disponer del libro original, usar el [dashboard con generador sintético](../dashboard-invernaderos/README.md).

## Ejecución con un libro compatible

Desde esta carpeta:

```bash
pip install -r requirements.txt
python procesamiento/limpiar_datos.py
python procesamiento/generar_variables.py
python procesamiento/preparar_analisis_estadistico.py
```

Los resultados se escriben en las carpetas `Datos/Procesados`, `Datos/Analiticos` y `Datos/Reportes`. Se conserva la limpieza conservadora: los ceros válidos no se eliminan por ser cero y los duplicados por llave se reportan antes de decidir su tratamiento.

[Volver a análisis de datos](../README.md)
