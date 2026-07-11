import sqlite3
from tmdb_requests import get_details_movie,get_details_tv
from datetime import datetime
from fastapi import HTTPException
current_time = datetime.now().isoformat()
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
    year = row[2].split("-")[0] if row[2] else "N/A"
    return {"tmdb_id":row[0],
            "title":row[1],
            "year":year,
            "status":row[3],
            "rating":row[4],
            "poster_url":f"https://image.tmdb.org/t/p/w500{row[5]}" if row[5] is not None else None
            }
    
def display_watchlist_items(user_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT 
                w.tmdb_id,
                m.title,
                m.release_date,
                w.status,
                w.rating,
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
def display_favourite_items(user_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT
                w.tmdb_id,
                m.title,
                m.release_date,
                w.status,
                w.rating,
                m.poster_path
                FROM watchlist w 
                LEFT JOIN media_cache m 
                    ON w.tmdb_id = m.tmdb_id 
                    AND w.media_type = m.media_type
                WHERE user_id = ? AND w.status = ?''',(user_id,"favourite",))
    rows = cur.fetchall()
    conn.close()
    favourites = [format_media_row(row) for row in rows]
    return favourites
def check_watchlist_item(item,user):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT 1 from watchlist WHERE tmdb_id = ? AND media_type = ? AND user_id = ?''',
                (item.tmdb_id,item.media_type.value,user.id))
    conn.close()
    if cur.fetchone():
        return True
    else:
        return False
    
def add_watchlist_item_db(item,user):
    if check_watchlist_item(item,user) == True:
        return {"message":"This item is already on your watchlist"}
    
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''SELECT 1 FROM media_cache WHERE tmdb_id = ? AND media_type = ?''',(item.tmdb_id,item.media_type.value))
    if not cur.fetchone():
        if item.media_type.value == "movie":
            data = get_details_movie(item.tmdb_id)
            cur.execute('''INSERT INTO media_cache 
                        (tmdb_id,
                        media_type,
                        title,
                        release_date,
                        poster_path, last_updated) 
                        VALUES (?,?,?,?,?,?) ''',
                        (item.tmdb_id,item.media_type.value,
                         data['name'],
                         data['release_date'],
                         data['poster'],
                         current_time,
                         ))
        else:
            data = get_details_tv(item.tmdb_id)
            cur.execute('''INSERT INTO media_cache 
                        (tmdb_id,
                        media_type,
                        title,
                        release_date,
                        poster_path, last_updated) 
                        VALUES (?,?,?,?,?,?) ''',
                        (item.tmdb_id,item.media_type.value,
                         data['name'],
                         data['release_date'],
                         data['poster'],
                         current_time,
                         ))
    

    cur.execute('''INSERT INTO watchlist (user_id,
                tmdb_id,
                media_type,
                status,
                rating,
                added_at) VALUES (?,?,?,?,?,?)''',
                (user.id,item.tmdb_id,item.media_type.value,item.status,item.rating,current_time,))
    conn.commit()
    conn.close()
    return {"message":f"Successfully added to watchlist item with tmdb_id of: {item.tmdb_id}"}
def edit_watchlist_item(id,user_id,edited_item,media_type):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    fields = []
    values = []
    if edited_item.status is not None:
        fields.append("status = ?")
        values.append(edited_item.status.value)
    if edited_item.rating is not None:
        fields.append("rating = ?")
        values.append(edited_item.rating)
    if not fields:
        return {"Error":"Nothing to update"}
    values.append(id)
    values.append(user_id)
    values.append(media_type)
    sql = f"UPDATE watchlist SET {' ,'.join(fields)} WHERE tmdb_id = ? AND user_id = ? AND media_type = ?"
    cur.execute(sql,tuple(values))
    conn.commit()
    conn.close()
    return {"status":"success"}
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
def delete_watchlist_item(id,user_id,media_type):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''DELETE FROM watchlist WHERE tmdb_id = ? AND user_id = ? AND media_type = ?''',(id,user_id,media_type,))
    rows = cur.rowcount
    conn.commit()
    conn.close()
    if rows == 0:
        raise HTTPException(status_code=404,detail=f"No item found with tmdb_id of {id}")
    return {"message":f"Succesfully deleted a {media_type} item with tmdb_id of {id}"}