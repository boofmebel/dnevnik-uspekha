"""
Pydantic схемы для правил семьи
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FamilyRulesResponse(BaseModel):
    """Схема ответа с правилами семьи"""
    id: int
    user_id: int
    rules: List[str] = Field(default_factory=list)  # Массив правил
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FamilyRulesUpdate(BaseModel):
    """Схема обновления правил семьи"""
    rules: List[str] = Field(..., description="Массив правил семьи")



