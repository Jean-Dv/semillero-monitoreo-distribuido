# Deriva entre runs y representación temporal local

## 1. Propósito y restricción experimental

Este informe registra la iteración posterior a la comparación exploratoria de
niveles absolutos. Se mantienen sin cambios el escenario
`astronomy-ad-failure-v1`, la cohorte de once servicios, las tres runs, sus
particiones y los tres detectores comparables. La iteración responde a dos
preguntas acotadas: cuánto cambia el régimen normal entre runs y si representar
cada observación respecto de una referencia normal de su propia run produce
una señal más estable.

Antes de calcular resultados se congeló
`local_reference_manifest_v1`. El manifiesto fija dieciocho instantes normales
iniciales por servicio y run, las transformaciones, los modelos, las rejillas de
hiperparámetros y el orden de selección. Los 594 registros de referencia —198
por partición— se excluyeron del ajuste, de la calibración de puntajes, de la
selección y de la evaluación. Las doce variantes quedaron seleccionadas con
validación antes de consultar prueba.

Este diseño añade una condición de uso: una ejecución futura deberá declarar
un periodo inicial normal. La referencia no utiliza ventanas de fallo, pero su
disponibilidad no puede asumirse en cualquier entorno operativo.

## 2. Deriva del régimen normal

Se compararon entrenamiento con validación y entrenamiento con prueba para cada
combinación de once servicios y dieciocho variables. Los valores de magnitud se
transformaron con `log1p` cuando correspondía. La distancia de
Kolmogorov-Smirnov (KS) describe cambios distributivos; el desplazamiento de
mediana se expresa respecto del IQR de entrenamiento, con desviación estándar y
uno como respaldos; la tercera medida compara las tasas de ausencia.

| Comparación | Pares | Mediana KS | KS ≥ 0,20 | Desplazamiento ≥ 1 | Ausencia Δ ≥ 0,10 |
|---|---:|---:|---:|---:|---:|
| Validación frente a entrenamiento | 198 | 0,121 | 0,180 | 0,057 | 0,101 |
| Prueba frente a entrenamiento | 198 | 0,123 | 0,278 | 0,072 | 0,101 |

La mediana global oculta cambios concentrados. El uso de memoria obtuvo KS de
1,0 en varios servicios, lo que indica distribuciones empíricas sin
solapamiento en esas muestras. En prueba también cambiaron las latencias p50,
p95 y p99 de `ad`. Estos resultados demuestran cambio entre las muestras
normales observadas, pero no permiten atribuirlo a una causa concreta ni
determinar por sí solos si se trata de deriva del sistema, de carga o del
proceso de medición.

## 3. Representación evaluada

Para cada combinación de run y servicio se calculó la mediana y el IQR con los
dieciocho registros de referencia. Cuando el IQR fue nulo se usó la desviación
estándar y, si la variable permaneció constante o ausente, una escala unitaria.
Cada variable original produjo dos componentes:

1. nivel local: diferencia entre el valor actual y la mediana de referencia,
   dividida por la escala local;
2. cambio temporal sin anticipación: diferencia frente al valor cronológico
   inmediatamente anterior del mismo servicio y run, dividida por la escala
   local.

Ambos componentes se limitaron al intervalo `[-20, 20]`. «Sin anticipación»
significa que la transformación usa solo información disponible hasta la
ventana actual; no expresa una relación causal entre la variable y el fallo.
Después de retirar la referencia quedaron 429 observaciones normales para
ajuste, 1067 para validación y 1056 para prueba. La prueba contiene 39 instantes
normales y 57 de fallo; por ello la prevalencia positiva global es 0,594, no
0,500. Para la tarea del servicio afectado, la prevalencia es 0,117.

## 4. Resultados de prueba

La tabla muestra las variantes más informativas. AP es precisión promedio. FP
indica cuántos de los 39 instantes normales se marcaron como fallo con el umbral
elegido en validación. La referencia aleatoria de localización entre once
servicios es aproximadamente 0,275 para MRR y 0,273 para Hit@3.

