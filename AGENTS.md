# Memoria compacta del proyecto

## Objetivo

Construir, por ciclos, el planteamiento del problema de una investigación sobre detección de patrones en la monitorización de sistemas distribuidos. La redacción debe basarse en el corpus de `papers/`, distinguir evidencia de inferencia y usar citación numérica y referencias en estilo IEEE.

## Alcance vigente: ciclo 6 (borrador para presentación)

- Incluido: planteamiento sintetizado, pregunta de investigación reformulada, objetivo general, tres objetivos específicos, alcances y limitaciones, justificación, diez núcleos del marco teórico, metodología DSRM, plan de trabajo y referencias.
- Excluido del documento de presentación: hipótesis, marco conceptual separado y metodología distinta de DSRM.
- El contexto macro disponible es internacional. El corpus actual no contiene evidencia cuantitativa específica para Colombia; no inventar ni extrapolar cifras nacionales.
- Objeto provisional: patrones obtenidos mediante el análisis conjunto de métricas, registros (logs) y trazas de sistemas distribuidos. Las tres señales forman parte del núcleo del proyecto; ninguna se tratará únicamente como complemento.
- La validación se realizará en sistemas controlados desplegados localmente. AIOpsLab es el antecedente principal para preparar esos escenarios, pero no debe nombrarse dentro del objetivo específico.
- La contribución central es el método interpretable; la extensión para Grafana es el medio de integración y presentación.
- La delimitación se organiza mediante cuatro variables tecnológicas: integración multimodal, desempeño del reconocimiento de patrones, interpretabilidad y utilidad para la toma de decisiones.
- El resultado se acota a un prototipo funcional de carácter experimental compuesto por el flujo multimodal, el método, el componente de procesamiento y la extensión para Grafana; no se plantea una implementación industrial.
- La validación se restringe a escenarios, datos y ventanas temporales reproducibles en sistemas controlados desplegados localmente. No se incluye por ahora una población humana ni un estudio de usabilidad con operadores.
- El marco teórico se organiza en diez núcleos derivados del mapa mental: observabilidad; dependencias distribuidas; señales multimodales; representación conjunta; aprendizaje automático; calidad y cambio de los datos; interpretabilidad; apoyo a decisiones; integración con Grafana; y validación reproducible.
- Ciberseguridad, procesamiento de lenguaje natural, mantenimiento predictivo y remediación automática se reconocen como áreas vecinas del mapa mental, pero quedan fuera de los núcleos porque no corresponden al alcance vigente.
- El documento de presentación no incluye un marco conceptual separado. Los conceptos necesarios se definen en el marco teórico o la metodología.
- En el planteamiento del problema no se nombrarán herramientas, plataformas, bancos de prueba ni modelos concretos. La necesidad del artefacto se justificará de forma genérica mediante la fragmentación de las señales, la carga de correlación manual y la necesidad de evidencia trazable.
- Límites de extensión: problema con pregunta incluida, máximo 600 palabras; alcances y limitaciones, máximo 250; justificación, máximo 300; marco teórico, máximo 1500.
- La metodología general seleccionada es DSRM, aplicada mediante identificación del problema, definición de objetivos, diseño y desarrollo, demostración, evaluación y comunicación.
- La aplicación de DSRM se desarrolla como un protocolo detallado: cada actividad declara propósito e insumos, acciones, producto verificable y criterio de avance o cierre.
- La entrada a DSRM es centrada en el problema y la secuencia es nominal e iterativa. La evaluación puede devolver el trabajo a la definición de objetivos o al diseño y desarrollo.
- CRISP-ML(Q) y MLOps no se adoptan como metodologías adicionales. Sus prácticas podrán consultarse dentro de las actividades técnicas sin alterar la elección de DSRM.
- El término preferido es «datos de referencia para la evaluación». «Oráculo de evaluación» es una denominación técnica para etiquetas, condiciones conocidas, componentes intervenidos, secuencias esperadas o criterios de aceptación; no es un agente ni una herramienta.
- La demostración y la evaluación son actividades distintas: la primera verifica el uso integral del prototipo en escenarios concretos; la segunda compara los resultados con objetivos, líneas base y datos de referencia.
- La evaluación conserva las cuatro variables de delimitación: integración multimodal, desempeño, interpretabilidad y utilidad. La reproducibilidad se trata como control transversal, no como una quinta variable.
- El documento incluye dos figuras propias: una cadena conceptual del problema sin herramientas específicas y un esquema de la aplicación iterativa de DSRM. Las figuras complementan el argumento y no reemplazan la evidencia ni las definiciones operativas.

