import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from fastapi.security import OAuth2PasswordRequestForm

from utils import *
from structs import *

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

# Your login endpoint, which generates the token
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tweet")
async def post_tweet(tweet: Tweet, user: User = Depends(get_current_user)):
    query = tweets.insert().values(
        content=tweet.content,
        user_id=user.id
    )
    await database.execute(query)
    return {"message": "Tweet posted successfully"}

# API to fetch latest tweets
@app.get("/tweets")
async def get_latest_tweets():
    query = tweets.select().order_by(tweets.c.timestamp.desc()).limit(50)
    return await database.fetch_all(query)

# API to fetch tweets of a specific user
@app.get("/tweets/{user_id}")
async def get_user_tweets(user_id: int):
    query = tweets.select().where(tweets.c.user_id == user_id).order_by(tweets.c.timestamp.desc())
    return await database.fetch_all(query)

# API to search tweets
@app.get("/search_tweets")
async def search_tweets(keyword: str):
    query = tweets.select().where(tweets.c.content.contains(keyword))
    return await database.fetch_all(query)