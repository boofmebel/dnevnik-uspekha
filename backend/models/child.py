"""
Модель ребёнка
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from models.user import Base


class Gender(str, enum.Enum):
    """Пол ребёнка"""
    GIRL = "girl"
    BOY = "boy"
    NONE = "none"


class Child(Base):
    """Модель ребёнка"""
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, default="Ребёнок")
    gender = Column(Enum(Gender), nullable=False, default=Gender.NONE)
    avatar = Column(Text, nullable=True)  # Base64 или URL
    
    # Связи
    user = relationship("User", back_populates="children")
    tasks = relationship("Task", back_populates="child", cascade="all, delete-orphan")
    stars = relationship("Star", back_populates="child", uselist=False, cascade="all, delete-orphan")
    piggy = relationship("Piggy", back_populates="child", uselist=False, cascade="all, delete-orphan")
    diary_entries = relationship("DiaryEntry", back_populates="child", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="child", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="child", uselist=False, cascade="all, delete-orphan")
    weekly_stats = relationship("WeeklyStat", back_populates="child", cascade="all, delete-orphan")
    parent_consents = relationship("ParentConsent", back_populates="child", cascade="all, delete-orphan")
    child_access = relationship("ChildAccess", back_populates="child", uselist=False, cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

