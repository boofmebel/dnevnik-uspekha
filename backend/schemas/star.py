"""
Pydantic схемы для звёзд
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StarHistoryBase(BaseModel):
    """Базовая схема истории звёзд"""
    description: str
    stars: int = Field(..., ge=0)


class StarHistoryResponse(StarHistoryBase):
    """Схема ответа с историей звёзд"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StarStreakResponse(BaseModel):
    """Схема ответа с серией дней"""
    current: int = Field(default=0, ge=0)
    last_date: Optional[str] = None
    best: int = Field(default=0, ge=0)
    claimed_rewards: List[int] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class StarResponse(BaseModel):
    """Схема ответа со звёздами"""
    today: int = Field(default=0, ge=0)
    total: int = Field(default=0, ge=0)
    history: List[StarHistoryResponse] = Field(default_factory=list)
    streak: Optional[StarStreakResponse] = None
    
    class Config:
        from_attributes = True


class StarAddRequest(BaseModel):
    """Схема добавления звёзд"""
    description: str = Field(..., min_length=1, max_length=200)
    stars: int = Field(..., ge=1, le=10)


class StarExchangeRequest(BaseModel):
    """Схема обмена звёзд на виртуальную валюту (для конвертации в подарки)"""
    stars: int = Field(..., ge=1)

