import sqlite3
import os

DB_FILE = "bulletins.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bulletins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
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
            ad_number TEXT,
            ad_effective_date TEXT,
            ad_link TEXT,
            ad_applicability TEXT,
            ad_amendment TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(
    filename, summary, aircraft, ata, system, action,
    compliance, reason, sb_id, group, is_compliant,
    ad_number, ad_effective_date, ad_link, ad_applicability, ad_amendment
):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Always overwrite if SB already exists
    c.execute("DELETE FROM bulletins WHERE sb_id = ?", (sb_id,))

    c.execute('''
        INSERT INTO bulletins (
            file_name, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant,
            ad_number, ad_effective_date, ad_link, ad_applicability, ad_amendment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group, is_compliant,
        ad_number, ad_effective_date, ad_link, ad_applicability, ad_amendment
    ))

    conn.commit()
    conn.close()

def fetch_all_bulletins():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT
            sb_id, aircraft, ata, system, action,
            compliance, group_id, is_compliant,
            ad_number, ad_effective_date, ad_link, ad_applicability, ad_amendment
        FROM bulletins
        ORDER BY id DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows
