from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
from app import models, schemas

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: models.User, user_update: schemas.UserUpdate):
    if user_update.email:
        user.email = user_update.email
    if user_update.full_name:
        user.full_name = user_update.full_name
    if user_update.password:
        from app.auth import get_password_hash
        user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()

# Task CRUD operations
def get_task(db: Session, task_id: int, user_id: Optional[int] = None):
    query = db.query(models.Task).filter(models.Task.id == task_id)
    if user_id:
        query = query.filter(models.Task.owner_id == user_id)
    return query.first()

def get_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    
    return query.offset(skip).limit(limit).all()

def get_tasks_count(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    
    return query.count()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.model_dump(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task: models.Task, task_update: schemas.TaskUpdate):
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Handle completion status
    if "status" in update_data and update_data["status"] == "completed" and task.status != "completed":
        update_data["completed_at"] = datetime.utcnow()
    elif "status" in update_data and update_data["status"] != "completed":
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: models.Task):
    db.delete(task)
    db.commit()