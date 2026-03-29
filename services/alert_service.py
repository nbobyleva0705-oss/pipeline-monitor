"""AlertRule and AlertEvent business logic."""


def validate_alert_rule(data):
    errors = []
    if not data.get('pipeline_id', '').strip():
        errors.append('pipeline_id is required')
    if not data.get('name', '').strip():
        errors.append('name is required')
    if not data.get('condition', '').strip():
        errors.append('condition is required')
    return errors


def create_alert_rule(db, data):
    pipeline = db.execute(
        "SELECT id FROM pipelines WHERE id = ?", (data['pipeline_id'],)
    ).fetchone()
    if not pipeline:
        raise ValueError(f"Pipeline '{data['pipeline_id']}' not found")

    db.execute(
        "INSERT INTO alert_rules (pipeline_id, name, condition, enabled) VALUES (?, ?, ?, ?)",
        (
            data['pipeline_id'].strip(),
            data['name'].strip(),
            data['condition'].strip(),
            1 if data.get('enabled', True) else 0,
        ),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM alert_rules WHERE pipeline_id = ? ORDER BY created_at DESC LIMIT 1",
        (data['pipeline_id'],),
    ).fetchone()
    return dict(row)


def get_all_alert_rules(db):
    rows = db.execute(
        """SELECT ar.*, p.name AS pipeline_name
           FROM alert_rules ar
           LEFT JOIN pipelines p ON ar.pipeline_id = p.id
           ORDER BY ar.created_at DESC"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_alert_rule_by_id(db, rule_id):
    row = db.execute(
        """SELECT ar.*, p.name AS pipeline_name
           FROM alert_rules ar
           LEFT JOIN pipelines p ON ar.pipeline_id = p.id
           WHERE ar.id = ?""",
        (rule_id,),
    ).fetchone()
    return dict(row) if row else None


def patch_alert_rule(db, rule_id, data):
    rule = db.execute("SELECT * FROM alert_rules WHERE id = ?", (rule_id,)).fetchone()
    if not rule:
        return None
    enabled = data.get('enabled')
    if enabled is not None:
        db.execute(
            "UPDATE alert_rules SET enabled = ? WHERE id = ?",
            (1 if enabled else 0, rule_id),
        )
        db.commit()
    return get_alert_rule_by_id(db, rule_id)


def delete_alert_rule(db, rule_id):
    rule = db.execute("SELECT id FROM alert_rules WHERE id = ?", (rule_id,)).fetchone()
    if not rule:
        return False
    db.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))
    db.commit()
    return True


def get_all_alerts(db):
    rows = db.execute(
        """SELECT ae.*, p.name AS pipeline_name, r.status AS run_status
           FROM alert_events ae
           LEFT JOIN pipelines p ON ae.pipeline_id = p.id
           LEFT JOIN job_runs r ON ae.run_id = r.id
           ORDER BY ae.created_at DESC"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_alert_by_id(db, alert_id):
    row = db.execute(
        """SELECT ae.*, p.name AS pipeline_name
           FROM alert_events ae
           LEFT JOIN pipelines p ON ae.pipeline_id = p.id
           WHERE ae.id = ?""",
        (alert_id,),
    ).fetchone()
    return dict(row) if row else None
