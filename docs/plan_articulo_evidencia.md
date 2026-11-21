# Plan del artículo y mapa de evidencia

**Proyecto:** Reconocimiento interpretable de patrones en la monitorización de sistemas distribuidos  
**Estado:** Transición al artículo empírico con evidencia de desarrollo y evaluación confirmatoria pendiente
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

El artículo deberá conservar la diferencia entre cuatro estados epistémicos:

1. **Evidencia bibliográfica:** afirmaciones sustentadas por el corpus.
2. **Decisión de diseño:** elección que deberá justificarse y registrarse, pero que no constituye un hallazgo de la literatura.
3. **Evidencia de desarrollo:** medición propia útil para diseñar el artefacto, identificar fallos y congelar decisiones, pero no para formular la conclusión final.
4. **Resultado confirmatorio:** afirmación reservada para la cohorte ciega y el protocolo congelado.

## 2 Estructura prevista del artículo final

### 2.1 Título, resumen y palabras clave

**Función.** Delimitar el problema, el artefacto, el método de investigación y el alcance de la validación.

**Afirmaciones permitidas antes de la evaluación confirmatoria.** El estudio diseña y evaluará un artefacto; integra las tres señales; adopta DSRM; restringe la validación al entorno local controlado; implementó el flujo local, produjo tres runs nominales y utilizó sus resultados como evidencia de desarrollo.

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

**Vacíos.** La detección de condición a nivel de sistema quedó fijada como tarea primaria confirmatoria y se congelaron cinco familias con dos representaciones. Continúa pendiente completar la operacionalización de interpretabilidad, evidencia y utilidad para la decisión.

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

**Estado.** El protocolo ciego fija cuatro celdas, tres repeticiones por celda, población común, reglas de exclusión, remuestreo por run y criterios de admisibilidad. La evaluación de interpretabilidad y utilidad todavía requiere tolerancias y tareas instrumentales completas.

**Criterio de cierre.** Cada objetivo queda vinculado con una medida, un dato de referencia, una prueba y un criterio de avance o cierre.

### 2.5 Diseño e implementación del artefacto

**Función.** Documentar requisitos, arquitectura, contratos y decisiones de implementación.

**Contenido obligatorio.** Fuentes de telemetría; flujo por modalidad; identificadores y tiempo; representación conjunta; método y líneas base; interfaz del componente de procesamiento; frontera con Grafana; proveniencia y versiones.

**Evidencia bibliográfica.** [11], [16]--[19], [22].

**Evidencia generada.** Contratos Bronze, Silver, Gold y Results; `gold_service_window_v2.2`; vistas tabular y secuencial; manifiestos; pruebas de componentes; paquetes por `run_id`; mediciones de calidad y tablero conectado a ClickHouse. El flujo local constituye evidencia de factibilidad, no una selección definitiva frente a AWS Glue.

**Criterio de cierre.** Una ejecución controlada produce un resultado rastreable desde la extensión hasta las observaciones de origen.

### 2.6 Demostración y configuración experimental

**Función.** Mostrar el funcionamiento integral sin confundirlo con efectividad general.

**Contenido obligatorio.** Sistema, versión, topología, carga, instrumentación, condición, ventana, repetición, semillas, datos de referencia y paquete de ejecución.

**Evidencia bibliográfica.** [9], [14], [21].

**Evidencia generada.** Tres ejecuciones nominales con referencia, `adFailure` y recuperación; 7177 observaciones únicas de once servicios; telemetría trimodal y paquetes con manifiesto, cronología, offsets, checkpoints, calidad, logs y checksums. La posición fija de la condición limita su uso a desarrollo.

**Evidencia pendiente.** Doce runs ciegas con tres controles y posiciones temprana, intermedia y tardía, ejecutadas únicamente después de implementar el generador congelado de puntajes.

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

Las cifras de las tres runs ya pueden redactarse en una subsección denominada explícitamente **resultados de desarrollo**. No se presentarán como estimación confirmatoria, superioridad general ni selección del método. La subsección confirmatoria permanecerá sin resultados hasta ejecutar, predecir y revelar el lote ciego.

#### 2.7.1 Evidencia de desarrollo disponible

| Resultado | Observación disponible | Interpretación permitida |
|---|---|---|
| Cohorte Gold | 7177 claves únicas; 2404, 2421 y 2352 observaciones por run | Factibilidad y trazabilidad de la representación para once servicios |
| Líneas base iniciales | AP global entre 0,479 y 0,500 frente a prevalencia 0,500 | Ausencia de generalización útil en esa partición; no selección |
| Deriva normal | KS ≥ 0,20 en 18,0 % de pares de validación y 27,8 % de prueba | Los niveles absolutos cambian entre runs de forma no uniforme |
| Referencia local | Mejor AP global 0,645, pero 39/39 instantes normales positivos; mejor MRR 0,289 | Un mejor ordenamiento no produjo un umbral operativo estable |
| Gradient boosting | AP afectado 0,234, MRR 0,335 y 38/40 falsos positivos normales | Candidato supervisado de desarrollo, no detector aceptado |
| Autoencoder LSTM | AP global 0,697 frente a 0,613; AP afectado 0,332 frente a 0,126; MRR 0,298 frente a 0,275; 20/29 falsos positivos | Candidato temporal principal, todavía con falsas alarmas altas |

Estas poblaciones no siempre coinciden: el autoencoder requiere doce pasos y dispone de menos extremos elegibles. El artículo deberá informar denominadores, prevalencias y reglas temporales junto a cada métrica.

### 2.8 Discusión

