# Desarrollo de gradient boosting y autoencoder temporal

## 1. Alcance del ciclo

Este ciclo completa el catálogo de familias previsto para la comparación al
incorporar árboles con potenciación de gradiente y un autoencoder temporal. Se
conservaron la cohorte de once servicios, la representación respecto de una
referencia local y las ablaciones de métricas, registros, trazas y unión
trimodal.

La run de prueba ya había sido observada en dos iteraciones anteriores. Por
ello, `extended_candidates_manifest_v1` prohíbe usarla en este desarrollo. Los
modelos se ajustaron con la primera run y se analizaron con validación. Las
métricas siguientes sirven para congelar candidatos y detectar problemas; no
son estimaciones confirmatorias ni autorizan seleccionar un algoritmo final.

## 2. Regímenes de aprendizaje

### 2.1 Árbol con potenciación de gradiente

Se implementó `HistGradientBoostingClassifier` de scikit-learn con una
configuración fija: tasa de aprendizaje 0,05, 200 iteraciones, hasta quince
hojas, mínimo veinte observaciones por hoja y regularización L2 igual a uno. El
ajuste supervisado empleó 429 observaciones normales como negativas y 57
observaciones de `ad` durante fallo como positivas. Las 570 observaciones de
otros servicios durante fallo no se convirtieron en negativas, porque podrían
contener propagación o efectos secundarios no etiquetados. Las dos clases
recibieron el mismo peso total.

El modelo produce un puntaje por servicio y ventana. Los puntajes se calibraron
por servicio con su distribución normal de entrenamiento y se agregaron por
máximo para la detección de sistema. Esta decisión mantiene las tres tareas de
los ciclos anteriores, pero el uso de etiquetas hace que el régimen supervisado
no sea equivalente a los detectores entrenados solo con normalidad.

### 2.2 Autoencoder temporal LSTM

Se instaló PyTorch CPU 2.15.0 en un entorno virtual local y se implementó un
autoencoder recurrente. Cada muestra contiene doce pasos consecutivos separados
por diez segundos. Las secuencias no cruzan ejecuciones, servicios ni
discontinuidades; las ventanas de frontera excluidas separan las fases sin usar
la condición como característica.

El codificador LSTM tiene 24 unidades y proyecta su estado a un espacio latente
de doce dimensiones. El decodificador reconstruye los doce pasos mediante otro
LSTM y una proyección lineal. Se entrenó durante 80 épocas, exclusivamente con
308 secuencias normales de entrenamiento. La validación contiene 825 secuencias
por servicio: 319 normales y 506 de fallo. Al exigir doce pasos, las métricas de
sistema se calculan sobre 29 instantes normales y 46 de fallo, una población
distinta de los 40 y 57 instantes disponibles para el árbol.

## 3. Resultados de validación

AP es precisión promedio. FP representa falsos positivos de sistema al aplicar
el umbral elegido en la propia validación; por ello su F1 es optimista y no mide
transferencia. Para gradient boosting la prevalencia es 0,588 a nivel de sistema
y 0,115 para el servicio afectado. Para el autoencoder es 0,613 y 0,126,
respectivamente. La referencia aleatoria de localización es aproximadamente
0,275 para MRR y 0,273 para Hit@3.

| Familia | Señales | AP sistema | FP | AP afectado | MRR | Hit@3 |
|---|---|---:|---:|---:|---:|---:|
| Gradient boosting | Métricas | 0,600 | 38/40 | 0,234 | 0,335 | 0,579 |
| Gradient boosting | Logs | 0,621 | 40/40 | 0,075 | 0,094 | 0,000 |
| Gradient boosting | Trazas | 0,588 | 40/40 | 0,072 | 0,125 | 0,035 |
| Gradient boosting | Trimodal | 0,590 | 39/40 | 0,206 | 0,314 | 0,491 |
| Autoencoder LSTM | Métricas | 0,697 | 20/29 | 0,332 | 0,298 | 0,348 |
| Autoencoder LSTM | Logs | 0,613 | 29/29 | 0,184 | 0,220 | 0,000 |
| Autoencoder LSTM | Trazas | 0,613 | 29/29 | 0,096 | 0,116 | 0,000 |
| Autoencoder LSTM | Trimodal | 0,613 | 29/29 | 0,109 | 0,133 | 0,000 |

Gradient boosting sobre logs encabeza la AP global de su familia porque ese fue
el primer criterio preespecificado, pero queda por debajo de las referencias en
identificación y localización del servicio afectado. La variante de métricas
presenta la señal supervisada más consistente para esas dos tareas: su AP del
servicio afectado duplica la prevalencia y su MRR supera la referencia
aleatoria. No obstante, marca 38 de 40 instantes normales como positivos. La
variante trimodal tampoco domina a métricas.

El autoencoder de métricas es el único candidato extendido que supera las tres
referencias principales en validación: AP global 0,697, AP del servicio afectado
0,332 y MRR 0,298. Su umbral aún produce veinte falsos positivos entre
veintinueve instantes normales, lo que impide afirmar utilidad operativa. Los
autoencoders de logs, trazas y unión trimodal no separan la condición a nivel de
sistema por encima de su prevalencia.

## 4. Evidencia explicativa y límites

En gradient boosting sobre métricas, la oclusión señala principalmente nivel de
memoria y CPU. En el autoencoder de métricas, los mayores errores de
reconstrucción del servicio afectado corresponden al nivel y cambio de CPU y al
cambio de tasa de solicitudes. Estas medidas describen sensibilidad o error de
reconstrucción; no demuestran que esas variables causen el fallo ni satisfacen
por sí solas la operacionalización de interpretabilidad.

Las secuencias se solapan y proceden de una sola run de entrenamiento y otra de
validación. Tampoco se ha eliminado el acoplamiento entre tiempo y fase: el
fallo ocurre después del periodo normal. El autoencoder dispone de menos
instantes evaluables por su requisito de historia. En consecuencia, comparar
directamente su AP con la del árbol sin informar prevalencia y población sería
incorrecto.

## 5. Decisión

Se incorporaron las dos familias faltantes, pero no se selecciona un algoritmo.
La clasificación mecánica por AP global sitúa logs primero para gradient
boosting, mientras las tareas de identificación y localización favorecen
métricas. Esta divergencia confirma que debe definirse una tarea primaria antes
de congelar una variante supervisada.

El autoencoder LSTM sobre métricas queda como candidato temporal principal para
una prueba futura porque supera las referencias de las tres tareas en
validación. Gradient boosting sobre métricas queda como candidato supervisado
para identificación y localización, no como detector global aceptado. Estas son
decisiones de desarrollo y no resultados confirmatorios.

El próximo protocolo deberá:

1. declarar cuál tarea determina la selección y cuáles son secundarias;
2. generar nuevas runs que desacoplen tiempo y condición;
3. conservar una cohorte ciega que no participe en transformaciones, selección
   de modalidad ni umbrales;
4. evaluar en esa cohorte las configuraciones congeladas y las líneas base bajo
   poblaciones comparables;
5. rechazar cualquier candidato cuyo umbral no controle las falsas alarmas,
   aunque su AP supere la prevalencia.

El manifiesto, el código y las instrucciones están en
`experiments/algorithm_comparison/`. Los informes detallados y los datos
continúan locales.
