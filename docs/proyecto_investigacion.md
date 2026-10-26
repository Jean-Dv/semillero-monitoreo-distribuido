# Proyecto de investigación

**Proyecto:** Detección de patrones en la monitorización de sistemas distribuidos  
**Versión:** Ciclo 5 (en desarrollo) - Justificación, delimitación, alcance y marcos teórico y conceptual  
**Alcance:** Sistemas distribuidos observados mediante métricas, registros y trazas, con validación en sistemas controlados desplegados localmente.

## Nota de alcance

El planteamiento se sustenta en los veintidós estudios disponibles en la carpeta *papers*. El corpus aporta un contexto internacional y técnico, pero no contiene estadísticas específicas de Colombia. La contribución central prevista es un método interpretable de reconocimiento de patrones sobre una representación conjunta de métricas, registros y trazas. El método se integrará mediante una extensión para Grafana; esta plataforma puede reunir consultas y visualizaciones de diversas fuentes, pero no unifica por sí sola las señales para el análisis.

## 1. Planteamiento del problema

Los servicios digitales dependen de sistemas distribuidos que deben operar continuamente. Sin embargo, su escala, sus dependencias y su lógica interna dificultan detectar y diagnosticar fallos, que pueden ocasionar interrupciones, pérdida de rendimiento y afectaciones económicas y reputacionales [1]. Para comprender su comportamiento, la observabilidad emplea métricas, que cuantifican el estado y el desempeño; registros o *logs*, que documentan eventos y cambios; y trazas, que reconstruyen el recorrido de las solicitudes entre servicios [1]. Aunque AIOps busca procesar estos datos mediante aprendizaje automático [1], [2], persiste una brecha entre su generación masiva y una interpretación oportuna, confiable y comprensible.

Los indicios de degradación se encuentran inmersos en una mayoría de eventos normales, por lo que la inspección manual no escala y las reglas predefinidas solo reconocen situaciones conocidas [3]. Un patrón anómalo puede manifestarse en atributos, frecuencias, intervalos, parámetros, correlaciones o contextos temporales. Además, los eventos concurrentes pueden llegar intercalados y sin identificadores consistentes, lo cual dificulta reconstruir sus relaciones [3].

La dificultad no se resuelve únicamente mostrando las señales en una misma herramienta. Métricas, registros y trazas difieren en estructura, granularidad, volumen y semántica, de modo que su análisis conjunto exige definir adquisición, sincronización, contexto compartido, transformación y representación. Los modelos gráficos son una alternativa documentada [4]–[8], pero no constituyen un requisito del proyecto. Kaiju demuestra otra posibilidad: representar las tres señales como eventos y aplicar operaciones de filtrado, unión y correlación sobre flujos, conservando procesamientos específicos por modalidad [11]. Una propuesta *schema-first* advierte que vincular señales exige metadatos semánticos compatibles [16]. Otros estudios relacionan trazas y registros mediante identificadores compartidos [17] o fusionan las tres modalidades para detectar y diagnosticar anomalías [18], [19]; sus arquitecturas son antecedentes, no requisitos. Por ello, el flujo y la representación conjunta son decisiones de investigación, no funciones delegables por completo en la plataforma de visualización.

La interpretabilidad también requiere una definición verificable. Una explicación puede no corresponder al criterio con el que el detector marcó una anomalía; por ello, la literatura recomienda evaluar su fidelidad, alcance y utilidad para el destinatario [12]. Asimismo, se distingue entre generar atribuciones —tarea algorítmica— e interpretarlas con conocimiento experto para reconocer una condición y decidir una acción —tarea cognitiva— [13]. En este proyecto, reconocer patrones deberá producir evidencia comprensible que apoye, sin reemplazar, el juicio del operador.

Los resultados publicados proceden de conjuntos y escenarios limitados, por lo que el desempeño y la utilidad operativa deben validarse. AIOpsLab permite desplegar sistemas, generar carga, inyectar fallos, exportar telemetría y evaluar agentes en condiciones reproducibles [9]; las revisiones recopilan tareas, datos y métricas disponibles [10]. ITBench confirma la pertinencia de separar el diagnóstico, la localización y el tiempo requerido por agentes que consultan señales de observabilidad [14]. Profesionales del sector reportan saturación de alertas, correlación difícil, metadatos insuficientes y dependencia del conocimiento experto [15], [20]. RCAEval y LO2 aportan casos reproducibles y datos etiquetados, aunque evidencian límites de cobertura y alineación [21], [22].

Si estas limitaciones persisten, cabe esperar una monitorización fragmentada y reactiva, con falsas alarmas, omisiones y verificación manual. Un método opaco o una interfaz que solo agregue paneles podría aumentar la carga cognitiva en vez de mejorar las decisiones. Se requiere, por tanto, investigar una representación multimodal y un método interpretable, integrarlos en una herramienta de observabilidad y comprobar su aporte en sistemas controlados.

### Pregunta problema

¿Cómo se puede mejorar la toma de decisiones en la monitorización de sistemas distribuidos mediante un método interpretable de reconocimiento de patrones en datos multimodales?

## 2. Objetivos

### 2.1 Objetivo general