| Método | Señales | AP sistema | FP | AP afectado | MRR | Hit@3 |
|---|---|---:|---:|---:|---:|---:|
| Isolation Forest | Trazas | 0,645 | 39 | 0,098 | 0,167 | 0,070 |
| Reglas robustas | Trazas | 0,644 | 39 | 0,095 | 0,189 | 0,105 |
| Isolation Forest | Trimodal | 0,624 | 39 | 0,098 | 0,157 | 0,088 |
| Reglas robustas | Logs | 0,608 | 38 | 0,135 | 0,289 | 0,298 |
| Isolation Forest | Métricas | 0,602 | 39 | 0,090 | 0,172 | 0,123 |
| One-Class SVM | Trimodal | 0,606 | 37 | 0,079 | 0,128 | 0,018 |

La AP global quedó entre 0,580 y 0,645. Su máximo supera la prevalencia en
0,051, pero no produjo un umbral útil: las variantes registraron entre 37 y 39
falsos positivos sobre 39 instantes normales. El F1 global entre 0,745 y 0,755
de varias variantes se explica por predecir casi todos los instantes como
positivos y no debe interpretarse como detección operativa satisfactoria.

La mejor AP del servicio afectado fue 0,145 con reglas sobre métricas, apenas
0,027 por encima de la prevalencia. La mejor MRR fue 0,289 con reglas sobre
logs, próxima a la referencia aleatoria. La representación trimodal no dominó
las ablaciones en ninguna de las tres tareas.

## 5. Interpretación y amenazas a la validez

La comparación anterior tenía prevalencia global 0,500; esta iteración tiene
0,594 porque reserva dieciocho instantes normales. Por tanto, el aumento bruto
de AP frente a v1 no debe interpretarse completo como una mejora de
representación. La comparación pertinente es la distancia respecto de la
prevalencia de cada diseño y la transferencia del umbral.

Además, en las tres runs la fase de fallo ocurre después de la fase normal. Un
puntaje que aumenta con el tiempo puede ordenar el fallo por encima del normal
sin reconocer `adFailure`. La AP mayor, combinada con umbrales inestables y una
localización débil, es compatible con ese factor temporal. Esta es una
inferencia metodológica y no una causa demostrada por los datos actuales.
Separar condición y tiempo requerirá runs de control sin fallo, orden de fases
alternado cuando sea seguro o condiciones introducidas en momentos distintos.

Los resultados continúan limitados a una run por partición, un tipo de fallo y
un sistema. La misma run de prueba ya fue consultada en dos iteraciones
exploratorias; no deberá reutilizarse para una selección confirmatoria.

## 6. Decisión y siguiente ciclo

La evidencia no permite seleccionar reglas robustas, Isolation Forest ni
One-Class SVM. La referencia local reduce conceptualmente la dependencia de
niveles absolutos, pero no resuelve la transferencia del umbral, la
identificación del servicio afectado ni la ventaja de la unión trimodal.

El siguiente ciclo debe cerrar primero el diseño experimental, no ampliar la
búsqueda de hiperparámetros sobre estas mismas runs:

1. definir el patrón verificable de `adFailure` por modalidad y la salida
   primaria, distinguiendo detección global de localización;
2. incorporar controles temporales que desacoplen fase y transcurso de la run;
3. fijar una nueva cohorte confirmatoria con runs independientes y, al menos,
   una condición adicional;
4. conservar el periodo de referencia local solo si el protocolo operativo
   puede garantizarlo;
5. evaluar características secuenciales únicamente con el nuevo protocolo y
   sin volver a ajustar decisiones con la prueba ya observada.

Los programas, el manifiesto y las instrucciones de reproducción están en
`experiments/algorithm_comparison/`. Los informes numéricos detallados se
mantienen locales, igual que los datos de las runs.
