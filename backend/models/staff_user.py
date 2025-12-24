"""
SQLAlchemy модель для Staff Users
Отдельная система аутентификации для операторов, поддержки и системных администраторов
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

# Используем тот же Base, что и для других моделей
from models.user import Base


class StaffRole(str, enum.Enum):
    """Роли staff пользователей"""
    ADMIN = "admin"  # Системный администратор
    SUPPORT = "support"  # Служба поддержки
    MODERATOR = "moderator"  # Модератор


class StaffUser(Base):
    """Модель staff пользователя"""
    __tablename__ = "staff_users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)  # Номер телефона для входа
    email = Column(String(255), unique=True, index=True, nullable=True)  # Опционально для уведомлений
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # admin, support, moderator
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    two_fa_secret = Column(String(255), nullable=True)  # Для 2FA (опционально)

