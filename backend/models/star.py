"""
Модели для работы со звёздами
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Star(Base):
    """Модель звёзд ребёнка"""
    __tablename__ = "stars"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    today = Column(Integer, default=0, nullable=False)
    total = Column(Integer, default=0, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="stars")
    history = relationship("StarHistory", back_populates="star", cascade="all, delete-orphan")
    streak = relationship("StarStreak", back_populates="star", uselist=False, cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StarHistory(Base):
    """История получения звёзд"""
    __tablename__ = "star_history"
    
    id = Column(Integer, primary_key=True, index=True)
    star_id = Column(Integer, ForeignKey("stars.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    
    # Связи
    star = relationship("Star", back_populates="history")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StarStreak(Base):
    """Серия дней выполнения задач"""
    __tablename__ = "star_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    star_id = Column(Integer, ForeignKey("stars.id"), nullable=False, unique=True, index=True)
    current = Column(Integer, default=0, nullable=False)
    last_date = Column(String, nullable=True)  # YYYY-MM-DD
    best = Column(Integer, default=0, nullable=False)
    claimed_rewards = Column(Text, nullable=True)  # JSON массив
    
    # Связи
    star = relationship("Star", back_populates="streak")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

