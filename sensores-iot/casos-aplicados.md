# Casos de instrumentación y datos

Resúmenes elaborados a partir de la guía de reservorios y del informe técnico ACREL recuperados. Describen el trabajo documentado, sin distribuir archivos operativos, identificadores de dispositivos, credenciales o enlaces de infraestructura.

## Nivel de reservorios

El sistema integra un sensor ultrasónico con SenseCAP S2100, transmisión LoRaWAN y recepción en ChirpStack. La lectura de distancia/nivel se transforma en una variable utilizable para seguimiento del reservorio. Para calcular volumen se necesita la referencia de montaje y una relación batimétrica propia de cada reservorio; esa calibración no se incluye como dato genérico.

El [codec S2100](sensecap-s2100/README.md) evidencia validación de tramas, conversiones de unidades y diagnóstico de mensajes anómalos. La guía original incluye el proceso de integración y visualización, pero no se recuperó un paquete completo de la aplicación de reservorios para publicarlo aquí.

## Monitoreo energético ACREL

El informe documenta la integración de un medidor ADF400L con un módulo AWT100 mediante RS-485/Modbus y transmisión LoRaWAN. La finalidad es disponer de registros de energía activa/reactiva, tensión, corriente y potencia para seguimiento posterior.

El estado descrito en el informe comprende arquitectura, configuración e integración de comunicación. La recepción continua, el histórico y el dashboard energético figuran como pasos siguientes. Este portafolio no los presenta como entregables ya terminados.

## Conexión con análisis de datos

Los dos casos muestran el recorrido desde una señal de campo hasta una medida estructurada: validar el mensaje, identificar unidades, controlar faltantes y preparar el almacenamiento temporal. Son la base de las aplicaciones de [análisis](../analisis-de-datos/README.md) y [predicción](../machine-learning/README.md).

[Volver a sensores](README.md)
