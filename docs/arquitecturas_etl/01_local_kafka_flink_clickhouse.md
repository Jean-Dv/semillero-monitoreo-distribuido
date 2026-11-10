# Arquitectura candidata 1: Kafka, Flink y ClickHouse en entorno local

## Propósito

Esta alternativa implementa un ETL de telemetría en tiempo casi real dentro
del entorno local controlado. Busca conservar la reproducibilidad del
experimento, operar sin depender de servicios externos y separar la
telemetría original de la representación preparada para aprendizaje
automático.

La arquitectura es candidata y no constituye todavía una selección
definitiva.

## Vista general

```text
Astronomy Shop
      |
      | OTLP
      v
OpenTelemetry Collector
      |\
      | +------> Prometheus / OpenSearch / Jaeger
      |                          |
      |                          +------> Grafana: señales originales
      |
      +--------> Kafka dedicado
                       |
                       v
                 Apache Flink
                 |           \
                 |            +----> MinIO: Bronze y Silver en Parquet
                 v
              ClickHouse
                 |
                 +----> método de aprendizaje automático
                 |
                 +----> Grafana: Gold y Results
```

Grafana continuará ejecutándose mediante Docker. Kafka, Flink, ClickHouse y
MinIO se desplegarán también mediante contenedores o dentro del clúster local;
no requieren instalaciones de servidor en el sistema anfitrión.

## Responsabilidades

### OpenTelemetry Collector

El Collector recibe OTLP desde los servicios y duplica la salida. Una rama
mantiene los backends actuales para inspección operativa. La otra envía los
mensajes a Kafka. Su responsabilidad se limita a recepción, procesamiento
ligero, control de lotes, reintentos y enrutamiento; no realiza la fusión
multimodal.

### Kafka

Kafka actúa como registro durable y desacopla la producción de telemetría del
procesamiento. Se desplegará una instancia dedicada; no se reutilizará el
Kafka funcional de Astronomy Shop, porque una intervención sobre el
experimento no debe afectar simultáneamente la aplicación y su canal de
observación.

Los temas iniciales serán:

```text
otel.metrics.v1
otel.logs.v1
otel.traces.v1
experiment.control.v1
gold.observation_windows.v1
results.patterns.v1
```

Separar las señales permite configurar retención, particiones y consumidores
de forma independiente. `experiment.control.v1` transportará eventos de
inicio, condición introducida, recuperación y cierre de cada ejecución.

### Apache Flink

Flink ejecuta las transformaciones con tiempo de evento:

1. decodifica el mensaje OTLP;
2. expande recursos, ámbitos, puntos, registros y spans;
3. normaliza nombres, unidades y marcas temporales;
4. calcula identificadores deterministas para detectar duplicados;
5. aplica marcas de agua y separa eventos excesivamente tardíos;
6. crea agregados por modalidad;
7. relaciona las señales por identificadores y ventanas;
8. produce la observación Gold y sus indicadores de calidad.

La implementación podrá combinar DataStream o PyFlink para decodificar OTLP
con Flink SQL para las agregaciones y uniones temporales. La elección interna
se hará después de observar la complejidad real de los mensajes.

### ClickHouse

ClickHouse almacena las observaciones Gold y los resultados que requieren
consulta interactiva. Cada registro tendrá una clave determinista de
ejecución, componente y ventana para tolerar reintentos y facilitar la
deduplicación. ClickHouse no reemplaza el archivo de los mensajes originales.

### MinIO y Parquet

MinIO proporciona almacenamiento de objetos compatible con S3. Los mensajes
Bronze y las tablas Silver se almacenarán en Parquet, particionados al menos
por modalidad, fecha y `run_id`. Esta copia permite reconstruir una ejecución
aunque los backends operativos de Astronomy Shop sean efímeros.

## Correlación de las señales

La correlación seguirá una jerarquía explícita:

1. `trace_id` y `span_id` para relacionar registros y trazas cuando estén
   presentes;
