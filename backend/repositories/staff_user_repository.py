"""
Repository для работы с staff_users
Согласно rules.md: repositories для доступа к БД
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from models.staff_user import StaffUser
from datetime import datetime


class StaffUserRepository:
    """Repository для работы с staff пользователями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, staff_id: int) -> Optional[StaffUser]:
        """Получить staff пользователя по ID"""
        result = await self.db.execute(
            select(StaffUser).where(StaffUser.id == staff_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[StaffUser]:
        """Получить staff пользователя по email"""
        result = await self.db.execute(
            select(StaffUser).where(StaffUser.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[StaffUser]:
        """Получить staff пользователя по телефону"""
        result = await self.db.execute(
            select(StaffUser).where(StaffUser.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def create(self, phone: str, password_hash: str, role: str, email: Optional[str] = None) -> StaffUser:
        """Создать нового staff пользователя"""
        staff_user = StaffUser(
            phone=phone,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        self.db.add(staff_user)
        await self.db.flush()
        await self.db.refresh(staff_user)
        return staff_user
    
    async def update_last_login(self, staff_id: int) -> None:
        """Обновить время последнего входа"""
        await self.db.execute(
            update(StaffUser)
            .where(StaffUser.id == staff_id)
            .values(last_login=datetime.now())
        )
        await self.db.flush()
    
    async def update_password(self, staff_id: int, password_hash: str) -> None:
        """Обновить пароль staff пользователя"""
        await self.db.execute(
            update(StaffUser)
            .where(StaffUser.id == staff_id)
            .values(password_hash=password_hash)
        )
        await self.db.flush()
    
    async def set_active(self, staff_id: int, is_active: bool) -> None:
        """Установить статус активности staff пользователя"""
        await self.db.execute(
            update(StaffUser)
            .where(StaffUser.id == staff_id)
            .values(is_active=is_active)
        )
        await self.db.flush()
    
    async def get_all_active(self) -> list[StaffUser]:
        """Получить всех активных staff пользователей"""
        result = await self.db.execute(
            select(StaffUser).where(StaffUser.is_active == True)
        )
        return list(result.scalars().all())

