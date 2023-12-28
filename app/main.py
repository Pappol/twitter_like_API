from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Body
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
from sqlalchemy import or_
from .metadata import tags_metadata

SECRET_KEY = os.getenv("SECRET_KEY")  # secret key for encoding and decoding JWT
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
app = FastAPI(
    title="Twitter_Like",
    description="This is a simple twitter like api designed as a technical interview for U-Hopper. The API is a robust and efficient way to handle user authentication, registration, and social media interactions, specifically focusing on tweets. [Github Repository](https://github.com/Pappol/twitter_like_API)",
    version="1.0.0",
    openapi_tags=tags_metadata
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.mount("/static", StaticFiles(directory="static"), name="static")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
def get_homepage(request: Request):
    #check if user is logged in
    if request.headers.get("Authorization"):
        return RedirectResponse(url="/static/home.html")
    else:
        return RedirectResponse(url="/static/login.html")

@app.get("/register", tags=["users"])
def get_register(request: Request):
    return RedirectResponse(url="/static/register.html")

@app.post("/register", tags=["users"])
def register_user(register_data: LoginSchema, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(register_data.password)
    user = User(username=register_data.username, hashed_password=hashed_password)

    #check if username is empty
    if not register_data.username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    #check if password is empty
    if not register_data.password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    
    #check if username already exists
    if db.query(User).filter(User.username == register_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db.add(user)
    db.commit()
    return {"username": register_data.username}


@app.post("/login", tags=["users"])
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


@app.post("/tweets", tags=["tweets"])
def post_tweet(tweet_data: TweetSchema, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    tweet = Tweet(content=tweet_data.content, user_id=user_id)
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return {"message": "Tweet posted successfully!", "tweet_id": tweet.id}

#get the latest tweets
@app.get("/tweets", tags=["tweets"])
def get_tweets(db: Session = Depends(get_db)):
    tweets = db.query(Tweet).order_by(Tweet.date_posted.desc()).all()
    #get the first 10 tweets
    tweets = tweets[:10]
    return tweets

@app.get("/search", tags=["tweets"])
def search_tweets(search: SearchSchema, db: Session = Depends(get_db)):
    term = search.term
    tweets = db.query(Tweet).filter(
        or_(
            Tweet.content.ilike(f"%{term}%")
        )
    ).order_by(Tweet.date_posted.desc()).all()

    # Limit the results to the first 10 tweets
    tweets = tweets[:10]

    return tweets

@app.delete("/users/{username}", tags=["users"])
async def delete_user(username: str, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    # Check if user exists
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only the user can delete itself
    if user_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully!"}

#getch the latest tweets of a user
@app.get("/tweets/{username}", tags=["tweets"])
def get_tweets_by_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tweets = db.query(Tweet).filter(Tweet.user_id == user.id).order_by(Tweet.date_posted.desc()).all()
    #get the first 10 tweets
    tweets = tweets[:10]
    return tweets
