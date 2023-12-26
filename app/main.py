from fastapi import FastAPI, Depends, HTTPException, status
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
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY")  # secret key for encoding and decoding JWT
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id


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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/tweet")
def post_tweet(tweet_data: TweetSchema, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    # Assuming get_current_user_id is a dependency that extracts the user's ID from the request
    tweet = Tweet(content=tweet_data.content, user_id=user_id)
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return {"message": "Tweet posted successfully!", "tweet_id": tweet.id}

