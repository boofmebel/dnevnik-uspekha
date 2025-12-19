"""
Репозиторий для работы с refresh tokens
Согласно rules.md: хранение, проверка, отзыв refresh tokens
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.refresh_token import RefreshToken
from core.security.password import hash_password, verify_password
import hashlib


class RefreshTokenRepository:
    """Репозиторий для работы с refresh tokens"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _hash_token(self, token: str) -> str:
        """Хеширование токена для безопасного хранения"""
        # Используем SHA-256 для хеширования токена
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def create(self, user_id: int, token: str, device_info: Optional[str] = None) -> RefreshToken:
        """Создание нового refresh token"""
        token_hash = self._hash_token(token)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            device_info=device_info
        )
        
        self.session.add(refresh_token)
        await self.session.flush()
        await self.session.refresh(refresh_token)
        
        return refresh_token
    
    async def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """Получение валидного (не отозванного) refresh token"""
        token_hash = self._hash_token(token)
        
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked_at.is_(None)
                )
            )
        )
        
        return result.scalar_one_or_none()
    
    async def revoke_token(self, token: str) -> bool:
        """Отзыв refresh token"""
        token_record = await self.get_valid_token(token)
        if not token_record:
            return False
        
        from datetime import datetime
        token_record.revoked_at = datetime.utcnow()
        await self.session.flush()
        
        return True
    
    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """Отзыв всех refresh tokens пользователя"""
        from datetime import datetime
        
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked_at.is_(None)
                )
            )
        )
        
        tokens = result.scalars().all()
        count = 0
        for token in tokens:
            token.revoked_at = datetime.utcnow()
            count += 1
        
        await self.session.flush()
        return count
    
    async def cleanup_expired_tokens(self, days: int = 90) -> int:
        """Очистка старых отозванных токенов (старше N дней)"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.revoked_at.isnot(None),
                    RefreshToken.revoked_at < cutoff_date
                )
            )
        )
        
        tokens = result.scalars().all()
        count = len(tokens)
        
        for token in tokens:
            await self.session.delete(token)
        
        await self.session.flush()
        return count
