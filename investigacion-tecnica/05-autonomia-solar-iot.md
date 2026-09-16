# Autonomía solar para nodos IoT

Para alimentar nodos de sensores en campo no basta con escoger un panel por potencia nominal. El dimensionamiento depende del consumo diario del sistema y de las condiciones reales de operación.

## Cálculo básico

1. Estimar la corriente de cada estado: medición, procesamiento, transmisión y espera.
2. Calcular el consumo diario en Wh.
3. Incluir pérdidas de conversión y margen por temperatura y envejecimiento.
4. Dimensionar la batería según la autonomía requerida.
5. Dimensionar el panel con horas solares pico conservadoras.
6. Verificar controlador de carga, tensiones, protecciones y conectores.

En el proyecto se consideraron panel solar, batería recargable y gestión de carga para nodos LoRaWAN.

También se revisaron aspectos prácticos como orientación del panel, suciedad, nubosidad, profundidad de descarga y seguimiento de la tensión de batería.

[Volver a investigación técnica](README.md)