Diseñar un método interpretable de reconocimiento de patrones a partir de datos multimodales que apoye la toma de decisiones en la monitorización de sistemas distribuidos.

### 2.2 Objetivos específicos

1. Diseñar un flujo de datos de observabilidad para sistemas distribuidos que integre métricas, registros y trazas en una representación conjunta apta para el análisis.

2. Explorar un método interpretable de aprendizaje automático para reconocer patrones en la representación conjunta de los datos de observabilidad de sistemas distribuidos.

3. Diseñar una extensión para una herramienta de observabilidad que integre el método de aprendizaje automático y presente los patrones identificados como información de apoyo a la toma de decisiones.

4. Validar la extensión diseñada mediante pruebas reproducibles con agentes de evaluación sobre sistemas controlados desplegados localmente, valorando el desempeño del método y la utilidad de los resultados para la toma de decisiones.

## 5. Justificación

La pertinencia tecnológica del proyecto radica en que las métricas, los registros y las trazas aportan perspectivas complementarias sobre el funcionamiento de los sistemas distribuidos [1]. Su integración exige resolver diferencias de formato, granularidad, tiempo y semántica [11], [16]. Aunque los estudios multimodales demuestran la viabilidad de analizar conjuntamente estas señales, sus resultados proceden de escenarios y arquitecturas limitados [5]–[8]. Además, la información obtenida debe ser comprensible y verificable para quien toma decisiones [12], [13]. Por ello, resulta pertinente investigar una solución integrada, interpretable y evaluable bajo condiciones controladas.

La investigación se orienta a convertir las tres señales de observabilidad en información conjunta que facilite la identificación y comprensión de patrones de operación. El método proporcionará evidencia sobre los datos y acontecimientos relacionados con cada resultado, sin sustituir el juicio experto ni afirmar automáticamente relaciones causales [12], [13]. La extensión para Grafana permitirá consultar y presentar esa información dentro de un entorno de observabilidad, de modo que pueda utilizarse como apoyo durante tareas previamente definidas. Así, la contribución podrá valorarse tanto por su desempeño técnico como por la utilidad de sus resultados para la toma de decisiones [14], [15].

En concreto, se busca diseñar un método interpretable de aprendizaje automático aplicado a una representación conjunta de datos multimodales. Las variables tecnológicas que delimitan el proyecto son la integración multimodal, el desempeño del reconocimiento de patrones, la interpretabilidad y la utilidad para la toma de decisiones. La integración comprenderá la alineación de métricas, registros y trazas mediante semántica, identificadores y contexto temporal compatibles [16]. La interpretabilidad se valorará por la fidelidad, relevancia, comprensibilidad y utilidad de la evidencia producida [12], [13], mientras el desempeño y la utilidad se evaluarán únicamente en los escenarios controlados seleccionados [9], [14].

Desde el punto de vista tecnológico, primero se diseñará un flujo para adquirir, identificar, sincronizar, transformar y fusionar métricas, registros y trazas [11], [16]. Después se explorará una técnica de aprendizaje automático sin imponer previamente una familia de modelos, y se establecerán criterios verificables para interpretar los patrones reconocidos [12], [13]. El método será ejecutado por un componente de procesamiento y sus resultados se integrarán mediante una extensión para Grafana, diferenciando la interfaz de las fuentes y del flujo de preparación. Finalmente, el prototipo se validará mediante pruebas reproducibles con agentes de evaluación sobre sistemas controlados desplegados localmente [9], [14].

## 6. Delimitación y alcance

### 6.1 Delimitación

La investigación se delimita al reconocimiento interpretable de patrones en sistemas distribuidos a partir de una representación conjunta de métricas, registros (*logs*) y trazas. Estas tres señales constituirán el núcleo del análisis. No se abordarán otras funciones de AIOps, como predicción de capacidad, ciberseguridad o remediación automática.

La delimitación comprende cuatro variables tecnológicas: **integración multimodal**, entendida como la relación de las señales mediante semántica, identificadores, sincronización y transformaciones compatibles [11], [16]–[19], [22]; **desempeño**, referido a los patrones que se definan y operacionalicen; **interpretabilidad**, valorada mediante fidelidad, relevancia, comprensibilidad y utilidad [12], [13]; y **utilidad para la toma de decisiones**, restringida al apoyo brindado en tareas previamente definidas [14], [15]. Un patrón no se asumirá automáticamente como fallo, tipo de fallo o causa raíz.

Se empleará aprendizaje automático, pero la técnica, las variables de entrada y la arquitectura se seleccionarán durante la investigación. No se exige aprendizaje profundo, Transformers, LLM, grafos u otra familia específica. Grafana será la plataforma de integración y presentación; la preparación de las señales y la ejecución del método corresponderán al flujo de datos y al componente de procesamiento [11], [16]–[19].

La validación se limitará a sistemas controlados desplegados localmente y a las configuraciones, cargas y periodos efectivamente evaluados [9], [21]. Las unidades de análisis serán los componentes del sistema y sus observaciones; no se incluye una población humana ni un estudio de usabilidad [13]–[15]. Quedan fuera el despliegue industrial, la operación continua, la remediación automática, la demostración definitiva de causalidad y la garantía de localizar siempre una causa raíz.

