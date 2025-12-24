"""
Репозиторий для работы со звёздами
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.star import Star, StarHistory, StarStreak


class StarRepository:
    """Репозиторий для работы со звёздами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_child_id(self, child_id: int) -> Optional[Star]:
        """Получение звёзд ребёнка"""
        result = await self.session.execute(
            select(Star).where(Star.child_id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, child_id: int) -> Star:
        """Получение или создание звёзд для ребёнка"""
        star = await self.get_by_child_id(child_id)
        if not star:
            star = Star(child_id=child_id)
            self.session.add(star)
            await self.session.flush()
            await self.session.refresh(star)
        return star
    
    async def add_history(self, star_id: int, description: str, stars: int) -> StarHistory:
        """Добавление записи в историю"""
        history = StarHistory(star_id=star_id, description=description, stars=stars)
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history
    
    async def get_streak(self, star_id: int) -> Optional[StarStreak]:
        """Получение серии дней"""
        result = await self.session.execute(
            select(StarStreak).where(StarStreak.star_id == star_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_streak(self, star_id: int) -> StarStreak:
        """Получение или создание серии дней"""
        streak = await self.get_streak(star_id)
        if not streak:
            streak = StarStreak(star_id=star_id)
            self.session.add(streak)
            await self.session.flush()
            await self.session.refresh(streak)
        return streak
    
    async def get_history(self, star_id: int, limit: int = 50) -> List[StarHistory]:
        """Получение истории звёзд"""
        result = await self.session.execute(
            select(StarHistory)
            .where(StarHistory.star_id == star_id)
            .order_by(StarHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())





