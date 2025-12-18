"""
Роутер для админ-панели
Согласно требованиям: полное управление сайтом
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from schemas.admin import (
    AdminUserResponse, AdminChildResponse, AdminSubscriptionResponse,
    AdminNotificationResponse, AdminStatsResponse, AdminUserUpdate, AdminChildUpdate
)
from repositories.user_repository import UserRepository
from repositories.child_repository import ChildRepository
from repositories.subscription_repository import SubscriptionRepository
from repositories.notification_repository import NotificationRepository
from core.database import get_db
from core.dependencies import get_current_user
from models.user import UserRole
from models.subscription import Subscription
from models.notification import Notification
from models.child import Child
from models.task import Task
from models.star import Star

router = APIRouter()


def check_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Проверка прав администратора"""
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin)
):
    """Получение общей статистики для админки"""
    user_repo = UserRepository(db)
    
    # Общее количество пользователей
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Количество родителей
    total_parents_result = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.PARENT)
    )
    total_parents = total_parents_result.scalar() or 0
    
    # Количество детей
    total_children_result = await db.execute(select(func.count(Child.id)))
    total_children = total_children_result.scalar() or 0
    
    # Активные подписки
    active_subscriptions_result = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.is_active == True)
    )
    active_subscriptions = active_subscriptions_result.scalar() or 0
    
    # Всего подписок
    total_subscriptions_result = await db.execute(select(func.count(Subscription.id)))
    total_subscriptions = total_subscriptions_result.scalar() or 0
    
    # Запросы на возврат
    refund_requests_result = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.refund_requested == True)
    )
    refund_requests = refund_requests_result.scalar() or 0
    
    # Всего уведомлений
    total_notifications_result = await db.execute(select(func.count(Notification.id)))
    total_notifications = total_notifications_result.scalar() or 0
    
    # Последние пользователи (10)
    recent_users_result = await db.execute(
        select(User)
        .order_by(desc(User.created_at))
        .limit(10)
    )
    recent_users = recent_users_result.scalars().all()
    
    # Последние подписки (10)
    recent_subscriptions_result = await db.execute(
        select(Subscription)
        .order_by(desc(Subscription.created_at))
        .limit(10)
    )
    recent_subscriptions = recent_subscriptions_result.scalars().all()
    
    # Последние уведомления (20)
    recent_notifications_result = await db.execute(
        select(Notification)
        .order_by(desc(Notification.created_at))
        .limit(20)
    )
    recent_notifications = recent_notifications_result.scalars().all()
    
    # Формируем ответы
    user_responses = []
    for user in recent_users:
        # Подсчитываем детей и подписки
        children_count = len(user.children) if hasattr(user, 'children') else 0
        subscriptions_count = len(user.subscriptions) if hasattr(user, 'subscriptions') else 0
        
        user_responses.append(AdminUserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            parent_id=user.parent_id,
            children_count=children_count,
            subscriptions_count=subscriptions_count,
            created_at=user.created_at,
            updated_at=user.updated_at
        ))
    
    subscription_responses = []
    for sub in recent_subscriptions:
        user = await user_repo.get_by_id(sub.user_id)
        subscription_responses.append(AdminSubscriptionResponse(
            id=sub.id,
            user_id=sub.user_id,
            user_email=user.email if user else "Unknown",
            start_date=sub.start_date,
            end_date=sub.end_date,
            is_active=sub.is_active,
            refund_requested=sub.refund_requested,
            refund_reason=sub.refund_reason,
            created_at=sub.created_at
        ))
    
    notification_responses = []
    for notif in recent_notifications:
        user = await user_repo.get_by_id(notif.user_id)
        notification_responses.append(AdminNotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            user_email=user.email if user else "Unknown",
            type=notif.type,
            message=notif.message,
            status=notif.status,
            created_at=notif.created_at
        ))
    
    return AdminStatsResponse(
        total_users=total_users,
        total_parents=total_parents,
        total_children=total_children,
        active_subscriptions=active_subscriptions,
        total_subscriptions=total_subscriptions,
        refund_requests=refund_requests,
        total_notifications=total_notifications,
        recent_users=user_responses,
        recent_subscriptions=subscription_responses,
        recent_notifications=notification_responses
    )


