from fastapi import FastAPI, HTTPException
from models import User
from database import SessionDep, create_db_and_tables
from sqlmodel import select

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Service is running"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/users/")
async def create_user(user: User, session: SessionDep):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user