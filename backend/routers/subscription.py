"""
Роутер для работы с подпиской
Согласно требованиям: управление подпиской с проверкой согласия родителей
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.subscription import (
    SubscriptionResponse,
    SubscriptionCancelRequest,
    SubscriptionRefundRequest,
    ParentConsentRequest,
    ParentConsentResponse
)
from repositories.subscription_repository import SubscriptionRepository, ParentConsentRepository
from services.notification_service import NotificationService
from models.notification import NotificationType
from core.database import get_db
from core.dependencies import get_current_user, check_parent_consent
from core.exceptions import NotFoundError, ValidationError
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/", response_model=SubscriptionResponse)
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение информации о подписке"""
    repo = SubscriptionRepository(db)
    subscription = await repo.get_by_user_id(current_user["id"])
    
    if not subscription:
        raise NotFoundError("Подписка не найдена")
    
    return SubscriptionResponse.model_validate(subscription)


@router.post("/consent", response_model=ParentConsentResponse)
async def create_parent_consent(
    consent_data: ParentConsentRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Создание согласия родителей на обработку данных ребёнка
    Согласно требованиям: обязательное согласие перед использованием Сервиса
    """
    from repositories.child_repository import ChildRepository
    
    child_repo = ChildRepository(db)
    child = await child_repo.get_by_id(consent_data.child_id)
    
    if not child or child.user_id != current_user["id"]:
        raise NotFoundError("Ребёнок не найден")
    
    consent_repo = ParentConsentRepository(db)
    existing_consent = await consent_repo.get_by_child_id(consent_data.child_id)
    
    # Получаем IP и User-Agent для аудита
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    consent_dict = {
        "user_id": current_user["id"],
        "child_id": consent_data.child_id,
        "consent_given": consent_data.consent_given,
        "consent_date": datetime.now() if consent_data.consent_given else None,
        "ip_address": ip_address,
        "user_agent": user_agent
    }
    
    if existing_consent:
        consent = await consent_repo.update(existing_consent, consent_dict)
    else:
        consent = await consent_repo.create(consent_dict)
    
    # Логируем создание согласия
    notification_service = NotificationService(db)
    await notification_service.send_notification(
        user_id=current_user["id"],
        type=NotificationType.CONSENT,
        message=f"Согласие родителей {'предоставлено' if consent_data.consent_given else 'отозвано'} для ребёнка {child.name}"
    )
    
    return ParentConsentResponse.model_validate(consent)


@router.post("/cancel")
async def cancel_subscription(
    cancel_data: SubscriptionCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(check_parent_consent)
):
    """
    Отмена подписки
    Согласно требованиям: проверка согласия родителей обязательна
    """
    repo = SubscriptionRepository(db)
    subscription = await repo.get_by_user_id(current_user["id"])
    
    if not subscription:
        raise NotFoundError("Подписка не найдена")
    
    if not subscription.is_active:
        raise ValidationError("Подписка уже отменена")
    
    # Отменяем подписку (не удаляем, а помечаем как неактивную)
    subscription.is_active = False
    await repo.update(subscription, {"is_active": False})
    
    # Логируем отмену
    notification_service = NotificationService(db)
    await notification_service.send_notification(
        user_id=current_user["id"],
        type=NotificationType.SUBSCRIPTION,
        message=f"Подписка отменена. Причина: {cancel_data.reason or 'Не указана'}",
        subscription_id=subscription.id
    )
    
    return {
        "status": "success",
        "message": "Подписка успешно отменена",
        "subscription": SubscriptionResponse.model_validate(subscription)
    }


@router.post("/refund-request")
async def request_refund(
    refund_data: SubscriptionRefundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(check_parent_consent)
):
    """
    Запрос на возврат средств
    Согласно требованиям: проверка согласия родителей и логирование
    """
    if not refund_data.parent_consent:
        raise ValidationError("Требуется подтверждение согласия родителя")
    
    repo = SubscriptionRepository(db)
    subscription = await repo.get_by_user_id(current_user["id"])
    
    if not subscription:
        raise NotFoundError("Подписка не найдена")
    
    if subscription.refund_requested:
        raise ValidationError("Запрос на возврат уже был отправлен")
    
    # Проверяем срок (14 дней с момента оформления)
    days_since_start = (datetime.now() - subscription.start_date).days
    if days_since_start > 14:
        raise ValidationError("Срок для запроса возврата истёк (14 дней с момента оформления)")
    
    # Помечаем запрос на возврат
    subscription.refund_requested = True
    subscription.refund_reason = refund_data.reason
    await repo.update(subscription, {
        "refund_requested": True,
        "refund_reason": refund_data.reason
    })
    
    # Логируем запрос на возврат
    notification_service = NotificationService(db)
    await notification_service.send_notification(
        user_id=current_user["id"],
        type=NotificationType.REFUND,
        message=f"Запрос на возврат средств. Причина: {refund_data.reason}",
        subscription_id=subscription.id,
        metadata={"days_since_start": days_since_start}
    )
    
    return {
        "status": "success",
        "message": "Запрос на возврат средств отправлен. Ожидайте обработки в течение 30 дней.",
        "subscription": SubscriptionResponse.model_validate(subscription)
    }

