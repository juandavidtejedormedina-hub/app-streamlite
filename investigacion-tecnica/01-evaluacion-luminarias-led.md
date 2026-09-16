# Evaluación técnica de luminarias LED

## Problema

Comparar luminarias LED con un criterio uniforme y emitir un resultado **APROBADO**, **NO APROBADO** o **INFORMACIÓN INSUFICIENTE**. El análisis evita decisiones basadas solo en la potencia nominal de la etiqueta.

## Criterios utilizados

- Potencia activa medida frente a potencia nominal.
- Factor de potencia y distorsión armónica total (THD).
- Flujo luminoso y eficacia, cuando existía ensayo fotométrico o evidencia equivalente.
- Estado de componentes, construcción e identificación del producto.
- Rango de tensión y consistencia entre ficha, etiqueta y medición.

## Lógica de decisión

Una luminaria podía entregar luz y aun así no aprobar: un factor de potencia bajo, una THD elevada, una diferencia material entre potencia declarada y medida o una falla constructiva son señales independientes. La categoría **INFORMACIÓN INSUFICIENTE** evita convertir la ausencia de una medición en aprobación automática.

El protocolo permite identificar productos con calidad de potencia deficiente, discrepancias entre la información declarada y la medición, o fallas visibles de construcción. Cada hallazgo se registra por separado para que el dictamen pueda auditarse sin depender de una impresión general del producto.

## Valor para análisis de datos

El trabajo muestra definición de reglas, control de calidad, manejo explícito de datos faltantes y trazabilidad de una decisión categórica. Es un ejemplo de cómo convertir mediciones eléctricas heterogéneas en una tabla de evaluación defendible.

## Publicación

Las fotografías, marcas evaluadas y archivos de medición no se distribuyen en este repositorio. Este resumen conserva únicamente el método técnico general.

[Volver a investigación técnica](README.md)