## Decisiones vigentes para la formulación de objetivos

- La investigación se basará en *machine learning* (aprendizaje automático). La técnica, el tipo de aprendizaje, las variables y la arquitectura deben determinarse mediante la investigación; no asumir de antemano aprendizaje profundo, Transformers, LLM, grafos u otra familia específica.
- El método deberá ser interpretable. «Interpretable» tendrá que operacionalizarse mediante criterios verificables, por ejemplo fidelidad de la explicación, correspondencia con variables o eventos relevantes, comprensibilidad y utilidad para la decisión. No equiparar automáticamente visualización, explicación *post hoc* e interpretabilidad.
- Se diseñará un flujo de datos que integre métricas, logs y trazas en una representación conjunta apta para análisis. Deberá precisar adquisición, identificadores compartidos, sincronización temporal, transformación, fusión y tratamiento de datos faltantes o heterogéneos.
- Ya no se exige una representación topológica o mediante grafos. Podrá estudiarse si la evidencia y el método la justifican, pero no forma parte obligatoria de los objetivos.
- Se diseñará una extensión para Grafana. La elección de esta plataforma no determina por sí sola cómo se prepararán ni representarán los datos para el método.
- Grafana puede consultar, transformar y correlacionar resultados de varias fuentes, pero no debe describirse como si convirtiera automáticamente las señales en un único conjunto apto para aprendizaje automático. Deben distinguirse la herramienta de visualización, las fuentes de datos, el flujo de preparación y el componente que ejecuta el método.
- El alcance de «reconocimiento de patrones» y «apoyo a la toma de decisiones» todavía debe operacionalizarse. No asumir sin validación que el método detectará siempre fallos, identificará su tipo o encontrará una causa raíz.
- La formulación tendrá un objetivo general y exactamente tres objetivos específicos.
- El objetivo general se formula en términos de apoyar decisiones mediante reconocimiento de patrones en datos multimodales; la interpretabilidad continúa como requisito del método y criterio de evaluación, aunque ya no aparezca en el enunciado del objetivo general.
- El segundo objetivo reunirá la exploración del método de aprendizaje automático y su integración en una extensión para una herramienta de observabilidad.
- El tercer y último objetivo específico estará dedicado explícitamente a validar la extensión diseñada.

## Decisiones vigentes para la metodología

- En la identificación del problema se organizarán la evidencia, las inferencias, las tareas de decisión, los límites y los requisitos iniciales sin fijar una herramienta o técnica.
- En la definición de objetivos se operacionalizarán patrón, representación conjunta, integración, desempeño, interpretabilidad, utilidad, tarea de decisión y agente de evaluación.
- En diseño y desarrollo se separarán el flujo multimodal, la exploración del método, el componente de procesamiento y la extensión. La selección del aprendizaje automático se realizará mediante comparación empírica y no por preferencia previa.
- En demostración se producirán paquetes de ejecución trazables por escenario, con versiones, configuración, carga, condición, ventana, telemetría, transformaciones y resultados.
- En evaluación se usarán líneas base, repeticiones y datos de referencia. Los agentes permitirán medir cumplimiento, exactitud, tiempo y consistencia de tareas, pero no inferir usabilidad o aceptación humana.
- En comunicación se entregarán la arquitectura, los contratos y diccionarios de datos, el protocolo, las métricas, los resultados, los errores, las amenazas a la validez y los materiales de reproducción.
- Las unidades de análisis serán observaciones multimodales asociadas con componentes o interacciones durante ventanas definidas; la unidad experimental combinará sistema, versión, configuración, carga, escenario, condición y repetición.
- Los controles de validez cubrirán definición de constructos, condiciones experimentales, variabilidad y límites de generalización. La telemetría sensible deberá excluirse o anonimizarse.
- Las fases de DSRM se redactarán como explicaciones correlacionadas que integren el propósito, los insumos, las acciones, los resultados y la continuidad del proceso, sin rótulos internos como «Propósito e insumos», «Actividades», «Producto y criterio de avance» o «Decisión de iteración».
## Objetivos acordados

