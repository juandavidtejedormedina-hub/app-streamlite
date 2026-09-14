# Dragino WSC2-L

[Codec recuperado](codec.js) compatible con la interfaz de ChirpStack v4. Incluye mensajes de estado en puerto 5, mediciones en puerto 2 y manejo de payloads vacíos o incompletos.

El desarrollo incorpora decodificación de segmentos de sensores ambientales, viento y PAR, además de filtros para valores reservados. El mapeo se conserva como parte del código del proyecto y debe contrastarse con el firmware y sensores conectados al equipo que vaya a utilizarlo.

[Pruebas de entradas sintéticas](../pruebas-codecs.cjs) · [Volver a sensores](../README.md)
