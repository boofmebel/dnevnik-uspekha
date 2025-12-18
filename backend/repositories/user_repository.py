"""
Репозиторий для работы с пользователями
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        """Создание нового пользователя"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

