# Aceptación de la cohorte y comparación exploratoria de algoritmos

## 1. Propósito y alcance

Este informe registra la decisión posterior a las tres repeticiones nominales
de `astronomy-ad-failure-v1` ejecutadas el 21 de noviembre de 2026. Su propósito
es determinar si `gold_service_window_v2.2` permite iniciar una exploración
reproducible de métodos y si la evidencia disponible basta para seleccionar un
algoritmo. Los resultados se limitan a Astronomy Shop, `adFailure`, once
servicios y las ventanas observadas; no se generalizan a otros sistemas ni
fallos.

## 2. Runs y calidad de la cohorte

Las tres ejecuciones terminaron con paquetes completos, cronologías válidas y
sumas SHA-256 verificadas:

| Partición | `run_id` | Filas de la cohorte | Filas generadas | Eventos tardíos |
|---|---|---:|---:|---:|
| Entrenamiento | `8d2c4e1a-8a91-4a35-afb2-3dbd009141c1` | 2404 | 6 | 0 |
| Validación | `9425edd0-c16e-4964-9c6f-dfe2193f91cf` | 2421 | 5 | 0 |
| Prueba | `5b95bd7f-a198-4e2e-b8ce-6c75f55ce008` | 2352 | 0 | 18441 |

Las 7177 filas poseen `feature_id` y clave lógica únicos. No se encontraron
columnas de etiquetas en `feature_tabular_v1`. Los eventos tardíos de la
tercera run quedaron exclusivamente en recuperación y ventanas de frontera:
15373 en recuperación pura y 3068 en fronteras. Por tanto, no contaminan las
fases primarias normal y fallo.

La cohorte primaria incluye `ad`, `checkout`, `currency`, `email`,
`fraud-detection`, `frontend`, `frontend-proxy`, `payment`, `product-catalog`,
`recommendation` y `shipping`. Aunque el perfil nominal encuentra catorce
nombres en las tres modalidades, `accounting`, `cart` y `quote` tienen métricas
en `astronomy-shop` y logs o trazas sin namespace. Esos tres servicios se
conservan como estrato de calidad separado y no se fusionan por coincidencia
nominal.

Se observaron dos errores JDBC transitorios durante el conjunto de ejecuciones.
El job de Flink conservó el mismo identificador, no registró checkpoints
fallidos ni restauraciones globales y continuó completando checkpoints. Estos
eventos se documentan como incidencias operativas, no como reinicios de las
runs.

## 3. Congelación y prevención de fuga

El manifiesto `partition_manifest_v1` asigna una run completa a cada partición.
No se dividen filas aleatoriamente porque las ventanas de treinta segundos se
desplazan cada diez segundos y se solapan. Cada fase primaria pura contiene 57
instantes por once servicios, es decir, 627 observaciones por condición y run.

Una ventana recibe una fase únicamente cuando su intervalo completo está
contenido en ella. Calentamiento se excluye; recuperación es secundaria; las
ventanas de frontera o exteriores no intervienen en la comparación primaria.
La imputación, las transformaciones, el escalado y la calibración de puntajes se
ajustan con las ventanas normales de entrenamiento.

Se operacionalizaron tres tareas complementarias:

1. detectar a nivel de sistema si el instante pertenece a normal o fallo;
2. distinguir las observaciones del servicio intervenido frente a las ventanas
   normales, sin convertir los demás servicios durante fallo en negativos;
3. ordenar los servicios durante fallo y medir la posición de `ad`.

## 4. Comparación exploratoria

Se evaluaron reglas robustas, Isolation Forest y One-Class SVM sobre métricas,
logs, trazas y la unión trimodal. Las magnitudes se transformaron con `log1p`
cuando correspondía y se escalaron por servicio mediante mediana e IQR. Los
hiperparámetros y umbrales se eligieron solo con validación. HDBSCAN se analizó
por separado porque su uso transductivo no equivale a predecir novedad en una
run futura.

La tabla resume resultados de prueba. AP es precisión promedio; MRR y Hit@3
corresponden a localización. La prevalencia positiva es 0,500 para detección de
sistema y 0,083 para observaciones del servicio afectado. Un ranking aleatorio
entre once servicios tendría MRR aproximado de 0,275 y Hit@3 de 0,273.

| Método | Modalidades | AP sistema | AP servicio afectado | MRR | Hit@3 |
|---|---|---:|---:|---:|---:|
| Reglas robustas | Trimodal | 0,500 | 0,119 | 0,236 | 0,000 |
| Isolation Forest | Trimodal | 0,482 | 0,122 | 0,371 | 0,456 |
| One-Class SVM | Trimodal | 0,500 | 0,127 | 0,301 | 0,474 |
| Isolation Forest | Solo métricas | 0,491 | 0,197 | 0,431 | 0,772 |
| One-Class SVM | Solo trazas | 0,499 | 0,122 | 0,365 | 0,421 |

Ningún detector separó normal y fallo a nivel de sistema: su AP de prueba quedó
entre 0,479 y 0,500, alrededor de la prevalencia aleatoria. El F1 cercano a
0,667 en varias variantes no representa una detección útil, pues los umbrales
transferidos desde validación marcaron casi todas las ventanas normales como
positivas. Por ello no debe usarse ese F1 aislado para declarar éxito.

Isolation Forest con métricas mostró señal parcial para el servicio afectado y
su ranking superó las referencias aleatorias, pero todavía produjo numerosos
falsos positivos y no constituye evidencia suficiente para seleccionarlo. La
unión trimodal no superó consistentemente las ablaciones, de modo que estas
runs no demuestran valor incremental de combinar las tres modalidades para la
tarea actual. El análisis de oclusión indica que memoria, latencias y tasa de
solicitudes influyen en algunos puntajes; se trata de sensibilidad del modelo,
no de causalidad ni de una explicación validada.

HDBSCAN tampoco separó los regímenes: la información mutua ajustada entre sus
grupos y la condición quedó entre -0,0022 y 0,0041 según la modalidad. Sus
grupos describen estructura interna o ruido, pero no un patrón asociado de
forma estable con `adFailure`.

## 5. Decisión y siguiente iteración

Gold v2.2 y la cohorte de once servicios se aceptan como base reproducible para
análisis exploratorio: cumplen unicidad, trazabilidad, separación de etiquetas,
partición por run y delimitación temporal. Esta aceptación no equivale a validar
la representación para reconocer el patrón ni a seleccionar un método.

No se selecciona todavía reglas, Isolation Forest, One-Class SVM ni HDBSCAN.
La falta de generalización entre runs y la ausencia de una ventaja trimodal
obligan a regresar iterativamente al diseño de la representación y de la tarea.
La siguiente iteración deberá:

1. cuantificar por servicio y variable la deriva entre los periodos normales de
   entrenamiento, validación y prueba;
2. estudiar cambios respecto de una línea base temporal local, además de
   niveles absolutos por ventana;
3. revisar qué manifestación verificable produce `adFailure` en cada modalidad
   y si la tarea primaria debe priorizar localización sobre clasificación global;
4. resolver o mantener explícitamente separado el estrato sin namespace;
5. incorporar condiciones adicionales y nuevas runs independientes antes de
   una selección confirmatoria;
6. evaluar una representación secuencial solo después de demostrar que la
   señal temporal y su continuidad justifican ese costo.

Los materiales ejecutables están en
`experiments/algorithm_comparison/`. Los datos e informes detallados permanecen
locales para evitar versionar mediciones experimentales voluminosas; sus hashes
se regeneran con el procedimiento documentado.
