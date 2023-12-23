from utils import *
from fastapi.security import OAuth2PasswordBearer

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

tweets = Table(
    "tweets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("content", String),
    Column("user_id", ForeignKey("users.id")),
    Column("timestamp", DateTime, default=datetime.utcnow)
)


class User(BaseModel):
    username: str
    email: str 
    hashed_password: str

class Tweet(BaseModel):
    content: str