### Objetivo general

Apoyar las decisiones en la monitorización de sistemas distribuidos mediante un método de reconocimiento de patrones a partir de datos multimodales.

### Objetivos específicos

1. Diseñar un flujo de datos de observabilidad para sistemas distribuidos que integre métricas, registros y trazas en una representación conjunta apta para el análisis.
2. Explorar un método de aprendizaje automático para reconocer patrones en la representación conjunta de los datos de observabilidad de sistemas distribuidos e integrarlo en una extensión para una herramienta de observabilidad que presente los patrones identificados como información de apoyo a la toma de decisiones.
3. Validar la extensión diseñada mediante pruebas con agentes de evaluación sobre sistemas controlados desplegados localmente, valorando el desempeño del método y la utilidad de los resultados para la toma de decisiones.

## Pregunta de investigación acordada

¿De qué manera un método interpretable de reconocimiento de patrones en métricas, registros y trazas puede apoyar la toma de decisiones en la monitorización de sistemas distribuidos?

El planteamiento y la pregunta deben mantenerse en un máximo de 600 palabras. La formulación evita el verbo «mejorar» porque no debe anticiparse un efecto favorable antes de la validación.

## Hallazgos consolidados

1. Los sistemas distribuidos a gran escala operan con exigencias continuas de disponibilidad; su escala y lógica incrementan la dificultad de detectar, localizar y diagnosticar fallos.
2. La inspección manual de logs no escala por el volumen de eventos. Las reglas y firmas predefinidas pierden utilidad ante escenarios no conocidos.
3. Los patrones relevantes no se limitan a secuencias: pueden involucrar frecuencia, temporalidad, parámetros, correlaciones y contexto.
4. Los datos presentan heterogeneidad, falta de estructura, intercalación entre procesos, ruido, pérdida de datos, escasez de etiquetas, desbalance y deriva.
5. La literatura reporta limitaciones de adaptación continua, explicabilidad, generalización entre plataformas y reproducibilidad.
6. La evaluación se concentra en pocos conjuntos de datos y puede favorecer patrones simples; las trazas siguen subutilizadas en AIOps basado en LLM.
7. El pronóstico debe redactarse como inferencia razonada: usar fórmulas como «si estas limitaciones persisten» o «cabe esperar», nunca como resultado empírico observado.
8. Los grafos multiatributo constituyen una alternativa documentada para integrar componentes y señales, pero no son la única representación posible ni un requisito del proyecto reorientado.
9. Estudios primarios multimodales reportan beneficios al integrar métricas, logs y trazas para detección, clasificación y localización, pero sus resultados proceden de pocos bancos de prueba y no son directamente comparables.
10. La unificación de las señales como eventos es un antecedente pertinente para diseñar el flujo y la representación conjunta; no obliga a adoptar una arquitectura concreta.
11. La literatura de detección explicable distingue la explicación producida por el algoritmo de la interpretación que realiza un experto para diagnosticar y decidir. La fidelidad y la utilidad de las explicaciones deben validarse.
12. Existen bancos de prueba y conjuntos de datos reproducibles para microservicios, incluida infraestructura basada en Kubernetes, que pueden orientar el caso de estudio sin sustituir la decisión empírica pendiente.
13. Los estudios con profesionales reportan saturación de datos y alertas, correlación difícil por falta de metadatos, vistas poco navegables y dependencia del conocimiento experto; esto sustenta orientar la extensión al apoyo de decisiones.
14. Los marcos de evaluación con agentes muestran la conveniencia de separar tareas, resultados y tiempos, pero no obligan a adoptar LLM ni métricas topológicas.
15. La integración de señales requiere semántica e identificadores compatibles: compartir el nombre de una dimensión no garantiza que dos campos representen el mismo concepto, y mostrar fuentes en una interfaz común no resuelve esa correspondencia.
16. DeepTraLog, MSTGAD y PDiagnose aportan alternativas de fusión y muestran beneficios experimentales del análisis conjunto, pero sus arquitecturas y bancos de prueba son distintos; no justifican imponer grafos, atención, aprendizaje profundo ni votación.
17. La evidencia industrial adicional muestra que las reglas siguen siendo comunes por su costo, soporte y adaptabilidad, aunque dependen de conocimiento y de una selección adecuada de parámetros y relaciones.
18. RCAEval amplía los recursos reproducibles para validación con 735 casos, tres sistemas, once tipos de fallo y quince líneas base, pero está orientado a análisis de causa raíz y deberá adaptarse al alcance que se defina para reconocimiento de patrones.
19. LO2 aporta datos reales y etiquetados a gran escala, pero sus trazas son incompletas; sustenta requisitos de recolección y alineación, no una validación trimodal directa.
20. La evidencia industrial y técnica sustenta la necesidad de un artefacto que conecte preparación multimodal, análisis interpretable y presentación trazable; reunir paneles no resuelve esa necesidad.
21. DSRM es la metodología general más adecuada porque la contribución es un artefacto compuesto que debe diseñarse, demostrarse y evaluarse frente a objetivos explícitos.
22. CRISP-ML(Q) se concentra en el ciclo de vida y el aseguramiento de calidad de aplicaciones de aprendizaje automático, mientras MLOps enfatiza capacidades de ingeniería y operación; ambos quedan como referencias técnicas, no como metodologías concurrentes.
## Registro de fuentes y claves IEEE

