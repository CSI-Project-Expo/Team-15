import sqlite3, os
from pathlib import Path
DB = Path(__file__).resolve().parent / 'sentinai.db'
print('DB path:', DB)
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("PRAGMA table_info('incidents')")
cols = cur.fetchall()
print('incidents columns:')
for c in cols:
    print(c)
conn.close()