import json
from fastapi import FastAPI
from models import Mediatype,User, Status
from tmbd_requests import search_movie,search_tv
from database import create_user_db,create_watchlist
create_user_db()
create_watchlist()
app = FastAPI()

@app.post("/auth/register")

@app.post("/auth/login")


@app.get("/")
async def home():
    return {"Hello":"World"}

@app.get("/search")
async def search(query : str, media_type : Mediatype = Mediatype.movie):
    if media_type == "movie":
        result = search_movie(query)
    else:
        result = search_tv(query)
    return result
@app.get("/favourites")   

@app.get("/watchlist")
async def display_watchlist():
    pass

@app.post("/watchlist")
async def add_to_watchlist():
    pass
@app.put("/watchlist/{id}")
async def edit_watchlist():
    pass