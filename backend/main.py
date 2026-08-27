import json
import time
from datetime import datetime, timedelta,timezone
from typing import Annotated
from fastapi import FastAPI,HTTPException,Depends,status,Response,Request
from fastapi.responses import JSONResponse
from backend.ratelimiting import RateLimiterStore
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from backend.models import Mediatype,User, Status,UserRegister,WatchListItem,EditWatchListItem,FavouriteUpdate
from backend.tmdb_requests import search_movie,search_tv,get_details_tv,get_details_movie,get_trending_movies,get_popular_movies,get_popular_tv_shows,get_trending_tv_shows
from backend.database import create_user_db,create_watchlist,save_user_to_db,add_watchlist_item_db,edit_watchlist_item,display_watchlist_items,create_media_cache,display_favourite_items,delete_watchlist_item,check_user_exists,addItemFavourites,check_watchlist_item
from backend.authentication import authenticate_user,Token,ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,get_password_hash,get_current_user
from backend.authentication import set_auth_cookie

from fastapi.middleware.cors import CORSMiddleware


now = datetime.now()
date = now.strftime("%Y/%m/%d")
create_user_db()
create_watchlist()
create_media_cache()
app = FastAPI()
limiter = RateLimiterStore(max_tokens=50,refill_rate=1,interval=1.2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limit_middleware(request : Request,call_next):
    client_ip = request.client.host
    bucket = limiter.get_bucket(client_ip)

    if not bucket.allow_requests():
        retry_after = bucket.get_reset_time() - time.time()
        return JSONResponse(status_code=429,
                            content={"detail":"Too many requests. Try again later"},
                            headers={"Retry-After": str(max(1,int(retry_after))),
                                    "X-RateLimit-Limit": str(bucket.max_tokens),
                                    "X-RateLimit-Remaining": str(bucket.get_remaining()),
                                    "X-RateLimit-Reset": str(int(bucket.get_reset_time())),
                                      },
                                )
    response = await call_next(request)    
    response.headers["X-RateLimit-Limit"] = str(bucket.max_tokens)
    response.headers["X-RateLimit-Remaining"] = str(bucket.get_remaining())
    response.headers["X-RateLimit-Reset"] = str(int(bucket.get_reset_time()))
    return response


@app.get("/health")
async def health():

    return {"Status":"Ok"}

@app.post("/auth/register")
async def register_user(user : UserRegister,response : Response):

    if check_user_exists(user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with that username already exists")

    hashed = get_password_hash(user.password)
    try:
        save_user_to_db(user,hashed)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error saving user to database" )
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub": user.username},expires_delta=access_token_expires)
    set_auth_cookie(response,access_token)
    return {"message":f"    Succesfully signed user with username: {user.username} "}

@app.post("/auth/login")
async def login_for_access_token(response : Response,form_data : OAuth2PasswordRequestForm = Depends ()):
    user = authenticate_user(form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub":user.username},expires_delta=access_token_expires)
    set_auth_cookie(response,access_token)

    return {"message":"Logged in successfully"}
@app.post("/auth/logout")
async def logout(reponse : Response):
    reponse.delete_cookie(
        key="access_token",
        path="/"
    )
    return {"message": "Successfully logged out"}

@app.get("/auth/me")
async def get_current_user_info(user : Annotated[User,Depends(get_current_user)]):
    return {"username":user.username}

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
    return {"{user.username} - {user.full_name}"}

@app.get("/favourites")   
async def display_favourites(user: Annotated[User,Depends(get_current_user)]):
    return display_favourite_items(user.id)

@app.get("/watchlist")
async def display_watchlist(user : Annotated[User,Depends(get_current_user)]):
    return display_watchlist_items(user.id)
    
@app.post("/watchlist")
async def add_to_watchlist(item: WatchListItem,user : Annotated[User,Depends(get_current_user)]):
    return add_watchlist_item_db(item,user)

@app.patch("/watchlist/{tmdb_id}")
async def edit_watchlist(tmdb_id: int,item : EditWatchListItem, user : Annotated[User,Depends(get_current_user)],media_type: Mediatype = Mediatype.movie,):
   return edit_watchlist_item(tmdb_id,user.id,item,media_type)

@app.delete("/watchlist/{tmdb_id}")
async def delete_from_watchlist(tmdb_id : int, user : Annotated[User,Depends(get_current_user)],media_type : Mediatype = Mediatype.movie,):
    return delete_watchlist_item(tmdb_id,user.id,media_type)

@app.patch("/watchlist/{tmdb_id}/favourites")
async def updateFavourite(tmdb_id : int,user :Annotated[User,Depends(get_current_user)],favourite : FavouriteUpdate,media_type : Mediatype = Mediatype.movie):
    return addItemFavourites(tmdb_id,user.id,media_type,favourite.is_favourite)

@app.get("/watchlist/{tmdb_id}")
async def is_item_on_watchlist(tmdb_id : int,user : Annotated[User,Depends(get_current_user)],media_type: Mediatype = Mediatype.movie) -> bool:
    return check_watchlist_item(tmdb_id,user,media_type)
@app.get("/movies/trending")
async def display_trending_movies():
    return get_trending_movies()

@app.get("/movies/popular")
async def display_popular_movies():
    return get_popular_movies()

@app.get("/tv/popular")
async def display_trending_tv_shows():
    return get_trending_tv_shows()

@app.get("/tv/popular")
async def display_popular_tv_shows():
    return get_popular_tv_shows()