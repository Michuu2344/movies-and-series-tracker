import sqlite3

def create_watchlist():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tmbd_id TEXT NOT NULL,
                media_type TEXT ,
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
def add_to_watchlist():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO watchlist ()''')
def get_user_from_db(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM user WHERE username = ?''',(username,))
    try:
        result = cur.fetchone()
        
        if result is None:
            return None
        
        return {
            "id":result[0],
            "username":result[1],
            "email":result[2],
            "full_name":result[3],
            "hashed_password":result[4]

        }
    
    finally:    
        conn.close()
def save_user_to_db(new_user,hashed):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO user (username,email,full_name,hashed_password) VALUES (?,?,?,?)''',
                (new_user.username,new_user.email,new_user.full_name,hashed))
    conn.commit()
    conn.close()