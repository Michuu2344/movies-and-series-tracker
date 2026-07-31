import sqlite3
import psycopg2
import os   
from dotenv import load_dotenv
from backend.tmdb_requests import get_details_movie,get_details_tv
from datetime import datetime
from fastapi import HTTPException
current_time = datetime.now().isoformat()
from backend.models import EditWatchListItem
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")



def create_watchlist(db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                tmdb_id INTEGER NOT NULL,
                media_type TEXT ,
                status TEXT NOT NULL,
                is_favourite BOOLEAN NOT NULL DEFAULT FALSE,
                rating INTEGER,
                added_at TIMESTAMP NOT NULL);''')
    conn.commit()
    conn.close()
def create_media_cache(db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur =conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS media_cache(tmdb_id INTEGER,
                       media_type TEXT,
                       title TEXT,
                       release_date TEXT,
                       poster_path TEXT,
                       last_updated TIMESTAMP,
                       PRIMARY KEY(tmdb_id,media_type));''')
    conn.commit()
    conn.close()
def create_user_db(db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT,
                email TEXT,
                full_name TEXT,
                hashed_password TEXT)''')
    conn.commit()
    conn.close()
def format_media_row(row):
    year = row[3].split("-")[0] if row[3] else "N/A"
    return {"tmdb_id":row[0],
            "media_type": row[1],
            "title":row[2],
            "year":year,
            "status":row[4],
            "rating":row[5],
            "poster_url":f"https://image.tmdb.org/t/p/w500{row[6]}" if row[6] is not None else None
            }
    
def display_watchlist_items(user_id,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''SELECT 
                w.tmdb_id,
                w.media_type,
                m.title,
                m.release_date,
                w.status,
                w.rating,
                m.poster_path
                FROM watchlist w
                LEFT JOIN media_cache m
                    ON w.tmdb_id = m.tmdb_id
                    AND w.media_type = m.media_type
                WHERE user_id = %s''',(user_id,))   
    rows = cur.fetchall()
    conn.close()
    watchlist = [format_media_row(row) for row in rows]
    return watchlist
def display_favourite_items(user_id,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
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
                WHERE user_id = %s AND w.status = %s''',(user_id,"favourite",))
    rows = cur.fetchall()
    conn.close()
    favourites = [format_media_row(row) for row in rows]
    return favourites
def check_watchlist_item(item,user,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''SELECT 1 from watchlist WHERE tmdb_id = %s AND media_type = %s AND user_id = %s''',
                (item.tmdb_id,item.media_type.value,user.id))
    
    if cur.fetchone():
        conn.close()
        return True
    else:
        conn.close()
        return False
    
def add_watchlist_item_db(item,user,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    if check_watchlist_item(item,user) == True:
        raise HTTPException(status_code=409,detail="This item is already on your watchlist")
        
    
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''SELECT 1 FROM media_cache WHERE tmdb_id = %s AND media_type = %s''',(item.tmdb_id,item.media_type.value,))
    if not cur.fetchone():
        if item.media_type.value == "movie":
            data = get_details_movie(item.tmdb_id)
            cur.execute('''INSERT INTO media_cache 
                        (tmdb_id,
                        media_type,
                        title,
                        release_date,
                        poster_path, last_updated) 
                        VALUES (%s,%s,%s,%s,%s,%s) ''',
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
                        VALUES (%s,%s,%s,%s,%s,%s) ''',
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
                is_favourite,
                added_at) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                (user.id,item.tmdb_id,item.media_type.value,item.status.value,item.rating,item.is_favourite,current_time,))
    conn.commit()
    conn.close()
    return {"message":f"Successfully added to watchlist item with tmdb_id of: {item.tmdb_id}"}
def edit_watchlist_item(id : int,user_id : int,edited_item : EditWatchListItem,media_type : str,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL

    update_data = edited_item.model_dump(exclude_unset=True)

    
    
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    fields = []
    values = []
    if edited_item.status is not None:
        fields.append("status = %s")
        values.append(edited_item.status.value)
    if edited_item.rating is not None:
        fields.append("rating = %s")
        values.append(edited_item.rating)
    if not fields:
        return {"Error":"Nothing to update"}
    values.append(id)
    values.append(user_id)
    values.append(media_type)
    sql = f"UPDATE watchlist SET {' ,'.join(fields)} WHERE tmdb_id = %s AND user_id = %s AND media_type = %s"
    cur.execute(sql,tuple(values))
    conn.commit()
    conn.close()
    return {"status":"success"}
def get_user_from_db(username,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM users WHERE username =%s''',(username,))
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
def save_user_to_db(new_user,hashed,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''INSERT INTO users (username,email,full_name,hashed_password) VALUES (%s,%s,%s,%s)''',
                (new_user.username,new_user.email,new_user.full_name,hashed,))
    conn.commit()
    conn.close()
def delete_watchlist_item(id,user_id,media_type,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''DELETE FROM watchlist WHERE tmdb_id = %s AND user_id = %s AND media_type =%s''',(id,user_id,media_type,))
    rows = cur.rowcount
    conn.commit()
    conn.close()
    if rows == 0:
        raise HTTPException(status_code=404,detail=f"No item found with tmdb_id of {id}")
    return {"message":f"Succesfully deleted a {media_type} item with tmdb_id of {id}"}

def check_user_exists(username : str,db_name = None):
    if db_name is None:
        db_name = DATABASE_URL
    conn = psycopg2.connect(db_name)
    cur = conn.cursor()
    cur.execute('''SELECT 1 FROM users WHERE username = %s''',(username,))
    try:
        result = cur.fetchone()
        if result is not None:
            return True
        else:
            return False
    finally:
        conn.close()
    





