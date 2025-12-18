"""
Pydantic схемы для копилки
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PiggyGoalBase(BaseModel):
    """Базовая схема цели копилки"""
    name: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., ge=0)


class PiggyGoalResponse(PiggyGoalBase):
    """Схема ответа с целью"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PiggyHistoryResponse(BaseModel):
    """Схема ответа с историей копилки"""
    id: int
    type: str
    amount: Decimal
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PiggyResponse(BaseModel):
    """Схема ответа с копилкой"""
    amount: Decimal = Field(default=0, ge=0)
    goal: Optional[PiggyGoalResponse] = None
    history: List[PiggyHistoryResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class PiggyGoalUpdate(BaseModel):
    """Схема обновления цели"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[Decimal] = Field(None, ge=0)


class PiggyAddRequest(BaseModel):
    """Схема добавления виртуальной валюты в копилку (для конвертации в подарки)"""
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None

