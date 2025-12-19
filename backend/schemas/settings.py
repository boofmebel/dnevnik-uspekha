"""
Pydantic схемы для настроек
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SettingsBase(BaseModel):
    """Базовая схема настроек (виртуальная валюта для конвертации в подарки)"""
    stars_to_money: int = Field(default=15, ge=1, le=100, description="Количество звёзд для обмена на виртуальную валюту")
    money_per_stars: Decimal = Field(default=200, ge=0, description="Виртуальная валюта за обмен (для конвертации в подарки)")
    max_daily_tasks: int = Field(default=10, ge=1, le=50, description="Максимальное количество дел в день")
    stars_per_task: int = Field(default=1, ge=1, le=10, description="Количество звёзд за выполнение одной задачи")


class SettingsUpdate(BaseModel):
    """Схема обновления настроек"""
    stars_to_money: Optional[int] = Field(None, ge=1, le=100)
    money_per_stars: Optional[Decimal] = Field(None, ge=0)
    max_daily_tasks: Optional[int] = Field(None, ge=1, le=50)
    stars_per_task: Optional[int] = Field(None, ge=1, le=10)


class SettingsResponse(SettingsBase):
    """Схема ответа с настройками"""
    id: int
    child_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

