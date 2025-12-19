#!/usr/bin/env python3
"""
Создание администратора на сервере
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к backend
backend_path = Path('/var/www/dnevnik-uspekha/backend')
if not backend_path.exists():
    backend_path = Path(__file__).parent.parent / 'backend'

sys.path.insert(0, str(backend_path))

try:
    from dotenv import load_dotenv
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import bcrypt
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите: pip install sqlalchemy asyncpg bcrypt python-dotenv")
    sys.exit(1)

async def create_admin():
    # Загружаем .env
    env_file = backend_path / '.env'
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Пробуем найти .env в корне
        root_env = Path('/var/www/dnevnik-uspekha/.env')
        if root_env.exists():
            load_dotenv(root_env)
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL не найден в .env")
        sys.exit(1)
    
    email = '79059510009@mail.ru'
    password = 'Admin123!'
    
    print(f"🔐 Создание администратора: {email}")
    
    # Генерируем хеш
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Подключаемся к базе
    engine = create_async_engine(db_url, echo=False)
    
    async with engine.begin() as conn:
        # Проверяем существующего пользователя
        result = await conn.execute(
            text("SELECT id, email, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        
        if user:
            print(f"✅ Пользователь найден: ID={user[0]}, роль={user[2]}")
            await conn.execute(
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
            await conn.execute(
                text("""
                    INSERT INTO users (email, password_hash, role, created_at)
                    VALUES (:email, :hash, 'admin', NOW())
                """),
                {"email": email, "hash": password_hash}
            )
            print("✅ Создан новый администратор")
        
        # Проверяем результат
        result = await conn.execute(
            text("SELECT id, email, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        print(f"✅ Готово! ID={user[0]}, Email={user[1]}, Role={user[2]}")
    
    await engine.dispose()
    print("\n🔑 Данные для входа:")
    print(f"   Email: {email}")
    print(f"   Пароль: {password}")

if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



