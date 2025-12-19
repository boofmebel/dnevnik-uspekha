#!/usr/bin/env python3
"""
Скрипт для проверки и настройки всех секретов и конфигурации
Использование: python scripts/setup_secrets.py
"""
import os
import secrets
import sys
from pathlib import Path

# Добавляем путь к backend для импорта
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def generate_secret_key(length: int = 32) -> str:
    """Генерация безопасного SECRET_KEY"""
    return secrets.token_urlsafe(length)

def check_env_file():
    """Проверка наличия .env файла"""
    env_path = backend_path / ".env"
    env_example_path = backend_path / ".env.example"
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        if env_example_path.exists():
            print(f"✅ Найден .env.example, создаю .env на его основе...")
            with open(env_example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print(f"✅ Файл .env создан из .env.example")
            return False
        else:
            print("⚠️  Создаю новый .env файл...")
            create_env_file(env_path)
            return False
    return True

def create_env_file(env_path: Path):
    """Создание нового .env файла с шаблоном"""
    secret_key = generate_secret_key(64)
    
    template = f"""# Конфигурация приложения "Дневник успеха"
# ВАЖНО: Не коммитьте этот файл в git!

# Безопасность
SECRET_KEY={secret_key}

# База данных
# Формат: postgresql+asyncpg://user:password@host:port/dbname
# Пример для локальной разработки:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dnevnik_uspekha

# Режим отладки (True для разработки, False для продакшена)
DEBUG=False

# Логирование
LOG_LEVEL=INFO
"""
    
    with open(env_path, 'w') as f:
        f.write(template)
    print(f"✅ Создан новый .env файл с SECRET_KEY")

def check_secret_key():
    """Проверка SECRET_KEY"""
    env_path = backend_path / ".env"
    
    if not env_path.exists():
        return False
    
    # Читаем .env файл
    secret_key = None
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('SECRET_KEY=') and not line.startswith('#'):
                secret_key = line.split('=', 1)[1].strip()
                break
    
    if not secret_key:
        print("❌ SECRET_KEY не найден в .env файле!")
        print("🔧 Генерирую новый SECRET_KEY...")
        
        # Читаем весь файл
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Ищем строку SECRET_KEY или добавляем новую
        new_secret_key = generate_secret_key(64)
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith('SECRET_KEY='):
                lines[i] = f"SECRET_KEY={new_secret_key}\n"
                found = True
                break
        
        if not found:
            # Добавляем в начало файла
            lines.insert(0, f"SECRET_KEY={new_secret_key}\n")
        
        # Записываем обратно
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ SECRET_KEY сгенерирован и добавлен в .env")
        return True
    
    if len(secret_key) < 32:
        print(f"⚠️  SECRET_KEY слишком короткий ({len(secret_key)} символов). Рекомендуется минимум 32.")
        return False
    
    print(f"✅ SECRET_KEY найден (длина: {len(secret_key)} символов)")
    return True

def check_database_url():
    """Проверка DATABASE_URL"""
    env_path = backend_path / ".env"
    
    if not env_path.exists():
        return False
    
    database_url = None
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL=') and not line.startswith('#'):
                database_url = line.split('=', 1)[1].strip()
                break
    
    if not database_url:
        print("❌ DATABASE_URL не найден в .env файле!")
        print("⚠️  Укажите DATABASE_URL в формате: postgresql+asyncpg://user:password@host:port/dbname")
        return False
    
    if not database_url.startswith(('postgresql+asyncpg://', 'postgresql://')):
        print(f"⚠️  DATABASE_URL имеет неожиданный формат: {database_url[:30]}...")
        return False
    
    print(f"✅ DATABASE_URL найден")
    return True

def check_settings():
    """Проверка настроек через Settings"""
    try:
        from core.config import settings
        
        print("\n📋 Проверка настроек через Settings:")
        
        # SECRET_KEY
        if settings.SECRET_KEY:
            print(f"  ✅ SECRET_KEY загружен (длина: {len(settings.SECRET_KEY)})")
        else:
            print(f"  ❌ SECRET_KEY не загружен!")
            return False
        
        # DATABASE_URL
        if settings.DATABASE_URL:
            # Скрываем пароль в выводе
            db_url_display = settings.DATABASE_URL
            if '@' in db_url_display:
                parts = db_url_display.split('@')
                if ':' in parts[0]:
                    user_pass = parts[0].split('://')[1] if '://' in parts[0] else parts[0]
                    if ':' in user_pass:
                        user, _ = user_pass.split(':', 1)
                        db_url_display = db_url_display.split('://')[0] + '://' + user + ':***@' + parts[1]
            print(f"  ✅ DATABASE_URL загружен: {db_url_display}")
        else:
            print(f"  ❌ DATABASE_URL не загружен!")
            return False
        
        # CORS
        print(f"  ✅ ALLOWED_ORIGINS: {len(settings.ALLOWED_ORIGINS)} origins")
        print(f"  ✅ ALLOWED_HOSTS: {len(settings.ALLOWED_HOSTS)} hosts")
        
        # Токены
        print(f"  ✅ ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
        print(f"  ✅ REFRESH_TOKEN_EXPIRE_DAYS: {settings.REFRESH_TOKEN_EXPIRE_DAYS}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка при загрузке настроек: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_env_example():
    """Создание .env.example файла"""
    env_example_path = backend_path / ".env.example"
    
    if env_example_path.exists():
        print("✅ .env.example уже существует")
        return
    
    template = """# Конфигурация приложения "Дневник успеха"
# Скопируйте этот файл в .env и заполните значения

# Безопасность
# Сгенерируйте SECRET_KEY командой: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=your-secret-key-here-minimum-32-characters

# База данных
# Формат: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dnevnik_uspekha

# Режим отладки
DEBUG=False

# Логирование
LOG_LEVEL=INFO
"""
    
    with open(env_example_path, 'w') as f:
        f.write(template)
    
    print("✅ Создан .env.example файл")

def main():
    """Основная функция"""
    print("🔐 Проверка и настройка секретов и конфигурации\n")
    
    # Создаем .env.example если его нет
    create_env_example()
    
    # Проверяем .env файл
    env_exists = check_env_file()
    
    # Проверяем SECRET_KEY
    secret_ok = check_secret_key()
    
    # Проверяем DATABASE_URL
    db_ok = check_database_url()
    
    # Проверяем настройки через Settings
    print("\n" + "="*50)
    settings_ok = check_settings()
    
    print("\n" + "="*50)
    print("📊 Итоги проверки:")
    print(f"  .env файл: {'✅' if env_exists else '❌'}")
    print(f"  SECRET_KEY: {'✅' if secret_ok else '❌'}")
    print(f"  DATABASE_URL: {'✅' if db_ok else '❌'}")
    print(f"  Settings загрузка: {'✅' if settings_ok else '❌'}")
    
    if all([env_exists, secret_ok, db_ok, settings_ok]):
        print("\n✅ Все проверки пройдены! Приложение готово к запуску.")
        return 0
    else:
        print("\n⚠️  Некоторые проверки не пройдены. Исправьте ошибки и запустите скрипт снова.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

