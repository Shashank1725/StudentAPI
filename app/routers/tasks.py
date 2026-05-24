from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.auth import get_current_active_user
from app.crud import (
    get_task, get_tasks, get_tasks_count,
    create_task, update_task, delete_task
)
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, PaginatedResponse, MessageResponse
from app import models

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new task for the current user"""
    return create_task(db, task, current_user.id)

@router.get("/", response_model=PaginatedResponse)
async def read_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of tasks to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all tasks for the current user with pagination and filters"""
    tasks = get_tasks(db, current_user.id, skip, limit, status, priority)
    total = get_tasks_count(db, current_user.id, status, priority)
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    return {
        "items": tasks,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
        "total_pages": total_pages
    }

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific task by ID"""
    task = get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update a task"""
    task = get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return update_task(db, task, task_update)

@router.patch("/{task_id}", response_model=TaskResponse)
async def partially_update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Partially update a task"""
    task = get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return update_task(db, task, task_update)

@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete a task"""
    task = get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    delete_task(db, task)
    return {"message": "Task deleted successfully"}

@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Mark a task as completed"""
    task = get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    from datetime import datetime
    from app.schemas import TaskStatusEnum
    
    task.status = TaskStatusEnum.COMPLETED
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task