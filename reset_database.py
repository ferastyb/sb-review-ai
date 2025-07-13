
import sqlite3
import os

DB_FILE = "bulletins.db"

# Delete old database
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Deleted old bulletins.db")

# Recreate schema
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute('''
CREATE TABLE bulletins (
    sb_id TEXT,
    summary TEXT,
    aircraft TEXT,
    ata INTEGER,
    system TEXT,
    action TEXT,
    compliance TEXT,
    reason TEXT,
    group_id TEXT,
    is_compliant BOOLEAN,
    ad_number TEXT,
    ad_effective_date TEXT,
    ad_link TEXT,
    ad_applicability TEXT,
    ad_amendment TEXT
)
''')

conn.commit()
conn.close()
print("✅ New database created with correct schema.")
