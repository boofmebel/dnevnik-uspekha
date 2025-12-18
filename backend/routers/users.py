"""
Роутер для работы с пользователями
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.admin import AdminUserResponse
from repositories.user_repository import UserRepository
from core.database import get_db
from core.dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=AdminUserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение текущего пользователя"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user["id"])
    
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Подсчитываем детей и подписки
    children_count = len(user.children) if hasattr(user, 'children') else 0
    subscriptions_count = len(user.subscriptions) if hasattr(user, 'subscriptions') else 0
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        parent_id=user.parent_id,
        children_count=children_count,
        subscriptions_count=subscriptions_count,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

