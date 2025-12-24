"""
Роутер для аутентификации
Согласно rules.md: JWT, refresh token rotation, rate limiting
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest,
    RegisterRequest, ChildPinRequest, ChildQrRequest, ChildAccessResponse,
    AdminLoginRequest, StaffLoginRequest
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
    request: Request,
    login_data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Универсальный endpoint для входа в систему
    Поддерживает как Product Users (parent, child), так и Staff Users (admin, support, moderator)
    Роль определяется автоматически по таблице, в которой найден пользователь
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Сначала пробуем найти в таблице product users
        auth_service = AuthService(db)
        user = await auth_service.authenticate(
            email=login_data.email,
            phone=login_data.phone,
            password=login_data.password
        )
    except Exception as e:
        logger.error(f"Error in product user authentication: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка аутентификации: {str(e)}")
    
    # Если не найден в product users, пробуем в staff users
    if not user and login_data.phone:
        try:
            from services.staff_auth_service import StaffAuthService
            staff_auth_service = StaffAuthService(db)
            user = await staff_auth_service.authenticate(
                phone=login_data.phone,
                password=login_data.password
            )
        except Exception as e:
            logger.error(f"Error in staff user authentication: {type(e).__name__}: {e}", exc_info=True)
            # Не поднимаем исключение, просто продолжаем - user останется None
        if user:
            # Для staff используем StaffAuthService для создания токенов
            access_token = staff_auth_service.create_access_token(user["id"], user.get("role"))
            refresh_token = staff_auth_service.create_refresh_token(user["id"], user.get("role"))
            
            # Получение информации об устройстве для логирования
            device_info = f"{request.headers.get('user-agent', 'Unknown')} | {request.client.host if request.client else 'Unknown'}"
            
            # Сохранение refresh token в БД
            await staff_auth_service.save_refresh_token(user["id"], refresh_token, device_info=device_info)
            
            # Установка refresh token в HttpOnly cookie
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
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email/телефон или пароль")
    
    # Для product users используем AuthService
    try:
        access_token = auth_service.create_access_token(user["id"], user.get("role"))
        refresh_token = auth_service.create_refresh_token(user["id"], user.get("role"))
        
        # Получение информации об устройстве для логирования
        device_info = f"{request.headers.get('user-agent', 'Unknown')} | {request.client.host if request.client else 'Unknown'}"
        
        # Сохранение refresh token в БД (согласно rules.md)
        await auth_service.save_refresh_token(user["id"], refresh_token, device_info=device_info)
        
        # Установка refresh token в HttpOnly cookie (согласно rules.md)
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
    except Exception as e:
        logger.error(f"Error creating tokens or saving refresh token: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка создания токенов: {str(e)}")


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
    request: Request,  # Для limiter должен быть первым
    register_data: RegisterRequest,
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
    
    ⚠️ Admin роль больше не поддерживается при регистрации.
    Staff пользователи создаются отдельно через админку.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Логируем входящие данные для отладки
    from core.utils.phone_validator import normalize_phone, validate_phone
    normalized_incoming = normalize_phone(register_data.phone)
    is_valid = validate_phone(normalized_incoming)
    logger.info(f"Регистрация: phone={register_data.phone}, normalized={normalized_incoming}, valid={is_valid}, name={register_data.name}, role={register_data.role}")
    
    # Проверка: admin роль больше не поддерживается
    if register_data.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Роль 'admin' больше не поддерживается при регистрации. Используйте /api/auth/staff-login для staff пользователей."
        )
    
    auth_service = AuthService(db)
    try:
        # Регистрация пользователя (создает запись в БД через flush)
        user = await auth_service.register(
            phone=register_data.phone,
            password=register_data.password,
            name=register_data.name,
            role=register_data.role,
            email=None  # Email больше не используется при регистрации
        )
        
        # Автоматический вход после регистрации
        access_token = auth_service.create_access_token(user["id"], user.get("role"))
        refresh_token = auth_service.create_refresh_token(user["id"], user.get("role"))
        
        # Получение информации об устройстве для логирования
        device_info = f"{request.headers.get('user-agent', 'Unknown')} | {request.client.host if request.client else 'Unknown'}"
        
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
        logger.error(f"ValueError при регистрации: {e}")
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
        logger.error(f"Ошибка регистрации: {type(e).__name__}: {e}", exc_info=True)
        # get_db() автоматически сделает rollback
        # Возвращаем более информативное сообщение об ошибке
        error_detail = str(e)
        if "phone" in error_detail.lower():
            error_detail = "Ошибка с номером телефона. Проверьте формат: +7XXXXXXXXXX"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {error_detail}"
        )


@router.get("/me")
async def get_current_user_info(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о текущем пользователе (product или staff)
    Используется для безопасного определения роли без декодирования JWT на клиенте
    
    Возвращает только минимальные данные: id и role
    Автоматически определяет тип пользователя (product или staff) по токену
    """
    from fastapi.security import HTTPBearer
    from core.security.jwt import verify_token
    
    # Получаем токен
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен"
        )
    
    # Декодируем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший токен"
        )
    
    user_id = int(payload.get("sub"))
    role = payload.get("role", "")
    
    # Проверяем, является ли это staff пользователем (по роли или по наличию в staff_users)
    is_staff_role = role in ["admin", "support", "moderator"]
    
    if is_staff_role:
        # Пробуем найти в staff_users
        try:
            from repositories.staff_user_repository import StaffUserRepository
            staff_repo = StaffUserRepository(db)
            staff_user = await staff_repo.get_by_id(user_id)
            if staff_user:
                return {
                    "id": staff_user.id,
                    "role": staff_user.role if isinstance(staff_user.role, str) else str(staff_user.role),
                    "is_staff": True
                }
        except Exception:
            # Если не найден в staff_users, но роль staff - возвращаем из токена
            pass
    
    # Пробуем найти в product users
    try:
        from repositories.user_repository import UserRepository
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if user:
            role_str = user.role
            if hasattr(role_str, 'value'):
                role_str = role_str.value
            elif not isinstance(role_str, str):
                role_str = str(role_str)
            return {
                "id": user.id,
                "role": role_str
            }
    except Exception:
        pass
    
    # Если не найден ни в одной таблице, возвращаем данные из токена
    return {
        "id": user_id,
        "role": role
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
    
    # Получаем доступ по QR-токену (с проверкой всех ограничений)
    access = await access_repo.get_by_qr_token(qr_request.qr_token)
    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR-код недействителен, истёк или уже использован"
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
    
    # ОДНОРАЗОВОЕ ИСПОЛЬЗОВАНИЕ: Помечаем токен как использованный
    from datetime import datetime
    await access_repo.update(access, {
        "qr_token_used_at": datetime.now()
    })
    await db.commit()  # Сохраняем изменения в БД
    
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


@router.post("/child-set-pin")
async def child_set_pin(
    request: Request,
    pin_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Установка PIN-кода для ребенка
    Вызывается после первого входа по QR-коду
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    from core.security.password import hash_password
    
    # Проверяем, что пользователь - ребенок
    if current_user.get("role") != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только дети могут устанавливать PIN"
        )
    
    child_id = current_user.get("child_id")
    if not child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID ребенка не найден"
        )
    
    pin = pin_data.get("pin")
    if not pin or len(pin) < 4 or len(pin) > 6 or not pin.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN должен содержать от 4 до 6 цифр"
        )
    
    access_repo = ChildAccessRepository(db)
    child_repo = ChildRepository(db)
    
    # Проверяем, что ребенок существует
    child = await child_repo.get_by_id(child_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # Получаем доступ
    access = await access_repo.get_by_child_id(child_id)
    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доступ для ребёнка не найден"
        )
    
    # Проверяем, что PIN еще не установлен
    if access.pin_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN уже установлен"
        )
    
    # Хешируем PIN
    pin_hash = hash_password(pin)
    
    # Обновляем доступ
    await access_repo.update(access, {
        "pin_hash": pin_hash
    })
    await db.commit()
    
    return {"message": "PIN-код успешно установлен"}


