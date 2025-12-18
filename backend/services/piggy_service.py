"""
Сервис для работы с копилкой
Согласно rules.md: бизнес-логика в services
"""
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.piggy_repository import PiggyRepository
from repositories.child_repository import ChildRepository
from schemas.piggy import PiggyGoalUpdate, PiggyAddRequest
from models.piggy import Piggy
from core.exceptions import NotFoundError
from decimal import Decimal


class PiggyService:
    """Сервис для работы с копилкой"""
    
    def __init__(self, session: AsyncSession):
        self.piggy_repo = PiggyRepository(session)
        self.child_repo = ChildRepository(session)
        self.session = session
    
    async def get_piggy(self, child_id: int) -> Piggy:
        """Получение копилки ребёнка"""
        child = await self.child_repo.get_by_id(child_id)
        if not child:
            raise NotFoundError("Ребёнок не найден")
        
        return await self.piggy_repo.get_or_create(child_id)
    
    async def update_goal(self, child_id: int, goal_data: PiggyGoalUpdate) -> dict:
        """Обновление цели копилки"""
        piggy = await self.get_piggy(child_id)
        
        update_data = goal_data.model_dump(exclude_unset=True)
        if update_data:
            await self.piggy_repo.create_or_update_goal(
                piggy.id,
                update_data.get("name", ""),
                Decimal(str(update_data.get("amount", 0)))
            )
        
        await self.session.refresh(piggy)
        return piggy
    
    async def add_virtual_currency(self, child_id: int, request: PiggyAddRequest) -> Piggy:
        """Добавление виртуальной валюты в копилку (для конвертации в подарки)"""
        piggy = await self.get_piggy(child_id)
        piggy.amount += request.amount
        
        await self.piggy_repo.add_history(
            piggy.id,
            "add",
            request.amount,
            request.description
        )
        
        await self.session.flush()
        await self.session.refresh(piggy)
        return piggy

