# Comparación exploratoria de algoritmos v1

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

Los CSV de entrada no contienen `condition`, `fault_type`,
`affected_component` ni `label_assignment_basis`. Las etiquetas se incorporan
solo después de definir las particiones y se usan para seleccionar
hiperparámetros y umbrales en validación o para evaluar la prueba.

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
