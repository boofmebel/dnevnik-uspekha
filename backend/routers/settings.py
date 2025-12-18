"""
Роутер для работы с настройками
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.settings import SettingsResponse, SettingsUpdate
from repositories.settings_repository import SettingsRepository
from repositories.child_repository import ChildRepository
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent
from core.exceptions import NotFoundError

router = APIRouter()


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение настроек ребёнка"""
    repo = SettingsRepository(db)
    settings = await repo.get_or_create(current_child.id)
    return SettingsResponse.model_validate(settings)


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обновление настроек"""
    repo = SettingsRepository(db)
    settings = await repo.get_or_create(current_child.id)
    settings = await repo.update(settings, settings_data.model_dump(exclude_unset=True))
    return SettingsResponse.model_validate(settings)

