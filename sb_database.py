import sqlite3
import os

# Define database path
DB_PATH = "bulletins.db"

# Initialize database and create table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bulletins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            summary TEXT,
            aircraft TEXT,
            ata TEXT,
            system TEXT,
            action TEXT,
            compliance TEXT,
            ad TEXT
        )
    """)
    conn.commit()
    conn.close()

# Save a record to the database
def save_to_db(file, summary, aircraft, ata, system, action, compliance, ad=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO bulletins (file, summary, aircraft, ata, system, action, compliance, ad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (file, summary, aircraft, ata, system, action, compliance, ad))
    conn.commit()
    conn.close()

# Fetch all records
def fetch_all_bulletins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM bulletins ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows
