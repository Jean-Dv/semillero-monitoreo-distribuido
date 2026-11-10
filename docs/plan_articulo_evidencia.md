# Plan del artículo y mapa de evidencia

**Proyecto:** Reconocimiento interpretable de patrones en la monitorización de sistemas distribuidos  
**Estado:** Plan de transición desde la propuesta del ciclo 6 hacia el artículo empírico  
**Fuente de alcance:** `AGENTS.md` y `docs/propuesta_investigacion.md`

## 1 Configuración del manuscrito

| Parámetro | Decisión vigente |
|---|---|
| Tipo de manuscrito | Artículo de ingeniería y ciencia del diseño con validación experimental |
| Pregunta | ¿De qué manera un método interpretable de reconocimiento de patrones en métricas, registros y trazas puede apoyar la toma de decisiones en la monitorización de sistemas distribuidos? |
| Contribución central prevista | Método interpretable; su alcance definitivo dependerá de la evaluación |
| Artefacto | Flujo multimodal, método, componente de procesamiento y extensión para Grafana |
| Metodología general | DSRM |
| Entorno de validación | Sistemas controlados desplegados localmente |
| Variables | Integración multimodal, desempeño, interpretabilidad y utilidad |
| Reproducibilidad | Control transversal, no quinta variable |
| Citación | Numérica, estilo IEEE, claves [1]--[24] vigentes |

El artículo deberá conservar la diferencia entre tres estados epistémicos:

1. **Evidencia bibliográfica:** afirmaciones sustentadas por el corpus.
2. **Decisión de diseño:** elección que deberá justificarse y registrarse, pero que no constituye un hallazgo de la literatura.
3. **Resultado empírico:** afirmación que solo podrá redactarse después de ejecutar el protocolo.

## 2 Estructura prevista del artículo final

### 2.1 Título, resumen y palabras clave

**Función.** Delimitar el problema, el artefacto, el método de investigación y el alcance de la validación.

**Afirmaciones permitidas antes de la evaluación.** El estudio diseña y evaluará un artefacto; integra las tres señales; adopta DSRM; restringe la validación al entorno local controlado.

**Afirmaciones reservadas.** No se indicará que el método mejora decisiones, supera líneas base, generaliza o identifica causas hasta contar con resultados.

**Criterio de cierre.** El resumen final deberá informar problema, método, entorno, resultados cuantificados y límites sin introducir afirmaciones ausentes del cuerpo.

### 2.2 Introducción

**Función.** Construir la secuencia problema, brecha, pregunta, contribución y alcance.

**Afirmaciones centrales.** La escala y las dependencias dificultan el análisis [1], [10]; la inspección manual y las reglas presentan límites [3], [20]; relacionar las tres señales exige semántica, identificadores, sincronización y transformaciones [11], [16]--[19], [22]; los profesionales reportan saturación y carga de correlación [15], [20].

**Evidencia disponible.** E01--E20, E32, E40--E42, E49 y E57 de la matriz.

**Evidencia faltante.** Ninguna para justificar el problema internacional. Si se añade pertinencia colombiana, se requerirán fuentes nacionales verificables.

**Criterio de cierre.** La introducción termina con la pregunta acordada, la contribución formulada como expectativa y los límites local, experimental y no causal.

### 2.3 Fundamentos y trabajo relacionado

Esta sección sintetizará los diez núcleos del marco teórico en cuatro bloques para evitar una revisión enciclopédica.

#### 2.3.1 Observabilidad y dependencias distribuidas

**Afirmaciones.** Las señales permiten inferir parcialmente el estado; las dependencias aportan contexto de propagación sin demostrar causalidad.

**Evidencia disponible.** [1], [4], [10], [15]; E03, E21--E24, E32 y E40--E41.

**Vacío.** Falta caracterizar la arquitectura y las dependencias del sistema que se seleccione.

**Criterio de cierre.** Cada concepto deberá conectarse con una decisión observable del diseño experimental.

#### 2.3.2 Representación conjunta y calidad de datos

**Afirmaciones.** La integración requiere procesamiento por modalidad, correspondencia semántica, alineación temporal, tratamiento de ausencias y proveniencia.

**Evidencia disponible.** [11], [16]--[19], [22]; E35--E36, E42--E45, E48--E49.

**Vacíos.** Deben definirse identificadores, relojes, ventanas, transformaciones, estrategia de fusión y reglas de calidad para las fuentes concretas.

**Criterio de cierre.** El artículo incluye un contrato de datos y explica por qué la representación elegida conserva semántica y trazabilidad.

