"""
Скрипт для получения списка всех пользователей
Использование: python3 backend/scripts/list_users.py
"""
import asyncio
import sys
from pathlib import Path

# Добавляем директорию backend в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from repositories.user_repository import UserRepository


async def list_users():
    """Получение списка всех пользователей"""
    async with AsyncSessionLocal() as session:
        try:
            user_repo = UserRepository(session)
            
            # Получаем всех пользователей
            from sqlalchemy import select
            from models.user import User
            
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("❌ Пользователи не найдены в базе данных")
                return
            
            print(f"✅ Найдено пользователей: {len(users)}\n")
            print("=" * 60)
            
            for user in users:
                print(f"ID: {user.id}")
                print(f"Имя: {user.name}")
                print(f"Телефон: {user.phone}")
                print(f"Email: {user.email or 'не указан'}")
                print(f"Роль: {user.role}")
                print("-" * 60)
            
            print("\n💡 Для входа используйте:")
            if users:
                first_user = users[0]
                print(f"   Телефон: {first_user.phone}")
                print(f"   Пароль: (пароль, который вы устанавливали при регистрации)")
                print(f"\n   Или зарегистрируйте нового пользователя через форму регистрации")
            
        except Exception as e:
            print(f"❌ Ошибка при получении пользователей: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Главная функция"""
    await list_users()


if __name__ == "__main__":
    asyncio.run(main())