### 6.2 Alcance

El proyecto llegará hasta un **prototipo funcional experimental**, no hasta una implementación industrial. Comprenderá un flujo para adquirir, sincronizar, transformar y fusionar las tres señales; un método de aprendizaje automático; un componente que produzca evidencia interpretable; y una extensión para Grafana que presente los patrones como apoyo a la toma de decisiones.

El alcance incluye la puesta en funcionamiento del flujo, la selección y evaluación del método, su integración en la extensión y la validación reproducible mediante agentes de evaluación en sistemas locales controlados. Se valorarán la integración, el desempeño, la interpretabilidad y la utilidad de los resultados [9], [12]–[14], [21]. Las métricas y datos de referencia se definirán al operacionalizar cada variable.

La extensión mostrará los patrones y su evidencia asociada. Solo incluirá detección, clasificación, priorización o localización de posibles causas si los resultados experimentales lo sustentan. El trabajo concluirá con la demostración y documentación del prototipo, sus resultados y limitaciones; no comprenderá endurecimiento para producción, alta disponibilidad, escalamiento industrial ni certificaciones de seguridad.

## 7. Marco referencial

### 7.1 Marco teórico

#### 7.1.1 DE LA SUPERVISIÓN REACTIVA A LA OBSERVABILIDAD DE SISTEMAS DISTRIBUIDOS

La monitorización tradicional utiliza indicadores, umbrales y alertas para comprobar condiciones conocidas. En arquitecturas distribuidas y cambiantes, esta supervisión ofrece una visión parcial. La observabilidad amplía su propósito al aportar evidencia para examinar el estado y el comportamiento del sistema a partir de sus salidas [1], [15]. No consiste solo en añadir paneles: un estudio con 28 profesionales de 16 organizaciones reporta saturación de datos, metadatos insuficientes y dificultades para correlacionar información [15].

AIOps incorpora análisis y aprendizaje automático para asistir tareas operativas [1], [2], pero no transforma automáticamente la telemetría en conocimiento útil. Para este proyecto, la observabilidad sustenta el análisis conjunto de señales y conserva al operador como responsable de interpretar la evidencia y decidir. La contribución tecnológica consiste en organizar información dispersa y hacer examinables los patrones reconocidos, no en reemplazar el juicio humano.

#### 7.1.2 DE LOS COMPONENTES AISLADOS A LAS DEPENDENCIAS DE LOS SISTEMAS DISTRIBUIDOS

Los sistemas distribuidos reúnen componentes que cooperan desde procesos o nodos distintos. En microservicios, una solicitud puede atravesar varios servicios, lo que introduce concurrencia, dependencias cambiantes y múltiples puntos de degradación. Una condición observada en un componente puede asociarse con efectos posteriores en otros, aunque esa relación no demuestre por sí sola la causa [4], [10].

La arquitectura aporta contexto para relacionar comportamientos locales, acontecimientos e interacciones. Diversos trabajos emplean grafos para modelar dependencias y propagar información entre componentes [4]–[6], [8], pero no demuestran que esta representación sea obligatoria. El proyecto podrá utilizar topologías, eventos, ventanas temporales o atributos compartidos, según los datos y el método. Dado que los bancos existentes cubren pocas arquitecturas y tipos de fallo [9], [10], [21], las conclusiones se limitarán a los escenarios observados.

#### 7.1.3 MÉTRICAS, REGISTROS Y TRAZAS COMO BASE MULTIMODAL DE LA OBSERVABILIDAD

Las métricas cuantifican recursos, latencias o tasas; los registros documentan acontecimientos; y las trazas reconstruyen recorridos entre servicios. Su complementariedad permite relacionar tendencias, eventos e interacciones, aunque sus diferencias de estructura, frecuencia, volumen y semántica dificultan el análisis conjunto [1]. En este proyecto, las tres señales forman el núcleo multimodal y ninguna se tratará como complemento opcional.

Eadro, DiagFusion, AnoFusion, MSTGAD y PDiagnose presentan mecanismos distintos para combinar estas modalidades en tareas de detección, clasificación o localización [5]–[7], [18], [19]. Sus resultados respaldan la viabilidad de la fusión, pero no son directamente comparables porque emplean sistemas, fallos y métricas diferentes. Además, una señal incompleta o desalineada puede introducir relaciones engañosas. Por ello, el proyecto deberá documentar qué obtiene de cada fuente, qué transforma y qué información conserva antes de relacionar la representación con los patrones reconocidos.

#### 7.1.4 DE LA REUNIÓN DE FUENTES A UNA REPRESENTACIÓN CONJUNTA PARA EL ANÁLISIS

Reunir fuentes en una interfaz no las convierte en datos aptos para aprendizaje automático. El flujo debe definir adquisición, identificadores, sincronización, transformaciones y tratamiento de ausencias o diferencias semánticas [11], [16]. Estas decisiones condicionan lo que el método podrá reconocer y forman parte del diseño de investigación.

