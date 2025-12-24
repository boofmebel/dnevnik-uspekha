#!/usr/bin/env python3
"""
Скрипт миграции админов из users в staff_users
Использование: python3 scripts/migrate_admins_to_staff.py [--dry-run]
"""
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os
import secrets
import string

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
    else:
        print("❌ DATABASE_URL не найден в .env файле")
        sys.exit(1)
else:
    print("❌ .env файл не найден")
    sys.exit(1)

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select, update, text
    from core.security.password import hash_password
    from models.user import User
    from models.staff_user import StaffUser
    from repositories.user_repository import UserRepository
    from repositories.staff_user_repository import StaffUserRepository
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install 'sqlalchemy[asyncio]' asyncpg python-dotenv")
    sys.exit(1)


def generate_temp_password(length=16):
    """Генерация временного безопасного пароля"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def migrate_admins(dry_run=False):
    """Миграция админов из users в staff_users"""
    
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            user_repo = UserRepository(session)
            staff_repo = StaffUserRepository(session)
            
            # Находим всех админов в users
            result = await session.execute(
                select(User).where(User.role == "admin")
            )
            admins = result.scalars().all()
            
            if not admins:
                print("✅ Админов в таблице users не найдено")
                return
            
            print(f"\n📋 Найдено админов: {len(admins)}")
            print("=" * 60)
            
            migrated = []
            skipped = []
            
            for admin in admins:
                print(f"\n👤 Админ ID={admin.id}:")
                print(f"   Email: {admin.email or 'Нет email'}")
                print(f"   Phone: {admin.phone or 'Нет телефона'}")
                print(f"   Name: {admin.name or 'Нет имени'}")
                
                # Проверяем, есть ли уже такой staff пользователь
                if admin.email:
                    existing_staff = await staff_repo.get_by_email(admin.email)
                    if existing_staff:
                        print(f"   ⚠️  Staff пользователь с email {admin.email} уже существует, пропускаем")
                        skipped.append(admin)
                        continue
                
                if dry_run:
                    temp_password = generate_temp_password()
                    print(f"   🔐 Временный пароль: {temp_password}")
                    print(f"   ✅ Будет создан staff пользователь с ролью 'admin'")
                    migrated.append({
                        "admin": admin,
                        "temp_password": temp_password
                    })
                else:
                    # Генерируем временный пароль
                    temp_password = generate_temp_password()
                    
                    # Создаём staff пользователя
                    # Используем email если есть, иначе создаём на основе phone
                    staff_email = admin.email
                    if not staff_email:
                        # Если нет email, создаём на основе phone или id
                        if admin.phone:
                            staff_email = f"admin_{admin.phone.replace('+', '').replace(' ', '')}@migrated.local"
                        else:
                            staff_email = f"admin_{admin.id}@migrated.local"
                    
                    # Хешируем пароль
                    password_hash = hash_password(temp_password)
                    
                    # Создаём staff пользователя
                    staff_user = await staff_repo.create(
                        email=staff_email,
                        password_hash=password_hash,
                        role="admin"
                    )
                    
                    print(f"   ✅ Создан staff пользователь ID={staff_user.id}")
                    print(f"   📧 Email: {staff_email}")
                    print(f"   🔐 Временный пароль: {temp_password}")
                    print(f"   ⚠️  ВАЖНО: Сохраните пароль! Пользователь должен сменить его при первом входе.")
                    
                    migrated.append({
                        "admin": admin,
                        "staff_user": staff_user,
                        "temp_password": temp_password
                    })
            
            if not dry_run and migrated:
                # Обнуляем роль admin в users
                print("\n" + "=" * 60)
                print("🔄 Обнуление роли admin в таблице users...")
                
                admin_ids = [m["admin"].id for m in migrated]
                await session.execute(
                    update(User)
                    .where(User.id.in_(admin_ids))
                    .values(role="parent")  # Меняем на parent, так как admin больше не используется
                )
                
                await session.commit()
                print(f"✅ Роль обновлена для {len(migrated)} пользователей")
            
            # Итоговая сводка
            print("\n" + "=" * 60)
            print("📊 ИТОГИ МИГРАЦИИ:")
            print("=" * 60)
            print(f"✅ Мигрировано: {len(migrated)}")
            print(f"⚠️  Пропущено: {len(skipped)}")
            
            if migrated and not dry_run:
                print("\n📋 ДАННЫЕ ДЛЯ ВХОДА (сохраните!):")
                print("-" * 60)
                for m in migrated:
                    admin = m["admin"]
                    staff_user = m.get("staff_user")
                    temp_password = m["temp_password"]
                    email = staff_user.email if staff_user else (admin.email or f"admin_{admin.id}@migrated.local")
                    print(f"Email: {email}")
                    print(f"Пароль: {temp_password}")
                    print("-" * 60)
            
            if dry_run:
                print("\n⚠️  Это был dry-run. Для реальной миграции запустите без --dry-run")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при миграции: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🔍 DRY-RUN режим: изменения не будут сохранены")
    
    try:
        asyncio.run(migrate_admins(dry_run=dry_run))
        print("\n✅ Миграция завершена успешно!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


