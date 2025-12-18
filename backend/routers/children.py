"""
Роутер для работы с детьми
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.child import ChildCreate, ChildUpdate, ChildResponse
from repositories.child_repository import ChildRepository
from core.database import get_db
from core.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=list[ChildResponse])
async def get_children(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение списка детей пользователя"""
    repo = ChildRepository(db)
    children = await repo.get_by_user_id(current_user["id"])
    return [ChildResponse.model_validate(c) for c in children]


@router.post("/", response_model=ChildResponse)
async def create_child(
    child_data: ChildCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание ребёнка"""
    repo = ChildRepository(db)
    child = await repo.create({
        **child_data.model_dump(),
        "user_id": current_user["id"]
    })
    return ChildResponse.model_validate(child)


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: int,
    child_data: ChildUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновление ребёнка"""
    repo = ChildRepository(db)
    child = await repo.get_by_id(child_id)
    
    if not child or child.user_id != current_user["id"]:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    child = await repo.update(child, child_data.model_dump(exclude_unset=True))
    return ChildResponse.model_validate(child)
