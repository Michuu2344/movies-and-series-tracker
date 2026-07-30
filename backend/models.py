from pydantic import BaseModel,Field
from typing import Optional
from enum import Enum
from datetime import datetime
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
class WatchListItem(BaseModel):
    tmdb_id : int
    media_type : Mediatype
    status : Status
    rating: int | None = Field(None, ge=1, le=10)
    is_favourite :bool = False
class EditWatchListItem(BaseModel):
    status : Optional[Status] = None
    rating: Optional[int] = None
