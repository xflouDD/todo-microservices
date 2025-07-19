from fastapi import FastAPI, HTTPException
from models import Task
from database import SessionDep, create_db_and_tables
from sqlmodel import select
from datetime import datetime
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Service is running"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/tasks/")
async def create_task(task: Task, session: SessionDep):
    try:
        response = requests.get(f"http://users:8001/users/{task.user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
    except requests.RequestException:
        raise HTTPException(status_code=400, detail="Failed to connect to Users Service")

    if not hasattr(task, 'priority'):
        task.priority = 2
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.post("/tasks/{task_id}/finish")
async def finish_task(task_id: int, session: SessionDep):
    return complete_task(task_id, session)

def complete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.is_completed = True
    task.completed_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    
    return task

@app.get("/tasks/{user_id}/completed")
async def get_completed_tasks(user_id: int, session: SessionDep):
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.is_completed == True)
    ).all()
    return tasks

@app.get("/tasks/{user_id}/active")
async def get_active_tasks(user_id: int, session: SessionDep):
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.is_completed == False)
    ).all()
    return tasks

@app.get("/tasks/{user_id}/priority/{priority}")
async def get_active_tasks_by_priority(user_id: int, priority: int,session: SessionDep):
    query = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.is_completed == False)
        .where(Task.priority == priority)
    )
    
    tasks = session.exec(query).all()
    return tasks