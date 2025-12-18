"""
Роутер для работы со списком желаний
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.wishlist import WishlistItemCreate, WishlistItemUpdate, WishlistItemResponse
from models.wishlist import WishlistItem
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent
from core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()


@router.get("/", response_model=list[WishlistItemResponse])
async def get_wishlist(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение списка желаний"""
    result = await db.execute(
        select(WishlistItem)
        .where(WishlistItem.child_id == current_child.id)
        .order_by(WishlistItem.position, WishlistItem.id)
    )
    items = list(result.scalars().all())
    return [WishlistItemResponse.model_validate(i) for i in items]


@router.post("/", response_model=WishlistItemResponse)
async def create_wishlist_item(
    item_data: WishlistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Создание элемента списка желаний"""
    item = WishlistItem(
        child_id=current_child.id,
        **item_data.model_dump()
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return WishlistItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=WishlistItemResponse)
async def update_wishlist_item(
    item_id: int,
    item_data: WishlistItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обновление элемента списка желаний"""
    result = await db.execute(
        select(WishlistItem).where(WishlistItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise NotFoundError("Элемент не найден")
    
    if item.child_id != current_child.id:
        raise ForbiddenError("Нет доступа к этому элементу")
    
    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    await db.flush()
    await db.refresh(item)
    return WishlistItemResponse.model_validate(item)


@router.delete("/{item_id}")
async def delete_wishlist_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Удаление элемента из списка желаний"""
    result = await db.execute(
        select(WishlistItem).where(WishlistItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise NotFoundError("Элемент не найден")
    
    if item.child_id != current_child.id:
        raise ForbiddenError("Нет доступа к этому элементу")
    
    await db.delete(item)
    await db.flush()
    return {"message": "Элемент удалён"}

