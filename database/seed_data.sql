-- Seed data for Big Data Pipeline Monitor

-- Datasets
INSERT INTO datasets (id, name, description, owner, schema_version)
VALUES
    ('ds-001', 'customer_transactions', 'Raw transaction data from e-shop', 'analytics-team', 3),
    ('ds-002', 'customer_events',       'Clickstream and user events',       'data-team',      2),
    ('ds-003', 'product_logs',          'Product interaction logs',          'platform-team',  1);

-- Pipelines
INSERT INTO pipelines (id, dataset_id, name, description, schedule, active)
VALUES
    ('pl-001', 'ds-001', 'daily-aggregation',    'Daily revenue aggregation',       '0 2 * * *',   1),
    ('pl-002', 'ds-001', 'fraud-detection',       'Real-time fraud scoring',         '*/15 * * * *', 1),
    ('pl-003', 'ds-002', 'feature-engineering',  'ML feature pipeline',             '0 4 * * *',   0);

-- Pipeline versions
INSERT INTO pipeline_versions (id, pipeline_id, version, config)
VALUES
    ('pv-001', 'pl-001', 1, '{"engine":"spark","query":"SELECT date, SUM(amount) FROM transactions GROUP BY date"}'),
    ('pv-002', 'pl-002', 1, '{"engine":"flink","model":"fraud_v2","threshold":0.85}'),
    ('pv-003', 'pl-003', 1, '{"engine":"spark","steps":["extract","transform","load"]}');

-- Job runs (mix of statuses)
INSERT INTO job_runs (id, pipeline_id, pipeline_version, status, started_at, finished_at, records_processed, error_message)
VALUES
    ('run-001', 'pl-001', 1, 'success', datetime('now','-3 hours'), datetime('now','-2 hours 50 minutes'), 142300, NULL),
    ('run-002', 'pl-001', 1, 'success', datetime('now','-27 hours'), datetime('now','-26 hours 55 minutes'), 138900, NULL),
    ('run-003', 'pl-002', 1, 'failed',  datetime('now','-1 hour'),   datetime('now','-59 minutes'), 0, 'Connection timeout to scoring service'),
    ('run-004', 'pl-002', 1, 'success', datetime('now','-2 hours'),  datetime('now','-1 hour 58 minutes'), 5400, NULL),
    ('run-005', 'pl-001', 1, 'running', datetime('now','-5 minutes'), NULL, 0, NULL);

-- Job run steps for run-001
INSERT INTO job_run_steps (id, run_id, name, status, started_at, finished_at)
VALUES
    ('step-001', 'run-001', 'extract',   'success', datetime('now','-3 hours'),              datetime('now','-2 hours 58 minutes')),
    ('step-002', 'run-001', 'transform', 'success', datetime('now','-2 hours 58 minutes'),   datetime('now','-2 hours 52 minutes')),
    ('step-003', 'run-001', 'load',      'success', datetime('now','-2 hours 52 minutes'),   datetime('now','-2 hours 50 minutes'));

-- Job run steps for run-003 (failed)
INSERT INTO job_run_steps (id, run_id, name, status, started_at, finished_at)
VALUES
    ('step-004', 'run-003', 'extract',   'success', datetime('now','-1 hour'),     datetime('now','-59 minutes 30 seconds')),
    ('step-005', 'run-003', 'transform', 'failed',  datetime('now','-59 minutes 30 seconds'), datetime('now','-59 minutes')),
    ('step-006', 'run-003', 'load',      'pending', NULL, NULL);

-- Job run steps for run-005 (currently running)
INSERT INTO job_run_steps (id, run_id, name, status, started_at, finished_at)
VALUES
    ('step-007', 'run-005', 'extract',   'success', datetime('now','-5 minutes'), datetime('now','-4 minutes')),
    ('step-008', 'run-005', 'transform', 'running', datetime('now','-4 minutes'), NULL),
    ('step-009', 'run-005', 'load',      'pending', NULL, NULL);

-- Alert rules
INSERT INTO alert_rules (id, pipeline_id, name, condition, enabled)
VALUES
    ('ar-001', 'pl-001', 'daily-agg runtime alert', 'runtime > 600', 1),
    ('ar-002', 'pl-002', 'fraud pipeline failure',  'status == failed', 1);

-- Alert events
INSERT INTO alert_events (id, rule_id, run_id, pipeline_id, message, severity, status)
VALUES
    ('ae-001', 'ar-002', 'run-003', 'pl-002', 'Pipeline fraud-detection failed: Connection timeout to scoring service', 'critical', 'open'),
    ('ae-002', 'ar-001', 'run-002', 'pl-001', 'Pipeline daily-aggregation completed but runtime exceeded threshold', 'warning', 'resolved');
