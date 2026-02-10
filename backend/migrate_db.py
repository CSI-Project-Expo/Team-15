import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parent / 'sentinai.db'
print('DB:', DB)
conn = sqlite3.connect(str(DB))
cur = conn.cursor()

def add_column_if_missing(table, col_name, col_def):
    cur.execute(f"PRAGMA table_info('{table}')")
    cols = [c[1] for c in cur.fetchall()]
    if col_name in cols:
        print(f"{table}.{col_name} already exists")
        return
    print(f"Adding column {col_name} to {table}")
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
    conn.commit()

# incidents
add_column_if_missing('incidents', 'severity', "TEXT DEFAULT 'medium'")
add_column_if_missing('incidents', 'confidence', 'REAL')
add_column_if_missing('incidents', 'acknowledged', 'INTEGER DEFAULT 0')
add_column_if_missing('incidents', 'metadata_json', 'TEXT')

# events
add_column_if_missing('events', 'severity', "TEXT DEFAULT 'normal'")
add_column_if_missing('events', 'details', 'TEXT')

# recordings: ensure columns exist (optional)
add_column_if_missing('recordings', 'thumbnail', 'TEXT')
add_column_if_missing('recordings', 'has_alerts', 'INTEGER DEFAULT 0')

print('Migration completed')
conn.close()
