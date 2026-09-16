# Autonomía solar para nodos IoT

## Pregunta de diseño

¿Cómo sostener sensores, almacenamiento y transmisión LoRaWAN en ubicaciones sin alimentación confiable? El dimensionamiento debe partir de energía diaria, no únicamente de la potencia máxima del panel.

## Método

1. Medir o estimar la corriente de cada estado: adquisición, procesamiento, transmisión, espera y almacenamiento.
2. Multiplicar consumo por tiempo de permanencia para obtener Wh/día.
3. Incorporar pérdidas de conversión, autodescarga, temperatura y envejecimiento.
4. Dimensionar batería para los días de autonomía requeridos y limitar la profundidad de descarga.
5. Dimensionar panel con horas solares pico conservadoras y margen por suciedad, orientación y nubosidad.
6. Verificar controlador de carga, tensiones, protecciones y conectores.

## Aplicación

La propuesta contempla panel solar, batería recargable y gestión de carga. La selección nominal no reemplaza el balance energético: el intervalo de muestreo, el tiempo de radio, la eficiencia del convertidor y la radiación del sitio determinan la autonomía real.

## Criterios de aceptación

- Recuperación de carga después del peor día razonable.
- Operación dentro del rango de tensión de todos los módulos.
- Margen para degradación y ampliaciones.
- Protección frente a inversión, sobrecorriente, humedad y cableado expuesto.
- Registro de tensión de batería para mantenimiento preventivo.

[Volver a investigación técnica](README.md)
