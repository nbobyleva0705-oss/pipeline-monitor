"""JobRun business logic and pipeline simulation."""
import random
import sqlite3
import threading
import time
from datetime import datetime, timezone

from db import DB_PATH

VALID_TRANSITIONS = {
    'pending': {'running'},
    'running': {'success', 'failed'},
    'success': set(),
    'failed':  set(),
}

STEPS = ['extract', 'transform', 'load']


def create_run(db, pipeline_id):
    pipeline = db.execute(
        "SELECT * FROM pipelines WHERE id = ?", (pipeline_id,)
    ).fetchone()
    if not pipeline:
        raise ValueError("Pipeline not found")
    if not pipeline['active']:
        raise ValueError("Pipeline is inactive and cannot be run")

    version_row = db.execute(
        "SELECT version FROM pipeline_versions WHERE pipeline_id = ? ORDER BY version DESC LIMIT 1",
        (pipeline_id,),
    ).fetchone()
    version = version_row['version'] if version_row else 1

    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        """INSERT INTO job_runs (pipeline_id, pipeline_version, status, started_at)
           VALUES (?, ?, 'running', ?)""",
        (pipeline_id, version, now),
    )
    db.commit()

    run = db.execute(
        "SELECT * FROM job_runs WHERE pipeline_id = ? ORDER BY started_at DESC LIMIT 1",
        (pipeline_id,),
    ).fetchone()
    run_id = run['id']

    # Create steps (all pending)
    for step_name in STEPS:
        db.execute(
            "INSERT INTO job_run_steps (run_id, name, status) VALUES (?, ?, 'pending')",
            (run_id, step_name),
        )
    db.commit()

    # Simulate run in background thread
    t = threading.Thread(target=_simulate_run, args=(run_id, pipeline_id), daemon=True)
    t.start()

    return dict(run)


def _simulate_run(run_id, pipeline_id):
    """Simulate ETL steps and final status in background."""
    time.sleep(random.uniform(1.5, 3.0))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        steps = conn.execute(
            "SELECT * FROM job_run_steps WHERE run_id = ? ORDER BY rowid", (run_id,)
        ).fetchall()

        will_fail = random.random() < 0.3  # 30% chance of failure
        fail_at = random.randint(0, len(steps) - 1) if will_fail else -1

        for i, step in enumerate(steps):
            step_start = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE job_run_steps SET status='running', started_at=? WHERE id=?",
                (step_start, step['id']),
            )
            conn.commit()
            time.sleep(random.uniform(0.3, 0.8))

            if i == fail_at:
                conn.execute(
                    "UPDATE job_run_steps SET status='failed', finished_at=? WHERE id=?",
                    (datetime.now(timezone.utc).isoformat(), step['id']),
                )
                conn.commit()
                _finish_run(conn, run_id, pipeline_id, 'failed',
                            error_message=f"Step '{step['name']}' failed unexpectedly")
                return

            conn.execute(
                "UPDATE job_run_steps SET status='success', finished_at=? WHERE id=?",
                (datetime.now(timezone.utc).isoformat(), step['id']),
            )
            conn.commit()

        records = random.randint(5000, 200000)
        _finish_run(conn, run_id, pipeline_id, 'success', records_processed=records)

    finally:
        conn.close()


def _finish_run(conn, run_id, pipeline_id, status, error_message=None, records_processed=0):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """UPDATE job_runs
           SET status=?, finished_at=?, records_processed=?, error_message=?
           WHERE id=?""",
        (status, now, records_processed, error_message, run_id),
    )
    conn.commit()

    if status == 'failed':
        _create_alerts_for_failure(conn, run_id, pipeline_id, error_message)


def _create_alerts_for_failure(conn, run_id, pipeline_id, error_message):
    rules = conn.execute(
        "SELECT * FROM alert_rules WHERE pipeline_id = ? AND enabled = 1",
        (pipeline_id,),
    ).fetchall()
    for rule in rules:
        conn.execute(
            """INSERT INTO alert_events (rule_id, run_id, pipeline_id, message, severity, status)
               VALUES (?, ?, ?, ?, 'critical', 'open')""",
            (rule['id'], run_id, pipeline_id,
             f"Pipeline failed: {error_message or 'unknown error'}"),
        )
    conn.commit()


def get_runs(db, pipeline_id=None, status=None, date=None):
    query = """SELECT r.*, p.name AS pipeline_name
               FROM job_runs r
               LEFT JOIN pipelines p ON r.pipeline_id = p.id
               WHERE 1=1"""
    params = []

    if pipeline_id:
        query += " AND r.pipeline_id = ?"
        params.append(pipeline_id)
    if status:
        query += " AND r.status = ?"
        params.append(status)
    if date:
        query += " AND date(r.started_at) = ?"
        params.append(date)

    query += " ORDER BY r.started_at DESC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_run_by_id(db, run_id):
    row = db.execute(
        """SELECT r.*, p.name AS pipeline_name
           FROM job_runs r
           LEFT JOIN pipelines p ON r.pipeline_id = p.id
           WHERE r.id = ?""",
        (run_id,),
    ).fetchone()
    if not row:
        return None
    run = dict(row)
    steps = db.execute(
        "SELECT * FROM job_run_steps WHERE run_id = ? ORDER BY rowid", (run_id,)
    ).fetchall()
    run['steps'] = [dict(s) for s in steps]
    return run


def patch_run(db, run_id, data):
    run = db.execute("SELECT * FROM job_runs WHERE id = ?", (run_id,)).fetchone()
    if not run:
        raise ValueError("Run not found")

    new_status = data.get('status')
    if new_status:
        allowed = VALID_TRANSITIONS.get(run['status'], set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {run['status']} -> {new_status}"
            )

    fields, params = [], []
    if new_status:
        fields.append("status = ?")
        params.append(new_status)
        if new_status in ('success', 'failed'):
            fields.append("finished_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
    if 'error_message' in data:
        fields.append("error_message = ?")
        params.append(data['error_message'])
    if 'records_processed' in data:
        fields.append("records_processed = ?")
        params.append(int(data['records_processed']))

    if fields:
        params.append(run_id)
        db.execute(f"UPDATE job_runs SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()

        if new_status == 'failed':
            _create_alerts_for_failure(db, run_id, run['pipeline_id'],
                                       data.get('error_message', 'Manual status update'))

    return get_run_by_id(db, run_id)
