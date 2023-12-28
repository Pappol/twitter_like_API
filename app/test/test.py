import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from main import Base  # Import the Base from your main file
import os
import requests

url = "http://localhost:8000"

client = TestClient(app)


def test_register_user(client):
    data = {"username": "username",
            "password": "password"}
    
    # Test user registration
    response = client.post("/register", json=data)
    assert response.status_code == 200

def test_login_user(client):
    data = {"username": "username",
            "password": "password"}
    
    # Test user login
    response = client.post("/login", json=data)
    #check if access_token is returned
    if response.json().get("access_token"):
        assert response.status_code == 200

def test_post_tweet(client):
    login_data = {"username": "username",
                  "password": "password"}
    
    data = {"tweet": "tweet"}

    #login user and save access_token
    response = client.post("/login", json=login_data)
    access_token = response.json().get("access_token")

    # Test posting a tweet
    response = client.post("/tweet", json=data, cookies={"access_token": access_token})
    assert response.status_code == 200

def test_get_latest_tweets(client):
    response = client.get("/tweets")
    assert response.status_code == 200

def test_get_user_tweets(client):
    data = {"username": "username"}
    response = client.get("/tweets/"+data["username"])
    assert response.status_code == 200
