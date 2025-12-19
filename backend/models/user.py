"""
SQLAlchemy модель пользователя
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

# Base для всех моделей
Base = declarative_base()


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    PARENT = "parent"
    CHILD = "child"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # Имя пользователя (родителя)
    email = Column(String, unique=True, index=True, nullable=True)  # Опционально, если регистрация по телефону
    phone = Column(String, unique=True, index=True, nullable=True)  # Номер телефона для регистрации
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Временно String вместо Enum для совместимости с БД
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Для детей
    
    # Связи
    children = relationship("Child", back_populates="user", cascade="all, delete-orphan")
    parent = relationship("User", remote_side=[id], backref="children_users")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    parent_consents = relationship("ParentConsent", back_populates="user", cascade="all, delete-orphan")
    family_rules = relationship("FamilyRules", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

