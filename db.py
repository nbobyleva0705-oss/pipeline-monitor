"""SQLite connection helper."""
import os
import sqlite3

from flask import g

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pipeline_monitor.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def _migrate(conn):
    """Apply incremental schema migrations to existing DB."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(pipeline_versions)")}

    if 'is_active' not in cols:
        conn.execute("ALTER TABLE pipeline_versions ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")

    if 'expires_at' not in cols:
        conn.execute("ALTER TABLE pipeline_versions ADD COLUMN expires_at TEXT")

    conn.commit()

    # Seed historical versions if only v1 exists for pl-001 and pl-002
    existing = {row[0] for row in conn.execute("SELECT id FROM pipeline_versions")}

    if 'pv-001-v2' not in existing:
        # daily-aggregation: mark v1 as expired, add v2 and v3
        conn.execute("UPDATE pipeline_versions SET is_active=0, expires_at=datetime('now','-60 days') WHERE id='pv-001'")
        conn.execute("""INSERT OR IGNORE INTO pipeline_versions (id, pipeline_id, version, config, is_active, expires_at, created_at)
            VALUES ('pv-001-v2','pl-001',2,
                '{"engine":"spark","query":"SELECT date, SUM(amount), COUNT(*) FROM transactions GROUP BY date","timeout":300}',
                0, datetime('now','-30 days'), datetime('now','-30 days'))""")
        conn.execute("""INSERT OR IGNORE INTO pipeline_versions (id, pipeline_id, version, config, is_active, expires_at, created_at)
            VALUES ('pv-001-v3','pl-001',3,
                '{"engine":"spark","query":"SELECT date, SUM(amount), COUNT(*), AVG(amount) FROM transactions GROUP BY date","timeout":600,"partitions":8}',
                1, NULL, datetime('now','-5 days'))""")

    if 'pv-002-v2' not in existing:
        # fraud-detection: mark v1 as expired, add v2
        conn.execute("UPDATE pipeline_versions SET is_active=0, expires_at=datetime('now','-45 days') WHERE id='pv-002'")
        conn.execute("""INSERT OR IGNORE INTO pipeline_versions (id, pipeline_id, version, config, is_active, expires_at, created_at)
            VALUES ('pv-002-v2','pl-002',2,
                '{"engine":"flink","model":"fraud_v3","threshold":0.90,"features":["amount","location","device"]}',
                1, NULL, datetime('now','-10 days'))""")

    conn.commit()


def init_app(app):
    app.teardown_appcontext(close_db)

    # Run migrations on startup
    conn = sqlite3.connect(DB_PATH)
    try:
        _migrate(conn)
    finally:
        conn.close()
