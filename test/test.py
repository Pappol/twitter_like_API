import requests
import json
import pytest

@pytest.fixture
def url():
    return "http://localhost:8000"

def test_delete_user(url):
    login_data = {"username": "username", "password": "password"}
    response = requests.post(url+"/login", json=login_data)
    
    # If login fails, attempt to register the user
    if response.status_code != 200:
        response = requests.post(url+"/register", json=login_data)

        # If registration fails, raise an exception
        if response.status_code != 200:
            raise Exception("Registration failed")

        # After successful registration, attempt to log in again
        response = requests.post(url+"/login", json=login_data)
        # If login still fails, raise an exception
        if response.status_code != 200:
            raise Exception("Login failed after registration")
    # If login is successful, proceed to get the access token
    access_token = response.json().get("access_token")

    # Check if the access token is received
    if not access_token:
        raise Exception("Failed to retrieve access token")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Attempt to delete the user
    response = requests.delete(url + "/users/" + login_data["username"], headers=headers)

    # Assert that the deletion was successful
    assert response.status_code == 200


def test_register_user(url):
    data = {"username": "username", "password": "password"}
    response = requests.post(url + "/register", json=data)
    assert response.status_code == 200


def test_login_user(url):
    data = {"username": "username",
            "password": "password"}
    json_data = json.dumps(data)
    
    # Test user login
    response = requests.post(url+"/login", json=data)
    #check if access_token is returned
    if response.json().get("access_token"):
        assert response.status_code == 200

def test_post_tweet(url):
    # User credentials for login
    login_data = {"username": "username", "password": "password"}

    # Attempt to log in and retrieve access token
    response = requests.post(f"{url}/login", json=login_data)
    assert response.status_code == 200, "Login failed"

    # Extract access token from the login response
    access_token = response.json().get("access_token")
    assert access_token is not None, "Access token not retrieved"

    # Prepare headers with the access token for authorization
    headers = {"Authorization": f"Bearer {access_token}"}

    # Data for the tweet
    tweet_data = {"content": "tweet"}  # Ensure this matches the expected schema in your API

    # Post a tweet
    response = requests.post(f"{url}/tweets", json=tweet_data, headers=headers)
    
    # Assert that posting the tweet was successful
    assert response.status_code == 200, "Posting tweet failed"


def test_get_latest_tweets(url):
    response = requests.get(url+"/tweets")
    assert response.status_code == 200

def test_get_user_tweets(url):
    username = "username"
    response = requests.get(url + "/tweets/" + username)
    assert response.status_code == 200
