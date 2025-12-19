"""
Модель правил семьи
Согласно требованиям: каждый родитель может редактировать правила семьи
"""
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class FamilyRules(Base):
    """Модель правил семьи для родителя"""
    __tablename__ = "family_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    rules = Column(Text, nullable=False, default="[]")  # JSON массив правил
    
    # Связи
    user = relationship("User", back_populates="family_rules")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