Kaiju representa las señales como eventos correlacionables [11]; la telemetría *schema-first* exige tipos, unidades y metadatos compatibles [16]; DeepTraLog utiliza identificadores compartidos [17]; y MSTGAD y PDiagnose aplican estrategias diferentes de fusión [18], [19]. LO2 confirma que la falta de trazas y alineación limita una integración trimodal [22]. Por tanto, el proyecto distinguirá recolección, preparación, representación y análisis. La forma final podrá ser tabular, temporal, basada en eventos, topológica o híbrida, siempre que sea justificable y rastreable.

#### 7.1.5 DE LAS REGLAS ESTÁTICAS AL APRENDIZAJE AUTOMÁTICO PARA RECONOCER PATRONES

Las reglas y los umbrales son comprensibles y cuentan con amplio soporte, por lo que continúan siendo frecuentes. Los quince participantes del estudio de Steidl et al. utilizaban reglas propias, aunque algunas organizaciones también empleaban soluciones de inteligencia artificial [20]. Su límite es que dependen de conocimiento, parámetros y relaciones previstas, y pierden cobertura ante combinaciones no anticipadas [3], [20].

El aprendizaje automático permite inferir regularidades mediante estrategias supervisadas, no supervisadas y arquitecturas diversas [5]–[8], [17]–[19]. Esta variedad muestra que ninguna técnica es universal. El proyecto no impondrá aprendizaje profundo, Transformers, LLM, grafos u otra familia: la elección dependerá de la definición de patrón, los datos, los recursos y la interpretabilidad. Como métodos simples pueden ser competitivos en algunos conjuntos [3], las alternativas deberán compararse con criterios explícitos.

#### 7.1.6 HETEROGENEIDAD, CALIDAD Y CAMBIO EN LOS DATOS DE MONITORIZACIÓN

Los datos distribuidos pueden llegar intercalados, duplicados, incompletos o sin identificadores consistentes. También varían en formato, escala, frecuencia y reloj. Estas condiciones pueden alterar las relaciones que el método interpreta como patrones [3], [16], [22]. La escasez de etiquetas y el desbalance añaden dificultad, pues los casos de interés suelen ser pocos y su clasificación manual exige conocimiento experto [3]. LO2, por ejemplo, aporta registros y métricas reales a gran escala, pero no trazas completas [22].

Los cambios de versión, configuración, carga o infraestructura también pueden reducir la vigencia de un modelo [1]–[3]. El proyecto no promete adaptación continua; evaluará periodos y escenarios reproducibles. Para interpretar sus resultados deberá registrar las condiciones de captura, las transformaciones y las versiones utilizadas, evitando presentar el desempeño experimental como generalización indefinida.

#### 7.1.7 DE LA DETECCIÓN A LA INTERPRETACIÓN: EVIDENCIA PARA COMPRENDER LOS PATRONES

Detectar una regularidad no explica necesariamente por qué fue señalada ni qué significa para la operación. Li et al. distinguen la anomalía esperada por el usuario, el criterio del detector y la explicación generada [12]. Si no coinciden, una salida comprensible puede ser infiel al modelo; por ello, una gráfica o puntuación no basta para afirmar interpretabilidad.

Sipple y Youssef separan la atribución algorítmica de la interpretación que realiza una persona con conocimiento del contexto [13]. El método deberá producir evidencia rastreable, cuya fidelidad, relevancia, comprensibilidad y utilidad se evalúen. Nezha aporta un antecedente multimodal interpretable [8], pero no convierte su arquitectura gráfica en requisito. El proyecto podrá emplear un modelo interpretable, una explicación complementaria o ambos, sin atribuir causalidad no demostrada.

#### 7.1.8 DEL RECONOCIMIENTO DE PATRONES AL APOYO DE DECISIONES OPERATIVAS

Un patrón puede expresarse como frecuencia, secuencia, relación temporal, combinación de valores o comportamiento contextual [3]. Detectar una desviación, clasificarla, localizar un componente y proponer una causa posible son tareas distintas. Eadro, DiagFusion, AnoFusion y Nezha exploran combinaciones de estas capacidades [5]–[8], pero sus resultados no permiten tratarlas como equivalentes ni garantizadas.

Las correlaciones pueden priorizar componentes o reconstruir secuencias, pero no demuestran causalidad. La revisión de diagnóstico de microservicios confirma la diversidad de tareas y granularidades [10]. Por ello, el proyecto hablará de patrones, evidencia y posibles componentes relevantes. Apoyar decisiones significará presentar información pertinente sin decidir por el operador. Los estudios industriales reportan saturación y dependencia del conocimiento experto [15], mientras ITBench separa tareas, resultados y tiempos [14]. La evaluación con agentes medirá tareas definidas, no aceptación humana.

#### 7.1.9 INTEGRACIÓN DEL MÉTODO EN GRAFANA: DATOS, PROCESAMIENTO Y VISUALIZACIÓN

La integración en una herramienta de observabilidad exige separar responsabilidades: las fuentes producen o almacenan señales; el flujo las prepara; el componente de procesamiento ejecuta el método; y la interfaz presenta los resultados. Así se evita atribuir a la visualización una unificación semántica que depende de metadatos, identificadores y transformaciones [11], [16].

