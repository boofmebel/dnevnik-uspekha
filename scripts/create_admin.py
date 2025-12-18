#!/usr/bin/env python3
"""
Скрипт для создания администратора
Использование: python3 scripts/create_admin.py email password
"""
import sys
import asyncio
from pathlib import Path

# Добавляем путь к backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from core.config import settings
from core.security.password import hash_password
from models.user import User, UserRole
from models import Base


async def create_admin(email: str, password: str):
    """Создание или обновление администратора"""
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
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем существующего пользователя
            user.role = UserRole.ADMIN
            user.password_hash = hash_password(password)
            print(f"✅ Пользователь {email} обновлён и назначен администратором")
        else:
            # Создаём нового администратора
            user = User(
                email=email,
                password_hash=hash_password(password),
                role=UserRole.ADMIN
            )
            session.add(user)
            print(f"✅ Создан новый администратор: {email}")
        
        await session.commit()
        print(f"✅ Готово! Теперь вы можете войти как администратор.")
        print(f"   Email: {email}")
        print(f"   Пароль: {password}")


async def list_users():
    """Список всех пользователей"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("❌ Пользователей в базе нет")
            return
        
        print("\n📋 Список пользователей:")
        print("-" * 60)
        for user in users:
            role_icon = "🔐" if user.role == UserRole.ADMIN else "👤"
            print(f"{role_icon} {user.email} ({user.role.value})")
        print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 scripts/create_admin.py <email> <password>  # Создать/обновить администратора")
        print("  python3 scripts/create_admin.py --list              # Показать всех пользователей")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        asyncio.run(list_users())
    else:
        if len(sys.argv) < 3:
            print("❌ Ошибка: укажите email и пароль")
            print("Использование: python3 scripts/create_admin.py <email> <password>")
            sys.exit(1)
        
        email = sys.argv[1]
        password = sys.argv[2]
        
        asyncio.run(create_admin(email, password))

