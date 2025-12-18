"""
Модели для работы с копилкой
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Piggy(Base):
    """Модель копилки ребёнка (виртуальная валюта для конвертации в подарки)"""
    __tablename__ = "piggies"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    amount = Column(Numeric(10, 2), default=0, nullable=False)  # Виртуальная валюта (для конвертации в подарки)
    
    # Связи
    child = relationship("Child", back_populates="piggy")
    goal = relationship("PiggyGoal", back_populates="piggy", uselist=False, cascade="all, delete-orphan")
    history = relationship("PiggyHistory", back_populates="piggy", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PiggyGoal(Base):
    """Цель копилки"""
    __tablename__ = "piggy_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    piggy_id = Column(Integer, ForeignKey("piggies.id"), nullable=False, unique=True, index=True)
    name = Column(String, nullable=False, default="")
    amount = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Связи
    piggy = relationship("Piggy", back_populates="goal")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PiggyHistory(Base):
    """История операций с копилкой (виртуальная валюта)"""
    __tablename__ = "piggy_history"
    
    id = Column(Integer, primary_key=True, index=True)
    piggy_id = Column(Integer, ForeignKey("piggies.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # 'add', 'withdraw', 'streak', 'exchange'
    amount = Column(Numeric(10, 2), nullable=False)  # Виртуальная валюта
    description = Column(String, nullable=True)
    
    # Связи
    piggy = relationship("Piggy", back_populates="history")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

