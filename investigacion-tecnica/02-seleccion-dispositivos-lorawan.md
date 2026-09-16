# Selección de dispositivos LoRaWAN para sensores

## Objetivo

Elegir equipos capaces de adquirir sensores de campo y enviar los datos hacia un servidor LoRaWAN en aplicaciones agrícolas. La comparación consideró más que el precio de compra: integración, consumo, protección y mantenibilidad cambian el costo real del despliegue.

## Matriz de evaluación

| Dimensión | Pregunta de control |
| --- | --- |
| Interfaz | ¿Dispone de RS-485/Modbus, SDI-12 o UART según el sensor? |
| Radio | ¿Soporta la banda y el plan de canales requeridos? |
| Operación | ¿Trabaja como Clase A y permite configurar intervalos y datalogging? |
| Energía | ¿Integra batería, entrada solar y estrategia de bajo consumo? |
| Protección | ¿La envolvente y los conectores son adecuados para exteriores? |
| Integración | ¿Existe codec, documentación de payload y comandos remotos? |
| Soporte | ¿Hay manual, firmware, disponibilidad y soporte verificable? |

## Equipos estudiados

Se revisaron alternativas de Dragino, Milesight, Seeed Studio/SenseCAP, Appcon, Taiga y otros fabricantes. Las pruebas aplicadas incluyeron el **Dragino WSC2-L**, el **SenseCAP S2100** y el **Dragino LHT65N**. Los codecs públicos y sus vectores sintéticos están en [Sensores e IoT](../sensores-iot/README.md).

## Resultado de ingeniería

El WSC2-L quedó como referencia operativa para adquisición multivariable; el S2100 se empleó en el caso de nivel de reservorios; y el LHT65N se evaluó para temperatura, humedad y almacenamiento temporal de mensajes. Algunas opciones se descartaron porque no exponían la interfaz UART requerida o porque su integración no cubría el caso de uso completo.

## Límite público

No se publican cotizaciones, números de serie, claves, identificadores LoRaWAN ni ubicaciones. La selección final depende del sensor, el consumo, el montaje y la disponibilidad comercial del momento.

[Volver a investigación técnica](README.md)
