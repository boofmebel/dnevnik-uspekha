"""
Модель уведомлений
Согласно требованиям: логирование всех действий (подписка, возвраты, жалобы)
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from models.user import Base


class NotificationType(str, enum.Enum):
    """Типы уведомлений"""
    SUBSCRIPTION = "subscription"
    REFUND = "refund"
    COMPLAINT = "complaint"
    CONSENT = "consent"
    SYSTEM = "system"


class NotificationStatus(str, enum.Enum):
    """Статусы уведомлений"""
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class Notification(Base):
    """Модель уведомления"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON для дополнительных данных
    
    # Связи
    user = relationship("User", back_populates="notifications")
    subscription = relationship("Subscription", back_populates="notifications")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
