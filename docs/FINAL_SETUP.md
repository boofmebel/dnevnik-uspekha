# 🚀 Финальная настройка - всё готово!

## ✅ Что уже сделано:
- ✅ Репозиторий на GitHub: https://github.com/boofmebel/dnevnik-uspekha
- ✅ Ветки main и dev созданы
- ✅ Workflow файл подготовлен
- ✅ SSH ключи готовы
- ✅ IP сервера: [настройте через переменную окружения или Secrets]

## 📋 Что осталось (5 минут):

### 1. Добавить workflow файл в GitHub (через UI)

1. Откройте: https://github.com/boofmebel/dnevnik-uspekha
2. Нажмите "Add file" → "Create new file"
3. Путь: `.github/workflows/deploy.yml`
4. Скопируйте содержимое из файла `WORKFLOW_CONTENT.txt` (в корне проекта)
5. **ВАЖНО:** Убедитесь что создаете в ветке `main` (не dev!)
6. Нажмите "Commit new file"

### 2. Настройте Secrets в GitHub

1. Перейдите: https://github.com/boofmebel/dnevnik-uspekha/settings/secrets/actions
2. Добавьте секреты (см. файл `GITHUB_SECRETS.md`):
   - `SERVER_HOST`: `ваш-ip-адрес-сервера`
   - `SERVER_USER`: `root`
   - `SERVER_SSH_KEY`: содержимое `SSH_PRIVATE_KEY.txt`
   - `SERVER_PATH`: `/var/www/dnevnik-uspekha`

### 3. Подготовьте сервер

Выполните на сервере:

```bash
ssh root@ваш-ip-адрес-сервера

# Создайте директорию
mkdir -p /var/www/dnevnik-uspekha
cd /var/www/dnevnik-uspekha

# Клонируйте репозиторий
git clone https://github.com/boofmebel/dnevnik-uspekha.git .

# Добавьте публичный ключ
# Скопируйте содержимое SSH_PUBLIC_KEY.txt и добавьте в ~/.ssh/authorized_keys
nano ~/.ssh/authorized_keys
# Вставьте ключ, сохраните (Ctrl+X, Y, Enter)
```

### 4. Проверьте деплой

```bash
# Сделайте небольшое изменение
echo "# Test" >> README.md
git add .
git commit -m "Test deployment"
git push origin main
```

Проверьте: GitHub → Actions → должен быть успешный деплой ✅

---

## 📁 Полезные файлы:
- `WORKFLOW_CONTENT.txt` - содержимое для workflow файла
- `SSH_PRIVATE_KEY.txt` - приватный ключ для GitHub Secrets
- `SSH_PUBLIC_KEY.txt` - публичный ключ для сервера
- `GITHUB_SECRETS.md` - инструкция по настройке Secrets
- `setup_server.sh` - скрипт для настройки сервера