- `[1]` L. Zhang et al., 2025, encuesta sobre AIOps y LLM. Archivo: `papers/zhang-etal-2025-aiops-llm-survey.pdf`.
- `[2]` J. Diaz-de-Arcaya et al., 2023, revisión sistemática conjunta MLOps/AIOps. Archivo: `papers/diaz-de-arcaya-etal-2023-mlops-aiops-systematic-survey.pdf`.
- `[3]` M. Landauer et al., 2023, encuesta sobre aprendizaje profundo para detección de anomalías en logs. Archivo: `papers/landauer-etal-2023-deep-learning-anomaly-detection-log-data.pdf`.
- `[4]` Á. Brandón et al., 2020, análisis de causa raíz basado en representaciones gráficas de arquitecturas orientadas a servicios y microservicios. Archivo: `papers/brandon-etal-2020-graph-based-root-cause-analysis.pdf`. DOI: `10.1016/j.jss.2019.110432`.
- `[5]` C. Lee et al., 2023, Eadro: detección y localización conjunta con logs, KPI y trazas. Archivo: `papers/lee-etal-2023-eadro-multisource-troubleshooting.pdf`. DOI: `10.1109/ICSE48619.2023.00150`.
- `[6]` S. Zhang et al., 2023, DiagFusion: diagnóstico multimodal, grafo de dependencias, localización y tipo de fallo. Archivo: `papers/zhang-etal-2023-diagfusion-multimodal-failure-diagnosis.pdf`. DOI: `10.1109/TSC.2023.3290018`.
- `[7]` C. Zhao et al., 2023, AnoFusion: detección no supervisada de fallos con datos multimodales. Archivo: `papers/zhao-etal-2023-anofusion-multimodal-failure-detection.pdf`. DOI: `10.1145/3580305.3599902`.
- `[8]` G. Yu et al., 2023, Nezha: análisis interpretable y granular de causas mediante datos multimodales y grafos de eventos. Archivo: `papers/yu-etal-2023-nezha-multimodal-root-cause-analysis.pdf`. DOI: `10.1145/3611643.3616249`.
- `[9]` Y. Chen et al., 2025, AIOpsLab: marco reproducible para despliegue, carga, inyección de fallos, telemetría y evaluación. Archivo: `papers/chen-etal-2025-aiopslab-evaluation-framework.pdf`.
- `[10]` S. Zhang et al., 2025, revisión integral del diagnóstico de fallos en microservicios. Archivo: `papers/zhang-etal-2025-microservice-failure-diagnosis-survey.pdf`. DOI: `10.1145/3715005`.
- `[11]` M. Scrocca et al., 2020, Kaiju: observabilidad orientada a eventos y representación conjunta de métricas, logs y trazas. Archivo: `papers/scrocca-etal-2020-kaiju-event-driven-observability.pdf`. DOI: `10.1145/3401025.3401740`.
- `[12]` Z. Li et al., 2024, encuesta sobre detección explicable de anomalías. Archivo: `papers/li-etal-2024-explainable-anomaly-detection-survey.pdf`. DOI: `10.1145/3609333`.
- `[13]` J. Sipple y A. Youssef, 2022, método general de XAI para detección no supervisada de anomalías y evaluación mediante error de atribución. Archivo: `papers/sipple-youssef-2022-explainable-ai-anomaly-detection.pdf`. DOI: `10.1007/978-3-031-16564-1_16`.
- `[14]` S. Jha et al., 2025, ITBench: marco y escenarios ejecutables para evaluar agentes en tareas de operaciones de TI. Archivo: `papers/jha-etal-2025-itbench-ai-agents.pdf`.
- `[15]` S. Niedermaier et al., 2019, estudio cualitativo industrial sobre observabilidad y monitorización de sistemas distribuidos. Archivo: `papers/niedermaier-etal-2019-observability-monitoring-interview-study.pdf`. DOI: `10.1007/978-3-030-33702-5_3`.
- `[16]` Y. Shkuro et al., 2022, artículo de posición sobre telemetría *schema-first*, semántica y correlación entre señales. Archivo: `papers/shkuro-etal-2022-schema-first-telemetry.pdf`. DOI: `10.48550/arXiv.2206.11380`.
- `[17]` C. Zhang et al., 2022, DeepTraLog: detección de anomalías mediante una representación conjunta de trazas y registros. Archivo: `papers/zhang-etal-2022-deeptralog-trace-log-anomaly-detection.pdf`. DOI: `10.1145/3510003.3510180`.
- `[18]` J. Huang et al., 2023, MSTGAD: detección multimodal con métricas, registros y trazas y modelado de dependencias temporales. Archivo: `papers/huang-etal-2023-mstgad-multimodal-anomaly-detection.pdf`. DOI: `10.1109/ASE56229.2023.00138`.
- `[19]` C. Hou et al., 2021, PDiagnose: diagnóstico de problemas de rendimiento con fuentes heterogéneas. Archivo: `papers/hou-etal-2021-pdiagnose-heterogeneous-data.pdf`. DOI: `10.1109/ISPA-BDCloud-SocialCom-SustainCom52081.2021.00074`.
- `[20]` M. Steidl et al., 2024, estudio industrial sobre anomalías en ejecución, enfoques empleados y parámetros de monitorización. Archivo: `papers/steidl-etal-2024-industry-runtime-anomalies.pdf`. DOI: `10.1109/SEAA64295.2024.00062`.
- `[21]` L. Pham et al., 2025, RCAEval: banco reproducible para análisis de causa raíz con telemetría de microservicios. Archivo: `papers/pham-etal-2025-rcaeval-benchmark.pdf`. DOI: `10.1145/3701716.3715290`.
- `[22]` A. Bakhtin et al., 2025, LO2: conjunto de datos etiquetado de registros y métricas de un sistema de microservicios, con discusión de las limitaciones de trazado y alineación. Archivo: `papers/bakhtin-etal-2025-lo2-dataset.pdf`. DOI: `10.1145/3727582.3728682`.
- `[23]` K. Peffers et al., 2007, DSRM para investigación de ciencia del diseño en sistemas de información. Archivo: `papers/peffers-etal-2007-dsrm.pdf`. DOI: `10.2753/MIS0742-1222240302`.
- `[24]` S. Studer et al., 2021, CRISP-ML(Q) como modelo de proceso con aseguramiento de calidad para aplicaciones de aprendizaje automático. Archivo: `papers/studer-etal-2021-crisp-mlq.pdf`. DOI: `10.3390/make3020020`.

