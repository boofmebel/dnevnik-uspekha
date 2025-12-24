"""
Роутер для Staff панели (admin, support, moderator)
Отдельная система для операторов и поддержки
Согласно плану миграции: разделение Product и Staff auth
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
from core.dependencies import get_current_staff, check_staff_role
from models.user import User
from models.subscription import Subscription
from models.notification import Notification, NotificationType
from models.child import Child
from models.task import Task
from models.star import Star

router = APIRouter()


@router.get("/stats", response_model=AdminStatsResponse)
async def get_staff_stats(
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin", "support", "moderator"]))
):
    """
    Получение общей статистики для staff панели
    Доступ: admin, support, moderator
    """
    from sqlalchemy.exc import ProgrammingError
    
    user_repo = UserRepository(db)
    
    # Общее количество пользователей
    try:
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0
    except Exception:
        total_users = 0
    
    # Количество родителей
    try:
        total_parents_result = await db.execute(
            select(func.count(User.id)).where(User.role == "parent")
        )
        total_parents = total_parents_result.scalar() or 0
    except Exception:
        total_parents = 0
    
    # Количество детей
    try:
        total_children_result = await db.execute(select(func.count(Child.id)))
        total_children = total_children_result.scalar() or 0
    except Exception:
        total_children = 0
    
    # Количество активных подписок
    try:
        active_subscriptions_result = await db.execute(
            select(func.count(Subscription.id)).where(Subscription.is_active == True)
        )
        active_subscriptions = active_subscriptions_result.scalar() or 0
    except Exception:
        active_subscriptions = 0
    
    # Количество задач
    try:
        total_tasks_result = await db.execute(select(func.count(Task.id)))
        total_tasks = total_tasks_result.scalar() or 0
    except Exception:
        total_tasks = 0
    
    # Количество звёзд
    try:
        total_stars_result = await db.execute(select(func.count(Star.id)))
        total_stars = total_stars_result.scalar() or 0
    except Exception:
        total_stars = 0
    
    return AdminStatsResponse(
        total_users=total_users,
        total_parents=total_parents,
        total_children=total_children,
        active_subscriptions=active_subscriptions,
        total_tasks=total_tasks,
        total_stars=total_stars
    )


@router.get("/users", response_model=List[AdminUserResponse])
async def get_staff_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None, description="Фильтр по роли"),
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin", "support"]))
):
    """
    Получение списка пользователей
    Доступ: admin, support
    """
    user_repo = UserRepository(db)
    
    query = select(User)
    if role:
        query = query.where(User.role == role)
    
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        AdminUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role if isinstance(user.role, str) else str(user.role),
            parent_id=user.parent_id,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
        for user in users
    ]


@router.get("/children", response_model=List[AdminChildResponse])
async def get_staff_children(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin", "support", "moderator"]))
):
    """
    Получение списка детей
    Доступ: admin, support, moderator
    """
    child_repo = ChildRepository(db)
    
    query = select(Child).order_by(desc(Child.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    children = result.scalars().all()
    
    return [
        AdminChildResponse(
            id=child.id,
            name=child.name,
            user_id=child.user_id,
            created_at=child.created_at.isoformat() if child.created_at else None
        )
        for child in children
    ]


@router.get("/subscriptions", response_model=List[AdminSubscriptionResponse])
async def get_staff_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin", "support"]))
):
    """
    Получение списка подписок
    Доступ: admin, support
    """
    subscription_repo = SubscriptionRepository(db)
    
    query = select(Subscription)
    if active_only:
        query = query.where(Subscription.is_active == True)
    
    query = query.order_by(desc(Subscription.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return [
        AdminSubscriptionResponse(
            id=sub.id,
            user_id=sub.user_id,
            is_active=sub.is_active,
            created_at=sub.created_at.isoformat() if sub.created_at else None
        )
        for sub in subscriptions
    ]


@router.get("/notifications", response_model=List[AdminNotificationResponse])
async def get_staff_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    type: Optional[str] = Query(None, description="Фильтр по типу"),
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin", "support", "moderator"]))
):
    """
    Получение списка уведомлений
    Доступ: admin, support, moderator
    """
    notification_repo = NotificationRepository(db)
    
    query = select(Notification)
    if type:
        query = query.where(Notification.type == type)
    
    query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [
        AdminNotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            type=notif.type.value if hasattr(notif.type, 'value') else str(notif.type),
            message=notif.message,
            created_at=notif.created_at.isoformat() if notif.created_at else None
        )
        for notif in notifications
    ]


@router.put("/users/{user_id}")
async def update_staff_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin"]))
):
    """
    Обновление пользователя
    Доступ: только admin
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    update_data = user_data.dict(exclude_unset=True)
    await user_repo.update(user_id, update_data)
    
    updated_user = await user_repo.get_by_id(user_id)
    return AdminUserResponse(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        phone=updated_user.phone,
        role=updated_user.role if isinstance(updated_user.role, str) else str(updated_user.role),
        parent_id=updated_user.parent_id,
        created_at=updated_user.created_at.isoformat() if updated_user.created_at else None
    )


@router.delete("/users/{user_id}")
async def delete_staff_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_staff: dict = Depends(check_staff_role(["admin"]))
):
    """
    Удаление пользователя
    Доступ: только admin
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    await user_repo.delete(user_id)
    return {"message": "Пользователь удалён"}


@router.get("/me")
async def get_staff_me(
    current_staff: dict = Depends(get_current_staff)
):
    """
    Получение информации о текущем staff пользователе
    """
    return {
        "id": current_staff.get("id"),
        "phone": current_staff.get("phone"),
        "email": current_staff.get("email"),
        "role": current_staff.get("role"),
        "is_staff": True
    }

