import json
from datetime import datetime, timedelta,timezone
from typing import Annotated
from fastapi import FastAPI,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from models import Mediatype,User, Status,UserRegister
from tmbd_requests import search_movie,search_tv,get_details_tv,get_details_movie
from database import create_user_db,create_watchlist,save_user_to_db
from authentication import authenticate_user,Token,ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,get_password_hash


create_user_db()
create_watchlist()
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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
@app.get("/media/{tmbd_id}")
async def get_details(tmbd_id : int, media_type: Mediatype = Mediatype.movie):
    if media_type =="movie":
        result = get_details_movie(tmbd_id)
    else:
        result = get_details_tv(tmbd_id)
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