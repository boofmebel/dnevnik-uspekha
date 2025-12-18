#!/usr/bin/env python3
"""
Прямое создание администратора
Использование: python3 scripts/create_admin_direct.py email password
"""
import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Добавляем путь к backend
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Загружаем .env файл
env_file = backend_path / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Загружен .env файл: {env_file}")
else:
    print(f"⚠️  .env файл не найден: {env_file}")

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select, text
    from core.config import settings
    from core.security.password import hash_password
    from models.user import User, UserRole
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Попробуйте установить зависимости: pip install sqlalchemy asyncpg passlib[bcrypt]")
    sys.exit(1)


async def create_admin_direct(email: str, password: str):
    """Прямое создание администратора"""
    try:
        print(f"🔐 Создание администратора: {email}")
        print(f"📝 Пароль: {password}")
        print("")
        
        # Получаем DATABASE_URL
        db_url = settings.DATABASE_URL
        print(f"🔗 Подключение к базе данных...")
        print(f"   URL: {db_url[:50]}...")
        print("")
        
        # Создаём engine
        engine = create_async_engine(
            db_url,
            echo=False
        )
        
        # Создаём сессию
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            # Проверяем, существует ли пользователь
            print("🔍 Проверка существующего пользователя...")
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✅ Пользователь найден: ID={user.id}, роль={user.role.value}")
                # Обновляем
                user.role = UserRole.ADMIN
                user.password_hash = hash_password(password)
                print(f"✅ Обновлён: роль=admin, пароль обновлён")
            else:
                print("📝 Создание нового пользователя...")
                # Создаём нового
                user = User(
                    email=email,
                    password_hash=hash_password(password),
                    role=UserRole.ADMIN
                )
                session.add(user)
                print(f"✅ Создан новый администратор")
            
            await session.commit()
            await session.refresh(user)
            
            print("")
            print("=" * 60)
            print("✅ ГОТОВО!")
            print("=" * 60)
            print(f"Email: {user.email}")
            print(f"Роль: {user.role.value}")
            print(f"ID: {user.id}")
            print("")
            print("🔑 Данные для входа:")
            print(f"   Email: {email}")
            print(f"   Пароль: {password}")
            print("")
            print("🚀 Следующие шаги:")
            print("   1. Откройте: http://89.104.74.123:3000")
            print("   2. Войдите с email и паролем выше")
            print("   3. Откройте админку: http://89.104.74.123:3000/admin.html")
            print("")
            
            await engine.dispose()
            return True
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "79059510009@mail.ru"
    password = sys.argv[2] if len(sys.argv) > 2 else "Admin123!"
    
    success = asyncio.run(create_admin_direct(email, password))
    sys.exit(0 if success else 1)

