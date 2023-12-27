from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LoginSchema(BaseModel):
    username: str
    password: str

class TweetSchema(BaseModel):
    content: str

class SearchSchema(BaseModel):
    term: str