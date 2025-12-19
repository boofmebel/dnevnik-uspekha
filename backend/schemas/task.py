"""
Pydantic схемы для задач
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.task import TaskType, TaskStatus


class TaskBase(BaseModel):
    """Базовая схема задачи"""
    text: str = Field(..., min_length=1, max_length=500)
    task_type: TaskType
    status: Optional[TaskStatus] = None
    stars: int = Field(default=0, ge=0, le=10)
    position: int = Field(default=0, ge=0)


class TaskCreate(TaskBase):
    """Схема создания задачи"""
    pass


class TaskUpdate(BaseModel):
    """Схема обновления задачи"""
    text: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    status: Optional[TaskStatus] = None
    stars: Optional[int] = Field(None, ge=0, le=10)
    position: Optional[int] = Field(None, ge=0)


class TaskResponse(TaskBase):
    """Схема ответа с задачей"""
    id: int
    child_id: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Схема списка задач"""
    checklist: list[TaskResponse] = []
    kanban: dict[str, list[TaskResponse]] = Field(default_factory=lambda: {
        "todo": [],
        "doing": [],
        "done": []
    })



