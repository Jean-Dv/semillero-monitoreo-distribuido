# Manifiesto confirmatorio para la comparación ciega

## Estado

`confirmatory_manifest_v1` quedó congelado antes de preparar o ejecutar el lote
ciego. Su SHA-256 es:

```text
255f33b26a7042681352f38c2a1e16b45b97950abd15222cdfad17227c1157e8
```

El archivo canónico está en
`experiments/algorithm_comparison/config/confirmatory_manifest_v1.json`; el
checksum se conserva junto a él y
`scripts/validate_confirmatory_manifest.py` verifica tanto su integridad como
los hashes de los manifiestos, programas de desarrollo y protocolo ciego de los
que depende. Las runs anteriores se consideran desarrollo: ninguna conserva el
papel de prueba confirmatoria después de esta congelación.

## Comparación congelada

Se evaluarán cinco familias sobre dos representaciones comunes, para diez
variantes fijas:

| Familia | Métricas | Trimodal | Régimen |
|---|---|---|---|
| Reglas robustas | Sí | Sí | Línea base interpretable |
| Isolation Forest | Sí | Sí | No supervisado tabular |
| One-Class SVM | Sí | Sí | No supervisado de una clase |
| HistGradientBoosting | Sí | Sí | Supervisado |
| Autoencoder LSTM | Sí | Sí | No supervisado temporal |

No se incluye HDBSCAN porque su agrupamiento transductivo no produce un
detector congelado aplicable a nuevas runs. Tampoco se conservan únicamente las
modalidades que encabezaron una métrica anterior. Comparar métricas y unión
trimodal dentro de cada familia mantiene una ablación común y permite atribuir
el cambio a la integración de señales, no a que cada algoritmo reciba una
entrada elegida retrospectivamente.

Los hiperparámetros, semillas, ajustes, calibradores y umbrales son los ya
obtenidos con entrenamiento y validación. La cohorte ciega no podrá intervenir
en reentrenamiento, imputación aprendida, escalado, calibración, selección de
modalidad, umbral, candidato o población. El conjunto de entrenamiento sigue
siendo la primera run de desarrollo; la validación anterior aporta los valores
congelados y la antigua prueba queda solo como antecedente observado.

## Representación e inferencia

Cada run dispone de una referencia declarada normal formada por sus primeros
dieciocho inicios de ventana posteriores al calentamiento. Por servicio y
variable se calculan mediana, IQR con respaldos, nivel local y cambio respecto
de la ventana inmediatamente anterior. Las filas de referencia quedan fuera de
la inferencia evaluable.

El autoencoder usa doce pasos separados por diez segundos. Durante la inferencia
ciega las secuencias se forman cronológicamente sin consultar fases ni
condiciones y no cruzan runs, servicios o discontinuidades reales. Después de
revelar, la evaluación primaria conserva únicamente los extremos cuya historia
completa pertenece a una misma condición pura. Los modelos tabulares se
restringen a esos mismos extremos para que la comparación primaria use una
población común; sus poblaciones nativas se podrán informar de manera
secundaria.

## Tarea y criterio de decisión

La tarea primaria es detectar la condición a nivel de sistema. Para cada
instante se toma el máximo puntaje calibrado entre servicios y se calcula
precisión promedio sobre ventanas puras normales y de falla. Se informará la
prevalencia empírica y un intervalo del 95 % mediante 2000 remuestreos por
`run_code`.

La utilidad no se decidirá solo por la precisión promedio. En los tres
controles sin falla, los puntos positivos consecutivos separados por menos de
treinta segundos se agrupan como un episodio. Un candidato deja de ser
admisible si supera seis episodios por hora normal. También debe superar como
estimación puntual las referencias aleatorias de localización —MRR 0,2745 y
Hit@3 0,2727— y mantener la dirección de los resultados en las celdas temprana,
intermedia y tardía.

Entre candidatos admisibles se prioriza la mayor precisión promedio; diferencias
de hasta 0,01 se resuelven por menor tasa de episodios falsos y luego por mayor
MRR. Dentro de una familia se conserva métricas salvo que la variante trimodal
mejore la precisión promedio en más de 0,01 sin empeorar falsas alarmas ni MRR.
Si ningún candidato satisface los criterios, la conclusión preespecificada es
no seleccionar algoritmo; los límites no podrán relajarse después de revelar.

## Contrato ciego

El analista producirá puntajes para los diez `model_id` y las doce runs usando
solo códigos opacos. Los archivos de puntajes no pueden contener condición,
falla, componente afectado, celda, fase ni instante de inyección. Un manifiesto
de predicciones registrará el hash del manifiesto confirmatorio, el lote, los
artefactos de modelo y cada archivo de puntajes.

Al preparar un lote, `blind_batch.py` copia sin modificar el manifiesto
confirmatorio, lo marca como solo lectura y añade su SHA-256 a
`commitment.json` y `public-cohort.json`. La verificación rechaza cualquier
diferencia. La asignación solo podrá revelarse después de resumir
criptográficamente las predicciones.

La validación previa a la preparación se ejecuta desde el repositorio académico:

```bash
python3 experiments/algorithm_comparison/scripts/validate_confirmatory_manifest.py
```

El siguiente trabajo técnico es implementar y probar el generador ciego de
puntajes contra este contrato, sin modificar el manifiesto congelado. Si una
corrección futura cambia una decisión científica y no solo repara una
implementación, deberá crearse una versión nueva antes de ejecutar datos que
puedan influir en ella.
