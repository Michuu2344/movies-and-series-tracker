
import psycopg2
from psycopg2 import pool
import os   
from dotenv import load_dotenv
from backend.tmdb_requests import get_details_movie,get_details_tv
from datetime import datetime
from fastapi import HTTPException
current_time = datetime.now().isoformat()
from backend.models import EditWatchListItem
from contextlib import contextmanager
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

db_pool = pool.ThreadedConnectionPool(minconn=1,maxconn=10,dsn=DATABASE_URL)


@contextmanager
def get_cursor():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)

def create_watchlist():
    with get_cursor() as cur:      
        cur.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                tmdb_id INTEGER NOT NULL,
                media_type TEXT ,
                status TEXT NOT NULL,
                is_favourite BOOLEAN NOT NULL DEFAULT FALSE,
                rating INTEGER,
                added_at TIMESTAMP NOT NULL);''')
                
def create_media_cache():
    with get_cursor() as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS media_cache(tmdb_id INTEGER,
                       media_type TEXT,
                       title TEXT,
                       release_date TEXT,
                       poster_path TEXT,
                       last_updated TIMESTAMP,
                       PRIMARY KEY(tmdb_id,media_type));''')
def create_user_db():
    with get_cursor() as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT,
                email TEXT,
                full_name TEXT,
                hashed_password TEXT)''')

#lepszym rozwiazaniem bedzie redis i przechowywanie tych danych w pamieci podrecznej
def create_recently_viewed():
    with get_cursor as cur:
        sql_script = '''CREATE TABLE IF NOT EXISTS recently_viewed (
    
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                tmdb_id INTEGER NOT NULL,
                media_type VARCHAR(10) NOT NULL,
                viewed_at TIMESTAMP NOT NULL DEFAULT NOW(),
                UNIQUE (user_id,tmdb_id,media_type)
                );
                CREATE INDEX IF NOT EXISTS idx_recently_viewed_user_time 
                ON recently_viewed (user_id, viewed_at DESC);'''
        cur.execute(sql_script) 

def add_to_recently_viewed():
    with get_cursor() as cur:
        sql_script = '''INSERT INTO recently_viewed (user_id,tmdb_id,media_type,viewed_at) VALUES (%s,%s,%s,%s);'''
        cur.execute(sql_script)

def format_media_row(row):
    year = row[3].split("-")[0] if row[3] else "N/A"
    return {"tmdb_id":row[0],
            "media_type": row[1],
            "title":row[2],
            "release_date":year,
            "status":row[4],
            "rating":row[5],
            "poster_url":f"https://image.tmdb.org/t/p/w500{row[6]}" if row[6] is not None else None,
            "is_favourite" : row[7]
            }

def format_recently_viewed_row(row):
    return {"tmdb_id":row[0],
            "media_type": row[1],
            "title":row[2],}    

def display_watchlist_items(user_id):
    with get_cursor() as cur:
        cur.execute('''SELECT 
                w.tmdb_id,
                w.media_type,
                m.title,
                m.release_date,
                w.status,
                w.rating,
                m.poster_path,
                w.is_favourite
                FROM watchlist w
                LEFT JOIN media_cache m
                    ON w.tmdb_id = m.tmdb_id
                    AND w.media_type = m.media_type
                WHERE w.user_id = %s''',(user_id,))   
        rows = cur.fetchall()
        watchlist = [format_media_row(row) for row in rows]
        return watchlist



def display_favourite_items(user_id):
    with get_cursor() as cur:
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
                WHERE user_id = %s AND w.is_favourite = %s''',(user_id,True,))
        rows = cur.fetchall()
    
        favourites = [format_media_row(row) for row in rows]
        return favourites

def check_watchlist_item(item,user):
    with get_cursor() as cur:
        cur.execute('''SELECT 1 from watchlist WHERE tmdb_id = %s AND media_type = %s AND user_id = %s''',
                (item.tmdb_id,item.media_type.value,user.id))
    
        if cur.fetchone():
            return True
        else:
            return False
        
def check_if_item_is_on_watchlist(tmdb_id,user_id,media_type):
    with get_cursor() as cur:
        cur.execute('''SELECT 1 from watchlist WHERE user_id = %s AND tmdb_id = %s AND media_type = %s''',(user_id,tmdb_id,media_type))
        if cur.fetchone():
            return True
        else:
            return False
  
def check_if_item_is_favourite(tmdb_id,user_id,media_type):
    with get_cursor() as cur:
        cur.execute('''SELECT 1 from watchlist WHERE is_favourite = %s AND user_id = %s AND tmdb_id = %s AND media_type = %s''',(True,user_id,tmdb_id,media_type))

        if cur.fetchone():
            return True
        else:
            return False

def add_watchlist_item_db(item,user):
    
    if check_watchlist_item(item,user) == True:
        raise HTTPException(status_code=409,detail="This item is already on your watchlist")
    media_type =  item.media_type.value    

    with get_cursor() as cur:
        cur.execute('''SELECT 1 FROM media_cache WHERE tmdb_id = %s AND media_type = %s''',(item.tmdb_id,media_type,))
        cached = cur.fetchone() is not None
        
    data = None
    if not cached:
        if(media_type == "movie"):
            data = get_details_movie(item.tmdb_id)
        else:
            data = get_details_tv(item.tmdb_id)
    with get_cursor() as cur:
        if data:
            cur.execute('''INSERT INTO media_cache 
                                    (tmdb_id,
                                    media_type,
                                    title,
                                    release_date,
                                    poster_path, last_updated) 
                                    VALUES (%s,%s,%s,%s,%s,%s)
                                    ON CONFLICT (tmdb_id,media_type) DO NOTHING ''',
                                    (item.tmdb_id,media_type,
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
                (user.id,item.tmdb_id,media_type,item.status.value,item.rating,item.is_favourite,current_time,))
        
    return {"message":f"Successfully added to watchlist item with tmdb_id of: {item.tmdb_id}"}

def edit_watchlist_item(id : int,user_id : int,edited_item : EditWatchListItem,media_type : str):
    
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
    with get_cursor() as cur:   
        cur.execute(sql,tuple(values))

    
    return {"status":"success"}
def get_user_from_db(username):
    with get_cursor() as cur:  
        cur.execute('''SELECT * FROM users WHERE username =%s''',(username,))

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
def save_user_to_db(new_user,hashed):
    with get_cursor() as cur:
        cur.execute('''INSERT INTO users (username,email,full_name,hashed_password) VALUES (%s,%s,%s,%s)''',
                (new_user.username,new_user.email,new_user.full_name,hashed,))
        
def delete_watchlist_item(id,user_id,media_type):
    with get_cursor() as cur:
        cur.execute('''DELETE FROM watchlist WHERE tmdb_id = %s AND user_id = %s AND media_type =%s''',(id,user_id,media_type,))
        deleted = cur.rowcount
        if deleted == 0:
            raise HTTPException(status_code=404,detail=f"No item found with tmdb_id of {id}")
        
    return {"message":f"Succesfully deleted a {media_type} item with tmdb_id of {id}"}

def check_user_exists(username : str):
    with get_cursor() as cur:
        cur.execute('''SELECT 1 FROM users WHERE username = %s''',(username,))
        result = cur.fetchone()
        return result is not None
        
def addItemFavourites(tmdb_id : int, user_id : int,media_type : str,isFavourite : bool):
    with get_cursor() as cur:
        cur.execute('''UPDATE watchlist SET is_favourite = %s WHERE user_id = %s AND tmdb_id = %s AND media_type = %s''',
                (isFavourite,user_id,tmdb_id,media_type,))

