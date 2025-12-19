#!/usr/bin/env python3
"""
Скрипт для установки и настройки PostgreSQL
Проверяет наличие PostgreSQL и помогает с установкой
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_postgresql_installed():
    """Проверка установлен ли PostgreSQL"""
    # Проверяем через which
    result = subprocess.run(['which', 'psql'], capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout.strip()
    
    # Проверяем стандартные пути
    common_paths = [
        '/usr/local/bin/psql',
        '/opt/homebrew/bin/psql',
        '/usr/bin/psql',
        '/Library/PostgreSQL/*/bin/psql',
    ]
    
    for path_pattern in common_paths:
        if '*' in path_pattern:
            import glob
            matches = glob.glob(path_pattern)
            if matches:
                return True, matches[0]
        elif os.path.exists(path_pattern):
            return True, path_pattern
    
    return False, None

def check_postgresql_running():
    """Проверка запущен ли PostgreSQL"""
    try:
        result = subprocess.run(['pg_isready', '-h', 'localhost'], 
                              capture_output=True, text=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def install_postgresql_macos():
    """Установка PostgreSQL на macOS"""
    print("📦 Установка PostgreSQL на macOS...")
    
    # Проверяем Homebrew
    brew_result = subprocess.run(['which', 'brew'], capture_output=True)
    if brew_result.returncode == 0:
        print("✅ Homebrew найден, устанавливаем PostgreSQL...")
        try:
            subprocess.run(['brew', 'install', 'postgresql@14'], check=True)
            subprocess.run(['brew', 'services', 'start', 'postgresql@14'], check=True)
            print("✅ PostgreSQL установлен и запущен через Homebrew")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки: {e}")
            return False
    else:
        print("❌ Homebrew не найден")
        print("💡 Установите Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False

def create_database():
    """Создание базы данных"""
    print("📋 Создание базы данных dnevnik_uspekha...")
    
    try:
        # Пробуем создать БД через createdb
        result = subprocess.run(['createdb', 'dnevnik_uspekha'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ База данных создана")
            return True
        else:
            # Пробуем через psql
            psql_cmd = "CREATE DATABASE dnevnik_uspekha;"
            result = subprocess.run(['psql', '-U', 'postgres', '-c', psql_cmd],
                                  capture_output=True, text=True, input='')
            if result.returncode == 0:
                print("✅ База данных создана через psql")
                return True
            else:
                print(f"⚠️  Не удалось создать БД автоматически: {result.stderr}")
                print("💡 Создайте вручную: createdb dnevnik_uspekha")
                return False
    except Exception as e:
        print(f"⚠️  Ошибка создания БД: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ПРОВЕРКА И УСТАНОВКА POSTGRESQL")
    print("=" * 60)
    
    # Проверка установки
    installed, path = check_postgresql_installed()
    if installed:
        print(f"✅ PostgreSQL найден: {path}")
    else:
        print("❌ PostgreSQL не найден")
        system = platform.system()
        if system == "Darwin":  # macOS
            install_postgresql_macos()
        else:
            print(f"⚠️  Автоматическая установка для {system} не поддерживается")
            print("💡 Установите PostgreSQL вручную:")
            print("   Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib")
            print("   CentOS/RHEL: sudo yum install postgresql-server")
            return 1
    
    # Проверка запуска
    if check_postgresql_running():
        print("✅ PostgreSQL запущен")
    else:
        print("❌ PostgreSQL не запущен")
        print("💡 Запустите PostgreSQL:")
        if platform.system() == "Darwin":
            print("   brew services start postgresql@14")
        else:
            print("   sudo systemctl start postgresql")
        return 1
    
    # Создание БД
    create_database()
    
    print("\n" + "=" * 60)
    print("✅ PostgreSQL готов к использованию!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

