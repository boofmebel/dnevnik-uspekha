"""
Скрипт для удаления пользователя по номеру телефона
Использование: python -m backend.scripts.delete_user_by_phone +79682227908
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
from core.utils.phone_validator import normalize_phone


async def delete_user_by_phone(phone: str):
    """Удаление пользователя по номеру телефона"""
    # Нормализуем номер телефона
    normalized_phone = normalize_phone(phone)
    print(f"🔍 Поиск пользователя с номером: {normalized_phone}")
    
    async with AsyncSessionLocal() as session:
        try:
            user_repo = UserRepository(session)
            
            # Находим пользователя
            user = await user_repo.get_by_phone(normalized_phone)
            
            if not user:
                print(f"❌ Пользователь с номером {normalized_phone} не найден")
                return False
            
            print(f"✅ Найден пользователь:")
            print(f"   ID: {user.id}")
            print(f"   Имя: {user.name}")
            print(f"   Телефон: {user.phone}")
            print(f"   Роль: {user.role}")
            
            # Удаляем связанные данные перед удалением пользователя
            from sqlalchemy import text
            user_id = user.id
            
            # Удаляем refresh tokens
            result = await session.execute(
                text("DELETE FROM refresh_tokens WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_tokens = result.rowcount
            print(f"   Удалено refresh tokens: {deleted_tokens}")
            
            # Удаляем пользователя
            await session.execute(
                text("DELETE FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            await session.commit()
            
            print(f"✅ Пользователь успешно удалён")
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при удалении пользователя: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("❌ Использование: python -m backend.scripts.delete_user_by_phone +79682227908")
        print("   или: python backend/scripts/delete_user_by_phone.py +79682227908")
        sys.exit(1)
    
    phone = sys.argv[1]
    success = await delete_user_by_phone(phone)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

