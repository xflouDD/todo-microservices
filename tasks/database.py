from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yaroslav8@localhost:5432/todo_microservices")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)