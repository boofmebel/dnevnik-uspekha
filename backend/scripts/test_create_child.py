"""
Тестовый скрипт для проверки создания ребенка
"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from repositories.child_repository import ChildRepository
from repositories.user_repository import UserRepository
from models.child import Gender, Child
from core.utils.phone_validator import normalize_phone

async def test_create_child():
    """Тест создания ребенка"""
    print("🧪 Тестирование создания ребенка...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Находим тестового пользователя
            user_repo = UserRepository(session)
            test_phone = "+79991234567"
            user = await user_repo.get_by_phone(normalize_phone(test_phone))
            
            if not user:
                print(f"❌ Пользователь с номером {test_phone} не найден")
                return False
            
            print(f"✅ Найден пользователь: {user.name} (ID: {user.id})")
            
            # Создаем ребенка
            child_repo = ChildRepository(session)
            child_data = {
                "name": "Тестовый Ребенок",
                "gender": Gender.GIRL.value,  # Используем значение enum
                "user_id": user.id
            }
            
            print(f"📤 Создание ребенка с данными: {child_data}")
            child = await child_repo.create(child_data)
            
            await session.flush()
            await session.refresh(child)
            
            print(f"✅ Ребенок создан успешно:")
            print(f"   ID: {child.id}")
            print(f"   Имя: {child.name}")
            print(f"   Пол: {child.gender}")
            print(f"   User ID: {child.user_id}")
            
            await session.commit()
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании ребенка: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_create_child())
    sys.exit(0 if success else 1)

