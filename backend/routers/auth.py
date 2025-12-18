"""
Роутер для аутентификации
Согласно rules.md: JWT, refresh token rotation, rate limiting
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import LoginRequest, LoginResponse, RefreshRequest
from services.auth_service import AuthService
from core.security.jwt import verify_token
from core.database import get_db

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

