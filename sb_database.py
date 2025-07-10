# sb_database.py
import sqlite3

DB_PATH = "sb_data.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bulletins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                summary TEXT,
                aircraft TEXT,
                ata TEXT,
                system TEXT,
                action TEXT,
                compliance TEXT,
                reason TEXT,
                sb_id TEXT,
                group_name TEXT,
                is_compliant TEXT,
                ad_number TEXT,
                ad_effective_date TEXT,
                ad_link TEXT,
                ad_applicability TEXT,
                amendment TEXT
            )
        ''')

def save_to_db(filename, summary, aircraft, ata, system, action, compliance, reason,
               sb_id, group_name, is_compliant, ad_number, ad_effective_date,
               ad_link, ad_applicability, amendment):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO bulletins (
                filename, summary, aircraft, ata, system, action,
                compliance, reason, sb_id, group_name, is_compliant,
                ad_number, ad_effective_date, ad_link, ad_applicability, amendment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_name, str(is_compliant),
            ad_number, ad_effective_date, ad_link, ad_applicability, amendment
        ))

def fetch_all_bulletins():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute('SELECT filename, aircraft, ata, system, action, compliance, group_name, is_compliant, ad_number, ad_effective_date, ad_link, ad_applicability, amendment FROM bulletins').fetchall()
    return rows
