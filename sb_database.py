import sqlite3

def init_db():
    conn = sqlite3.connect("bulletins.db")
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
            ad_effective_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(file_name, summary, aircraft, ata, system, action,
               compliance, reason, sb_id, group, is_compliant,
               ad_number, ad_effective_date):

    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO bulletins (
            file_name, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant,
            ad_number, ad_effective_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file_name, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group, is_compliant,
        ad_number, ad_effective_date
    ))
    conn.commit()
    conn.close()

def fetch_all_bulletins():
    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bulletins")
    data = c.fetchall()
    conn.close()
    return data
