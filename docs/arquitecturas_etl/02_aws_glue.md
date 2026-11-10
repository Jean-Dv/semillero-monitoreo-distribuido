# Arquitectura candidata 2: ETL administrado con AWS Glue

## Propósito

Esta alternativa traslada el procesamiento del flujo a servicios
administrados de AWS. Busca reducir la administración del motor de ETL,
aprovechar almacenamiento durable en S3 y evaluar una ruta de despliegue en la
nube sin cambiar el contrato multimodal consumido por el método.

La arquitectura es candidata. Su adopción no debe contradecir la validación
del sistema controlado local ni introducir una dependencia que impida
reproducir los experimentos.

## Vista general

```text
Astronomy Shop local
      |
      | OTLP
      v
OpenTelemetry Collector
      |\
      | +------> Prometheus / OpenSearch / Jaeger
      |                          |
      |                          +------> Grafana: señales originales
      |
      +--------> Kinesis Data Streams o Amazon MSK
                               |
                               v
                      AWS Glue Streaming
                      Spark Structured Streaming
                               |
                  +------------+-------------+
                  |                          |
                  v                          v
          S3 + Parquet/Iceberg       destino de consulta
          Bronze/Silver/Gold         Athena o ClickHouse
                                              |
                                              v
                                      Grafana en Docker
```

El sistema sometido a las condiciones experimentales permanece local. La
telemetría cruza hacia AWS, donde se procesa y persiste. Grafana continúa en
Docker y consulta el destino autorizado; no se instalará localmente como
servicio del sistema anfitrión.

## Fuente de streaming

### Opción Kinesis

Kinesis Data Streams ofrece la integración más directa con Glue. Se propone
un stream por modalidad:

```text
otel-metrics-v1
otel-logs-v1
otel-traces-v1
experiment-control-v1
```

El Collector dispone de un exportador para Kinesis capaz de procesar las tres
señales. Se priorizará OTLP protobuf. La codificación `otlp_json` requiere una
evaluación explícita porque el componente la identifica como experimental.

### Opción MSK o Kafka

Amazon MSK es preferible si se necesita conservar el contrato Kafka de la
arquitectura local o facilitar la portabilidad. Un Kafka autogestionado
también puede ser fuente de Glue, pero exige conectividad, TLS y una conexión
de Glue configurada. No se reutilizará el Kafka funcional de Astronomy Shop.

La decisión entre Kinesis y MSK forma parte de esta alternativa y se tomará
según costo, conectividad, portabilidad y volumen observado.

## Procesamiento en AWS Glue

Glue Streaming utiliza Spark Structured Streaming. Para este proyecto, el
trabajo deberá:

1. declarar esquemas explícitos para cada señal;
2. decodificar y expandir los mensajes OTLP;
3. normalizar atributos, tiempos, unidades e identificadores;
4. aplicar marcas de agua y deduplicación;
5. agregar cada modalidad por componente y ventana;
6. unir los agregados en una representación Gold;
7. escribir checkpoints y datos en ubicaciones separadas de S3;
8. registrar en el catálogo los esquemas que deban consultarse.

No se utilizará detección automática del esquema para el tramo que realiza
uniones de flujos, porque Glue no permite esas uniones cuando la detección
automática está activa. Los contratos deben ser explícitos y versionados.

## Modelo de ejecución y latencia

La correlación multimodal requiere operaciones con estado: agregaciones,
deduplicación, ventanas y uniones. Por ello se utilizará el modo microbatch de
Glue, no el modo de tiempo real de Glue 6.0.

El modo de tiempo real de Glue 6.0 ofrece menor latencia, pero está limitado a
Kafka, Scala y operaciones sin estado. No admite las operaciones centrales de
esta propuesta. El intervalo del microbatch se ajustará después del perfilado;
un rango inicial de 10 a 30 segundos puede probarse, pero no se considera una
decisión final.

## Versiones y desarrollo local

Los trabajos se escribirán con interfaces estándar de Spark Structured
Streaming para reducir el acoplamiento. AWS publica imágenes Docker para
desarrollar y probar trabajos Glue localmente. Glue 5.0 ofrece Spark 3.5.4 y
Python 3.11, combinación compatible con la versión de Python empleada por
AIOpsLab.

La imagen local facilita pruebas unitarias y de transformaciones, pero no
reproduce por completo el servicio administrado, IAM, redes VPC, Kinesis,
MSK, autoescalado, latencias ni costos. La validación de la alternativa exige
por tanto al menos una ejecución real en AWS.

## Persistencia y consulta

S3 será el repositorio durable:

```text
s3://<bucket>/telemetry/bronze/signal=<signal>/run_id=<run_id>/...
s3://<bucket>/telemetry/silver/signal=<signal>/run_id=<run_id>/...
s3://<bucket>/telemetry/gold/run_id=<run_id>/...
s3://<bucket>/telemetry/checkpoints/job=<job>/...
```

