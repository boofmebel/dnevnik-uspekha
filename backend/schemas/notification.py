"""
Pydantic схемы для уведомлений
Согласно требованиям: валидация уведомлений
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.notification import NotificationType, NotificationStatus


class NotificationResponse(BaseModel):
    """Схема ответа с уведомлением"""
    id: int
    user_id: int
    subscription_id: Optional[int] = None
    type: NotificationType
    message: str
    status: NotificationStatus
    meta_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ComplaintRequest(BaseModel):
    """Схема запроса жалобы"""
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=20, max_length=2000)
    parent_consent: bool = Field(..., description="Подтверждение согласия родителя на обработку жалобы")


class NotificationCreate(BaseModel):
    """Схема создания уведомления"""
    user_id: int
    type: NotificationType
    message: str
    subscription_id: Optional[int] = None
    meta_data: Optional[str] = None

