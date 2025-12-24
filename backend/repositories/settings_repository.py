"""
Репозиторий для работы с настройками
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.settings import Settings


class SettingsRepository:
    """Репозиторий для работы с настройками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_child_id(self, child_id: int) -> Optional[Settings]:
        """Получение настроек ребёнка"""
        result = await self.session.execute(
            select(Settings).where(Settings.child_id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, child_id: int) -> Settings:
        """Получение или создание настроек для ребёнка"""
        settings = await self.get_by_child_id(child_id)
        if not settings:
            settings = Settings(child_id=child_id)
            self.session.add(settings)
            await self.session.flush()
            await self.session.refresh(settings)
        return settings
    
    async def update(self, settings: Settings, settings_data: dict) -> Settings:
        """Обновление настроек"""
        for key, value in settings_data.items():
            setattr(settings, key, value)
        await self.session.flush()
        await self.session.refresh(settings)
        return settings





