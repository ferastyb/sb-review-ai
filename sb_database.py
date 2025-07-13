import sqlite3
import os

DB_NAME = "bulletins.db"

def initialize_database():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE bulletins (
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
    filename,
    summary,
    aircraft,
    ata,
    system,
    action,
    compliance,
    reason,
    sb_id,
    group,
    is_compliant,
    ad_number,
    ad_effective_date,
    ad_link,
    ad_applicability,
    ad_amendment
):
    initialize_database()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO bulletins (
            file_name, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant,
            ad_number, ad_effective_date, ad_link,
            ad_applicability, ad_amendment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group, is_compliant,
        ad_number, ad_effective_date, ad_link,
        ad_applicability, ad_amendment
    ))
    conn.commit()
    conn.close()

def fetch_all_bulletins():
    initialize_database()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT
            sb_id, aircraft, ata, system, action,
            compliance, group_id, is_compliant,
            ad_number, ad_effective_date, ad_link,
            ad_applicability, ad_amendment
        FROM bulletins
    ''')
    rows = c.fetchall()
    conn.close()
    return rows
