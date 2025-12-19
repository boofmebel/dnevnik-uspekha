#!/usr/bin/env python3
"""
Скрипт для создания администратора (если его нет) и получения токена
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings
from core.security.password import hash_password
from core.security.jwt import create_access_token
from repositories.user_repository import UserRepository
from models.user import User, UserRole


async def create_admin_if_needed(session: AsyncSession):
    """Создает администратора, если его нет"""
    user_repo = UserRepository(session)
    
    # Проверяем, есть ли администратор
    admin_phone = "+79991234567"  # Тестовый номер
    admin_password = "admin123"   # Тестовый пароль
    
    existing_admin = await user_repo.get_by_phone(admin_phone)
    
    if existing_admin:
        print(f"✅ Администратор уже существует:")
        print(f"   ID: {existing_admin.id}")
        print(f"   Телефон: {existing_admin.phone}")
        print(f"   Email: {existing_admin.email}")
        print(f"   Роль: {existing_admin.role}")
        return existing_admin
    
    # Создаем администратора
    print("🔨 Создаю администратора...")
    password_hash = hash_password(admin_password)
    
    admin_data = {
        "phone": admin_phone,
        "password_hash": password_hash,
        "role": UserRole.ADMIN.value
    }
    
    admin = await user_repo.create(admin_data)
    await session.commit()
    
    print(f"✅ Администратор создан:")
    print(f"   ID: {admin.id}")
    print(f"   Телефон: {admin.phone}")
    print(f"   Роль: {admin.role}")
    print(f"   Пароль: {admin_password}")
    
    return admin


async def get_token_for_admin(session: AsyncSession, admin: User):
    """Получает токен для администратора"""
    from core.security.jwt import create_access_token
    
    role = admin.role.value if hasattr(admin.role, 'value') else str(admin.role)
    token = create_access_token({"sub": str(admin.id)}, expires_delta=None)
    
    return token


async def test_token(token: str):
    """Тестирует токен"""
    from core.security.jwt import verify_token
    
    print("\n🔍 Проверка токена...")
    payload = verify_token(token)
    
    if payload:
        print("✅ Токен валиден!")
        print(f"   User ID: {payload.get('sub')}")
        print(f"   Тип: {payload.get('type')}")
        print(f"   Истекает: {payload.get('exp')}")
        return True
    else:
        print("❌ Токен невалиден!")
        return False


async def main():
    """Основная функция"""
    print("=" * 60)
    print("🔐 Создание администратора и получение токена")
    print("=" * 60)
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session_maker() as session:
            # Создаем администратора
            admin = await create_admin_if_needed(session)
            
            # Получаем токен
            print("\n🎫 Получение токена...")
            token = await get_token_for_admin(session, admin)
            
            print("\n" + "=" * 60)
            print("✅ ТОКЕН ПОЛУЧЕН:")
            print("=" * 60)
            print(token)
            print("=" * 60)
            
            # Тестируем токен
            is_valid = await test_token(token)
            
            if is_valid:
                print("\n✅ Все готово! Токен работает.")
                print("\n📋 Данные для входа:")
                print(f"   Телефон: {admin.phone}")
                print(f"   Пароль: admin123")
                print(f"\n🔑 Токен (скопируйте его):")
                print(token)
            else:
                print("\n❌ Проблема с токеном. Проверьте SECRET_KEY.")
                return 1
                
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await engine.dispose()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

