import sqlite3

def create_watchlist():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                id INT SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                tmbd_id TEXT NOT NULL,
                media type TEXT NOT NULL,
                status TEXT NOT NULL,
                rating TEXT,
                added_at TEXT);''')
    conn.commit()
    conn.close()
def create_user_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS user (
                username TEXT,
                email TEXT,
                full_name TEXT,
                hashed_password TEXT)''')
    conn.commit()
    conn.close()
create_watchlist()
create_user_db()