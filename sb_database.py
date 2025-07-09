import sqlite3

# Initialize the database and create the table if it doesn't exist
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
            ad_suggestion TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save a new bulletin to the database
def save_to_db(file_name, summary, aircraft, ata, system, action,
               compliance, reason, sb_id, group, is_compliant, ad_suggestion):
    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO bulletins (
            file_name, summary, aircraft, ata, system, action,
            compliance, reason, sb_id, group_id, is_compliant, ad_suggestion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file_name, summary, aircraft, ata, system, action,
        compliance, reason, sb_id, group, is_compliant, ad_suggestion
    ))
    conn.commit()
    conn.close()

# Fetch all saved bulletins
def fetch_all_bulletins():
    conn = sqlite3.connect("bulletins.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bulletins")
    rows = c.fetchall()
    conn.close()
    return rows
