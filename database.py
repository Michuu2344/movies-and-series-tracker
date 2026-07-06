import sqlite3

def create_watchlist():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tmdb_id INTEGER NOT NULL,
                media_type TEXT ,
                status TEXT NOT NULL,
                rating INTEGER,
                added_at TEXT);''')
    conn.commit()
    conn.close()
def create_media_cache():
    conn = sqlite3.connect('database.db')
    cur = conn.execute('''CREATE TABLE IF NOT EXISTS media_cache(tmdb_id INT,
                       media_type TEXT,
                       title TEXT,
                       release_date TEXT,
                       poster_path TEXT,
                       last_updated TIMESTAMP,
                       PRIMARY KEY(tmdb_id,media_type));''')
    conn.commit()
    conn.close()
def create_user_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                full_name TEXT,
                hashed_password TEXT)''')
    conn.commit()
    conn.close()
def format_media_row(row):
    return {"title":row[0],
            "year":row[1].split("-") if row[1] else "N/A",
            "status":row[2],
            "rating":row[3],
            "poster_url":f"https://image.tmdb.org/t/p/w500{row[4]}" if row[4] is not None else None
            }
def display_watchlist_items(user_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT 
                w.tmdb_id,
                w.status,
                w.rating,
                m.title,
                m.release_date,
                m.poster_path
                FROM watchlist w
                LEFT JOIN media_cache m
                    ON w.tmdb_id = m.tmdb_id
                    AND w.media_type = m.media_type
                WHERE user_id = ?''',(user_id,))   
    rows = cur.fetchall()
    conn.close()
    watchlist = [format_media_row(row) for row in rows]
    return watchlist
    
    
   

def add_watchlist_item_db(item,user,date):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT 1 FROM media_cache WHERE tmdb_id = ? AND media_type = ?''',(item.tmdb_id,item.media_type.value))
    if not cur.fetchone():
        #pobieramy z api
        pass
    
    
    #cur.execute('''INSERT INTO watchlist (user_id, tmdb_id,media_type,status,rating,added_at) VALUES (?,?,?,?,?,?)''',
                #(user.id,item.tmdb_id,item.media_type,item.status,item.rating,date,))
    
    conn.close()
def edit_watchlist_item(id,user_id,edited_item):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if edited_item.status and edited_item == None:
        conn.close()
    cur.execute('''UPDATE watchlist SET status = ?,rating = ? WHERE tmdb_id = ?, user_id = ?''',
                (edited_item.status,edited_item.rating,id,user_id,))
    conn.commit()
    conn.close()
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

