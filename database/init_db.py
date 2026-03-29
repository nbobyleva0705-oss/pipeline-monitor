"""Initialize the SQLite database: apply schema and seed data."""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'pipeline_monitor.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')
SEED_PATH = os.path.join(BASE_DIR, 'seed_data.sql')


def init_db(seed=True):
    db_path = os.path.normpath(DB_PATH)
    print(f"Initializing database at: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    print("Schema applied.")

    if seed:
        with open(SEED_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        print("Seed data inserted.")

    conn.commit()
    conn.close()
    print("Done.")


if __name__ == '__main__':
    init_db()
