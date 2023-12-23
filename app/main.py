from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from .models import *
from .schema import *
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class LoginSchema(BaseModel):
    username: str
    password: str

# Database configuration
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"  # User
    f"{os.getenv('POSTGRES_PASSWORD')}@"          # Password
    "db:5432/"                                    # Hostname and port
    f"{os.getenv('POSTGRES_DB')}"                 # Database name
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app configuration
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password):
    return pwd_context.hash(password)

# Database initialization
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    pass

@app.get("/")
def get_login(request: Request):
    #check if user is logged in
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/static/home.html")
    else:
        return RedirectResponse(url="/static/login.html")

@app.get("/register")
def get_register(request: Request):
    return RedirectResponse(url="/static/register.html")

@app.post("/register")
def register_user(register_data: LoginSchema, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(register_data.password)
    user = User(username=register_data.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return {"username": register_data.username}


@app.post("/login")
def login_user(register_data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == register_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(register_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"message": "Logged in successfully!"}
