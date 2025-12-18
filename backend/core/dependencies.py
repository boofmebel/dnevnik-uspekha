"""
Dependencies для FastAPI
Согласно rules.md: получение текущего пользователя, проверка прав
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security.jwt import verify_token
from repositories.user_repository import UserRepository
from repositories.child_repository import ChildRepository
from repositories.subscription_repository import ParentConsentRepository
from core.exceptions import ForbiddenError

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Получение текущего пользователя из JWT токена"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )
    
    user_id = int(payload.get("sub"))
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


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

