"""
Роутер для работы с задачами
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.task import TaskCreate, TaskUpdate, TaskListResponse, TaskResponse
from services.task_service import TaskService
from core.database import get_db
from core.dependencies import get_current_child, check_parent_consent

router = APIRouter()


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child)
):
    """Получение всех задач ребёнка"""
    service = TaskService(db)
    tasks = await service.get_tasks(current_child.id)
    
    return TaskListResponse(
        checklist=[TaskResponse.model_validate(t) for t in tasks["checklist"]],
        kanban={
            "todo": [TaskResponse.model_validate(t) for t in tasks["kanban"]["todo"]],
            "doing": [TaskResponse.model_validate(t) for t in tasks["kanban"]["doing"]],
            "done": [TaskResponse.model_validate(t) for t in tasks["kanban"]["done"]]
        }
    )


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Создание задачи"""
    service = TaskService(db)
    task = await service.create_task(current_child.id, task_data)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Обновление задачи"""
    service = TaskService(db)
    task = await service.update_task(task_id, current_child.id, task_data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_child: dict = Depends(get_current_child),
    _: bool = Depends(check_parent_consent)
):
    """Удаление задачи"""
    service = TaskService(db)
    await service.delete_task(task_id, current_child.id)
    return {"message": "Задача удалена"}
