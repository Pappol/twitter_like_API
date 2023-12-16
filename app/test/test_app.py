import pytest
from fastapi.testclient import TestClient
from ..main import app  # Replace with your actual FastAPI app import

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

    # You should also test attempting to register the same user again,
    # and expect a 400 status code.
    
def test_login():
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Add more tests for invalid login credentials

def test_post_tweet():
    # This requires a logged-in user. You'll need to retrieve a token first and use it here.
    token = "your_token_here"
    response = client.post(
        "/tweet",
        json={"content": "Hello, World!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Tweet posted successfully"}

    # More tests for posting tweets, including invalid cases.

def test_get_latest_tweets():
    response = client.get("/tweets")
    assert response.status_code == 200
    # Check the response format as expected

def test_get_user_tweets():
    user_id = 1  # Use an actual user_id from your database
    response = client.get(f"/tweets/{user_id}")
    assert response.status_code == 200
    # Validate the response content

def test_search_tweets():
    keyword = "Hello"
    response = client.get(f"/search_tweets?keyword={keyword}")
    assert response.status_code == 200
    # Validate the response content

# Add more tests as needed
