from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from databases import Database
from sqlalchemy import create_engine
from passlib.context import CryptContext
import os
from sqlalchemy import Table, Column, Integer, String, MetaData
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")



DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
database = Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("email", String),
    Column("hashed_password", String),
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    email: str 
    password: str


@app.on_event("startup")
async def startup():
    await database.connect()
    # Create tables if they don't exist
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def get_login(request: Request):
    return RedirectResponse(url="/static/login.html")

@app.get("/registration")
def get_login(request: Request):
    return RedirectResponse(url="/static/register.html")

@app.post("/register")
async def register(user: User):
    # Example of checking if the user already exists
    query = users.select().where(users.c.username == user.username)
    db_user = await database.fetch_one(query)

    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash the user's password
    hashed_password = pwd_context.hash(user.password)

    # Insert the new user into the database
    query = users.insert().values(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    await database.execute(query)
    
    return {"message": "User created successfully"}
@app.post("/login")
async def login(user: User):
    query = users.select().where(users.c.username == user.username)
    db_user = await database.fetch_one(query)

    if db_user and pwd_context.verify(user.password, db_user["hashed_password"]):
        return {"message": "Login successful"}

    raise HTTPException(status_code=401, detail="Invalid credentials")