Grafana será la plataforma de la extensión, no la arquitectura del método. Mostrará los patrones, su contexto y la evidencia entregada por el componente de procesamiento, conservando vínculos con las fuentes. Una vista común solo es útil si responde a tareas concretas; paneles saturados pueden aumentar la carga del usuario [15]. Como la fusión multimodal requiere procesamiento específico [18], [19], la extensión se limitará a presentar resultados y apoyar la evaluación, sin almacenar telemetría ni ejecutar remediación.

#### 7.1.10 DE LA PRUEBA DEL MÉTODO A LA VALIDACIÓN REPRODUCIBLE EN SISTEMAS CONTROLADOS

Validar una propuesta multimodal exige documentar el sistema, la carga, las condiciones, la instrumentación, las ventanas y las transformaciones. AIOpsLab organiza despliegue, generación de carga, inyección de condiciones y evaluación reproducible [9]. ITBench separa tareas, resultados y tiempos [14]; RCAEval aporta 735 casos de fallo y quince líneas base [21]; y LO2 ofrece datos reales, aunque sin trazas completas [22]. Estos recursos orientan el diseño, pero ninguno cubre por sí solo las cuatro variables del proyecto.

La validación se realizará en sistemas controlados locales y diferenciará integración multimodal, desempeño, interpretabilidad y utilidad [12]–[14]. Los agentes ejecutarán tareas definidas sin imponer una tecnología interna ni sustituir estudios futuros con operadores. Las conclusiones quedarán limitadas a los sistemas, configuraciones, datos y periodos observados.

### 7.2 Marco conceptual

El marco conceptual reúne dos términos específicos derivados de cada núcleo temático. Se eligieron conceptos que no habían sido desarrollados como unidades autónomas en el marco teórico, con el fin de evitar duplicaciones y precisar elementos que deberán emplearse en el diseño y la evaluación del proyecto.

#### 7.2.1 ESTADO INTERNO INFERIDO Y CONTEXTO OPERACIONAL

**Estado interno inferido.** Es la estimación del comportamiento o condición de un sistema a partir de las señales externas que produce. No corresponde a una lectura directa y completa del sistema: se construye relacionando valores, acontecimientos e interacciones observables. En este proyecto, será la interpretación provisional obtenida del análisis conjunto de métricas, registros y trazas; por tanto, dependerá de la cobertura y calidad de esas señales y no se presentará como una descripción absoluta de lo ocurrido [1], [15].

**Contexto operacional.** Es el conjunto de datos que permite interpretar una observación dentro de las condiciones en que fue generada, como el servicio, la versión, la carga, el instante, la configuración o la tarea ejecutada. Una misma variación puede tener significados distintos según ese contexto. La literatura industrial resalta que la falta de metadatos dificulta correlacionar información, mientras la telemetría con semántica explícita facilita establecer relaciones consistentes [15], [16]. En el proyecto, este contexto acompañará los patrones y limitará las conclusiones a los escenarios evaluados.

#### 7.2.2 CADENA DE PROPAGACIÓN Y GRANULARIDAD DE LOCALIZACIÓN

**Cadena de propagación.** Es una secuencia de componentes y manifestaciones mediante la cual una condición observada en una parte del sistema aparece posteriormente asociada con efectos en otras partes conectadas. La cadena organiza dependencias y precedencias útiles para examinar un incidente, pero no demuestra causalidad por sí sola. Los modelos gráficos y los marcos de evaluación operativa utilizan este tipo de recorrido para representar cómo una alteración puede extenderse entre servicios [4], [14]. En la investigación se empleará, si los datos lo permiten, para contextualizar patrones y posibles componentes relacionados.

**Granularidad de localización.** Es el nivel de detalle con el que un método señala dónde se concentra una condición de interés. Puede referirse al sistema completo, a un servicio, a una instancia, a un recurso o a un indicador. Las revisiones y bancos de prueba muestran que los resultados cambian según la unidad escogida y que no es equivalente localizar un servicio a identificar un indicador concreto [10], [21]. Por ello, el proyecto deberá declarar la granularidad evaluada y evitar conclusiones más precisas que los datos de referencia disponibles.

#### 7.2.3 PLANTILLA DE REGISTRO Y SEGMENTO DE TRAZA

**Plantilla de registro.** Es la estructura estable extraída de un mensaje de registro después de separar sus partes constantes de valores variables, como identificadores, direcciones o tiempos. Las plantillas permiten agrupar mensajes semejantes y reducir la variabilidad textual, pero pueden perder información o dejar de generalizar cuando cambia el software [3]. Para el flujo propuesto, una plantilla será una posible transformación de los registros, cuya utilidad deberá compararse con otras representaciones y cuya relación con el mensaje original deberá conservarse.

**Segmento de traza.** Es la unidad que representa una operación individual dentro del recorrido distribuido de una solicitud. Contiene información temporal y atributos del componente que ejecutó la operación, y se relaciona con otros segmentos para reconstruir el recorrido. DeepTraLog utiliza identificadores compartidos para vincular estas unidades con registros asociados [17]. En el proyecto, los segmentos podrán aportar relaciones entre servicios y referencias temporales, siempre que la instrumentación y la cobertura de las trazas sean suficientes [1], [17].

