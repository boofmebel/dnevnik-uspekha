"""
Pydantic схемы для списка желаний
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class WishlistItemBase(BaseModel):
    """Базовая схема элемента списка желаний"""
    name: str = Field(..., min_length=1, max_length=200)
    price: Optional[Decimal] = Field(None, ge=0)
    position: int = Field(default=0, ge=0)


class WishlistItemCreate(WishlistItemBase):
    """Схема создания элемента"""
    pass


class WishlistItemUpdate(BaseModel):
    """Схема обновления элемента"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[Decimal] = Field(None, ge=0)
    achieved: Optional[bool] = None
    position: Optional[int] = Field(None, ge=0)


class WishlistItemResponse(WishlistItemBase):
    """Схема ответа с элементом"""
    id: int
    child_id: int
    achieved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True



