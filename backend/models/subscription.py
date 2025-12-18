"""
Модель подписки
Согласно требованиям: поддержка подписки с возвратами и логированием
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Subscription(Base):
    """Модель подписки пользователя"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    refund_requested = Column(Boolean, default=False, nullable=False)
    refund_reason = Column(String, nullable=True)  # Причина запроса возврата
    
    # Связи
    user = relationship("User", back_populates="subscriptions")
    notifications = relationship("Notification", back_populates="subscription", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