#### 2.3.3 Reconocimiento de patrones e interpretabilidad

**Afirmaciones.** No existe una técnica universal; visualización, explicación *post hoc* e interpretabilidad no son equivalentes.

**Evidencia disponible.** [3], [5]--[8], [12], [13], [17]--[20]; E25--E30, E37--E38 y E43--E46.

**Vacíos.** Falta operacionalizar patrón, seleccionar líneas base, fijar la unidad de salida y escoger métricas de fidelidad, correspondencia, complejidad y estabilidad.

**Criterio de cierre.** La selección del método se deriva de una comparación ejecutada bajo el mismo protocolo y no de una preferencia previa.

#### 2.3.4 Apoyo a decisiones y validación reproducible

**Afirmaciones.** Detección, clasificación, localización y posible causa son tareas diferentes; la evaluación con agentes no equivale a utilidad humana.

**Evidencia disponible.** [9], [10], [14], [15], [20], [21]; E31--E34, E39--E41 y E46--E47.

**Vacíos.** Faltan las tareas, respuestas aceptables, capacidades permitidas, datos de referencia y condición de comparación para los agentes.

**Criterio de cierre.** El artículo especifica qué decisión se apoya, qué puede observar el agente y qué inferencias permanecen fuera del alcance.

### 2.4 Metodología de investigación

**Función.** Explicar DSRM, las unidades, el protocolo, las variables y los controles de validez.

**Afirmaciones.** DSRM es la única metodología general [23]; CRISP-ML(Q) y MLOps aportan prácticas técnicas sin constituir metodologías concurrentes [2], [24].

**Evidencia disponible.** E58--E63.

**Vacíos.** Faltan criterios numéricos o reglas de aceptación, número de repeticiones, estrategia de partición, análisis estadístico y reglas de exclusión.

**Criterio de cierre.** Cada objetivo queda vinculado con una medida, un dato de referencia, una prueba y un criterio de avance o cierre.

### 2.5 Diseño e implementación del artefacto

**Función.** Documentar requisitos, arquitectura, contratos y decisiones de implementación.

**Contenido obligatorio.** Fuentes de telemetría; flujo por modalidad; identificadores y tiempo; representación conjunta; método y líneas base; interfaz del componente de procesamiento; frontera con Grafana; proveniencia y versiones.

**Evidencia bibliográfica.** [11], [16]--[19], [22].

**Evidencia que debe generar el proyecto.** Esquemas, diccionario de datos, manifiestos, pruebas de componentes, registros de decisiones y mediciones de calidad del flujo.

**Criterio de cierre.** Una ejecución controlada produce un resultado rastreable desde la extensión hasta las observaciones de origen.

### 2.6 Demostración y configuración experimental

**Función.** Mostrar el funcionamiento integral sin confundirlo con efectividad general.

**Contenido obligatorio.** Sistema, versión, topología, carga, instrumentación, condición, ventana, repetición, semillas, datos de referencia y paquete de ejecución.

**Evidencia bibliográfica.** [9], [14], [21].

**Evidencia que debe generar el proyecto.** Matriz de escenarios, ejecuciones de referencia, condiciones introducidas, telemetría trimodal y bitácoras completas.

**Criterio de cierre.** Existen ejecuciones integrales repetibles para el comportamiento de referencia y al menos una condición de interés.

### 2.7 Evaluación y resultados

La sección se organizará por variable, no por componente de software.

| Subsección | Resultado que deberá informar | Evidencia mínima | Criterio de cierre |
|---|---|---|---|
| Integración | Cobertura, correspondencia, desfase, ausencias y trazabilidad | Mediciones por modalidad, escenario y repetición | Se conoce qué proporción de observaciones puede relacionarse y por qué falla el resto |
| Desempeño | Capacidad para reconocer el patrón y costo de inferencia | Líneas base, prueba reservada, variabilidad y errores | La métrica corresponde a la tarea y se reporta sin seleccionar solo escenarios favorables |
| Interpretabilidad | Fidelidad, correspondencia, estabilidad y complejidad | Explicaciones, perturbaciones y eventos de referencia | La evidencia mostrada refleja el comportamiento del método dentro de una tolerancia definida |
| Utilidad | Cumplimiento, exactitud, tiempo y consistencia de tareas | Agentes, condición de comparación y respuestas de referencia | Se delimita el apoyo instrumental sin inferir aceptación humana |
| Análisis de errores | Fallos por modalidad, transformación, condición y etapa | Casos negativos y mixtos | Los errores modifican o limitan la contribución declarada |

