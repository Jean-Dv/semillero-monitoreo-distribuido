SELECT
    run_id,
    window_start,
    window_end,
    condition,
    fault_type,
    affected_component,
    label_assignment_basis
FROM aiopslab.evaluation_reference_v1
WHERE run_id IN
(
    '8d2c4e1a-8a91-4a35-afb2-3dbd009141c1',
    '9425edd0-c16e-4964-9c6f-dfe2193f91cf',
    '5b95bd7f-a198-4e2e-b8ce-6c75f55ce008'
)
ORDER BY run_id, window_start
FORMAT CSVWithNames
