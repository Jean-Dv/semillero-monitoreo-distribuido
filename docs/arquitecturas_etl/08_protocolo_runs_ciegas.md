# Protocolo de runs ciegas para desacoplar tiempo y condición

## Estado y propósito

Este documento define la siguiente cohorte de evaluación y registra su
implementación en el repositorio hermano `AIOpsLab`. El protocolo está listo
para prepararse y ejecutarse, pero las doce runs todavía no se han producido.
Por ello, no contiene resultados ni selecciona un algoritmo.

Las tres runs nominales anteriores tenían siempre la misma secuencia:
operación normal, `adFailure` y recuperación. Esa regularidad deja dos
explicaciones compatibles con una puntuación alta: el método puede reconocer la
condición o puede responder al tiempo transcurrido, la deriva entre periodos o
un cambio acumulativo del entorno. Además, la run de prueba anterior ya fue
consultada en iteraciones exploratorias y no debe reutilizarse como evidencia
confirmatoria.

La nueva cohorte responde a ambos problemas:

1. introduce un control sin falla y desplaza la misma condición a tres momentos
   del horizonte, manteniendo igual duración, carga y configuración; y
2. oculta la asignación al responsable del modelado hasta que sus predicciones
   hayan sido congeladas y resumidas mediante SHA-256.

El cegamiento es procedimental y de una sola parte. El operador que ejecuta la
inyección puede conocer la asignación; el analista y el proceso de modelado no
deben conocerla. Los permisos del archivo sellado reducen exposiciones
accidentales, pero no constituyen cifrado ni protegen frente a un operador con
acceso deliberado al mismo sistema.

## Diseño balanceado

Todas las runs usan cinco minutos de calentamiento y cincuenta minutos de
observación. En las tres celdas intervenidas la falla dura diez minutos. La
posición cambia sin cambiar el horizonte total:

| Celda sellada | Repeticiones | Referencia normal | Falla | Recuperación | Observación |
|---|---:|---:|---:|---:|---:|
| Control sin falla | 3 | 50 min | 0 min | 0 min | 50 min |
| Falla temprana | 3 | 10 min | 10 min | 30 min | 50 min |
| Falla intermedia | 3 | 20 min | 10 min | 20 min | 50 min |
| Falla tardía | 3 | 30 min | 10 min | 10 min | 50 min |

El lote comprende doce runs de 55 minutos cada una. Su duración programada
acumulada es de once horas, a la que deben añadirse preflight, drenaje,
estabilización Gold y cualquier pausa operativa. Debe reservarse una ventana
continua superior a doce horas y evitar suspensión, hibernación o cambio de
configuración del host.

Las tres posiciones permiten observar si una puntuación sigue al inicio real de
la condición y no a un minuto fijo. El control permite cuantificar falsas
alarmas producidas por deriva o antigüedad de la run. La aleatorización del
orden distribuye entre las celdas, en expectativa, los cambios acumulativos del
entorno. Con tres repeticiones por celda, la cohorte sigue siendo pequeña: sirve
para una comparación controlada local y para estimar consistencia, pero no
sustenta por sí sola generalización a otros sistemas o fallas.

## Elementos congelados antes de ejecutar

La asignación ciega evita ajustar contra las nuevas etiquetas, pero no impide
decisiones retrospectivas si el protocolo analítico permanece abierto. Estos
elementos quedaron versionados en `confirmatory_manifest_v1` y se explican en
`09_manifiesto_confirmatorio.md`:

- la tarea primaria —detección global, identificación del servicio afectado o
  localización— y las tareas secundarias;
- los algoritmos candidatos y las líneas base;
- las variables por modalidad, ablaciones y representación temporal;
- el ajuste, imputación, escalado, longitud de secuencia, umbral e
  hiperparámetros, todos obtenidos sin usar la nueva cohorte;
- las métricas, la unidad de cómputo y el tratamiento de ventanas de frontera;
- el esquema del archivo de predicciones que se congelará antes de revelar.

Los datos nuevos son exclusivamente de evaluación. No deben intervenir en
entrenamiento, selección de variables, calibración de umbrales, elección de
hiperparámetros ni selección entre candidatos. Si se decide permitir una
referencia normal local, su longitud y transformación deben quedar fijadas por
anticipado y aplicarse igual a las doce runs; la celda temprana garantiza un
mínimo de diez minutos normales.

## Asignación, compromiso y roles

`blind_batch.py prepare` expande el diseño, mezcla criptográficamente sus doce
asignaciones y crea un código opaco por run. El lote contiene cinco archivos
de control:

| Archivo | Contenido y acceso antes de revelar |
|---|---|
| `protocol.snapshot.json` | Copia inmutable del diseño, sin la asignación aleatoria |
| `confirmatory-manifest.snapshot.json` | Copia byte a byte del manifiesto analítico congelado |
| `commitment.json` | Hash del protocolo y compromiso SHA-256 de la asignación |
| `public-cohort.json` | Orden, código opaco, `run_id` y estado; no contiene celda ni tiempos de inyección |
| `allocation.sealed.json` | Correspondencia completa; permisos `0600`, solo para custodia y ejecución |

