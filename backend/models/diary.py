"""
Модель дневника
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class DiaryEntry(Base):
    """Запись в дневнике"""
    __tablename__ = "diary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="diary_entries")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