**Función.** Responder la pregunta y relacionar los resultados con la literatura.

**Preguntas de control.** ¿Qué patrón pudo reconocerse y bajo qué condiciones? ¿Qué aportó cada modalidad? ¿La evidencia fue fiel? ¿Qué tareas apoyó? ¿Qué explicaciones alternativas permanecen? ¿Qué parte del resultado depende del sistema local?

**Criterio de cierre.** Cada afirmación de contribución enlaza un resultado propio, un antecedente y un límite. Una asociación no se convierte en causalidad.

### 2.9 Conclusiones

**Función.** Responder la pregunta con el nivel de fuerza permitido por los resultados.

**Criterio de cierre.** No se introduce evidencia nueva; se distinguen contribución demostrada, resultado negativo o mixto, límites y siguiente validación necesaria.

### 2.10 Materiales de reproducibilidad y declaraciones

El paquete final deberá incluir disponibilidad de datos y código, versiones, instrucciones de reproducción, diccionarios y contratos, configuración, semillas, resultados por repetición, exclusiones, ética, financiación, contribuciones de autoría y conflictos de interés.

## 3 Registro actualizado de vacíos de evidencia

| ID | Prioridad | Vacío | Estado actual | Producto que lo cierra |
|---|---|---|---|---|
| G01 | Crítica | Definición operacional de patrón y tarea | Parcial: detección de condición es primaria; servicio y localización son secundarias | Ejemplos positivos/negativos y vínculo definitivo con la tarea de decisión |
| G02 | Crítica | Sistema, infraestructura y mecanismo de condiciones | Parcial: Astronomy Shop, entorno local y `adFailure` están implementados | Ejecución válida de `blind_protocol_v1` |
| G03 | Crítica | Fuentes trimodales, identificadores, relojes y calidad | Parcialmente cerrado para once servicios; tres identidades siguen separadas | Informe final de calidad de la cohorte ciega |
| G04 | Crítica | Datos de referencia y respuestas aceptables | Parcial: fases, condición y componente están versionados | Respuestas aceptables para las tareas de decisión y agentes |
| G05 | Crítica | Líneas base, particiones, repeticiones y análisis | Cerrado en diseño: diez variantes y protocolo congelados | Generador ciego implementado y predicciones comprometidas |
| G06 | Alta | Métricas y tolerancias de interpretabilidad | Abierto | Protocolo de fidelidad, correspondencia y estabilidad |
| G07 | Alta | Validez de la utilidad medida con agentes | Abierto | Tareas, condición de comparación y límite explícito del proxy |
| G08 | Alta | Frontera técnica y capacidades de la extensión | Parcial: Gold, Results y Grafana están separados | Contrato de API y pruebas de integración de la extensión |
| G09 | Media | Selección de fusión, ventanas y ausencias | Parcial: métricas y trimodal están congeladas como ablación | Resultados ciegos y análisis de sensibilidad |
| G10 | Condicional | Contexto colombiano | No iniciado y no requerido por el alcance vigente | Fuentes nacionales solo si se formulan afirmaciones nacionales |

## 4 Orden de cierre recomendado

1. Implementar y probar el generador ciego de puntajes contra `confirmatory_manifest_v1` sin modificar sus decisiones científicas.
2. Preparar y ejecutar las doce runs de `blind_protocol_v1`, congelar predicciones y revelar la asignación.
3. Evaluar desempeño y ablaciones en la población común; conservar la conclusión «sin selección» si ningún candidato supera los criterios.
4. Cerrar G06 con una evaluación de explicaciones del candidato admisible, si existe.
5. Implementar G08 y cerrar G07 mediante tareas reproducibles con agentes, sin inferir usabilidad humana.
6. Consolidar discusión, amenazas a la validez, materiales de reproducción y conclusión final.

## 5 Afirmaciones que permanecen prohibidas hasta contar con evidencia

- El método mejora la toma de decisiones.
- La representación trimodal supera siempre a las modalidades individuales.
- El método identifica causas raíz o demuestra causalidad.
- La explicación es interpretable porque se visualiza.
- La evaluación con agentes demuestra usabilidad o aceptación humana.
- Los resultados se generalizan a cualquier sistema distribuido.
- Una familia concreta de modelos es la solución requerida.

## 6 Criterio para redactar resultados

La sección de resultados de desarrollo puede redactarse porque existen un contrato multimodal, tres ejecuciones reconstruibles, datos de referencia y comparaciones ejecutables. Cada cifra deberá etiquetarse como exploratoria o de validación y conservar su población. La sección de resultados confirmatorios solo podrá abrirse cuando las doce runs estén completas, el generador haya producido puntajes para los diez candidatos, las predicciones estén comprometidas por hash y la asignación se revele después de ese compromiso.

## 7 Siguiente ciclo

El siguiente ciclo implementará el generador ciego de puntajes. El artefacto deberá validar el hash de `confirmatory_manifest_v1`, reconstruir los diez `model_id`, ajustar únicamente con los datos históricos permitidos, formar secuencias sin etiquetas de fase y producir puntajes por código opaco, servicio y ventana. También generará `blind_predictions_manifest_v1` con hashes de modelos y archivos. Las pruebas deberán demostrar que no lee `allocation.sealed.json`, `evaluation_reference_v1` ni cronologías de fase durante representación o inferencia.

Solo después de aprobar esas pruebas se autoriza preparar el lote. Este orden evita que errores o decisiones de implementación se resuelvan después de observar nuevas condiciones. Cualquier cambio científico en variables, candidatos, umbrales, tareas o métricas exigirá una nueva versión del manifiesto antes de ejecutar las runs.
