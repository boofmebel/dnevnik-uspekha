"""
Модель статистики недели
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Integer as SQLInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class WeeklyStat(Base):
    """Статистика за день"""
    __tablename__ = "weekly_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    stars = Column(SQLInteger, default=0, nullable=False)
    tasks_completed = Column(SQLInteger, default=0, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="weekly_stats")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

