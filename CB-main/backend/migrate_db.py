import sqlite3

conn = sqlite3.connect('sentinai.db')
cursor = conn.cursor()

# Add missing severity column
cursor.execute('ALTER TABLE incidents ADD COLUMN severity TEXT DEFAULT "medium"')

# Add missing metadata_json column  
cursor.execute('ALTER TABLE incidents ADD COLUMN metadata_json TEXT')

conn.commit()
conn.close()
print("✅ Database updated!")