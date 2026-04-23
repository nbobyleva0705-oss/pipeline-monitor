"""Pipeline business logic."""
import json


def validate_pipeline(data):
    errors = []
    if not data.get('name', '').strip():
        errors.append('name is required')
    if not data.get('dataset_id', '').strip():
        errors.append('dataset_id is required')
    return errors


def create_pipeline(db, data):
    # Business rule: dataset must exist
    ds = db.execute(
        "SELECT id FROM datasets WHERE id = ?", (data['dataset_id'],)
    ).fetchone()
    if not ds:
        raise ValueError(f"Dataset '{data['dataset_id']}' not found")

    db.execute(
        """INSERT INTO pipelines (dataset_id, name, description, schedule, active)
           VALUES (?, ?, ?, ?, ?)""",
        (
            data['dataset_id'].strip(),
            data['name'].strip(),
            data.get('description', '').strip() or None,
            data.get('schedule', '').strip() or None,
            1 if data.get('active', True) else 0,
        ),
    )
    db.commit()

    pipeline = db.execute(
        "SELECT * FROM pipelines WHERE name = ? ORDER BY created_at DESC LIMIT 1",
        (data['name'].strip(),),
    ).fetchone()
    pipeline_id = pipeline['id']

    # Create initial version
    config = json.dumps(data.get('config', {}))
    db.execute(
        "INSERT INTO pipeline_versions (pipeline_id, version, config) VALUES (?, 1, ?)",
        (pipeline_id, config),
    )
    db.commit()
    return dict(pipeline)


def get_all_pipelines(db):
    rows = db.execute(
        """SELECT p.*,
                  d.name AS dataset_name,
                  (SELECT status FROM job_runs WHERE pipeline_id = p.id
                   ORDER BY started_at DESC LIMIT 1) AS last_run_status,
                  (SELECT started_at FROM job_runs WHERE pipeline_id = p.id
                   ORDER BY started_at DESC LIMIT 1) AS last_run_at
           FROM pipelines p
           LEFT JOIN datasets d ON p.dataset_id = d.id
           ORDER BY p.created_at DESC"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_pipeline_by_id(db, pipeline_id):
    row = db.execute(
        """SELECT p.*, d.name AS dataset_name
           FROM pipelines p
           LEFT JOIN datasets d ON p.dataset_id = d.id
           WHERE p.id = ?""",
        (pipeline_id,),
    ).fetchone()
    if not row:
        return None

    pipeline = dict(row)

    # Attach recent runs
    runs = db.execute(
        "SELECT * FROM job_runs WHERE pipeline_id = ? ORDER BY started_at DESC LIMIT 10",
        (pipeline_id,),
    ).fetchall()
    pipeline['runs'] = [dict(r) for r in runs]

    # Attach alert rules
    rules = db.execute(
        "SELECT * FROM alert_rules WHERE pipeline_id = ?", (pipeline_id,)
    ).fetchall()
    pipeline['alert_rules'] = [dict(r) for r in rules]

    # Attach run statistics
    stats = db.execute(
        """SELECT
               COUNT(*) AS total_runs,
               SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS success_runs,
               SUM(CASE WHEN status='failed'  THEN 1 ELSE 0 END) AS failed_runs,
               AVG(CASE WHEN finished_at IS NOT NULL
                   THEN (julianday(finished_at) - julianday(started_at)) * 86400
                   ELSE NULL END) AS avg_runtime_seconds
           FROM job_runs WHERE pipeline_id = ?""",
        (pipeline_id,),
    ).fetchone()
    pipeline['stats'] = dict(stats)

    # Attach current version
    current_ver = db.execute(
        "SELECT * FROM pipeline_versions WHERE pipeline_id = ? ORDER BY version DESC LIMIT 1",
        (pipeline_id,),
    ).fetchone()
    pipeline['current_version'] = dict(current_ver) if current_ver else None

    return pipeline


def get_pipeline_versions(db, pipeline_id):
    rows = db.execute(
        "SELECT * FROM pipeline_versions WHERE pipeline_id = ? ORDER BY version DESC",
        (pipeline_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def create_pipeline_version(db, pipeline_id, data):
    pipeline = db.execute("SELECT id FROM pipelines WHERE id = ?", (pipeline_id,)).fetchone()
    if not pipeline:
        raise ValueError("Pipeline not found")

    last = db.execute(
        "SELECT version FROM pipeline_versions WHERE pipeline_id = ? ORDER BY version DESC LIMIT 1",
        (pipeline_id,),
    ).fetchone()
    next_version = (last['version'] + 1) if last else 1

    config = json.dumps(data.get('config', {}))
    db.execute(
        "INSERT INTO pipeline_versions (pipeline_id, version, config) VALUES (?, ?, ?)",
        (pipeline_id, next_version, config),
    )
    db.commit()

    row = db.execute(
        "SELECT * FROM pipeline_versions WHERE pipeline_id = ? AND version = ?",
        (pipeline_id, next_version),
    ).fetchone()
    return dict(row)


def patch_pipeline(db, pipeline_id, data):
    pipeline = db.execute("SELECT * FROM pipelines WHERE id = ?", (pipeline_id,)).fetchone()
    if not pipeline:
        return None
    fields, params = [], []
    if 'active' in data:
        fields.append("active = ?")
        params.append(1 if data['active'] else 0)
    if fields:
        params.append(pipeline_id)
        db.execute(f"UPDATE pipelines SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return get_pipeline_by_id(db, pipeline_id)