No cambiar la numeración sin actualizar simultáneamente `docs/propuesta_investigacion.md`, `docs/matriz_evidencia.md`, este registro y los artefactos exportados. `docs/proyecto_investigacion.md` se conserva como fuente histórica del ciclo 5 y mantiene las referencias [1]–[22].

## Contrato de redacción

- Idioma: español académico claro, sin traducciones literales innecesarias.
- Citas: referencias numéricas entre corchetes en orden de aparición, antes del signo de puntuación cuando corresponda: `[1]`.
- Referencias: formato IEEE, DOI o identificador persistente cuando exista.
- Evitar afirmaciones causales no sustentadas. Diferenciar «la literatura reporta» de «se infiere para el proyecto».
- Mantener la pregunta de investigación acordada y distinguirla de una hipótesis o una solución demostrada.
- Presentar el aprendizaje automático como orientación tecnológica acordada, sin anticipar una técnica específica (DL, Transformer, LLM u otra) mientras la investigación no la justifique.
- Tratar métricas, logs y trazas como entradas conjuntas del análisis, no como alternativas excluyentes ni como ampliaciones opcionales.
- Emplear expresiones como «apoyar la identificación», «localizar posibles causas» o «análisis de causa raíz» mientras no exista evidencia de que el método demuestra causalidad.
- Mantener explícita la validación en sistemas controlados desplegados localmente; no generalizar los resultados a cualquier sistema distribuido sin evidencia.
- Describir Grafana como plataforma de la extensión y distinguirla de los sistemas que recolectan, procesan o almacenan las señales. No atribuirle una unificación semántica automática de los datos.
- No nombrar Grafana ni otras herramientas específicas dentro del planteamiento del problema. Puede aparecer en objetivos, alcances, justificación, marco teórico, metodología y plan de trabajo.
- Usar «datos de referencia para la evaluación» como término principal y definir «oráculo de evaluación» antes de emplearlo como sinónimo.

