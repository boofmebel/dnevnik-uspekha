"""
Роутер для работы со статистикой недели
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.weekly_stats import WeeklyStatsResponse, WeeklyStatResponse
from models.weekly_stats import WeeklyStat
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/", response_model=WeeklyStatsResponse)
async def get_weekly_stats(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение статистики недели"""
    # Получаем статистику за последние 14 дней
    result = await db.execute(
        select(WeeklyStat)
        .where(WeeklyStat.child_id == current_child.id)
        .order_by(WeeklyStat.date.desc())
        .limit(14)
    )
    all_stats = list(result.scalars().all())
    
    # Разделяем на текущую неделю и прошлую
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)
    
    days = [s for s in all_stats if s.date >= week_start.strftime("%Y-%m-%d")]
    last_week = [s for s in all_stats if last_week_start.strftime("%Y-%m-%d") <= s.date < week_start.strftime("%Y-%m-%d")]
    
    return WeeklyStatsResponse(
        days=[WeeklyStatResponse.model_validate(s) for s in days],
        last_week=[WeeklyStatResponse.model_validate(s) for s in last_week]
    )


@router.post("/update")
async def update_daily_stat(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обновление статистики за сегодня"""
    from repositories.star_repository import StarRepository
    from repositories.task_repository import TaskRepository
    from models.task import TaskType
    
    today = datetime.now().date().strftime("%Y-%m-%d")
    
    # Получаем или создаём статистику за сегодня
    result = await db.execute(
        select(WeeklyStat)
        .where(WeeklyStat.child_id == current_child.id)
        .where(WeeklyStat.date == today)
    )
    stat = result.scalar_one_or_none()
    
    if not stat:
        stat = WeeklyStat(child_id=current_child.id, date=today)
        db.add(stat)
    
    # Получаем звёзды за сегодня
    star_repo = StarRepository(db)
    star = await star_repo.get_by_child_id(current_child.id)
    if star:
        stat.stars = star.today
    
    # Получаем количество выполненных задач
    task_repo = TaskRepository(db)
    tasks = await task_repo.get_by_child_id(current_child.id, TaskType.CHECKLIST)
    stat.tasks_completed = sum(1 for t in tasks if t.completed)
    
    await db.flush()
    await db.refresh(stat)
    
    return WeeklyStatResponse.model_validate(stat)

