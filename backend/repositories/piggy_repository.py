"""
Репозиторий для работы с копилкой
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.piggy import Piggy, PiggyGoal, PiggyHistory
from decimal import Decimal


class PiggyRepository:
    """Репозиторий для работы с копилкой"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_child_id(self, child_id: int) -> Optional[Piggy]:
        """Получение копилки ребёнка"""
        result = await self.session.execute(
            select(Piggy).where(Piggy.child_id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, child_id: int) -> Piggy:
        """Получение или создание копилки для ребёнка"""
        piggy = await self.get_by_child_id(child_id)
        if not piggy:
            piggy = Piggy(child_id=child_id)
            self.session.add(piggy)
            await self.session.flush()
            await self.session.refresh(piggy)
        return piggy
    
    async def get_goal(self, piggy_id: int) -> Optional[PiggyGoal]:
        """Получение цели копилки"""
        result = await self.session.execute(
            select(PiggyGoal).where(PiggyGoal.piggy_id == piggy_id)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_goal(self, piggy_id: int, name: str, amount: Decimal) -> PiggyGoal:
        """Создание или обновление цели"""
        goal = await self.get_goal(piggy_id)
        if not goal:
            goal = PiggyGoal(piggy_id=piggy_id, name=name, amount=amount)
            self.session.add(goal)
        else:
            goal.name = name
            goal.amount = amount
        await self.session.flush()
        await self.session.refresh(goal)
        return goal
    
    async def add_history(self, piggy_id: int, type: str, amount: Decimal, description: Optional[str] = None) -> PiggyHistory:
        """Добавление записи в историю"""
        history = PiggyHistory(piggy_id=piggy_id, type=type, amount=amount, description=description)
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history
    
    async def get_history(self, piggy_id: int, limit: int = 50) -> List[PiggyHistory]:
        """Получение истории копилки"""
        result = await self.session.execute(
            select(PiggyHistory)
            .where(PiggyHistory.piggy_id == piggy_id)
            .order_by(PiggyHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())