El analista recibe `commitment.json`, `public-cohort.json` y exportaciones de
características identificadas por código opaco. No recibe el archivo sellado,
los datos de referencia, la cronología de fases ni los paquetes completos. El
operador conserva la asignación y ejecuta la inyección. Después de producir las
predicciones, el analista entrega un único archivo acordado que relacione cada
código opaco con sus puntuaciones o rankings.

La revelación calcula primero el SHA-256 del archivo de predicciones y escribe
`predictions-commitment.json`. Solo entonces crea
`allocation-revealed.json`. Así queda trazabilidad de que la salida existía
antes de que el analista conociera las condiciones. La integridad criptográfica
no sustituye la separación de roles: copiar los archivos sellados, consultar
`evaluation_reference_v1` o inspeccionar las fases rompería el cegamiento aunque
los hashes siguieran siendo válidos.

## Implementación

La especificación ejecutable está en
`../AIOpsLab/deploy/etl/blind_protocol_v1.json`. El orquestador
`../AIOpsLab/deploy/etl/blind_batch.py` implementa cuatro operaciones:

```bash
# 1. Crear y comprometer una asignación; no inicia servicios ni runs.
python3 deploy/etl/blind_batch.py prepare \
  --protocol deploy/etl/blind_protocol_v1.json

# 2. Verificar los hashes del lote preparado.
python3 deploy/etl/blind_batch.py verify --batch-dir <batch-dir>

# 3. Ejecutar o reanudar las runs pendientes.
python3 deploy/etl/blind_batch.py run --batch-dir <batch-dir>

# 4. Congelar las predicciones y revelar la asignación.
python3 deploy/etl/blind_batch.py reveal \
  --batch-dir <batch-dir> \
  --predictions <predictions-file>
```

El ejecutor `experiment.py` incorpora el modo `--control-cycle`, que registra
calentamiento y operación normal sin modificar la bandera. También exige que
`batch_id`, código opaco y compromiso se declaren juntos; una declaración
parcial falla antes de recolectar. Las runs ciegas usan una repetición, escala
`1.0`, no aceptan omitir el control de backlog y se clasifican como
`blind_confirmatory_candidate`. Esta clasificación indica destino previsto, no
convierte automáticamente una run técnicamente completa en evidencia válida.

El orquestador reutiliza las salvaguardas existentes: capacidad de disco,
estabilidad y ausencia de reinicios del plano de control, variante base de la
bandera, lag medible y acotado, duración de fases, restauración de la falla,
estabilidad de Gold y paquete con checksums. Si una run falla, registra el
estado, conserva su paquete y detiene el lote. Al reanudar, omite códigos ya
completos y vuelve a intentar el pendiente; la asignación comprometida no
cambia.

La implementación fue verificada mediante 27 pruebas unitarias combinadas.
Estas cubren validación del diseño balanceado, igualdad del horizonte,
ocultamiento de las celdas en el archivo público, permisos `0600`, verificación
del compromiso, construcción del control sin falla, exclusión mutua entre modos
del ejecutor, bloqueo de la revelación prematura y rechazo de predicciones
vacías. Son pruebas del artefacto, no
evidencia de ejecución de la cohorte.

## Entrega ciega y evaluación posterior

Una exportación para modelado debe unir cada `run_id` público con su código
opaco y excluir campos o artefactos que revelen condición, fase o instante de
inyección. Se mantienen `run_id`, servicio y tiempo relativo porque son
necesarios para secuencias y rankings, pero el tiempo debe expresarse respecto
del inicio de la observación sin marcas de fase. También deben excluirse
`condition`, `fault_type`, `affected_component`, `label_assignment_basis` y
cualquier nombre de archivo que codifique la celda.

Después de revelar, la comparación debe informar como mínimo:

- falsas alarmas y distribución de puntuaciones en los tres controles;
- desempeño por posición temprana, intermedia y tardía, no solo el agregado;
- tiempo respecto del inicio real de la falla y respecto del inicio de la run;
- consistencia entre las tres repeticiones de cada celda;
- detección global, identificación del servicio y localización como tareas
  separadas cuando se conserven las tres;
- métricas tabulares y secuenciales sobre poblaciones explícitas, sin comparar
  denominadores distintos como si fueran equivalentes;
- ablaciones por modalidad y desempeño de la unión trimodal;
- intervalos o dispersión por run, además del valor agregado.

La evidencia apoyará que un candidato reconoce la condición, y no únicamente
el tiempo, si mantiene pocas falsas alarmas en control, su respuesta se desplaza
con el inicio real de la falla y el patrón aparece de forma consistente en las
tres posiciones. Si la puntuación aparece aproximadamente en el mismo minuto
de todas las runs, incluidos los controles, se interpretará como señal de
deriva temporal. Si solo funciona en una posición, deberá informarse esa
dependencia y no presentarse como reconocimiento estable.

## Criterio de cierre

El lote queda apto para evaluación únicamente cuando las doce runs estén
completas, los paquetes y compromisos sean válidos, el entorno no haya cambiado
entre ellas y el archivo de predicciones se haya congelado antes de revelar.
Una falla técnica, una exposición anticipada de la asignación o un cambio del
modelo motivado por resultados de la cohorte invalida el carácter ciego de la
comparación. En ese caso, los datos podrán conservarse como desarrollo, pero se
requerirá una cohorte nueva para una afirmación confirmatoria.
