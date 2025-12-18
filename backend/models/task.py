"""
Модель задачи
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from models.user import Base


class TaskType(str, enum.Enum):
    """Тип задачи"""
    CHECKLIST = "checklist"
    KANBAN = "kanban"


class TaskStatus(str, enum.Enum):
    """Статус задачи в канбане"""
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Task(Base):
    """Модель задачи"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    text = Column(String, nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), nullable=True)  # Для канбана
    completed = Column(Boolean, default=False, nullable=False)
    stars = Column(Integer, default=0, nullable=False)
    position = Column(Integer, default=0)  # Для сортировки
    
    # Связи
    child = relationship("Child", back_populates="tasks")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

