"""
Сервис для работы с уведомлениями
Согласно rules.md: бизнес-логика в services
"""
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.notification_repository import NotificationRepository
from typing import Optional
from models.notification import NotificationType, NotificationStatus
from schemas.notification import NotificationCreate
import json


class NotificationService:
    """Сервис для работы с уведомлениями"""
    
    def __init__(self, session: AsyncSession):
        self.notification_repo = NotificationRepository(session)
        self.session = session
    
    async def send_notification(
        self,
        user_id: int,
        type: NotificationType,
        message: str,
        subscription_id: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Шаблонная функция для отправки уведомлений
        Согласно требованиям: логирование всех действий
        """
        notification_data = {
            "user_id": user_id,
            "type": type,
            "message": message,
            "subscription_id": subscription_id,
            "status": NotificationStatus.PENDING,
            "meta_data": json.dumps(metadata) if metadata else None
        }
        
        notification = await self.notification_repo.create(notification_data)
        
        # Здесь можно добавить отправку через email/push/telegram
        # Пока просто помечаем как отправленное
        await self.notification_repo.update_status(notification, NotificationStatus.SENT)
        
        return {
            "id": notification.id,
            "status": "sent",
            "message": "Уведомление отправлено"
        }

