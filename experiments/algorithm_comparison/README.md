# Comparación exploratoria de algoritmos

Este directorio congela y compara la primera cohorte nominal derivada de
`gold_service_window_v2.2`. Los datos exportados y los informes detallados se
mantienen locales; se versionan el manifiesto, las consultas y los programas
necesarios para reproducirlos.

## Cohorte y particiones

- entrenamiento: `8d2c4e1a-8a91-4a35-afb2-3dbd009141c1`;
- validación: `9425edd0-c16e-4964-9c6f-dfe2193f91cf`;
- prueba: `5b95bd7f-a198-4e2e-b8ce-6c75f55ce008`;
- namespace: `astronomy-shop`;
- once servicios con correspondencia trimodal por namespace;
- entrenamiento limitado a ventanas normales puras;
- evaluación primaria limitada a ventanas normales y de fallo puras;
- calentamiento excluido y recuperación tratada como análisis secundario.

`accounting`, `cart` y `quote` no se fusionan con la cohorte primaria porque
sus señales sin namespace no pueden asociarse únicamente por compartir
`service.name`.

## Reproducción

Desde la raíz de este repositorio:

```bash
docker compose -f ../AIOpsLab/deploy/etl/docker-compose.yaml up -d clickhouse
python experiments/algorithm_comparison/scripts/export_dataset.py
python experiments/algorithm_comparison/scripts/validate_dataset.py
python experiments/algorithm_comparison/scripts/compare_algorithms.py
docker compose -f ../AIOpsLab/deploy/etl/docker-compose.yaml stop clickhouse
```

El exportador genera `features_v1.csv`, `evaluation_reference_v1.csv` y
`SHA256SUMS`. El validador crea las asignaciones por fase y comprueba contrato,
cohorte, unicidad y separación de etiquetas. El comparador genera:

- `detector_comparison_v1.csv` y `.json`;
- `hdbscan_exploration_v1.json`;
- `explanations_v1.json`.

## Iteración con referencia temporal local

La segunda iteración queda preespecificada en
`config/local_reference_manifest_v1.json`. Conserva las runs, la cohorte, los
algoritmos y las tareas de v1, pero sustituye los niveles absolutos entre runs
por dos componentes temporales sin anticipación: el nivel respecto de una
referencia local y el cambio frente a la ventana previa.

La referencia de cada servicio se estima con los primeros dieciocho instantes
normales puros de su propia run. Esas filas se excluyen tanto del ajuste como de
la evaluación. Este diseño supone que una ejecución futura dispone de un
periodo inicial declarado como normal; no supone conocer anticipadamente las
ventanas de fallo.

Después de generar y validar el conjunto v1, la iteración se reproduce con:

```bash
python experiments/algorithm_comparison/scripts/analyze_normal_drift.py
python experiments/algorithm_comparison/scripts/compare_local_reference.py
```

El primer programa genera `normal_drift_v1.csv` y `.json`. El segundo congela
todos los modelos mediante validación antes de consultar la partición de prueba
y produce `local_reference_comparison_v1.csv` y `.json`, además del informe de
auditoría y las oclusiones. Estos informes también permanecen locales.

## Candidatos supervisado y temporal

`config/extended_candidates_manifest_v1.json` añade gradient boosting y un
autoencoder temporal LSTM. Este ciclo excluye la run de prueba ya observada:
ajusta con entrenamiento y usa validación solo para ordenar provisionalmente
las variantes y fijar umbrales para futuras runs independientes.

El autoencoder requiere PyTorch CPU. Para crear un entorno aislado y reproducir
el desarrollo:

```bash
python -m venv experiments/algorithm_comparison/.venv
experiments/algorithm_comparison/.venv/bin/python -m pip install \
  -r experiments/algorithm_comparison/requirements.txt
experiments/algorithm_comparison/.venv/bin/python \
  experiments/algorithm_comparison/scripts/compare_extended_candidates.py
```

