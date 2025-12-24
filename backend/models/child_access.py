"""
Модель доступа ребёнка (PIN и QR-код)
Согласно требованиям: каждый ребёнок имеет свой PIN и QR-код
"""
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class ChildAccess(Base):
    """Модель доступа ребёнка (PIN и QR-токен)"""
    __tablename__ = "child_access"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    pin_hash = Column(String, nullable=True)  # Зашифрованный PIN (bcrypt), NULL до первого входа
    qr_token = Column(String, unique=True, nullable=True, index=True)  # Уникальный токен для QR-кода
    qr_token_expires_at = Column(DateTime(timezone=True), nullable=True)  # Срок действия QR-токена (общий срок)
    qr_token_valid_from = Column(DateTime(timezone=True), nullable=True)  # Время начала действия QR-токена (для временного окна)
    qr_token_used_at = Column(DateTime(timezone=True), nullable=True)  # Время первого использования (одноразовое использование)
    is_active = Column(Boolean, default=True, nullable=False)  # Можно отключить доступ
    failed_attempts = Column(Integer, default=0, nullable=False)  # Количество неудачных попыток
    locked_until = Column(DateTime(timezone=True), nullable=True)  # Блокировка до определённого времени
    
    # Связи
    child = relationship("Child", back_populates="child_access", uselist=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

