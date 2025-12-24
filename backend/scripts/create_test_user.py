"""
Скрипт для создания тестового пользователя с известным паролем
Использование: python3 backend/scripts/create_test_user.py
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
from core.security.password import hash_password
from core.utils.phone_validator import normalize_phone


async def create_test_user():
    """Создание тестового пользователя"""
    phone = "+79991234567"
    password = "test123"
    name = "Тестовый Пользователь"
    
    normalized_phone = normalize_phone(phone)
    print(f"🔍 Проверка пользователя с номером: {normalized_phone}")
    
    async with AsyncSessionLocal() as session:
        try:
            user_repo = UserRepository(session)
            
            # Проверяем, существует ли пользователь
            existing_user = await user_repo.get_by_phone(normalized_phone)
            
            if existing_user:
                print(f"✅ Пользователь уже существует:")
                print(f"   ID: {existing_user.id}")
                print(f"   Имя: {existing_user.name}")
                print(f"   Телефон: {existing_user.phone}")
                print(f"   Роль: {existing_user.role}")
                print(f"\n📋 Данные для входа:")
                print(f"   Телефон: {existing_user.phone}")
                print(f"   Пароль: {password}")
                return existing_user
            
            # Создаем нового пользователя
            print("🔨 Создаю тестового пользователя...")
            password_hash = hash_password(password)
            
            user_data = {
                "phone": normalized_phone,
                "password_hash": password_hash,
                "name": name,
                "role": "parent"
            }
            
            user = await user_repo.create(user_data)
            await session.commit()
            
            print(f"✅ Тестовый пользователь создан:")
            print(f"   ID: {user.id}")
            print(f"   Имя: {user.name}")
            print(f"   Телефон: {user.phone}")
            print(f"   Роль: {user.role}")
            
            print(f"\n📋 Данные для входа:")
            print(f"   Телефон: {user.phone}")
            print(f"   Пароль: {password}")
            
            return user
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании пользователя: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """Главная функция"""
    await create_test_user()


if __name__ == "__main__":
    asyncio.run(main())

