"""
Роутер для аутентификации
Согласно rules.md: JWT, refresh token rotation, rate limiting
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest,
    RegisterRequest, ChildPinRequest, ChildQrRequest, ChildAccessResponse,
    AdminLoginRequest
)
from services.auth_service import AuthService
from core.security.jwt import verify_token, create_access_token
from core.database import get_db
from core.dependencies import get_current_user
from core.exceptions import ValidationError
from core.middleware.rate_limit import limiter

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: LoginRequest,
    http_request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему
    Согласно rules.md: rate limiting на login endpoint (5 попыток в минуту)
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate(
        email=request.email,
        phone=request.phone,
        password=request.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email/телефон или пароль")
    
    # Создание токенов с ролью пользователя
    access_token = auth_service.create_access_token(user["id"], user.get("role"))
    refresh_token = auth_service.create_refresh_token(user["id"], user.get("role"))
    
    # Получение информации об устройстве для логирования
    device_info = f"{http_request.headers.get('user-agent', 'Unknown')} | {http_request.client.host if http_request.client else 'Unknown'}"
    
    # Сохранение refresh token в БД (согласно rules.md)
    await auth_service.save_refresh_token(user["id"], refresh_token, device_info=device_info)
    
    # Установка refresh token в HttpOnly cookie (согласно rules.md)
    # secure=True только в production (HTTPS)
    from core.config import settings
    secure_cookie = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",  # lax для работы через прокси
        max_age=30 * 24 * 60 * 60  # 30 дней
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access token
    Согласно rules.md: rotation + новый access token
    """
    auth_service = AuthService(db)
    
    # Получение refresh token из HttpOnly cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token не найден")
    
    # Получение информации об устройстве для логирования
    device_info = f"{request.headers.get('user-agent', 'Unknown')} | {request.client.host if request.client else 'Unknown'}"
    
    # Проверка и ротация токена
    new_access_token, new_refresh_token = await auth_service.refresh_token_rotation(
        refresh_token, 
        device_info=device_info
    )
    
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Недействительный или истекший refresh token")
    
    # Установка нового refresh token в HttpOnly cookie
    # secure=True только в production (HTTPS)
    from core.config import settings
    secure_cookie = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",  # lax для работы через прокси
        max_age=30 * 24 * 60 * 60  # 30 дней
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/register")
@limiter.limit("3/hour")
async def register(
    request: RegisterRequest,
    http_request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя (родителя)
    
    Все операции выполняются в одной транзакции:
    1. Создание пользователя
    2. Создание токенов
    3. Сохранение refresh token (если реализовано)
    
    При ошибке транзакция откатывается автоматически через get_db()
    """
    auth_service = AuthService(db)
    try:
        # Регистрация пользователя (создает запись в БД через flush)
        user = await auth_service.register(
            phone=request.phone,
            password=request.password,
            name=request.name,
            role=request.role,
            email=None  # Email больше не используется при регистрации
        )
        
        # Автоматический вход после регистрации
        access_token = auth_service.create_access_token(user["id"], user.get("role"))
        refresh_token = auth_service.create_refresh_token(user["id"], user.get("role"))
        
        # Получение информации об устройстве для логирования
        device_info = f"{http_request.headers.get('user-agent', 'Unknown')} | {http_request.client.host if http_request.client else 'Unknown'}"
        
        # Сохранение refresh token в БД (согласно rules.md)
        await auth_service.save_refresh_token(user["id"], refresh_token, device_info=device_info)
        
        # Коммит транзакции произойдет автоматически в get_db() после успешного выполнения
        # Если здесь произойдет ошибка, get_db() сделает rollback
        
        # secure=True только в production (HTTPS)
        from core.config import settings
        secure_cookie = settings.ENVIRONMENT == "production"
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite="lax",  # lax для работы через прокси
            max_age=30 * 24 * 60 * 60
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    except ValueError as e:
        # Ошибки валидации (дубликаты, неверный формат и т.д.)
        # get_db() автоматически сделает rollback
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError as e:
        # Дополнительная обработка IntegrityError на уровне роутера
        # (хотя основная обработка уже в сервисе)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"IntegrityError при регистрации: {e}", exc_info=True)
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "phone" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким номером телефона уже существует"
            )
        elif "email" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка создания пользователя. Возможно, пользователь с такими данными уже существует."
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка регистрации: {type(e).__name__}: {e}", exc_info=True)
        # get_db() автоматически сделает rollback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе
    Используется для безопасного определения роли без декодирования JWT на клиенте
    """
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "role": current_user.get("role")
    }


