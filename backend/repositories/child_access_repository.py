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
        """
        Получение доступа по QR-токену с проверкой всех ограничений:
        - Токен должен быть активен
        - Токен не должен быть использован (одноразовое использование)
        - Токен должен быть в пределах общего срока действия
        - Токен должен быть в пределах временного окна (1 час с момента генерации)
        """
        result = await self.session.execute(
            select(ChildAccess)
            .where(ChildAccess.qr_token == qr_token)
            .where(ChildAccess.is_active == True)
        )
        access = result.scalar_one_or_none()
        
        if not access:
            return None
        
        now = datetime.now()
        
        # Проверка: токен не должен быть использован (одноразовое использование)
        if access.qr_token_used_at is not None:
            return None
        
        # Проверка общего срока действия
        if access.qr_token_expires_at:
            if now > access.qr_token_expires_at:
                return None
        
        # Проверка временного окна (1 час с момента генерации)
        if access.qr_token_valid_from:
            time_since_generation = now - access.qr_token_valid_from
            if time_since_generation.total_seconds() > 3600:  # 1 час = 3600 секунд
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
    
    async def delete(self, access: ChildAccess) -> None:
        """Удаление доступа"""
        await self.session.delete(access)
        await self.session.flush()
    
    def generate_qr_token(self) -> str:
        """Генерация уникального QR-токена"""
        return secrets.token_urlsafe(32)
    
    def generate_pin(self) -> str:
        """Генерация случайного PIN (4 цифры)"""
        return f"{secrets.randbelow(10000):04d}"





