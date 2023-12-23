from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Pydantic schema for Tweet
class TweetSchema(BaseModel):
    id: Optional[int] = None
    content: str
    date_posted: Optional[datetime] = None
    user_id: int

    class Config:
        orm_mode = True

# Pydantic schema for User
class UserSchema(BaseModel):
    id: Optional[int] = None
    username: str
    hashed_password: Optional[str] = None
    tweets: List[TweetSchema] = []

    class Config:
        orm_mode = True