Parquet es suficiente para el primer perfil. Iceberg puede incorporarse si se
requieren evolución de esquema, actualizaciones o administración transaccional
de tablas. El formato se elegirá por necesidad observada, no por defecto.

Para Grafana se contemplan dos rutas:

- consultar las tablas de S3 mediante Athena;
- cargar o consultar Gold desde ClickHouse cuando se requiera menor latencia
  interactiva.

La ruta elegida debe preservar identificadores de procedencia y evitar que la
interfaz se convierta en el lugar donde se realiza la fusión.

## Seguridad y gobernanza

La alternativa requiere:

- roles IAM con privilegios mínimos;
- cifrado en tránsito y en reposo;
- separación de buckets o prefijos por capa;
- exclusión o anonimización de secretos y datos sensibles antes del envío;
- credenciales fuera del repositorio;
- registro de región, cuenta, versiones y configuración en cada ejecución;
- política de expiración para datos y checkpoints.

La salida desde el sistema local hacia AWS debe registrarse como parte de las
condiciones experimentales, porque añade latencia y posibles fallos de red.

## Costos que deben medirse

El presupuesto incluirá al menos:

- horas de ejecución y capacidad de Glue;
- Kinesis o MSK;
- almacenamiento y solicitudes de S3;
- consultas de Athena o capacidad de ClickHouse;
- transferencia de datos;
- logs y métricas de CloudWatch.

Los trabajos de streaming se facturan mientras están activos. Las pruebas
deben tener cierre automático y límites presupuestarios para evitar que una
ejecución experimental quede abierta.

## Plan de implementación

1. Ejecutar el perfilado local antes de dimensionar servicios AWS.
2. Versionar los contratos OTLP, Silver y Gold.
3. Construir el trabajo PySpark con Spark Structured Streaming estándar.
4. Probar transformaciones mediante la imagen Docker de Glue.
5. Crear infraestructura declarativa para IAM, S3 y Kinesis o MSK.
6. Configurar la rama del Collector hacia AWS.
7. Desplegar el trabajo Glue con checkpoints en S3.
8. Validar la salida Bronze, Silver y Gold.
9. Conectar el Grafana en Docker con Athena o ClickHouse.
10. Ejecutar el escenario normal, `adFailure` y recuperación.
11. Medir latencia, costo, pérdida, duplicados y recuperación.
12. Comparar el resultado con la arquitectura local usando los mismos datos.

## Ventajas esperadas

- Reduce la administración del motor de procesamiento.
- Integra almacenamiento durable, catálogo y servicios analíticos de AWS.
- Permite escalar sin dimensionar manualmente un clúster local completo.
- Facilita una evaluación adicional de despliegue administrado.

## Riesgos y mitigaciones

| Riesgo | Mitigación propuesta |
|---|---|
| Contradicción con la validación local | Mantener el sistema controlado local y una ruta reproducible de desarrollo |
| Dependencia de AWS | Usar Spark estándar y contratos independientes del proveedor |
| Costos de trabajos continuos | Límites, alertas y cierre automático por ejecución |
| Latencia de red desde el laboratorio | Medirla y registrarla como condición experimental |
| Cambios de esquema | Esquemas explícitos, catálogo y versionado |
| Exposición de telemetría sensible | Filtrado previo, cifrado e IAM mínimo |
| Diferencias entre Docker y Glue administrado | Pruebas de integración en AWS antes de aceptar la alternativa |

## Criterios de aceptación del prototipo

- Las tres modalidades llegan a AWS con un `run_id` verificable.
- Los esquemas son explícitos y versionados.
- Los checkpoints permiten continuar después de detener y reiniciar el job.
- La representación Gold puede reconstruirse desde Bronze.
- Se cuantifican latencia, duplicados, pérdida y costo por ejecución.
- Grafana consulta los resultados sin realizar la fusión.
- El trabajo puede probarse parcialmente en Docker y desplegarse de forma
  reproducible mediante infraestructura declarativa.

## Fuentes técnicas de implementación

- [AWS Glue Streaming](https://docs.aws.amazon.com/glue/latest/dg/streaming-chapter.html).
- [Trabajos ETL de streaming en AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/add-job-streaming.html).
- [Conceptos avanzados de streaming en AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/glue-streaming-advanced-concepts.html).
- [Modelos de ejecución de Glue Streaming](https://docs.aws.amazon.com/us_en/glue/latest/dg/glue-streaming-execution-models.html).
- [Desarrollo local de Glue mediante Docker](https://docs.aws.amazon.com/glue/latest/dg/develop-local-docker-image.html).
- [Versiones de AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/release-notes.html).
- [Precios de AWS Glue](https://aws.amazon.com/glue/pricing/).
- [Exportador Kinesis de OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/awskinesisexporter).

