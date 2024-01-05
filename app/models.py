from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

    tweets = relationship('Tweet', back_populates='author')

class Tweet(Base):
    __tablename__ = 'tweet'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    date_posted = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('user.id'))

    author = relationship('User', back_populates='tweets')
