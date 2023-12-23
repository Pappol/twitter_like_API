from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from databases import Database
from passlib.context import CryptContext
import os
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, create_engine, select
from pydantic import BaseModel
from datetime import datetime, timedelta
from structs import *


# Your secret key
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# This should match the tokenUrl you set in OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    username: str = None

# Function to decode and verify the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_user_by_username(username: str):
    query = select([users]).where(users.c.username == username)
    result = await database.fetch_one(query)

    if result:
        user_data = User(
            username=result["username"],
            email=result["email"],
            password=result["hashed_password"]
        )
        print(user_data)
        return user_data

    return None

# Function to create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)