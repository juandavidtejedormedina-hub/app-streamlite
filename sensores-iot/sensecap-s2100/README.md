# SenseCAP S2100 — Reservorios

[Código JavaScript](codec.js) para el formato de dos mediciones utilizado en el proyecto recuperado. Espera `fPort: 3`, once bytes, cabecera `0x31`, canales `0x12` y dos enteros de 32 bits en orden big-endian.

El codec convierte la primera medida a metros, centímetros y milímetros, y la segunda a temperatura. Rechaza puerto, longitud, tipo de trama o canales inesperados y reconoce el valor reservado `0x80000000`. La cabecera diagnóstica `0x12` se identifica sin inventar mediciones.

Estas reglas corresponden a esa configuración del proyecto; no son un decodificador universal de todos los modos del S2100. No se incluye el Excel de validación de campo mencionado en los comentarios originales.

## Ejemplo sintético

```javascript
decodeUplink({
  fPort: 3,
  bytes: [0x31, 0x12, 0x00, 0x00, 0x12, 0xD4, 0x50, 0x00, 0x00, 0x61, 0xA8]
});
```

Valores esperados: **1,234 m** y **25 °C**. [Pruebas](../pruebas-codecs.cjs).

[Volver a sensores](../README.md)
