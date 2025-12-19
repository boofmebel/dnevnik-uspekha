#!/usr/bin/env python3
"""
Скрипт для проверки настройки проекта
Проверяет SECRET_KEY, БД, Redis и другие настройки
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_secret_key():
    """Проверка SECRET_KEY"""
    print("🔍 Проверка SECRET_KEY...")
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        print("   ❌ SECRET_KEY не установлен в переменных окружения")
        print("   💡 Установите: export SECRET_KEY='ваш-секретный-ключ'")
        return False
    if len(secret_key) < 32:
        print(f"   ⚠️  SECRET_KEY слишком короткий ({len(secret_key)} символов)")
        print("   💡 Рекомендуется минимум 32 символа")
        return False
    print(f"   ✅ SECRET_KEY установлен ({len(secret_key)} символов)")
    return True

def check_database():
    """Проверка подключения к БД"""
    print("\n🔍 Проверка подключения к БД...")
    try:
        from core.config import settings
        from core.database import engine
        from sqlalchemy import text
        import asyncio
        
        async def test_connection():
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        
        if asyncio.run(test_connection()):
            print("   ✅ Подключение к БД успешно")
            return True
        else:
            print("   ❌ Не удалось подключиться к БД")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка подключения к БД: {e}")
        return False

def check_redis():
    """Проверка подключения к Redis"""
    print("\n🔍 Проверка подключения к Redis...")
    try:
        import redis
        from core.config import settings
        
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        print("   ✅ Redis доступен")
        return True
    except ImportError:
        print("   ⚠️  Библиотека redis не установлена")
        print("   💡 Установите: pip install redis")
        return False
    except Exception as e:
        print(f"   ⚠️  Redis недоступен: {e}")
        print("   💡 Будет использоваться in-memory хранилище для rate limiting")
        return False

def check_migrations():
    """Проверка миграций"""
    print("\n🔍 Проверка миграций Alembic...")
    try:
        from alembic.config import Config
        from alembic import command
        from alembic.script import ScriptDirectory
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        heads = script.get_revision("head")
        
        print(f"   ✅ Миграции найдены, текущая версия: {heads}")
        return True
    except Exception as e:
        print(f"   ⚠️  Ошибка проверки миграций: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 50)
    print("ПРОВЕРКА НАСТРОЙКИ ПРОЕКТА")
    print("=" * 50)
    
    results = []
    results.append(("SECRET_KEY", check_secret_key()))
    results.append(("База данных", check_database()))
    results.append(("Redis", check_redis()))
    results.append(("Миграции", check_migrations()))
    
    print("\n" + "=" * 50)
    print("ИТОГИ:")
    print("=" * 50)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_ok = all(result for _, result in results)
    
    if all_ok:
        print("\n✅ Все проверки пройдены!")
    else:
        print("\n⚠️  Некоторые проверки не пройдены. Исправьте ошибки перед запуском.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

