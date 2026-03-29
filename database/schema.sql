-- Big Data Pipeline Monitor — SQLite Schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS datasets (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    owner       TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pipelines (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    dataset_id  TEXT NOT NULL REFERENCES datasets(id),
    name        TEXT NOT NULL,
    description TEXT,
    schedule    TEXT,
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pipeline_versions (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    pipeline_id TEXT NOT NULL REFERENCES pipelines(id),
    version     INTEGER NOT NULL DEFAULT 1,
    config      TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS job_runs (
    id                 TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    pipeline_id        TEXT NOT NULL REFERENCES pipelines(id),
    pipeline_version   INTEGER NOT NULL DEFAULT 1,
    status             TEXT NOT NULL DEFAULT 'pending'
                           CHECK(status IN ('pending','running','success','failed')),
    started_at         TEXT,
    finished_at        TEXT,
    records_processed  INTEGER NOT NULL DEFAULT 0,
    error_message      TEXT
);

CREATE TABLE IF NOT EXISTS job_run_steps (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    run_id      TEXT NOT NULL REFERENCES job_runs(id),
    name        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','running','success','failed')),
    started_at  TEXT,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS alert_rules (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    pipeline_id TEXT NOT NULL REFERENCES pipelines(id),
    name        TEXT NOT NULL,
    condition   TEXT NOT NULL,
    enabled     INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alert_events (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    rule_id     TEXT REFERENCES alert_rules(id),
    run_id      TEXT REFERENCES job_runs(id),
    pipeline_id TEXT REFERENCES pipelines(id),
    message     TEXT NOT NULL,
    severity    TEXT NOT NULL DEFAULT 'warning'
                    CHECK(severity IN ('info','warning','critical')),
    status      TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','resolved')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
