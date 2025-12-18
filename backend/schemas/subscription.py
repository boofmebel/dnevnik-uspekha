"""
Pydantic схемы для подписки
Согласно требованиям: валидация данных подписки
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.subscription import Subscription
from models.notification import NotificationType, NotificationStatus


class SubscriptionResponse(BaseModel):
    """Схема ответа с подпиской"""
    id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    refund_requested: bool
    refund_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubscriptionCancelRequest(BaseModel):
    """Схема запроса на отмену подписки"""
    reason: Optional[str] = Field(None, max_length=500)


class SubscriptionRefundRequest(BaseModel):
    """Схема запроса на возврат средств"""
    reason: str = Field(..., min_length=10, max_length=1000)
    parent_consent: bool = Field(..., description="Подтверждение согласия родителя")


class ParentConsentRequest(BaseModel):
    """Схема запроса согласия родителей"""
    child_id: int
    consent_given: bool = Field(..., description="Согласие на обработку данных ребёнка")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ParentConsentResponse(BaseModel):
    """Схема ответа с согласием родителей"""
    id: int
    user_id: int
    child_id: int
    consent_given: bool
    consent_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

