"""
Роутер для работы с пользователями
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """Получение текущего пользователя"""
    # В реальной реализации:
    # user = await user_service.get_current_user(current_user)
    return {"message": "Get current user"}

