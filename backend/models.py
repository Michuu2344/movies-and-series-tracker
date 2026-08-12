from pydantic import BaseModel,Field,field_validator
from typing import Optional
from enum import Enum
from datetime import datetime
import re
class UserRegister(BaseModel):
    username:str
    email:str
    full_name:str
    password : str

    @field_validator("password")
    @classmethod
    def validate_password(cls,value):
        errors = []
        if len(value) < 8:
            errors.append("at least 8 characters")
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]",value):
            errors.append("at least one uppercase character")
            raise ValueError("Password must contain at least one uppercase character")
        if not re.search(r"[a-z]",value):
            errors.append("at least one lowercase character")
        if not re.search(r"\d",value):
            errors.append("at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]",value):
            errors.append("at least one special character")  
        if errors:
            raise ValueError(f"Password must contain: {' ,'.join(errors)}")
        return value
    @field_validator("username")
    @classmethod
    def validate_username(cls,value):
          if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long")
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
class FavouriteUpdate(BaseModel):
    is_favourite : bool