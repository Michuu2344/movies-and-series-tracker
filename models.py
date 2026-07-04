from pydantic import BaseModel
from typing import Optional
from enum import Enum
class UserRegister(BaseModel):
    username:str
    email:str
    full_name:str
    password : str


class User(BaseModel):
    id : int
    username : str
    email: str
    full_name : str
class UserInDB(User):
    hashed_password : str
class Mediatype(str,Enum):
    movie = "movie"
    tv = "tv"
class Status(str,Enum):
    watching = "watching"
    completed = "completed"
    want_to_watch = "want_to_watch"
    dropped = "dropped"
    favourite = "favourite"
class WatchListItem(BaseModel):
    tmbd_id : int
    media_type : Mediatype
    status : Status