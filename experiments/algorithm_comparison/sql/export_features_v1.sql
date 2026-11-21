SELECT
    feature_id,
    run_id,
    scenario_id,
    window_start,
    window_end,
    service_name,
    service_namespace,
    k8s_namespace,
    pod_count,
    deployment_count,
    metric_point_count,
    request_rate,
    span_count,
    server_span_count,
    span_error_ratio,
    log_count,
    log_error_ratio,
    latency_p50_ms,
    latency_p95_ms,
    latency_p99_ms,
    cpu_usage_cores,
    memory_working_set_bytes,
    dependency_edge_count,
    missing_metrics,
    missing_logs,
    missing_traces,
    identity_mismatch_suspected,
    late_event_count,
    duplicate_event_count,
    schema_error_count,
    row_present,
    source_references_json,
    gold_contract_version
FROM aiopslab.feature_tabular_v1
WHERE run_id IN
(
    '8d2c4e1a-8a91-4a35-afb2-3dbd009141c1',
    '9425edd0-c16e-4964-9c6f-dfe2193f91cf',
    '5b95bd7f-a198-4e2e-b8ce-6c75f55ce008'
)
AND k8s_namespace = 'astronomy-shop'
AND service_name IN
(
    'ad',
    'checkout',
    'currency',
    'email',
    'fraud-detection',
    'frontend',
    'frontend-proxy',
    'payment',
    'product-catalog',
    'recommendation',
    'shipping'
)
ORDER BY run_id, window_start, service_name, feature_id
FORMAT CSVWithNames
