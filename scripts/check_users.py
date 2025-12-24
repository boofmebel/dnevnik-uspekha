#!/usr/bin/env python3
"""
Скрипт для проверки пользователей в базе данных
Использование: python3 scripts/check_users.py
"""
import sys
import asyncio
from pathlib import Path

# Добавляем путь к backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select
    from core.config import settings
    from models.user import User, UserRole
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что вы находитесь в корне проекта")
    sys.exit(1)


async def check_users():
    """Проверка пользователей в базе данных"""
    try:
        # Создаём engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False
        )
        
        # Создаём сессию
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            # Получаем всех пользователей
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("📋 Пользователей в базе данных нет")
                print("")
                print("✅ Вы можете создать аккаунт через регистрацию:")
                print("   1. Откройте: http://89.104.74.123:3000")
                print("   2. Зарегистрируйтесь с email и паролем")
                print("   3. Затем сделайте себя администратором (см. инструкцию)")
                return
            
            print(f"📋 Найдено пользователей: {len(users)}")
            print("")
            print("=" * 60)
            print("Список пользователей:")
            print("=" * 60)
            
            for user in users:
                role_icon = "🔐" if user.role == UserRole.ADMIN else "👤"
                print(f"{role_icon} ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Роль: {user.role.value}")
                print(f"   Создан: {user.created_at}")
                print("-" * 60)
            
            # Проверяем администраторов
            admins = [u for u in users if u.role == UserRole.ADMIN]
            if admins:
                print(f"\n✅ Найдено администраторов: {len(admins)}")
                for admin in admins:
                    print(f"   - {admin.email}")
            else:
                print("\n⚠️  Администраторов не найдено!")
                print("")
                print("Для создания администратора:")
                print("  1. Выберите email из списка выше")
                print("  2. Выполните SQL: UPDATE users SET role = 'admin' WHERE email = 'ваш_email';")
            
            await engine.dispose()
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("")
        print("Возможные причины:")
        print("  1. База данных не доступна")
        print("  2. Неправильный DATABASE_URL в .env")
        print("  3. Отсутствуют зависимости Python")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_users())