#### 7.2.4 CORRESPONDENCIA SEMÁNTICA Y VENTANA DE CORRELACIÓN

**Correspondencia semántica.** Es la verificación de que campos procedentes de fuentes distintas representan conceptos compatibles, con significado, tipo, unidad y alcance comparables. La coincidencia de nombres no garantiza equivalencia; por ejemplo, dos valores denominados «duración» pueden medir etapas o unidades diferentes. El enfoque *schema-first* propone explicitar esa información antes de correlacionar señales [16]. Para esta investigación, la correspondencia semántica será una condición del flujo multimodal y deberá documentarse antes de fusionar atributos.

**Ventana de correlación.** Es un intervalo temporal definido para agrupar o relacionar observaciones que podrían pertenecer a un mismo contexto de ejecución. Su amplitud determina qué acontecimientos se consideran próximos: una ventana demasiado estrecha puede separar información relacionada y una demasiado amplia puede reunir coincidencias irrelevantes. Kaiju y MSTGAD muestran alternativas para operar sobre flujos y dependencias temporales [11], [18]. El proyecto deberá justificar la ventana utilizada según la frecuencia de cada señal y comprobar su efecto en los patrones reconocidos.

#### 7.2.5 REGLA DE DECISIÓN Y ACTUALIZACIÓN DEL MODELO

**Regla de decisión.** Es el criterio que transforma variables observadas o una salida numérica en una categoría, prioridad o indicación operativa. Puede formularse explícitamente mediante condiciones y umbrales o aprenderse a partir de datos. Las reglas explícitas son comunes por su costo y facilidad de soporte, aunque dependen de parámetros y relaciones definidos por expertos [20]. En el proyecto, toda regla aplicada después del método deberá declararse para distinguir el patrón producido por el modelo de la forma en que se presenta o clasifica su resultado.

**Actualización del modelo.** Es el proceso de ajustar parámetros, datos de entrenamiento o criterios de inferencia cuando cambia el sistema o se incorpora nueva evidencia. No equivale necesariamente a aprendizaje continuo: puede ejecutarse periódicamente y bajo control experimental. Las revisiones señalan que muchos enfoques se entrenan fuera de línea y que la adaptación sigue siendo una limitación [1]–[3]. La investigación no promete actualización automática, pero deberá registrar la versión del modelo y las condiciones bajo las cuales sería necesario volver a ajustarlo.

#### 7.2.6 DERIVA DE CONCEPTO Y DESFASE TEMPORAL

**Deriva de concepto.** Es el cambio, a lo largo del tiempo, de la relación entre los datos observados y el comportamiento que un modelo intenta reconocer. Puede aparecer cuando se modifican versiones, cargas, configuraciones o patrones de uso, de modo que una representación previamente válida pierde capacidad descriptiva. La literatura reporta dificultades de adaptación y generalización frente a sistemas cambiantes [1]–[3]. En el proyecto, la deriva se tratará como una limitación: los resultados solo serán válidos para los periodos y condiciones incluidos en la validación.

**Desfase temporal.** Es la diferencia entre los tiempos registrados por fuentes o componentes que deberían relacionarse. Puede originarse por relojes no sincronizados, frecuencias de muestreo distintas, retrasos de transmisión o momentos de persistencia diferentes. Este desfase puede impedir que una métrica, un registro y una traza del mismo contexto queden asociados correctamente [16], [22]. El flujo deberá identificarlo y aplicar criterios de alineación documentados antes de construir la representación conjunta.

#### 7.2.7 ATRIBUCIÓN DE CARACTERÍSTICAS Y ERROR DE ATRIBUCIÓN

**Atribución de características.** Es la asignación de una contribución o relevancia a las variables de entrada respecto de un resultado producido por el método. Su finalidad es indicar qué elementos influyeron en una detección o puntuación, pero esa asignación puede describir solo el comportamiento aproximado del modelo y no una causa real del sistema. Las taxonomías de detección explicable diferencian el mecanismo, el alcance y el momento en que se genera una explicación [12]. El proyecto deberá vincular las atribuciones con señales y acontecimientos verificables.

**Error de atribución.** Es la diferencia entre la relevancia asignada por un mecanismo explicativo y una referencia considerada válida, como variables señaladas por expertos o conocidas en un escenario controlado. Sipple y Youssef proponen esta medida para evaluar explicaciones en detección no supervisada de anomalías [13]. En esta investigación podrá emplearse, si existen datos de referencia adecuados, para valorar la fidelidad de la evidencia interpretable y evitar asumir que una explicación es correcta solo porque parece comprensible.

#### 7.2.8 TRIAJE OPERATIVO Y CONFIANZA OPERATIVA

**Triaje operativo.** Es la priorización inicial de patrones, alertas o evidencias según su relevancia para una tarea de monitorización. Su propósito es orientar qué debe examinarse primero, no resolver automáticamente el incidente. Los marcos con agentes separan tareas y resultados, mientras los estudios con profesionales reportan saturación de información y dificultad para correlacionarla [14], [15]. En el prototipo, el triaje podrá expresarse mediante ordenamientos o agrupaciones únicamente si el método y los datos de referencia permiten justificarlos.

