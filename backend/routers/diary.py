"""
Роутер для работы с дневником
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.diary import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse
from models.diary import DiaryEntry
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent
from core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()


@router.get("/", response_model=list[DiaryEntryResponse])
async def get_diary_entries(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение всех записей дневника"""
    result = await db.execute(
        select(DiaryEntry)
        .where(DiaryEntry.child_id == current_child.id)
        .order_by(DiaryEntry.created_at.desc())
    )
    entries = list(result.scalars().all())
    return [DiaryEntryResponse.model_validate(e) for e in entries]


@router.post("/", response_model=DiaryEntryResponse)
async def create_diary_entry(
    entry_data: DiaryEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Создание записи в дневнике"""
    entry = DiaryEntry(
        child_id=current_child.id,
        **entry_data.model_dump()
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return DiaryEntryResponse.model_validate(entry)


@router.put("/{entry_id}", response_model=DiaryEntryResponse)
async def update_diary_entry(
    entry_id: int,
    entry_data: DiaryEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обновление записи в дневнике"""
    result = await db.execute(
        select(DiaryEntry).where(DiaryEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise NotFoundError("Запись не найдена")
    
    if entry.child_id != current_child.id:
        raise ForbiddenError("Нет доступа к этой записи")
    
    update_data = entry_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)
    
    await db.flush()
    await db.refresh(entry)
    return DiaryEntryResponse.model_validate(entry)


@router.delete("/{entry_id}")
async def delete_diary_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Удаление записи из дневника"""
    result = await db.execute(
        select(DiaryEntry).where(DiaryEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise NotFoundError("Запись не найдена")
    
    if entry.child_id != current_child.id:
        raise ForbiddenError("Нет доступа к этой записи")
    
    await db.delete(entry)
    await db.flush()
    return {"message": "Запись удалена"}

