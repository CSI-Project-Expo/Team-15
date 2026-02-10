import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parent / 'sentinai.db'
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
for table in ['events','cameras','recordings']:
    try:
        cur.execute(f"PRAGMA table_info('{table}')")
        cols = cur.fetchall()
        print(table)
        for c in cols:
            print(' ', c)
    except Exception as e:
        print('error', table, e)
conn.close()