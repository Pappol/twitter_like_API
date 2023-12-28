# Twitter_like_API
Twitter-like fastapi based API


1. [Overview](#overview)
2. [System Architecture](#system-architecture)

3. [API Endpoints](#api-endpoints)

4. [Installation and Setup](#installation-and-setup)

5. [API Documentation](#api-documentation)
6. [Testing](#testing)


## Overview
Twitter_Like is an API designed to mimic basic functionalities of a social media platform similar to Twitter. Developed using FastAPI, this API facilitates user authentication, registration, and interaction with tweets. Its robust and efficient architecture is particularly tailored for technical interviews and educational purposes.

Version: 1.0.0

## System Architecture
The Twitter_Like API is built on the FastAPI framework, leveraging asynchronous programming for improved performance. The API uses SQLAlchemy for database interactions, and the database is PostgreSQL. User passwords are securely managed using the Passlib library.

### Key Components
- FastAPI: A modern, fast (high-performance) web framework for building APIs.
- SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) for database interactions.
- PostgreSQL: The database system.
- Passlib: For hashing and verifying passwords securely.
- Pydantic: For data validation and settings management using Python type annotations.
- Python-Jose: For handling JWT tokens for secure and stateless authentication.

### Authentication and Authorization
- OAuth2: The API uses OAuth2 with password flow for authentication.
- JWT Tokens: JSON Web Tokens (JWT) are used for secure user authentication. Tokens have a configurable expiration time.
- Password Hashing: User passwords are hashed using bcrypt, ensuring security standards.
- Permission Checks: The API performs permission checks, ensuring users can only access their data.

## API Endpoints
The API provides various endpoints categorized under 'users' and 'tweets' tags:

### Users
- /register: For user registration.
- /login: For user login, returning a JWT token upon successful authentication.
- /users/{username}: For deleting a user (self).

### Tweets
- /tweets: For posting a new tweet and retrieving the latest tweets.
- /tweets/{username}: For retrieving tweets from a specific user.
- /search: For searching tweets based on content.

### Database Initialization

On startup, the database schema is created if not existing.


## Installation and Setup
Clone the repository:
```
git clone https://github.com/Pappol/twitter_like_API

```

Set Environment Variables:
- SECRET_KEY: A secret key for JWT encoding and decoding.
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes.
- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB: PostgreSQL credentials.

in the tw.env file

Run the application:
```
docker-compose up --build
```

This will start the application on http://localhost:8000.

## API Documentation
The API documentation is available at http://localhost:8000/docs once the application is running

## Testing
The API can be tested using an external environment with the following steps:

- Install the requirements:
```
pip install -r test_requirements.txt
```

- Run the tests:
```
cd tests
pytest tests.py
```