## Artefactos canónicos

- Fuente editable vigente: `docs/propuesta_investigacion.md`.
- Fuente del ciclo anterior conservada: `docs/proyecto_investigacion.md`.
- Trazabilidad: `docs/matriz_evidencia.md`.
- Plan de transición al artículo empírico y registro de vacíos: `docs/plan_articulo_evidencia.md`.
- Borrador IEEE derivado: `articulo_ieee.tex`. Debe conservar la pregunta, los tres objetivos, DSRM como única metodología general y la numeración [1]–[24]; no sustituye la fuente editable vigente.
- Exportador: `scripts/build_documents.py`.
- Salidas vigentes: `output/docx/propuesta_investigacion.docx` y `output/pdf/propuesta_investigacion.pdf`.
- Guía humana: `README.md`.

## Alternativas técnicas vigentes para el ETL

- Se documentan dos arquitecturas candidatas en `docs/arquitecturas_etl/`:
  una alternativa local basada en OpenTelemetry Collector, Kafka, Flink,
  ClickHouse y MinIO; y una alternativa administrada basada en OpenTelemetry
  Collector, Kinesis o MSK, AWS Glue Streaming y S3.
- Ninguna alternativa ha sido seleccionada. La decisión requiere observar
  primero esquemas, caudal, cardinalidad, retrasos, duplicados, datos faltantes
  y correspondencia de identificadores en métricas, registros y trazas.
- Ambas alternativas deben conservar las capas lógicas Bronze, Silver, Gold y
  Results, así como contratos de datos independientes del motor.
- Grafana permanece como capa de integración y presentación; no realiza la
  adquisición, la persistencia, la fusión semántica ni la ejecución del método.
- La alternativa local es la referencia inicial para una validación
  completamente reproducible en el entorno controlado. AWS Glue se mantiene
  como opción administrada o híbrida y exige cuantificar latencia de red,
  costo y diferencias entre las pruebas Docker y la ejecución real en AWS.
- La observación inicial deberá comparar periodos de operación normal,
  condición introducida y recuperación, con `adFailure` como primera condición
  candidata en Astronomy Shop, sin asumir que será el escenario definitivo.
- Existe un prototipo técnico de la alternativa local en el repositorio hermano
  `AIOpsLab`. Su documentación académica se conserva en
  `docs/arquitecturas_etl/03_prototipo_local_implementado.md` y su evidencia de
  implementación se registra como A01–A07 en `docs/matriz_evidencia.md`.
- El prototipo local constituye evidencia de factibilidad dentro de diseño y
  desarrollo de DSRM; no selecciona de manera definitiva la alternativa local
  ni descarta la alternativa administrada.
