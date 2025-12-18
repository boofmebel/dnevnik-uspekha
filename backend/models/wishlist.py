"""
Модель списка желаний
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class WishlistItem(Base):
    """Элемент списка желаний"""
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=True)
    achieved = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, default=0)  # Для сортировки
    
    # Связи
    child = relationship("Child", back_populates="wishlist_items")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

