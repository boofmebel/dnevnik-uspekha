"""
Роутер для работы с копилкой
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.piggy import PiggyResponse, PiggyGoalUpdate, PiggyAddRequest, PiggyGoalResponse, PiggyHistoryResponse
from services.piggy_service import PiggyService
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent

router = APIRouter()


@router.get("/", response_model=PiggyResponse)
async def get_piggy(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение копилки ребёнка"""
    service = PiggyService(db)
    piggy = await service.get_piggy(current_child.id)
    
    from repositories.piggy_repository import PiggyRepository
    piggy_repo = PiggyRepository(db)
    goal = await piggy_repo.get_goal(piggy.id)
    history = await piggy_repo.get_history(piggy.id)
    
    return PiggyResponse(
        amount=piggy.amount,
        goal=PiggyGoalResponse.model_validate(goal) if goal else None,
        history=[PiggyHistoryResponse.model_validate(h) for h in history]
    )


@router.put("/goal", response_model=PiggyResponse)
async def update_goal(
    goal_data: PiggyGoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обновление цели копилки"""
    service = PiggyService(db)
    piggy = await service.update_goal(current_child.id, goal_data)
    
    from repositories.piggy_repository import PiggyRepository
    piggy_repo = PiggyRepository(db)
    goal = await piggy_repo.get_goal(piggy.id)
    history = await piggy_repo.get_history(piggy.id)
    
    return PiggyResponse(
        amount=piggy.amount,
        goal=PiggyGoalResponse.model_validate(goal) if goal else None,
        history=[PiggyHistoryResponse.model_validate(h) for h in history]
    )


@router.post("/add", response_model=PiggyResponse)
async def add_virtual_currency(
    request: PiggyAddRequest,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Добавление виртуальной валюты в копилку (для конвертации в подарки)"""
    service = PiggyService(db)
    piggy = await service.add_virtual_currency(current_child.id, request)
    
    from repositories.piggy_repository import PiggyRepository
    piggy_repo = PiggyRepository(db)
    goal = await piggy_repo.get_goal(piggy.id)
    history = await piggy_repo.get_history(piggy.id)
    
    return PiggyResponse(
        amount=piggy.amount,
        goal=PiggyGoalResponse.model_validate(goal) if goal else None,
        history=[PiggyHistoryResponse.model_validate(h) for h in history]
    )
