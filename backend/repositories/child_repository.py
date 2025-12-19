"""
Репозиторий для работы с детьми
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.child import Child
from models.user import User


class ChildRepository:
    """Репозиторий для работы с детьми"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, child_id: int) -> Optional[Child]:
        """Получение ребёнка по ID"""
        result = await self.session.execute(
            select(Child).where(Child.id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> List[Child]:
        """Получение всех детей пользователя"""
        result = await self.session.execute(
            select(Child).where(Child.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def create(self, child_data: dict) -> Child:
        """Создание нового ребёнка"""
        child = Child(**child_data)
        self.session.add(child)
        await self.session.flush()
        await self.session.refresh(child)
        return child
    
    async def update(self, child: Child, child_data: dict) -> Child:
        """Обновление ребёнка"""
        for key, value in child_data.items():
            setattr(child, key, value)
        await self.session.flush()
        await self.session.refresh(child)
        return child
    
    async def delete(self, child: Child) -> None:
        """Удаление ребёнка"""
        await self.session.delete(child)
        await self.session.flush()