@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[UserRole] = None
):
    """Получение списка всех пользователей"""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    user_responses = []
    for user in users:
        children_count = len(user.children) if hasattr(user, 'children') else 0
        subscriptions_count = len(user.subscriptions) if hasattr(user, 'subscriptions') else 0
        
        user_responses.append(AdminUserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            parent_id=user.parent_id,
            children_count=children_count,
            subscriptions_count=subscriptions_count,
            created_at=user.created_at,
            updated_at=user.updated_at
        ))
    
    return user_responses


@router.get("/children", response_model=List[AdminChildResponse])
async def get_all_children(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Получение списка всех детей"""
    result = await db.execute(
        select(Child)
        .order_by(desc(Child.created_at))
        .offset(skip)
        .limit(limit)
    )
    children = result.scalars().all()
    
    child_responses = []
    for child in children:
        user = await UserRepository(db).get_by_id(child.user_id)
        
        # Подсчитываем задачи
        tasks_result = await db.execute(
            select(func.count(Task.id)).where(Task.child_id == child.id)
        )
        tasks_count = tasks_result.scalar() or 0
        
        # Получаем звёзды
        stars_result = await db.execute(
            select(Star).where(Star.child_id == child.id)
        )
        star = stars_result.scalar_one_or_none()
        stars_total = star.total if star else 0
        
        child_responses.append(AdminChildResponse(
            id=child.id,
            user_id=child.user_id,
            parent_email=user.email if user else "Unknown",
            name=child.name,
            gender=child.gender.value if child.gender else "none",
            tasks_count=tasks_count,
            stars_total=stars_total,
            created_at=child.created_at
        ))
    
    return child_responses


@router.get("/subscriptions", response_model=List[AdminSubscriptionResponse])
async def get_all_subscriptions(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(False)
):
    """Получение списка всех подписок"""
    query = select(Subscription)
    
    if active_only:
        query = query.where(Subscription.is_active == True)
    
    query = query.order_by(desc(Subscription.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    user_repo = UserRepository(db)
    subscription_responses = []
    for sub in subscriptions:
        user = await user_repo.get_by_id(sub.user_id)
        subscription_responses.append(AdminSubscriptionResponse(
            id=sub.id,
            user_id=sub.user_id,
            user_email=user.email if user else "Unknown",
            start_date=sub.start_date,
            end_date=sub.end_date,
            is_active=sub.is_active,
            refund_requested=sub.refund_requested,
            refund_reason=sub.refund_reason,
            created_at=sub.created_at
        ))
    
    return subscription_responses


@router.get("/notifications", response_model=List[AdminNotificationResponse])
async def get_all_notifications(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    type: Optional[NotificationType] = None
):
    """Получение списка всех уведомлений"""
    query = select(Notification)
    
    if type:
        query = query.where(Notification.type == type)
    
    query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    user_repo = UserRepository(db)
    notification_responses = []
    for notif in notifications:
        user = await user_repo.get_by_id(notif.user_id)
        notification_responses.append(AdminNotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            user_email=user.email if user else "Unknown",
            type=notif.type,
            message=notif.message,
            status=notif.status,
            created_at=notif.created_at
        ))
    
    return notification_responses


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin)
):
    """Обновление пользователя (блокировка, изменение роли)"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем данные
    update_data = user_data.model_dump(exclude_unset=True)
    # Здесь можно добавить логику блокировки (например, добавить поле is_active в модель User)
    
    if "email" in update_data:
        user.email = update_data["email"]
    if "role" in update_data:
        user.role = update_data["role"]
    
    await db.flush()
    await db.refresh(user)
    
    return {"message": "Пользователь обновлён", "user": AdminUserResponse.model_validate(user)}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(check_admin)
):
    """Удаление пользователя (осторожно!)"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Нельзя удалить самого себя
    if user.id == admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя"
        )
    
    await db.delete(user)
    await db.flush()
    
    return {"message": "Пользователь удалён"}

