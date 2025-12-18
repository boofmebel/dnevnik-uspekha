"""
Модель согласия родителей
Согласно требованиям: обязательное согласие родителей на обработку данных ребёнка
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class ParentConsent(Base):
    """Модель согласия родителей на обработку данных ребёнка"""
    __tablename__ = "parent_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String, nullable=True)  # Для аудита
    user_agent = Column(Text, nullable=True)  # Для аудита
    
    # Связи
    user = relationship("User", back_populates="parent_consents")
    child = relationship("Child", back_populates="parent_consents")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

