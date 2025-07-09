import sqlite3
import os

DB_PATH = "bulletins.db"

def init_db():
    # If DB doesn't exist or table missing, create it
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bulletins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            summary TEXT,
            aircraft TEXT,
            ata TEXT,
            system TEXT,
            action TEXT,
            compliance TEXT,
            reason TEXT,
            sb_id TEXT,
            group_id TEXT,
            is_compliant BOOLEAN,
            ad_suggestion TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(file, summary, aircraft, ata, system, action,
               compliance, reason, sb_id, group_id, is_compliant, ad_suggestion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO bulletins (
            file, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant, ad_suggestion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group_id, is_compliant, ad_suggestion
    ))
    conn.commit()
    conn.close()

def fetch_all_bulletins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM bulletins")
    results = c.fetchall()
    conn.close()
    return results
