import sqlite3

# Initialize or upgrade the database schema
def init_db():
    conn = sqlite3.connect("sb_data.db")
    c = conn.cursor()
    c.execute("""
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
            amendment TEXT
        )
    """)
    conn.commit()
    conn.close()

# Save SB record
def save_to_db(
    filename, summary, aircraft, ata, system, action,
    compliance, reason, sb_id, group_name, is_compliant,
    ad_number, ad_effective_date, ad_link, ad_applicability, amendment
):
    conn = sqlite3.connect("sb_data.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO bulletins (
            file_name, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant,
            ad_number, ad_effective_date, ad_link, ad_applicability, amendment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group_name, is_compliant,
        ad_number, ad_effective_date, ad_link, ad_applicability, amendment
    ))
    conn.commit()
    conn.close()

# Fetch all records for display
def fetch_all_bulletins():
    conn = sqlite3.connect("sb_data.db")
    c = conn.cursor()
    c.execute("""
        SELECT 
            file_name, aircraft, ata, system, action, compliance,
            group_id, is_compliant, ad_number, ad_effective_date,
            ad_link, ad_applicability, amendment, summary
        FROM bulletins
        ORDER BY id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows
