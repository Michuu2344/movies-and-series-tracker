import json
from datetime import datetime, timedelta,timezone
from typing import Annotated
from fastapi import FastAPI,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from models import Mediatype,User, Status,UserRegister,WatchListItem,EditWatchListItem
from tmdb_requests import search_movie,search_tv,get_details_tv,get_details_movie
from database import create_user_db,create_watchlist,save_user_to_db,add_watchlist_item_db,edit_watchlist_item,display_watchlist_items,create_media_cache,display_favourite_items
from authentication import authenticate_user,Token,ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,get_password_hash,get_current_user
from authentication import oauth2_scheme
now = datetime.now()
date = now.strftime("%Y/%m/%d")
create_user_db()
create_watchlist()
create_media_cache()
app = FastAPI()
@app.post("/auth/register")
async def register_user(user : UserRegister):
    hashed = get_password_hash(user.password)
    save_user_to_db(user,hashed)
    return {f"Succesfully signed user with username: {user.username} "}
@app.post("/auth/login")
async def login_for_access_token(form_data : Annotated[OAuth2PasswordRequestForm,Depends()],)->Token:
    user = authenticate_user(form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub":user.username},expires_delta=access_token_expires)
    return Token(access_token=access_token,token_type="bearer")

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
@app.get("/media/{tmdb_id}")
async def get_details(tmdb_id : int, media_type: Mediatype = Mediatype.movie):
    if media_type =="movie":
        result = get_details_movie(tmdb_id)
    else:
        result = get_details_tv(tmdb_id)
    return result
@app.get("/me")
async def get_my_information(user: Annotated[User,Depends(get_current_user)]):
    return {f"{user.username} - {user.full_name}"}

@app.get("/favourites")   
async def display_favourites(user: Annotated[User,Depends(get_current_user)]):
    return display_favourite_items(user.id)
@app.get("/watchlist")
async def display_watchlist(user : Annotated[User,Depends(get_current_user)]):
    return display_watchlist_items(user.id)
    
@app.post("/watchlist")
async def add_to_watchlist(item: WatchListItem,user : Annotated[User,Depends(get_current_user)]):
    
    add_watchlist_item_db(item,user)
    
    return {f"Successfully added to watchlist item with id: {item.tmdb_id}"}
    

@app.put("/watchlist/{tmdb_id}")
async def edit_watchlist(tmdb_id: int,item : EditWatchListItem, user : Annotated[User,Depends(get_current_user)],media_type: Mediatype = Mediatype.movie,):
   return edit_watchlist_item(tmdb_id,user.id,item,media_type)
    