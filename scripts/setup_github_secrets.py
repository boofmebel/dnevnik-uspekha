#!/usr/bin/env python3
"""
Скрипт для автоматической настройки GitHub Secrets через API
Требует GITHUB_TOKEN с правами: repo, admin:repo_hook
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error
from nacl import encoding, public

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Шифрует секрет используя публичный ключ репозитория"""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def get_repo_public_key(repo_owner: str, repo_name: str, token: str):
    """Получает публичный ключ репозитория для шифрования секретов"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/public-key"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Python-Script'
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data.get('key'), data.get('key_id')
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка при получении публичного ключа: {e.code}")
        try:
            error_data = json.loads(e.read().decode())
            print(f"   Сообщение: {error_data.get('message', 'N/A')}")
        except:
            pass
        return None, None

def create_or_update_secret(repo_owner: str, repo_name: str, secret_name: str, secret_value: str, token: str):
    """Создает или обновляет секрет в репозитории"""
    # Получаем публичный ключ
    public_key, key_id = get_repo_public_key(repo_owner, repo_name, token)
    if not public_key or not key_id:
        print(f"❌ Не удалось получить публичный ключ для {secret_name}")
        return False
    
    # Шифруем секрет
    try:
        encrypted_value = encrypt_secret(public_key, secret_value)
    except Exception as e:
        print(f"❌ Ошибка при шифровании {secret_name}: {e}")
        return False
    
    # Отправляем запрос на создание/обновление секрета
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/{secret_name}"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'User-Agent': 'Python-Script'
    }
    
    data = {
        'encrypted_value': encrypted_value,
        'key_id': key_id
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method='PUT')
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [201, 204]:
                print(f"✅ Secret '{secret_name}' успешно создан/обновлен")
                return True
            else:
                print(f"⚠️  Неожиданный статус для {secret_name}: {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка при создании {secret_name}: {e.code}")
        try:
            error_data = json.loads(e.read().decode())
            print(f"   Сообщение: {error_data.get('message', 'N/A')}")
        except:
            pass
        return False

def main():
    repo_owner = "boofmebel"
    repo_name = "dnevnik-uspekha"
    
    # Получаем токен
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ ОШИБКА: GITHUB_TOKEN не установлен!")
        print("\n📋 Установите токен:")
        print("export GITHUB_TOKEN='your-token-here'")
        return 1
    
    print("🔐 Настройка GitHub Secrets...")
    print(f"📦 Репозиторий: {repo_owner}/{repo_name}\n")
    
    # Значения для Secrets
    secrets = {
        'SERVER_HOST': '89.104.74.123',
        'SERVER_USER': 'root',
        'SERVER_PATH': '/var/www/dnevnik-uspekha',
        'SERVER_PORT': '22'
    }
    
    # Получаем SSH ключ
    ssh_key_path = os.path.expanduser('~/.ssh/id_rsa')
    if os.path.exists(ssh_key_path):
        with open(ssh_key_path, 'r') as f:
            ssh_key = f.read().strip()
        secrets['SERVER_SSH_KEY'] = ssh_key
        print(f"✅ SSH ключ найден: {ssh_key_path}")
    else:
        print(f"❌ SSH ключ не найден: {ssh_key_path}")
        print("   Создайте ключ: ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa")
        return 1
    
    # Создаем/обновляем все Secrets
    print("\n📋 Создание Secrets...\n")
    success_count = 0
    for secret_name, secret_value in secrets.items():
        if create_or_update_secret(repo_owner, repo_name, secret_name, secret_value, token):
            success_count += 1
        print()
    
    print(f"\n✅ Готово! Создано/обновлено {success_count} из {len(secrets)} Secrets")
    
    if success_count == len(secrets):
        print("\n🎉 Все Secrets настроены! Деплой должен работать автоматически.")
        return 0
    else:
        print("\n⚠️  Некоторые Secrets не удалось создать. Проверьте права токена.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

