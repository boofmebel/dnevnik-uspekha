"""
Сервис для работы с задачами
Согласно rules.md: бизнес-логика в services
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.task_repository import TaskRepository
from repositories.child_repository import ChildRepository
from schemas.task import TaskCreate, TaskUpdate
from models.task import Task, TaskType
from core.exceptions import NotFoundError, ForbiddenError


class TaskService:
    """Сервис для работы с задачами"""
    
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.child_repo = ChildRepository(session)
        self.session = session
    
    async def get_tasks(self, child_id: int) -> dict:
        """Получение всех задач ребёнка"""
        checklist = await self.task_repo.get_by_child_id(child_id, TaskType.CHECKLIST)
        kanban_todo = await self.task_repo.get_by_child_id(child_id, TaskType.KANBAN)
        
        # Разделяем канбан по статусам
        kanban = {
            "todo": [t for t in kanban_todo if t.status == "todo"],
            "doing": [t for t in kanban_todo if t.status == "doing"],
            "done": [t for t in kanban_todo if t.status == "done"]
        }
        
        return {
            "checklist": checklist,
            "kanban": kanban
        }
    
    async def create_task(self, child_id: int, task_data: TaskCreate) -> Task:
        """Создание задачи"""
        # Проверка существования ребёнка
        child = await self.child_repo.get_by_id(child_id)
        if not child:
            raise NotFoundError("Ребёнок не найден")
        
        task_dict = task_data.model_dump()
        task_dict["child_id"] = child_id
        return await self.task_repo.create(task_dict)
    
    async def update_task(self, task_id: int, child_id: int, task_data: TaskUpdate) -> Task:
        """Обновление задачи"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Задача не найдена")
        
        if task.child_id != child_id:
            raise ForbiddenError("Нет доступа к этой задаче")
        
        update_dict = task_data.model_dump(exclude_unset=True)
        return await self.task_repo.update(task, update_dict)
    
    async def delete_task(self, task_id: int, child_id: int) -> None:
        """Удаление задачи"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Задача не найдена")
        
        if task.child_id != child_id:
            raise ForbiddenError("Нет доступа к этой задаче")
        
        await self.task_repo.delete(task)

