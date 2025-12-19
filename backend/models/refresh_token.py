"""
SQLAlchemy модель для refresh tokens
Согласно rules.md: хранение refresh tokens в БД с device_info, issued_at, revoked_at
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.user import Base


class RefreshToken(Base):
    """Модель refresh token"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)  # Хеш токена для безопасности
    device_info = Column(Text, nullable=True)  # Информация об устройстве (User-Agent, IP и т.д.)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)  # Время отзыва токена
    
    # Связь с пользователем
    user = relationship("User", backref="refresh_tokens")
    
    def is_revoked(self) -> bool:
        """Проверка, отозван ли токен"""
        return self.revoked_at is not None
