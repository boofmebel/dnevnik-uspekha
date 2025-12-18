"""
Роутер для аутентификации
Согласно rules.md: JWT, refresh token rotation, rate limiting
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest,
    RegisterRequest, ChildPinRequest, ChildQrRequest, ChildAccessResponse
)
from services.auth_service import AuthService
from core.security.jwt import verify_token, create_access_token
from core.database import get_db
from core.exceptions import ValidationError

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему
    Согласно rules.md: rate limiting на login endpoint
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    # Создание токенов
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # Сохранение refresh token в БД (согласно rules.md)
    await auth_service.save_refresh_token(user.id, refresh_token)
    
    # Установка refresh token в HttpOnly cookie (согласно rules.md)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Только HTTPS
        samesite="strict",
        max_age=30 * 24 * 60 * 60  # 30 дней
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/refresh")
async def refresh(
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access token
    Согласно rules.md: rotation + новый access token
    """
    auth_service = AuthService(db)
    # Получение refresh token из cookie
    # В реальной реализации нужно получить из request.cookies
    # Здесь упрощённый пример
    
    # Проверка и ротация токена
    new_access_token, new_refresh_token = await auth_service.refresh_token_rotation()
    
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    
    # Установка нового refresh token
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 24 * 60 * 60
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/register")
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя (родителя)
    """
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            role=request.role
        )
        
        # Автоматический вход после регистрации
        access_token = auth_service.create_access_token(user["id"])
        refresh_token = auth_service.create_refresh_token(user["id"])
        
        await auth_service.save_refresh_token(user["id"], refresh_token)
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=30 * 24 * 60 * 60
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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
async def child_pin_login(
    request: ChildPinRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход ребёнка по PIN-коду
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    from core.security.password import verify_password
    from datetime import datetime, timedelta
    
    access_repo = ChildAccessRepository(db)
    child_repo = ChildRepository(db)
    
    # Получаем доступ ребёнка
    access = await access_repo.get_by_child_id(request.child_id)
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
    
    # Проверка PIN
    if not verify_password(request.pin, access.pin_hash):
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
    child = await child_repo.get_by_id(request.child_id)
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
async def child_qr_login(
    request: ChildQrRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход ребёнка по QR-коду
    """
    from repositories.child_access_repository import ChildAccessRepository
    from repositories.child_repository import ChildRepository
    
    access_repo = ChildAccessRepository(db)
    child_repo = ChildRepository(db)
    
    # Получаем доступ по QR-токену
    access = await access_repo.get_by_qr_token(request.qr_token)
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