**Confianza operativa.** Es el grado de respaldo que un usuario o evaluador puede otorgar a un resultado para emplearlo dentro de una decisión concreta. No depende solo del desempeño estadístico: también requiere evidencia comprensible, consistencia, conocimiento de las limitaciones y posibilidad de verificar el resultado. La literatura de explicabilidad y los estudios industriales relacionan la opacidad y las alertas poco útiles con mayor carga de revisión [12], [15], [20]. El proyecto no medirá aceptación humana, pero podrá examinar condiciones técnicas que favorezcan un uso justificado.

#### 7.2.9 PROVENIENCIA DE DATOS Y TRAZABILIDAD DEL RESULTADO

**Proveniencia de datos.** Es el registro del origen de una observación y de las transformaciones aplicadas antes de utilizarla. Incluye la fuente, el momento de adquisición, la versión del esquema, las operaciones de limpieza y las fusiones realizadas. Los enfoques orientados a eventos y a esquemas explícitos muestran que conservar este contexto es necesario para relacionar señales heterogéneas [11], [16]. En el proyecto, la proveniencia permitirá reproducir la representación y determinar qué datos respaldan cada ejecución del método.

**Trazabilidad del resultado.** Es la capacidad de seguir una salida del método hasta las observaciones, transformaciones y criterios que participaron en su producción. Se diferencia de la proveniencia porque comienza en el resultado y reconstruye hacia atrás la evidencia que lo sustenta. Esta capacidad contribuye a evaluar explicaciones y a detectar discrepancias entre el criterio del modelo y la interpretación esperada [12], [13]. La extensión deberá conservar referencias suficientes para que los patrones presentados puedan examinarse en sus fuentes.

#### 7.2.10 INYECCIÓN DE FALLOS Y ORÁCULO DE EVALUACIÓN

**Inyección de fallos.** Es la introducción deliberada y controlada de una condición de fallo o degradación para observar sus efectos y generar datos de evaluación. Debe especificar el tipo de condición, el componente intervenido, el momento y el mecanismo utilizado. AIOpsLab y RCAEval emplean procedimientos reproducibles para preparar escenarios y telemetría con condiciones conocidas [9], [21]. En la investigación, esta técnica podrá utilizarse en sistemas locales siempre que corresponda al alcance definido para los patrones y no se confunda con una reproducción completa de producción.

**Oráculo de evaluación.** Es la referencia que determina cuál debería ser el resultado correcto o aceptable para una tarea experimental. Puede consistir en etiquetas, acontecimientos conocidos, componentes intervenidos, secuencias esperadas o criterios de puntuación. ITBench y RCAEval muestran la necesidad de separar la tarea, el dato de referencia y la medida aplicada [14], [21]. El proyecto deberá definir oráculos distintos para desempeño, interpretabilidad y utilidad, pues una única etiqueta no permite validar simultáneamente las cuatro variables tecnológicas.

## Referencias

[1] L. Zhang et al., “A survey of AIOps in the era of large language models,” arXiv preprint arXiv:2507.12472, Jul. 2025, doi: 10.48550/arXiv.2507.12472.

[2] J. Diaz-de-Arcaya, A. I. Torre-Bastida, G. Zárate, R. Miñón, and A. Almeida, “A joint study of the challenges, opportunities, and roadmap of MLOps and AIOps: A systematic survey,” ACM Comput. Surv., vol. 56, no. 4, Art. no. 84, pp. 1–30, Oct. 2023, doi: 10.1145/3625289.

[3] M. Landauer, S. Onder, F. Skopik, and M. Wurzenberger, “Deep learning for anomaly detection in log data: A survey,” Mach. Learn. Appl., vol. 12, Art. no. 100470, Jun. 2023, doi: 10.1016/j.mlwa.2023.100470.

[4] Á. Brandón, M. Solé, A. Huélamo, D. Solans, M. S. Pérez, and V. Muntés-Mulero, “Graph-based root cause analysis for service-oriented and microservice architectures,” J. Syst. Softw., vol. 159, Art. no. 110432, Jan. 2020, doi: 10.1016/j.jss.2019.110432.

[5] C. Lee, T. Yang, Z. Chen, Y. Su, and M. R. Lyu, “Eadro: An end-to-end troubleshooting framework for microservices on multi-source data,” in Proc. 45th IEEE/ACM Int. Conf. Softw. Eng. (ICSE), 2023, pp. 1750–1762, doi: 10.1109/ICSE48619.2023.00150.

[6] S. Zhang et al., “Robust failure diagnosis of microservice system through multimodal data,” IEEE Trans. Serv. Comput., vol. 16, no. 6, pp. 3851–3864, Nov.–Dec. 2023, doi: 10.1109/TSC.2023.3290018.

[7] C. Zhao et al., “Robust multimodal failure detection for microservice systems,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discov. Data Min. (KDD), 2023, pp. 5639–5649, doi: 10.1145/3580305.3599902.

