"""Dataset business logic."""


def validate_dataset(data):
    errors = []
    if not data.get('name', '').strip():
        errors.append('name is required')
    if not data.get('owner', '').strip():
        errors.append('owner is required')
    return errors


def create_dataset(db, data):
    db.execute(
        """INSERT INTO datasets (name, description, owner, schema_version)
           VALUES (?, ?, ?, ?)""",
        (
            data['name'].strip(),
            data.get('description', '').strip() or None,
            data['owner'].strip(),
            int(data.get('schema_version', 1)),
        ),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM datasets WHERE name = ?", (data['name'].strip(),)
    ).fetchone()
    return dict(row)


def get_all_datasets(db):
    rows = db.execute("SELECT * FROM datasets ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def get_dataset_by_id(db, dataset_id):
    row = db.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    return dict(row) if row else None