- Se verificaron la construcción de la imagen ETL, el despliegue de Kafka y
  Flink, los cuatro temas, la conectividad desde Kubernetes, las pruebas
  unitarias, la ruta OTLP integrada, los checkpoints, la persistencia
  Bronze/Silver en Parquet/MinIO, Gold en ClickHouse y la consulta desde
  Grafana. Una repetición funcional al 1 % recorrió calentamiento, operación
  normal, `adFailure` y recuperación, y restauró la bandera a `off`.
- El perfil preliminar acumuló 23 800 mensajes Bronze, 436 322 eventos Silver
  y 6 660 ventanas Gold. Sus retrasos incluyen el drenaje de mensajes previos,
  por lo que no justifican todavía las ventanas ni marcas de agua definitivas.
  Continúan pendientes una medición en régimen estacionario y las tres
  repeticiones nominales del protocolo de 105 minutos.
- El drenaje inicial reveló tres reinicios por agotamiento del heap al construir
  lotes JDBC de 200 filas. El lote se redujo a 20 filas; el trabajo Flink
  sustituto mantuvo diez subtareas y completó 12 checkpoints, ninguno fallido,
  sin registrar excepciones en la observación posterior. Falta una prueba prolongada
  para considerar cerrada la validación de memoria.
- La siguiente iteración mantendrá un Gold canónico por servicio y ventana; no
  se creará un Gold por algoritmo. Se derivarán un conjunto tabular común y otro
  secuencial, con etiquetas experimentales separadas y contratos versionados.
  Una representación Gold adicional solo se justificará si cambia la unidad de
  análisis, por ejemplo, hacia trazas, secuencias de eventos o grafos.
- Antes del modelado se corregirán la identidad entre modalidades, la semántica
  de tasas y errores, las unidades de CPU y memoria, la rejilla temporal y el
  tratamiento de ausencias. El plan y los criterios de aceptación están en
  `docs/arquitecturas_etl/04_mejora_gold_y_protocolo_runs.md`.

## Protocolo para ciclos siguientes

1. Leer este archivo antes de redactar.
2. Incorporar y registrar nuevas fuentes sin romper la numeración IEEE existente, salvo revisión bibliográfica deliberada.
3. Actualizar primero la matriz de evidencia y después la fuente narrativa.
4. Registrar aquí las decisiones, hechos consolidados, cambios de alcance y pendientes; compactar y reemplazar información obsoleta en lugar de acumular un diario extenso.
5. Regenerar DOCX/PDF y verificar visualmente todas las páginas antes de cerrar el ciclo.

## Pendientes deliberados

- Definir el entorno empírico o caso de estudio concreto: aplicación, banco de datos, infraestructura local controlada, agentes de evaluación y mecanismo de generación o inyección de condiciones de interés.
- Determinar las fuentes concretas desde las que la extensión de Grafana obtendrá métricas, logs y trazas.
- Repetir el perfilado con el consumidor al día y ejecutar las tres
  repeticiones nominales; después comparar, con mediciones estacionarias, la
  arquitectura local y la alternativa administrada con AWS Glue.
- Implementar y validar `gold_service_window_v2`, `feature_tabular_v1` y
  `feature_sequence_v1` antes de entrenar los algoritmos candidatos; congelar
  las particiones por `run_id` y ajustar todo preprocesamiento solo con datos de
  entrenamiento.
- Seleccionar y justificar el enfoque de aprendizaje automático, sus variables de entrada y el esquema de entrenamiento o inferencia.
- Definir cómo se adquirirán, identificarán, sincronizarán, transformarán y fusionarán métricas, logs y trazas en una representación conjunta.
- Completar la operacionalización de «patrón», «interpretable», «apoyo a la toma de decisiones», «agente de evaluación» y «utilidad de los resultados», y establecer métricas y datos de referencia para validarlos.
- Decidir qué capacidades concretas expondrá la extensión y cuál será la frontera entre la interfaz, el servicio de procesamiento y las fuentes de observabilidad.
- Continuar ampliando el corpus con estudios primarios sobre fusión temporal, evaluación de explicaciones y utilidad para operadores; si se requiere contexto nacional, incorporar fuentes colombianas verificables.
