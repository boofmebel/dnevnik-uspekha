#!/usr/bin/env python3
"""
Простое создание администратора через прямое подключение к БД
"""
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

# Загружаем .env
backend_path = Path(__file__).parent.parent / "backend"
env_file = backend_path / ".env"
if env_file.exists():
    load_dotenv(env_file)
    db_url = os.getenv("DATABASE_URL")
    print(f"✅ Загружен .env: {env_file}")
    print(f"📝 DATABASE_URL: {db_url[:50]}...")
else:
    print("❌ .env файл не найден")
    sys.exit(1)

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    import bcrypt
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите: pip install 'sqlalchemy[asyncio]' asyncpg bcrypt python-dotenv")
    sys.exit(1)


async def create_admin(email: str, password: str):
    """Создание администратора"""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"\n🔐 Создание администратора:")
    print(f"   Email: {email}")
    print(f"   Пароль: {password}")
    print(f"   Хеш: {password_hash[:30]}...")
    print("")
    
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Проверяем существующего пользователя
        result = await session.execute(
            text("SELECT id, email, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        
        if user:
            print(f"✅ Пользователь найден: ID={user[0]}, роль={user[2]}")
            # Обновляем
            await session.execute(
                text("""
                    UPDATE users 
                    SET role = 'admin', 
                        password_hash = :hash,
                        updated_at = NOW()
                    WHERE email = :email
                """),
                {"email": email, "hash": password_hash}
            )
            print("✅ Обновлён: роль=admin")
        else:
            print("📝 Создание нового пользователя...")
            # Создаём нового
            await session.execute(
                text("""
                    INSERT INTO users (email, password_hash, role, created_at)
                    VALUES (:email, :hash, 'admin', NOW())
                """),
                {"email": email, "hash": password_hash}
            )
            print("✅ Создан новый администратор")
        
        await session.commit()
        
        # Проверяем результат
        result = await session.execute(
            text("SELECT id, email, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        
        print("")
        print("=" * 60)
        print("✅ ГОТОВО!")
        print("=" * 60)
        print(f"ID: {user[0]}")
        print(f"Email: {user[1]}")
        print(f"Роль: {user[2]}")
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


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "79059510009@mail.ru"
    password = sys.argv[2] if len(sys.argv) > 2 else "Admin123!"
    
    try:
        asyncio.run(create_admin(email, password))
        print("✅ Успешно завершено!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

