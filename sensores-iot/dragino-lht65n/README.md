# Dragino LHT65N

[Codec recuperado](codec.js) con entradas `decodeUplink(input)` y `Decode(fPort, bytes, variables)`. La segunda interfaz resuelve la incompatibilidad con entornos que invocan `Decode`.

Contempla mensajes de estado, mediciones normales y registros almacenados según el puerto y los indicadores del payload. Antes de usarlo con un equipo, comprobar modelo, sonda, firmware y formato real del mensaje. Se mantienen las conversiones del código recuperado; no se afirma certificación del fabricante.

[Pruebas de entradas sintéticas](../pruebas-codecs.cjs) · [Volver a sensores](../README.md)