2. `service.name`, namespace, workload y pod para identificar el componente;
3. tiempo de evento para ubicar las observaciones en la misma ventana;
4. metadatos de Kubernetes para relacionar métricas de infraestructura con el
   servicio o workload correspondiente.

Las métricas no se forzarán a una relación individual con cada span. Se
agregarán por componente y ventana. La unión Gold será externa para conservar
ventanas en las que falte una modalidad y registrará esa ausencia como dato de
calidad.

## Parámetros iniciales sujetos a medición

Para el primer prototipo se podrán ensayar ventanas de 30 segundos con avance
de 10 segundos y una tolerancia inicial de 30 segundos para eventos tardíos.
Estos valores son hipótesis de ingeniería: el perfil de retraso observado,
especialmente su percentil 99, determinará la configuración final.

La retención de Kafka será corta y suficiente para reproducción operativa. El
archivo de largo plazo se realizará en MinIO. No se fijarán todavía el número
de particiones ni los límites de recursos.

## Entrega y recuperación

Flink conservará estado y offsets mediante checkpoints. Para evitar afirmar
una garantía de extremo a extremo que el destino no proporcione, el diseño
combinará entrega al menos una vez con:

- claves deterministas;
- transformaciones idempotentes;
- deduplicación explícita;
- checkpoints persistentes;
- pruebas de interrupción y recuperación.

La evaluación deberá comprobar que un reinicio no pierde ventanas y que los
duplicados posibles no alteran el resultado final.

## Plan de implementación

1. Perfilar las tres señales mediante consultas de solo lectura a los
   backends actuales.
2. Definir y versionar los contratos Bronze, Silver y Gold.
3. Añadir al Collector una rama secundaria hacia Kafka.
4. Crear los temas y las políticas de retención.
5. Implementar el trabajo de normalización en Flink.
6. Implementar las agregaciones y la unión multimodal.
7. Persistir Bronze y Silver en MinIO y Gold en ClickHouse.
8. Aprovisionar ClickHouse como fuente de datos del Grafana en Docker.
9. Ejecutar el escenario normal, `adFailure` y recuperación.
10. Probar reproducción, reinicio, datos tardíos y ausencia parcial de
    señales.

## Ventajas esperadas

- Mantiene la validación completamente local.
- Permite controlar versiones, configuración y recursos.
- Facilita la reproducción sin costos de nube.
- Proporciona procesamiento con tiempo de evento y estado.
- Reduce la dependencia de un proveedor.

## Riesgos y mitigaciones

| Riesgo | Mitigación propuesta |
|---|---|
| Sobrecarga de recursos en la estación local | Medir primero el caudal y fijar límites por contenedor |
| Complejidad operativa | Componer servicios por perfiles y automatizar comprobaciones de salud |
| Cambios del esquema OTLP | Versionar contratos y conservar Bronze intacto |
| Duplicados al recuperar | Claves deterministas e idempotencia |
| Eventos fuera de orden | Tiempo de evento, marcas de agua y salida de eventos tardíos |
| Contaminación de la aplicación | Kafka dedicado y límites de recursos separados |

## Criterios de aceptación del prototipo

- Las tres modalidades llegan al flujo y quedan asociadas con un `run_id`.
- La copia Bronze permite reproducir una ejecución.
- Gold representa ventanas con una, dos o tres modalidades sin descartarlas.
- Cada resultado puede rastrearse hasta sus entradas Silver y Bronze.
- Un reinicio controlado no produce pérdida silenciosa.
- Grafana consulta Gold sin ejecutar la lógica de fusión.
- El escenario de falla y recuperación produce un paquete experimental
  repetible, sin asumir que la falla siempre será reconocida por el método.

## Fuentes técnicas de implementación

- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/).
- [Exportador Kafka de OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/exporter/kafkaexporter/README.md).
- [Documentación de Apache Kafka](https://kafka.apache.org/documentation/).
- [Tiempo de evento y análisis de flujos en Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/streaming_analytics/).
- [Tolerancia a fallos de Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/).
- [Integración de ClickHouse con Grafana](https://clickhouse.com/integrations/grafana).

