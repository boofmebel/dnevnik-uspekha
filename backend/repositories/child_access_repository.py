"""
Репозиторий для работы с доступом ребёнка (PIN и QR)
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.child_access import ChildAccess
from datetime import datetime, timedelta, timezone
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
        - Токен должен быть не использован (одноразовое использование)
        """
        result = await self.session.execute(
            select(ChildAccess)
            .where(ChildAccess.qr_token == qr_token)
            .where(ChildAccess.is_active == True)
        )
        access = result.scalar_one_or_none()
        
        if not access:
            return None
        
        now = datetime.now(timezone.utc)
        
        # Логирование для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Проверка QR-токена: token={qr_token[:20]}..., child_id={access.child_id}, now={now}, used_at={access.qr_token_used_at}, expires_at={access.qr_token_expires_at}, is_active={access.is_active}")
        
        # Проверка активности
        if not access.is_active:
            logger.warning(f"QR-токен неактивен для ребенка {access.child_id}")
            return None
        
        # Проверка: токен не должен быть использован (одноразовое использование)
        if access.qr_token_used_at is not None:
            logger.warning(f"QR-токен уже использован: used_at={access.qr_token_used_at}, child_id={access.child_id}")
            return None
        
        # Проверка общего срока действия
        if access.qr_token_expires_at:
            if now > access.qr_token_expires_at:
                logger.warning(f"QR-токен истек по общему сроку: expires_at={access.qr_token_expires_at}, now={now}, child_id={access.child_id}")
                return None
        
        logger.info(f"QR-токен валиден, доступ разрешен для ребенка {access.child_id}")
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





