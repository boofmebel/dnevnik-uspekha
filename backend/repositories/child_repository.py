"""
Репозиторий для работы с детьми
Согласно rules.md: доступ к базе данных в repositories
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.child import Child
from models.user import User


class ChildRepository:
    """Репозиторий для работы с детьми"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, child_id: int) -> Optional[Child]:
        """Получение ребёнка по ID"""
        result = await self.session.execute(
            select(Child).where(Child.id == child_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> List[Child]:
        """Получение всех детей пользователя"""
        result = await self.session.execute(
            select(Child).where(Child.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def create(self, child_data: dict) -> Child:
        """Создание нового ребёнка"""
        from models.child import Gender
        
        # Убеждаемся, что gender передается как строка (значение enum)
        child_data = child_data.copy()
        if 'gender' in child_data:
            gender_value = child_data['gender']
            # Если это Gender enum, берем его значение (строку)
            if isinstance(gender_value, Gender):
                child_data['gender'] = gender_value.value
            # Если это уже строка, проверяем валидность
            elif isinstance(gender_value, str):
                # Проверяем, что строка валидна
                try:
                    Gender(gender_value)  # Проверка валидности
                    child_data['gender'] = gender_value
                except ValueError:
                    # Если невалидно, используем NONE
                    child_data['gender'] = Gender.NONE.value
            # Если это что-то другое, пытаемся преобразовать
            else:
                if hasattr(gender_value, 'value'):
                    child_data['gender'] = gender_value.value
                else:
                    child_data['gender'] = Gender.NONE.value
        
        # Убеждаемся, что gender - это строка перед созданием объекта
        if 'gender' in child_data and not isinstance(child_data['gender'], str):
            child_data['gender'] = str(child_data['gender'])
        
        try:
            child = Child(**child_data)
            self.session.add(child)
            await self.session.flush()
            await self.session.refresh(child)
            return child
        except Exception as e:
            # Логируем ошибку для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при создании Child: {e}", exc_info=True)
            logger.error(f"Данные: {child_data}")
            logger.error(f"Тип gender: {type(child_data.get('gender'))}, значение: {child_data.get('gender')}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def update(self, child: Child, child_data: dict) -> Child:
        """Обновление ребёнка"""
        for key, value in child_data.items():
            setattr(child, key, value)
        await self.session.flush()
        await self.session.refresh(child)
        return child
    
    async def delete(self, child: Child) -> None:
        """Удаление ребёнка"""
        await self.session.delete(child)
        await self.session.flush()





