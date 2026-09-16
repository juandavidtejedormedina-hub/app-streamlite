# Sensores e IoT

Proyectos relacionados con adquisición de datos, LoRaWAN y decodificación de payloads.

| Proyecto | Contenido |
| --- | --- |
| [SenseCAP S2100](sensecap-s2100/README.md) | Decodificación de nivel/distancia y temperatura |
| [Dragino LHT65N](dragino-lht65n/README.md) | Codec compatible con distintas interfaces de decodificación |
| [Dragino WSC2-L](dragino-wsc2-l/README.md) | Decodificación de variables ambientales y mensajes de estado |
| [Casos aplicados](casos-aplicados.md) | Reservorios y monitoreo energético |

Las pruebas de codecs pueden ejecutarse con:

```bash
node pruebas-codecs.cjs
```

Los vectores usados en las pruebas son sintéticos y sirven para comprobar el comportamiento del código. La validación final siempre debe hacerse con el dispositivo, firmware y sensores reales.

[Volver al portafolio](../README.md)