No se redactarán cifras, superioridades ni hallazgos antes de ejecutar estas pruebas.

### 2.8 Discusión

**Función.** Responder la pregunta y relacionar los resultados con la literatura.

**Preguntas de control.** ¿Qué patrón pudo reconocerse y bajo qué condiciones? ¿Qué aportó cada modalidad? ¿La evidencia fue fiel? ¿Qué tareas apoyó? ¿Qué explicaciones alternativas permanecen? ¿Qué parte del resultado depende del sistema local?

**Criterio de cierre.** Cada afirmación de contribución enlaza un resultado propio, un antecedente y un límite. Una asociación no se convierte en causalidad.

### 2.9 Conclusiones

**Función.** Responder la pregunta con el nivel de fuerza permitido por los resultados.

**Criterio de cierre.** No se introduce evidencia nueva; se distinguen contribución demostrada, resultado negativo o mixto, límites y siguiente validación necesaria.

### 2.10 Materiales de reproducibilidad y declaraciones

El paquete final deberá incluir disponibilidad de datos y código, versiones, instrucciones de reproducción, diccionarios y contratos, configuración, semillas, resultados por repetición, exclusiones, ética, financiación, contribuciones de autoría y conflictos de interés.

## 3 Registro de vacíos de evidencia

| ID | Prioridad | Vacío | Tipo | Producto que lo cierra |
|---|---|---|---|---|
| G01 | Crítica | Definición operacional de patrón y tarea | Decisión metodológica | Especificación con ejemplos positivos, negativos y granularidad |
| G02 | Crítica | Sistema, infraestructura y mecanismo de condiciones | Decisión empírica | Protocolo y matriz de escenarios |
| G03 | Crítica | Fuentes trimodales, identificadores, relojes y calidad | Evidencia empírica | Piloto de captura y perfil de datos |
| G04 | Crítica | Datos de referencia y respuestas aceptables | Decisión experimental | Oráculo documentado por escenario |
| G05 | Crítica | Líneas base, particiones, repeticiones y análisis | Diseño experimental | Plan de evaluación congelado antes de la prueba |
| G06 | Alta | Métricas y tolerancias de interpretabilidad | Bibliográfica y metodológica | Protocolo de fidelidad, correspondencia y estabilidad |
| G07 | Alta | Validez de la utilidad medida con agentes | Bibliográfica y experimental | Tareas, condición de comparación y límite explícito del proxy |
| G08 | Alta | Frontera técnica y capacidades de la extensión | Evidencia técnica | Contrato de API, esquema de resultados y pruebas de integración |
| G09 | Media | Selección de fusión, ventanas y ausencias | Evidencia comparativa | Ablaciones y análisis de sensibilidad |
| G10 | Condicional | Contexto colombiano | Bibliográfica | Fuentes nacionales, solo si se formulan afirmaciones nacionales |

## 4 Orden de cierre recomendado

1. Cerrar G01 y G04 para saber qué salida se evaluará.
2. Cerrar G02 y ejecutar el piloto G03.
3. Definir G05 con base en el patrón y los datos disponibles.
4. Cerrar G06 y G07 antes de implementar la evaluación.
5. Diseñar G08 en paralelo con el componente de procesamiento.
6. Resolver G09 mediante experimentos, no mediante una decisión previa.

La selección del algoritmo ocurrirá después de los pasos 1--3. Elegirlo antes invertiría la relación entre problema, datos, método y evaluación establecida por DSRM.

## 5 Afirmaciones que permanecen prohibidas hasta contar con evidencia

- El método mejora la toma de decisiones.
- La representación trimodal supera siempre a las modalidades individuales.
- El método identifica causas raíz o demuestra causalidad.
- La explicación es interpretable porque se visualiza.
- La evaluación con agentes demuestra usabilidad o aceptación humana.
- Los resultados se generalizan a cualquier sistema distribuido.
- Una familia concreta de modelos es la solución requerida.

## 6 Criterio para iniciar la redacción de resultados

La sección de resultados podrá abrirse cuando existan, como mínimo, una definición de patrón aprobada, un protocolo de evaluación congelado, una matriz de escenarios, una captura trimodal validada, datos de referencia, líneas base ejecutables y al menos una repetición integral reconstruible desde sus artefactos. Antes de ese punto, el manuscrito deberá denominar sus salidas «previstas», «candidatas» o «por evaluar».