@router.post("/logout")
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Выход из системы"""
    auth_service = AuthService(db)
    # Отзыв refresh token (согласно rules.md)
    await auth_service.revoke_refresh_token()
    
    # Удаление cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Выход выполнен успешно"}


@router.post("/child-pin", response_model=LoginResponse)
@limiter.limit("5/minute")
async def child_pin_login(
    request: Request,
    pin_request: ChildPinRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход ребёнка по PIN-коду
    Rate limit: 5 попыток в минуту
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    from core.security.password import verify_password
    from datetime import datetime, timedelta
    
    access_repo = ChildAccessRepository(db)
    child_repo = ChildRepository(db)
    
    # Получаем доступ ребёнка
    access = await access_repo.get_by_child_id(pin_request.child_id)
    if not access or not access.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доступ для ребёнка не найден"
        )
    
    # Проверка блокировки
    if access.locked_until and datetime.now() < access.locked_until:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Доступ заблокирован до {access.locked_until.strftime('%H:%M:%S')}"
        )
    
    # Проверка, что PIN установлен
    if not access.pin_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN не установлен. Пожалуйста, сначала войдите по QR-коду и установите PIN."
        )
    
    # Проверка PIN
    if not verify_password(pin_request.pin, access.pin_hash):
        # Увеличиваем счётчик неудачных попыток
        access.failed_attempts += 1
        
        # Блокировка после 5 неудачных попыток
        if access.failed_attempts >= 5:
            access.locked_until = datetime.now() + timedelta(minutes=15)
            await access_repo.update(access, {
                "failed_attempts": access.failed_attempts,
                "locked_until": access.locked_until
            })
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Слишком много неудачных попыток. Доступ заблокирован на 15 минут."
            )
        else:
            await access_repo.update(access, {"failed_attempts": access.failed_attempts})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Неверный PIN. Осталось попыток: {5 - access.failed_attempts}"
            )
    
    # Сброс счётчика при успешном входе
    await access_repo.update(access, {"failed_attempts": 0, "locked_until": None})
    
    # Получаем данные ребёнка
    child = await child_repo.get_by_id(pin_request.child_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # Создаём токен для ребёнка
    # Используем child_id в токене, но роль CHILD
    token_data = {
        "sub": str(child.user_id),  # ID пользователя-родителя
        "child_id": str(child.id),   # ID ребёнка
        "role": "child"
    }
    access_token = create_access_token(token_data)
    refresh_token = create_access_token(token_data)  # Упрощённо, можно улучшить
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": child.id,
            "email": f"child_{child.id}",
            "role": "child",
            "child_id": child.id,
            "name": child.name
        }
    )


@router.post("/child-qr", response_model=LoginResponse)
@limiter.limit("5/minute")
async def child_qr_login(
    request: Request,
    qr_request: ChildQrRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход ребёнка по QR-коду
    Rate limit: 5 попыток в минуту
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    
    access_repo = ChildAccessRepository(db)
    child_repo = ChildRepository(db)
    
    # Получаем доступ по QR-токену
    access = await access_repo.get_by_qr_token(qr_request.qr_token)
    if not access or not access.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR-код недействителен или истёк"
        )
    
    # Получаем данные ребёнка
    child = await child_repo.get_by_id(access.child_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # Проверяем, установлен ли PIN
    # Если PIN не установлен, возвращаем флаг, что требуется установка PIN
    pin_required = not access.pin_hash
    
    # Создаём токен для ребёнка
    token_data = {
        "sub": str(child.user_id),
        "child_id": str(child.id),
        "role": "child"
    }
    access_token = create_access_token(token_data)
    
    # Если PIN не установлен, возвращаем специальный ответ
    if pin_required:
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": child.id,
                "email": f"child_{child.id}",
                "role": "child",
                "child_id": child.id,
                "name": child.name,
                "pin_required": True  # Флаг, что требуется установка PIN
            }
        )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": child.id,
            "email": f"child_{child.id}",
            "role": "child",
            "child_id": child.id,
            "name": child.name
        }
    )


@router.post("/admin-login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def admin_login(
    request: Request,
    login_data: AdminLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход администратора по телефону
    Проверка по ADMIN_PHONE из переменных окружения или по role == "admin"
    """
    from core.utils.phone_validator import normalize_phone
    from core.config import settings
    
    # Нормализуем телефон
    normalized_phone = normalize_phone(login_data.phone)
    
    # Проверяем админский телефон (если задан в env)
    admin_phone_check = False
    if settings.ADMIN_PHONE:
        admin_phone_normalized = normalize_phone(settings.ADMIN_PHONE)
        admin_phone_check = normalized_phone == admin_phone_normalized
    
    # Аутентификация
    auth_service = AuthService(db)
    user = await auth_service.authenticate(
        phone=normalized_phone,
        password=login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный телефон или пароль"
        )
    
    # Проверяем права администратора: либо по телефону, либо по роли
    is_admin_by_phone = admin_phone_check
    is_admin_by_role = user.get("role") == "admin"
    
    if not (is_admin_by_phone or is_admin_by_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администраторам"
        )
    
    # Создание токенов
    access_token = auth_service.create_access_token(user["id"], user.get("role"))
    refresh_token = auth_service.create_refresh_token(user["id"], user.get("role"))
    
    # Получение информации об устройстве для логирования
    device_info = f"{request.headers.get('user-agent', 'Unknown')} | {request.client.host if request.client else 'Unknown'}"
    
    # Сохранение refresh token в БД
    await auth_service.save_refresh_token(user["id"], refresh_token, device_info=device_info)
    
    # Установка refresh token в HttpOnly cookie
    # secure=True только в production (HTTPS)
    from core.config import settings
    secure_cookie = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=30 * 24 * 60 * 60  # 30 дней
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