@router.post("/child-biometric-challenge")
async def child_biometric_challenge(
    request: Request,
    challenge_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение challenge для биометрической аутентификации ребенка
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    import secrets
    import base64
    
    child_id = challenge_data.get("child_id")
    if not child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID ребенка не указан"
        )
    
    child_repo = ChildRepository(db)
    child = await child_repo.get_by_id(child_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # Генерируем challenge
    challenge_bytes = secrets.token_bytes(32)
    challenge_b64 = base64.b64encode(challenge_bytes).decode('utf-8')
    
    # Сохраняем challenge в сессии (можно использовать Redis в продакшене)
    # Пока используем простой подход - возвращаем challenge
    # В продакшене нужно сохранять challenge с временем жизни
    
    return {
        "challenge": challenge_b64,
        "rpId": request.url.hostname,
        "allowCredentials": []  # Пока не используем сохраненные credentials
    }


@router.post("/child-biometric-verify", response_model=LoginResponse)
async def child_biometric_verify(
    request: Request,
    verify_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверка биометрической аутентификации ребенка
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    import base64
    
    child_id = verify_data.get("child_id")
    credential = verify_data.get("credential")
    
    if not child_id or not credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно данных для проверки"
        )
    
    child_repo = ChildRepository(db)
    child = await child_repo.get_by_id(child_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # В реальном приложении здесь должна быть проверка credential
    # с использованием библиотеки для WebAuthn (например, py_webauthn)
    # Пока упрощенная версия - проверяем только наличие credential
    
    if not credential.get("id") or not credential.get("response"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат credential"
        )
    
    # TODO: Реализовать полную проверку WebAuthn credential
    # Для продакшена нужно:
    # 1. Проверить challenge
    # 2. Проверить signature
    # 3. Проверить authenticatorData
    # 4. Проверить clientDataJSON
    
    # Пока упрощенная версия - считаем, что биометрия прошла успешно
    # В продакшене нужно использовать библиотеку py_webauthn или аналогичную
    
    # Создаём токен для ребёнка
    token_data = {
        "sub": str(child.user_id),
        "child_id": str(child.id),
        "role": "child"
    }
    access_token = create_access_token(token_data)
    
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
    
    ⚠️ DEPRECATED: Используйте /api/auth/staff-login для staff пользователей
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


@router.post("/staff-login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def staff_login(
    request: Request,
    login_data: StaffLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход staff пользователя (admin, support, moderator) по телефону
    Отдельная система аутентификации для операторов и поддержки
    """
    from services.staff_auth_service import StaffAuthService
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Staff login attempt for phone: {login_data.phone}")
    
    # Аутентификация staff пользователя
    staff_auth_service = StaffAuthService(db)
    staff_user = await staff_auth_service.authenticate(
        phone=login_data.phone,
        password=login_data.password
    )
    
    if not staff_user:
        logger.warning(f"Failed staff login attempt for phone: {login_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль"
        )
    
    logger.info(f"Successful staff login: id={staff_user['id']}, phone={staff_user['phone']}, role={staff_user['role']}")
    
    # Создание токенов
    access_token = staff_auth_service.create_access_token(staff_user["id"], staff_user.get("role"))
    refresh_token = staff_auth_service.create_refresh_token(staff_user["id"], staff_user.get("role"))
    
    # Получение информации об устройстве для логирования
    device_info = f"{request.headers.get('user-agent', 'Unknown')} | {request.client.host if request.client else 'Unknown'}"
    
    # Сохранение refresh token в БД
    await staff_auth_service.save_refresh_token(staff_user["id"], refresh_token, device_info=device_info)
    
    # Установка refresh token в HttpOnly cookie
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
        user=staff_user
    )

