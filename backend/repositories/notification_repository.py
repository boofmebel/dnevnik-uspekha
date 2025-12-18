"""
Репозиторий для работы с уведомлениями
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.notification import Notification, NotificationType, NotificationStatus


class NotificationRepository:
    """Репозиторий для работы с уведомлениями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, notification_data: dict) -> Notification:
        """Создание уведомления"""
        notification = Notification(**notification_data)
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification
    
    async def get_by_user_id(self, user_id: int, limit: int = 50) -> List[Notification]:
        """Получение уведомлений пользователя"""
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Получение уведомления по ID"""
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, notification: Notification, status: NotificationStatus) -> Notification:
        """Обновление статуса уведомления"""
        notification.status = status
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

