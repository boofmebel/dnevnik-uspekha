"""
Pydantic схемы для статистики недели
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class WeeklyStatBase(BaseModel):
    """Базовая схема статистики"""
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    stars: int = Field(default=0, ge=0)
    tasks_completed: int = Field(default=0, ge=0)


class WeeklyStatResponse(WeeklyStatBase):
    """Схема ответа со статистикой"""
    id: int
    child_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WeeklyStatsResponse(BaseModel):
    """Схема ответа со статистикой недели"""
    days: List[WeeklyStatResponse] = Field(default_factory=list)
    last_week: List[WeeklyStatResponse] = Field(default_factory=list)

