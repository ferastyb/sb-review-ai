# sb_database.py
import sqlite3

DB_FILE = "sb_data.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS service_bulletins (
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
                ad_effective_date TEXT
            )
        """)
        conn.commit()

def save_to_db(filename, summary, aircraft, ata, system, action, compliance,
               reason, sb_id, group_name, is_compliant, ad_number, ad_effective_date):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO service_bulletins (
                filename, summary, aircraft, ata, system, action, compliance,
                reason, sb_id, group_name, is_compliant, ad_number, ad_effective_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, summary, aircraft, ata, system, action, compliance,
            reason, sb_id, group_name, str(is_compliant), ad_number, ad_effective_date
        ))
        conn.commit()

def fetch_all_bulletins():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT
                filename, summary, aircraft, ata, system, action,
                compliance, group_name, is_compliant, ad_number, ad_effective_date
            FROM service_bulletins
        """)
        return c.fetchall()
