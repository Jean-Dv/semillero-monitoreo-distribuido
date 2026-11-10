# Alternativas de arquitectura para el ETL de telemetría

## Estado de la decisión

Este directorio documenta dos arquitecturas candidatas para construir el flujo
de datos en tiempo casi real del prototipo. Ninguna ha sido seleccionada como
arquitectura definitiva. La decisión se tomará después de observar la
telemetría real de un sistema controlado y comparar las alternativas mediante
criterios reproducibles.

Las opciones son:

1. [Arquitectura local con Kafka, Flink y ClickHouse](01_local_kafka_flink_clickhouse.md).
2. [Arquitectura administrada con AWS Glue](02_aws_glue.md).

## Artefacto técnico documentado

La [documentación académica del prototipo local
implementado](03_prototipo_local_implementado.md) describe el trabajo realizado
en el repositorio hermano `AIOpsLab`, los contratos Bronze, Silver, Gold y
Results, las garantías de entrega, el protocolo experimental y el estado de su
verificación. Este prototipo aporta evidencia de factibilidad para la actividad
de diseño y desarrollo de DSRM; no constituye por sí mismo la selección
definitiva de la arquitectura local frente a la alternativa administrada.

La [mejora del Gold y protocolo de
ejecuciones](04_mejora_gold_y_protocolo_runs.md) especifica e informa la
iteración vigente: un Gold canónico por servicio y ventana, conjuntos derivados
para algoritmos tabulares y temporales, criterios de calidad, tres runs nominales
y reglas para una comparación sin fuga temporal. Los contratos v2.2 y el
protocolo automatizado ya están implementados; las tres runs nominales correctas
y la aceptación del Gold permanecen pendientes. Los paquetes generados durante
el desarrollo se conservan localmente y no son evidencia experimental. La
iteración no selecciona un algoritmo ni crea un Gold independiente para cada
candidato.

La guía ejecutable para subir, redesplegar, validar, correr escenarios y
conservar cada paquete de evidencia se mantiene junto al código en
`../AIOpsLab/deploy/etl/GUIA_EJECUCION.md` (ruta relativa entre los dos
repositorios hermanos).

Los dos primeros documentos son notas técnicas de diseño, el tercero registra
el artefacto base y el cuarto especifica y registra su iteración vigente. Ninguno
modifica por sí solo la formulación académica, la numeración IEEE ni el corpus de
`docs/propuesta_investigacion.md`.

## Contexto común

El sistema controlado inicial es Astronomy Shop desplegado mediante AIOpsLab.
La instrumentación produce métricas, registros y trazas mediante
OpenTelemetry. El entorno existente conserva Prometheus, OpenSearch y Jaeger
como backends de observación y Grafana como capa de presentación.

El flujo nuevo no debe atribuir a Grafana la adquisición, la persistencia, la
fusión semántica o la ejecución del método de aprendizaje automático. Grafana
consultará los resultados y mantendrá vínculos hacia la telemetría original.

## Arquitectura lógica invariante

La implementación podrá cambiar, pero ambas opciones deben satisfacer el mismo
flujo lógico:

```text
Sistema controlado
      |
      | métricas, registros y trazas (OTLP)
      v
Adquisición y enrutamiento
      |
      v
Transporte reproducible y desacoplado
      |
      v
Normalización por modalidad
      |
      v
Sincronización y fusión temporal
      |
      v
Representación multimodal conjunta
      |
      +----------> método de aprendizaje automático
      |                         |
      |                         v
      +----------------> resultados interpretables
                                |
                                v
                              Grafana
```

## Capas de datos compartidas

Las dos alternativas emplearán las mismas capas conceptuales:

- **Bronze:** mensajes OTLP originales, inmutables y asociados con una
  ejecución experimental.
- **Silver:** tablas normalizadas de métricas, registros y spans, conservando
  identificadores, atributos y procedencia.
- **Gold:** observaciones multimodales por componente y ventana temporal,
  preparadas para análisis y aprendizaje automático.
- **Results:** patrones, puntuaciones, explicaciones, incertidumbre y vínculos
  hacia las observaciones que sustentan cada resultado.

La separación permite cambiar el motor de procesamiento sin alterar el
contrato lógico consumido por el método o por Grafana.

## Unidad conjunta inicial

La hipótesis de diseño inicial es una observación asociada con un servicio o
componente durante una ventana de tiempo:

```text
run_id
scenario_id
window_start
window_end
service_name
namespace
workload
pod
metric_features
log_features
trace_features
quality_flags
source_references
```

Esta estructura no es todavía el esquema definitivo. La observación inicial
de los datos determinará el tamaño y avance de las ventanas, los atributos
disponibles, el tratamiento de valores faltantes y la granularidad más
apropiada.

## Comparación preliminar

| Criterio | Kafka + Flink + ClickHouse local | AWS Glue |
|---|---|---|
| Lugar de ejecución | Docker y Kubernetes locales | Servicio administrado en AWS |
| Motor | Apache Flink | Spark Structured Streaming |
| Modelo principal | Flujo continuo con tiempo de evento | Microbatches para operaciones con estado |
| Transporte | Kafka dedicado | Kinesis, MSK o Kafka |
| Persistencia reproducible | MinIO y Parquet | S3 y Parquet o Iceberg |
| Consulta inmediata | ClickHouse | Athena, ClickHouse o un destino JDBC |
| Validación completamente local | Sí | No; solo el desarrollo puede aproximarse con Docker |
| Dependencia del proveedor | Baja | Alta |
| Administración de infraestructura | Mayor | Menor |
| Costos externos durante la prueba | No obligatorios | Glue, transporte, almacenamiento y consultas |
| Ajuste inicial al alcance local | Alto | Parcial o híbrido |

## Observación que precede a la selección

Antes de elegir una arquitectura se ejecutará un protocolo de perfilado con
una carga estable y tres periodos: funcionamiento normal, una condición
introducida conocida y recuperación. La primera condición candidata es
`adFailure` en Astronomy Shop. El protocolo se repetirá y registrará al menos:

- eventos, puntos y bytes por segundo para cada modalidad;
- esquemas, atributos, tipos y variaciones observadas;
- cardinalidad de etiquetas y atributos;
- retraso entre tiempo de evento y tiempo de recepción;
- eventos duplicados, tardíos o fuera de orden;
- proporción de registros enlazables con trazas;
- consistencia de `service.name` y de los metadatos de Kubernetes;
- ausencia parcial de señales;
- consumo de CPU, memoria y almacenamiento del flujo;
- latencia desde la emisión hasta la disponibilidad del registro Gold.

La salida será un perfil versionado por `run_id`, no una inspección manual
aislada.

## Criterios para tomar la decisión

Cada alternativa se probará con el mismo conjunto de eventos y los mismos
contratos Bronze, Silver y Gold. La selección considerará:

1. cobertura de las tres modalidades sin pérdida no explicada;
2. exactitud temporal y capacidad de tratar datos tardíos;
3. reproducibilidad mediante repetición o reproducción de una ejecución;
4. latencia de extremo a extremo;
5. comportamiento ante reinicio del procesador;
6. trazabilidad desde Gold hasta los eventos originales;
7. recursos, costos y esfuerzo operativo;
8. facilidad para integrar el método y Grafana;
9. compatibilidad con la validación local definida en la investigación;
10. portabilidad de los contratos y transformaciones.

La decisión deberá registrar mediciones y limitaciones. No se seleccionará una
alternativa únicamente por familiaridad, popularidad o preferencia previa.