El programa genera `extended_candidates_development_v1.csv` y `.json`. Compara
cuatro ablaciones de `HistGradientBoostingClassifier` y cuatro de un
autoencoder codificador-decodificador LSTM sobre secuencias de doce pasos. Sus
resultados son de desarrollo y no sustituyen una prueba ciega.

Los CSV de entrada no contienen `condition`, `fault_type`,
`affected_component` ni `label_assignment_basis`. Las etiquetas se incorporan
solo después de definir las particiones y se usan para seleccionar
hiperparámetros y umbrales en validación o para evaluar la prueba.

## Siguiente cohorte ciega

La siguiente evaluación no reutilizará la prueba anterior. El protocolo
`../AIOpsLab/deploy/etl/blind_protocol_v1.json` define doce runs con igual
duración: tres controles sin falla y tres repeticiones con `adFailure` en cada
posición temprana, intermedia y tardía. El orquestador
`../AIOpsLab/deploy/etl/blind_batch.py` entrega al analista solo códigos opacos
y `run_id`; la asignación se revela después de congelar el archivo de
predicciones.

`config/confirmatory_manifest_v1.json` congela diez variantes de reglas
robustas, Isolation Forest, One-Class SVM, gradient boosting y autoencoder LSTM
sobre métricas y unión trimodal. También fija la tarea primaria, variables,
preprocesamiento, hiperparámetros, umbrales, población común, métricas, límite de
falsas alarmas y contrato de salida. Su SHA-256 se conserva en
`config/confirmatory_manifest_v1.sha256`.

Valide la congelación antes de preparar el lote:

```bash
python3 experiments/algorithm_comparison/scripts/validate_confirmatory_manifest.py
```

Las nuevas características podrán contener tiempo relativo y código opaco,
pero no la fase, la condición, el instante de inyección ni los datos de
referencia. El procedimiento completo está en
[`docs/arquitecturas_etl/08_protocolo_runs_ciegas.md`](../../docs/arquitecturas_etl/08_protocolo_runs_ciegas.md).
La decisión confirmatoria congelada se explica en
[`docs/arquitecturas_etl/09_manifiesto_confirmatorio.md`](../../docs/arquitecturas_etl/09_manifiesto_confirmatorio.md).

El siguiente paso obligatorio es implementar y probar un generador ciego de
puntajes que lea este manifiesto, reconstruya las diez variantes sin
reseleccionarlas y produzca `blind_predictions_manifest_v1` con hashes de
modelos y archivos de puntajes. No prepare ni ejecute el lote de doce runs hasta
que ese generador y sus pruebas estén completos.

## Métodos y preprocesamiento

Se comparan reglas robustas, Isolation Forest y One-Class SVM sobre cuatro
conjuntos: métricas, logs, trazas y la unión trimodal. HDBSCAN se informa aparte
como agrupamiento transductivo; no se presenta como detector de novedad.

Las magnitudes no negativas usan `log1p`. La imputación y el escalado robusto
por servicio se ajustan únicamente con ventanas normales de entrenamiento. Los
puntajes se calibran por servicio contra su distribución normal de
entrenamiento antes de agregarlos o compararlos.

La comparación evalúa tres tareas diferentes:

1. detección de la condición a nivel de sistema;
2. detección de la observación correspondiente al servicio intervenido;
3. posición de `affected_component` en el ranking de servicios durante fallo.

El resumen académico y la decisión de avance están en
[`docs/arquitecturas_etl/05_aceptacion_gold_y_comparacion_exploratoria.md`](../../docs/arquitecturas_etl/05_aceptacion_gold_y_comparacion_exploratoria.md).
La iteración de representación se interpreta en
[`docs/arquitecturas_etl/06_deriva_y_representacion_temporal_local.md`](../../docs/arquitecturas_etl/06_deriva_y_representacion_temporal_local.md).
Los candidatos añadidos se documentan en
[`docs/arquitecturas_etl/07_candidatos_supervisado_y_temporal.md`](../../docs/arquitecturas_etl/07_candidatos_supervisado_y_temporal.md).
