
from typing import Annotated
from datetime import datetime, timedelta,timezone
import jwt
from pydantic import BaseModel
from fastapi import Depends,HTTPException,status,Request,Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from backend.models import User,UserInDB, UserRegister
from backend.database import get_user_from_db

import os
from dotenv import load_dotenv
load_dotenv()
DUMMY_PASSWORD = os.getenv("DUMMY_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type : str

class TokenData(BaseModel):
    username : str | None = None

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash(DUMMY_PASSWORD)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password,hashed_password):
    return password_hash.verify(plain_password,hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(username: str) -> UserInDB | None:
    user = get_user_from_db(username)
    if user is None:
        return None
    return UserInDB(**user)
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
async def get_current_user(request : Request):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No token in cookies log in")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials - log in"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
def set_auth_cookie(response : Response,access_token : str):
    expire_date = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    response.set_cookie(
            key = "access_token",
            value = access_token,
            max_age= ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires= expire_date,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/"
            )


