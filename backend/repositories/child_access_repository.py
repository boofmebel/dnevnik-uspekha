"""
Репозиторий для работы с доступом ребёнка (PIN и QR)
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.child_access import ChildAccess
from datetime import datetime, timedelta
import secrets


class ChildAccessRepository:
    """Репозиторий для работы с доступом ребёнка"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_child_id(self, child_id: int) -> Optional[ChildAccess]:
        """Получение доступа по ID ребёнка"""
        result = await self.session.execute(
            select(ChildAccess).where(ChildAccess.child_id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_qr_token(self, qr_token: str) -> Optional[ChildAccess]:
        """Получение доступа по QR-токену"""
        result = await self.session.execute(
            select(ChildAccess)
            .where(ChildAccess.qr_token == qr_token)
            .where(ChildAccess.is_active == True)
        )
        access = result.scalar_one_or_none()
        
        # Проверка срока действия
        if access and access.qr_token_expires_at:
            if datetime.now() > access.qr_token_expires_at:
                return None
        
        return access
    
    async def create(self, access_data: dict) -> ChildAccess:
        """Создание доступа"""
        access = ChildAccess(**access_data)
        self.session.add(access)
        await self.session.flush()
        await self.session.refresh(access)
        return access
    
    async def update(self, access: ChildAccess, access_data: dict) -> ChildAccess:
        """Обновление доступа"""
        for key, value in access_data.items():
            setattr(access, key, value)
        await self.session.flush()
        await self.session.refresh(access)
        return access
    
    def generate_qr_token(self) -> str:
        """Генерация уникального QR-токена"""
        return secrets.token_urlsafe(32)
    
    def generate_pin(self) -> str:
        """Генерация случайного PIN (4 цифры)"""
        return f"{secrets.randbelow(10000):04d}"

