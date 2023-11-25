from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from databases import Database
from sqlalchemy import create_engine
from passlib.context import CryptContext
import os
from sqlalchemy import Table, Column, Integer, String, MetaData
from pydantic import BaseModel
from sqlalchemy import Table, Column, ForeignKey, DateTime
from datetime import datetime

# Your secret key
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# This should match the tokenUrl you set in OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# A function to fetch user data from the database
def get_user_by_username(username: str):
    # Your database query here
    pass

# Function to create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
