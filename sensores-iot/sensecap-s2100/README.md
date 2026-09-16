# SenseCAP S2100 — Reservorios

Codec JavaScript utilizado para interpretar el formato de datos del SenseCAP S2100 en el proyecto de nivel de reservorios.

La trama esperada usa `fPort: 3` e incluye dos mediciones. El codec convierte la primera a distancia/nivel y la segunda a temperatura.

También valida longitud, cabecera, canales y valores reservados antes de devolver los datos.

## Ejemplo

```javascript
decodeUplink({
  fPort: 3,
  bytes: [0x31, 0x12, 0x00, 0x00, 0x12, 0xD4, 0x50, 0x00, 0x00, 0x61, 0xA8]
});
```

Resultado esperado para este ejemplo: **1,234 m** y **25 °C**.

Las reglas corresponden a la configuración usada en este proyecto y no a todos los modos posibles del S2100.

[Ver codec](codec.js) · [Pruebas](../pruebas-codecs.cjs) · [Volver a sensores](../README.md)
