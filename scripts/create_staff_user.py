#!/usr/bin/env python3
"""
Скрипт для создания staff пользователя (admin, support, moderator)
Использование: python3 scripts/create_staff_user.py <phone> <password> [role] [email]
Роль по умолчанию: admin
Email опционален
"""
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os
import bcrypt

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
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from models.staff_user import StaffUser
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


async def create_staff_user(email: str, password: str, role: str = "admin"):
    """Создание staff пользователя"""
    
    if role not in ["admin", "support", "moderator"]:
        print(f"❌ Неверная роль: {role}. Доступные: admin, support, moderator")
        return False
    
    # Используем sync URL для простоты
    db_url = os.getenv("DATABASE_URL").replace("+asyncpg", "")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Проверяем, существует ли пользователь
        existing = session.query(StaffUser).filter(StaffUser.email == email).first()
        if existing:
            print(f"⚠️ Пользователь с email {email} уже существует")
            print(f"   Обновляю пароль и роль...")
            # Хешируем пароль
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            existing.password_hash = password_hash
            existing.role = role
            existing.is_active = True
            session.commit()
            print(f"✅ Пользователь обновлён:")
            print(f"   📧 Email: {email}")
            print(f"   👤 Role: {role}")
            print(f"   🔑 Password: {password}")
            return True
        
        # Хешируем пароль
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Создаём пользователя
        staff_user = StaffUser(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        
        session.add(staff_user)
        session.commit()
        
        print(f"✅ Staff пользователь создан:")
        print(f"   📧 Email: {email}")
        print(f"   👤 Role: {role}")
        print(f"   🔑 Password: {password}")
        print(f"\n🌐 Вход: http://localhost:3000/staff/login")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python3 scripts/create_staff_user.py <phone> <password> [role] [email]")
        print("Пример: python3 scripts/create_staff_user.py +79991234567 admin123 admin admin@example.com")
        sys.exit(1)
    
    phone = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "admin"
    email = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Используем sync версию
    db_url = os.getenv("DATABASE_URL").replace("+asyncpg", "")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from models.staff_user import StaffUser
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Проверяем, существует ли пользователь по телефону
        existing = session.query(StaffUser).filter(StaffUser.phone == phone).first()
        if existing:
            print(f"⚠️ Пользователь с телефоном {phone} уже существует")
            print(f"   Обновляю пароль и роль...")
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            existing.password_hash = password_hash
            existing.role = role
            existing.is_active = True
            if email:
                existing.email = email
            session.commit()
            print(f"✅ Пользователь обновлён:")
            print(f"   📱 Phone: {phone}")
            if email:
                print(f"   📧 Email: {email}")
            print(f"   👤 Role: {role}")
            print(f"   🔑 Password: {password}")
        else:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            staff_user = StaffUser(
                phone=phone,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=True
            )
            session.add(staff_user)
            session.commit()
            print(f"✅ Staff пользователь создан:")
            print(f"   📱 Phone: {phone}")
            if email:
                print(f"   📧 Email: {email}")
            print(f"   👤 Role: {role}")
            print(f"   🔑 Password: {password}")
        
        print(f"\n🌐 Вход: http://localhost:3000/staff/login")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

