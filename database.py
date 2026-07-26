import sqlite3

DB_NAME = "transactions.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            type TEXT,
            date TEXT,
            merchant TEXT,
            category TEXT,
            raw_message TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_transaction(amount, txn_type, date, merchant, category, raw_message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (amount, type, date, merchant, category, raw_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (amount, txn_type, date, merchant, category, raw_message))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    rows = cursor.fetchall()
    conn.close()
    return rows