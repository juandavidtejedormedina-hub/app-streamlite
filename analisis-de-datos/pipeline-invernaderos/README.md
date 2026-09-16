# Pipeline de datos de invernaderos

Scripts en Python para limpiar y preparar datos ambientales antes del análisis.

## Estructura

| Etapa | Archivo | Trabajo realizado |
| --- | --- | --- |
| Limpieza | [limpiar_datos.py](procesamiento/limpiar_datos.py) | Normalización de columnas y fechas, revisión de duplicados y reglas de limpieza |
| Variables derivadas | [generar_variables.py](procesamiento/generar_variables.py) | Variables temporales, rezagos y acumulados |
| Preparación estadística | [preparar_analisis_estadistico.py](procesamiento/preparar_analisis_estadistico.py) | Tablas y archivos listos para análisis |

## Datos

El código espera un archivo en `Datos/Raw/Datos Excel.xlsx`. Los datos originales no se publican en este repositorio.

El esquema de variables puede revisarse en:

- [Diccionario de datos](docs/diccionario_datos.md)
- [Variables derivadas](docs/variables_derivadas.md)

## Ejecutar

```bash
pip install -r requirements.txt
python procesamiento/limpiar_datos.py
python procesamiento/generar_variables.py
python procesamiento/preparar_analisis_estadistico.py
```

Los resultados se guardan en `Datos/Procesados`, `Datos/Analiticos` y `Datos/Reportes`.

Para probar una parte del flujo sin datos reales, el [dashboard de invernaderos](../dashboard-invernaderos/README.md) incluye un generador de datos sintéticos.

[Volver a análisis de datos](../README.md)
