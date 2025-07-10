# sb_database.py
import sqlite3

def init_db():
    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bulletins (
            id INTEGER PRIMARY KEY,
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
            amendment TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(
    filename, summary, aircraft, ata, system, action,
    compliance, reason, sb_id, group_name, is_compliant,
    ad_number, ad_effective_date, ad_link, ad_applicability, amendment
):
    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO bulletins (
            file_name, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant,
            ad_number, ad_effective_date, ad_link, ad_applicability, amendment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group_name, is_compliant,
        ad_number, ad_effective_date, ad_link, ad_applicability, amendment
    ))
    conn.commit()
    conn.close()

def fetch_all_bulletins():
    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute('''
        SELECT sb_id, aircraft, ata, system, action, compliance, group_id,
               is_compliant, ad_number, ad_effective_date, ad_link,
               ad_applicability, amendment
        FROM bulletins
    ''')
    rows = c.fetchall()
    conn.close()
    return rows
