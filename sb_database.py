import sqlite3

def init_db():
    conn = sqlite3.connect("sb_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bulletins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            summary TEXT,
            aircraft TEXT,
            ata TEXT,
            system TEXT,
            action TEXT,
            compliance TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(filename, summary, aircraft, ata, system, action, compliance):
    conn = sqlite3.connect("sb_data.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO bulletins (filename, summary, aircraft, ata, system, action, compliance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (filename, summary, aircraft, ata, system, action, compliance))
    conn.commit()
    conn.close()

def fetch_all_bulletins():
    conn = sqlite3.connect("sb_data.db")
    df = None
    try:
        df = conn.cursor().execute("SELECT * FROM bulletins").fetchall()
    finally:
        conn.close()
    return df
