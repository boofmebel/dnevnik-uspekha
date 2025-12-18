"""
Pydantic схемы для админ-панели
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.user import UserRole
from models.subscription import Subscription
from models.notification import NotificationType, NotificationStatus


class AdminUserResponse(BaseModel):
    """Схема пользователя для админки"""
    id: int
    email: str
    role: UserRole
    parent_id: Optional[int] = None
    children_count: int = 0
    subscriptions_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminChildResponse(BaseModel):
    """Схема ребёнка для админки"""
    id: int
    user_id: int
    parent_email: str
    name: str
    gender: str
    tasks_count: int = 0
    stars_total: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminSubscriptionResponse(BaseModel):
    """Схема подписки для админки"""
    id: int
    user_id: int
    user_email: str
    start_date: datetime
    end_date: datetime
    is_active: bool
    refund_requested: bool
    refund_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminNotificationResponse(BaseModel):
    """Схема уведомления для админки"""
    id: int
    user_id: int
    user_email: str
    type: NotificationType
    message: str
    status: NotificationStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminStatsResponse(BaseModel):
    """Схема статистики для админки"""
    total_users: int
    total_parents: int
    total_children: int
    active_subscriptions: int
    total_subscriptions: int
    refund_requests: int
    total_notifications: int
    recent_users: List[AdminUserResponse] = []
    recent_subscriptions: List[AdminSubscriptionResponse] = []
    recent_notifications: List[AdminNotificationResponse] = []


class AdminUserUpdate(BaseModel):
    """Схема обновления пользователя"""
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None  # Для блокировки пользователей


class AdminChildUpdate(BaseModel):
    """Схема обновления ребёнка"""
    name: Optional[str] = None
    is_active: Optional[bool] = None  # Для блокировки доступа

