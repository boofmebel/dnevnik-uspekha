"""
Pydantic схемы для дневника
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DiaryEntryBase(BaseModel):
    """Базовая схема записи дневника"""
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1)


class DiaryEntryCreate(DiaryEntryBase):
    """Схема создания записи"""
    pass


class DiaryEntryUpdate(BaseModel):
    """Схема обновления записи"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1)


class DiaryEntryResponse(DiaryEntryBase):
    """Схема ответа с записью"""
    id: int
    child_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

