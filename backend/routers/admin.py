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
from core.dependencies import get_current_user, check_admin_access
from models.user import User, UserRole
from models.subscription import Subscription
from models.notification import Notification, NotificationType
from models.child import Child
from models.task import Task
from models.star import Star

router = APIRouter()


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(check_admin_access)
):
    """Получение общей статистики для админки"""
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
    
    # Активные подписки
    try:
        active_subscriptions_result = await db.execute(
            select(func.count(Subscription.id)).where(Subscription.is_active == True)
        )
        active_subscriptions = active_subscriptions_result.scalar() or 0
    except Exception:
        active_subscriptions = 0
    
    # Всего подписок
    try:
        total_subscriptions_result = await db.execute(select(func.count(Subscription.id)))
        total_subscriptions = total_subscriptions_result.scalar() or 0
    except Exception:
        total_subscriptions = 0
    
    # Запросы на возврат
    try:
        refund_requests_result = await db.execute(
            select(func.count(Subscription.id)).where(Subscription.refund_requested == True)
        )
        refund_requests = refund_requests_result.scalar() or 0
    except Exception:
        refund_requests = 0
    
    # Всего уведомлений
    try:
        total_notifications_result = await db.execute(select(func.count(Notification.id)))
        total_notifications = total_notifications_result.scalar() or 0
    except Exception:
        total_notifications = 0
    
    # Последние пользователи (10)
    try:
        recent_users_result = await db.execute(
            select(User)
            .order_by(desc(User.created_at))
            .limit(10)
        )
        recent_users = list(recent_users_result.scalars().all())
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Загружено пользователей для статистики: {len(recent_users)}")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка загрузки пользователей: {e}", exc_info=True)
        recent_users = []
    
    # Последние подписки (10)
    try:
        recent_subscriptions_result = await db.execute(
            select(Subscription)
            .order_by(desc(Subscription.created_at))
            .limit(10)
        )
        recent_subscriptions = recent_subscriptions_result.scalars().all()
    except Exception:
        recent_subscriptions = []
    
    # Последние уведомления (20)
    try:
        recent_notifications_result = await db.execute(
            select(Notification)
            .order_by(desc(Notification.created_at))
            .limit(20)
        )
        recent_notifications = recent_notifications_result.scalars().all()
    except Exception:
        recent_notifications = []
    
    # Формируем ответы
    import logging
    logger = logging.getLogger(__name__)
    user_responses = []
    logger.info(f"Начинаем обработку {len(recent_users)} пользователей для статистики")
    for user in recent_users:
        try:
            # Подсчитываем детей и подписки через запросы, чтобы избежать проблем с lazy loading
            children_count = 0
            subscriptions_count = 0
            try:
                # Используем уже импортированные модели
                children_result = await db.execute(
                    select(func.count(Child.id)).where(Child.user_id == user.id)
                )
                children_count = children_result.scalar() or 0
                
                subscriptions_result = await db.execute(
                    select(func.count(Subscription.id)).where(Subscription.user_id == user.id)
                )
                subscriptions_count = subscriptions_result.scalar() or 0
            except Exception as count_error:
                # Продолжаем с нулевыми значениями
                logger.warning(f"Ошибка подсчета для пользователя {user.id}: {count_error}")
                pass
            
            # Преобразуем role в строку для схемы
            role_str = user.role
            if isinstance(role_str, str):
                pass  # Уже строка
            elif hasattr(role_str, 'value'):
                role_str = role_str.value
            else:
                role_str = str(role_str)
            
            user_response = AdminUserResponse(
                id=user.id,
                name=user.name,
                phone=user.phone,
                email=user.email,
                role=role_str,
                parent_id=user.parent_id,
                children_count=children_count,
                subscriptions_count=subscriptions_count,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            user_responses.append(user_response)
            logger.info(f"✅ Обработан пользователь {user.id}: {user.name or user.phone or user.email}, роль: {role_str}")
        except Exception as e:
            logger.error(f"❌ Ошибка обработки пользователя {user.id}: {e}", exc_info=True)
            continue
    
    logger.info(f"Всего обработано пользователей: {len(user_responses)} из {len(recent_users)}")
    
    subscription_responses = []
    for sub in recent_subscriptions:
        try:
            user = await user_repo.get_by_id(sub.user_id)
            # Используем имя, телефон или email для идентификации пользователя
            user_identifier = "Unknown"
            if user:
                user_identifier = user.name or user.phone or user.email or "Unknown"
            
            subscription_responses.append(AdminSubscriptionResponse(
                id=sub.id,
                user_id=sub.user_id,
                user_email=user_identifier,
                start_date=sub.start_date,
                end_date=sub.end_date,
                is_active=sub.is_active,
                refund_requested=sub.refund_requested,
                refund_reason=sub.refund_reason,
                created_at=sub.created_at
            ))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка обработки подписки {sub.id}: {e}")
            continue
    
    notification_responses = []
    for notif in recent_notifications:
        try:
            user = await user_repo.get_by_id(notif.user_id)
            # Используем имя, телефон или email для идентификации пользователя
            user_identifier = "Unknown"
            if user:
                user_identifier = user.name or user.phone or user.email or "Unknown"
            
            notification_responses.append(AdminNotificationResponse(
                id=notif.id,
                user_id=notif.user_id,
                user_email=user_identifier,
                type=notif.type,
                message=notif.message,
                status=notif.status,
                created_at=notif.created_at
            ))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка обработки уведомления {notif.id}: {e}")
            continue
    
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
    current_admin: dict = Depends(check_admin_access),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[UserRole] = None
):
    """Получение списка всех пользователей"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        
        query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        user_responses = []
        for user in users:
            try:
                # Подсчитываем детей и подписки через запросы, чтобы избежать проблем с lazy loading
                children_count = 0
                subscriptions_count = 0
                try:
                    from models.child import Child
                    from models.subscription import Subscription
                    children_result = await db.execute(
                        select(func.count(Child.id)).where(Child.user_id == user.id)
                    )
                    children_count = children_result.scalar() or 0
                    
                    subscriptions_result = await db.execute(
                        select(func.count(Subscription.id)).where(Subscription.user_id == user.id)
                    )
                    subscriptions_count = subscriptions_result.scalar() or 0
                except Exception as count_error:
                    logger.warning(f"Ошибка подсчета для пользователя {user.id}: {count_error}")
                    # Продолжаем с нулевыми значениями
                
                # Преобразуем роль в строку для схемы
                role_str = user.role
                if isinstance(role_str, str):
                    pass  # Уже строка
                elif hasattr(role_str, 'value'):
                    role_str = role_str.value
                else:
                    role_str = str(role_str)
                
                user_responses.append(AdminUserResponse(
                    id=user.id,
                    name=user.name,
                    phone=user.phone,
                    email=user.email,
                    role=role_str,
                    parent_id=user.parent_id,
                    children_count=children_count,
                    subscriptions_count=subscriptions_count,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ))
            except Exception as e:
                logger.error(f"Ошибка обработки пользователя {user.id}: {e}", exc_info=True)
                continue
        
        return user_responses
    except Exception as e:
        logger.error(f"Ошибка получения пользователей из БД: {e}", exc_info=True)
        # Возвращаем пустой список вместо ошибки 500
        return []


@router.get("/children", response_model=List[AdminChildResponse])
async def get_all_children(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(check_admin_access),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Получение списка всех детей"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        result = await db.execute(
            select(Child)
            .order_by(desc(Child.created_at))
            .offset(skip)
            .limit(limit)
        )
        children = result.scalars().all()
        
        child_responses = []
        for child in children:
            try:
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
                
                # Используем имя, телефон или email для идентификации родителя
                parent_identifier = "Unknown"
                if user:
                    parent_identifier = user.name or user.phone or user.email or "Unknown"
                
                child_responses.append(AdminChildResponse(
                    id=child.id,
                    user_id=child.user_id,
                    parent_email=parent_identifier,
                    name=child.name,
                    gender=child.gender.value if child.gender else "none",
                    tasks_count=tasks_count,
                    stars_total=stars_total,
                    created_at=child.created_at
                ))
            except Exception as e:
                logger.error(f"Ошибка обработки ребёнка {child.id}: {e}")
                # Продолжаем обработку других детей
                continue
        
        return child_responses
    except Exception as e:
        logger.error(f"Ошибка получения детей из БД: {e}", exc_info=True)
        # Возвращаем пустой список вместо ошибки 500
        return []


@router.get("/subscriptions", response_model=List[AdminSubscriptionResponse])
async def get_all_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(check_admin_access),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(False)
):
    """Получение списка всех подписок"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        query = select(Subscription)
        
        if active_only:
            query = query.where(Subscription.is_active == True)
        
        query = query.order_by(desc(Subscription.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        subscriptions = result.scalars().all()
        
        user_repo = UserRepository(db)
        subscription_responses = []
        for sub in subscriptions:
            try:
                user = await user_repo.get_by_id(sub.user_id)
                # Используем имя, телефон или email для идентификации пользователя
                user_identifier = "Unknown"
                if user:
                    user_identifier = user.name or user.phone or user.email or "Unknown"
                
                subscription_responses.append(AdminSubscriptionResponse(
                    id=sub.id,
                    user_id=sub.user_id,
                    user_email=user_identifier,
                    start_date=sub.start_date,
                    end_date=sub.end_date,
                    is_active=sub.is_active,
                    refund_requested=sub.refund_requested,
                    refund_reason=sub.refund_reason,
                    created_at=sub.created_at
                ))
            except Exception as e:
                logger.error(f"Ошибка обработки подписки {sub.id}: {e}")
                # Продолжаем обработку других подписок
                continue
        
        return subscription_responses
    except Exception as e:
        logger.error(f"Ошибка получения подписок из БД: {e}", exc_info=True)
        # Возвращаем пустой список вместо ошибки 500
        return []


@router.get("/notifications", response_model=List[AdminNotificationResponse])
async def get_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(check_admin_access),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    type: Optional[NotificationType] = None
):
    """Получение списка всех уведомлений"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        query = select(Notification)
        
        if type:
            query = query.where(Notification.type == type)
        
        query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        user_repo = UserRepository(db)
        notification_responses = []
        for notif in notifications:
            try:
                user = await user_repo.get_by_id(notif.user_id)
                # Используем имя, телефон или email для идентификации пользователя
                user_identifier = "Unknown"
                if user:
                    user_identifier = user.name or user.phone or user.email or "Unknown"
                
                notification_responses.append(AdminNotificationResponse(
                    id=notif.id,
                    user_id=notif.user_id,
                    user_email=user_identifier,
                    type=notif.type,
                    message=notif.message,
                    status=notif.status,
                    created_at=notif.created_at
                ))
            except Exception as e:
                # Логируем ошибку, но продолжаем обработку других уведомлений
                logger.error(f"Ошибка обработки уведомления {notif.id}: {e}")
                continue
            except Exception as e:
                # Логируем ошибку, но продолжаем обработку других уведомлений
                logger.error(f"Ошибка обработки уведомления {notif.id}: {e}")
                continue
        
        return notification_responses
    except Exception as e:
        logger.error(f"Ошибка получения уведомлений из БД: {e}", exc_info=True)
        # Возвращаем пустой список вместо ошибки 500
        return []


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(check_admin_access)
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
    
    if "name" in update_data:
        user.name = update_data["name"] if update_data["name"] else None
    
    if "phone" in update_data:
        from core.utils.phone_validator import normalize_phone, validate_phone
        phone = update_data["phone"]
        if phone:
            normalized_phone = normalize_phone(phone)
            if not validate_phone(normalized_phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный формат номера телефона"
                )
            user.phone = normalized_phone
    
    if "parent_id" in update_data:
        user.parent_id = update_data["parent_id"]
    
    if "email" in update_data:
        user.email = update_data["email"]
    if "role" in update_data:
        # Преобразуем роль в строку для сохранения в БД (модель User хранит роль как String)
        role = update_data["role"]
        if isinstance(role, UserRole):
            user.role = role.value
        elif isinstance(role, str):
            user.role = role
        else:
            user.role = str(role)
    
    await db.flush()
    await db.refresh(user)
    
    return {"message": "Пользователь обновлён", "user": AdminUserResponse.model_validate(user)}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(check_admin_access)
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
    if user.id == current_admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя"
        )
    
    await db.delete(user)
    await db.flush()
    
    return {"message": "Пользователь удалён"}

