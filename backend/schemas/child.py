"""
Pydantic схемы для детей
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.child import Gender


class ChildBase(BaseModel):
    """Базовая схема ребёнка"""
    name: str = Field(..., min_length=1, max_length=100)
    gender: Gender = Gender.NONE
    avatar: Optional[str] = None


class ChildCreate(ChildBase):
    """Схема создания ребёнка"""
    pass


class ChildUpdate(BaseModel):
    """Схема обновления ребёнка"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[Gender] = None
    avatar: Optional[str] = None


class ChildResponse(ChildBase):
    """Схема ответа с ребёнком"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True



