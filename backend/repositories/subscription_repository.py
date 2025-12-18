"""
Репозиторий для работы с подписками
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.subscription import Subscription
from models.parent_consent import ParentConsent


class SubscriptionRepository:
    """Репозиторий для работы с подписками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """Получение подписки пользователя"""
        result = await self.session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, subscription_data: dict) -> Subscription:
        """Создание подписки"""
        subscription = Subscription(**subscription_data)
        self.session.add(subscription)
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription
    
    async def update(self, subscription: Subscription, subscription_data: dict) -> Subscription:
        """Обновление подписки"""
        for key, value in subscription_data.items():
            setattr(subscription, key, value)
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription


class ParentConsentRepository:
    """Репозиторий для работы с согласиями родителей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_id(self, user_id: int) -> Optional[ParentConsent]:
        """Получение согласия пользователя"""
        result = await self.session.execute(
            select(ParentConsent).where(ParentConsent.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_child_id(self, child_id: int) -> Optional[ParentConsent]:
        """Получение согласия для ребёнка"""
        result = await self.session.execute(
            select(ParentConsent).where(ParentConsent.child_id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, consent_data: dict) -> ParentConsent:
        """Создание согласия"""
        consent = ParentConsent(**consent_data)
        self.session.add(consent)
        await self.session.flush()
        await self.session.refresh(consent)
        return consent
    
    async def update(self, consent: ParentConsent, consent_data: dict) -> ParentConsent:
        """Обновление согласия"""
        for key, value in consent_data.items():
            setattr(consent, key, value)
        await self.session.flush()
        await self.session.refresh(consent)
        return consent

