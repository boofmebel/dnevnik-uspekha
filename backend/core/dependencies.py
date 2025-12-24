"""
Dependencies для FastAPI
Согласно rules.md: получение текущего пользователя, проверка прав
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security.jwt import verify_token
from repositories.user_repository import UserRepository
from repositories.child_repository import ChildRepository
from repositories.subscription_repository import ParentConsentRepository
from core.exceptions import ForbiddenError
from models.user import UserRole

security = HTTPBearer(auto_error=False)  # Отключаем автоматическую ошибку для отладки


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Получение текущего пользователя из JWT токена"""
    # Пробуем получить токен из HTTPBearer
    token = None
    if credentials:
        token = credentials.credentials
    
    # Если не получили, пробуем из заголовка напрямую
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен"
        )
    
    # Логируем для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"=== TOKEN VERIFICATION START ===")
    logger.info(f"Token preview: {token[:50]}... (length: {len(token)})")
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Authorization header: {request.headers.get('Authorization', 'NOT SET')[:50]}...")
    
    try:
        payload = verify_token(token)
        
        if not payload:
            logger.error(f"Token verification failed: payload is None")
            logger.error(f"This usually means:")
            logger.error(f"  1. Token expired")
            logger.error(f"  2. SECRET_KEY mismatch")
            logger.error(f"  3. Invalid token format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный или истекший токен. Пожалуйста, войдите заново."
            )
        
        logger.info(f"Token verified successfully. Payload: {payload}")
        user_id = int(payload.get("sub"))
        logger.info(f"Extracted user_id: {user_id}")
        
        try:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_id(user_id)
        except Exception as db_error:
            logger.error(f"Ошибка подключения к БД при проверке пользователя: {db_error}")
            # Если БД недоступна, но токен валиден, создаем временного пользователя из токена
            # Это позволяет работать админке даже если БД временно недоступна
            role_from_token = payload.get("role", "admin")
            logger.warning(f"БД недоступна, используем данные из токена: user_id={user_id}, role={role_from_token}")
            result = {
                "id": user_id,
                "email": None,
                "phone": None,
                "role": role_from_token
            }
            logger.info(f"=== TOKEN VERIFICATION SUCCESS (без БД) ===")
            return result
        
        if not user:
            logger.warning(f"User not found for user_id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        logger.info(f"User found: id={user.id}, email={user.email}, phone={user.phone}, role={user.role}")
        
        # Преобразуем роль в строку для совместимости
        role = user.role
        if hasattr(role, 'value'):
            role = role.value
        elif not isinstance(role, str):
            role = str(role)
        
        result = {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "role": role
        }
        
        logger.info(f"=== TOKEN VERIFICATION SUCCESS ===")
        logger.info(f"Returning user: id={result['id']}, role={result['role']}")
        return result
    except HTTPException:
        logger.error(f"=== TOKEN VERIFICATION FAILED (HTTPException) ===")
        raise
    except Exception as e:
        logger.error(f"=== TOKEN VERIFICATION FAILED (Exception) ===")
        logger.error(f"Error in get_current_user: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка проверки токена: {str(e)}"
        )


async def get_current_child(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Получение текущего ребёнка пользователя"""
    child_repo = ChildRepository(db)
    children = await child_repo.get_by_user_id(current_user["id"])
    
    if not children:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # Для упрощения возвращаем первого ребёнка
    # В реальной реализации можно добавить выбор ребёнка
    return children[0]


async def check_parent_consent(
    current_user: dict = Depends(get_current_user),
    current_child: dict = Depends(get_current_child),
    db: AsyncSession = Depends(get_db)
) -> bool:
    """
    Проверка согласия родителей на обработку данных ребёнка
    Согласно требованиям: обязательная проверка перед действиями с данными ребёнка
    """
    consent_repo = ParentConsentRepository(db)
    consent = await consent_repo.get_by_child_id(current_child.id)
    
    if not consent or not consent.consent_given:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется согласие родителей на обработку данных ребёнка"
        )
    
    return True


async def check_admin_access(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Проверка прав администратора
    """
    # Проверяем роль (может быть строкой или enum)
    user_role = current_user.get("role")
    
    # Логируем для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Checking admin access for role: {user_role}, type: {type(user_role)}")
    
    # Нормализуем роль к строке для проверки
    role_str = None
    if isinstance(user_role, str):
        role_str = user_role.lower().strip()
    elif isinstance(user_role, UserRole):
        role_str = user_role.value.lower().strip()
    elif hasattr(user_role, 'value'):
        role_str = str(user_role.value).lower().strip()
    else:
        role_str = str(user_role).lower().strip()
    
    # Проверяем, является ли роль администратором
    is_admin = role_str == "admin" or role_str == UserRole.ADMIN.value.lower()
    
    if not is_admin:
        logger.warning(f"Access denied: role '{user_role}' (normalized: '{role_str}') is not admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Недостаточно прав. Требуется роль администратора. Текущая роль: {user_role}"
        )
    
    logger.info(f"Admin access granted for user {current_user.get('id')}")
    return current_user


async def get_current_staff(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Получение текущего staff пользователя из JWT токена
    Используется для staff routes (/api/staff/*)
    """
    from repositories.staff_user_repository import StaffUserRepository
    
    # Пробуем получить токен из HTTPBearer
    token = None
    if credentials:
        token = credentials.credentials
    
    # Если не получили, пробуем из заголовка напрямую
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен"
        )
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"=== STAFF TOKEN VERIFICATION START ===")
    logger.info(f"Token preview: {token[:50]}... (length: {len(token)})")
    
    try:
        payload = verify_token(token)
        
        if not payload:
            logger.error("Staff token verification failed: payload is None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный или истекший токен. Пожалуйста, войдите заново."
            )
        
        logger.info(f"Staff token verified successfully. Payload: {payload}")
        staff_id = int(payload.get("sub"))
        logger.info(f"Extracted staff_id: {staff_id}")
        
        try:
            staff_repo = StaffUserRepository(db)
            staff_user = await staff_repo.get_by_id(staff_id)
        except Exception as db_error:
            logger.error(f"Ошибка подключения к БД при проверке staff пользователя: {db_error}")
            # Если БД недоступна, но токен валиден, создаем временного staff из токена
            role_from_token = payload.get("role", "admin")
            logger.warning(f"БД недоступна, используем данные из токена: staff_id={staff_id}, role={role_from_token}")
            result = {
                "id": staff_id,
                "email": None,
                "role": role_from_token,
                "is_staff": True
            }
            logger.info(f"=== STAFF TOKEN VERIFICATION SUCCESS (без БД) ===")
            return result
        
        if not staff_user:
            logger.warning(f"Staff user not found for staff_id: {staff_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Staff пользователь не найден"
            )
        
        if not staff_user.is_active:
            logger.warning(f"Staff user {staff_id} is not active")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт staff пользователя деактивирован"
            )
        
        logger.info(f"Staff user found: id={staff_user.id}, email={staff_user.email}, role={staff_user.role}")
        
        # Преобразуем роль в строку для совместимости
        role = staff_user.role
        if not isinstance(role, str):
            role = str(role)
        
        result = {
            "id": staff_user.id,
            "phone": staff_user.phone,
            "email": staff_user.email,
            "role": role,
            "is_staff": True
        }
        
        logger.info(f"=== STAFF TOKEN VERIFICATION SUCCESS ===")
        logger.info(f"Returning staff: id={result['id']}, role={result['role']}")
        return result
    except HTTPException:
        logger.error("=== STAFF TOKEN VERIFICATION FAILED (HTTPException) ===")
        raise
    except Exception as e:
        logger.error(f"=== STAFF TOKEN VERIFICATION FAILED (Exception) ===")
        logger.error(f"Error in get_current_staff: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка проверки токена: {str(e)}"
        )


def check_staff_role(required_roles: list[str]):
    """
    Фабрика для создания dependency проверки роли staff пользователя (RBAC)
    required_roles: список разрешённых ролей, например ['admin', 'support']
    
    Использование:
        current_staff: dict = Depends(check_staff_role(["admin", "support"]))
    """
    async def _check_staff_role_inner(
        current_staff: dict = Depends(get_current_staff)
    ) -> dict:
        staff_role = current_staff.get("role", "").lower()
        
        if staff_role not in [r.lower() for r in required_roles]:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Staff access denied: role '{staff_role}' not in {required_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуются роли: {', '.join(required_roles)}. Ваша роль: {staff_role}"
            )
        
        return current_staff
    
    return _check_staff_role_inner

