"""
Роутер для работы со звёздами
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.star import StarResponse, StarAddRequest, StarExchangeRequest, StarHistoryResponse, StarStreakResponse
from services.star_service import StarService
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent

router = APIRouter()


@router.get("/", response_model=StarResponse)
async def get_stars(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение звёзд ребёнка"""
    service = StarService(db)
    star = await service.get_stars(current_child.id)
    
    # Получаем историю и streak
    from repositories.star_repository import StarRepository
    star_repo = StarRepository(db)
    history = await star_repo.get_history(star.id)
    streak = await star_repo.get_or_create_streak(star.id)
    
    return StarResponse(
        today=star.today,
        total=star.total,
        history=[StarHistoryResponse.model_validate(h) for h in history],
        streak=StarStreakResponse.model_validate(streak) if streak else None
    )


@router.post("/add")
async def add_stars(
    request: StarAddRequest,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Добавление звёзд"""
    service = StarService(db)
    result = await service.add_stars(current_child.id, request)
    star = result["star"]
    rewards = result.get("rewards", [])
    
    from repositories.star_repository import StarRepository
    star_repo = StarRepository(db)
    history = await star_repo.get_history(star.id)
    streak = await star_repo.get_or_create_streak(star.id)
    
    return {
        "star": StarResponse(
            today=star.today,
            total=star.total,
            history=[StarHistoryResponse.model_validate(h) for h in history],
            streak=StarStreakResponse.model_validate(streak) if streak else None
        ),
        "rewards": rewards
    }


@router.post("/exchange")
async def exchange_stars(
    request: StarExchangeRequest,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обмен звёзд на виртуальную валюту (для конвертации в подарки)"""
    service = StarService(db)
    result = await service.exchange_stars(current_child.id, request)
    return result


@router.post("/check-streak")
async def check_streak(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Проверка серии дней"""
    service = StarService(db)
    result = await service.check_streak(current_child.id)
    return result
