#!/usr/bin/env python3
"""
Скрипт для проверки всех импортов
Использование: python scripts/check_imports.py
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

errors = []

def check_import(module_name, description):
    """Проверка импорта модуля"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        errors.append((module_name, str(e)))
        return False

print("Проверка импортов backend...\n")

# Проверка core модулей
check_import("core.config", "core.config")
check_import("core.database", "core.database")
check_import("core.dependencies", "core.dependencies")
check_import("core.exceptions", "core.exceptions")
check_import("core.security.jwt", "core.security.jwt")
check_import("core.security.password", "core.security.password")
check_import("core.security.csrf", "core.security.csrf")
check_import("core.middleware.csrf", "core.middleware.csrf")

# Проверка моделей
check_import("models", "models")
check_import("models.user", "models.user")
check_import("models.refresh_token", "models.refresh_token")
check_import("models.child", "models.child")
check_import("models.task", "models.task")
check_import("models.star", "models.star")
check_import("models.piggy", "models.piggy")

# Проверка репозиториев
check_import("repositories.user_repository", "repositories.user_repository")

# Проверка сервисов
check_import("services.auth_service", "services.auth_service")

# Проверка роутеров
check_import("routers.auth", "routers.auth")
check_import("routers.users", "routers.users")
check_import("routers.children", "routers.children")
check_import("routers.tasks", "routers.tasks")
check_import("routers.stars", "routers.stars")
check_import("routers.piggy", "routers.piggy")

# Проверка схем
check_import("schemas.auth", "schemas.auth")

# Проверка main
check_import("main", "main (FastAPI app)")

print("\n" + "="*50)
if errors:
    print(f"❌ Найдено {len(errors)} ошибок:")
    for module, error in errors:
        print(f"   {module}: {error}")
    sys.exit(1)
else:
    print("✅ Все импорты успешны!")
    sys.exit(0)

