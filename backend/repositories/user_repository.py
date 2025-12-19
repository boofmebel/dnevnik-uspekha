"""
Репозиторий для работы с пользователями
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Получение пользователя по номеру телефона"""
        result = await self.session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        """
        Создание нового пользователя
        
        Примечание: flush() отправляет SQL в БД, но не коммитит транзакцию.
        Коммит происходит в get_db() dependency после успешного выполнения endpoint.
        Если происходит ошибка, get_db() делает rollback автоматически.
        """
        try:
            user = User(**user_data)
            self.session.add(user)
            await self.session.flush()  # Отправляет в БД, получаем ID
            await self.session.refresh(user)  # Обновляем объект из БД
            return user
        except IntegrityError:
            # Пробрасываем IntegrityError для обработки в сервисе
            # Это позволяет обработать race conditions и дубликаты
            raise

