from fastapi import FastAPI, HTTPException
from models import User
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")


@app.post("/register")
def register(user: User):
    if user.username in users:
        return {"message": "User already exists"}
    
    users[user.username] = user
    return {"message": "User created successfully"}


@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
