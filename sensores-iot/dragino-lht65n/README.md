# Dragino LHT65N

Codec JavaScript para decodificar mensajes del Dragino LHT65N.

Incluye compatibilidad con las interfaces `decodeUplink(input)` y `Decode(fPort, bytes, variables)`, lo que permite usarlo en entornos que esperan cualquiera de las dos funciones.

El código contempla mensajes de estado, mediciones normales y registros almacenados según el puerto y el contenido del payload.

Antes de usarlo con otro equipo conviene verificar modelo, sonda, firmware y formato de mensaje, ya que pueden existir diferencias entre versiones.

[Ver codec](codec.js) · [Pruebas](../pruebas-codecs.cjs) · [Volver a sensores](../README.md)
