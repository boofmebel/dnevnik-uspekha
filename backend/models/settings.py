"""
Модель настроек
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Settings(Base):
    """Настройки ребёнка (виртуальная валюта для конвертации в подарки)"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    stars_to_money = Column(Integer, default=15, nullable=False)  # Количество звёзд для обмена на виртуальную валюту
    money_per_stars = Column(Numeric(10, 2), default=200, nullable=False)  # Виртуальная валюта за обмен (для конвертации в подарки по усмотрению родителей)
    max_daily_tasks = Column(Integer, default=10, nullable=False)  # Максимальное количество дел в день
    stars_per_task = Column(Integer, default=1, nullable=False)  # Количество звёзд за выполнение одной задачи
    
    # Связи
    child = relationship("Child", back_populates="settings")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

