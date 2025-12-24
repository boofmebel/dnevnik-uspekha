#!/usr/bin/env python3
"""
Скрипт для создания администратора по номеру телефона
Использование: python3 scripts/create_admin_by_phone.py <телефон> <пароль> [имя]
"""
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

# Добавляем путь к backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Загружаем .env
backend_path = Path(__file__).parent.parent / "backend"
env_file = backend_path / ".env"
if env_file.exists():
    load_dotenv(env_file)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"✅ Загружен .env: {env_file}")
        print(f"📝 DATABASE_URL: {db_url[:50]}...")
    else:
        print("❌ DATABASE_URL не найден в .env файле")
        sys.exit(1)
else:
    print("❌ .env файл не найден")
    print(f"💡 Создайте файл: {env_file}")
    sys.exit(1)

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select, text
    import bcrypt
    from core.utils.phone_validator import normalize_phone, validate_phone
    from models.user import User
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install 'sqlalchemy[asyncio]' asyncpg bcrypt python-dotenv")
    sys.exit(1)


async def create_admin_by_phone(phone: str, password: str, name: str = "Администратор"):
    """Создание администратора по номеру телефона"""
    
    # Нормализуем телефон
    try:
        normalized_phone = normalize_phone(phone)
        if not validate_phone(normalized_phone):
            print(f"❌ Неверный формат номера телефона: {phone}")
            print("💡 Используйте формат: +7XXXXXXXXXX или 7XXXXXXXXXX")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка нормализации телефона: {e}")
        sys.exit(1)
    
    # Хешируем пароль (используем прямой bcrypt для избежания проблем с passlib)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    print(f"\n🔐 Создание администратора:")
    print(f"   Телефон: {normalized_phone}")
    print(f"   Имя: {name}")
    print(f"   Пароль: {'*' * len(password)}")
    print(f"   Хеш: {password_hash[:30]}...")
    print("")
    
    # Создаём engine
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Проверяем существующего пользователя
            result = await session.execute(
                select(User).where(User.phone == normalized_phone)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ Пользователь найден: ID={existing_user.id}, роль={existing_user.role}")
                # Обновляем существующего пользователя
                existing_user.role = "admin"
                existing_user.password_hash = password_hash
                existing_user.name = name
                print("✅ Обновлён: роль=admin, пароль обновлён")
            else:
                print("📝 Создание нового пользователя...")
                # Создаём нового администратора
                new_user = User(
                    phone=normalized_phone,
                    password_hash=password_hash,
                    role="admin",
                    name=name
                )
                session.add(new_user)
                print("✅ Создан новый администратор")
            
            await session.commit()
            
            # Проверяем результат
            result = await session.execute(
                select(User).where(User.phone == normalized_phone)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ Ошибка: пользователь не найден после создания")
                sys.exit(1)
            
            print("")
            print("=" * 60)
            print("✅ ГОТОВО!")
            print("=" * 60)
            print(f"ID: {user.id}")
            print(f"Телефон: {user.phone}")
            print(f"Имя: {user.name}")
            print(f"Роль: {user.role}")
            print("")
            print("🔑 Данные для входа в админку:")
            print(f"   Телефон: {normalized_phone}")
            print(f"   Пароль: {password}")
            print("")
            print("🚀 Следующие шаги:")
            print("   1. Убедитесь, что backend запущен")
            print("   2. Откройте: http://localhost:8000/admin")
            print("   3. Войдите с телефоном и паролем выше")
            print("")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании администратора: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()


async def list_admins():
    """Список всех администраторов"""
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == "admin")
        )
        admins = result.scalars().all()
        
        if not admins:
            print("❌ Администраторов в базе нет")
            return
        
        print("\n📋 Список администраторов:")
        print("-" * 60)
        for admin in admins:
            print(f"🔐 ID: {admin.id}")
            print(f"   Телефон: {admin.phone}")
            print(f"   Имя: {admin.name or 'Не указано'}")
            print(f"   Email: {admin.email or 'Не указан'}")
            print(f"   Создан: {admin.created_at}")
            print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 scripts/create_admin_by_phone.py <телефон> <пароль> [имя]")
        print("  python3 scripts/create_admin_by_phone.py --list")
        print("")
        print("Примеры:")
        print("  python3 scripts/create_admin_by_phone.py 79059510009 admin123")
        print("  python3 scripts/create_admin_by_phone.py +79059510009 admin123 'Иван Иванов'")
        print("  python3 scripts/create_admin_by_phone.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        asyncio.run(list_admins())
    else:
        if len(sys.argv) < 3:
            print("❌ Ошибка: укажите телефон и пароль")
            print("Использование: python3 scripts/create_admin_by_phone.py <телефон> <пароль> [имя]")
            sys.exit(1)
        
        phone = sys.argv[1]
        password = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else "Администратор"
        
        try:
            asyncio.run(create_admin_by_phone(phone, password, name))
            print("✅ Успешно завершено!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

