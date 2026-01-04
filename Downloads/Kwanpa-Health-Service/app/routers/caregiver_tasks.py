# back/app/routers/caregiver_tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver_tasks import CaregiverTask, TaskStatus, TaskPriority
from app.models.caregiver import CaregiverRelationship

router = APIRouter(prefix="/caregiver", tags=["caregiver"])

# Pydantic Models
class TaskCreate(BaseModel):
    patient_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    task_type: str = Field(..., description="medication, appointment, checkup, etc.")
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurrence_days: Optional[List[int]] = None
    notes: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    caregiver_id: int
    patient_id: int
    patient_name: str
    title: str
    description: Optional[str]
    task_type: str
    status: str
    priority: str
    due_date: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    completed_at: Optional[datetime]
    is_recurring: bool
    recurrence_rule: Optional[str]
    recurrence_days: Optional[List[int]]
    notes: Optional[str]
    attachments: Optional[List[str]]
    is_overdue: bool
    created_at: datetime
    updated_at: Optional[datetime]

# GET route MUST come before POST route for same path
@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    patient_id: Optional[int] = Query(None),
    due_date_from: Optional[date] = Query(None),
    due_date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks for caregiver"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    query = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == current_user.id
    )
    
    if status:
        query = query.filter(CaregiverTask.status == status)
    if priority:
        query = query.filter(CaregiverTask.priority == priority)
    if patient_id:
        relationship = db.query(CaregiverRelationship).filter(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.patient_id == patient_id,
            CaregiverRelationship.status == "approved"
        ).first()
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view tasks for this patient"
            )
        query = query.filter(CaregiverTask.patient_id == patient_id)
    
    if due_date_from:
        query = query.filter(CaregiverTask.due_date >= due_date_from)
    if due_date_to:
        query = query.filter(CaregiverTask.due_date <= due_date_to)
    
    tasks = query.order_by(CaregiverTask.due_date).all()
    
    response = []
    for task in tasks:
        patient = db.query(User).filter(User.id == task.patient_id).first()
        response.append(TaskResponse(
            id=task.id,
            caregiver_id=task.caregiver_id,
            patient_id=task.patient_id,
            patient_name=patient.username if patient else "Unknown",
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            status=task.status.value,
            priority=task.priority.value,
            due_date=task.due_date,
            start_time=task.start_time,
            end_time=task.end_time,
            completed_at=task.completed_at,
            is_recurring=task.is_recurring,
            recurrence_rule=task.recurrence_rule,
            recurrence_days=task.recurrence_days,
            notes=task.notes,
            attachments=task.attachments or [],
            is_overdue=task.is_overdue(),
            created_at=task.created_at,
            updated_at=task.updated_at
        ))
    
    return response

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task for a patient"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == task_data.patient_id,
        CaregiverRelationship.status == "approved"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this patient"
        )
    
    patient = db.query(User).filter(User.id == task_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    task = CaregiverTask(
        caregiver_id=current_user.id,
        patient_id=task_data.patient_id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        priority=task_data.priority,
        due_date=task_data.due_date,
        start_time=task_data.start_time,
        end_time=task_data.end_time,
        is_recurring=task_data.is_recurring,
        recurrence_rule=task_data.recurrence_rule,
        recurrence_days=task_data.recurrence_days,
        notes=task_data.notes,
        assigned_by=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        caregiver_id=task.caregiver_id,
        patient_id=task.patient_id,
        patient_name=patient.username or patient.email,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        status=task.status.value,
        priority=task.priority.value,
        due_date=task.due_date,
        start_time=task.start_time,
        end_time=task.end_time,
        completed_at=task.completed_at,
        is_recurring=task.is_recurring,
        recurrence_rule=task.recurrence_rule,
        recurrence_days=task.recurrence_days,
        notes=task.notes,
        attachments=task.attachments or [],
        is_overdue=task.is_overdue(),
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.get("/tasks/overdue")
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overdue tasks"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    tasks = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == current_user.id,
        CaregiverTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
        CaregiverTask.due_date < datetime.utcnow()
    ).order_by(CaregiverTask.due_date).all()
    
    return [
        {
            "id": task.id,
            "title": task.title,
            "patient_id": task.patient_id,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "is_overdue": task.is_overdue()
        }
        for task in tasks
    ]

@router.get("/tasks/today")
async def get_todays_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's tasks"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    tasks = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == current_user.id,
        CaregiverTask.due_date.between(today_start, today_end)
    ).order_by(CaregiverTask.priority).all()
    
    return [
        {
            "id": task.id,
            "title": task.title,
            "patient_id": task.patient_id,
            "priority": task.priority.value,
            "status": task.status.value,
            "due_date": task.due_date.isoformat() if task.due_date else None
        }
        for task in tasks
    ]

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    
    task = db.query(CaregiverTask).filter(
        CaregiverTask.id == task_id,
        CaregiverTask.caregiver_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    if task_data.status == TaskStatus.COMPLETED and not task.completed_at:
        task.completed_at = datetime.utcnow()
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status.value,
        "priority": task.priority.value,
        "updated_at": task.updated_at.isoformat()
    }

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    
    task = db.query(CaregiverTask).filter(
        CaregiverTask.id == task_id,
        CaregiverTask.caregiver_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark task as completed"""
    
    task = db.query(CaregiverTask).filter(
        CaregiverTask.id == task_id,
        CaregiverTask.caregiver_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status.value,
        "completed_at": task.completed_at.isoformat()
    }