[8] G. Yu, P. Chen, Y. Li, H. Chen, X. Li, and Z. Zheng, “Nezha: Interpretable fine-grained root causes analysis for microservices on multi-modal observability data,” in Proc. 31st ACM Joint Eur. Softw. Eng. Conf. Symp. Found. Softw. Eng. (ESEC/FSE), 2023, pp. 553–565, doi: 10.1145/3611643.3616249.

[9] Y. Chen et al., “AIOpsLab: A holistic framework to evaluate AI agents for enabling autonomous clouds,” Proc. Mach. Learn. Syst., vol. 7, 2025. [Online]. Available: https://proceedings.mlsys.org/paper_files/paper/2025/hash/d1f9e4a9f109b6e8b75ed362736f22ec-Abstract-Conference.html

[10] S. Zhang et al., “Failure diagnosis in microservice systems: A comprehensive survey and analysis,” ACM Trans. Softw. Eng. Methodol., vol. 35, no. 1, Art. no. 2, pp. 1–55, Dec. 2025, doi: 10.1145/3715005.

[11] M. Scrocca, R. Tommasini, A. Margara, E. Della Valle, and S. Sakr, “The Kaiju project: Enabling event-driven observability,” in Proc. 14th ACM Int. Conf. Distributed Event-Based Syst. (DEBS), 2020, pp. 85–96, doi: 10.1145/3401025.3401740.

[12] Z. Li, Y. Zhu, and M. van Leeuwen, “A survey on explainable anomaly detection,” ACM Trans. Knowl. Discov. Data, vol. 18, no. 1, Art. no. 23, pp. 1–54, Jan. 2024, doi: 10.1145/3609333.

[13] J. Sipple and A. Youssef, “A general-purpose method for applying explainable AI for anomaly detection,” in Foundations of Intelligent Systems, Lecture Notes in Computer Science, vol. 13515, 2022, pp. 162–174, doi: 10.1007/978-3-031-16564-1_16.

[14] S. Jha et al., “ITBench: Evaluating AI agents across diverse real-world IT automation tasks,” in Proc. 42nd Int. Conf. Mach. Learn. (ICML), Proc. Mach. Learn. Res., vol. 267, pp. 27134–27197, 2025. [Online]. Available: https://proceedings.mlr.press/v267/jha25a.html

[15] S. Niedermaier, F. Koetter, A. Freymann, and S. Wagner, “On observability and monitoring of distributed systems: An industry interview study,” in Service-Oriented Computing, Lecture Notes in Computer Science, vol. 11895, 2019, pp. 36–52, doi: 10.1007/978-3-030-33702-5_3.

[16] Y. Shkuro, B. Renard, and A. Singh, “Positional paper: Schema-first application telemetry,” arXiv preprint arXiv:2206.11380, Jun. 2022, doi: 10.48550/arXiv.2206.11380.

[17] C. Zhang, X. Peng, C. Sha, K. Zhang, Z. Fu, X. Wu, Q. Lin, and D. Zhang, “DeepTraLog: Trace-log combined microservice anomaly detection through graph-based deep learning,” in Proc. 44th Int. Conf. Softw. Eng. (ICSE), 2022, pp. 623–634, doi: 10.1145/3510003.3510180.

[18] J. Huang, Y. Yang, H. Yu, J. Li, and X. Zheng, “Twin graph-based anomaly detection via attentive multi-modal learning for microservice system,” in Proc. 38th IEEE/ACM Int. Conf. Automated Softw. Eng. (ASE), 2023, pp. 66–78, doi: 10.1109/ASE56229.2023.00138.

[19] C. Hou, T. Jia, Y. Wu, Y. Li, and J. Han, “Diagnosing performance issues in microservices with heterogeneous data source,” in Proc. IEEE Int. Conf. Parallel Distrib. Process. Appl., Big Data Cloud Comput., Sustain. Comput. Commun., Social Comput. Netw. (ISPA/BDCloud/SocialCom/SustainCom), 2021, pp. 493–500, doi: 10.1109/ISPA-BDCloud-SocialCom-SustainCom52081.2021.00074.

[20] M. Steidl, B. Dornauer, M. Felderer, R. Ramler, M.-C. Racasan, and M. Gattringer, “How industry tackles anomalies during runtime: Approaches and key monitoring parameters,” in Proc. 50th Euromicro Conf. Softw. Eng. Adv. Appl. (SEAA), 2024, pp. 364–372, doi: 10.1109/SEAA64295.2024.00062.

[21] L. Pham, H. Zhang, H. Ha, F. Salim, and X. Zhang, “RCAEval: A benchmark for root cause analysis of microservice systems with telemetry data,” in Companion Proc. ACM Web Conf. (WWW Companion), 2025, pp. 777–780, doi: 10.1145/3701716.3715290.

[22] A. Bakhtin, J. Nyyssölä, Y. Wang, N. Ahmad, K. Ping, M. Esposito, M. Mäntylä, and D. Taibi, “LO2: Microservice API anomaly dataset of logs and metrics,” in Proc. 21st Int. Conf. Predictive Models Data Analytics Softw. Eng. (PROMISE), 2025, pp. 1–10, doi: 10.1145/3727582.3728682.
