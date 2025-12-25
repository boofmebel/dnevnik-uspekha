"""
Репозиторий для работы с задачами
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.task import Task, TaskType, TaskStatus


class TaskRepository:
    """Репозиторий для работы с задачами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Получение задачи по ID"""
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_child_id(self, child_id: int, task_type: Optional[TaskType] = None) -> List[Task]:
        """Получение задач ребёнка"""
        query = select(Task).where(Task.child_id == child_id)
        if task_type:
            query = query.where(Task.task_type == task_type)
        query = query.order_by(Task.position, Task.id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, task_data: dict) -> Task:
        """Создание новой задачи"""
        task = Task(**task_data)
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task
    
    async def update(self, task: Task, task_data: dict) -> Task:
        """Обновление задачи"""
        for key, value in task_data.items():
            setattr(task, key, value)
        await self.session.flush()
        await self.session.refresh(task)
        return task
    
    async def delete(self, task: Task) -> None:
        """Удаление задачи"""
        await self.session.delete(task)
        await self.session.flush()






