# Casos aplicados de instrumentación y datos

## Nivel de reservorios

El sistema integra un sensor ultrasónico, un SenseCAP S2100 y una red LoRaWAN con recepción en ChirpStack.

La lectura de distancia se transforma en una variable de nivel. Para calcular volumen se necesita la geometría y la relación batimétrica de cada reservorio, por lo que esa parte depende de la calibración de cada sitio.

El [codec del S2100](sensecap-s2100/README.md) incluye validación de trama, conversión de unidades y manejo de mensajes inesperados.

## Monitoreo energético

Otro caso trabajado corresponde a la integración de un medidor ACREL con comunicación RS-485/Modbus y transmisión mediante LoRaWAN.

Las variables consideradas incluyen energía activa y reactiva, tensión, corriente y potencia.

La arquitectura de comunicación y configuración quedó documentada. El histórico continuo y el dashboard energético pertenecen a etapas posteriores del proyecto y no se presentan aquí como desarrollos terminados.

En ambos casos, el trabajo parte de la señal de campo y termina en datos estructurados que luego pueden almacenarse, visualizarse o analizarse.

No se publican credenciales, identificadores de dispositivos ni información de infraestructura.

[Volver a sensores](README.md)
